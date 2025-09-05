import time
from typing import Optional

import numpy

from .io import load_data

try:
    import cupy

    from .cupyutils import log_allocated_gpu_memory
except ImportError:
    CUPY_AVAILABLE = False
    CUPY_MEM_POOL = None
else:
    CUPY_AVAILABLE = True
    CUPY_MEM_POOL = cupy.get_default_memory_pool()
import logging

MASK_PIXELS_AVAILABLE = None

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_index_shifted(
    data_shape: tuple,
    center_x: int,
    center_y: int,
):
    """Calculates the x,y index vectors, shifted to recreate the centro-symmetric pixels

    Inputs:
        - data_shape (tuple): shape of the data array (2 dimensional)
        - center_x (int): beam center in the first data dimension
        - center_y (int): beam center in the second data dimension
    Outputs:
        Tuple: pair of shifted x,y index vectors
    """
    y, x = numpy.meshgrid(
        numpy.arange(data_shape[0]),
        numpy.arange(data_shape[1]),
        indexing="ij",
        sparse=True,
    )

    x_ = 2 * int(center_x) - x + 1
    y_ = 2 * int(center_y) - y + 1

    # Think it's correct
    return x_, y_


def get_position_vectors(
    data_shape: tuple,
    use_cupy: bool = False,
):
    """Creates the x,y index vector of a 2-dimensional data array

    Inputs:
        - data_shape (tuple): shape of the data array (2 dimensional)
        - use_cupy (bool): transfer the vectors to the GPU, ready to process using cupy
    Outputs:
        - Tuple: pair of x-y index vector
    """
    y_vector, x_vector = numpy.meshgrid(
        numpy.arange(data_shape[0]),
        numpy.arange(data_shape[1]),
        indexing="ij",
        sparse=True,
    )
    if use_cupy:
        return cupy.asarray(x_vector), cupy.asarray(y_vector)
    return x_vector, y_vector


def shift_position_vectors(
    x_vector: numpy.ndarray,
    y_vector: numpy.ndarray,
    center_x: int,
    center_y: int,
    use_cupy: bool = False,
):
    """Shift a pair of index vectors, to point to centro-symmetric brothers

    Inputs:
        - x_vector (numpy.ndarray) : index vector along the first dimension of array
        - y_vector (numpy.ndarray) : index vector along the second dimension of array
        - center_x (int): beam center in the first data dimension
        - center_y (int): beam center in the second data dimension
        - use_cupy (bool): the return result is transfered to the GPU using cupy
    Outputs:
        - Tuple: pair of shifted x,y index vectors
    """
    center_x = int(center_x)
    center_y = int(center_y)
    x_shifted = 2 * center_x - x_vector + 1
    y_shifted = 2 * center_y - y_vector + 1
    if use_cupy:
        return cupy.asarray(x_shifted), cupy.asarray(y_shifted)
    return x_shifted, y_shifted


def get_mask_limits(
    data_shape: tuple = None,
    center_x: int = None,
    center_y: int = None,
    x_shifted: numpy.ndarray = None,
    y_shifted: numpy.ndarray = None,
    use_cupy: bool = False,
):
    """
    Mask limits is the primitive mask, it defines the area where the cave can be applied.
    It's the area of the pixels whose centro-symmetric brother falls in the detector surface.
    If the center of the beam matches with the center of the detector, the whole detector area can be caved.
    If the center falls into the edge of the detector, no pixel can be caved.

    Inputs:
        - data_shape (tuple): shape of the data array (2 dimensional)
        - center_x (int): beam center in the first data dimension
        - center_y (int): beam center in the second data dimension
        - x_shifted (numpy.ndarray) : shifted index vector along the first data dimension
        - y_shifted (numpy.ndarray) : shifted index vector along the second data dimension
        - use_cupy (bool): the return result is transfered to the GPU using cupy
    Outputs:
        - numpy.ndarray / cupy.ndarray: array to mask the pixels whose centrosymmetric brother falls out of the detector area.
    """
    if x_shifted is None or y_shifted is None:
        x_vector, y_vector = get_position_vectors(
            data_shape=data_shape,
            use_cupy=use_cupy,
        )
        x_shifted, y_shifted = shift_position_vectors(
            x_vector=x_vector,
            y_vector=y_vector,
            center_x=center_x,
            center_y=center_y,
            use_cupy=use_cupy,
        )
    x_max = x_shifted.shape[-1]
    y_max = y_shifted.shape[0]
    if use_cupy:
        mask_limits_x_cupy = cupy.logical_and(x_shifted > 0, y_shifted > 0)
        mask_limits_y_cupy = cupy.logical_and(x_shifted < x_max, y_shifted < y_max)
        mask_limits_cupy = mask_limits_x_cupy & mask_limits_y_cupy  # boolean
        return mask_limits_cupy
    mask_limits_x = numpy.logical_and(x_shifted > 0, y_shifted > 0)
    mask_limits_y = numpy.logical_and(x_shifted < x_max, y_shifted < y_max)
    mask_limits = mask_limits_x & mask_limits_y  # boolean
    return mask_limits


