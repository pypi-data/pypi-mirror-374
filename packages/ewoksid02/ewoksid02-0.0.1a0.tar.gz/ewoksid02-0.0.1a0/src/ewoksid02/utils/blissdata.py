import logging
import os
import re
import time
from importlib.metadata import version
from typing import Any, Dict, Optional, Tuple

import h5py
import numpy
import numpy as np
from blissdata.beacon.data import BeaconData
from blissdata.h5api import dynamic_hdf5
from blissdata.redis_engine.exceptions import (
    IndexNoMoreThereError,
    IndexNotYetThereError,
    IndexWontBeThereError,
)
from blissdata.redis_engine.scan import Scan
from blissdata.redis_engine.store import DataStore
from packaging.version import Version

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

HEADERS_KEY_MONITOR = "HSI1"
HEADERS_KEY_EXPOSURE_TIME = "HSTime"

LIMA_URL_TEMPLATE_ID02 = (
    "{dirname}/{images_prefix}{{file_index}}.h5::/entry_0000/measurement/data"
)
IMAGE_PREFIX_TEMPLATE_ID02 = "{collection_name}_{img_acq_device}_{scan_number}_"


def get_datastore(beacon_host: str = None) -> DataStore:
    """Returns the datastore object from blissdata

    Inputs:
        - beacon_host (str) : hostname and beacon port
    """
    try:
        os.environ["BEACON_HOST"] = beacon_host
        datastore = DataStore(url=BeaconData().get_redis_data_db())
        return datastore
    except Exception:
        return


def load_scan(
    scan_memory_url: str, wait_until_start: bool = True, beacon_host: str = None
) -> Scan:
    """
    Loads a scan from the data store using the provided scan memory URL.

    Inputs:
        - scan_memory_url (str): The URL of the scan memory to load.
        - wait_until_start (bool, optional): Whether to wait until the scan starts. Defaults to True.
        - beacon_host (str) : hostname and beacon port
    Outputs:
        - Scan: The loaded scan object.
    """
    datastore = get_datastore(beacon_host=beacon_host)
    if not datastore:
        return
    if Version(version("blissdata")) >= Version("2.0.0"):
        scan = datastore.load_scan(key=scan_memory_url)
    else:
        scan = datastore.load_scan(key=scan_memory_url, scan_cls=Scan)
    if wait_until_start:
        while scan.state < 2:
            scan.update(block=False)
    return scan


def get_limastream(
    detector_name: str,
    scan: Scan = None,
    scan_memory_url: str = None,
    beacon_host: str = None,
):
    """
    Retrieves the Lima stream for a specific detector from the scan memory.

    Inputs:
        - detector_name (str): The name of the detector.
        - scan (Scan): blissdata.redis_engine.scan.Scan object
        - scan_memory_url (str): The URL of the scan memory.
        - beacon_host (str) : hostname and beacon port
    Outputs:
        - LimaStream: The Lima stream object for the specified detector.
    """
    if not scan:
        scan = load_scan(
            scan_memory_url=scan_memory_url,
            wait_until_start=True,
            beacon_host=beacon_host,
        )
    if Version(version("blissdata")) >= Version("2.0.0"):
        lima_stream = scan.streams[f"{detector_name}:image"]
    else:
        from blissdata.stream import LimaStream

        lima_stream = LimaStream(stream=scan.streams[f"{detector_name}:image"])
    return lima_stream


def get_lima_url_template_args_id02(
    scan_number: int,
    detector_name: str,
    collection_name: str = None,
    scan_number_format: str = "%05d",
    image_prefix_template: str = IMAGE_PREFIX_TEMPLATE_ID02,
) -> Optional[Dict[str, str]]:

    lima_url_template_args = {
        "images_prefix": image_prefix_template.format(
            collection_name=collection_name,
            img_acq_device=detector_name,
            scan_number=scan_number_format % scan_number,
        )
    }
    return lima_url_template_args


def get_length_dataset_dynamic_file(
    filename_data: str,
    scan_nb: int,
    detector_name: str,
    lima_url_template="",
    lima_url_template_args={},
    subscan=1,
):
    params_dynamic_file = {
        "file": filename_data,
        "lima_names": [detector_name],
        "lima_url_template": lima_url_template,
        "lima_url_template_args": lima_url_template_args,
    }

    with dynamic_hdf5.File(**params_dynamic_file) as root:
        lima_dataset = root[f"{scan_nb}.{subscan}/instrument/{detector_name}/data"]
        length_dataset = len(lima_dataset)
    return length_dataset


def get_length_dataset_static_file(
    filename_data: str,
    data_path: str,
):
    with h5py.File(filename_data, "r") as f:
        if data_path in f:
            return len(f[data_path])
        else:
            logger.error(f"{data_path} not found in {filename_data}")
            return


def track_length_dataset_dynamic_file(
    lima_name,
    scan_memory_url,
    beacon_host=None,
    lima_url_template="",
    lima_url_template_args={},
    subscan=1,
    **kwargs,
):
    scan = load_scan(scan_memory_url=scan_memory_url, beacon_host=beacon_host)
    while scan.state < 2:
        scan.update(block=False)

    master_filename = scan.info["filename"]
    scan_nb = scan.info["scan_nb"]
    nb_points = scan.info["npoints"]

    params_dynamic_file = {
        "file": master_filename,
        "lima_names": [lima_name],
        "lima_url_template": lima_url_template,
        "lima_url_template_args": lima_url_template_args,
        **kwargs,
    }

    wait = True
    while wait:
        with dynamic_hdf5.File(**params_dynamic_file) as root:
            lima_dataset = root[f"{scan_nb}.{subscan}/instrument/{lima_name}/data"]

            length = len(lima_dataset)
            if length == nb_points:
                wait = False
            elif scan.state == 4:
                length = len(lima_dataset)
                wait = False
            else:
                scan.update(block=False)
                time.sleep(1)
            yield length

    final_length = get_length_dataset_dynamic_file(
        detector_name=lima_name,
        scan_memory_url=scan_memory_url,
        lima_url_template=lima_url_template,
        lima_url_template_args=lima_url_template_args,
        subscan=subscan,
        **kwargs,
    )
    if final_length != length:
        return final_length


