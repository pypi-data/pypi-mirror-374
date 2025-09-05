import logging
import os
import time
from typing import Optional

import numexpr
import numpy
from pyFAI.version import MAJOR

if MAJOR >= 2025:
    from pyFAI.integrator.azimuthal import AzimuthalIntegrator
else:
    from pyFAI.azimuthalIntegrator import AzimuthalIntegrator
try:
    import cupy

    from .cupyutils import log_allocated_gpu_memory
except ImportError:
    cupy = None
    CUPY_AVAILABLE = False
    CUPY_MEM_POOL = None
else:
    CUPY_AVAILABLE = True
    CUPY_MEM_POOL = cupy.get_default_memory_pool()


from .io import load_data

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

PERSISTENT_NORMALIZATION = None


def _get_persistent_normalization_params(**kwargs):
    flat_filename = kwargs.get("flat_filename")
    mask_filename = kwargs.get("mask_filename")
    dark_filename = kwargs.get("dark_filename")
    azimuthal_integrator = kwargs.get("azimuthal_integrator")
    return {
        "flat_filename": flat_filename,
        "flat_mtime": os.path.getmtime(flat_filename) if flat_filename else None,
        "mask_filename": mask_filename,
        "mask_mtime": os.path.getmtime(mask_filename) if mask_filename else None,
        "dark_filename": dark_filename,
        "dark_mtime": os.path.getmtime(dark_filename) if dark_filename else None,
        "azimuthal_integrator": azimuthal_integrator,
        "polarization_factor": kwargs.get("polarization_factor"),
        "polarization_axis": kwargs.get("polarization_axis"),
        "ai_kwargs": {
            "dist": azimuthal_integrator.dist,
            "poni1": azimuthal_integrator.poni1,
            "poni2": azimuthal_integrator.poni2,
            "rot1": azimuthal_integrator.rot1,
            "rot2": azimuthal_integrator.rot2,
            "rot3": azimuthal_integrator.rot3,
            "wavelegth": azimuthal_integrator.wavelength,
            "detector": azimuthal_integrator.detector,
        },
    }


def _get_persistent_normalization_arrays(use_cupy=False, **kwargs):
    mask_filename = kwargs.get("mask_filename")
    flat_filename = kwargs.get("flat_filename")
    dark_filename = kwargs.get("dark_filename")
    polarization_factor = kwargs.get("polarization_factor")
    polarization_axis = kwargs.get("polarization_axis")
    azimuthal_integrator = kwargs.get("azimuthal_integrator")
    dummy = kwargs.get("dummy")
    delta_dummy = kwargs.get("delta_dummy")
    datatype = kwargs.get("datatype")
    binning = kwargs.get("binning", (1, 1))
    data_signal_shape = azimuthal_integrator.detector.shape

    array_mask = (
        load_data(
            filename=mask_filename, binning=binning, data_signal_shape=data_signal_shape
        )
        if mask_filename
        else None
    )
    array_flat = (
        load_data(
            filename=flat_filename, binning=binning, data_signal_shape=data_signal_shape
        )
        if flat_filename
        else None
    )
    array_dark = (
        load_data(
            filename=dark_filename, binning=binning, data_signal_shape=data_signal_shape
        )
        if dark_filename
        else None
    )

    if array_mask is not None and dummy is not None and delta_dummy is not None:
        if array_flat is not None:
            if delta_dummy == 0:
                array_mask |= array_flat == dummy
            else:
                array_mask |= abs(array_flat - dummy) < delta_dummy
        if array_dark is not None:
            if delta_dummy == 0:
                array_mask |= array_dark == dummy
            else:
                array_mask |= abs(array_dark - dummy) < delta_dummy

    array_polarization = azimuthal_integrator.polarization(
        factor=polarization_factor,
        axis_offset=polarization_axis,
    )
    array_solidangle = azimuthal_integrator.solidAngleArray()

    # Patch due to inconsistent chiArray and position_array methods in pyFAI
    if "chi_center" in azimuthal_integrator._cached_array:
        azimuthal_integrator._cached_array.pop("chi_center")

    persistent_arrays = {
        "polarization": array_polarization,
        "polarization_cupy": None,
        "flatfield": array_flat,
        "flatfield_cupy": None,
        "dark": array_dark,
        "dark_cupy": None,
        "mask": array_mask,
        "mask_cupy": None,
        "solidangle": array_solidangle,
        "solidangle_cupy": None,
        "normalization_cupy": None,
    }

    if use_cupy and CUPY_AVAILABLE:
        array_normalization = numpy.ones(
            azimuthal_integrator.detector.shape, dtype=datatype
        )

        if array_polarization is not None:
            persistent_arrays["polarization_cupy"] = cupy.asarray(array_polarization)
            array_normalization *= array_polarization
        if array_flat is not None:
            persistent_arrays["flatfield_cupy"] = cupy.asarray(array_flat)
            array_normalization *= array_flat
        if array_solidangle is not None:
            persistent_arrays["solidangle_cupy"] = cupy.asarray(array_solidangle)
            array_normalization *= array_solidangle
        if array_mask is not None:
            persistent_arrays["mask_cupy"] = cupy.asarray(array_mask)
        persistent_arrays["normalization_cupy"] = cupy.asarray(
            array_normalization  # not masked yet
        )

        if array_dark is not None:
            persistent_arrays["dark_cupy"] = cupy.asarray(array_dark)

    return persistent_arrays


