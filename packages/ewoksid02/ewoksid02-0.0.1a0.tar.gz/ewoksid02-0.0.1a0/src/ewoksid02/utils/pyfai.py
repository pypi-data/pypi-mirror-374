import logging
from typing import Dict, Optional

import h5py
import numexpr
import numpy
from pyFAI import detector_factory
from pyFAI.method_registry import IntegrationMethod, Method
from pyFAI.worker import Worker

from ewoksid02.utils.io import get_from_headers, load_data

from .normalization import AzimuthalIntegrator

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

AIS = None
MAXIMUM_AIS = 5
WORKERS = None
MAXIMUM_WORKERS = 5
DISTORTION_WORKERS = None
MAXIMUM_DISTORTION_WORKERS = 5
POLARIZATION = None
DARK_CURRENT = None
FLAT_FIELD = None
MASK_GAPS = None


def get_detector_instance(
    dataset: numpy.ndarray,
    psize_1: float,
    psize_2: float,
) -> Optional[object]:
    """
    Create a detector instance based on the dataset and pixel sizes.

    Parameters:
        dataset (numpy.ndarray): The input dataset.
        psize_1 (float): Pixel size in the first dimension.
        psize_2 (float): Pixel size in the second dimension.

    Returns:
        Optional[object]: A detector instance or None if the dataset is None.
    """
    if dataset is None:
        return

    array_shape = dataset[0].shape
    detector_config = {
        "pixel1": psize_2,
        "pixel2": psize_1,
        "max_shape": array_shape,
    }
    return detector_factory(name="detector", config=detector_config)


def create_azimuthal_integrator(ai_kwargs: Dict) -> AzimuthalIntegrator:
    """
    Create an AzimuthalIntegrator instance with the given parameters.

    Parameters:
        ai_kwargs (Dict): Keyword arguments for the AzimuthalIntegrator.

    Returns:
        AzimuthalIntegrator: The created AzimuthalIntegrator instance.
    """
    ai = AzimuthalIntegrator(**ai_kwargs)
    ai.solidAngleArray(absolute=False)
    return ai