def get_length_lima_stream(
    detector_name,
    scan: Scan = None,
    scan_memory_url: str = None,
    beacon_host: str = None,
    lima_url_template="",
    lima_url_template_args={},
    subscan=1,
):
    limastream = get_limastream(
        scan=scan,
        scan_memory_url=scan_memory_url,
        detector_name=detector_name,
        beacon_host=beacon_host,
    )

    # To overcome Lima bug with memory when mask processing is active
    try:
        # _ = limastream[0]
        # Check the len of a limastream does not crash regarding the Lima Bug
        last_index_available = len(limastream)
    except Exception:
        logger.warning("Data is no more available from Lima memory")
        if not scan:
            scan = load_scan(scan_memory_url=scan_memory_url, beacon_host=beacon_host)
        last_index_available = get_length_dataset_dynamic_file(
            filename_data=scan.info["filename"],
            scan_nb=scan.info["scan_nb"],
            detector_name=detector_name,
            lima_url_template=lima_url_template,
            lima_url_template_args=lima_url_template_args,
            subscan=subscan,
        )
    return last_index_available


def track_length_dataset(
    lima_name,
    scan_memory_url,
    beacon_host=None,
    lima_url_template="",
    lima_url_template_args={},
    subscan=1,
    **kwargs,
):
    scan = load_scan(scan_memory_url=scan_memory_url, beacon_host=beacon_host)
    nb_points = scan.info["npoints"]

    limastream_params = {
        "scan_memory_url": scan_memory_url,
        "detector_name": lima_name,
    }

    wait = True
    memory_available = True
    last_index_available = 0

    while wait:
        if memory_available:
            limastream = get_limastream(**limastream_params)
            try:
                _ = limastream[0]
                last_index_available = len(limastream)
                logger.info("Data is available from Lima memory")
            except IndexNotYetThereError:
                pass
            except IndexNoMoreThereError:
                logger.warning("Data is no more available from Lima memory")
                memory_available = False
            except RuntimeError:
                pass

            if last_index_available == nb_points:
                wait = False
            elif scan.state == 4:
                last_index_available = len(limastream)
                wait = False
            else:
                scan.update(block=False)
                time.sleep(1)
        else:
            logger.info("Data is only available in the files")
            params_dynamic_file = {
                "file": scan.info["filename"],
                "lima_names": [lima_name],
                "lima_url_template": lima_url_template,
                "lima_url_template_args": lima_url_template_args,
                **kwargs,
            }

            with dynamic_hdf5.File(**params_dynamic_file) as root:
                scan_nb = scan.info["scan_nb"]
                lima_dataset = root[f"{scan_nb}.{subscan}/instrument/{lima_name}/data"]

                last_index_available = len(lima_dataset)
                if last_index_available == nb_points:
                    wait = False
                elif scan.state == 4:
                    last_index_available = len(lima_dataset)
                    wait = False
                else:
                    scan.update(block=False)
                    time.sleep(1)

        yield last_index_available


def track_dataset(
    lima_name,
    scan_memory_url,
    beacon_host=None,
    lima_url_template="",
    lima_url_template_args={},
    subscan=1,
    max_slice_size=10,
    start_from_memory=True,
    **kwargs,
):
    scan = load_scan(scan_memory_url=scan_memory_url, beacon_host=beacon_host)
    nb_points = scan.info["npoints"]

    limastream_params = {
        "scan_memory_url": scan_memory_url,
        "detector_name": lima_name,
    }

    wait = True
    memory_available = start_from_memory
    last_index_read = 0
    while wait:
        dataset = None

        if memory_available:
            try:
                scan.update(block=False)
                limastream = get_limastream(**limastream_params)
            except Exception:
                wait = False
                continue

            try:
                _ = limastream[0]
                last_index_available = len(limastream)
                slice_end = min(last_index_read + max_slice_size, last_index_available)
                dataset = limastream[last_index_read:slice_end]
                if dataset and len(dataset) == 0:
                    continue

                logger.info(
                    f"Data retrieved from Lima memory: {slice_end - last_index_read} frames"
                )
                last_index_read = slice_end
            except IndexNotYetThereError:
                continue
            except IndexNoMoreThereError:
                logger.warning(
                    "Data is no more available from Lima memory. Switching to h5api..."
                )
                memory_available = False
                continue
            except RuntimeError:
                continue

            if last_index_read == nb_points:
                wait = False
            elif scan.state == 4:
                limastream = get_limastream(**limastream_params)
                try:
                    length = len(limastream)
                    if length == last_index_read:
                        wait = False
                except Exception:
                    memory_available = False
                    continue

        if not memory_available:
            params_dynamic_file = {
                "file": scan.info["filename"],
                "lima_names": [lima_name],
                "lima_url_template": lima_url_template,
                "lima_url_template_args": lima_url_template_args,
                **kwargs,
            }

            with dynamic_hdf5.File(**params_dynamic_file) as root:
                scan_nb = scan.info["scan_nb"]
                lima_dataset = root[f"{scan_nb}.{subscan}/instrument/{lima_name}/data"]

                length = len(lima_dataset)
                if length > last_index_read:
                    slice_end = min(last_index_read + max_slice_size, length)
                    dataset = lima_dataset[last_index_read:slice_end]
                    logger.info(f"Data retrieved from hdf5 file: {len(dataset)} frames")
                    last_index_read = slice_end

                if last_index_read == nb_points:
                    wait = False
                elif scan.state == 4 and last_index_read == len(lima_dataset):
                    wait = False
                else:
                    scan.update(block=False)

        yield dataset