def calculate_persistent_normalization_array(
    azimuthal_integrator: AzimuthalIntegrator,
    mask_array: numpy.ndarray = None,
    polarization_array: numpy.ndarray = None,
    flat_field_array: numpy.ndarray = None,
    solid_angle_array: numpy.ndarray = None,
    dummy: float = -10,
    datatype: str = "float32",
    **kwargs,
):
    normalization_array = numpy.ones(
        azimuthal_integrator.detector.shape,
        dtype=datatype,
    )
    if polarization_array is not None:
        normalization_array *= polarization_array
    if flat_field_array is not None:
        normalization_array *= flat_field_array
    if solid_angle_array is not None:
        normalization_array *= solid_angle_array
    if mask_array is not None:
        normalization_array = numpy.where(mask_array, dummy, normalization_array)
    return normalization_array


def get_persistent_normalization_arrays(
    azimuthal_integrator: AzimuthalIntegrator,
    flat_filename: str = None,
    mask_filename: str = None,
    dark_filename: str = None,
    polarization_factor: float = 1.0,
    polarization_axis: int = 0,
    dummy: float = -10,
    delta_dummy: float = 0.01,
    datatype: str = "float32",
    use_cupy: bool = False,
    binning: tuple = (1, 1),
):
    global PERSISTENT_NORMALIZATION

    persistent_params = {
        "azimuthal_integrator": azimuthal_integrator,
        "flat_filename": flat_filename,
        "mask_filename": mask_filename,
        "dark_filename": dark_filename,
        "polarization_factor": polarization_factor,
        "polarization_axis": polarization_axis,
        "dummy": dummy,
        "delta_dummy": delta_dummy,
        "datatype": datatype,
        "binning": binning,
    }

    if PERSISTENT_NORMALIZATION is None:
        logger.info("No cached normalization. Instantiating a new one...")
        PERSISTENT_NORMALIZATION = {}
        PERSISTENT_NORMALIZATION["params"] = _get_persistent_normalization_params(
            **persistent_params
        )
        PERSISTENT_NORMALIZATION["arrays"] = _get_persistent_normalization_arrays(
            use_cupy=use_cupy, **persistent_params
        )
        PERSISTENT_NORMALIZATION["use_cupy"] = use_cupy
    else:
        if (
            PERSISTENT_NORMALIZATION["params"]["flat_filename"] != flat_filename
            or (
                flat_filename
                and PERSISTENT_NORMALIZATION["params"]["flat_mtime"]
                != os.path.getmtime(flat_filename)
            )
            or PERSISTENT_NORMALIZATION["params"]["mask_filename"] != mask_filename
            or (
                mask_filename
                and PERSISTENT_NORMALIZATION["params"]["mask_mtime"]
                != os.path.getmtime(mask_filename)
            )
            or PERSISTENT_NORMALIZATION["params"]["dark_filename"] != dark_filename
            or (
                dark_filename
                and PERSISTENT_NORMALIZATION["params"]["dark_mtime"]
                != os.path.getmtime(dark_filename)
            )
            or PERSISTENT_NORMALIZATION["params"]["polarization_factor"]
            != polarization_factor
            or PERSISTENT_NORMALIZATION["params"]["polarization_axis"]
            != polarization_axis
            or PERSISTENT_NORMALIZATION["params"]["ai_kwargs"]
            != {
                "dist": azimuthal_integrator.dist,
                "poni1": azimuthal_integrator.poni1,
                "poni2": azimuthal_integrator.poni2,
                "rot1": azimuthal_integrator.rot1,
                "rot2": azimuthal_integrator.rot2,
                "rot3": azimuthal_integrator.rot3,
                "wavelegth": azimuthal_integrator.wavelength,
                "detector": azimuthal_integrator.detector,
            }
            or use_cupy != PERSISTENT_NORMALIZATION["use_cupy"]
        ):
            logger.info("New normalization parameters. Instantiating a new one...")
            PERSISTENT_NORMALIZATION["params"] = _get_persistent_normalization_params(
                **persistent_params
            )
            PERSISTENT_NORMALIZATION["arrays"] = _get_persistent_normalization_arrays(
                use_cupy=use_cupy, **persistent_params
            )
            PERSISTENT_NORMALIZATION["use_cupy"] = use_cupy
        else:
            logger.info("Re-using cached normalization parameters...")

    return PERSISTENT_NORMALIZATION["arrays"]