def process_data_caving(
    data: numpy.ndarray,
    Center_1: int,
    Center_2: int,
    filename_mask_to_cave: Optional[str] = None,
    filename_mask_reference: Optional[str] = None,
    Dummy: int = None,
    flip_caving: bool = False,
    algorithm: str = "numpy",
    return_mask: bool = False,
    **kwargs,
):
    """Performs a caving algorithm on each frame of a dataset

    Inputs:
        - data (numpy.ndarray): data (2D) or dataset (3D) to be caved
        - Center_1 (int): beam center in the first data dimension
        - Center_2 (int): beam center in the second data dimension
        - filename_mask_to_cave (str): path to the file with a static mask, whose pixels will be caved
        - filename_mask_reference (str): path to the file with a mask, whose pixels won't be caved
        - Dummy (int): value of pixels to be caved and also value to fill all the masked pixels before applying the caving
        - flip_caving (bool): perform a symmetric caving in both directions of the array, the center is the array center
        - algorithm (str): implementation of caving (numpy or cupy)
        - return_mask (bool): return each complete caving mask used per frame
        - **kwargs
    Outputs:
        - numpy.ndarray: caved dataset
    """
    if algorithm not in ALGORITHMS_AVAILABLE:
        logger.warning(
            f"Algorithm '{algorithm}' is not available. Using '{DEFAULT_ALGORITHM}' instead."
        )
        algorithm = DEFAULT_ALGORITHM
    elif algorithm == "cupy" and not CUPY_AVAILABLE:
        logger.warning(f"CuPy is not available. Using {DEFAULT_ALGORITHM} instead.")
        algorithm = DEFAULT_ALGORITHM
    binning = kwargs.get("binning")

    if data.ndim == 2:
        data_shape = data.shape
        data = data[numpy.newaxis, ...]
    elif data.ndim == 3:
        data_shape = data[0].shape
        data = data

    mask_static = load_data(
        filename=filename_mask_to_cave,
        binning=binning,
        data_signal_shape=data_shape,
    )
    mask_reference = load_data(
        filename=filename_mask_reference,
        binning=binning,
        data_signal_shape=data_shape,
    )

    if mask_static is not None:
        mask_static = mask_static.astype(bool)
    if mask_reference is not None:
        mask_reference = mask_reference.astype(bool)

    params_caving = {
        "dataset": data,
        "mask_static": mask_static,  # bool
        "mask_reference": mask_reference,  # bool
        "Center_1": Center_1,
        "Center_2": Center_2,
        "Dummy": Dummy,
        "return_mask": return_mask,
        "flip_caving": flip_caving,
        **kwargs,
    }
    result = ALGORITHMS_AVAILABLE[algorithm]["algorithm"](
        **params_caving,
    )
    return result


