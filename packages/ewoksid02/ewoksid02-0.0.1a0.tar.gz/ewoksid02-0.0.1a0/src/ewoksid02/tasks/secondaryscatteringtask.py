from contextlib import ExitStack

import numexpr
from silx.io.h5py_utils import open_item as open_item_silx

from ewoksid02.tasks.id02processingtask import ID02ProcessingTask
from ewoksid02.utils.secondaryscattering import process_dataset_2scat

DEFAULT_WINDOW_ROI_SIZE = 120
DEFAULT_ALGORITHM = "numpy"


class SecondaryScatteringTask(
    ID02ProcessingTask,
    optional_input_names=[
        "filename_window_wagon",
        "WindowRoiSize",
        "Dummy",
        "Center_1",
        "Center_2",
        "algorithm",
        "pre_caving",
        "filename_mask_to_cave",
        "filename_mask_reference",
        "flip_caving",
        "save_secondary_scattering",
        "BSize_1",
        "BSize_2",
    ],
    output_names=[
        "secondary_scattering",
    ],
):
    """The `SecondaryScatteringTask` class is responsible for calculating and correcting the scattering coming from
    the window that separates the wagon from the flying tube.
    It can be used to correct any scattering source that is close to the detector.

    Optional Inputs:
        - filename_window_wagon (str): Path to the mask file used for defining the scattering window WAXS pattern.
        - WindowRoiSize (float): Distance parameter for subdata extraction during secondary scattering correction.
        - Dummy (float): Value to perform a pre-caving step (to mask the detector gaps)
        - Center_1 (float): Beam center in the first dimension.
        - Center_2 (float): Beam center in the second dimension.
        - algorithm (str): Implementation to perform the secondary scattering correction and pre-caving (numpy or cupy).
        - pre_caving (bool): To perform a caving step before the correction.
        - filename_mask_to_cave (str): Path to the mask file used for the caving operation.
        - filename_mask_reference (str): Path to the reference mask file (kind of a negative mask).
        - flip_caving (bool): Cave the image with its flipped projection, both horizontal and vertical. WARNING: it is physically not correct!
        - save_secondary_scattering (bool): Flag to save the secondary scattering dataset. Default is `False`.
        - BSize_1 (float): Pixel binning 1.
        - BSize_2 (float): Pixel binning 2.
    Outputs:
        - secondary_scattering (numpy.ndarray): Dataset with the calculated secondary scattering.
    """

    def run(self):
        super().run(processing_type="2scat")
        self.update_dataset_2scat()

    def get_processing_inputs(self, stack: ExitStack = None) -> dict:
        if stack:
            return self._get_processing_inputs(stack=stack)

        with ExitStack() as stack:
            return self._get_processing_inputs(
                stack=stack,
            )

    def _get_processing_inputs(self, stack: ExitStack) -> dict:
        # metadata_mcs = None
        metadata_parameters_group = None
        if self.filename_metadata_headers_input and self.filename_metadata_mcs_input:
            metadata_parameters_group = self._open_metadata_h5pygroup(
                stack,
                self.filename_metadata_headers_input,
                self.path_to_metadata_headers_input,
            )

        processing_params = {
            "filename_window_wagon": self.get_input_value(
                "filename_window_wagon",
                self.get_mask_window(metadata_file_group=metadata_parameters_group),
            ),
            "WindowRoiSize": self.get_parameter(
                "WindowRoiSize", metadata_parameters_group
            ),
            "Dummy": self.get_parameter("Dummy", metadata_parameters_group),
            "Center_1": self.get_parameter("Center_1", metadata_parameters_group),
            "Center_2": self.get_parameter("Center_2", metadata_parameters_group),
            "binning": (
                int(self.get_parameter("BSize_1", metadata_parameters_group)),
                int(self.get_parameter("BSize_2", metadata_parameters_group)),
            ),
            "algorithm": self.get_input_value("algorithm", DEFAULT_ALGORITHM),
            "pre_caving": self.get_input_value("pre_caving", True),
            "filename_mask_to_cave": self.get_input_value(
                "filename_mask_to_cave",
                self.get_mask_gaps_filename(
                    metadata_file_group=metadata_parameters_group
                ),
            ),
            "filename_mask_reference": self.get_input_value(
                "filename_mask_reference",
                self.get_mask_beamstop_filename(
                    metadata_file_group=metadata_parameters_group
                ),
            ),
            "flip_caving": self.get_input_value(
                "flip_caving",
                bool(self.get_from_headers("nw_cave_flip")),
            ),
        }

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
                corrected_dataset_signal,
                corrected_dataset_variance,
                corrected_dataset_sigma,
                secondary_scattering,
            ) = process_dataset_2scat(
                dataset_signal=self.dataset_signal,
                dataset_variance=dataset_variance,
                **processing_params,
            )

            self.outputs.dataset_signal = corrected_dataset_signal
            self.outputs.dataset_variance = corrected_dataset_variance
            self.outputs.dataset_sigma = corrected_dataset_sigma
            self.outputs.secondary_scattering = secondary_scattering

        self.log_benchmark(self.bench_process)

    def update_dataset_2scat(self):
        if not self.processing_filename or not self.do_save:
            return

        if not self.get_input_value("save_secondary_scattering", False):
            return

        with ExitStack() as stack:
            file = stack.enter_context(
                open_item_silx(filename=self.processing_filename, name="/", mode="a")
            )
            nexus_data_grp = file[self.path_to_nxdata_output]

            self.update_dataset(
                added_dataset=self.outputs.secondary_scattering,
                range_index_read=self.range_index_read,
                h5_group=nexus_data_grp,
                h5_dataset_name="secondary_scattering",
            )
