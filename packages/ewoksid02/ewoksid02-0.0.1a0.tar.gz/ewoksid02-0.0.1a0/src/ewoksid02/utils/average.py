import logging
from typing import List, Optional, Tuple

import numexpr
import numpy

logger = logging.getLogger(__name__)


def get_centrosymmetric_limits(azimuth_range: List[float]) -> Tuple[List[float], ...]:
    """
    Calculate the centrosymmetric limits for a given azimuth range.

    Inputs:
        azimuth_range (List[float]): The azimuth range as a list of two values.
    Outputs:
        Tuple[List[float], ...]: A tuple containing one or two lists of centrosymmetric limits.
    """
    if azimuth_range[0] == azimuth_range[1]:
        return ([-180, 180],)

    lim = numpy.array(azimuth_range)
    if lim.prod() <= 0:
        lim = max(abs(lim))
        return ([max(-lim, -180), min(lim, 180)],)
    else:
        a = min(max(abs(lim)), 180)
        b = max(min(abs(lim)), -180)
        return ([-a, -b], [b, a])


def get_array_limit(
    azimuth_range: List[float], azimuth_array: numpy.ndarray
) -> Tuple[int, int]:
    """
    Get the array indices corresponding to the azimuth range.

    Inputs:
        azimuth_range (List[float]): The azimuth range as a list of two values.
        azimuth_array (numpy.ndarray): The array of azimuth values.
    Outputs:
        Tuple[int, int]: The indices corresponding to the azimuth range.
    """
    arg_min = numpy.argmin(abs(azimuth_array - azimuth_range[0]))
    arg_max = numpy.argmin(abs(azimuth_array - azimuth_range[1]))
    return (arg_min, arg_max)


def calculate_average(
    dataset_intensity: Optional[numpy.ndarray],
    dataset_sum_signal: Optional[numpy.ndarray] = None,
    dataset_sum_norm: Optional[numpy.ndarray] = None,
    dataset_sum_variance: Optional[numpy.ndarray] = None,
    array_ranges: Optional[List[Tuple[int, int]]] = None,
    Dummy: int = -10,
    calculate_variance: bool = False,
) -> Tuple[
    Optional[numpy.ndarray],
    Optional[numpy.ndarray],
    Optional[numpy.ndarray],
    Optional[numpy.ndarray],
]:
    """
    Calculate the average intensity, signal normalization, variance, and sigma for a dataset.

    Inputs:
        dataset_intensity (Optional[numpy.ndarray]): The intensity dataset.
        dataset_sum_signal (Optional[numpy.ndarray], optional): The sum signal dataset. Defaults to None.
        dataset_sum_norm (Optional[numpy.ndarray], optional): The sum normalization dataset. Defaults to None.
        dataset_sum_variance (Optional[numpy.ndarray], optional): The sum variance dataset. Defaults to None.
        array_ranges (Optional[List[Tuple[int, int]]], optional): The ranges for averaging. Defaults to None.
        Dummy (int, optional): The dummy value to replace invalid data. Defaults to -10.
    Outputs:
        Tuple[Optional[numpy.ndarray], Optional[numpy.ndarray], Optional[numpy.ndarray], Optional[numpy.ndarray]]:
        The average intensity, signal normalization, variance, and sigma datasets.
    """
    sum_signal = None
    sum_norm = None
    sum_variance = None
    dataset_average_intensity = numpy.zeros(
        (dataset_intensity.shape[0], dataset_intensity.shape[-1])
    )
    dataset_average_signal_norm = numpy.zeros_like(dataset_average_intensity)
    dataset_average_variance = numpy.zeros_like(dataset_average_intensity)
    dataset_average_sigma = numpy.zeros_like(dataset_average_intensity)

    if dataset_sum_signal is not None:
        sum_signal = numpy.zeros(
            (dataset_sum_signal.shape[0], dataset_sum_signal.shape[-1])
        )
    if dataset_sum_norm is not None:
        sum_norm = numpy.zeros((dataset_sum_norm.shape[0], dataset_sum_norm.shape[-1]))
    if dataset_sum_variance is not None:
        sum_variance = numpy.zeros(
            (dataset_sum_variance.shape[0], dataset_sum_variance.shape[-1])
        )
    array_ranges = array_ranges or [(0, -1)]

    mask_slice = numpy.zeros_like(dataset_intensity)
    for array_range in array_ranges:
        if not isinstance(array_range, (list, tuple)):
            logger.error(f"Array range {array_range} is not a list or tuple.")
            continue

        if len(array_range) != 2:
            logger.error(
                f"Array range {array_range} is not valid. It should contain two elements."
            )
            continue

        lim_0 = int(array_range[0])
        lim_1 = int(array_range[1])

        mask_slice[:, lim_0:lim_1, :] = 1

    logger.warning(f"{Dummy=}")
    dataset_average_intensity = numexpr.evaluate(
        "where(mask_slice == 0, Dummy, dataset_intensity)"
    )
    dataset_average_intensity[dataset_average_intensity == Dummy] = numpy.nan
    dataset_average_intensity = numpy.nanmean(dataset_average_intensity, axis=1)

    if dataset_sum_signal is not None:
        sum_signal = numexpr.evaluate(
            "where(mask_slice == 0, Dummy, dataset_sum_signal)"
        )
        sum_signal[sum_signal == Dummy] = numpy.nan
        sum_signal = numpy.nansum(sum_signal, axis=1)
    if dataset_sum_norm is not None:
        sum_norm = numexpr.evaluate("where(mask_slice == 0, Dummy, dataset_sum_norm)")
        sum_norm[sum_norm == Dummy] = numpy.nan
        sum_norm = numpy.nansum(sum_norm, axis=1)
    if dataset_sum_variance is not None:
        sum_variance = numexpr.evaluate(
            "where(mask_slice == 0, Dummy, dataset_sum_variance)"
        )
        sum_variance[sum_variance == Dummy] = numpy.nan
        sum_variance = numpy.nansum(sum_variance, axis=1)

    if sum_signal is not None and sum_norm is not None:
        dataset_average_signal_norm = numexpr.evaluate(
            "where(sum_norm <= 0.0, sum_norm, sum_signal / sum_norm)"
        )

    if sum_variance is not None and sum_norm is not None:
        dataset_average_variance = numexpr.evaluate(
            "where(sum_norm <= 0.0, sum_norm, sum_variance / (sum_norm * sum_norm))"
        )
        dataset_average_sigma = numexpr.evaluate(
            "where(sum_norm <= 0.0, sum_norm, sqrt(sum_variance) / sum_norm)"
        )

    return (
        dataset_average_intensity,
        dataset_average_signal_norm,
        dataset_average_variance,
        dataset_average_sigma,
    )