def normalize_dataset_cupy(
    dataset_signal: numpy.ndarray,
    dataset_variance: Optional[numpy.ndarray] = None,
    normalization_values: numpy.ndarray = None,
    array_dark_cupy=None,
    array_normalization_cupy=None,
    array_mask_cupy=None,
    dummy: float = -10,
    datatype: str = "float32",
    **kwargs,
):
    log_allocated_gpu_memory()
    t1 = time.perf_counter()
    dataset_normalized_signal = numpy.zeros_like(dataset_signal, dtype=datatype)
    dataset_normalized_variance = numpy.zeros_like(dataset_signal, dtype=datatype)
    dataset_normalized_sigma = numpy.zeros_like(dataset_signal, dtype=datatype)
    # logger.info(f"Time to initialize numpy output arrays: {t2 - t1:.2f} seconds")

    # One by one
    nb_frames = len(dataset_signal)
    if normalization_values is None:
        normalization_values = numpy.ones(nb_frames, dtype=datatype)
    elif isinstance(normalization_values, (int, float)):
        normalization_values = numpy.full(
            nb_frames, normalization_values, dtype=datatype
        )

    for index_frame, data_signal, normalization_factor in zip(
        range(nb_frames), dataset_signal, normalization_values
    ):
        data_signal_cu = cupy.asarray(data_signal, dtype=datatype)

        # Remove dark from raw (not from norm)
        if array_dark_cupy is not None:
            data_signal_cu -= array_dark_cupy

        if dataset_variance is not None:
            data_variance_cu = cupy.asarray(
                dataset_variance[index_frame], dtype=datatype
            )
        else:
            data_variance_cu = None

        # Get final normalization array
        normalization_array_cu_frame = array_normalization_cupy * normalization_factor

        # Normalize the signal
        data_signal_normalized_cu = cupy.where(
            normalization_array_cu_frame == 0.0,
            dummy,
            data_signal_cu / normalization_array_cu_frame,
        )
        # Normalize the variance and sigma
        if data_variance_cu is not None:
            data_variance_normalized_cu = cupy.where(
                normalization_array_cu_frame == 0.0,
                dummy,
                data_variance_cu
                / (normalization_array_cu_frame * normalization_array_cu_frame),
            )
            data_sigma_normalized_cu = cupy.where(
                normalization_array_cu_frame == 0.0,
                dummy,
                cupy.sqrt(data_variance_cu) / cupy.abs(normalization_array_cu_frame),
            )

        # Mask all results
        if array_mask_cupy is not None:
            data_signal_normalized_cu = cupy.where(
                array_mask_cupy, dummy, data_signal_normalized_cu
            )
            if data_variance_cu is not None:
                data_variance_normalized_cu = cupy.where(
                    array_mask_cupy, dummy, data_variance_normalized_cu
                )
                data_sigma_normalized_cu = cupy.where(
                    array_mask_cupy, dummy, data_sigma_normalized_cu
                )

        # Allocate numpy arrays in place
        dataset_normalized_signal[index_frame] = data_signal_normalized_cu.get()
        dataset_normalized_variance[index_frame] = data_variance_normalized_cu.get()
        dataset_normalized_sigma[index_frame] = data_sigma_normalized_cu.get()

    t3 = time.perf_counter()
    logger.info(f"Total time for normalization: {t3 - t1:.2f} seconds")
    log_allocated_gpu_memory()
    return (
        dataset_normalized_signal,
        dataset_normalized_variance,
        dataset_normalized_sigma,
    )


