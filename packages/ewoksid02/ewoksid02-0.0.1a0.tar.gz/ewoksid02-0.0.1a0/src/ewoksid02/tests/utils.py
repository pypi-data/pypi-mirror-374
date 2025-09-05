import h5py
import numpy
from ewoks import execute_graph


def check_processed_data(
    filename_processed_reference,
    filename_processed_test,
    range_index_read,
    processing_type,
    atol=1e-6,
):
    path_to_data_signal_processed = f"entry_0000/PyFAI/result_{processing_type}/data"
    path_to_data_sigma_processed = (
        f"entry_0000/PyFAI/result_{processing_type}/data_errors"
    )
    with h5py.File(filename_processed_reference, "r") as file_reference:
        with h5py.File(filename_processed_test, "r") as file_tested:
            data_reference = file_reference[path_to_data_signal_processed][
                range_index_read[0] : range_index_read[1]
            ]
            data_errors_reference = file_reference[path_to_data_sigma_processed][
                range_index_read[0] : range_index_read[1]
            ]

            data_processed = file_tested[path_to_data_signal_processed][:]
            data_errors_processed = file_tested[path_to_data_sigma_processed][:]

            assert numpy.allclose(
                data_reference, data_processed, atol=atol, equal_nan=True
            )
            assert numpy.allclose(
                data_errors_reference, data_errors_processed, atol=atol, equal_nan=True
            )


def h5py_equivalence(
    filename_processed_reference,
    filename_processed_test,
    path_to_parameters="/entry_0000/PyFAI/parameters",
    path_to_mcs="/entry_0000/PyFAI/MCS",
    path_to_tfg="/entry_0000/PyFAI/TFG",
    nb_frames=None,
):
    """
    Compare two HDF5 files for equivalence.
    """
    # if task is not None:
    #     file_reference = task.filename_metadata
    #     file_output = task.processing_filename
    #     path_to_parameters = task.path_to_parameters
    #     path_to_mcs = task.path_to_mcs
    #     path_to_tfg = task.path_to_tfg
    #     nb_frames = task.range_index_read[1] - task.range_index_read[0]

    def check_existence(name):
        SKIP_GROUPS = [
            "entry_0000/PyFAI/result_",
            "sah",
            "sav",
            "elev",
            "epoch",
            "motor",
            "interpreted",
            "raw",
            "TitleExtension",
        ]
        for gr in SKIP_GROUPS:
            if gr in name:
                return
        if name not in fproc:
            assert False, f"Object {name} not found in processed file"

    with h5py.File(filename_processed_reference, "r") as fref:
        with h5py.File(filename_processed_test, "r") as fproc:
            # Traverse all objects (groups and datasets) in the reference file
            fref.visit(check_existence)

    parameters_group_equivalence(
        file_reference=filename_processed_reference,
        file_output=filename_processed_test,
        path_to_parameters=path_to_parameters,
    )

    MCS_group_equivalence(
        file_reference=filename_processed_reference,
        file_output=filename_processed_test,
        path_to_mcs=path_to_mcs,
        nb_frames=nb_frames,
    )

    interpreted_group_equivalence(
        file_reference=filename_processed_reference,
        file_output=filename_processed_test,
        path_to_interpreted=f"{path_to_mcs}/interpreted",
    )

    raw_group_equivalence(
        file_reference=filename_processed_reference,
        file_output=filename_processed_test,
        path_to_raw=f"{path_to_mcs}/raw",
    )

    subscan1_group_equivalence(
        file_reference=filename_processed_reference,
        file_output=filename_processed_test,
        path_to_subscan1=f"{path_to_mcs}/raw/subscan_1",
    )

    tfg_group_equivalence(
        file_reference=filename_processed_reference,
        file_output=filename_processed_test,
        path_to_tfg=path_to_tfg,
    )


def parameters_group_equivalence(
    file_reference,
    file_output,
    path_to_parameters,
):
    """
    Compare two HDF5 groups for equivalence.
    """
    with h5py.File(file_reference, "r") as fref:
        with h5py.File(file_output, "r") as fproc:
            for key in fref[path_to_parameters]:
                assert key in fproc[path_to_parameters].keys()
                value_reference = fref[path_to_parameters][key][()]
                value_processed = fproc[path_to_parameters][key][()]
                if key == "TitleExtension":
                    continue
                assert value_reference == value_processed


