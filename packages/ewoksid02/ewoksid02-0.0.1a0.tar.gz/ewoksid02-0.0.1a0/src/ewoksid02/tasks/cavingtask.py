from contextlib import ExitStack

import numpy

from ewoksid02.tasks.id02processingtask import ID02ProcessingTask
from ewoksid02.utils.caving import process_data_caving

DEFAULT_ALGORITHM = "numpy"


class CavingTask(
    ID02ProcessingTask,
    optional_input_names=[
        "Dummy",
        "Center_1",
        "Center_2",
        "filename_mask_to_cave",
        "filename_mask_reference",
        "flip_caving",
        "algorithm",
    ],
):
    """The `CavingTask` class is responsible for applying a "caving" operation to datasets in the ID02 SAXS pipeline.
    The caving is applied to those pixels whose intensity matches with a dummy value + those pixels provided by a mask file.

    Optional Inputs:
        - Dummy (float): Value to replace invalid pixels in the dataset.
        - Center_1 (float): Beam center in the first dimension.
        - Center_2 (float): Beam center in the second dimension.
        - filename_mask_to_cave (str): Path to the mask file used for the caving operation.
        - filename_mask_reference (str): Path to the reference mask file (kind of a negative mask).
        - flip_caving (bool): Cave the image with its flipped projection, both horizontal and vertical. WARNING: it is physically not correct!
        - algorithm (str): Implementation to perform the caving (numpy or cupy).
    """

    def run(self, processing_type: str = "caving"):
        super().run(processing_type=processing_type)

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

        processing_params = {
            "Dummy": self.get_parameter("Dummy", metadata_parameters_group),
            "Center_1": self.get_parameter("Center_1", metadata_parameters_group),
            "Center_2": self.get_parameter("Center_2", metadata_parameters_group),
            "filename_mask_to_cave": self.get_input_value(
                "filename_mask_to_cave", None
            ),
            "filename_mask_reference": self.get_input_value(
                "filename_mask_reference", None
            ),
            "flip_caving": self.get_input_value(
                "flip_caving",
                bool(self.get_from_headers("nw_cave_flip")),
            ),
            "algorithm": self.get_input_value("algorithm", DEFAULT_ALGORITHM),
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
            processing_params = self.get_processing_inputs(stack)
            self.processing_params = processing_params

            self.log_info("Caving data...")
            caved_dataset = process_data_caving(
                data=self.dataset_signal,
                **processing_params,
            )

            if not self.get_input_value("save_variance", False):
                caved_dataset_variance = None
            elif self.dataset_variance is not None:
                caved_dataset_variance = process_data_caving(
                    data=self.dataset_variance,
                    **processing_params,
                )
            else:
                caved_dataset_variance = numpy.zeros_like(caved_dataset)

            if self.dataset_sigma is not None:
                caved_dataset_sigma = process_data_caving(
                    data=self.dataset_sigma,
                    **processing_params,
                )
            else:
                caved_dataset_sigma = numpy.zeros_like(caved_dataset)

            self.log_debug("Caving processing done")
            self.outputs.dataset_signal = caved_dataset
            self.outputs.dataset_variance = caved_dataset_variance
            self.outputs.dataset_sigma = caved_dataset_sigma

        self.log_benchmark(self.bench_process)


class CavingGapsTask(
    CavingTask,
):
    """The `CavingGapsTask` inherits 'CavingTask'.
    Here, it will take the parameters from the headers to perform the caving operation
    and cover the gaps in the dataset and avoid the beamstop. Hence, no explicit mask filenames are needed.
    """

    def run(self, processing_type: str = "gaps"):
        super().run(processing_type=processing_type)

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

        processing_params = {
            "Dummy": self.get_parameter("Dummy", metadata_parameters_group),
            "Center_1": self.get_parameter("Center_1", metadata_parameters_group),
            "Center_2": self.get_parameter("Center_2", metadata_parameters_group),
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
            "algorithm": self.get_input_value("algorithm", DEFAULT_ALGORITHM),
        }

        return processing_params


class CavingBeamstopTask(
    CavingTask,
):
    """The `CavingBeamstopTask` inherits 'CavingTask'.
    Here, it will take the parameters from the headers to perform the caving operation
    and cover the beamstop. Hence, no explicit mask filename is needed.
    """

    def run(self, processing_type: str = "cave"):
        super().run(processing_type=processing_type)

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

        processing_params = {
            "Dummy": self.get_parameter("Dummy", metadata_parameters_group),
            "Center_1": self.get_parameter("Center_1", metadata_parameters_group),
            "Center_2": self.get_parameter("Center_2", metadata_parameters_group),
            "filename_mask_to_cave": self.get_input_value(
                "filename_mask_to_cave",
                self.get_mask_beamstop_filename(
                    metadata_file_group=metadata_parameters_group
                ),
            ),
            "filename_mask_reference": None,
            "flip_caving": self.get_input_value(
                "flip_caving",
                bool(self.get_from_headers("nw_cave_flip")),
            ),
            "algorithm": self.get_input_value("algorithm", DEFAULT_ALGORITHM),
        }

        return processing_params
