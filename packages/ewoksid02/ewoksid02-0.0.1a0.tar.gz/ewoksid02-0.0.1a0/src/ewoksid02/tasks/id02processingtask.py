import json
import os
import re
import threading
import time
from contextlib import ExitStack
from string import Formatter

import h5py
import hdf5plugin
import numpy
from ewokscore import missing_data
from pyFAI import version as pyFAIVersion
from silx.io.h5py_utils import open_item as open_item_silx

from ewoksid02.tasks.looptask import ID02LoopTask
from ewoksid02.utils.blissdata import (
    copy_group_excluding_dataset,
    get_counter_factor,
    get_deltatime_values,
    get_exposuretime_values,
    get_HS32C_array,
    get_HS32V_array,
    get_intensity0_values,
    get_intensity1_values,
    match_stream,
    read_blissdata_stream,
)
from ewoksid02.utils.io import (
    KEY_BEAMSTOP_MASK_FILE,
    KEY_BEAMSTOP_MASK_FOLDER,
    KEY_DARK_FILE,
    KEY_DARK_FOLDER,
    KEY_DETECTOR_MASK_FILE,
    KEY_DETECTOR_MASK_FOLDER,
    KEY_FLAT_FILE,
    KEY_FLAT_FOLDER,
    KEY_TITLEEXTENSION,
    KEY_WINDOW_FILE,
    KEY_WINDOW_FOLDER,
    get_from_headers,
    get_headers,
    get_isotime,
)

lock = threading.Lock()

PYFAI_PROCESSES = ["norm", "gaps", "2scat", "cave", "azim", "ave", "caving"]
TRUSAXS_PROCESSES = ["scalers", "dispatch"]
ALL_PROCESSES = PYFAI_PROCESSES + TRUSAXS_PROCESSES

PROCESSING_TYPE_TASK = {
    "norm": "ewoksid02.tasks.normalizationtask.NormalizationTask",
    "gaps": "ewoksid02.tasks.cavingtask.CavingGapsTask",
    "2scat": "ewoksid02.tasks.secondaryscatteringtask.SecondaryScatteringTask",
    "cave": "ewoksid02.tasks.cavingtask.CavingBeamstopTask",
    "azim": "ewoksid02.tasks.azimuthaltask.AzimuthalTask",
    "ave": "ewoksid02.tasks.averagetask.AverageTask",
    "scalers": "ewoksid02.tasks.scalerstask.ScalersTask",
}

KEYS_FLOAT = [
    "Center_1",
    "Center_2",
    "Dummy",
    "DDummy",
    "PSize_1",
    "PSize_2",
    "SampleDistance",
    "WaveLength",
]

KEYS_INT = [
    "BSize_1",
    "BSize_2",
    "Offset_1",
    "Offset_2",
    "RasterOrientation",
]

HEADERS_KEY_MONITOR = "HSI1"
HEADERS_KEY_EXPOSURE_TIME = "HSTime"
CHUNK_SIZE_3D = (1, 200, 200)

ENTRY_NAME = "entry_0000"
NXPROCESS_NAME_PYFAI = "PyFAI"
NXPROCESS_NAME_TRUSAXS = "TRUSAXS"
NXPROCESS_NAME_EWOKS = "ewoks"
MCS_NAME = "MCS"
TFG_NAME = "TFG"
NXDATA_NAME = "result_{processing_type}"
DATA_NAME = "data"
DATA_VARIANCE_NAME = "data_variance"
DATA_SIGMA_NAME = "data_errors"

NX_PROCESS_PYFAI_PATH = f"/{ENTRY_NAME}/{NXPROCESS_NAME_PYFAI}"
NX_PROCESS_EWOKS_PATH = f"/{ENTRY_NAME}/{NXPROCESS_NAME_EWOKS}"
NX_PROCESS_PATH_TRUSAXS = f"/{ENTRY_NAME}/{NXPROCESS_NAME_TRUSAXS}"
MCS_PATH = f"{NX_PROCESS_PYFAI_PATH}/{MCS_NAME}"
TFG_PATH = f"{NX_PROCESS_PYFAI_PATH}/{TFG_NAME}"
NXDATA_PATH_FORMAT = f"{NX_PROCESS_PYFAI_PATH}/{NXDATA_NAME}"
DATA_PATH_FORMAT = f"{NXDATA_PATH_FORMAT}/{DATA_NAME}"
DATA_VARIANCE_PATH_FORMAT = f"{NXDATA_PATH_FORMAT}/{DATA_VARIANCE_NAME}"
DATA_SIGMA_PATH_FORMAT = f"{NXDATA_PATH_FORMAT}/{DATA_SIGMA_NAME}"

INFO_COMMON = {"h5path": ENTRY_NAME, "name": "ewoksid02", "value": "0.1"}


