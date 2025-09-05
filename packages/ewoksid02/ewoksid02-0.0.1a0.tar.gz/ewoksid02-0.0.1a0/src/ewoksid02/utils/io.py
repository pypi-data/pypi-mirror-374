import logging
import os
import time
from typing import Dict, List, Optional, Union

import fabio
import h5py
import numpy

try:
    import cupy
except ImportError:
    CUPY_AVAILABLE = False
else:
    CUPY_AVAILABLE = True

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

KEY_PIXEL_SIZE_1 = "PSize_1"
KEY_PIXEL_SIZE_2 = "PSize_2"
KEY_BINNING_1 = "BSize_1"
KEY_BINNING_2 = "BSize_2"
KEY_WAVELENGTH = "WaveLength"
KEY_SAMPLEDETECTOR_DISTANCE = "SampleDistance"
KEY_NORMALIZATION_FACTOR = "NormalizationFactor"
KEY_DETECTOR_MASK_FOLDER = "DetectorMaskFilePath"
KEY_DETECTOR_MASK_FILE = "DetectorMaskFileName"
KEY_BEAMSTOP_MASK_FOLDER = "MaskFilePath"
KEY_BEAMSTOP_MASK_FILE = "MaskFileName"
KEY_POLARIZATION_FACTOR = "polarization_factor"
KEY_POLARIZATION_AXIS = "polarization_axis_offset"
KEY_VARIANCE_FORMULA = "variance_formula"
KEY_WINDOW_ROI_SIZE = "WindowRoiSize"
KEY_DARK_FOLDER = "DarkFilePath"
KEY_DARK_FILE = "DarkFileName"
KEY_FLAT_FOLDER = "FlatfieldFilePath"
KEY_FLAT_FILE = "FlatfieldFileName"
KEY_WINDOW_FOLDER = "WindowFilePath"
KEY_WINDOW_FILE = "WindowFileName"
KEY_DUMMY = "Dummy"
KEY_DELTA_DUMMY = "DDummy"
KEY_CENTER_1 = "Center_1"
KEY_CENTER_2 = "Center_2"
KEY_NPT2_RAD = "npt2_rad"
KEY_NPT2_AZIM = "npt2_azim"
KEY_UNIT = "unit"
KEY_TITLEEXTENSION = "TitleExtension"
KEY_ALGORITHM_NORMALIZATION = "NormAlgorithm"


def get_isotime(forceTime: Optional[float] = None) -> str:
    """
    Get the current time as an ISO8601 string.

    Inputs:
        - forceTime (Optional[float], optional): Enforce a given time (current by default). Defaults to None.
    Outputs:
        - str: The current time as an ISO8601 string.
    """
    if forceTime is None:
        forceTime = time.time()
    localtime = time.localtime(forceTime)
    gmtime = time.gmtime(forceTime)
    tz_h = localtime.tm_hour - gmtime.tm_hour
    tz_m = localtime.tm_min - gmtime.tm_min
    return "%s%+03i:%02i" % (time.strftime("%Y-%m-%dT%H:%M:%S", localtime), tz_h, tz_m)


def get_from_headers(
    key: str,
    headers: Optional[Dict[str, Union[str, float]]] = None,
    metadata_file_group: Optional[h5py.Group] = None,
    to_integer: bool = False,
) -> Optional[Union[str, float, int]]:
    """
    Retrieve a header value from the header object (for online processing) or from an HDF5 group (for offline processing).

    Inputs:
        - key (str): The key to retrieve.
        - headers (Optional[Dict[str, Union[str, float]]], optional): The header object. Defaults to None.
        - metadata_file_group (Optional[h5py.Group], optional): The HDF5 group. Defaults to None.
        - to_integer (bool, optional): Whether to convert the value to an integer. Defaults to False.
    Outputs:
        - Optional[Union[str, float, int]]: The retrieved value or None if not found.
    """
    value = None

    if headers:
        # Retrieve directly from the header object
        if key not in headers:
            logger.warning(f"Key {key} is not in headers")
            return
        value = headers[key]
    elif metadata_file_group:
        # Retrieve from a group in the metadata file
        if key not in metadata_file_group:
            logger.warning(f"Key {key} not in {metadata_file_group}")
            return
        value = metadata_file_group[key][()]
    else:
        return

    if isinstance(value, bytes):
        value = value.decode("UTF-8")
    try:
        value = float(value)
        if to_integer:
            return int(value)
        return value
    except Exception:
        return value


def get_flat_filename(**kwargs):
    """Returns the whole filename for the flat field correction from the headers."""
    flat_folder = get_from_headers(key=KEY_FLAT_FOLDER, **kwargs)
    flat_file = get_from_headers(key=KEY_FLAT_FILE, **kwargs)
    if flat_folder is None or flat_file is None:
        return

    flat_filename = os.path.join(flat_folder, flat_file)
    if not os.path.exists(flat_filename):
        return
    return flat_filename


def get_mask_detector_filename(**kwargs):
    """Returns the whole filename for the detector gaps mask from the headers."""
    mask_folder = get_from_headers(key=KEY_DETECTOR_MASK_FOLDER, **kwargs)
    mask_file = get_from_headers(key=KEY_DETECTOR_MASK_FILE, **kwargs)
    if mask_folder is None or mask_file is None:
        return

    mask_filename = os.path.join(mask_folder, mask_file)
    if not os.path.exists(mask_filename):
        return
    return mask_filename