def get_available_dataset(
    lima_name: str,
    scan_memory_url: str = "",
    lima_url_template: str = "",
    lima_url_template_args: Dict[str, Any] = {},
    scan_nb: int = None,
    subscan: int = 1,
    last_index_read: int = 0,
    max_slice_size: int = 10,
    start_from_memory: bool = True,
    range_index_read: Optional[Tuple[int, int]] = None,
    data_filename: str = None,
) -> Optional[np.ndarray]:
    """
    Retrieves the available dataset from either Lima memory or an HDF5 file.

    Args:
        lima_name (str): Name of the detector.
        scan_memory_url (str): URL to the scan memory.
        lima_url_template (str, optional): Template for Lima file URLs. Defaults to "".
        lima_url_template_args (dict, optional): Arguments for the Lima URL template. Defaults to {}.
        subscan (int, optional): Subscan number. Defaults to 1.
        last_index_read (int, optional): Last index read from the dataset. Defaults to 0.
        max_slice_size (int, optional): Maximum number of frames to read in one slice. Defaults to 10.
        start_from_memory (bool, optional): Whether to start reading from memory. Defaults to True.
    Returns:
        Optional[np.ndarray]: The retrieved dataset, or None if no data is available.
    """
    if scan_memory_url:
        return read_dataset_online(
            scan_memory_url=scan_memory_url,
            detector_name=lima_name,
            lima_url_template=lima_url_template,
            lima_url_template_args=lima_url_template_args,
            subscan=subscan,
            last_index_read=last_index_read,
            max_slice_size=max_slice_size,
            start_from_memory=start_from_memory,
            range_index_read=range_index_read,
        )
    else:
        return read_datasets_offline(
            data_filename=data_filename,
            scan_nb=scan_nb,
            subscan=subscan,
            detector_name=lima_name,
            last_index_read=last_index_read,
            max_slice_size=max_slice_size,
            range_index_read=range_index_read,
        )


def read_dataset_online(
    detector_name: str,
    scan: Scan = None,
    scan_memory_url: str = None,
    beacon_host: str = None,
    lima_url_template: str = "",
    lima_url_template_args: Dict[str, Any] = {},
    subscan: int = 1,
    last_index_read: int = 0,
    max_slice_size: int = 10,
    start_from_memory: bool = True,
    range_index_read: Optional[Tuple[int, int]] = None,
):
    """
    Reads a dataset from an online source, either from Lima memory or through dynamic hdf5 file.

    This method attempts to retrieve data from Lima memory first. If the data is no longer
    available in memory, it falls back to reading from an HDF5 file.

    Args:
        scan_memory_url (str): URL to the scan memory.
        lima_name (str): Name of the detector.
        lima_url_template (str, optional): Template for Lima file URLs. Defaults to "".
        lima_url_template_args (Dict[str, Any], optional): Arguments for the Lima URL template. Defaults to an empty dictionary.
        subscan (int, optional): Subscan number. Defaults to 1.
        last_index_read (int, optional): The last index read from the dataset. Defaults to 0.
        max_slice_size (int, optional): Maximum number of frames to read in one slice. Defaults to 10.
        start_from_memory (bool, optional): Whether to start reading from Lima memory. Defaults to True.
        range_index_read (tuple[int, int] | None, optional): Range of indices to read. If None, reads all available data. Defaults to None.

    Returns:
        None: The method does not return a value directly. Instead, it processes the dataset
        and logs the retrieved data.
    """
    if not scan:
        scan = load_scan(scan_memory_url=scan_memory_url, beacon_host=beacon_host)

    limastream_params = {
        "scan": scan,
        "scan_memory_url": scan_memory_url,
        "detector_name": detector_name,
        "beacon_host": beacon_host,
    }

    memory_available = start_from_memory
    dataset = None
    wait_for_data = True
    logger.info("Waiting for data...")
    while wait_for_data:
        if memory_available:
            try:
                scan.update(block=False)
                limastream = get_limastream(**limastream_params)
            except Exception as e:
                # Handle canceled or non-existent scans
                logger.warning(f"Scan canceled or does not exist. Exiting. {e}")
                wait_for_data = False
                continue

            try:
                # Check if the requested frame is available in memory
                _ = limastream[last_index_read]
                last_index_available = len(limastream)
                logger.info(f"{last_index_available=}, {last_index_read=}")

                if last_index_available > last_index_read:
                    # Determine the slice range
                    if range_index_read is not None:
                        slice_end = min(range_index_read[-1], last_index_available)
                    else:
                        slice_end = min(
                            last_index_read + max_slice_size, last_index_available
                        )
                    dataset = limastream[last_index_read:slice_end]
                    if dataset is not None:
                        if len(dataset) == 0:
                            dataset = None
                            continue
                        if len(dataset) > 0:
                            wait_for_data = False
                            logger.info(
                                f"Data retrieved from Lima memory: {len(dataset)} frames"
                            )
                            last_index_read = slice_end
                    else:
                        continue
                elif last_index_available == len(limastream):
                    # time.sleep(1)
                    # wait_for_data = False
                    # No new data, if the scan is not over, wait (to be tested)
                    if scan.state == 4:
                        wait_for_data = False
                    continue
                else:
                    continue
            except IndexNotYetThereError:
                # Frame not yet available
                continue
            except IndexNoMoreThereError:
                logger.warning(
                    "Data is no more available from Lima memory. Switching to h5api..."
                )
                memory_available = False
                continue
            except IndexWontBeThereError:
                logger.warning("No more data can be retrieved")
                wait_for_data = False
                continue
            except Exception as e:
                print(
                    f"Exception! Looks like Lima memory is not reachable. Switching to file... {e}"
                )
                memory_available = False
                continue

        if not memory_available:
            params_dynamic_file = {
                "file": scan.info["filename"],
                "lima_names": [detector_name],
                "lima_url_template": lima_url_template,
                "lima_url_template_args": lima_url_template_args,
                # "prioritize_non_native_h5items" : True,
            }

            with dynamic_hdf5.File(**params_dynamic_file) as root:
                scan_nb = scan.info["scan_nb"]
                dset_data = root[f"{scan_nb}.{subscan}/instrument/{detector_name}/data"]

                last_index_available = len(dset_data)
                if last_index_available > last_index_read:
                    slice_end = min(
                        last_index_read + max_slice_size, last_index_available
                    )
                    dataset = dset_data[last_index_read:slice_end, :, :]
                    if dataset is not None:
                        if len(dataset) == 0:
                            dataset = None
                            continue
                        if len(dataset) > 0:
                            wait_for_data = False
                            logger.info(
                                f"Data retrieved from hdf5 file: {len(dataset)} frames"
                            )
                            last_index_read = slice_end

    return dataset


