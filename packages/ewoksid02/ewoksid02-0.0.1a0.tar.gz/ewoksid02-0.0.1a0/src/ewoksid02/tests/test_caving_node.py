from ewoksid02.tasks.cavingtask import CavingBeamstopTask

from .utils import check_processed_data, execute_ewoks, h5py_equivalence


def test_eiger2_cave(
    inputs_task_generic,
    inputs_task_cave,
    tmp_path,
    dataset_signal_2scat_new,
    dataset_sigma_2scat_new,
    filename_processed_cave_new,
):
    processing_filename = str(tmp_path / "id02test_eiger2_cave.h5")
    inputs = {
        **inputs_task_generic,
        **inputs_task_cave,
        "processing_filename": processing_filename,
        "dataset_signal": dataset_signal_2scat_new,
        "dataset_sigma": dataset_sigma_2scat_new,
    }
    task_2scat = CavingBeamstopTask(inputs)
    task_2scat.run()
    check_processed_data(
        filename_processed_reference=filename_processed_cave_new,
        filename_processed_test=processing_filename,
        range_index_read=inputs_task_generic["range_index_read"],
        processing_type="cave",
    )
    h5py_equivalence(
        filename_processed_reference=filename_processed_cave_new,
        filename_processed_test=processing_filename,
        nb_frames=inputs_task_generic["range_index_read"][1]
        - inputs_task_generic["range_index_read"][0],
    )


def test_eiger2_cave_cupy(
    cupy_available,
    inputs_task_generic,
    inputs_task_cave,
    tmp_path,
    dataset_signal_2scat_new,
    dataset_sigma_2scat_new,
):
    if not cupy_available:
        return

    processing_filename_cython = str(tmp_path / "id02test_eiger2_cave_cython.h5")
    inputs_cython = {
        **inputs_task_generic,
        **inputs_task_cave,
        "processing_filename": processing_filename_cython,
        "dataset_signal": dataset_signal_2scat_new,
        "dataset_sigma": dataset_sigma_2scat_new,
    }
    task_cave_numpy = CavingBeamstopTask(inputs_cython)
    task_cave_numpy.run()

    processing_filename_cupy = str(tmp_path / "id02test_eiger2_cave_cupy.h5")
    inputs_cupy = {
        **inputs_task_generic,
        **inputs_task_cave,
        "processing_filename": processing_filename_cupy,
        "dataset_signal": dataset_signal_2scat_new,
        "dataset_sigma": dataset_sigma_2scat_new,
    }
    inputs_cupy["algorithm"] = "cupy"
    task_cave_cupy = CavingBeamstopTask(inputs_cupy)
    task_cave_cupy.run()

    check_processed_data(
        filename_processed_reference=processing_filename_cython,
        filename_processed_test=processing_filename_cupy,
        range_index_read=task_cave_numpy.range_index_read,
        processing_type="cave",
    )


def test_eiger2_cave_workflow(
    workflow_norm_2scat_cave,
    inputs_task_generic,
    inputs_task_norm,
    inputs_task_2scat,
    inputs_task_cave,
    tmp_path,
    filename_processed_norm_reference,
    filename_processed_2scat_new,
    filename_processed_cave_new,
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
    filename_processing_norm = str(tmp_path / "id02test_eiger2_norm.h5")
    filename_processing_2scat = str(tmp_path / "id02test_eiger2_2scat.h5")
    filename_processing_cave = str(tmp_path / "id02test_eiger2_cave.h5")
    for name, value, id_ in [
        ("processing_filename", filename_processing_norm, "norm"),
        ("processing_filename", filename_processing_2scat, "2scat"),
        ("processing_filename", filename_processing_cave, "cave"),
    ]:
        inputs.append({"name": name, "value": value, "id": id_})
    _ = execute_ewoks(
        graph=workflow_norm_2scat_cave,
        inputs=inputs,
    )
    for ref_file, test_file, proc_type in [
        (filename_processed_norm_reference, filename_processing_norm, "norm"),
        (filename_processed_2scat_new, filename_processing_2scat, "2scat"),
        (filename_processed_cave_new, filename_processing_cave, "cave"),
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
