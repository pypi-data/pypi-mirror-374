import time
from typing import Optional, Tuple

import numexpr
import numpy
from scipy.signal import convolve as oaconvolve_numpy

from .io import load_data

try:
    import cupy
    from cupyx.scipy.signal import oaconvolve as oaconvolve_cupy

    from .cupyutils import log_allocated_gpu_memory
except ImportError:
    CUPY_AVAILABLE = False
    CUPY_MEM_POOL = None
else:
    CUPY_AVAILABLE = True
    CUPY_MEM_POOL = cupy.get_default_memory_pool()
import logging

from .caving import (
    _process_data_caving_cupy,
    get_mask_limits,
    get_position_vectors,
    process_data_caving,
    shift_position_vectors,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def shift_window(
    array_window: numpy.ndarray,
    cx: int,
    cy: int,
) -> Tuple[numpy.ndarray, numpy.ndarray]:
    """
    Shift the window data to align with the specified center coordinates and apply a mask.

    Parameters:
        window_data (numpy.ndarray): The input window data to be shifted.
        cx (int): X-coordinate of the direct beam.
        cy (int): Y-coordinate of the direct beam.

    Returns:
        Tuple[numpy.ndarray, numpy.ndarray]: The shifted window data and the mask.
    """
    y_size, x_size = array_window.shape
    y, x = numpy.meshgrid(numpy.arange(y_size), numpy.arange(x_size), indexing="ij")

    y_center_mask, x_center_mask = numpy.unravel_index(
        numpy.argmax(array_window), shape=array_window.shape
    )
    deltax = int(cx) - x_center_mask
    deltay = int(cy) - y_center_mask

    x_clipped = numpy.clip(x - deltax, 0, x_size - 5)
    y_clipped = numpy.clip(y - deltay, 0, y_size - 5)
    window_shifted = array_window[y_clipped, x_clipped]

    x_shifted = x - deltax
    y_shifted = y - deltay

    mask_x = numpy.logical_and(0.0 < x_shifted, x_shifted < x.max())
    mask_y = numpy.logical_and(0.0 < y_shifted, y_shifted < y.max())
    mask = mask_x & mask_y

    # Shifting and clipping mask are ok (in 4 shift directions)
    return window_shifted, ~mask


def _process_dataset_2scat_numpy(
    dataset_signal: numpy.ndarray,  # 3dim
    array_window: numpy.ndarray,  # Original, non-shifted
    Center_1: int,
    Center_2: int,
    WindowRoiSize: int = 120,
    Dummy: Optional[int] = -10,
    dataset_variance: Optional[numpy.ndarray] = None,
    clip_data: bool = True,
    use_numexpr: bool = False,
    pre_caving: bool = False,
    log: bool = False,
    **kwargs: Optional[dict],
) -> Tuple[Optional[numpy.ndarray], Optional[numpy.ndarray]]:
    if log:
        logger.info("Using numpy for secondary scattering correction")
    t0_ = time.perf_counter()
    if pre_caving:
        params_caving_numpy = {
            "Center_1": Center_1,
            "Center_2": Center_2,
            "Dummy": Dummy,
            "algorithm": "numpy",
            "return_mask": False,
            "log": log,
            **kwargs,
        }
        dataset_signal = process_data_caving(
            data=dataset_signal,
            **params_caving_numpy,
        )
        if dataset_variance is not None:
            dataset_variance = process_data_caving(
                data=dataset_variance,
                **params_caving_numpy,
            )

    # 1) Slice the original data around the center, this will be the convolution kernel
    Center_1 = int(Center_1)
    Center_2 = int(Center_2)
    WindowRoiSize = int(WindowRoiSize)
    t0 = time.perf_counter()
    subdataset_signal = dataset_signal[
        :,
        Center_2 - WindowRoiSize : Center_2 + WindowRoiSize,
        Center_1 - WindowRoiSize : Center_1 + WindowRoiSize,
    ].copy()
    t1 = time.perf_counter()

    # 2) Cover the dummy values in the subdataset (dummy values jeopardize the convolution)
    numpy.copyto(subdataset_signal, 0.0, where=subdataset_signal == Dummy)
    t2 = time.perf_counter()

    # 3) Shift the window
    array_window_shifted, mask_clip = shift_window(
        array_window=array_window,
        cx=Center_1,
        cy=Center_2,
    )
    t3 = time.perf_counter()

    # 3) Perform the convolution all across the dataset (3-dimensional)
    signal_2scat = numpy.array(
        [
            oaconvolve_numpy(array_window_shifted, subdata, mode="same")
            for subdata in subdataset_signal
        ]
    )
    t4 = time.perf_counter()

    # 4) Calculate the corrected signal, variance and sigma
    if use_numexpr:
        dataset_signal_corrected = numexpr.evaluate(
            "where(dataset_signal <= 0.0, dataset_signal, dataset_signal - signal_2scat)"
        )

        if dataset_variance is not None:
            dataset_variance_corrected = numexpr.evaluate(
                "where(dataset_variance <= 0.0, dataset_variance, dataset_variance + signal_2scat + 0.0)"
            )
            dataset_sigma_corrected = numexpr.evaluate(
                "where(dataset_variance_corrected <= 0.0, dataset_variance_corrected, sqrt(dataset_variance_corrected))"
            )
        else:
            dataset_variance_corrected = None
            dataset_sigma_corrected = None
    else:
        dataset_signal_corrected = numpy.where(
            dataset_signal <= 0.0, dataset_signal, dataset_signal - signal_2scat
        )
        if dataset_variance is not None:
            dataset_variance_corrected = numpy.where(
                dataset_variance <= 0.0,
                dataset_variance,
                dataset_variance + signal_2scat + 0.0,
            )
            dataset_sigma_corrected = numpy.where(
                dataset_variance_corrected <= 0.0,
                dataset_variance_corrected,
                numpy.sqrt(dataset_variance_corrected),
            )
        else:
            dataset_variance_corrected = None
            dataset_sigma_corrected = None
    t5 = time.perf_counter()

    # 5) Clip the data that could not be corrected
    if clip_data:
        if use_numexpr:
            dataset_signal_corrected = numexpr.evaluate(
                "where(mask_clip, Dummy, dataset_signal_corrected)"
            )

            if dataset_variance_corrected is not None:
                dataset_variance_corrected = numexpr.evaluate(
                    "where(mask_clip, Dummy, dataset_variance_corrected)"
                )
            if dataset_sigma_corrected is not None:
                dataset_sigma_corrected = numexpr.evaluate(
                    "where(mask_clip, Dummy, dataset_sigma_corrected)"
                )
        else:
            numpy.copyto(dataset_signal_corrected, Dummy, where=mask_clip)
            if dataset_variance_corrected is not None:
                numpy.copyto(dataset_variance_corrected, Dummy, where=mask_clip)
            if dataset_sigma_corrected is not None:
                numpy.copyto(dataset_sigma_corrected, Dummy, where=mask_clip)
    t6 = time.perf_counter()

    if log:
        nb_frames = len(dataset_signal)
        logger.info(
            f"  1) Subdata slicing per frame: {(t1 - t0) / nb_frames * 1000:.4f} ms"
        )
        logger.info(
            f"  2) Mask subdata per frame shifting: {(t2 - t1) / nb_frames * 1000:.4f} ms"
        )
        logger.info(f"  3) Window shifting: {(t3 - t2) * 1000:.4f} ms")
        logger.info(
            f"  4) Convolution per frame: {(t4 - t3) / nb_frames * 1000:.4f} ms"
        )
        logger.info(
            f"  5) Correction calculation per frame: {(t5 - t4) / nb_frames * 1000:.4f} ms"
        )
        logger.info(
            f"  6) Data clipping per frame: {(t6 - t5) / nb_frames * 1000:.4f} ms"
        )
        logger.info(
            f"  7) Total 2scat per frame: {(t6 - t0) / nb_frames * 1000:.4f} ms"
        )
        logger.info(
            f"Total time 2scat+cave per frame: {(t6 - t0_) / nb_frames*1000:.4f} ms"
        )

    return (
        dataset_signal_corrected,
        dataset_variance_corrected,
        dataset_sigma_corrected,
        signal_2scat,
    )


def _process_dataset_2scat_cupy(
    dataset_signal: numpy.ndarray,  # 3dim
    array_window: numpy.ndarray,  # Original, non-shifted
    center_x: int,
    center_y: int,
    window_roi_size: int = 120,
    dummy: Optional[int] = -10,
    dataset_variance: Optional[numpy.ndarray] = None,
    clip_data: bool = True,
    pre_caving: bool = False,
    **kwargs: Optional[dict],
) -> Tuple[Optional[numpy.ndarray], Optional[numpy.ndarray]]:
    log_allocated_gpu_memory()
    center_x = int(center_x)
    center_y = int(center_y)
    window_roi_size = int(window_roi_size)
    if pre_caving:
        data_shape = dataset_signal.shape[1:]
        binning = kwargs.get("binning")
        x_vector_cupy, y_vector_cupy = get_position_vectors(
            data_shape=data_shape, use_cupy=True
        )
        x_shifted_cupy, y_shifted_cupy = shift_position_vectors(
            x_vector=x_vector_cupy,
            y_vector=y_vector_cupy,
            center_x=center_x,
            center_y=center_y,
            use_cupy=True,
        )
        mask_limits_cupy = get_mask_limits(
            x_shifted=x_shifted_cupy,
            y_shifted=y_shifted_cupy,
            use_cupy=True,
        )
        filename_mask_to_cave = kwargs.get("filename_mask_to_cave")
        filename_mask_reference = kwargs.get("filename_mask_reference")
        mask_static_cupy = None
        mask_reference_cupy = None
        if filename_mask_to_cave:
            mask_static = load_data(
                filename=filename_mask_to_cave,
                binning=binning,
                data_signal_shape=data_shape,
            )
            if mask_static is not None:
                mask_static_cupy = cupy.asarray(mask_static).astype(bool)

        if filename_mask_reference:
            mask_reference = load_data(
                filename=filename_mask_reference,
                binning=binning,
                data_signal_shape=data_shape,
            )
            if mask_reference is not None:
                mask_reference_cupy = cupy.asarray(mask_reference).astype(bool)

        flip_caving = kwargs.get("flip_caving", False)
        params_caving_cupy = {
            "mask_limits_cupy": mask_limits_cupy,
            "x_shifted_cupy": x_shifted_cupy,
            "y_shifted_cupy": y_shifted_cupy,
            "mask_static_cupy": mask_static_cupy,
            "mask_reference_cupy": mask_reference_cupy,
            "dummy": dummy,
            "flip_caving": flip_caving,
            "mask_flip_cupy": ~mask_limits_cupy,
            "x_vector_cupy": x_vector_cupy,
            "y_vector_cupy": y_vector_cupy,
        }

    array_window_shifted, mask_clip = shift_window(
        array_window=array_window,
        cx=center_x,
        cy=center_y,
    )
    params_2scat_cupy = {
        "array_window_cupy": cupy.asarray(array_window_shifted),
        "center_x": center_x,
        "center_y": center_y,
        "window_roi_size": window_roi_size,
        "dummy": dummy,
        "clip_data": clip_data,
        "mask_clip_cupy": cupy.asarray(mask_clip),
    }

    dataset_signal_corrected = numpy.zeros_like(dataset_signal)
    dataset_signal_2scat = numpy.zeros_like(dataset_signal)
    dataset_variance_corrected = None
    dataset_sigma_corrected = None
    if dataset_variance is not None:
        dataset_variance_corrected = numpy.zeros_like(dataset_variance)
        dataset_sigma_corrected = numpy.zeros_like(dataset_variance)

    for index_frame, data_signal in enumerate(dataset_signal):
        if pre_caving:
            (
                data_signal_cupy,
                _,
            ) = _process_data_caving_cupy(
                data=data_signal,
                **params_caving_cupy,
            )

            if dataset_variance is not None:
                (
                    data_variance_cupy,
                    _,
                ) = _process_data_caving_cupy(
                    data=dataset_variance[index_frame],
                    **params_caving_cupy,
                )
            else:
                data_variance_cupy = None
        else:
            data_signal_cupy = cupy.asarray(data_signal)
            data_variance_cupy = None
            if dataset_variance is not None:
                data_variance_cupy = cupy.asarray(dataset_variance[index_frame])

        (
            data_signal_corrected_cupy,
            data_variance_corrected_cupy,
            data_sigma_corrected_cupy,
            signal_2scat_cupy,
        ) = _process_data_2scat_cupy(
            data_signal=data_signal_cupy,
            data_variance=data_variance_cupy,
            **params_2scat_cupy,
        )

        dataset_signal_corrected[index_frame] = data_signal_corrected_cupy.get()
        dataset_signal_2scat[index_frame] = signal_2scat_cupy.get()
        if data_variance_corrected_cupy is not None:
            dataset_variance_corrected[index_frame] = data_variance_corrected_cupy.get()
        if data_sigma_corrected_cupy is not None:
            dataset_sigma_corrected[index_frame] = data_sigma_corrected_cupy.get()
    log_allocated_gpu_memory()
    return (
        dataset_signal_corrected,
        dataset_variance_corrected,
        dataset_sigma_corrected,
        dataset_signal_2scat,
    )


def _process_data_2scat_cupy(
    data_signal: numpy.ndarray,
    array_window_cupy: numpy.ndarray,  # already shifted window
    center_x: int,
    center_y: int,
    window_roi_size: int = 120,
    dummy: Optional[int] = -10,
    data_variance: Optional[numpy.ndarray] = None,
    clip_data: bool = True,
    mask_clip_cupy: Optional[numpy.ndarray] = None,
    **kwargs: Optional[dict],
) -> Tuple[Optional[numpy.ndarray], Optional[numpy.ndarray]]:
    data_signal_cupy = None
    if isinstance(data_signal, cupy.ndarray):
        data_signal_cupy = data_signal
    elif isinstance(data_signal, numpy.ndarray):
        data_signal_cupy = cupy.asarray(data_signal)

    data_variance_cupy = None
    if data_variance is not None:
        if isinstance(data_variance, cupy.ndarray):
            data_variance_cupy = data_variance
        elif isinstance(data_variance, numpy.ndarray):
            data_variance_cupy = cupy.asarray(data_variance)

    # 1) Slice the original data around the center, this will be the convolution kernel
    subdata_signal_cupy = data_signal_cupy[
        center_y - window_roi_size : center_y + window_roi_size,
        center_x - window_roi_size : center_x + window_roi_size,
    ].copy()

    # 2) Cover the dummy values in the subdataset (dummy values jeopardize the convolution)
    cupy.copyto(subdata_signal_cupy, 0.0, where=subdata_signal_cupy == dummy)

    # 3) Perform the convolution
    signal_2scat_cupy = oaconvolve_cupy(
        array_window_cupy, subdata_signal_cupy, mode="same"
    )

    # 4) Calculate the corrected signal, variance and sigma
    data_signal_corrected_cupy = cupy.where(
        data_signal_cupy <= 0.0, data_signal_cupy, data_signal_cupy - signal_2scat_cupy
    )
    if data_variance_cupy is not None:
        data_variance_corrected_cupy = cupy.where(
            data_variance_cupy <= 0.0,
            data_variance_cupy,
            data_variance_cupy + signal_2scat_cupy + 0.0,
        )
        data_sigma_corrected_cupy = cupy.where(
            data_variance_corrected_cupy <= 0.0,
            data_variance_corrected_cupy,
            cupy.sqrt(data_variance_corrected_cupy),
        )
    else:
        data_variance_corrected_cupy = None
        data_sigma_corrected_cupy = None

    # 5) Clip the data that could not be corrected
    if clip_data:
        cupy.copyto(data_signal_corrected_cupy, dummy, where=mask_clip_cupy)
        if data_variance_corrected_cupy is not None:
            cupy.copyto(data_variance_corrected_cupy, dummy, where=mask_clip_cupy)
        if data_sigma_corrected_cupy is not None:
            cupy.copyto(data_sigma_corrected_cupy, dummy, where=mask_clip_cupy)

    return (
        data_signal_corrected_cupy,
        data_variance_corrected_cupy,
        data_sigma_corrected_cupy,
        signal_2scat_cupy,
    )


def process_dataset_2scat(
    dataset_signal: numpy.ndarray,
    filename_window_wagon: str,
    Center_1: float,
    Center_2: float,
    WindowRoiSize: int = 120,
    Dummy: Optional[int] = -10,
    dataset_variance: Optional[numpy.ndarray] = None,
    algorithm: str = "numpy",
    clip_data: bool = True,
    pre_caving: bool = True,
    **kwargs: Optional[dict],
) -> Tuple[Optional[numpy.ndarray], Optional[numpy.ndarray]]:
    """
    Calculate the secondary scattering correction for the given dataset.

    Parameters:
        dataset (numpy.ndarray): The input dataset to be corrected.
        window_pattern (str): Path to the window pattern file.
        window_roi_size (int): Distance to extract subdata for correction.
        center_x (Optional[float], optional): X-coordinate of the center. Defaults to None.
        center_y (Optional[float], optional): Y-coordinate of the center. Defaults to None.
        dummy (int, optional): Dummy value for masked regions. Defaults to -10.
        use_cupy (bool, optional): Whether to use CuPy for GPU acceleration. Defaults to True.

    Returns:
        Tuple[Optional[numpy.ndarray], Optional[numpy.ndarray]]: The corrected dataset and the secondary scattering.
    """
    dataset_signal_corrected = None
    dataset_variance_corrected = None
    dataset_sigma_corrected = None
    dataset_2scat_correction = None

    results = (
        dataset_signal_corrected,
        dataset_variance_corrected,
        dataset_sigma_corrected,
        dataset_2scat_correction,
    )

    if dataset_signal is None:
        logger.error("Dataset is None. Sec. scattering correction cannot be performed")
        return results

    if dataset_signal.ndim not in (2, 3):
        logger.error(
            f"Dataset with shape {dataset_signal.shape} must be 2 or 3-dimensional"
        )
        return results

    # Load the additional data
    if filename_window_wagon is None:
        logger.error(
            "Window pattern data is None. Cannot perform secondary scattering correction"
        )
        return results

    binning = kwargs.get("binning")
    data_signal_shape = dataset_signal[0].shape
    array_window = load_data(
        filename=filename_window_wagon,
        binning=binning,
        data_signal_shape=data_signal_shape,
    )
    if array_window is None:
        logger.error(
            f"{filename_window_wagon} could not be loaded. Cannot perform secondary scattering correction"
        )
        return results

    if algorithm not in ALGORITHMS_AVAILABLE:
        logger.warning(
            f"Algorithm '{algorithm}' is not available. Using '{DEFAULT_ALGORITHM}' instead."
        )
        algorithm = DEFAULT_ALGORITHM
    elif algorithm == "cupy" and not CUPY_AVAILABLE:
        logger.warning(f"CuPy is not available. Using {DEFAULT_ALGORITHM} instead.")
        algorithm = DEFAULT_ALGORITHM

    params_2scat = {
        "dataset_signal": dataset_signal,
        "dataset_variance": dataset_variance,
        "Center_1": Center_1,
        "Center_2": Center_2,
        "array_window": array_window,
        "WindowRoiSize": WindowRoiSize,
        "Dummy": Dummy,
        "clip_data": clip_data,
        "pre_caving": pre_caving,
        **kwargs,
    }

    results = ALGORITHMS_AVAILABLE[algorithm]["algorithm"](**params_2scat)
    return results


ALGORITHMS_AVAILABLE = {
    "numpy": {"algorithm": _process_dataset_2scat_numpy, "use_cupy": False},
    "cupy": {"algorithm": _process_dataset_2scat_cupy, "use_cupy": True},
}
DEFAULT_ALGORITHM = "numpy"