def read_datasets_offline(
    data_filename: str,
    path_to_data_signal: str,
    path_to_data_variance: str,
    path_to_data_sigma: str,
    last_index_read: int,
    max_slice_size: int = 100,
    range_index_read: Optional[Tuple[int, int]] = None,
) -> tuple:
    """
    Reads a dataset from an HDF5 file, handling different possible structures.

    Args:
        data_filename (str): Path to the HDF5 file.
        lima_name (str): Name of the detector.
        last_index_read (int): Starting index for slicing the dataset.
        scan_nb (int): Scan number.
        max_slice_size (int): Maximum number of frames to read in one slice.
        range_index_read (tuple[int, int] | None): Range of indices to read. If None, reads all available data.

    Returns:
        numpy.ndarray: The sliced dataset, or None if no data is found.
    """
    dataset_signal = None
    dataset_variance = None
    dataset_sigma = None

    data_signal = None
    data_variance = None
    data_sigma = None

    with h5py.File(data_filename, "r") as f:
        if path_to_data_signal and path_to_data_signal in f:
            dataset_signal = f[path_to_data_signal]
        if path_to_data_variance and path_to_data_variance in f:
            dataset_variance = f[path_to_data_variance]
        if path_to_data_sigma and path_to_data_sigma in f:
            dataset_sigma = f[path_to_data_sigma]

        if dataset_signal is not None:
            length = len(dataset_signal)
            slice_init = last_index_read
            if range_index_read is None:
                slice_init = last_index_read
                slice_end = min(
                    last_index_read + max_slice_size,
                    length,
                )
            else:
                slice_end = min(
                    slice_init + max_slice_size, length, range_index_read[-1]
                )
            data_signal = dataset_signal[slice_init:slice_end]
            if dataset_variance is not None:
                data_variance = dataset_variance[slice_init:slice_end]
            if dataset_sigma is not None:
                data_sigma = dataset_sigma[slice_init:slice_end]

    return (data_signal, data_variance, data_sigma)


def read_dataset_offline(
    filename_data: str,
    detector_name: str,
    scan_nb: int,
    last_index_read: int,
    max_slice_size: int = 100,
    range_index_read: Optional[Tuple[int, int]] = None,
) -> tuple:
    dataset = None
    with h5py.File(filename_data, "r") as f:
        path_to_data_signal = f"{scan_nb}.1/instrument/{detector_name}/data"
        if path_to_data_signal not in f:
            logger.error(f"Dataset {path_to_data_signal} not found in {filename_data}")
            return

        dataset = f[path_to_data_signal]
        length = len(dataset)
        slice_init = last_index_read
        if range_index_read is None:
            slice_end = min(
                last_index_read + max_slice_size,
                length,
            )
        else:
            slice_end = min(range_index_read[-1], length)
        data_signal = dataset[slice_init:slice_end]
    return data_signal


def copy_group_excluding_dataset(src_group, dest_group, exclude_dataset):
    for attr_name, attr_value in src_group.attrs.items():
        dest_group.attrs[attr_name] = attr_value

    for name, item in src_group.items():
        if isinstance(item, h5py.Group):
            # Recursively copy subgroups
            new_subgroup = dest_group.create_group(name)
            copy_group_excluding_dataset(item, new_subgroup, exclude_dataset)
        elif isinstance(item, h5py.Dataset):
            if name != exclude_dataset:  # Skip the excluded dataset
                src_group.copy(name, dest_group, name=name)


def continue_pipeline(
    detector_name: str = None,
    scan_memory_url=None,
    beacon_host: str = None,
    last_index_read=0,
    lima_url_template="",
    lima_url_template_args={},
    subscan=1,
    filename_data=None,
    path_to_data_signal: str = None,  # To be used for static files
) -> bool:
    """
    Checks if there are still frames to be read from a running/complete scan or from a file
    """
    logger.info(
        f"Checking if there are still frames to read. Last index read: {last_index_read}"
    )
    if scan_memory_url:
        return continue_pipeline_bliss(
            scan_memory_url=scan_memory_url,
            beacon_host=beacon_host,
            detector_name=detector_name,
            last_index_read=last_index_read,
            subscan=subscan,
            lima_url_template=lima_url_template,
            lima_url_template_args=lima_url_template_args,
        )
    elif filename_data:
        return continue_pipeline_offline(
            filename_data=filename_data,
            last_index_read=last_index_read,
            path_to_data_signal=path_to_data_signal,
        )