def get_persistent_azimuthal_integrator(
    dataset: numpy.ndarray,
    headers: dict = None,
    metadata_parameters_group: h5py.Group = None,
    **kwargs,
):
    if dataset is None:
        return

    params_headers = {
        "headers": headers,
        "metadata_file_group": metadata_parameters_group,
    }

    SampleDistance = kwargs.get("SampleDistance")
    if SampleDistance is None:
        SampleDistance = get_from_headers(key="SampleDistance", **params_headers)
    Center_1 = kwargs.get("Center_1")
    if Center_1 is None:
        Center_1 = get_from_headers(key="Center_1", **params_headers)
    Center_2 = kwargs.get("Center_2")
    if Center_2 is None:
        Center_2 = get_from_headers(key="Center_2", **params_headers)
    PSize_1 = kwargs.get("PSize_1")
    if PSize_1 is None:
        PSize_1 = get_from_headers(key="PSize_1", **params_headers)
    PSize_2 = kwargs.get("PSize_2")
    if PSize_2 is None:
        PSize_2 = get_from_headers(key="PSize_2", **params_headers)
    BSize_1 = kwargs.get("BSize_1")
    if BSize_1 is None:
        BSize_1 = get_from_headers(key="BSize_1", **params_headers)
    BSize_2 = kwargs.get("BSize_2")
    if BSize_2 is None:
        BSize_2 = get_from_headers(key="BSize_2", **params_headers)
    wavelength = kwargs.get("WaveLength")
    if wavelength is None:
        wavelength = get_from_headers(key="WaveLength", **params_headers)
    rot1 = kwargs.get("DetectorRotation_2")
    if rot1 is None:
        rot1 = get_from_headers(key="DetectorRotation_2", **params_headers)
    rot2 = kwargs.get("DetectorRotation_1")
    if rot2 is None:
        rot2 = get_from_headers(key="DetectorRotation_1", **params_headers)
    rot3 = kwargs.get("DetectorRotation_3")
    if rot3 is None:
        rot3 = get_from_headers(key="DetectorRotation_3", **params_headers)

    if BSize_1 != 1 or BSize_2 != 1:
        logger.warning(f"Binning is activated in this detector: ({BSize_1}, {BSize_2})")

    detector = get_detector_instance(
        dataset=dataset,
        psize_1=PSize_1,
        psize_2=PSize_2,
    )

    ai_kwargs = {
        "dist": SampleDistance,
        "poni1": Center_2 * PSize_2,
        "poni2": Center_1 * PSize_1,
        "rot1": rot1,
        "rot2": rot2,
        "rot3": rot3,
        "wavelength": wavelength,
        "detector": detector,
    }

    global AIS
    if AIS is None:
        logger.info("No cached Integrators. Instatiating a new AzimuthalIntegrator...")
        ai = create_azimuthal_integrator(ai_kwargs)
        AIS = [
            {
                "AI": ai,
                "AI_CONFIG": ai_kwargs,
            }
        ]
        logger.info(ai)
        logger.info(f"Cached integrators: {len(AIS)}")
        return AIS[0]["AI"]
    else:
        for ai in AIS:
            if ai_kwargs == ai["AI_CONFIG"]:
                logger.info(
                    f"Re-using AzimuthalIntegrator... Cached integrators: {len(AIS)}"
                )
                return ai["AI"]

        logger.info("New poni parameters. Instatiating the new AzimuthalIntegrator...")
        new_ai = create_azimuthal_integrator(ai_kwargs)
        AIS.append({"AI": new_ai, "AI_CONFIG": ai_kwargs})

        if len(AIS) > MAXIMUM_AIS:
            logger.info(
                "Reached maximum number of AzimuthalIntegrators. The oldest one is popped out"
            )
            _ = AIS.pop(0)

        logger.info(f"Cached integrators: {len(AIS)}")
        return new_ai


def get_gpu_method():
    if (
        IntegrationMethod.select_method(dim=1, split="full", algo="csr", impl="opencl")[
            0
        ].impl
        == "OpenCL"
    ):
        return Method(dim=2, split="full", algo="csr", impl="opencl", target=(0, 0))
    return Method(dim=2, split="full", algo="csr", impl="cython", target=None)


def create_new_worker(azimuthal_integrator, integration_options={}):
    method = integration_options.get("method", get_gpu_method())
    worker = Worker(
        azimuthalIntegrator=azimuthal_integrator,
        shapeIn=azimuthal_integrator.detector.shape,
        shapeOut=(
            integration_options["npt2_azim"],
            integration_options["npt2_rad"],
        ),
        unit=integration_options["unit"],
        dummy=integration_options["dummy"],
        delta_dummy=integration_options["delta_dummy"],
        method=method,
    )
    worker.correct_solid_angle = False
    worker.output = "raw"
    worker.error_model = "azimuthal"
    worker.ai.empty = worker.dummy

    config_worker = {
        # integration options
        "npt2_rad": worker.nbpt_rad,
        "npt2_azim": worker.nbpt_azim,
        "unit": str(worker.unit),
        "dummy": worker.dummy,
        "delta_dummy": worker.delta_dummy,
        "method": method,
    }
    config_ai = {
        # poni parameters
        "dist": azimuthal_integrator.dist,
        "poni1": azimuthal_integrator.poni1,
        "poni2": azimuthal_integrator.poni2,
        "rot1": azimuthal_integrator.rot1,
        "rot2": azimuthal_integrator.rot2,
        "rot3": azimuthal_integrator.rot3,
        "wavelength": azimuthal_integrator.wavelength,
        "detector_shape": azimuthal_integrator.detector.shape,
        "pixel1": azimuthal_integrator.detector.pixel1,
        "pixel2": azimuthal_integrator.detector.pixel2,
    }
    return worker, {**config_worker, **config_ai}