def normalize_dataset_cython(
    dataset_signal: numpy.ndarray,
    dataset_variance: Optional[numpy.ndarray] = None,
    normalization_values: numpy.ndarray = None,
    array_flat: numpy.ndarray = None,
    array_dark: numpy.ndarray = None,
    array_mask: numpy.ndarray = None,
    array_solidangle: numpy.ndarray = None,
    array_polarization: numpy.ndarray = None,
    Dummy: float = -10,
    DDummy: float = 0.01,
    datatype: str = "float32",
    **kwargs,
):
    from pyFAI.ext.preproc import preproc as preproc_cy

    dataset_normalized_signal = numpy.zeros_like(dataset_signal, dtype=datatype)
    dataset_normalized_variance = numpy.zeros_like(dataset_signal, dtype=datatype)
    dataset_normalized_sigma = numpy.zeros_like(dataset_signal, dtype=datatype)

    preproc_params = {
        "dark": array_dark,
        "flat": array_flat,
        "mask": array_mask,
        "solidangle": array_solidangle,
        "polarization": array_polarization,
        "absorption": None,
        "dummy": Dummy,
        "delta_dummy": DDummy,
        "empty": None,
    }

    nb_frames = len(dataset_signal)
    if normalization_values is None:
        normalization_values = numpy.ones(nb_frames, dtype=datatype)
    elif isinstance(normalization_values, (int, float)):
        normalization_values = numpy.full(
            nb_frames, normalization_values, dtype=datatype
        )

    for index_frame, data_signal, normalization_factor in zip(
        range(nb_frames), dataset_signal, normalization_values
    ):
        if dataset_variance is None:
            dataset_normalized_signal[index_frame] = preproc_cy(
                raw=data_signal,
                variance=None,
                normalization_factor=normalization_factor,
                **preproc_params,
            )
        else:
            proc_data = preproc_cy(
                raw=data_signal,
                variance=dataset_variance[index_frame],
                normalization_factor=normalization_factor,
                **preproc_params,
            )
            pp_signal = proc_data[:, :, 0]  # noqa
            pp_variance = proc_data[:, :, 1]  # noqa
            pp_normalisation = proc_data[:, :, 2]  # noqa

            dataset_normalized_signal[index_frame] = numexpr.evaluate(
                f"where(pp_normalisation == 0.0, {Dummy}, pp_signal / pp_normalisation)"
            )
            dataset_normalized_variance[index_frame] = numexpr.evaluate(
                f"where(pp_normalisation == 0.0, {Dummy}, pp_variance / (pp_normalisation * pp_normalisation))"
            )
            dataset_normalized_sigma[index_frame] = numexpr.evaluate(
                f"where(pp_normalisation == 0.0, {Dummy}, sqrt(pp_variance) / abs(pp_normalisation))"
            )

    return (
        dataset_normalized_signal,
        dataset_normalized_variance,
        dataset_normalized_sigma,
    )


ALGORITHMS_AVAILABLE = {
    "cython": {"algorithm": normalize_dataset_cython, "use_cupy": False},
    "cupy": {"algorithm": normalize_dataset_cupy, "use_cupy": True},
}
DEFAULT_ALGORITHM = "cython"