def continue_pipeline_bliss(
    detector_name: str,
    scan: Scan = None,
    scan_memory_url: str = None,
    beacon_host: str = None,
    last_index_read: int = 0,
    subscan: int = 1,
    lima_url_template: str = None,
    lima_url_template_args: dict = None,
):
    try:
        if not scan:
            scan = load_scan(
                scan_memory_url=scan_memory_url,
                beacon_host=beacon_host,
                wait_until_start=False,
            )
        state = scan.state
    except Exception as e:
        logger.error(f"scan {scan_memory_url} could not be loaded!: {e}")
        return False

    if state < 2:
        logger.info("Scan started but acquisition did not. Wait, data is coming")
        return True
    elif state in (2, 3):
        logger.info("Scan is running. Wait for data")
        return True
    if state == 4:
        logger.info("Scan is complete")
        if not scan.streams:
            logger.warning(
                "\n\tThe scan is complete and does not contain any streams. End of the workflow.\n\t"
            )
            return False

        if f"{detector_name}:image" not in scan.streams:
            logger.error(f"There is no stream {detector_name}:image in the scan")
            return False

        current_length = get_length_lima_stream(
            scan=scan,
            scan_memory_url=scan_memory_url,
            beacon_host=beacon_host,
            detector_name=detector_name,
            lima_url_template=lima_url_template,
            lima_url_template_args=lima_url_template_args,
            subscan=subscan,
        )
        if current_length is None:
            return False

        logger.info(f"Current length of the dataset: {current_length}")
        if current_length == last_index_read:
            logger.info("\n\tNo more frames to read. End of the workflow\n\t")
            return False
        elif current_length > last_index_read:
            logger.info("There are still frames to read. Continue")
            return True
        else:
            logger.error(
                "There are more read then stored frames. Something went wrong!"
            )
            return False


def continue_pipeline_offline(
    filename_data: str,
    last_index_read: int = 0,
    path_to_data_signal: str = None,
):
    current_length = get_length_dataset_static_file(
        filename_data=filename_data,
        data_path=path_to_data_signal,
    )
    if current_length is None:
        return False

    logger.info(
        f"Current length of the dataset: {current_length}. Last index read: {last_index_read}"
    )
    if current_length == last_index_read:
        logger.info("\n\tNo more frames to read. End of the workflow\n\t")
        return False
    elif current_length > last_index_read:
        logger.info("There are still frames to read. Continue")
        return True
    else:
        logger.error("There are more read then stored frames. Something went wrong!")
        return True


def get_intensity0_values(
    range_index_read: tuple = None,
    scan: Scan = None,
    scan_memory_url: str = None,
    beacon_host: str = None,
    headers: dict = None,
    metadata_file: str = None,
    h5_path_to_mcs: str = None,
    metadata_mcs_group: h5py.Group = None,
    header_key_to_intensity0="HSI0",
    header_key_to_factor0="HSI0Factor",
):
    if range_index_read is None:
        range_index_read = [None, None]

    if scan_memory_url and headers:
        I0_factor = float(headers.get(header_key_to_factor0))

        if I0_factor is None:
            return None, None

        pin0 = str(headers.get(header_key_to_intensity0))
        stream_0 = match_stream(
            pin_name=pin0,
            scan=scan,
            beacon_host=beacon_host,
            scan_memory_url=scan_memory_url,
            stream_group="scalers",
        )
        if stream_0 is None:
            return None, None

        counter_0 = read_blissdata_stream(
            stream=stream_0, range_to_read=range_index_read
        )
        if counter_0 is None:
            logger.error(f"Counter {pin0} could not be read")
            return None, None

        exposure_time = get_exposuretime_values(
            scan=scan,
            range_index_read=range_index_read,
            headers=headers,
            scan_memory_url=scan_memory_url,
        )

        if exposure_time is None:
            logger.error("Measured time could not be read")
            return None, None

        sot = headers.get("ShutterOpeningTime") or 0.0
        sct = headers.get("ShutterClosingTime") or 0.0
        correction = (exposure_time - sot + sct) / (exposure_time - sot)

        intensity_0_uncor = counter_0 * I0_factor
        intensity_0_shutcor = intensity_0_uncor * correction

        return intensity_0_uncor, intensity_0_shutcor

    elif metadata_mcs_group:
        if "Intensity0UnCor" not in metadata_mcs_group:
            logger.error(f"No Intensity0UnCor found in : {metadata_mcs_group}")
            intensity_0_uncor = None
        else:
            intensity_0_uncor = metadata_mcs_group["Intensity0UnCor"][
                range_index_read[0] : range_index_read[1]
            ]

        if "Intensity0ShutCor" not in metadata_mcs_group:
            logger.error(f"No Intensity0ShutCor found in : {metadata_mcs_group}")
            intensity_0_shutcor = None
        else:
            intensity_0_shutcor = metadata_mcs_group["Intensity0ShutCor"][
                range_index_read[0] : range_index_read[1]
            ]

        return intensity_0_uncor, intensity_0_shutcor

    elif metadata_file and h5_path_to_mcs:
        with h5py.File(metadata_file, "r") as f:
            if h5_path_to_mcs not in f:
                logger.error(f"No MCS group found in : {metadata_file}")
                return None, None

            mcs_grp = f[h5_path_to_mcs]

            if "Intensity0UnCor" not in mcs_grp:
                logger.error(f"No Intensity0UnCor found in :{h5_path_to_mcs}")
                intensity_0_uncor = None
            else:
                intensity_0_uncor = mcs_grp["Intensity0UnCor"][
                    range_index_read[0] : range_index_read[1]
                ]

            if "Intensity0ShutCor" not in mcs_grp:
                logger.error(f"No Intensity0ShutCor found in :{h5_path_to_mcs}")
                intensity_0_shutcor = None
            else:
                intensity_0_shutcor = mcs_grp["Intensity0ShutCor"][
                    range_index_read[0] : range_index_read[1]
                ]

            return intensity_0_uncor, intensity_0_shutcor
    else:
        return None, None