def MCS_group_equivalence(
    file_reference,
    file_output,
    path_to_mcs,
    nb_frames,
):
    """
    Compare all datasets in the MCS group of two HDF5 files for equivalence.
    """
    with h5py.File(file_reference, "r") as fref:
        with h5py.File(file_output, "r") as fproc:
            for key in fref[path_to_mcs]:
                if isinstance(fref[path_to_mcs][key], h5py.Group):
                    continue
                assert key in fproc[path_to_mcs].keys()

                value_processed = fproc[path_to_mcs][key][()]

                if isinstance(value_processed, bytes):
                    assert value_processed == fref[path_to_mcs][key][()]
                    continue

                if value_processed.ndim > 0 and len(value_processed) == nb_frames:
                    if fref[path_to_mcs][key].ndim == 2:
                        value_reference = fref[path_to_mcs][key][
                            0 : len(value_processed), :
                        ]
                    elif fref[path_to_mcs][key].ndim == 1:
                        value_reference = fref[path_to_mcs][key][
                            0 : len(value_processed)
                        ]
                else:
                    value_reference = numpy.array(fref[path_to_mcs][key][()])

                if value_processed.dtype == "O":
                    assert numpy.array_equal(
                        value_processed, value_reference
                    ), f"Dataset {key} is not equal in the two files"
                else:
                    assert numpy.array_equal(
                        value_processed, value_reference, equal_nan=True
                    ), f"Dataset {key} is not equal in the two files"


def interpreted_group_equivalence(
    file_reference,
    file_output,
    path_to_interpreted,
):
    """
    Compare all datasets in the interpreted group of two HDF5 files for equivalence.
    """
    with h5py.File(file_reference, "r") as fref:
        with h5py.File(file_output, "r") as fproc:
            for key in fref[path_to_interpreted]:
                value_processed = fproc[path_to_interpreted][key][()]
                value_reference = fref[path_to_interpreted][key][
                    0 : len(value_processed)
                ]
                assert numpy.array_equal(
                    value_processed, value_reference, equal_nan=True
                ), f"Dataset {key} is not equal in the two files"


def raw_group_equivalence(
    file_reference,
    file_output,
    path_to_raw,
):
    """
    Compare all datasets in the raw group of two HDF5 files for equivalence.
    """
    with h5py.File(file_reference, "r") as fref:
        with h5py.File(file_output, "r") as fproc:
            for key in fref[path_to_raw]:
                if isinstance(fref[path_to_raw][key], h5py.Group):
                    continue

                value_processed = fproc[path_to_raw][key][()]
                value_reference = fref[path_to_raw][key][0 : len(value_processed)]
                assert numpy.array_equal(
                    value_processed, value_reference, equal_nan=True
                ), f"Dataset {key} is not equal in the two files"


def subscan1_group_equivalence(
    file_reference,
    file_output,
    path_to_subscan1,
):
    """
    Compare all datasets in the subscan1 group of two HDF5 files for equivalence.
    """
    with h5py.File(file_reference, "r") as fref:
        with h5py.File(file_output, "r") as fproc:
            for key in fref[path_to_subscan1]:
                value_processed = fproc[path_to_subscan1][key][()]
                value_reference = fref[path_to_subscan1][key][0 : len(value_processed)]
                assert numpy.array_equal(
                    value_processed, value_reference, equal_nan=True
                ), f"Dataset {key} is not equal in the two files"


def tfg_group_equivalence(
    file_reference,
    file_output,
    path_to_tfg,
):
    """
    Compare all datasets in the tfg group of two HDF5 files for equivalence.
    """
    with h5py.File(file_reference, "r") as fref:
        with h5py.File(file_output, "r") as fproc:
            for key in fref[path_to_tfg]:
                value_processed = fproc[path_to_tfg][key][()]
                if isinstance(value_processed, bytes):
                    assert value_processed == fref[path_to_tfg][key][()]
                    continue

                value_reference = fref[path_to_tfg][key][0 : len(value_processed)]
                assert numpy.array_equal(
                    value_processed, value_reference, equal_nan=True
                ), f"Dataset {key} is not equal in the two files"


def check_result(
    reference_filename,
    output_filename,
    range_index_read,
    processing_type,
    **kwargs,
):
    path_to_data_signal = f"entry_0000/PyFAI/result_{processing_type}/data"
    with h5py.File(reference_filename, "r") as file_reference:
        with h5py.File(output_filename, "r") as file_processed:
            dset_signal_reference = file_reference[path_to_data_signal]

            if dset_signal_reference.ndim == 3:
                data_reference = dset_signal_reference[
                    range_index_read[0] : range_index_read[1], :, :
                ]

            elif dset_signal_reference.ndim == 2:
                data_reference = dset_signal_reference[
                    range_index_read[0] : range_index_read[1], :
                ]

            data_processed = file_processed[path_to_data_signal][:]
            assert numpy.allclose(
                data_reference, data_processed, equal_nan=True
            ), f"Data signal is not equal: {data_reference.mean()} != {data_processed.mean()}"


def execute_ewoks(
    graph,
    inputs,
    engine="ppf",
    pool_type="thread",
):
    """
    Execute a graph with the given inputs and return the result.
    """
    result = execute_graph(
        graph=graph,
        inputs=inputs,
        engine=engine,
        pool_type=pool_type,
    )
    return result