def _process_dataset_caving_numpy(
    dataset: numpy.ndarray,  # 3 dims are accepted
    Center_1: int,
    Center_2: int,
    mask_static: numpy.ndarray = None,  # boolean type
    mask_reference: numpy.ndarray = None,  # boolean type
    Dummy: int = None,
    use_numexpr: bool = False,
    flip_caving: bool = False,
    return_mask: bool = False,
    log: bool = False,
    **kwargs,
):
    """Performs a caving algorithm on each frame of a dataset using numpy implementation

    Inputs:
        - dataset (numpy.ndarray): dataset (3D) to be caved
        - Center_1 (int): beam center in the first data dimension
        - Center_2 (int): beam center in the second data dimension
        - mask_static (numpy.ndarray): static mask, whose pixels will be caved
        - mask_reference (numpy.ndarray): mask whose pixels won't be caved
        - Dummy (int): value of pixels to be caved and also value to fill all the masked pixels before applying the caving
        - use_numexpr (bool): flag to desactivate numexpr accelleration
        - flip_caving (bool): perform a symmetric caving in both directions of the array, the center is the array center
        - return_mask (bool): return each complete caving mask used per frame
        - log (bool): verbose execution with benchmarks
        - **kwargs
    Outputs:
        - numpy.ndarray: caved dataset
    """
    if log:
        logger.info("Processing dataset caving with NumPy")

    t0 = time.perf_counter()
    data_shape = dataset.shape[1:]
    x_vector, y_vector = get_position_vectors(
        data_shape=data_shape,
    )
    x_shifted, y_shifted = shift_position_vectors(
        x_vector=x_vector, y_vector=y_vector, center_x=Center_1, center_y=Center_2
    )

    # 1) Create the mask with the detector limits, the provided static mask and the dynamic mask (dummy)
    mask_limits = get_mask_limits(
        x_shifted=x_shifted,
        y_shifted=y_shifted,
    )
    if mask_static is not None and Dummy is not None:
        mask_caving = mask_limits & (mask_static + (dataset == Dummy))
    elif mask_static is not None and Dummy is None:
        mask_caving = mask_limits & mask_static
    elif mask_static is None and Dummy is not None:
        mask_caving = mask_limits & (dataset == Dummy)
    else:
        logger.warning("No mask and no dummy value provided, no caving applied.")
        return dataset
    t1 = time.perf_counter()

    # 2) Remove a reference mask that we don't want to cave
    if mask_reference is not None:
        mask_caving ^= mask_caving & mask_reference[y_shifted, x_shifted]
    t2 = time.perf_counter()

    # 3) Invert the dataset to create the centro-symmetric brother and substitute the masked values
    dataset_caved = numpy.copy(dataset)
    if Dummy is not None:
        numpy.copyto(dataset_caved, Dummy, where=mask_caving)
        numpy.copyto(
            dataset_caved, dataset_caved[:, y_shifted, x_shifted], where=mask_caving
        )
    else:
        numpy.copyto(dataset_caved, dataset[:, y_shifted, x_shifted], where=mask_caving)
    t3 = time.perf_counter()

    # 4) Flip the dataset (not physically correct, be careful)
    if flip_caving:
        mask_flip = ~mask_limits
        numpy.copyto(
            dataset_caved,
            dataset_caved[:, numpy.flipud(y_vector), numpy.fliplr(x_vector)],
            where=mask_flip,
        )
    t4 = time.perf_counter()

    if log:
        nb_frames = len(dataset)
        logger.info(
            f"  1) Prepare masks per frame: {(t1 - t0) / nb_frames * 1000:.4f} ms"
        )
        logger.info(
            f"  2) Remove reference per frame: {(t2 - t1) / nb_frames * 1000:.4f} ms"
        )
        logger.info(f"  3) Caving per frame: {(t3 - t2) / nb_frames * 1000:.4f} ms")
        logger.info(f"  4) Flipping per frame: {(t4 - t3) / nb_frames * 1000:.4f} ms")
        logger.info(
            f"  5) Total caving per frame: {(t4 - t0) / nb_frames * 1000:.4f} ms"
        )

    if return_mask:
        return dataset_caved, mask_caving
    return dataset_caved


