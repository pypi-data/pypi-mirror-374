import gc
import logging
import os

import numpy
import psutil
from ewokscore import Task
from silx.io.h5py_utils import open_item as open_item_silx

from ewoksid02.utils.blissdata import (
    LIMA_URL_TEMPLATE_ID02,
    continue_pipeline_bliss,
    continue_pipeline_offline,
    load_scan,
    read_dataset_offline,
    read_dataset_online,
    read_datasets_offline,
)

logger = logging.getLogger(__name__)


class ID02LoopTask(
    Task,
    input_names=[
        "detector_name",
    ],
    optional_input_names=[
        "scan_memory_url",
        "filename_data",  # Bliss master file for a dataset
        "scan_nb",
        "subscan",
        "max_slice_size",
        "last_index_read",
        "range_index_read",
        "loop_nb",
        "dataset_signal",
        "dataset_variance",
        "dataset_sigma",
        "reading_node",
        "lima_url_template",
        "lima_url_template_args",
        "beacon_host",
        "log_level",
        "info",
        "info_history",
    ],
    output_names=[
        "last_index_read",
        "loop_nb",
        "dataset_signal",
        "dataset_variance",
        "dataset_sigma",
        "continue_pipeline",
        "info_history",
    ],
):
    """The `ID02LoopTask` class is a base task designed to handle iterative data processing in the ID02 SAXS pipeline.
    It provides functionality for reading datasets, managing processing loops, and controlling the pipeline flow.
    This class is intended to be extended by more specific tasks, such as `ID02ProcessingTask`.
    This class could be seen also a Reading node.

    Inputs:
        - detector_name (str): Name of the detector used for data acquisition. This is the only mandatory input.
    Optional Inputs:
        - scan_memory_url (str): URL for accessing scan memory in online processing.
        - filename_data (str): Path to the dataset file (Master file, Nexus writer) for offline processing.
        - scan_nb (int): Scan number for identifying the dataset.
        - subscan (int): Subscan number for processing. Default is `1`.
        - max_slice_size (int): Maximum number of frames to process in one iteration. Default is `20`.
        - last_index_read (int): Index of the last frame read in the dataset. Default is `0`.
        - range_index_read (list): Range of indices to read from the dataset. This parameter is not propagated to the next task.
        - loop_nb (int): Current loop iteration number. Default is `0`.
        - dataset_signal (numpy.ndarray): Signal dataset to be processed.
        - dataset_variance (numpy.ndarray): Variance dataset to be processed.
        - dataset_sigma (numpy.ndarray): Sigma dataset to be processed.
        - reading_node (bool): Flag to indicate if the task should read data from the node.
        - lima_url_template (str): Format string to locate the Lima file and the path to the data inside that file.
        - lima_url_template_args (dict): Dictionary to format the lima_url_template.
        - beacon_host (str): Host and port to plug blissdata to the correct beacon server. Only for online processing.
        - log_level (str): Logging level for the task. Default is `"warning"`.
        - info (dict): Additional metadata to save.
        - info_history (dict): Additional metadata to propagate and save, creating a history of processing.
    Outputs:
        - last_index_read (int): Updated index of the last frame read.
        - loop_nb (int): Updated loop iteration number.
        - dataset_signal (numpy.ndarray): Processed signal dataset.
        - dataset_variance (numpy.ndarray): Processed variance dataset.
        - dataset_sigma (numpy.ndarray): Processed sigma dataset.
        - continue_pipeline (bool): Flag to indicate whether the pipeline should continue.
        - info_history (dict): Additional metadata to propagate and save, creating a history of processing.

    Usage:
    ------
    This class is intended to be used as part of a larger pipeline for SAXS data processing.
    It handles the reading and propagation of data:
    - If 'reading_node' is set to True, it will try to get data from Blissdata (online processing) or from a static file (offline processing).
    - If 'reading_node' is set to False (default) and it receives a dataset, it will just propagate the dataset to the next task.
    Since the SAXS pipeline is a loop, if `reading_node` to True, the task will become a kind of entry-exit valve for the pipeline.
    """

    def run(self):
        self.pid = os.getpid()
        self._process = psutil.Process()
        self.detector_name = self.inputs.detector_name
        self.scan_memory_url = self.get_input_value("scan_memory_url", None)
        self.filename_data = self.get_input_value("filename_data", None)
        self.scan_nb = self.get_input_value("scan_nb", None)
        self.subscan = self.get_input_value("subscan", 1)
        self.max_slice_size = self.get_input_value("max_slice_size", 50)
        self.last_index_read = self.get_input_value("last_index_read", 0)
        self.range_index_read = self.get_input_value("range_index_read", None)
        self.loop_nb = self.get_input_value("loop_nb", 0)
        self.beacon_host = self.get_input_value("beacon_host", None)

        self.outputs.last_index_read = self.last_index_read
        self.outputs.loop_nb = self.loop_nb
        self.outputs.dataset_signal = self.get_input_value("dataset_signal", None)
        self.outputs.dataset_variance = self.get_input_value("dataset_variance", None)
        self.outputs.dataset_sigma = self.get_input_value("dataset_sigma", None)
        self.outputs.continue_pipeline = True

        self.set_log_level(log_level=self.get_input_value("log_level", "warning"))
        if self.scan_memory_url:
            self._prepare_online_processing()
        else:
            self._prepare_offline_processing()

        gc.collect()
        self.log_allocated_memory()
        self._get_datasets()

    def _get_datasets(self) -> None:
        already_processed_frames = self.last_index_read
        if (
            self.get_input_value("reading_node", False)
            or self.get_input_value("dataset_signal", None) is None
        ):
            if (
                self.range_index_read
                and self.last_index_read >= self.range_index_read[1]
            ):
                self.log_error(
                    f"Requested range_index {self.range_index_read} has been already read! (Last index: {self.last_index_read}). Canceling the pipeline."
                )
                self.outputs.continue_pipeline = False
                return

            # These incoming datasets cannot be None, they will always be numpy arrays (maybe empty)
            dataset_signal, dataset_variance, dataset_sigma = self.get_new_datasets()
            nb_read_frames = len(dataset_signal)
            if nb_read_frames > 0:
                new_last_index = self.last_index_read + nb_read_frames
                if self.range_index_read is None:
                    self.range_index_read = [
                        self.last_index_read,
                        new_last_index,
                    ]
                    self.last_index_read = self.last_index_read + nb_read_frames
                else:
                    self.last_index_read += len(dataset_signal)

                logger.info(
                    f"""
                            Already processed frames: {already_processed_frames},
                            New dataset sliced with {nb_read_frames} frames, index: {already_processed_frames} -> {self.last_index_read},
                            New last index: {self.last_index_read},
                            """
                )
            else:
                if self.scan_memory_url:
                    self.outputs.continue_pipeline = continue_pipeline_bliss(
                        scan=self.scan,
                        detector_name=self.detector_name,
                        last_index_read=self.last_index_read,
                        subscan=self.subscan,
                        lima_url_template=self.get_input_value(
                            "lima_url_template", LIMA_URL_TEMPLATE_ID02
                        ),
                        lima_url_template_args=self.get_input_value(
                            "lima_url_template_args", {}
                        ),
                    )
                elif self.filename_data:
                    self.outputs.continue_pipeline = continue_pipeline_offline(
                        filename_data=self.filename_data,
                        last_index_read=self.last_index_read,
                        path_to_data_signal=self.path_to_data_signal_source,
                    )
            self.loop_nb += 1
            self.outputs.loop_nb = self.loop_nb
            self.outputs.last_index_read = self.last_index_read
            self.outputs.dataset_signal = dataset_signal
            self.outputs.dataset_variance = dataset_variance
            self.outputs.dataset_sigma = dataset_sigma

        self.dataset_signal = self.outputs.dataset_signal
        self.dataset_variance = self.outputs.dataset_variance
        self.dataset_sigma = self.outputs.dataset_sigma
        self.range_index_read = self.range_index_read or [
            self.last_index_read - len(self.dataset_signal),
            self.last_index_read,
        ]

    def set_log_level(self, log_level="warning"):
        if not isinstance(log_level, str):
            return
        if log_level.lower() == "info":
            logger.setLevel(logging.INFO)
        elif log_level.lower() == "warning":
            logger.setLevel(logging.WARNING)
        elif log_level.lower() == "error":
            logger.setLevel(logging.ERROR)
        elif log_level.lower() == "debug":
            logger.setLevel(logging.DEBUG)

    def log_debug(self, msg):
        self._log(level="debug", msg=msg)

    def log_info(self, msg):
        self._log(level="info", msg=msg)

    def log_warning(self, msg):
        self._log(level="warning", msg=msg)

    def log_error(self, msg):
        self._log(level="error", msg=msg)

    def _log(self, level, msg):
        msg = f"Loop #{self.loop_nb}: {self.__class__.__name__}: (PID: {self.pid}): {msg}. "
        logger.__getattribute__(level)(msg)

    def log_allocated_memory(self):
        mem_usage_GB = self._process.memory_info().rss / 1e9
        total_mem_GB = psutil.virtual_memory().total / 1e9
        # used_mem_GB = psutil.virtual_memory().used / 1e9
        available_mem_GB = psutil.virtual_memory().available / 1e9

        if available_mem_GB / total_mem_GB < 0.1:
            mem_message = "Low memory available"
            color_prefix = "\033[91m"
        elif available_mem_GB / total_mem_GB < 0.3:
            mem_message = "Medium memory available"
            color_prefix = "\033[93m"
        else:
            mem_message = "Sufficient memory available"
            color_prefix = "\033[92m"
        color_suffix = "\033[0m"

        logger.info(
            f"{color_prefix}Loop #{self.loop_nb}: {self.__class__.__name__}: (PID: {self.pid}): \
                Memory: {mem_usage_GB}GB used; {available_mem_GB}GB available. {mem_message}{color_suffix}"
        )

    def log_benchmark(self, bench):
        self.log_info(
            f"Benchmark. Total ({bench.nb_frames}). {bench.benchmark_name}: {bench.bench_total_s:.2f} s. Per frame: {bench.bench_per_frame_ms:.2f} ms"
        )

    def _prepare_online_processing(self):
        if not self.scan_memory_url.startswith("esrf:scan:"):
            raise ValueError(
                f"scan_memory_url {self.scan_memory_url} is not compatible as it should start with 'esrf:scan:'"
            )

        if not os.environ.get("BEACON_HOST"):
            raise ValueError(
                "Online processing requires a BEACON_HOST environment variable"
            )

        self.scan = self.get_scan()
        self.filename_data = self.scan.info["filename"]
        self.scan_nb = self.scan.info["scan_nb"]
        self.path_to_detector_source = (
            f"/{self.scan_nb}.{self.subscan}/instrument/{self.detector_name}"
        )
        self.path_to_data_signal_source = f"{self.path_to_detector_source}/data"
        self.path_to_data_variance_source = None
        self.path_to_data_sigma_source = None

    def _prepare_offline_processing(self):
        self.scan = None

        if not self.filename_data or not os.path.exists(self.filename_data):
            raise ValueError(f"filename_data {self.filename_data} does not exist")

        with open_item_silx(self.filename_data, "/", "r") as file_input:
            if self.scan_nb is None:
                self.scan_nb = self.scan_nb or 1

            if f"{self.scan_nb}.{self.subscan}" in file_input:
                # This is a BLISS dataset file
                self.path_to_detector_source = (
                    f"/{self.scan_nb}.{self.subscan}/instrument/{self.detector_name}"
                )
                self.path_to_data_signal_source = f"{self.path_to_detector_source}/data"
                self.path_to_data_variance_source = None
                self.path_to_data_sigma_source = None

            elif "entry_0000/PyFAI" in file_input:
                # This is an ewoks/dahu processed file
                result_groups = [
                    grp for grp in file_input["entry_0000/PyFAI/"] if "result_" in grp
                ]
                if result_groups:
                    self.path_to_data_signal_source = (
                        f"entry_0000/PyFAI/{result_groups[0]}/data"
                    )
                    self.path_to_data_variance_source = (
                        f"entry_0000/PyFAI/{result_groups[0]}/data_variance"
                    )
                    self.path_to_data_sigma_source = (
                        f"entry_0000/PyFAI/{result_groups[0]}/data_errors"
                    )
                    self.path_to_detector_source = (
                        f"entry_0000/PyFAI/{self.detector_name}"
                    )
            else:
                raise ValueError(
                    f"filename_data {self.filename_data} is not a valid BLISS dataset file or ewoks/dahu processed file"
                )

    def get_scan(self):
        if self.scan_memory_url:
            return load_scan(
                scan_memory_url=self.scan_memory_url, beacon_host=self.beacon_host
            )

    def generate_streams(self):
        if self.scan:
            for stream_name, stream in self.scan.streams.items():
                yield stream_name, stream

    def get_new_datasets(self):
        if self.scan_memory_url:
            dataset_signal, dataset_variance, dataset_sigma = (
                self.get_datasets_from_bliss()
            )
        else:
            dataset_signal, dataset_variance, dataset_sigma = (
                self.get_datasets_from_static_file()
            )
        if dataset_signal is None or len(dataset_signal) == 0:
            return numpy.array([]), numpy.array([]), numpy.array([])
        else:
            return dataset_signal, dataset_variance, dataset_sigma

    def get_datasets_from_bliss(self):
        """Get the dataset from the bliss scan memory."""
        if not self.scan_memory_url:
            self.log_error("scan_memory_url is mandatory to get dataset from bliss")
            return

        if not os.environ.get("BEACON_HOST"):
            self.log_error(
                "Online processing requires a BEACON_HOST environment variable"
            )
            return
        dataset_signal = read_dataset_online(
            scan=self.scan,
            detector_name=self.detector_name,
            lima_url_template=self.get_input_value(
                "lima_url_template", LIMA_URL_TEMPLATE_ID02
            ),
            lima_url_template_args=self.get_input_value("lima_url_template_args", {}),
            subscan=self.subscan,
            last_index_read=self.last_index_read,
            max_slice_size=self.max_slice_size,
            range_index_read=self.range_index_read,
        )
        dataset_variance = numpy.array([])
        dataset_sigma = numpy.array([])

        return dataset_signal, dataset_variance, dataset_sigma

    def get_datasets_from_static_file(self):
        """Get the dataset from the static file."""
        if not self.filename_data:
            self.log_error("filename_data is mandatory to get dataset from static file")
            return
        dataset_signal, dataset_variance, dataset_sigma = read_datasets_offline(
            data_filename=self.filename_data,
            path_to_data_signal=self.path_to_data_signal_source,
            path_to_data_variance=self.path_to_data_variance_source,
            path_to_data_sigma=self.path_to_data_sigma_source,
            last_index_read=self.last_index_read,
            max_slice_size=self.max_slice_size,
            range_index_read=self.range_index_read,
        )

        return dataset_signal, dataset_variance, dataset_sigma


