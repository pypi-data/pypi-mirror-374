from contextlib import ExitStack

import h5py

from ewoksid02.tasks.id02processingtask import ID02ProcessingTask
from ewoksid02.utils.blissdata import HEADERS_KEY_MONITOR, get_monitor_values
from ewoksid02.utils.normalization import (
    calculate_normalization_values,
    normalize_dataset,
)
from ewoksid02.utils.pyfai import get_persistent_azimuthal_integrator


class NormalizationTask(
    ID02ProcessingTask,
    optional_input_names=[
        "filename_mask",
        "filename_dark",
        "filename_flat",
        "Dummy",
        "DDummy",
        "NormalizationFactor",
        "polarization_factor",
        "polarization_axis_offset",
        "Center_1",
        "Center_2",
        "PSize_1",
        "PSize_2",
        "BSize_1",
        "BSize_2",
        "SampleDistance",
        "WaveLength",
        "DetectorRotation_1",
        "DetectorRotation_2",
        "DetectorRotation_3",
        "pin_monitor",
        "header_pin_monitor",
        "variance_formula",
        "algorithm",
    ],
):
    """The `NormalizationTask` class is responsible for normalizing datasets in the ID02 SAXS pipeline.
    It extends the `ID02ProcessingTask` class and provides additional functionality to apply a standard pyFAI normalization:
    - Methods to read monitor values from the metadata file or from blissdata
    - Methods to read normalization parameters from the metadata file or from the headers
    - Methods to cache pyFAI azimuthal integrator and apply normalization
    - Applies corrections such as masking, dark frame subtraction, flat field correction, and polarization adjustments.

    Optional Inputs:
        - filename_mask (str): Path to the mask file for correcting detector gaps or bad pixels.
        - filename_dark (str): Path to the file for dark current correction.
        - filename_flat (str): Path to the file for flat field correction.
        - Dummy (float): Value to replace invalid pixels in the dataset.
        - DDummy (float): Tolerance for dummy pixel replacement.
        - NormalizationFactor (float): Factor for normalizing the dataset.
        - polarization_factor (float): Factor for polarization correction.
        - polarization_axis_offset (float): Axis for polarization correction.
        - Center_1 (float): Beam center in the first dimension.
        - Center_2 (float): Beam center in the second dimension.
        - PSize_1 (float): Pixel size 1.
        - PSize_2 (float): Pixel size 2.
        - BSize_1 (float): Pixel binning 1.
        - BSize_2 (float): Pixel binning 2.
        - SampleDistance (float): Sample to detector distance in meters.
        - WaveLength (float): Wavelength of beam in meters.
        - DetectorRotation_1 (float): rot2 of pyFAI.
        - DetectorRotation_2 (float): rot1 of pyFAI.
        - DetectorRotation_3 (float): rot3 of pyFAI.
        - pin_monitor (str): Pin to the monitor stream.
        - header_pin_monitor (str): Header key used to monitor values.
        - variance_formula (str): Formula for calculating variance in the dataset.
        - algorithm (str): Implementation to perform the normalization (cython or cupy).
    """

    def run(self):
        super().run(processing_type="norm")

    def get_processing_inputs(self, stack: ExitStack = None) -> dict:
        if stack:
            return self._get_processing_inputs(stack=stack)

        with ExitStack() as stack:
            return self._get_processing_inputs(
                stack=stack,
            )

    def _get_processing_inputs(self, stack: ExitStack) -> dict:
        metadata_mcs = None
        metadata_parameters_group = None
        if self.filename_metadata_headers_input and self.filename_metadata_mcs_input:
            metadata_mcs = self._open_metadata_h5pygroup(
                stack, self.filename_metadata_mcs_input, self.path_to_metadata_mcs_input
            )
            metadata_parameters_group = self._open_metadata_h5pygroup(
                stack,
                self.filename_metadata_headers_input,
                self.path_to_metadata_headers_input,
            )

        normalization_values = self.get_normalization_values(
            metadata_mcs_group=metadata_mcs,
            metadata_parameters_group=metadata_parameters_group,
        )

        azimuthal_integrator = get_persistent_azimuthal_integrator(
            dataset=self.dataset_signal,
            Center_1=self.get_parameter("Center_1", metadata_parameters_group),
            Center_2=self.get_parameter("Center_2", metadata_parameters_group),
            PSize_1=self.get_parameter("PSize_1", metadata_parameters_group),
            PSize_2=self.get_parameter("PSize_2", metadata_parameters_group),
            SampleDistance=self.get_parameter(
                "SampleDistance", metadata_parameters_group
            ),
            WaveLength=self.get_parameter("WaveLength", metadata_parameters_group),
            BSize_1=self.get_parameter("BSize_1", metadata_parameters_group),
            BSize_2=self.get_parameter("BSize_2", metadata_parameters_group),
            DetectorRotation_1=self.get_parameter(
                "DetectorRotation_1", metadata_parameters_group
            ),
            DetectorRotation_2=self.get_parameter(
                "DetectorRotation_2", metadata_parameters_group
            ),
            DetectorRotation_3=self.get_parameter(
                "DetectorRotation_3", metadata_parameters_group
            ),
        )

        params_normalization = {
            "filename_mask": self.get_input_value(
                "filename_mask",
                self.get_mask_gaps_filename(
                    metadata_file_group=metadata_parameters_group
                ),
            ),
            "filename_dark": self.get_input_value(
                "filename_dark",
                self.get_dark_filename(metadata_file_group=metadata_parameters_group),
            ),
            "filename_flat": self.get_input_value(
                "filename_flat",
                self.get_flat_filename(metadata_file_group=metadata_parameters_group),
            ),
            "Dummy": self.get_parameter("Dummy", metadata_parameters_group),
            "DDummy": self.get_parameter("DDummy", metadata_parameters_group),
            "polarization_factor": self.get_parameter(
                "polarization_factor", metadata_parameters_group
            ),
            "polarization_axis_offset": self.get_parameter(
                "polarization_axis_offset", metadata_parameters_group
            ),
            "variance_formula": self.get_parameter(
                "variance_formula", metadata_parameters_group
            ),
            "binning": (
                self.get_parameter("BSize_1", metadata_parameters_group),
                self.get_parameter("BSize_2", metadata_parameters_group),
            ),
            "algorithm": self.get_input_value("algorithm", "float32"),
            "datatype": self.get_input_value("datatype", "float32"),
            "normalization_values": normalization_values,
            "azimuthal_integrator": azimuthal_integrator,
        }
        return params_normalization

    def process(self) -> None:
        do_process = super().process()
        if do_process is False:
            return

        with ExitStack() as stack:
            if len(self.dataset_signal) == 0:
                return

            self.bench_process = self.Benchmark(
                nb_frames=len(self.dataset_signal), benchmark_name="processing"
            )
            stack.enter_context(self.bench_process)

            processing_params = self.get_processing_inputs(
                stack=stack,
            )
            self.processing_params = processing_params

            self.log_info("Normalizing data...")
            (
                dataset_signal_normalized,
                dataset_variance_normalized,
                dataset_sigma_normalized,
            ) = normalize_dataset(
                dataset_signal=self.dataset_signal,
                **processing_params,
            )
            self.log_debug("Processing done")
            self.outputs.dataset_signal = dataset_signal_normalized
            self.outputs.dataset_variance = dataset_variance_normalized
            self.outputs.dataset_sigma = dataset_sigma_normalized

        self.log_benchmark(self.bench_process)

    def get_normalization_values(
        self,
        metadata_mcs_group: h5py.Group = None,
        metadata_parameters_group: h5py.Group = None,
    ):
        return calculate_normalization_values(
            monitor_values=self.get_monitor_values(
                metadata_mcs_group=metadata_mcs_group
            ),
            psize_1=self.get_parameter("PSize_1", metadata_parameters_group),
            psize_2=self.get_parameter("PSize_2", metadata_parameters_group),
            dist=self.get_parameter("SampleDistance", metadata_parameters_group),
            normalization_factor=self.get_parameter(
                "NormalizationFactor", metadata_parameters_group
            ),
        )

    def get_monitor_values(self, metadata_mcs_group: h5py.Group = None):
        """Generic method to read monitor_values online (from blissdata streams)
        or offline (from a group in the scalers file)
        """
        stream_monitor = None
        if self.scan:
            stream_monitor = self.get_stream_monitor()
            if not stream_monitor:
                self.log_error(
                    "No stream monitor could be found. Normalization would be incomplete"
                )
                return

        monitor_values = get_monitor_values(
            range_index_read=self.range_index_read,
            stream_monitor=stream_monitor,
            headers=self.headers,
            metadata_mcs_group=metadata_mcs_group,
        )
        return monitor_values

    def get_stream_monitor(self):
        pin_monitor = self.get_input_value("pin_monitor", None)  # Something like pin4
        header_pin_monitor = self.get_input_value(
            "header_pin_monitor", HEADERS_KEY_MONITOR
        )  # Something like HSI1
        if not pin_monitor and header_pin_monitor and self.headers:
            pin_monitor = self.headers.get(header_pin_monitor)

        if not pin_monitor:
            self.log_error(
                "No pin to any monitor stream! Normalization would be incomplete."
            )
            return

        return self.match_stream(
            pin_name=pin_monitor,
            stream_group="scalers",
        )