class ID02ProcessingTask(
    ID02LoopTask,
    optional_input_names=[
        "filename_metadata",
        "filename_lima",
        "headers",
        "scalers_keys",
        "slow_counters",
        "datatype",
        "subtitle",
        "processing_filename",
        "processing_subtitle",
        "do_processing",
        "do_save",
        "save_variance",
        "save_sigma",
        "force_saving",
        "save_metadata",
    ],
):
    """This class contains processing support methods and saving methods in the ID02 SAXS pipeline.
    It extends the `ID02LoopTask` class and provides additional functionality for handling metadata, processing flags,
    and saving processed data to HDF5 files.This class is designed to be used as part of the ID02 pipeline.It does not contain a process method, that has to be implemented in the child class.

    Optional Inputs:
        - filename_metadata (str): Only for offline processing. Path to the metadata file where the scalers parameters and redis metadata was stored.
        - filename_lima (str): Path to the first Lima file, the only place where some detector metadata can be found.
        - headers (dict): Only for Online processing. Dictionary containing headers information.
        - scalers_keys (dict): Only for Online processing. Dictionary mapping scaler keys to their respective values.
        - slow_counters (list): List with the name of the slow streams from the subscan2.
        - datatype (str): Datatype to be used to save the 2D data. Default and recommended is float32.
        - subtitle (str): Subtitle for the processing task to be added to the output filename.
        - processing_filename (str): Full path to the (new) output file.
        - processing_subtitle (str): Additional subtitle for the processing task.
        - do_processing (bool): Flag to enable or disable processing. Default is `True`.
        - do_save (bool): Flag to enable or disable saving of processed data. Default is `True`.
        - save_variance (bool): Flag to enable or disable saving of variance dataset. Default is `False`.
        - save_sigma (bool): Flag to enable or disable saving of sigma dataset. Default is `True`.
        - force_saving (bool): Flag to enable or disable saving of data eveng if do_processing is False. Default is `False`.
        - save_metadata (bool): Flag to enable or disable saving of metadata. Default is `True`.
    """

    class Benchmark:
        """A context manager for benchmarking."""

        def __init__(self, nb_frames, benchmark_name="processing"):
            self.nb_frames = nb_frames
            self.benchmark_name = benchmark_name
            self.bench_total_s = 0.0
            self.bench_per_frame_ms = 0.0

        def __enter__(self):
            self.start = time.perf_counter()
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.end = time.perf_counter()
            self.bench_total_s = self.end - self.start
            if self.nb_frames > 0:
                self.bench_per_frame_ms = self.bench_total_s / self.nb_frames * 1000
            else:
                self.bench_per_frame_ms = 0

    def run(self, processing_type):
        super().run()
        self.processing_type = processing_type
        self.bench_process = None
        self.bench_saving = None

        if not self.outputs.continue_pipeline:
            return

        # Processing and saving flags
        self.filename_metadata = self.get_input_value("filename_metadata", None)
        self.filename_lima = self.get_input_value("filename_lima", None)
        self.headers = self.get_input_value("headers", dict())
        self.scalers_keys = self.get_input_value("scalers_keys", dict())
        self.slow_counters = self.get_input_value("slow_counters", list())
        self.processing_filename = self.get_input_value("processing_filename", None)
        self.do_processing = self.get_input_value("do_processing", True)
        self.do_save = self.get_input_value("do_save", True)

        if not self.do_processing:
            self.log_warning(msg=f"Processing {self.processing_type} will be skipped.")
            if not self.get_input_value("force_saving", False):
                self.do_save = False
                self.processing_filename = None
                return

        if not self.do_save:
            self.log_warning("Save flag was set to False, data will not be saved")
            self.processing_filename = None
        elif self.do_save and not self.processing_filename:
            raise ValueError(
                "Processing filename is not set."
            )  # Fix July 2025. Processing filename has to be provided.
            # Either use blissoda/id02 tools or the offline scripts that will generate the processing filename.
            self.processing_filename = self.generate_processing_filename()
            self.log_info(
                f"Processed {self.processing_type} data will be saved in {self.processing_filename}"
            )

        self._check_no_overwriting()
        self._check_processing_routes()
        self._map_metadata_input_paths()
        self._map_output_paths()
        self.process()

        if self.do_save:
            self.save()

    def _check_no_overwriting(self):
        # If online, there is no checkpoint, we assume that the inputs are correct and fresh generated
        # If offline, we need to check if the processing file already exists
        # We rely on the first loop of the pipeline to create the processing file
        if not self.scan_memory_url and self.processing_filename:
            if self.loop_nb == 1 and os.path.exists(self.processing_filename):
                self.log_error(
                    f"Offline processing, processing file {self.processing_filename} already exist. Data will not be saved. Choose another name! Workflow is canceled!"
                )
                # If I raise Exception here, connection with Redis is lost (?)
                # raise Exception
                self.do_processing = False
                self.do_save = False
                self.outputs.continue_pipeline = False

    def _check_processing_routes(self):
        if self.scan_memory_url:
            # For online processing, the metadata is in Redis except headers and detector metadata
            if not self.headers:
                self.log_error(
                    "For online processing, headers should be provided. Some metadata may be missing!"
                )
            if not self.filename_lima:
                self.log_error(
                    "For online processing, (one) LIMA file should be provided. Detector metadata will be missing!"
                )
        else:
            # For offline processing, metadata has to be either in the filename_metadata+filename_lima or in the data file
            if self.filename_metadata and self.filename_lima:
                return
            elif not self.filename_metadata and not self.filename_lima:
                # If no metadata is provided, we trust that filename_data is a processed file.
                self.filename_metadata = self.filename_data
                self.filename_lima = self.filename_data
            elif self.filename_metadata:
                raise ValueError(
                    "LIMA file is not provided. Some metadata will be missing!"
                )
            elif self.filename_lima:
                raise ValueError(
                    "Metadata (scalers) file is not provided. Processing cannot be completed!"
                )

    def _map_metadata_input_paths(self):
        if self.scan_memory_url and self.headers:
            # Online processing
            self.filename_metadata_detector_input = self.filename_lima
            self.path_to_metadata_detector_input = (
                f"{ENTRY_NAME}/ESRF-ID02/{self.detector_name}",
                f"{ENTRY_NAME}/instrument/{self.detector_name}",
            )
            self.filename_metadata_headers_input = self.filename_lima
            self.path_to_metadata_headers_input = (
                f"{ENTRY_NAME}/ESRF-ID02/{self.detector_name}/header",
                f"{ENTRY_NAME}/instrument/{self.detector_name}/header",
            )
            self.filename_metadata_mcs_input = None
            self.path_to_metadata_mcs_input = None
            self.filename_metadata_tfg_input = None
            self.path_to_metadata_tfg_input = None
            self.filename_metadata_titleextension_input = None
            self.path_to_metadata_titleextension_input = None
            self.filename_metadata_raw_input = None
            self.path_to_metadata_raw_input = None
        elif self.filename_data != self.filename_metadata != self.filename_lima:
            # Processing from a raw file
            self.filename_metadata_detector_input = self.filename_lima
            self.path_to_metadata_detector_input = (
                f"{ENTRY_NAME}/ESRF-ID02/{self.detector_name}",
                f"{ENTRY_NAME}/instrument/{self.detector_name}",
            )
            self.filename_metadata_headers_input = self.filename_lima
            self.path_to_metadata_headers_input = (
                f"{ENTRY_NAME}/ESRF-ID02/{self.detector_name}/header",
                f"{ENTRY_NAME}/instrument/{self.detector_name}/header",
            )
            self.filename_metadata_mcs_input = self.filename_metadata
            self.path_to_metadata_mcs_input = (
                f"{ENTRY_NAME}/{NXPROCESS_NAME_TRUSAXS}/MCS"
            )
            self.filename_metadata_tfg_input = self.filename_metadata
            self.path_to_metadata_tfg_input = (
                f"{ENTRY_NAME}/{NXPROCESS_NAME_TRUSAXS}/TFG"
            )
            self.filename_metadata_titleextension_input = self.filename_metadata
            self.path_to_metadata_titleextension_input = (
                f"{ENTRY_NAME}/{NXPROCESS_NAME_TRUSAXS}/parameters"
            )
            self.filename_metadata_raw_input = self.filename_data
            self.path_to_metadata_raw_input = f"{self.scan}.{self.subscan}/measurement"
        elif self.filename_data == self.filename_lima == self.filename_metadata:
            # Processing from a processed file
            self.filename_metadata_detector_input = self.filename_data
            self.path_to_metadata_detector_input = (
                f"{ENTRY_NAME}/{NXPROCESS_NAME_PYFAI}/{self.detector_name}"
            )
            self.filename_metadata_headers_input = self.filename_data
            self.path_to_metadata_headers_input = (
                f"{ENTRY_NAME}/{NXPROCESS_NAME_PYFAI}/parameters"
            )
            self.filename_metadata_mcs_input = self.filename_data
            self.path_to_metadata_mcs_input = f"{ENTRY_NAME}/{NXPROCESS_NAME_PYFAI}/MCS"
            self.filename_metadata_tfg_input = self.filename_data
            self.path_to_metadata_tfg_input = f"{ENTRY_NAME}/{NXPROCESS_NAME_PYFAI}/TFG"
            self.filename_metadata_titleextension_input = self.filename_data
            self.path_to_metadata_titleextension_input = (
                self.path_to_metadata_headers_input
            )
            self.filename_metadata_raw_input = None
            self.path_to_metadata_raw_input = None

    def process(self):
        self.processing_params = {}
        if not self.do_processing or self.dataset_signal.size == 0:
            self.log_warning(f"Skipping processing {self.processing_type}")
            self.do_save = False
            return False
        return True

    def _map_output_paths(self):
        # Write some h5 paths
        if self.processing_type in TRUSAXS_PROCESSES:
            self.path_to_nxprocess_pyfai_output = NX_PROCESS_PATH_TRUSAXS
            self.path_to_nxdata_output = (
                f"{self.path_to_nxprocess_pyfai_output}/result_{self.processing_type}"
            )
            self.path_to_data_signal_processed = "entry_0000/TRUSAXS/MCS"
        else:
            self.path_to_nxprocess_pyfai_output = NX_PROCESS_PYFAI_PATH
            self.path_to_nxdata_output = NXDATA_PATH_FORMAT.format(
                processing_type=self.processing_type
            )
            self.path_to_data_signal_processed = DATA_PATH_FORMAT.format(
                processing_type=self.processing_type
            )
            self.path_to_data_variance_processed = DATA_VARIANCE_PATH_FORMAT.format(
                processing_type=self.processing_type
            )
            self.path_to_data_sigma_processed = DATA_SIGMA_PATH_FORMAT.format(
                processing_type=self.processing_type
            )
        self.path_to_nxprocess_ewoks_output = NX_PROCESS_EWOKS_PATH
        self.path_to_metadata_mcs_output = f"{self.path_to_nxprocess_pyfai_output}/MCS"
        self.path_to_metadata_tfg_output = f"{self.path_to_nxprocess_pyfai_output}/TFG"
        self.path_to_metadata_headers_output = (
            f"{self.path_to_nxprocess_pyfai_output}/parameters"
        )
        self.path_to_metadata_detector_output = (
            f"{self.path_to_nxprocess_pyfai_output}/{self.detector_name}"
        )
        self.path_to_bench_output = f"{self.path_to_nxprocess_pyfai_output}/benchmark"

    def _open_metadata_h5pygroup(
        self, stack: ExitStack, filename: str, h5path: str | tuple
    ) -> h5py.Group:
        if not os.path.exists(filename):
            return None

        metadata_h5pygroup = None
        if isinstance(h5path, str):
            metadata_h5pygroup = stack.enter_context(
                open_item_silx(filename, h5path, mode="r", retry_timeout=1)
            )
        elif isinstance(h5path, tuple):
            for path in h5path:
                try:
                    metadata_h5pygroup = stack.enter_context(
                        open_item_silx(filename, path, mode="r", retry_timeout=0.1)
                    )
                except Exception:
                    self.log_info(f"Could not open {path}. Trying next path.")
                    continue
        return metadata_h5pygroup

    def match_stream(self, pin_name: str, stream_group: str = "scalers"):
        return match_stream(
            scan=self.scan,
            pin_name=pin_name,
            stream_group=stream_group,
        )

    def get_from_headers(
        self, key: str, metadata_parameters_group: h5py.Group = None, to_integer=False
    ):
        return get_from_headers(
            key=key,
            headers=self.headers,
            metadata_file_group=metadata_parameters_group,
            to_integer=to_integer,
        )

    def get_parameter(self, key: str, metadata_parameters_group: h5py = None):
        value = self.get_input_value(key=key)
        if value == missing_data.MISSING_DATA:
            # Try to get it from header
            value = self.get_from_headers(
                key=key, metadata_parameters_group=metadata_parameters_group
            )
        return value

    def get_headers(self, metadata_file_group: h5py.Group = None):
        return get_headers(
            headers=self.headers,
            metadata_file_group=metadata_file_group,
        )

    def get_headers_filename(
        self, folder_key: str, file_key: str, metadata_file_group: h5py.Group = None
    ):
        folder = self.get_from_headers(
            key=folder_key, metadata_parameters_group=metadata_file_group
        )
        file_name = self.get_from_headers(
            key=file_key, metadata_parameters_group=metadata_file_group
        )
        if folder is None or file_name is None:
            return

        filename = os.path.join(folder, file_name)
        if not os.path.exists(filename):
            return
        return filename

    def get_mask_beamstop_filename(self, metadata_file_group: h5py.Group = None):
        return self.get_headers_filename(
            folder_key=KEY_BEAMSTOP_MASK_FOLDER,
            file_key=KEY_BEAMSTOP_MASK_FILE,
            metadata_file_group=metadata_file_group,
        )

    def get_mask_gaps_filename(self, metadata_file_group: h5py.Group = None):
        return self.get_headers_filename(
            folder_key=KEY_DETECTOR_MASK_FOLDER,
            file_key=KEY_DETECTOR_MASK_FILE,
            metadata_file_group=metadata_file_group,
        )

    def get_flat_filename(self, metadata_file_group: h5py.Group = None):
        return self.get_headers_filename(
            folder_key=KEY_FLAT_FOLDER,
            file_key=KEY_FLAT_FILE,
            metadata_file_group=metadata_file_group,
        )

    def get_dark_filename(self, metadata_file_group: h5py.Group = None):
        return self.get_headers_filename(
            folder_key=KEY_DARK_FOLDER,
            file_key=KEY_DARK_FILE,
            metadata_file_group=metadata_file_group,
        )

    def get_mask_window(self, metadata_file_group: h5py.Group = None):
        return self.get_headers_filename(
            folder_key=KEY_WINDOW_FOLDER,
            file_key=KEY_WINDOW_FILE,
            metadata_file_group=metadata_file_group,
        )

    def save(self):
        self.log_info("Saving processed data...")
        with ExitStack() as stack:
            self.create_processing_file()

            if not self.processing_filename or not self.do_save:
                return

            # Append data to the nexus data group
            stack.enter_context(lock)
            self.bench_saving = self.Benchmark(
                nb_frames=len(self.dataset_signal), benchmark_name="saving"
            )
            stack.enter_context(self.bench_saving)
            self.update_id02_data(
                stack=stack,
            )
            if self.get_input_value("save_metadata", True):
                self.update_id02_metadata(stack)

        self.log_benchmark(self.bench_saving)
        self.save_benchmark(self.bench_process)
        self.save_benchmark(self.bench_saving)

    def create_processing_file(self):
        if not self.processing_filename:
            return

        if self.scan_memory_url:
            # With online processing, loop_nb=1 doesnt have to be the beginning of processing
            # Processing files are created if they dont exist, never overwrite, and only if there is self.dataset_signal
            if os.path.exists(self.processing_filename):
                return

            if self.dataset_signal is None:
                return
        else:
            # With offline processing, it will create the file in the first loop, since there will always be dataset_signal

            # Comment for dispatching
            if self.loop_nb == 1 and os.path.exists(self.processing_filename):
                self.log_error(
                    f"Offline processing, processing file {self.processing_filename} already exist. Data will not be saved. Choose another name!"
                )
                self.outputs.repeat = False
                return

            if os.path.exists(self.processing_filename):
                return

            if self.loop_nb > 1:
                return

        # Create directories if needed
        os.makedirs(os.path.dirname(self.processing_filename), exist_ok=True)

        self.log_info(f"Creating file: {self.processing_filename}")
        with ExitStack() as stack:
            root_group = stack.enter_context(
                open_item_silx(filename=self.processing_filename, name="/", mode="w")
            )
            root_group = self.write_root_group(root_group=root_group)

            if self.processing_type in PYFAI_PROCESSES:
                title = (
                    f"{self.processing_filename}:{self.path_to_data_signal_processed}"
                )
            elif self.processing_type in TRUSAXS_PROCESSES:
                title = "TFG metadata collection"
            else:
                title = ""

            # Entry group
            entry_group = self.create_h5_group(
                h5_parent_group=root_group,
                h5_group_name=ENTRY_NAME,
                title=title,
                NX_class="NXentry",
                default=self.path_to_nxdata_output,
            )
            entry_group["program_name"] = self.__class__.__name__
            entry_group["start_time"] = str(get_isotime())
            if self.processing_type in PYFAI_PROCESSES:
                entry_group["detector_name"] = self.detector_name

            # Configuration group
            configuration_group = self.create_h5_group(
                h5_parent_group=entry_group,
                h5_group_name="configuration",
                NX_class="NXnote",
            )
            configuration_group["type"] = "text/json"
            configuration_group["data"] = json.dumps(
                self.get_headers(), indent=2, separators=(",\r\n", ": ")
            )

            # Ewoks configuration group
            ewoksid02_parameters = self.create_h5_group(  # noqa
                h5_parent_group=configuration_group,
                h5_group_name="parameters",
                NX_class="NXcollection",
            )

            # PyFAI Nexus group
            if self.processing_type in PYFAI_PROCESSES:
                process_group = self.create_h5_group(
                    h5_parent_group=entry_group,
                    h5_group_name="PyFAI",
                    NX_class="NXprocess",
                    default=self.path_to_nxdata_output,
                )
                process_group["date"] = str(get_isotime())
                process_group["processing_type"] = self.processing_type
                process_group["program"] = "pyFAI"
                process_group["version"] = pyFAIVersion
            elif self.processing_type in TRUSAXS_PROCESSES:
                process_group = self.create_h5_group(
                    h5_parent_group=entry_group,
                    h5_group_name="TRUSAXS",
                    NX_class="NXinstrument",
                )
                process_group["date"] = str(get_isotime())
                process_group["processing_type"] = self.processing_type
                process_group["program"] = "TruSAXS"
            else:
                return

            # MCS group
            hs32n_array = None
            hs32z_array = None
            hs32f_array = None
            metadata_mcs_input = None

            metadata_mcs_output = self.create_h5_group(
                h5_parent_group=process_group,
                h5_group_name="MCS",
                NX_class="NXcollection",
            )
            metadata_mcs_output["device"] = "bliss"

            if self.scan_memory_url and self.headers:
                hs32n_array = [
                    self.headers[key] for key in self.headers if "HS32N" in key
                ]
                hs32z_array = [
                    self.headers[key] for key in self.headers if "HS32Z" in key
                ]
                hs32f_array = [
                    self.headers[key] for key in self.headers if "HS32F" in key
                ]
            elif (
                self.filename_metadata_mcs_input
                and self.filename_metadata_headers_input
            ):
                metadata_mcs_input = self._open_metadata_h5pygroup(
                    stack,
                    self.filename_metadata_mcs_input,
                    self.path_to_metadata_mcs_input,
                )

                if "HS32N" in metadata_mcs_input:
                    hs32n_array = metadata_mcs_input["HS32N"][:]
                    hs32n_array = [item.decode("UTF-8") for item in hs32n_array]
                else:
                    self.log_error(f"No HS32N found in:{metadata_mcs_input}")

                if "HS32Z" in metadata_mcs_input:
                    hs32z_array = metadata_mcs_input["HS32Z"][:]
                else:
                    self.log_error(f"No HS32Z found in:{metadata_mcs_input}")

                if "HS32F" in metadata_mcs_input:
                    hs32f_array = metadata_mcs_input["HS32F"][:]
                else:
                    self.log_error(f"No HS32F found in:{metadata_mcs_input}")

            if hs32n_array is not None:
                metadata_mcs_output.create_dataset(
                    name="HS32N",
                    data=hs32n_array,
                    dtype=h5py.string_dtype(encoding="utf-8"),
                )

            if hs32z_array is not None:
                metadata_mcs_output.create_dataset(
                    name="HS32Z",
                    data=hs32z_array,
                    dtype="float64",
                )

            if hs32f_array is not None:
                metadata_mcs_output.create_dataset(
                    name="HS32F",
                    data=hs32f_array,
                    dtype="float64",
                )

            # HSI0Factor, HSI1Factor
            for key in ["HSI0Factor", "HSI1Factor"]:
                value = self.get_from_headers(
                    key=key,
                    metadata_parameters_group=metadata_mcs_input,
                )
                if value is not None:
                    metadata_mcs_output.create_dataset(
                        name=key, data=value, dtype="float64"
                    )

            # HSI0, HSI1, HSTime
            for key in ["HSI0", "HSI1", "HSTime"]:
                if self.scalers_keys:
                    for pin_index, pin_name in self.scalers_keys.get(
                        "val_counter_names", {}
                    ).items():
                        if self.get_from_headers(key=key) == pin_name:
                            metadata_mcs_output.create_dataset(
                                name=key, data=pin_index, dtype="int64"
                            )
                            break
                elif metadata_mcs_input:
                    if key in metadata_mcs_input:
                        metadata_mcs_output.create_dataset(
                            name=key, data=metadata_mcs_input[key][()], dtype="int64"
                        )

            # ShutterTime
            for key in ["ShutterOpeningTime", "ShutterClosingTime"]:
                value = self.get_from_headers(key=key)
                if value is None:
                    value = 0.0
                metadata_mcs_output.create_dataset(
                    name=key, data=value, dtype="float64"
                )

            # Parameters & TFG group
            metadata_headers_input = self._open_metadata_h5pygroup(
                stack,
                self.filename_metadata_headers_input,
                self.path_to_metadata_headers_input,
            )
            headers = self.get_headers(metadata_file_group=metadata_headers_input)

            metadata_headers_output = self.create_h5_group(
                h5_parent_group=process_group,
                h5_group_name="parameters",
                NX_class="NXcollection",
            )
            for key, value in headers.items():
                if key in KEYS_FLOAT:
                    metadata_headers_output.create_dataset(
                        name=key, data=value, dtype="float64"
                    )
                elif key in KEYS_INT:
                    metadata_headers_output.create_dataset(
                        name=key, data=value, dtype="int64"
                    )
                elif key == "TitleExtension":
                    continue
                else:
                    value = str(value)
                    metadata_headers_output.create_dataset(
                        name=key,
                        data=value,
                        dtype=h5py.string_dtype(encoding="utf-8"),
                    )

            # TFG group
            metadata_tfg_output = self.create_h5_group(
                h5_parent_group=process_group,
                h5_group_name="TFG",
                NX_class="NXcollection",
            )
            metadata_tfg_output["device"] = "bliss"

            for key in ["HMStartEpoch", "HMStartTime"]:
                if key in headers:
                    value = str(headers[key])
                    metadata_tfg_output.create_dataset(
                        name=key, data=value, dtype=h5py.string_dtype(encoding="utf-8")
                    )
                else:
                    self.log_warning(f"Key {key} not found in headers")

            # Type some static information
            info_list = [{**INFO_COMMON}]
            info_list += [
                {
                    "h5path": ENTRY_NAME,
                    "name": "processing_type",
                    "value": self.processing_type,
                }
            ]
            info_list += self.processing_info()
            for info_item in info_list:
                h5group = info_item.get("h5path")
                if h5group in root_group:
                    root_group[h5group][info_item["name"]] = str(info_item["value"])

            # Create the ewoks processing group
            ewoks = self.create_h5_group(
                h5_parent_group=root_group,
                h5_group_name=self.path_to_nxprocess_ewoks_output,
                NX_class="NXprocess",
            )

            # Type the history of the processing
            history = self.create_h5_group(
                h5_parent_group=ewoks,
                h5_group_name="history",
                NX_class="NXcollection",
            )
            self.engage_history(
                history_group=history,
            )

    def update_id02_data(
        self,
        stack: ExitStack,
    ):
        if not self.processing_filename:
            return

        file = stack.enter_context(
            open_item_silx(filename=self.processing_filename, name="/", mode="a")
        )
        # Three datasets: data, data_variance, data_errors
        if self.path_to_nxdata_output not in file:
            nexus_data_grp = self.create_h5_group(
                h5_parent_group=file,
                h5_group_name=self.path_to_nxdata_output,
                NX_class="NXdata",
                default=self.path_to_data_signal_processed,
                signal="data",
            )
        else:
            nexus_data_grp = file[self.path_to_nxdata_output]
        self.update_dataset(
            added_dataset=self.outputs.dataset_signal,
            h5_group=nexus_data_grp,
            h5_dataset_name="data",
        )
        if self.get_input_value("save_variance", False):
            self.update_dataset(
                added_dataset=self.outputs.dataset_variance,
                h5_group=nexus_data_grp,
                h5_dataset_name="data_variance",
            )
        if self.get_input_value("save_sigma", True):
            self.update_dataset(
                added_dataset=self.outputs.dataset_sigma,
                h5_group=nexus_data_grp,
                h5_dataset_name="data_errors",
            )

    def update_id02_metadata(self, stack: ExitStack):
        if not self.processing_filename:
            return

        if self.dataset_signal.size == 0:
            return

        # Update MCS group
        if self.processing_type not in ALL_PROCESSES:
            self.log_error(f"Processing type {self.processing_type} not valid")
            return

        file_output = stack.enter_context(
            open_item_silx(filename=self.processing_filename, name="/", mode="a")
        )
        metadata_mcs_output = file_output.require_group(
            self.path_to_metadata_mcs_output
        )
        metadata_tfg_output = file_output.require_group(
            self.path_to_metadata_tfg_output
        )
        metadata_headers_output = file_output.require_group(
            self.path_to_metadata_headers_output
        )
        nexus_data_grp_destination = file_output.require_group(
            self.path_to_nxdata_output
        )

        metadata_mcs_input = None
        metadata_tfg_input = None
        metadata_titleextension_input = None
        metadata_detector_input = None
        if (
            self.filename_metadata_mcs_input
            and self.filename_metadata_tfg_input
            and self.filename_metadata_headers_input
            and self.filename_metadata_titleextension_input
        ):
            metadata_mcs_input = self._open_metadata_h5pygroup(
                stack, self.filename_metadata_mcs_input, self.path_to_metadata_mcs_input
            )
            metadata_tfg_input = self._open_metadata_h5pygroup(
                stack, self.filename_metadata_tfg_input, self.path_to_metadata_tfg_input
            )
            metadata_titleextension_input = self._open_metadata_h5pygroup(
                stack,
                self.filename_metadata_titleextension_input,
                self.path_to_metadata_titleextension_input,
            )
            metadata_detector_input = self._open_metadata_h5pygroup(
                stack,
                self.filename_metadata_detector_input,
                self.path_to_metadata_detector_input,
            )

        # Update HS32C
        self.update_hs32c(
            mcs_group_destination=metadata_mcs_output,
            mcs_group_source=metadata_mcs_input,
        )

        # Update HS32V
        self.update_hs32v(
            mcs_group_destination=metadata_mcs_output,
            mcs_group_source=metadata_mcs_input,
        )

        # Update ExposureTime
        self.update_exposure_time(
            mcs_group=metadata_mcs_output,
            mcs_group_source=metadata_mcs_input,
        )

        # Update TFG group
        self.update_delta_time(
            tfg_group=metadata_tfg_output,
            nexus_data_grp=nexus_data_grp_destination,
            tfg_group_source=metadata_tfg_input,
        )

        # Update Intensity datasets (Needs HS32V updated)
        self.update_intensity_metadata(
            mcs_group_destination=metadata_mcs_output,
            mcs_group_source=metadata_mcs_input,
        )

        # MCS: raw and interpreted (interpolated values)
        self.update_raw_group(
            mcs_group_destination=metadata_mcs_output,
            mcs_group_source=metadata_mcs_input,
        )

        self.update_interpreted_group(
            mcs_group_destination=metadata_mcs_output,
            mcs_group_source=metadata_mcs_input,
        )

        # Update TitleExtension
        self.update_title_extension(
            parameters_group_destination=metadata_headers_output,
            parameters_group_source=metadata_titleextension_input,
        )

        # Update NexusDetector with metadata from the RAW_DATA file (has to be accesible). To be done only once
        if (
            self.processing_type not in TRUSAXS_PROCESSES
            and self.path_to_metadata_detector_output not in file_output
        ):
            if metadata_detector_input is not None:
                metadata_detector_output = self.create_h5_group(
                    h5_parent_group=file_output,
                    h5_group_name=self.path_to_metadata_detector_output,
                    NX_class="NXdetector",
                )

                self.update_nexus_detector_group(
                    nxdetector_group_destination=metadata_detector_output,
                    nxdetector_group_source=metadata_detector_input,
                )

        # Save the processing params (only once)
        nxprocess_ewoks = file_output[self.path_to_nxprocess_ewoks_output]
        self.save_processing_params(h5_parent_group=nxprocess_ewoks)

    def update_nexus_detector_group(
        self,
        nxdetector_group_destination: h5py.Group = None,
        nxdetector_group_source: h5py.Group = None,
    ):
        for name, item in nxdetector_group_source.items():
            if isinstance(item, h5py.Group):
                # Recursively copy subgroups
                new_subgroup = nxdetector_group_destination.create_group(name)
                copy_group_excluding_dataset(item, new_subgroup, "data")
            elif isinstance(item, h5py.Dataset):
                if name != "data":  # Skip the excluded dataset
                    nxdetector_group_source.copy(
                        name, nxdetector_group_destination, name=name
                    )

    def update_hs32c(
        self, mcs_group_destination: str, mcs_group_source: h5py.Group = None
    ):
        new_hs32c = get_HS32C_array(
            scan=self.scan,
            scan_memory_url=self.scan_memory_url,
            beacon_host=self.beacon_host,
            range_index_read=self.range_index_read,
            headers=self.headers,
            scalers_keys=self.scalers_keys,
            metadata_mcs_group=mcs_group_source,
        )

        self.update_dataset(
            added_dataset=new_hs32c,
            h5_group=mcs_group_destination,
            h5_dataset_name="HS32C",
        )

    def update_hs32v(
        self, mcs_group_destination: str, mcs_group_source: h5py.Group = None
    ):
        new_hs32v = get_HS32V_array(
            scan=self.scan,
            scan_memory_url=self.scan_memory_url,
            beacon_host=self.beacon_host,
            range_index_read=self.range_index_read,
            headers=self.headers,
            scalers_keys=self.scalers_keys,
            metadata_mcs_group=mcs_group_source,
        )

        self.update_dataset(
            added_dataset=new_hs32v,
            h5_group=mcs_group_destination,
            h5_dataset_name="HS32V",
        )

    def update_exposure_time(
        self,
        mcs_group: h5py.Group,
        mcs_group_source: h5py.Group = None,
    ):
        exposition_time_raw = get_exposuretime_values(
            scan=self.scan,
            scan_memory_url=self.scan_memory_url,
            beacon_host=self.beacon_host,
            range_index_read=self.range_index_read,
            headers=self.headers,
            metadata_mcs_group=mcs_group_source,
        )
        if exposition_time_raw is None:
            self.log_warning("Default exposure_time zeros will be used")
            exposition_time_raw = numpy.zeros(
                self.range_index_read[1] - self.range_index_read[0]
            )

        exposure_time_factor = get_counter_factor(
            scan_memory_url=self.scan_memory_url,
            headers=self.headers,
            metadata_mcs_group=mcs_group_source,
            header_key_to_pin="HSTime",
        )
        if exposure_time_factor is None:
            self.log_warning("Default exposure time factor 1.0 will be used")
            exposure_time_factor = 1.0

        exposition_time = exposition_time_raw * exposure_time_factor

        self.update_dataset(
            added_dataset=exposition_time,
            h5_group=mcs_group,
            h5_dataset_name="ExposureTime",
        )

    def update_title_extension(
        self,
        parameters_group_destination: h5py.Group,
        parameters_group_source: h5py.Group = None,
    ):
        slow_counters = self.get_input_value("slow_counters", [])

        # The title extensions will always be the size of last index (from 0 -> last_frame)
        new_title_extensions = numpy.full(
            shape=(self.range_index_read[1],),
            fill_value="",
            dtype=h5py.string_dtype(encoding="utf-8"),
        )

        if self.scan_memory_url:
            title_extension_template = self.get_from_headers(
                key=KEY_TITLEEXTENSION,
                metadata_parameters_group=parameters_group_source,
            )

            if title_extension_template is None:
                self.log_warning("TitleExtension not found.")
            else:
                parsed_template = [
                    (motor_name, stream_name, format_spec)
                    for motor_name, stream_name, format_spec, _ in Formatter().parse(
                        title_extension_template
                    )
                    if stream_name is not None
                ]

                for title_extension_item in parsed_template:
                    motor_name_te, stream_name_te, format_spec = title_extension_item
                    regex_stream = re.compile(stream_name_te.replace("_", "[:_]"))

                    stream_name = next(
                        (
                            stream_name
                            for stream_name, stream in self.generate_streams()
                            if re.fullmatch(regex_stream, stream.name)
                        ),
                        None,
                    )

                    if stream_name is None:
                        self.log_warning(
                            f"No stream found for TitleExtension item: {title_extension_item}"
                        )
                        continue

                    # Check if the stream is slow
                    # nb_frames_fast = len(self.scan.streams["mcs:epoch"])
                    nb_frames_stream = len(self.scan.streams[stream_name])

                    if (
                        nb_frames_stream < self.range_index_read[1]
                    ) and stream_name in slow_counters:
                        values = self.interpolate_slow_stream(
                            slow_streamname=stream_name,
                        )
                        if values is None:
                            continue
                        # range_index_read = [0, len(values)]
                    else:
                        values = read_blissdata_stream(
                            stream=self.scan.streams[stream_name],
                            range_to_read=[0, self.range_index_read[1]],
                        )
                        if values is None:
                            continue
                        # range_index_read = [0, len(values)]

                    if len(values) != self.range_index_read[1]:
                        self.log_warning(
                            f"title extension: {len(values)=}, {self.range_index_read=}"
                        )

                    for index in range(len(new_title_extensions)):
                        value = (
                            format(values[index], format_spec)
                            if format_spec
                            else values[index]
                        )
                        cell = f"{motor_name_te}{value}"
                        if new_title_extensions[index] == "":
                            new_title_extensions[index] = cell
                        else:
                            new_title_extensions[index] += f"{cell}"

        elif parameters_group_source:
            if "TitleExtension" in parameters_group_source:
                new_title_extensions = numpy.array(
                    parameters_group_source["TitleExtension"][
                        0 : self.range_index_read[1]
                    ],
                    dtype=h5py.string_dtype(encoding="utf-8"),
                )
            else:
                self.log_error(f"No TitleExtension found in {parameters_group_source}")

        if new_title_extensions is None:
            new_title_extensions = numpy.full(
                shape=((self.range_index_read[1] - self.range_index_read[0]),),
                fill_value="",
                dtype=h5py.string_dtype(encoding="utf-8"),
            )

        self.update_dataset(
            added_dataset=new_title_extensions,
            h5_group=parameters_group_destination,
            h5_dataset_name="TitleExtension",
            range_index_read=[0, self.range_index_read[1]],
        )

    def update_delta_time(
        self,
        tfg_group: h5py.Group,
        nexus_data_grp: h5py.Group,
        tfg_group_source: h5py.Group = None,
    ):
        new_deltatime = get_deltatime_values(
            scan=self.scan,
            scan_memory_url=self.scan_memory_url,
            beacon_host=self.beacon_host,
            range_index_read=self.range_index_read,
            metadata_tfg_group=tfg_group_source,
        )

        self.update_dataset(
            added_dataset=new_deltatime,
            h5_group=tfg_group,
            h5_dataset_name="delta_time",
        )
        self.update_dataset(
            added_dataset=new_deltatime,
            h5_group=nexus_data_grp,
            h5_dataset_name="t",
            unit="s",
        )

    def update_intensity_metadata(
        self,
        mcs_group_destination: h5py.Group,
        mcs_group_source: h5py.Group = None,
    ):
        intensity0uncor, intensity0shutcor = get_intensity0_values(
            scan=self.scan,
            scan_memory_url=self.scan_memory_url,
            beacon_host=self.beacon_host,
            range_index_read=self.range_index_read,
            headers=self.headers,
            metadata_mcs_group=mcs_group_source,
        )

        intensity1uncor, intensity1shutcor = get_intensity1_values(
            scan=self.scan,
            scan_memory_url=self.scan_memory_url,
            beacon_host=self.beacon_host,
            range_index_read=self.range_index_read,
            headers=self.headers,
            metadata_mcs_group=mcs_group_source,
        )

        self.update_dataset(
            added_dataset=intensity0shutcor,
            h5_group=mcs_group_destination,
            h5_dataset_name="Intensity0ShutCor",
        )
        self.update_dataset(
            added_dataset=intensity1shutcor,
            h5_group=mcs_group_destination,
            h5_dataset_name="Intensity1ShutCor",
        )
        self.update_dataset(
            added_dataset=intensity0uncor,
            h5_group=mcs_group_destination,
            h5_dataset_name="Intensity0UnCor",
        )
        self.update_dataset(
            added_dataset=intensity1uncor,
            h5_group=mcs_group_destination,
            h5_dataset_name="Intensity1UnCor",
        )

    def update_raw_group(
        self,
        mcs_group_destination: h5py.Group,
        mcs_group_source: h5py.Group = None,
    ):
        self.update_raw_subscan1(
            mcs_group_destination=mcs_group_destination,
            mcs_group_source=mcs_group_source,
        )
        self.update_raw_subscan2(
            mcs_group_destination=mcs_group_destination,
            mcs_group_source=mcs_group_source,
        )

    def update_raw_subscan1(
        self, mcs_group_destination: h5py.Group, mcs_group_source: h5py.Group = None
    ):
        raw_group_dest = mcs_group_destination.require_group("raw")
        subscan1_grp_dest = raw_group_dest.require_group("subscan_1")

        if self.scan_memory_url:
            KEY_STREAMS_SUBSCAN1 = ["mcs", "scalers", "trm", "stats_max"]
            for stream_name, stream in self.generate_streams():
                if any(key in stream_name for key in KEY_STREAMS_SUBSCAN1):
                    values = read_blissdata_stream(
                        stream=stream,
                        range_to_read=self.range_index_read,
                    )
                    dset_name = stream_name.split(":")[-1]
                    if "stats_max" in stream_name:
                        dset_name = f"{stream_name.split(':')[0]}_stats_max"

                    self.update_dataset(
                        added_dataset=values,
                        h5_group=subscan1_grp_dest,
                        h5_dataset_name=dset_name,
                    )

        elif self.filename_metadata and mcs_group_source:
            if "raw" not in mcs_group_source:
                self.log_error(f"No raw group in {mcs_group_source}")
                return

            raw_group_source = mcs_group_source["raw"]
            if "subscan_1" not in raw_group_source:
                self.log_error(f"No subscan_1 in {raw_group_source}")
                return

            subscan1_grp_source = raw_group_source["subscan_1"]

            for dset_name in subscan1_grp_source:
                values = subscan1_grp_source[dset_name][
                    self.range_index_read[0] : self.range_index_read[1]
                ]

                self.update_dataset(
                    added_dataset=values,
                    h5_group=subscan1_grp_dest,
                    h5_dataset_name=dset_name,
                )

    def update_raw_subscan2(
        self, mcs_group_destination: h5py.Group, mcs_group_source: h5py.Group = None
    ):
        if self.scan_memory_url:
            # Will be done in update_interpreted_subscan2
            ...

        elif self.filename_metadata and mcs_group_source:
            # Only once, this is detached from the subscan1 loop
            raw_group = mcs_group_destination.require_group("raw")
            if "subscan_2" in raw_group:
                return

            if "raw" not in mcs_group_source:
                self.log_warning(f"No raw group in {mcs_group_source}")
                return

            raw_group_source = mcs_group_source["raw"]
            if "subscan_2" not in raw_group_source:
                self.log_warning(f"No subscan_2 in {raw_group_source}")
                return

            subscan2_grp_dest = raw_group.require_group("subscan_2")
            subscan2_grp_source = raw_group_source["subscan_2"]
            for dset_name in subscan2_grp_source:
                values = subscan2_grp_source[dset_name][:]

                if values.dtype.kind == "U":
                    dtype = h5py.string_dtype(encoding="utf-8")
                    values = values.astype(h5py.string_dtype(encoding="utf-8"))
                else:
                    dtype = values.dtype

                subscan2_grp_dest.create_dataset(
                    name=dset_name,
                    shape=values.shape,
                    maxshape=(None,),
                    dtype=dtype,
                )

    def update_interpreted_group(
        self,
        mcs_group_destination: h5py.Group,
        mcs_group_source: h5py.Group = None,
    ):
        self.update_interpreted_subscan1(
            mcs_group=mcs_group_destination,
            mcs_group_source=mcs_group_source,
        )
        self.update_interpreted_subscan2(
            mcs_group=mcs_group_destination,
        )

    def update_interpreted_subscan1(
        self, mcs_group: h5py.Group, mcs_group_source: h5py.Group
    ):
        interpreted_grp = mcs_group.require_group("interpreted")
        if self.scan_memory_url:
            KEY_STREAMS_SUBSCAN1 = ["mcs", "scalers", "trm", "stats_max"]
            for stream_name, stream in self.generate_streams():
                if any(key in stream_name for key in KEY_STREAMS_SUBSCAN1):
                    values = read_blissdata_stream(
                        stream=stream,
                        range_to_read=self.range_index_read,
                    )
                    dset_name = stream_name.replace(":", "_")
                    self.update_dataset(
                        added_dataset=values,
                        h5_group=interpreted_grp,
                        h5_dataset_name=dset_name,
                    )

        elif self.filename_metadata and mcs_group_source:
            if "interpreted" not in mcs_group_source:
                self.log_error(f"No interpreted group in {mcs_group_source}")
                return

            interpreted_grp_source = mcs_group_source["interpreted"]
            for dset_name in interpreted_grp_source:
                values = interpreted_grp_source[dset_name][
                    self.range_index_read[0] : self.range_index_read[1]
                ]
                self.update_dataset(
                    added_dataset=values,
                    h5_group=interpreted_grp,
                    h5_dataset_name=dset_name,
                )

    def interpolate_slow_stream(
        self,
        slow_streamname: str,
        slow_epoch_streamname: str = "sampling_timer:epoch",
        fast_epoch_streamname: str = "mcs:epoch",
    ):
        slow_stream = self.scan.streams.get(slow_streamname)
        slow_epoch_stream = self.scan.streams.get(slow_epoch_streamname)
        fast_epoch_stream = self.scan.streams.get(fast_epoch_streamname)
        for name, s in [
            (slow_streamname, slow_stream),
            (slow_epoch_streamname, slow_epoch_stream),
            (fast_epoch_streamname, fast_epoch_stream),
        ]:
            if s is None:
                self.log_error(
                    f"Stream {name} not found in scan streams. Cannot interpolate."
                )
                return

        nb_slow_frames = min(len(slow_stream), len(slow_epoch_stream))
        if nb_slow_frames == 0:
            self.log_warning(
                f"Slow Stream {slow_streamname} is empty. Cannot interpolate."
            )
            return

        # stream_values contains the maximum number of elements (0 -> nb_av_frames)
        slow_stream_values = read_blissdata_stream(
            stream=slow_stream,
            range_to_read=[0, nb_slow_frames],
        )
        slow_epoch_values = read_blissdata_stream(
            stream=slow_epoch_stream,
            range_to_read=[0, nb_slow_frames],
        )

        # nb_fast_frames = len(fast_epoch_stream)
        fast_epoch_values = read_blissdata_stream(
            stream=fast_epoch_stream,
            range_to_read=[0, self.range_index_read[1]],
        )

        # len(interpdata) = len(fast_epoch_values)
        slow_stream_interp_values = numpy.interp(
            fast_epoch_values, slow_epoch_values, slow_stream_values
        )
        return slow_stream_interp_values

    def update_interpreted_subscan2(
        self,
        mcs_group: h5py.Group,
    ):
        interpreted_grp = mcs_group.require_group("interpreted")
        raw_grp = mcs_group.require_group("raw")

        if self.scan_memory_url:
            slow_counters = self.get_input_value("slow_counters", [])
            for stream_name, stream in self.generate_streams():
                if stream_name in slow_counters:
                    key_name_interpreted = f"{stream_name.replace(':', '_')}"
                    key_name_raw_subscan2 = f"{stream_name.replace(':', '_')}"
                elif "sampling_timer" in stream_name:
                    key_name_interpreted = f"{stream_name.replace(':', '_')}"
                    key_name_raw_subscan2 = stream_name.split(":")[-1]
                else:
                    continue

                slow_stream = stream
                nb_slow_frames = len(slow_stream)
                if nb_slow_frames == 0:
                    self.log_warning(
                        f"Slow stream {stream_name} is empty. Cannot interpolate."
                    )
                    continue

                slow_stream_values = read_blissdata_stream(
                    stream=slow_stream,
                    range_to_read=[0, nb_slow_frames],
                )

                # Paste the non-interpolated values into raw-subscan2
                subscan2_grp = raw_grp.require_group("subscan_2")

                if key_name_raw_subscan2 not in subscan2_grp:
                    dset_raw_subscan2 = subscan2_grp.create_dataset(
                        name=key_name_raw_subscan2,
                        shape=numpy.array(stream).shape,
                        maxshape=(None,),
                        dtype=numpy.array(stream).dtype,
                    )
                else:
                    dset_raw_subscan2 = subscan2_grp[key_name_raw_subscan2]
                if len(dset_raw_subscan2) == nb_slow_frames:
                    continue

                dset_raw_subscan2.resize((nb_slow_frames,))
                dset_raw_subscan2[:] = slow_stream_values

                if "sampling_timer" in stream_name:
                    # These counters do not need to be interpolated
                    continue

                interpolated_values = self.interpolate_slow_stream(
                    slow_streamname=stream_name,
                )
                if interpolated_values is None:
                    continue

                if key_name_interpreted not in interpreted_grp:
                    dset_interpreted = interpreted_grp.create_dataset(
                        name=key_name_interpreted,
                        shape=(0,),
                        maxshape=(None,),
                        dtype=interpolated_values.dtype,
                    )
                else:
                    dset_interpreted = interpreted_grp[key_name_interpreted]
                dset_interpreted.resize((len(interpolated_values),))
                dset_interpreted[:] = interpolated_values
        else:
            # Nothing, because if it's offline, nothing has to be interpolated
            pass

    def interpolate_subscan2(
        self, slow_epoch_values, slow_stream_values, fast_epoch_values
    ):
        interpdata = numpy.interp(
            fast_epoch_values, slow_epoch_values, slow_stream_values
        )
        return interpdata

    def create_h5_group(
        self,
        h5_parent_group: h5py.Group,
        h5_group_name: str,
        title: str = None,
        **kwargs,
    ) -> h5py.Group:
        """
        Unified method to create a group in a HDF5 file with additional attributes.

        h5_parent_group: h5py.Group - Parent group where the new group will be created
        h5_group_name: str - Name of the new group
        title: str - Title of the group
        kwargs: dict - Additional arguments to add as attributes in the group
        """
        if h5_group_name in h5_parent_group:
            self.log_warning(
                f"Group {h5_group_name} already exists in {h5_parent_group.name}"
            )
            return

        h5_group = h5_parent_group.create_group(h5_group_name)
        if title:
            h5_group["title"] = title
        for key, value in kwargs.items():
            h5_group.attrs[key] = value
        return h5_group

    def update_dataset(
        self,
        added_dataset: numpy.ndarray,
        h5_group: h5py.Group,
        h5_dataset_name: str,
        range_index_read: tuple = None,
        **kwargs,
    ) -> None:
        """
        Update a dataset in a HDF5 file with new data.
        It will create the dataset if it does not exist.

        added_dataset: numpy.ndarray - Array with the new data. It has to contain an additional dimension to the data
        h5_group: h5py.Group - Group in the HDF5 file where the dataset is located
        h5_dataset_name: str - Name of the dataset in h5_group
        kwargs: dict - Additional arguments to add as attributes in the dataset
        """
        if range_index_read is None:
            range_index_read = self.range_index_read

        if added_dataset is None or len(added_dataset) == 0:
            return

        if not isinstance(added_dataset, numpy.ndarray):
            self.log_error(f"Added dataset is not a numpy array. {type(added_dataset)}")
            return

        self.log_debug(
            f"Updating dataset {h5_dataset_name} with {len(added_dataset)} new frames"
        )

        ndim = added_dataset.ndim
        if h5_dataset_name not in h5_group:
            if ndim == 3:
                interpretation = "image"
                dtype = self.get_input_value("datatype", "float32")
                compression = hdf5plugin.Bitshuffle(cname="lz4")
                chunks = CHUNK_SIZE_3D
            elif ndim == 2:
                interpretation = "spectrum"
                dtype = "float64"
                compression = None
                chunks = None
            elif ndim == 1:
                interpretation = "scalar"
                dtype = added_dataset.dtype
                compression = None
                chunks = None
                if added_dataset.dtype.kind == "U":
                    dtype = h5py.string_dtype(encoding="utf-8")
                    added_dataset = added_dataset.astype(
                        h5py.string_dtype(encoding="utf-8")
                    )

            dset = h5_group.create_dataset(
                name=h5_dataset_name,
                shape=(0,) + added_dataset.shape[1:ndim],
                maxshape=(None,) + added_dataset.shape[1:ndim],
                chunks=chunks,
                dtype=dtype,
                compression=compression,
            )
            dset.attrs["interpretation"] = interpretation
            for key, value in kwargs.items():
                dset.attrs[key] = value
        else:
            dset = h5_group[h5_dataset_name]
        minimum_needed_length = max(self.last_index_read, len(added_dataset))
        if len(dset) < minimum_needed_length:
            dset.resize((minimum_needed_length, *dset.shape[1:ndim]))

        slice_end = max(self.last_index_read, minimum_needed_length)
        slice_init = slice_end - len(added_dataset)

        try:
            dset[slice_init:slice_end] = added_dataset
            self.log_debug(
                f"Dataset {h5_dataset_name} updated with {len(added_dataset)} frames"
            )
        except Exception as e:
            self.log_error(
                f"{e}: Failed while saving {h5_dataset_name}. dset.shape={dset.shape}, {added_dataset.shape=}"
            )

    def write_root_group(self, root_group: h5py.Group) -> h5py.Group:
        self.log_debug("Creating root group")
        root_group.attrs["HDF5_Version"] = h5py.version.hdf5_version
        root_group.attrs["NX_class"] = "NXroot"
        root_group.attrs["creator"] = "ewoksid02"
        root_group.attrs["file_name"] = str(self.processing_filename)
        root_group.attrs["file_time"] = get_isotime()
        root_group.attrs["default"] = ENTRY_NAME
        return root_group

    def save_benchmark(
        self,
        bench,
    ):
        if not self.do_save:
            return

        benchmark_name = bench.benchmark_name
        total_time = bench.bench_total_s
        time_per_frame = bench.bench_per_frame_ms
        nb_frames = bench.nb_frames

        with ExitStack() as stack:
            if not self.processing_filename or not self.do_save:
                return

            # Append data to the nexus data group
            stack.enter_context(lock)
            processing_file = stack.enter_context(
                open_item_silx(filename=self.processing_filename, name="/", mode="a")
            )

            if self.path_to_bench_output not in processing_file:
                bench_grp = self.create_h5_group(
                    h5_parent_group=processing_file,
                    h5_group_name=self.path_to_bench_output,
                    title="Benchmark",
                    NX_class="NXdata",
                    default=self.path_to_bench_output,
                    signal="data",
                )
            else:
                bench_grp = processing_file[self.path_to_bench_output]

            if f"{benchmark_name}_loop_nb" not in bench_grp:
                loop_dset = bench_grp.create_dataset(
                    name=f"{benchmark_name}_loop_nb",
                    dtype="int32",
                    shape=(0,),
                    maxshape=(None,),
                )
                perframe_dset = bench_grp.create_dataset(
                    name=f"{benchmark_name}_per_frame",
                    dtype="float32",
                    shape=(0,),
                    maxshape=(None,),
                )
                perframe_mean_dset = bench_grp.create_dataset(
                    name=f"{benchmark_name}_per_frame_mean",
                    dtype="float32",
                    data=time_per_frame,
                )
                perframe_std_dset = bench_grp.create_dataset(
                    name=f"{benchmark_name}_per_frame_std",
                    dtype="float32",
                    data=0.0,
                )
                nbframes_dset = bench_grp.create_dataset(
                    name=f"{benchmark_name}_nb_frames",
                    dtype="int32",
                    shape=(0,),
                    maxshape=(None,),
                )
                total_dset = bench_grp.create_dataset(
                    name=f"{benchmark_name}_total",
                    dtype="float32",
                    shape=(0,),
                    maxshape=(None,),
                )
                accumulated_dset = bench_grp.create_dataset(
                    name=f"{benchmark_name}_accumulated",
                    dtype="float32",
                    shape=(0,),
                    maxshape=(None,),
                )
            else:
                loop_dset = bench_grp[f"{benchmark_name}_loop_nb"]
                perframe_dset = bench_grp[f"{benchmark_name}_per_frame"]
                perframe_mean_dset = bench_grp[f"{benchmark_name}_per_frame_mean"]
                perframe_std_dset = bench_grp[f"{benchmark_name}_per_frame_std"]
                nbframes_dset = bench_grp[f"{benchmark_name}_nb_frames"]
                total_dset = bench_grp[f"{benchmark_name}_total"]
                accumulated_dset = bench_grp[f"{benchmark_name}_accumulated"]

            # Append new data
            loop_dset.resize((loop_dset.shape[0] + 1,))
            perframe_dset.resize((perframe_dset.shape[0] + 1,))
            nbframes_dset.resize((nbframes_dset.shape[0] + 1,))
            total_dset.resize((total_dset.shape[0] + 1,))
            accumulated_dset.resize((accumulated_dset.shape[0] + 1,))

            loop_dset[-1] = self.loop_nb
            perframe_dset[-1] = time_per_frame
            nbframes_dset[-1] = nb_frames
            total_dset[-1] = total_time
            if len(accumulated_dset) == 1:
                accumulated_dset[-1] = total_time
            else:
                accumulated_dset[-1] = accumulated_dset[-2] + total_time

            perframe_mean_dset[()] = perframe_dset[:].mean()
            perframe_std_dset[()] = perframe_dset[:].std()

    def save_processing_params(self, h5_parent_group: h5py.Group):
        if "processing" in h5_parent_group:
            return

        processing = self.create_h5_group(
            h5_parent_group=h5_parent_group,
            h5_group_name="processing",
            NX_class="NXcollection",
        )

        for key, value in self.processing_params.items():
            if isinstance(value, (int, float, numpy.ndarray, str)):
                processing.create_dataset(name=key, data=value)
                continue

            if isinstance(value, dict):
                value = json.dumps(value)
                processing.create_dataset(name=key, data=value)
                continue
            try:
                processing.create_dataset(name=key, data=str(value))
            except Exception:
                value = json.dumps(value.as_dict())
                processing.create_dataset(name=key, data=value)

    def engage_history(self, history_group: h5py.Group): ...

    def processing_info(self) -> list:
        return []
