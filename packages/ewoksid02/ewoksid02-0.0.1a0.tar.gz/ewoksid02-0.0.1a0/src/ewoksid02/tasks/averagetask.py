from contextlib import ExitStack

from pyFAI.units import to_unit
from silx.io.h5py_utils import open_item as open_item_silx

from ewoksid02.tasks.id02processingtask import ENTRY_NAME, ID02ProcessingTask
from ewoksid02.utils.average import calculate_average, get_array_limit


class AverageTask(
    ID02ProcessingTask,
    optional_input_names=[
        "dataset_sum_signal",
        "dataset_sum_normalization",
        "dataset_sum_variance",
        "radial_array",
        "azimuth_array",
        "Dummy",
        "unit",
        "azimuth_range",
        "pca_parameters",
    ],
    output_names=[
        "dataset_average_signal_norm",
        "radial_array",
    ],
):
    """The `AverageTask` class is responsible for calculating the average of datasets in the ID02 SAXS pipeline.
    It extends the `ID02ProcessingTask` class and provides additional functionality for handling averaging-specific
    inputs and processing logic. If azimuth_range is not provided, a full average will be performed.

    Optional Inputs:
        - dataset_sum_signal (numpy.ndarray): Sum of signal, non-normalized from an ai.integrate2d result.
        - dataset_sum_normalization (numpy.ndarray): Sum of normalized pixels, from an ai.integrate2d result.
        - dataset_sum_variance (numpy.ndarray): Sum of variance, from an ai.integrate2d result.
        - radial_array (numpy.ndarray): Radial axis array for the dataset.
        - azimuth_array (numpy.ndarray): Azimuthal axis array for the dataset.
        - Dummy (float): Value to replace invalid pixels in the dataset.
        - unit (str): Unit for the radial axis (e.g., "q_nm^-1").
        - azimuth_range (list of tuples): Azimuthal ranges for averaging (e.g., `[(0, 90), (270, 360)]`).
        - pca_parameters (dict): Parameters for Principal Component Analysis (PCA) if applicable.
    Outputs Parameters:
        - dataset_average_signal_norm (numpy.ndarray): Normalized average signal dataset.
        - radial_array (numpy.ndarray): Radial axis array for the averaged data.
    """

    def run(self):
        super().run(processing_type="ave")
        self.update_dataset_ave()

    def get_processing_inputs(self, stack: ExitStack = None) -> dict:
        if stack:
            return self._get_processing_inputs(stack=stack)

        with ExitStack() as stack:
            return self._get_processing_inputs(
                stack=stack,
            )

    def _get_processing_inputs(self, stack: ExitStack) -> dict:
        azimuth_range = self.get_input_value("azimuth_range", None)
        array_ranges = None
        metadata_parameters_group = None
        if self.filename_metadata_headers_input and self.filename_metadata_mcs_input:
            metadata_parameters_group = self._open_metadata_h5pygroup(
                stack,
                self.filename_metadata_headers_input,
                self.path_to_metadata_headers_input,
            )

        if azimuth_range is None:
            self.log_info("There is no azimuth_range. Full average will be done.")
            array_ranges = [(0, -1)]
        else:
            azimuth_array = self.get_input_value("azimuth_array", None)
            if azimuth_array is None:
                self.log_warning(
                    "There is no azimuth_array , azimuth ranges cannot be transformed into array limits. Full average will be done."
                )
                array_ranges = [(0, -1)]
            else:
                array_ranges = [
                    get_array_limit(azimuth_array=azimuth_array, azimuth_range=az_range)
                    for az_range in azimuth_range
                ]

        params_ave = {
            "array_ranges": array_ranges,
            "Dummy": self.get_parameter("Dummy", metadata_parameters_group),
        }

        return params_ave

    def process(self):
        do_process = super().process()
        if do_process is False:
            return

        with ExitStack() as stack:
            self.bench_process = self.Benchmark(
                nb_frames=len(self.dataset_signal), benchmark_name="processing"
            )
            stack.enter_context(self.bench_process)

            processing_params = self.get_processing_inputs(
                stack=stack,
            )
            self.processing_params = processing_params

            (
                dataset_average_intensity,
                dataset_average_signal_norm,
                dataset_average_variance,
                dataset_average_sigma,
            ) = calculate_average(
                dataset_intensity=self.dataset_signal,
                dataset_sum_signal=self.get_input_value("dataset_sum_signal", None),
                dataset_sum_norm=self.get_input_value(
                    "dataset_sum_normalization", None
                ),
                dataset_sum_variance=self.get_input_value("dataset_sum_variance", None),
                calculate_variance=self.get_input_value("save_variance", False),
                **processing_params,
            )

            self.outputs.dataset_signal = dataset_average_intensity
            self.outputs.dataset_average_signal_norm = dataset_average_signal_norm
            self.outputs.dataset_variance = dataset_average_variance
            self.outputs.dataset_sigma = dataset_average_sigma
            self.outputs.radial_array = self.get_input_value("radial_array", None)

        self.log_benchmark(self.bench_process)

    def update_dataset_ave(self):
        if not self.processing_filename or not self.do_save:
            return

        with ExitStack() as stack:
            file = stack.enter_context(
                open_item_silx(filename=self.processing_filename, name="/", mode="a")
            )
            nexus_data_grp = file[self.path_to_nxdata_output]
            metadata_parameters_group = None
            if (
                self.filename_metadata_headers_input
                and self.filename_metadata_mcs_input
            ):
                metadata_parameters_group = self._open_metadata_h5pygroup(
                    stack,
                    self.filename_metadata_headers_input,
                    self.path_to_metadata_headers_input,
                )

            self.update_dataset(
                added_dataset=self.outputs.dataset_average_signal_norm,
                h5_group=nexus_data_grp,
                h5_dataset_name="data_signal_norm",
            )

            # Add nexus data information (only once)
            unit = self.get_parameter("unit", metadata_parameters_group)
            radial_unit = to_unit(unit)

            if radial_unit is not None and radial_unit.short_name not in nexus_data_grp:
                if self.get_input_value("radial_array", None) is not None:
                    radial_dset = nexus_data_grp.create_dataset(
                        name=radial_unit.short_name,
                        data=self.get_input_value("radial_array", None),
                    )
                    radial_dset.attrs["unit"] = str(radial_unit)
                    radial_dset.attrs["interpretation"] = "scalar"
                    radial_dset.attrs["axis"] = "2"
                    nexus_data_grp.attrs["axes"] = [".", radial_unit.short_name]
                    nexus_data_grp.attrs["signal"] = "data"

    def processing_info(self) -> list:
        azimuth_range = self.get_input_value("azimuth_range", [0, 360])
        return [{"h5path": ENTRY_NAME, "name": "ave_limits", "value": azimuth_range}]