def get_intensity1_values(
    range_index_read: tuple = None,
    scan: Scan = None,
    scan_memory_url: str = None,
    beacon_host: str = None,
    headers: dict = None,
    metadata_file: str = None,
    h5_path_to_mcs: str = None,
    metadata_mcs_group: h5py.Group = None,
    header_key_to_intensity1="HSI1",
    header_key_to_factor1="HSI1Factor",
):
    if range_index_read is None:
        range_index_read = [None, None]

    if scan_memory_url and headers:
        I1_factor = float(headers.get(header_key_to_factor1))

        if I1_factor is None:
            return None, None

        pin1 = str(headers.get(header_key_to_intensity1))
        stream_1 = match_stream(
            scan=scan,
            beacon_host=beacon_host,
            pin_name=pin1,
            scan_memory_url=scan_memory_url,
            stream_group="scalers",
        )
        if stream_1 is None:
            return None, None

        counter_1 = read_blissdata_stream(
            stream=stream_1, range_to_read=range_index_read
        )
        if counter_1 is None:
            logger.error(f"Counter {pin1} could not be read")
            return None, None

        exposure_time = get_exposuretime_values(
            scan=scan,
            range_index_read=range_index_read,
            headers=headers,
            scan_memory_url=scan_memory_url,
        )

        if exposure_time is None:
            logger.error("Measured time could not be read")
            return None, None

        sot = headers.get("ShutterOpeningTime") or 0.0
        sct = headers.get("ShutterClosingTime") or 0.0
        correction = (exposure_time - sot + sct) / (exposure_time - sot)

        intensity_1_uncor = counter_1 * I1_factor
        intensity_1_shutcor = intensity_1_uncor * correction

        return intensity_1_uncor, intensity_1_shutcor

    elif metadata_mcs_group:
        if "Intensity1UnCor" not in metadata_mcs_group:
            logger.error(f"No Intensity1UnCor found in : {metadata_mcs_group}")
            intensity_1_uncor = None
        else:
            intensity_1_uncor = metadata_mcs_group["Intensity1UnCor"][
                range_index_read[0] : range_index_read[1]
            ]
        if "Intensity1ShutCor" not in metadata_mcs_group:
            logger.error(f"No Intensity1ShutCor found in : {metadata_mcs_group}")
            intensity_1_shutcor = None
        else:
            intensity_1_shutcor = metadata_mcs_group["Intensity1ShutCor"][
                range_index_read[0] : range_index_read[1]
            ]

        return intensity_1_uncor, intensity_1_shutcor

    elif metadata_file and h5_path_to_mcs:
        with h5py.File(metadata_file, "r") as f:
            if h5_path_to_mcs not in f:
                logger.error(f"No MCS group found in : {metadata_file}")
                return None, None

            mcs_grp = f[h5_path_to_mcs]

            if "Intensity1UnCor" not in mcs_grp:
                logger.error(f"No Intensity1UnCor found in :{h5_path_to_mcs}")
                intensity_1_uncor = None
            else:
                intensity_1_uncor = mcs_grp["Intensity1UnCor"][
                    range_index_read[0] : range_index_read[1]
                ]

            if "Intensity1ShutCor" not in mcs_grp:
                logger.error(f"No Intensity1ShutCor found in :{h5_path_to_mcs}")
                intensity_1_shutcor = None
            else:
                intensity_1_shutcor = mcs_grp["Intensity1ShutCor"][
                    range_index_read[0] : range_index_read[1]
                ]
            return intensity_1_uncor, intensity_1_shutcor
    else:
        return None, None


def get_deltatime_values(
    range_index_read: tuple = None,
    scan: Scan = None,
    scan_memory_url: str = None,
    beacon_host: str = None,
    pin_name="elapsed_time",
    metadata_file: str = None,
    h5_path_to_tfg: str = None,
    metadata_tfg_group: h5py.Group = None,
):
    """
    Generic method to retrieve the exposure time for every frame:
    The exposure time reading comes in microseconds, so a factor product is needed to get the seconds
    - Online: read from the blissdata streams, associated to pin monitor in HSTime
    - Offline: read directly from one column of HS32C
    """
    if range_index_read is None:
        range_index_read = [None, None]

    if scan_memory_url:
        if pin_name is None:
            return

        stream_deltatime = match_stream(
            scan=scan,
            beacon_host=beacon_host,
            pin_name=pin_name,
            scan_memory_url=scan_memory_url,
            stream_group="mcs",
        )

        if stream_deltatime is None:
            return

        stream_values = read_blissdata_stream(
            stream=stream_deltatime, range_to_read=range_index_read
        )

        return stream_values

    elif metadata_tfg_group:
        if "delta_time" not in metadata_tfg_group:
            logger.error(f"No delta_time found in : {metadata_tfg_group}")
            return

        counter_values = metadata_tfg_group["delta_time"][
            range_index_read[0] : range_index_read[1]
        ]
        return counter_values

    elif metadata_file and h5_path_to_tfg:
        with h5py.File(metadata_file, "r") as file:
            if h5_path_to_tfg not in file:
                logger.error(f"No TFG found in : {h5_path_to_tfg}")
                return

            tfg_grp = file[h5_path_to_tfg]

            if "delta_time" not in tfg_grp:
                logger.error(f"No delta_time found in :{h5_path_to_tfg}")
                return

            counter_values = tfg_grp["delta_time"][
                range_index_read[0] : range_index_read[1]
            ]

            return counter_values