def applied_mask_worker(worker, mask_filename, binning=(1, 1), data_signal_shape=None):
    if mask_filename is None:
        worker.mask_image = None
        worker.ai.set_mask(None)
    else:
        if isinstance(mask_filename, (list, tuple)):
            mask = numpy.zeros(worker.shape)
            for file in mask_filename:
                mask += load_data(
                    filename=file, binning=binning, data_signal_shape=data_signal_shape
                )
        else:
            mask = load_data(
                filename=mask_filename,
                binning=binning,
                data_signal_shape=data_signal_shape,
            )
            worker.set_mask_file(mask_filename)

        mask[mask < 0] = 1
        worker.mask_image = mask
        worker.ai.set_mask(mask)
    return worker


def get_persistent_pyfai_worker(
    azimuthal_integrator,
    filename_mask=None,
    integration_options={},
    npt2_rad=None,
    npt2_azim=None,
    unit=None,
    dummy=None,
    delta_dummy=None,
    method=get_gpu_method(),
    binning=(1, 1),
    **kwargs,
):

    # integration options
    applied_integration_options = {
        "npt2_rad": int(npt2_rad),
        "npt2_azim": int(npt2_azim),
        "unit": unit,
        "dummy": dummy,
        "delta_dummy": delta_dummy,
        "method": (
            (method.split, method.algo, method.impl)
            if isinstance(method, (IntegrationMethod, Method))
            else method
        ),
    }
    applied_integration_options.update(**integration_options)

    # poni parameters
    config_ai = {
        "dist": azimuthal_integrator.dist,
        "poni1": azimuthal_integrator.poni1,
        "poni2": azimuthal_integrator.poni2,
        "rot1": azimuthal_integrator.rot1,
        "rot2": azimuthal_integrator.rot2,
        "rot3": azimuthal_integrator.rot3,
        "wavelength": azimuthal_integrator.wavelength,
        "detector_shape": azimuthal_integrator.detector.shape,
        "pixel1": azimuthal_integrator.detector.pixel1,
        "pixel2": azimuthal_integrator.detector.pixel2,
    }

    incoming_config = {**applied_integration_options, **config_ai}

    global WORKERS
    if WORKERS is None:
        logger.info("No cached pyFAI workers. Instantiating a new worker")
        worker, worker_config = create_new_worker(
            azimuthal_integrator=azimuthal_integrator,
            integration_options=applied_integration_options,
        )
        WORKERS = [
            {
                "WORKER": worker,
                "WORKER_CONFIG": worker_config,
            }
        ]
        logger.info(f"Cached pyFAI workers: {len(WORKERS)}")
        worker = applied_mask_worker(
            worker=worker,
            mask_filename=filename_mask,
            binning=binning,
            data_signal_shape=azimuthal_integrator.detector.shape,
        )
        return worker
    else:
        logger.info("Cached pyFAI workers found. Checking for existing worker...")
        for worker_ in WORKERS:
            worker = worker_["WORKER"]
            worker_config = worker_["WORKER_CONFIG"]
            if worker_config == incoming_config:
                logger.info("Re-using a pyFAI worker")
                worker = applied_mask_worker(
                    worker=worker,
                    mask_filename=filename_mask,
                    binning=binning,
                    data_signal_shape=azimuthal_integrator.detector.shape,
                )
                logger.info(f"Cached pyFAI workers: {len(WORKERS)}")
                return worker

        logger.info("New config parameters. Instatiating a new pyFAI worker...")
        new_worker, new_worker_config = create_new_worker(
            azimuthal_integrator=azimuthal_integrator,
            integration_options=applied_integration_options,
        )

        WORKERS.append(
            {
                "WORKER": new_worker,
                "WORKER_CONFIG": new_worker_config,
            }
        )

        new_worker = applied_mask_worker(
            worker=new_worker,
            mask_filename=filename_mask,
            binning=binning,
            data_signal_shape=azimuthal_integrator.detector.shape,
        )

        if len(WORKERS) > MAXIMUM_WORKERS:
            logger.info(
                "Reached maximum number of pyFAI worker. The oldest one is popped out"
            )
            _ = WORKERS.pop(0)

        logger.info(f"Cached pyFAI workers: {len(WORKERS)}")
        return new_worker


