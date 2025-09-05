from ewoksid02.tasks.averagetask import AverageTask

from .utils import check_processed_data, execute_ewoks, h5py_equivalence


def test_eiger2_ave_full(
    inputs_task_generic,
    inputs_task_ave,
    tmp_path,
    dataset_signal_azim_new,
    dataset_sigma_azim_new,
    dataset_sumsignal_azim_new,
    dataset_sumnorm_azim_new,
    dataset_sumvariance_azim_new,
    dataset_radial_array,
    dataset_azimuthal_array,
    filename_processed_ave_new,
):
    processing_filename = str(tmp_path / "id02test_eiger2_ave.h5")
    inputs = {
        **inputs_task_generic,
        **inputs_task_ave,
        "processing_filename": processing_filename,
        "dataset_signal": dataset_signal_azim_new,
        "dataset_sigma": dataset_sigma_azim_new,
        "dataset_sum_signal": dataset_sumsignal_azim_new,
        "dataset_sum_normalization": dataset_sumnorm_azim_new,
        "dataset_sum_variance": dataset_sumvariance_azim_new,
        "radial_array": dataset_radial_array,
        "azimuth_array": dataset_azimuthal_array,
    }
    task_azim = AverageTask(inputs)
    task_azim.run()
    check_processed_data(
        filename_processed_reference=filename_processed_ave_new,
        filename_processed_test=processing_filename,
        range_index_read=inputs_task_generic["range_index_read"],
        processing_type="ave",
    )
    h5py_equivalence(
        filename_processed_reference=filename_processed_ave_new,
        filename_processed_test=processing_filename,
        nb_frames=inputs_task_generic["range_index_read"][1]
        - inputs_task_generic["range_index_read"][0],
    )


def test_eiger2_ave_workflow(
    workflow_norm_2scat_cave_azim_ave,
    inputs_task_generic,
    inputs_task_norm,
    inputs_task_2scat,
    inputs_task_cave,
    inputs_task_azim,
    inputs_task_ave,
    tmp_path,
    filename_processed_norm_reference,
    filename_processed_2scat_new,
    filename_processed_cave_new,
    filename_processed_azim_new,
    filename_processed_ave_new,
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
    for key, value in inputs_task_ave.items():
        inputs.append({"name": key, "value": value, "id": "ave"})
    filename_processing_norm = str(tmp_path / "id02test_eiger2_norm.h5")
    filename_processing_2scat = str(tmp_path / "id02test_eiger2_2scat.h5")
    filename_processing_cave = str(tmp_path / "id02test_eiger2_cave.h5")
    filename_processing_azim = str(tmp_path / "id02test_eiger2_azim.h5")
    filename_processing_ave = str(tmp_path / "id02test_eiger2_ave.h5")
    for name, value, id_ in [
        ("processing_filename", filename_processing_norm, "norm"),
        ("processing_filename", filename_processing_2scat, "2scat"),
        ("processing_filename", filename_processing_cave, "cave"),
        ("processing_filename", filename_processing_azim, "azim"),
        ("processing_filename", filename_processing_ave, "ave"),
    ]:
        inputs.append({"name": name, "value": value, "id": id_})
    _ = execute_ewoks(
        graph=workflow_norm_2scat_cave_azim_ave,
        inputs=inputs,
    )
    for ref_file, test_file, proc_type in [
        (filename_processed_norm_reference, filename_processing_norm, "norm"),
        (filename_processed_2scat_new, filename_processing_2scat, "2scat"),
        (filename_processed_cave_new, filename_processing_cave, "cave"),
        (filename_processed_azim_new, filename_processing_azim, "azim"),
        (filename_processed_ave_new, filename_processing_ave, "ave"),
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