def get_exposuretime_values(
    range_index_read=None,
    scan: Scan = None,
    scan_memory_url: str = None,
    beacon_host: str = None,
    headers: dict = None,
    metadata_file: str = None,
    h5_path_to_mcs: str = None,
    metadata_mcs_group: h5py.Group = None,
    pin_name: str = None,
    header_key_to_pin=HEADERS_KEY_EXPOSURE_TIME,
):
    """
    Generic method to retrieve the exposure time for every frame:
    The exposure time reading comes in microseconds, so a factor product is needed to get the seconds
    - Online: read from the blissdata streams, associated to pin monitor in HSTime
    - Offline: read directly from one column of HS32C
    """
    if range_index_read is None:
        range_index_read = [None, None]

    if scan_memory_url and headers:
        if header_key_to_pin:
            pin_name = headers.get(header_key_to_pin)

        if pin_name is None:
            logger.error(f"No {header_key_to_pin} found in headers")
            return

        stream_exposuretime = match_stream(
            scan=scan,
            scan_memory_url=scan_memory_url,
            beacon_host=beacon_host,
            pin_name=pin_name,
            stream_group="mcs",
            pattern="raw",
        )

        if stream_exposuretime is None:
            return

        stream_values = read_blissdata_stream(
            stream=stream_exposuretime, range_to_read=range_index_read
        )

        return stream_values

    elif metadata_mcs_group:
        if "HS32C" not in metadata_mcs_group:
            logger.error(f"No HS32C found in : {metadata_mcs_group}")
            return

        if header_key_to_pin not in metadata_mcs_group:
            logger.error(f"No {header_key_to_pin} found in :{metadata_mcs_group}")
            return

        pin_index = metadata_mcs_group[header_key_to_pin][()]
        counter_values = metadata_mcs_group["HS32C"][
            range_index_read[0] : range_index_read[1], pin_index - 1
        ]
        return counter_values

    elif metadata_file and h5_path_to_mcs:
        with h5py.File(metadata_file, "r") as file:
            if h5_path_to_mcs not in file:
                logger.error(f"No MCS found in : {h5_path_to_mcs}")
                return

            mcs_grp = file[h5_path_to_mcs]

            if "HS32C" not in mcs_grp:
                logger.error(f"No HS32C found in {h5_path_to_mcs}")
                return

            if header_key_to_pin not in mcs_grp:
                logger.error(f"No {header_key_to_pin} found in :{h5_path_to_mcs}")
                return

            pin_index = mcs_grp[header_key_to_pin][()]
            counter_values = mcs_grp["HS32C"][
                range_index_read[0] : range_index_read[1], pin_index - 1
            ]
            return counter_values


def get_monitor_values(
    range_index_read: tuple = None,
    stream_monitor=None,
    scan: Scan = None,
    scan_memory_url: str = None,
    beacon_host: str = None,
    headers: dict = None,
    filename_metadata: str = None,
    h5_path_to_mcs: str = None,
    metadata_mcs_group: h5py.Group = None,
    header_key_to_pin=HEADERS_KEY_MONITOR,
    pin_name=None,
):
    """
    Generic method to retrieve the monitor values:
        - Online: read from the blissdata streams, associated to pin monitor in HSI1
        - Offline: read directly from one column of HS32C
    """
    if range_index_read is None:
        range_index_read = [None, None]

    if stream_monitor or scan or scan_memory_url:
        if stream_monitor:
            ...
        elif scan or scan_memory_url:
            if pin_name:
                ...
            elif header_key_to_pin and headers:
                pin_name = headers.get(header_key_to_pin)

            if pin_name is None:
                return

            stream_monitor = match_stream(
                scan=scan,
                pin_name=pin_name,
                scan_memory_url=scan_memory_url,
                stream_group="scalers",
                beacon_host=beacon_host,
                # pattern="raw",
            )

        if stream_monitor is None:
            return

        stream_values = read_blissdata_stream(
            stream=stream_monitor, range_to_read=range_index_read
        )
        return stream_values

    elif metadata_mcs_group:
        if "HS32V" not in metadata_mcs_group:
            logger.error(f"No HS32V found in : {metadata_mcs_group}")
            return

        if header_key_to_pin not in metadata_mcs_group:
            logger.error(f"No {header_key_to_pin} found in :{metadata_mcs_group}")
            return

        pin_index = metadata_mcs_group[header_key_to_pin][()]
        counter_values = metadata_mcs_group["HS32V"][
            range_index_read[0] : range_index_read[1], pin_index - 1
        ]
        return counter_values

    elif filename_metadata and h5_path_to_mcs:
        with h5py.File(filename_metadata, "r") as file:
            if h5_path_to_mcs not in file:
                logger.error(f"No MCS found in : {h5_path_to_mcs}")
                return

            mcs_grp = file[h5_path_to_mcs]

            if "HS32V" not in mcs_grp:
                logger.error(f"No HS32V found in : {h5_path_to_mcs}")
                return

            if header_key_to_pin not in mcs_grp:
                logger.error(f"No {header_key_to_pin} found in :{h5_path_to_mcs}")
                return

            pin_index = mcs_grp[header_key_to_pin][()]
            counter_values = mcs_grp["HS32V"][
                range_index_read[0] : range_index_read[1], pin_index - 1
            ]
            return counter_values


def get_HS32V_array(
    range_index_read=None,
    scan: Scan = None,
    scan_memory_url: str = None,
    beacon_host: str = None,
    headers=None,
    scalers_keys=None,
    metadata_mcs_group: h5py.Group = None,
):
    """
    Generic method to get the HS32V array (scalers_counters):
        - Online: build the HS32V array reading from the scan streams (scalers), all "HS32N" or only those registered in 'scalers_keys'
        - Offline: read the HS32V array directly from a scalers file
    """
    if scan_memory_url:
        pin_names = [headers[key] for key in headers if "HS32N" in key]
        nb_pins = len(pin_names)

        if range_index_read is None:
            new_hs32v = None
        else:
            new_hs32v = numpy.zeros(
                (range_index_read[1] - range_index_read[0], nb_pins), dtype="float64"
            )

        val_counter_names = scalers_keys.get("val_counter_names", {})
        for pin_index, pin_name in val_counter_names.items():
            stream_hs32v = match_stream(
                scan=scan,
                scan_memory_url=scan_memory_url,
                beacon_host=beacon_host,
                pin_name=pin_name,
                stream_group="scalers",
            )
            if stream_hs32v is None:
                continue

            if new_hs32v is None:
                new_hs32v = numpy.zeros((len(stream_hs32v), nb_pins), dtype="float64")
                range_index_read = [0, len(stream_hs32v)]

            stream_values = read_blissdata_stream(
                stream=stream_hs32v, range_to_read=range_index_read
            )
            if stream_values is None:
                continue
            new_hs32v[:, int(pin_index) - 1] = stream_values

    elif metadata_mcs_group:
        if range_index_read is None:
            range_index_read = [None, None]

        if "HS32V" not in metadata_mcs_group:
            logger.error(f"No HS32V found in scalers:{metadata_mcs_group}")
            return

        new_hs32v = metadata_mcs_group["HS32V"][
            range_index_read[0] : range_index_read[1], :
        ]

    return new_hs32v


