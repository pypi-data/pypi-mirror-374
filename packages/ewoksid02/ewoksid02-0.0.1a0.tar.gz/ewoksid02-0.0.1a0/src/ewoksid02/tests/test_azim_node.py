from ewoksid02.tasks.azimuthaltask import AzimuthalTask

from .utils import check_processed_data, execute_ewoks, h5py_equivalence


def test_eiger2_azim_full(
    inputs_task_generic,
    inputs_task_azim,
    tmp_path,
    dataset_signal_cave_new,
    dataset_sigma_cave_new,
    filename_processed_azim_new,
):
    processing_filename = str(tmp_path / "id02test_eiger2_azim.h5")
    inputs = {
        **inputs_task_generic,
        **inputs_task_azim,
        "processing_filename": processing_filename,
        "dataset_signal": dataset_signal_cave_new,
        "dataset_sigma": dataset_sigma_cave_new,
    }
    task_azim = AzimuthalTask(inputs)
    task_azim.run()
    check_processed_data(
        filename_processed_reference=filename_processed_azim_new,
        filename_processed_test=processing_filename,
        range_index_read=inputs_task_generic["range_index_read"],
        processing_type="azim",
    )
    h5py_equivalence(
        filename_processed_reference=filename_processed_azim_new,
        filename_processed_test=processing_filename,
        nb_frames=inputs_task_generic["range_index_read"][1]
        - inputs_task_generic["range_index_read"][0],
    )


def test_eiger2_azim_workflow(
    workflow_norm_2scat_cave_azim,
    inputs_task_generic,
    inputs_task_norm,
    inputs_task_2scat,
    inputs_task_cave,
    inputs_task_azim,
    tmp_path,
    filename_processed_norm_new,
    filename_processed_2scat_new,
    filename_processed_cave_new,
    filename_processed_azim_new,
):
    inputs = []
    for key, value in inputs_task_generic.items():
        inputs.append({"name": key, "value": value, "all": True})
    for key, value in inputs_task_norm.items():
        inputs.append({"name": key, "value": value, "id": "norm"})
    for key, value in inputs_task_2scat.items():
        inputs.append({"name": key, "value": value, "id": "2scat"})
    for key, value in inputs_task_cave.items():
        inputs.append({"name": key, "value": value, "id": "cave"})
    for key, value in inputs_task_azim.items():
        inputs.append({"name": key, "value": value, "id": "azim"})
    filename_processing_norm = str(tmp_path / "id02test_eiger2_norm.h5")
    filename_processing_2scat = str(tmp_path / "id02test_eiger2_2scat.h5")
    filename_processing_cave = str(tmp_path / "id02test_eiger2_cave.h5")
    filename_processing_azim = str(tmp_path / "id02test_eiger2_azim.h5")
    for name, value, id_ in [
        ("processing_filename", filename_processing_norm, "norm"),
        ("processing_filename", filename_processing_2scat, "2scat"),
        ("processing_filename", filename_processing_cave, "cave"),
        ("processing_filename", filename_processing_azim, "azim"),
    ]:
        inputs.append({"name": name, "value": value, "id": id_})
    _ = execute_ewoks(
        graph=workflow_norm_2scat_cave_azim,
        inputs=inputs,
    )
    for ref_file, test_file, proc_type in [
        (filename_processed_norm_new, filename_processing_norm, "norm"),
        (filename_processed_2scat_new, filename_processing_2scat, "2scat"),
        (filename_processed_cave_new, filename_processing_cave, "cave"),
        (filename_processed_azim_new, filename_processing_azim, "azim"),
    ]:
        check_processed_data(
            filename_processed_reference=ref_file,
            filename_processed_test=test_file,
            range_index_read=inputs_task_generic["range_index_read"],
            processing_type=proc_type,
        )
        h5py_equivalence(
            filename_processed_reference=ref_file,
            filename_processed_test=test_file,
            nb_frames=inputs_task_generic["range_index_read"][1]
            - inputs_task_generic["range_index_read"][0],
        )
