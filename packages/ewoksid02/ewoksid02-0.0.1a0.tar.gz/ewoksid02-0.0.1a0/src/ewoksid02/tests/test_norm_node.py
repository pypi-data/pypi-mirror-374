from ewoksid02.tasks.normalizationtask import NormalizationTask

from .utils import check_processed_data, execute_ewoks, h5py_equivalence


def test_eiger2_normalization(
    inputs_task_generic,
    inputs_task_norm,
    tmp_path,
    filename_processed_norm_reference,
):
    processing_filename = str(tmp_path / "id02test_eiger2_norm.h5")
    inputs = {
        **inputs_task_generic,
        **inputs_task_norm,
        "processing_filename": processing_filename,
    }
    task_norm = NormalizationTask(inputs)
    task_norm.run()
    check_processed_data(
        filename_processed_reference=filename_processed_norm_reference,
        filename_processed_test=processing_filename,
        range_index_read=inputs_task_generic["range_index_read"],
        processing_type="norm",
    )
    h5py_equivalence(
        filename_processed_reference=filename_processed_norm_reference,
        filename_processed_test=processing_filename,
        nb_frames=inputs_task_generic["range_index_read"][1]
        - inputs_task_generic["range_index_read"][0],
    )


def test_eiger2_normalization_cupy(
    cupy_available,
    inputs_task_generic,
    inputs_task_norm,
    tmp_path,
):
    if not cupy_available:
        return

    processing_filename_cython = str(tmp_path / "id02test_eiger2_norm_cython.h5")
    inputs_cython = {
        **inputs_task_generic,
        **inputs_task_norm,
        "processing_filename": processing_filename_cython,
    }
    task_norm_cython = NormalizationTask(inputs_cython)
    task_norm_cython.run()

    processing_filename_cupy = str(tmp_path / "id02test_eiger2_norm_cupy.h5")
    inputs_cupy = {
        **inputs_task_generic,
        **inputs_task_norm,
        "processing_filename": processing_filename_cupy,
    }
    inputs_cupy["algorithm"] = "cupy"
    task_norm_cupy = NormalizationTask(inputs_cupy)
    task_norm_cupy.run()

    check_processed_data(
        filename_processed_reference=processing_filename_cython,
        filename_processed_test=processing_filename_cupy,
        range_index_read=task_norm_cython.range_index_read,
        processing_type="norm",
    )


def test_eiger2_normalization_workflow(
    workflow_norm,
    inputs_task_generic,
    inputs_task_norm,
    tmp_path,
    filename_processed_norm_reference,
):
    inputs = []
    for key, value in inputs_task_generic.items():
        inputs.append({"name": key, "value": value, "all": True})
    for key, value in inputs_task_norm.items():
        inputs.append({"name": key, "value": value, "id": "norm"})
    filename_processing_norm = str(tmp_path / "id02test_eiger2_norm.h5")
    inputs.append(
        {"name": "processing_filename", "value": filename_processing_norm, "id": "norm"}
    )
    _ = execute_ewoks(
        graph=workflow_norm,
        inputs=inputs,
    )
    check_processed_data(
        filename_processed_reference=filename_processed_norm_reference,
        filename_processed_test=filename_processing_norm,
        range_index_read=inputs_task_generic["range_index_read"],
        processing_type="norm",
    )
    h5py_equivalence(
        filename_processed_reference=filename_processed_norm_reference,
        filename_processed_test=filename_processing_norm,
        nb_frames=inputs_task_generic["range_index_read"][1]
        - inputs_task_generic["range_index_read"][0],
    )


def test_eiger2_normalization_workflow_loop(
    workflow_norm,
    inputs_task_generic,
    inputs_task_norm,
    tmp_path,
    filename_processed_norm_reference,
):
    workflow_norm["links"] = [
        {
            "source": "norm",
            "target": "norm",
            "conditions": [{"source_output": "continue_pipeline", "value": True}],
            "map_all_data": True,
        }
    ]

    inputs = []
    for key, value in inputs_task_generic.items():
        inputs.append({"name": key, "value": value, "all": True})
    for key, value in inputs_task_norm.items():
        inputs.append({"name": key, "value": value, "id": "norm"})
    filename_processing_norm = str(tmp_path / "id02test_eiger2_norm.h5")
    inputs.append(
        {"name": "processing_filename", "value": filename_processing_norm, "id": "norm"}
    )
    inputs.append({"name": "reading_node", "value": True, "id": "norm"})

    _ = execute_ewoks(
        graph=workflow_norm,
        inputs=inputs,
    )
    check_processed_data(
        filename_processed_reference=filename_processed_norm_reference,
        filename_processed_test=filename_processing_norm,
        range_index_read=inputs_task_generic["range_index_read"],
        processing_type="norm",
    )
    h5py_equivalence(
        filename_processed_reference=filename_processed_norm_reference,
        filename_processed_test=filename_processing_norm,
        nb_frames=inputs_task_generic["range_index_read"][1]
        - inputs_task_generic["range_index_read"][0],
    )