def normalize_dataset(
    azimuthal_integrator: AzimuthalIntegrator,
    dataset_signal: numpy.ndarray,
    normalization_values: numpy.ndarray = None,
    filename_mask: str = None,
    filename_dark: str = None,
    filename_flat: str = None,
    absorption=None,
    Dummy=None,
    DDummy=None,
    variance_formula=None,
    polarization_factor=0.99,
    polarization_axis_offset=0,
    datatype="float32",
    algorithm: str = "cython",
    **kwargs,
):
    if datatype in ("float32", numpy.float32):
        datatype = numpy.dtype("float32")
    elif datatype in ("float64", numpy.float64):
        datatype = numpy.dtype("float64")
    binning = kwargs.get("binning", (1, 1))

    dataset_variance = None
    data_signal_shape = dataset_signal[0].shape

    dark = (
        load_data(
            filename=filename_dark, binning=binning, data_signal_shape=data_signal_shape
        )
        if filename_dark
        else None
    )
    if variance_formula:
        variance_function = numexpr.NumExpr(
            variance_formula, [("data", numpy.float64), ("dark", numpy.float64)]
        )
        dataset_variance = variance_function(
            dataset_signal, 0 if dark is None else dark
        )

    if algorithm not in ALGORITHMS_AVAILABLE:
        logger.warning(
            f"Algorithm '{algorithm}' is not available. Using '{DEFAULT_ALGORITHM}' instead."
        )
        algorithm = DEFAULT_ALGORITHM
    elif algorithm == "cupy" and not CUPY_AVAILABLE:
        logger.warning(f"CuPy is not available. Using {DEFAULT_ALGORITHM} instead.")
        algorithm = DEFAULT_ALGORITHM

    logger.info(f"Performing normalization with algorithm: {algorithm}")
    t0 = time.perf_counter()

    persistent_normalization_arrays = get_persistent_normalization_arrays(
        azimuthal_integrator=azimuthal_integrator,
        flat_filename=filename_flat,
        mask_filename=filename_mask,
        dark_filename=filename_dark,
        polarization_factor=polarization_factor,
        polarization_axis=polarization_axis_offset,
        datatype=datatype,
        dummy=Dummy,
        delta_dummy=DDummy,
        use_cupy=ALGORITHMS_AVAILABLE[algorithm]["use_cupy"],
        binning=binning,
    )

    params_normalization = {
        "dataset_signal": dataset_signal,
        "dataset_variance": dataset_variance,
        "normalization_values": normalization_values,
        "array_flat": persistent_normalization_arrays["flatfield"],
        "array_dark": persistent_normalization_arrays["dark"],
        "array_mask": persistent_normalization_arrays["mask"],
        "array_solidangle": persistent_normalization_arrays["solidangle"],
        "array_polarization": persistent_normalization_arrays["polarization"],
        "array_dark_cupy": persistent_normalization_arrays["dark_cupy"],
        "array_normalization_cupy": persistent_normalization_arrays[
            "normalization_cupy"
        ],
        "array_mask_cupy": persistent_normalization_arrays["mask_cupy"],
        "dummy": Dummy,
        "delta_dummy": DDummy,
        "datatype": datatype,
    }

    (
        dataset_normalized_signal,
        dataset_normalized_variance,
        dataset_normalized_sigma,
    ) = ALGORITHMS_AVAILABLE[algorithm]["algorithm"](
        **params_normalization,
    )
    t1 = time.perf_counter()
    logger.info(
        f"Normalization completed in {t1 - t0:.2f} seconds using {algorithm} algorithm."
    )

    if dataset_normalized_variance is None:
        dataset_normalized_variance = numpy.zeros_like(dataset_signal, dtype=datatype)
    if dataset_normalized_sigma is None:
        dataset_normalized_sigma = numpy.zeros_like(dataset_signal, dtype=datatype)
    return (
        dataset_normalized_signal,
        dataset_normalized_variance,
        dataset_normalized_sigma,
    )


def calculate_normalization_values(
    monitor_values,
    azimuthal_integrator=None,
    psize_1=None,
    psize_2=None,
    dist=None,
    normalization_factor=None,
):
    if normalization_factor is None:
        normalization_factor = 1.0

    if azimuthal_integrator is not None:
        psize_1 = psize_1 or azimuthal_integrator.detector.pixel1
        psize_2 = psize_2 or azimuthal_integrator.detector.pixel2
        dist = dist or azimuthal_integrator.dist

    if monitor_values is None or psize_1 is None or psize_2 is None or dist is None:
        return normalization_factor

    solid_angle = psize_1 * psize_2 / dist**2
    return monitor_values * solid_angle / normalization_factor
