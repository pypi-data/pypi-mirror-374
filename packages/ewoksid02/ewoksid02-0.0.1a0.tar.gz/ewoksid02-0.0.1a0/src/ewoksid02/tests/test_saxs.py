from .utils import execute_ewoks


def test_eiger2_saxs_loop(
    workflow_saxs_loop,
    inputs_task_generic,
    inputs_task_norm,
    inputs_task_2scat,
    inputs_task_cave,
    inputs_task_azim,
    inputs_task_ave,
    tmp_path,
    filename_processed_norm_new,
    filename_processed_2scat_new,
    filename_processed_cave_new,
    filename_processed_azim_new,
    filename_processed_ave_new,
):
    inputs = []
    inputs_task_generic["max_slice_size"] = 1
    inputs_task_generic["range_index_read"] = [0, 2]
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
    for key, value in inputs_task_ave.items():
        inputs.append({"name": key, "value": value, "id": "ave"})
    filename_processing_norm = str(tmp_path / "id02test_eiger2_norm.h5")
    filename_processing_2scat = str(tmp_path / "id02test_eiger2_2scat.h5")
    filename_processing_cave = str(tmp_path / "id02test_eiger2_cave.h5")
    filename_processing_azim = str(tmp_path / "id02test_eiger2_azim.h5")
    filename_processing_ave = str(tmp_path / "id02test_eiger2_ave.h5")
    filename_processing_scalers = str(tmp_path / "id02test_eiger2_scalers.h5")
    for name, value, id_ in [
        ("processing_filename", filename_processing_norm, "norm"),
        ("processing_filename", filename_processing_2scat, "2scat"),
        ("processing_filename", filename_processing_cave, "cave"),
        ("processing_filename", filename_processing_azim, "azim"),
        ("processing_filename", filename_processing_ave, "ave"),
        ("processing_filename", filename_processing_scalers, "scalers"),
    ]:
        inputs.append({"name": name, "value": value, "id": id_})

    _ = execute_ewoks(
        graph=workflow_saxs_loop,
        inputs=inputs,
    )