def process_dataset_azim(
    dataset_signal: numpy.ndarray,
    azimuthal_integrator: AzimuthalIntegrator,
    dataset_variance: numpy.ndarray = None,
    filename_dark: str = None,
    filename_mask: str = None,
    npt2_rad: int = None,
    npt2_azim: int = None,
    unit: str = None,
    Dummy: int = None,
    DDummy: int = None,
    method: str = None,
    datatype: str = "float32",
    **kwargs,
):
    dataset_signal_azim = None
    dataset_variance_azim = None
    dataset_sigma_azim = None
    dataset_sumsignal_azim = None
    dataset_sumnorm_azim = None
    dataset_sumvariance_azim = None

    do_variance_formula = kwargs.get("do_variance_formula")
    variance_formula = kwargs.get("variance_formula")
    if dataset_variance is not None:
        ...
    elif dataset_variance is None and do_variance_formula and variance_formula:
        variance_function = numexpr.NumExpr(
            variance_formula, [("data", datatype), ("dark", datatype)]
        )
        dark = load_data(filename=filename_dark) if filename_dark else None
        dataset_variance = numpy.zeros_like(dataset_signal, dtype=datatype)
        for frame_index, data_signal in enumerate(dataset_signal):
            dataset_variance[frame_index] = variance_function(
                data_signal, 0 if dark is None else dark
            )

    worker = get_persistent_pyfai_worker(
        azimuthal_integrator=azimuthal_integrator,
        filename_mask=filename_mask,
        npt2_rad=npt2_rad,
        npt2_azim=npt2_azim,
        unit=unit,
        dummy=Dummy,
        delta_dummy=DDummy,
        method=method,
        **kwargs,
    )
    output_dataset_shape = (
        len(dataset_signal),
        worker.nbpt_azim,
        worker.nbpt_rad,
    )

    dataset_signal_azim = numpy.zeros(output_dataset_shape, dtype=datatype)
    dataset_sumsignal_azim = numpy.zeros(output_dataset_shape, dtype=datatype)
    dataset_sumnorm_azim = numpy.zeros(output_dataset_shape, dtype=datatype)

    if dataset_variance is not None:
        dataset_variance_azim = numpy.zeros(output_dataset_shape, dtype=datatype)
        dataset_sigma_azim = numpy.zeros(output_dataset_shape, dtype=datatype)
        dataset_sumvariance_azim = numpy.zeros(output_dataset_shape, dtype=datatype)

    logger.info(f"PyFAI worker used method: {worker.method}")
    for frame_index, data_signal in enumerate(dataset_signal):
        if dataset_variance is not None:
            data_variance = dataset_variance[frame_index]
        else:
            data_variance = None

        result2d_azim = worker.process(
            data=data_signal,
            variance=data_variance,
        )

        dataset_signal_azim[frame_index] = (
            result2d_azim.intensity
        )  # (sum_signal / sum_normalization)
        dataset_sumsignal_azim[frame_index] = result2d_azim.sum_signal
        dataset_sumnorm_azim[frame_index] = result2d_azim.sum_normalization

        if data_variance is not None:
            sum_var = result2d_azim.sum_variance  # noqa
            sum_norm = result2d_azim.sum_normalization  # noqa
            dataset_variance_azim[frame_index] = numexpr.evaluate(
                f"where(sum_norm <= 0.0, {worker.dummy}, sum_var / (sum_norm * sum_norm))"
            )
            dataset_sigma_azim[frame_index] = result2d_azim.sigma
            dataset_sumvariance_azim[frame_index] = result2d_azim.sum_variance

    return (
        dataset_signal_azim,
        dataset_variance_azim,
        dataset_sigma_azim,
        dataset_sumsignal_azim,
        dataset_sumnorm_azim,
        dataset_sumvariance_azim,
        result2d_azim.radial,
        result2d_azim.azimuthal,
    )