def _process_data_caving_cupy(
    data: numpy.ndarray,  # 2 dims are accepted
    mask_limits_cupy,  # cupy.ndarray,
    x_shifted_cupy=None,  # cupy.ndarray
    y_shifted_cupy=None,  # cupy.ndarray ,
    mask_static_cupy=None,  # cupy.ndarray ,  # boolean type
    mask_reference_cupy=None,  # cupy.ndarray,  # boolean type
    Dummy: int = None,
    flip_caving: bool = False,
    mask_flip_cupy=None,  # cupy.ndarray,
    x_vector_cupy=None,  # cupy.ndarray,
    y_vector_cupy=None,  # cupy.ndarray,
    **kwargs,
):  # -> cupy.ndarray:
    """Performs a caving algorithm on each frame of a dataset using cupy implementation

    Inputs:
        - data (numpy.ndarray): data (2D) or dataset (3D) to be caved
        - mask_limits_cupy (cupy.ndarray): the primitive mask with the detector limits, get with get_mask_limits
        - x_shifted_cupy (cupy.ndarray): shifted index vector along the first data dimension, transfered to GPU
        - y_shifted_cupy (cupy.ndarray): shifted index vector along the second data dimension, transfered to GPU
        - mask_static_cupy (cupy.ndarray): static mask, whose pixels will be caved, transfered to GPU
        - mask_reference_cupy (cupy.ndarray): mask whose pixels won't be caved, transfered to GPU
        - Dummy (int): value of pixels to be caved and also value to fill all the masked pixels before applying the caving
        - flip_caving (bool): perform a symmetric caving in both directions of the array, the center is the array center
        - mask_flip_cupy (cupy.ndarray): static mask for flipping caving, transfered to GPU
        - x_vector_cupy (cupy.ndarray): index vector along the first data dimension, transfered to GPU
        - y_vector_cupy (cupy.ndarray): index vector along the second data dimension, transfered to GPU
        - **kwargs
    Outputs:
        - cupy.ndarray: caved dataset still on GPU
    """
    bench_info = {
        "data_transfer": 0.0,
        "build_mask": 0.0,
        "remove_reference": 0.0,
        "data_caving": 0.0,
        "flip": 0.0,
    }

    t0 = time.perf_counter()
    # 1) Transfer the data to the GPU
    data_cupy = cupy.asarray(data)
    t1 = time.perf_counter()

    # 2) Create the mask with the detector limits, the provided static mask and the dynamic mask (dummy)
    if mask_static_cupy is not None and Dummy is not None:
        mask_caving_cupy = mask_limits_cupy & (mask_static_cupy + (data_cupy == Dummy))
    elif mask_static_cupy is not None and Dummy is None:
        mask_caving_cupy = mask_limits_cupy & mask_static_cupy
    elif mask_static_cupy is None and Dummy is not None:
        mask_caving_cupy = mask_limits_cupy & (data_cupy == Dummy)
    else:
        logger.warning("No mask and no dummy value provided, no caving applied.")
        return data
    t2 = time.perf_counter()

    # 3) Remove a reference mask that we don't want to cave
    if mask_reference_cupy is not None:
        mask_caving_cupy ^= (
            mask_caving_cupy & mask_reference_cupy[y_shifted_cupy, x_shifted_cupy]
        )
    t3 = time.perf_counter()

    # 4) Invert the dataset to create the centro-symmetric brother and substitute the masked values
    data_caved_cupy = cupy.copy(data_cupy)
    if Dummy is not None:
        cupy.copyto(data_caved_cupy, Dummy, where=mask_caving_cupy)
        cupy.copyto(
            data_caved_cupy,
            data_caved_cupy[y_shifted_cupy, x_shifted_cupy],
            where=mask_caving_cupy,
        )
    else:
        cupy.copyto(
            data_caved_cupy,
            data_cupy[y_shifted_cupy, x_shifted_cupy],
            where=mask_caving_cupy,
        )
    t4 = time.perf_counter()

    # 5) Flip the dataset (not physically correct, be careful)
    if flip_caving:
        cupy.copyto(
            data_caved_cupy,
            data_caved_cupy[cupy.flipud(y_vector_cupy), cupy.fliplr(x_vector_cupy)],
            where=mask_flip_cupy,
        )
    t5 = time.perf_counter()

    bench_info["data_transfer"] += t1 - t0
    bench_info["build_mask"] += t2 - t1
    bench_info["remove_reference"] += t3 - t2
    bench_info["data_caving"] += t4 - t3
    bench_info["flip"] += t5 - t4
    return data_caved_cupy, bench_info


