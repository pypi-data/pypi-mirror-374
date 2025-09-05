from ewoksid02.tasks.secondaryscatteringtask import SecondaryScatteringTask

from .utils import check_processed_data, execute_ewoks, h5py_equivalence


def test_eiger2_2scat(
    inputs_task_generic,
    inputs_task_2scat,
    tmp_path,
    dataset_signal_norm_new,
    dataset_sigma_norm_new,
    filename_processed_2scat_new,
):
    processing_filename = str(tmp_path / "id02test_eiger2_2scat.h5")
    inputs = {
        **inputs_task_generic,
        **inputs_task_2scat,
        "processing_filename": processing_filename,
        "dataset_signal": dataset_signal_norm_new,
        "dataset_sigma": dataset_sigma_norm_new,
    }
    task_2scat = SecondaryScatteringTask(inputs)
    task_2scat.run()
    check_processed_data(
        filename_processed_reference=filename_processed_2scat_new,
        filename_processed_test=processing_filename,
        range_index_read=inputs_task_generic["range_index_read"],
        processing_type="2scat",
    )
    h5py_equivalence(
        filename_processed_reference=filename_processed_2scat_new,
        filename_processed_test=processing_filename,
        nb_frames=inputs_task_generic["range_index_read"][1]
        - inputs_task_generic["range_index_read"][0],
    )


def test_eiger2_2scat_cupy(
    cupy_available,
    inputs_task_generic,
    inputs_task_2scat,
    tmp_path,
    dataset_signal_norm_new,
    dataset_sigma_norm_new,
):
    if not cupy_available:
        return

    processing_filename_numpy = str(tmp_path / "id02test_eiger2_2scat_numpy.h5")
    inputs_numpy = {
        **inputs_task_generic,
        **inputs_task_2scat,
        "processing_filename": processing_filename_numpy,
        "dataset_signal": dataset_signal_norm_new,
        "dataset_sigma": dataset_sigma_norm_new,
    }
    task_2scat_cython = SecondaryScatteringTask(inputs_numpy)
    task_2scat_cython.run()

    processing_filename_cupy = str(tmp_path / "id02test_eiger2_2scat_cupy.h5")
    inputs_cupy = {
        **inputs_task_generic,
        **inputs_task_2scat,
        "processing_filename": processing_filename_cupy,
        "dataset_signal": dataset_signal_norm_new,
        "dataset_sigma": dataset_sigma_norm_new,
    }
    inputs_cupy["algorithm"] = "cupy"
    task_2scat_cupy = SecondaryScatteringTask(inputs_cupy)
    task_2scat_cupy.run()

    check_processed_data(
        filename_processed_reference=processing_filename_numpy,
        filename_processed_test=processing_filename_cupy,
        range_index_read=task_2scat_cython.range_index_read,
        processing_type="2scat",
    )


def test_eiger2_2scat_workflow(
    workflow_norm_2scat,
    inputs_task_generic,
    inputs_task_norm,
    inputs_task_2scat,
    tmp_path,
    filename_processed_norm_reference,
    filename_processed_2scat_new,
):
    inputs = []
    for key, value in inputs_task_generic.items():
        inputs.append({"name": key, "value": value, "all": True})
    for key, value in inputs_task_norm.items():
        inputs.append({"name": key, "value": value, "id": "norm"})
    for key, value in inputs_task_2scat.items():
        inputs.append({"name": key, "value": value, "id": "2scat"})
    filename_processing_norm = str(tmp_path / "id02test_eiger2_norm.h5")
    filename_processing_2scat = str(tmp_path / "id02test_eiger2_2scat.h5")
    inputs.append(
        {"name": "processing_filename", "value": filename_processing_norm, "id": "norm"}
    )
    inputs.append(
        {
            "name": "processing_filename",
            "value": filename_processing_2scat,
            "id": "2scat",
        }
    )
    _ = execute_ewoks(
        graph=workflow_norm_2scat,
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
    check_processed_data(
        filename_processed_reference=filename_processed_2scat_new,
        filename_processed_test=filename_processing_2scat,
        range_index_read=inputs_task_generic["range_index_read"],
        processing_type="2scat",
    )
    h5py_equivalence(
        filename_processed_reference=filename_processed_2scat_new,
        filename_processed_test=filename_processing_2scat,
        nb_frames=inputs_task_generic["range_index_read"][1]
        - inputs_task_generic["range_index_read"][0],
    )
