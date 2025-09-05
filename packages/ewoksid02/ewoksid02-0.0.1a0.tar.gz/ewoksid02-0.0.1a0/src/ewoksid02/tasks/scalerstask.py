import threading
from contextlib import ExitStack

from ewoksid02.tasks.id02processingtask import ID02ProcessingTask

lock = threading.Lock()


class ScalersTask(
    ID02ProcessingTask,
):
    """The `ScalersTask` class is responsible for creating a scalers file, that contains a large chunk of the metadata for reprocessing.
    It extends the `ID02ProcessingTask` class and provides additional functionality to apply a standard pyFAI normalization:
        - Methods to read monitor values from the metadata file or from blissdata
        - Methods to read normalization parameters from the metadata file or from the headers
        - Methods to cache pyFAI azimuthal integrator and apply normalization
    """

    def run(self):
        super().run(processing_type="scalers")

    def process(self) -> None:
        return

    def save(
        self,
    ):
        if not self.do_save:
            return

        with ExitStack() as stack:
            self.create_processing_file()

            if not self.processing_filename or not self.do_save:
                return

            # Append data to the nexus data group
            stack.enter_context(lock)
            stack.enter_context(
                self.Benchmark(
                    nb_frames=len(self.dataset_signal), benchmark_name="saving"
                )
            )
            self.processing_params = {}
            self.update_id02_metadata(stack)