def _process_dataset_caving_cupy(
    dataset: numpy.ndarray,  # 3 dims are accepted
    Center_1: int,
    Center_2: int,
    mask_static: numpy.ndarray = None,  # boolean type
    mask_reference: numpy.ndarray = None,  # boolean type
    Dummy: int = None,
    log: bool = False,
    flip_caving: bool = False,
    **kwargs,
):
    """Performs a caving algorithm on each frame of a dataset using cupy implementation

    Inputs:
        - data (numpy.ndarray): dataset (3D) to be caved
        - Center_1 (int): beam center in the first data dimension
        - Center_2 (int): beam center in the second data dimension
        - mask_static (numpy.ndarray): static mask, whose pixels will be caved
        - mask_reference (numpy.ndarray): mask whose pixels won't be caved
        - Dummy (int): value of pixels to be caved and also value to fill all the masked pixels before applying the caving
        - log (bool): verbose execution with benchmarks
        - flip_caving (bool): perform a symmetric caving in both directions of the array, the center is the array center
        - **kwargs
    Outputs:
        - cupy.ndarray: caved dataset still on GPU
    """
    log_allocated_gpu_memory()
    if log:
        logger.info("Processing dataset caving with Cupy")

    t0 = time.perf_counter()
    data_shape = dataset.shape[1:]
    x_vector_cupy, y_vector_cupy = get_position_vectors(
        data_shape=data_shape, use_cupy=True
    )
    x_shifted_cupy, y_shifted_cupy = shift_position_vectors(
        x_vector=x_vector_cupy,
        y_vector=y_vector_cupy,
        center_x=Center_1,
        center_y=Center_2,
        use_cupy=True,
    )

    # 1) Create the mask with the detector limits, the provided static mask and the dynamic mask (dummy)
    mask_limits_cupy = get_mask_limits(
        x_shifted=x_shifted_cupy,
        y_shifted=y_shifted_cupy,
        use_cupy=True,
    )

    nb_frames = len(dataset)
    bench_info_dataset = {
        "data_transfer": 0.0,
        "build_mask": 0.0,
        "remove_reference": 0.0,
        "data_caving": 0.0,
        "flip": 0.0,
        "insert": 0.0,
        "total": 0.0,
    }

    dataset_caved = numpy.zeros_like(dataset, dtype=dataset.dtype)
    params = {
        "mask_limits_cupy": mask_limits_cupy,
        "mask_static_cupy": (
            cupy.asarray(mask_static) if mask_static is not None else None
        ),
        "mask_reference_cupy": (
            cupy.asarray(mask_reference) if mask_reference is not None else None
        ),
        "Dummy": Dummy,
        "x_shifted_cupy": x_shifted_cupy,
        "y_shifted_cupy": y_shifted_cupy,
        "flip_caving": flip_caving,
        "mask_flip_cupy": ~mask_limits_cupy,
        "y_vector_cupy": y_vector_cupy,
        "x_vector_cupy": x_vector_cupy,
        **kwargs,
    }

    for index_frame, data_frame in enumerate(dataset):
        t0 = time.perf_counter()
        (
            data_frame_caved_cupy,
            bench_info_data,
        ) = _process_data_caving_cupy(
            data=data_frame,
            **params,
        )
        t1 = time.perf_counter()
        dataset_caved[index_frame] = data_frame_caved_cupy.get()
        t2 = time.perf_counter()

        bench_info_dataset["data_transfer"] += bench_info_data["data_transfer"]
        bench_info_dataset["build_mask"] += bench_info_data["build_mask"]
        bench_info_dataset["remove_reference"] += bench_info_data["remove_reference"]
        bench_info_dataset["data_caving"] += bench_info_data["data_caving"]
        bench_info_dataset["flip"] += bench_info_data["flip"]
        bench_info_dataset["insert"] += t2 - t1
        bench_info_dataset["total"] += t2 - t0

    if log:
        logger.info(
            f"Data transfer time per frame: {bench_info_dataset['data_transfer']/nb_frames*1000:.4f} ms"
        )
        logger.info(
            f"Build mask time per frame: {bench_info_dataset['build_mask']/nb_frames*1000:.4f} ms"
        )
        logger.info(
            f"Remove reference time per frame: {bench_info_dataset['remove_reference']/nb_frames*1000:.4f} ms"
        )
        logger.info(
            f"Data caving time per frame: {bench_info_dataset['data_caving']/nb_frames*1000:.4f} ms"
        )
        logger.info(
            f"Flip time per frame: {bench_info_dataset['flip']/nb_frames*1000:.4f} ms"
        )
        logger.info(
            f"Insert time per frame: {bench_info_dataset['insert']/nb_frames*1000:.4f} ms"
        )
        logger.info(
            f"Total time per frame: {(bench_info_dataset['total'])/nb_frames*1000:.4f} ms"
        )
    log_allocated_gpu_memory()
    return dataset_caved


ALGORITHMS_AVAILABLE = {
    "numpy": {"algorithm": _process_dataset_caving_numpy, "use_cupy": False},
    "cupy": {"algorithm": _process_dataset_caving_cupy, "use_cupy": True},
}
DEFAULT_ALGORITHM = "numpy"