def get_HS32C_array(
    range_index_read=None,
    scan: Scan = None,
    scan_memory_url: str = None,
    beacon_host: str = None,
    headers=None,
    scalers_keys=None,
    metadata_mcs_group: h5py.Group = None,
):
    """
    Generic method to get the HS32C array (raw_counters):
        - Online: build the HS32C array reading from the scan streams (mcs), all "HS32N" or only those registered in 'scalers_keys'
        - Offline: read the HS32C array directly from a scalers file
    """
    new_hs32c = None
    if scan_memory_url and headers:
        pin_names = [headers[key] for key in headers if "HS32N" in key]
        nb_pins = len(pin_names)

        if range_index_read is None:
            new_hs32c = None
        else:
            new_hs32c = numpy.full(
                (range_index_read[1] - range_index_read[0], nb_pins),
                fill_value=-1,
                dtype="int64",
            )

        raw_counter_names = scalers_keys.get("raw_counter_names", {})
        for pin_index, pin_name in raw_counter_names.items():
            stream_hs32c = match_stream(
                pin_name=pin_name,
                scan=scan,
                scan_memory_url=scan_memory_url,
                beacon_host=beacon_host,
                stream_group="mcs",
                pattern="raw",
            )
            if stream_hs32c is None:
                continue

            if new_hs32c is None:
                new_hs32c = numpy.full(
                    (len(stream_hs32c), nb_pins), fill_value=-1, dtype="int64"
                )
                range_index_read = [0, len(stream_hs32c)]

            stream_values = read_blissdata_stream(
                stream=stream_hs32c, range_to_read=range_index_read
            )
            if stream_values is None:
                continue
            new_hs32c[:, int(pin_index) - 1] = stream_values

    elif metadata_mcs_group:
        if range_index_read is None:
            range_index_read = [None, None]

        if "HS32C" not in metadata_mcs_group:
            logger.error(f"No HS32C found in scalers:{metadata_mcs_group}")
            return

        new_hs32c = metadata_mcs_group["HS32C"][
            range_index_read[0] : range_index_read[1], :
        ]

    return new_hs32c


def match_stream(
    pin_name,
    scan: Scan = None,
    scan_memory_url=None,
    beacon_host=None,
    stream_group="mcs",  # mcs or scalers
    pattern="",  # like _raw
):
    """
    header_key_to_pin: key in header whose value is the name of the pin
    pin_name: value to find a match in a blissdata stream
    """
    if not scan:
        scan = load_scan(scan_memory_url=scan_memory_url, beacon_host=beacon_host)
    streams = {
        stream_name: stream
        for stream_name, stream in scan.streams.items()
        if stream_name.split(":")[0] == stream_group
    }

    for stream_name, stream in streams.items():
        if str(pin_name) in re.split(":|_", stream_name):
            if pattern in stream_name:
                return stream

    # Search again without cropping the _
    for stream_name, stream in streams.items():
        if str(pin_name) in re.split(":", stream_name):
            if pattern in stream_name:
                return stream


def get_counter_factor(
    scan_memory_url: str = None,
    headers: dict = None,
    metadata_file: str = None,
    h5_path_to_mcs: str = None,
    metadata_mcs_group: h5py.Group = None,
    header_key_to_pin=None,
    pin_name=None,
):
    if scan_memory_url and headers:
        if headers and header_key_to_pin:
            pin_name = headers.get(header_key_to_pin)

        if not pin_name:
            return

        hs32n = {key: headers[key] for key in headers.keys() if "HS32N" in key}
        hs32f = {key: headers[key] for key in headers.keys() if "HS32F" in key}

        for hs32n_key, hs32f_key in zip(hs32n, hs32f):
            if headers[hs32n_key] == pin_name:
                factor = headers[hs32f_key]
                return float(factor)

    elif metadata_mcs_group:
        if header_key_to_pin not in metadata_mcs_group:
            logger.error(f"No {header_key_to_pin} found in:{metadata_mcs_group}")
            return

        pin_index = metadata_mcs_group[header_key_to_pin][()]
        factor = metadata_mcs_group["HS32F"][int(pin_index - 1)]
        return float(factor)

    elif metadata_file and h5_path_to_mcs:
        with h5py.File(metadata_file, "r") as file:
            if h5_path_to_mcs not in file:
                logger.error(f"No MCS found in: {h5_path_to_mcs}")
                return

            mcs_grp = file[h5_path_to_mcs]

            if "HS32F" not in mcs_grp:
                logger.error(f"No HS32F found in:{h5_path_to_mcs}")
                return

            if header_key_to_pin not in mcs_grp:
                logger.error(f"No {header_key_to_pin} found in:{h5_path_to_mcs}")
                return

            pin_index = mcs_grp[header_key_to_pin][()]
            factor = mcs_grp["HS32F"][int(pin_index - 1)]

            return float(factor)


def read_blissdata_stream(stream, range_to_read: list) -> numpy.ndarray:
    """
    Centralized method to slice of blissdata stream
    """
    if range_to_read is None:
        range_to_read = [None, None]
    else:
        attempts = 0
        while len(stream) < range_to_read[1] and attempts < 10:
            time.sleep(0.1)
            attempts += 1

    if len(stream) < range_to_read[1]:
        logger.error(
            f"Requested range {range_to_read} is larger than the stream length {len(stream)}. Adjusting range."
        )

    try:
        read_values = stream[range_to_read[0] : range_to_read[1]]
        return read_values
    except Exception as e:
        logger.error(f"Error reading stream {stream} in {range_to_read=}: {e}")
        return None