def get_mask_beamstop_filename(**kwargs):
    """Returns the whole filename for the beamstop mask from the headers."""
    mask_folder = get_from_headers(key=KEY_BEAMSTOP_MASK_FOLDER, **kwargs)
    mask_file = get_from_headers(key=KEY_BEAMSTOP_MASK_FILE, **kwargs)
    if mask_folder is None or mask_file is None:
        return

    mask_filename = os.path.join(mask_folder, mask_file)
    if not os.path.exists(mask_filename):
        return
    return mask_filename


def get_dark_filename(**kwargs):
    """Returns the whole filename for the dark current correction from the headers."""
    dark_folder = get_from_headers(key=KEY_DARK_FOLDER, **kwargs)
    dark_file = get_from_headers(key=KEY_DARK_FILE, **kwargs)
    if dark_folder is None or dark_file is None:
        return

    dark_filename = os.path.join(dark_folder, dark_file)
    if not os.path.exists(dark_filename):
        return
    return dark_filename


def load_data(
    filename: Union[str, List[str]],
    binning: tuple = (1, 1),
    data_signal_shape: tuple = None,
) -> Optional[numpy.ndarray]:
    """
    Load data from a file or a list of files.

    Inputs:
        - filename (Union[str, List[str]]): The filename or list of filenames.
        - binning (tuple): binning of the data signal
        - data_signal_shape (tuple): shape of the data array (2-dimensional)
    Outputs:
        - Optional[numpy.ndarray]: The loaded data or None if the file does not exist.
    """
    if filename is None:
        return

    data = None
    if isinstance(filename, (tuple, list)):
        data = None
        for ind, file in enumerate(filename):
            data_ = _load_data(file)
            data_ = data_.astype("int32", copy=False)
            if data is None:
                data = data_
            else:
                data += data_
    elif isinstance(filename, str):
        data = _load_data(filename)

    if binning == (1, 1) and data_signal_shape is None:
        return data

    if data is not None and data.shape != data_signal_shape:
        from pyFAI.utils.mathutil import binning as binning_tool

        binning_additional_data = _get_data_binning(filename=filename)
        binning_relative = (
            int(binning[0] / binning_additional_data[0]),
            int(binning[1] / binning_additional_data[1]),
        )
        data_binned = binning_tool(data, binning_relative, norm=False)
        if data_binned.shape != data_signal_shape:
            raise ValueError(
                f"Data shape after binning {binning} from {filename} does not match the expected shape: {data_binned.shape} != {data_signal_shape}"
            )
        data = data_binned

    return data


def _load_data(filename: str) -> Optional[numpy.ndarray]:
    """
    Load data from a single file.

    Inputs:
        - filename (str): The filename.
    Outputs:
        - Optional[numpy.ndarray]: The loaded data or None if the file does not exist.
    """
    if not os.path.exists(filename):
        return

    if filename.endswith(".h5"):
        filename += "::/entry_0000/measurement/data"
    try:
        with fabio.open(filename) as f:
            return f.data
    except Exception as e:
        logger.error(f"File {filename} could not be open with fabio: {e}")


def _get_data_binning(filename: str):
    """
    Load data from a single file.

    Inputs:
        - filename (str): The filename.
    Outputs:
        - Optional[numpy.ndarray]: The loaded data or None if the file does not exist.
    """
    if not os.path.exists(filename):
        return

    if filename.endswith(".h5"):
        filename += "::/entry_0000/measurement/data"
    try:
        with fabio.open(filename) as f:
            b1 = f.header.get("Bsize_1")
            b1_ = f.header.get("BSize_1")
            b2 = f.header.get("Bsize_2")
            b2_ = f.header.get("BSize_2")
            b1 = b1 or b1_
            b2 = b2 or b2_
            return (int(b1), int(b2))
    except Exception as e:
        logger.error(f"File {filename} could not be open with fabio: {e}")


def get_headers(
    headers: Optional[Dict[str, Union[str, float]]] = None,
    metadata_file_group: Optional[h5py.Group] = None,
) -> Optional[Dict[str, Union[str, float]]]:
    """
    Retrieve headers from a dictionary or an HDF5 group.

    Inputs:
        - headers (Optional[Dict[str, Union[str, float]]], optional): The header dictionary. Defaults to None.
        - metadata_file_group (Optional[h5py.Group], optional): The HDF5 group. Defaults to None.
    Outputs:
        - Optional[Dict[str, Union[str, float]]]: The headers or None if not found.
    """
    if headers:
        return headers
    elif metadata_file_group:
        headers = {}
        for key in metadata_file_group:
            value = metadata_file_group[key][()]
            if isinstance(value, bytes):
                value = value.decode("UTF-8")
            headers[key] = value
        return headers
    else:
        return {}


def get_free_memory(device_id):
    """Retrieves the available memory on a GPU device"""
    if not CUPY_AVAILABLE:
        logger.warning("Cupy is not available.")
        return None

    with cupy.cuda.Device(device_id):
        free_mem, total_mem = cupy.cuda.runtime.memGetInfo()
        return free_mem


def get_best_gpu():
    """Decides the best GPU in terms of memory available"""
    if not CUPY_AVAILABLE:
        logger.warning("Cupy is not available.")
        return None

    best_device = None
    max_free_memory = 0

    for device_id in range(cupy.cuda.runtime.getDeviceCount()):
        free_memory = get_free_memory(device_id)
        if free_memory is not None and free_memory > max_free_memory:
            max_free_memory = free_memory
            best_device = device_id

    return best_device


def use_best_gpu():
    """
    Set the best available GPU for cupy operations.
    """
    best_device = get_best_gpu()
    if best_device is not None:
        cupy.cuda.Device(best_device).use()
        logger.info(f"Using GPU {best_device} with the most free memory.")
    else:
        logger.warning("No suitable GPU found or cupy is not available.")