class LoopTask(
    Task,
    optional_input_names=[
        "detector_name",
        "scan_memory_url",
        "filename_data",
        "scan_nb",
        "subscan",
        "max_slice_size",
        "last_index_read",
        "range_index_read",
        "loop_nb",
        "dataset",
        "reading_node",
        "lima_url_template",
        "lima_url_template_args",
        "beacon_host",
    ],
    output_names=[
        "last_index_read",
        "loop_nb",
        "dataset",
        "continue_pipeline",
    ],
):
    """The `LoopTask` class is a base task designed to handle iterative data processing.
    It provides functionality for reading datasets, managing processing loops, and controlling the pipeline flow.
    This class could be seen also a Reading node.

    Optional Inputs:
        - detector_name (str): Name of the detector used for data acquisition. This is the only mandatory input.
        - scan_memory_url (str): URL for accessing scan memory in online processing.
        - filename_data (str): Path to the dataset file (Master file, Nexus writer) for offline processing.
        - scan_nb (int): Scan number for identifying the dataset.
        - subscan (int): Subscan number for processing. Default is `1`.
        - max_slice_size (int): Maximum number of frames to process in one iteration. Default is `20`.
        - last_index_read (int): Index of the last frame read in the dataset. Default is `0`.
        - range_index_read (list): Range of indices to read from the dataset. This parameter is not propagated to the next task.
        - loop_nb (int): Current loop iteration number. Default is `0`.
        - dataset (numpy.ndarray): Signal dataset to be processed.
        - reading_node (bool): Flag to indicate if the task should read data from the node.
        - lima_url_template (str): Format string to locate the Lima file and the path to the data inside that file.
        - lima_url_template_args (dict): Dictionary to format the lima_url_template.
        - beacon_host (str): Host and port to plug blissdata to the correct beacon server. Only for online processing.
    Outputs:
        - last_index_read (int): Updated index of the last frame read.
        - loop_nb (int): Updated loop iteration number.
        - dataset (numpy.ndarray): Processed signal dataset.
        - continue_pipeline (bool): Flag to indicate whether the pipeline should continue.
    """

    def get_data(self) -> None:
        last_index_read = self.get_input_value("last_index_read", 0)
        range_index_read = self.get_input_value("range_index_read", None)
        loop_nb = self.get_input_value("loop_nb", 0)
        dataset = self.get_input_value("dataset", None)

        self.outputs.last_index_read = last_index_read
        self.outputs.dataset = dataset
        self.outputs.loop_nb = loop_nb
        self.outputs.continue_pipeline = True

        if self.get_input_value("reading_node", False) or dataset is None:
            if self.get_input_value("detector_name", None) is None:
                raise ValueError("detector_name is mandatory to read new data")

            if range_index_read and last_index_read >= range_index_read[1]:
                raise ValueError(
                    f"Requested range_index {range_index_read} has been already read! (Last index: {last_index_read}). Canceling the pipeline."
                )

            new_read_dataset = self.get_new_dataset()
            if new_read_dataset is None:
                new_read_dataset = numpy.array([])

            nb_read_frames = len(new_read_dataset)
            if nb_read_frames > 0:
                new_last_index = last_index_read + nb_read_frames
                new_range_index = [
                    last_index_read,
                    new_last_index,
                ]
                logger.info(
                    f"""
                            Already processed frames: {last_index_read},
                            New dataset sliced with {nb_read_frames} frames,
                            New range_index_read: {new_range_index},
                            New last index: {new_last_index},
                            """
                )
                self.outputs.last_index_read = new_last_index
            else:
                scan_memory_url = self.get_input_value("scan_memory_url", None)
                filename_data = self.get_input_value("filename_data", None)
                scan_nb = self.get_input_value("scan_nb", 1)
                subscan = self.get_input_value("subscan", 1)

                if scan_memory_url:
                    self.outputs.continue_pipeline = continue_pipeline_bliss(
                        scan=self.scan,
                        detector_name=self.inputs.detector_name,
                        last_index_read=last_index_read,
                        subscan=subscan,
                        lima_url_template=self.get_input_value(
                            "lima_url_template", None
                        ),
                        lima_url_template_args=self.get_input_value(
                            "lima_url_template_args", {}
                        ),
                    )
                elif filename_data:
                    self.outputs.continue_pipeline = continue_pipeline_offline(
                        filename_data=filename_data,
                        last_index_read=last_index_read,
                        path_to_data_signal=f"/{scan_nb}.{subscan}/instrument/{self.inputs.detector_name}/data",
                    )

            self.outputs.dataset = new_read_dataset
            self.outputs.loop_nb = loop_nb + 1
        self.last_index_read = self.outputs.last_index_read
        self.range_index_read = [
            self.last_index_read - len(self.outputs.dataset),
            self.last_index_read,
        ]
        return self.outputs.dataset

    def get_new_dataset(self):
        if self.get_input_value("scan_memory_url", None):
            return self._get_datasets_from_bliss()
        else:
            return self._get_datasets_from_static_file()

    def _get_datasets_from_bliss(self):
        """Get the dataset from the bliss scan memory."""
        if not os.environ.get("BEACON_HOST"):
            logger.error(
                "Online processing requires a BEACON_HOST environment variable"
            )
            return

        return read_dataset_online(
            scan=self.scan,
            detector_name=self.inputs.detector_name,
            lima_url_template=self.get_input_value("lima_url_template", None),
            lima_url_template_args=self.get_input_value("lima_url_template_args", {}),
            subscan=self.get_input_value("subscan", 1),
            last_index_read=self.get_input_value("last_index_read", 0),
            max_slice_size=self.get_input_value("max_slice_size", 20),
            range_index_read=self.get_input_value("range_index_read", None),
        )

    def _get_datasets_from_static_file(self):
        """Get the dataset from the static file."""
        return read_dataset_offline(
            filename_data=self.inputs.filename_data,
            detector_name=self.inputs.detector_name,
            scan_nb=self.get_input_value("scan_nb", 1),
            last_index_read=self.get_input_value("last_index_read", 0),
            max_slice_size=self.get_input_value("max_slice_size", 20),
            range_index_read=self.get_input_value("range_index_read", None),
        )
