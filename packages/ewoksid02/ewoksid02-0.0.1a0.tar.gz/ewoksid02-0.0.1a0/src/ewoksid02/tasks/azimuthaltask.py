from contextlib import ExitStack

import numexpr
from pyFAI.units import to_unit
from silx.io.h5py_utils import open_item as open_item_silx

from ewoksid02.tasks.id02processingtask import ID02ProcessingTask
from ewoksid02.utils.pyfai import (
    get_gpu_method,
    get_persistent_azimuthal_integrator,
    process_dataset_azim,
)

DEFAULT_NPT_RAD = 1600
DEFAULT_NPT_AZIM = 360


class AzimuthalTask(
    ID02ProcessingTask,
    optional_input_names=[
        "filename_mask",
        "filename_dark",
        "npt2_rad",
        "npt2_azim",
        "unit",
        "Dummy",
        "DDummy",
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
        "method",
        "integration_options",
        "do_variance_formula",
        "variance_formula",
        "save_sum",
    ],
    output_names=[
        "dataset_sum_signal",
        "dataset_sum_normalization",
        "dataset_sum_variance",
        "radial_array",
        "azimuth_array",
    ],
):
    """The `AzimuthalTask` class is responsible for performing azimuthal integration on datasets in the ID02 SAXS pipeline.
    It extends the `ID02ProcessingTask` class and provides additional functionality for handling azimuthal integration-specific
    inputs and processing logic using the pyFAI library.

    Optional Inputs:
        - filename_mask (str): Path to the mask file for masking invalid pixels.
        - filename_dark (str): Path to the file with a dark-current correction.
        - npt2_rad (int): Number of radial bins for the integration.
        - npt2_azim (int): Number of azimuthal bins for the integration.
        - unit (str): Unit for the radial axis (e.g., "q_nm^-1").
        - Dummy (float): Value to replace invalid pixels in the dataset.
        - DDummy (float): Tolerance for dummy pixel replacement.
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
        - method (str): Integration method to be used by pyFAI (e.g., "bbox", "csr").
        - integration_options (dict): Additional options for pyFAI integration.
        - do_variance_formula (bool): Flag to enable variance calculation using a formula. Default is `False`.
        - variance_formula (str): Formula for calculating variance in the dataset.
        - save_sum (bool): To save or not the arrays sum_signal, sum_normalization and sum_variance.
    Outputs:
        - dataset_sum_signal (numpy.ndarray): Summed signal dataset after azimuthal integration.
        - dataset_sum_normalization (numpy.ndarray): Summed normalization dataset after azimuthal integration.
        - dataset_sum_variance (numpy.ndarray): Summed variance dataset after azimuthal integration.
        - radial_array (numpy.ndarray): Radial axis array for the integrated data.
        - azimuth_array (numpy.ndarray): Azimuthal axis array for the integrated data.
    """

    def run(self):
        super().run(processing_type="azim")
        self.update_dataset_azim()

    def get_processing_inputs(self, stack: ExitStack = None) -> dict:
        if stack:
            return self._get_processing_inputs(stack=stack)

        with ExitStack() as stack:
            return self._get_processing_inputs(
                stack=stack,
            )

    def _get_processing_inputs(self, stack: ExitStack) -> dict:
        metadata_parameters_group = None
        if self.filename_metadata_headers_input and self.filename_metadata_mcs_input:
            metadata_parameters_group = self._open_metadata_h5pygroup(
                stack,
                self.filename_metadata_headers_input,
                self.path_to_metadata_headers_input,
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

        processing_params = {
            "filename_mask": self.get_input_value(
                "filename_mask",
                self.get_mask_beamstop_filename(
                    metadata_file_group=metadata_parameters_group
                ),
            ),
            "filename_dark": self.get_input_value(
                "filename_dark",
                self.get_dark_filename(metadata_file_group=metadata_parameters_group),
            ),
            "Dummy": self.get_parameter("Dummy", metadata_parameters_group),
            "DDummy": self.get_parameter("DDummy", metadata_parameters_group),
            "npt2_rad": self.get_parameter("npt2_rad", metadata_parameters_group),
            "npt2_azim": self.get_parameter("npt2_azim", metadata_parameters_group),
            "unit": self.get_parameter("unit", metadata_parameters_group),
            "method": self.get_input_value("method", get_gpu_method()),
            "integration_options": self.get_input_value("integration_options", {}),
            "do_variance_formula": self.get_input_value("do_variance_formula", False),
            "variance_formula": self.get_parameter(
                "variance_formula", metadata_parameters_group
            ),
            "datatype": self.get_input_value("datatype", "float32"),
            "binning": (
                self.get_parameter("BSize_1", metadata_parameters_group),
                self.get_parameter("BSize_2", metadata_parameters_group),
            ),
            "save_variance": self.get_input_value("save_variance", False),
            "save_sum": self.get_input_value("save_sum", False),
            "azimuthal_integrator": azimuthal_integrator,
        }
        if not processing_params.get("npt2_rad"):
            processing_params["npt2_rad"] = DEFAULT_NPT_RAD
        if not processing_params.get("npt2_azim"):
            processing_params["npt2_azim"] = DEFAULT_NPT_AZIM
        return processing_params

    def process(self) -> None:
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

            if self.dataset_variance is not None:
                dataset_variance = self.dataset_variance
            elif self.dataset_sigma is not None:
                dataset_sigma = self.dataset_sigma  # noqa
                Dummy = processing_params.get("Dummy", 0.0)  # noqa
                dataset_variance = numexpr.evaluate(
                    "where(dataset_sigma <= 0.0, Dummy, dataset_sigma ** 2)"
                )
            else:
                dataset_variance = None

            (
                dataset_signal_azim,
                dataset_variance_azim,
                dataset_sigma_azim,
                dataset_sumsignal_azim,
                dataset_sumnorm_azim,
                dataset_sumvariance_azim,
                array_radial,
                array_azim,
            ) = process_dataset_azim(
                dataset_signal=self.dataset_signal,
                dataset_variance=dataset_variance,
                **processing_params,
            )

            self.outputs.dataset_signal = dataset_signal_azim
            self.outputs.dataset_variance = dataset_variance_azim
            self.outputs.dataset_sigma = dataset_sigma_azim
            self.outputs.dataset_sum_signal = dataset_sumsignal_azim
            self.outputs.dataset_sum_normalization = dataset_sumnorm_azim
            self.outputs.dataset_sum_variance = dataset_sumvariance_azim
            self.outputs.radial_array = array_radial
            self.outputs.azimuth_array = array_azim

        self.log_benchmark(self.bench_process)

    def update_dataset_azim(
        self,
    ):
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
                added_dataset=self.outputs.dataset_sum_signal,
                h5_group=nexus_data_grp,
                h5_dataset_name="sum_signal",
            )

            self.update_dataset(
                added_dataset=self.outputs.dataset_sum_normalization,
                h5_group=nexus_data_grp,
                h5_dataset_name="sum_normalization",
            )

            self.update_dataset(
                added_dataset=self.outputs.dataset_sum_variance,
                h5_group=nexus_data_grp,
                h5_dataset_name="sum_variance",
            )

            unit = self.get_parameter("unit", metadata_parameters_group)
            radial_unit = to_unit(unit)

            # Update radial and azimuthal arrays only once
            if radial_unit and self.outputs.radial_array is not None:
                if radial_unit.short_name not in nexus_data_grp:
                    radial_dset = nexus_data_grp.create_dataset(
                        name=radial_unit.short_name,
                        data=self.outputs.radial_array,
                    )
                    radial_dset.attrs["axis"] = "3"
                    radial_dset.attrs["interpretation"] = "scalar"
                    radial_dset.attrs["unit"] = str(radial_unit)

            if self.outputs.azimuth_array is not None:
                if "chi" not in nexus_data_grp:
                    chi_dset = nexus_data_grp.create_dataset(
                        name="chi",
                        data=self.outputs.azimuth_array,
                    )
                    chi_dset.attrs["axis"] = "2"
                    chi_dset.attrs["interpretation"] = "scalar"
                    chi_dset.attrs["unit"] = "deg"

                    nexus_data_grp.attrs["axes"] = [".", "chi", radial_unit.short_name]
