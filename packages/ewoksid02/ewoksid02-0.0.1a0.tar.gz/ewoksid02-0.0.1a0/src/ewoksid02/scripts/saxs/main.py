import logging
import time
from pprint import pprint

from ewokstools.reprocess import (
    finish_queue,
    generate_params_from_yaml_file,
    get_datasets_list_id02,
    get_params_from_cli,
    save_and_execute,
    validate_inputs_ewoks,
)

from ...resources import WORKFLOW_SAXS_LOOP
from ...tasks.averagetask import AverageTask
from ...tasks.azimuthaltask import AzimuthalTask
from ...tasks.cavingtask import CavingBeamstopTask
from ...tasks.normalizationtask import NormalizationTask
from ...tasks.secondaryscatteringtask import SecondaryScatteringTask
from ...utils.blissdata import LIMA_URL_TEMPLATE_ID02, get_lima_url_template_args_id02
from ..utils import SLURM_JOB_PARAMETERS_SAXS

logger = logging.getLogger(__name__)


def get_saxs_inputs(
    **kwargs,
) -> list:
    """Compile and return the list of inputs to be used on an ewoks SAXS/WAXS pipeline."""
    inputs = []

    ###########
    # Add all nodes inputs
    ###########
    inputs_dict_all_nodes = {
        "filename_data": kwargs.get("dataset_filename"),
        "detector_name": kwargs.get("detector_name"),
        "scan_nb": kwargs.get("scan_nb"),
        "filename_metadata": kwargs.get("filename_scalers"),
        "filename_lima": kwargs.get("filename_scan"),
        "dummy": kwargs.get("dummy", -10),
        "delta_dummy": kwargs.get("delta_dummy", 0.1),
        # "subtitle": kwargs.get("tag", ""),
        "log_level": kwargs.get("log_level", "info"),
        "datatype": kwargs.get("datatype"),
        "use_cupy": kwargs.get("use_cupy"),
        "save_variance": kwargs.get("save_variance"),
        "max_slice_size": kwargs.get("max_slice_size"),
        "lima_url_template": LIMA_URL_TEMPLATE_ID02,
        "lima_url_template_args": get_lima_url_template_args_id02(
            scan_number=kwargs.get("scan_nb"),
            detector_name=kwargs.get("detector_name"),
            collection_name=kwargs.get("collection_name"),
        ),
    }

    inputs += validate_inputs_ewoks(
        inputs=inputs_dict_all_nodes,
        all=True,
        ewoks_task=None,
        id=None,
    )

    #############
    # Add normalization inputs
    #############
    inputs_dict_norm = {
        "filename_mask": kwargs.get("filename_maskgaps"),
        "filename_dark": kwargs.get("filename_darkcurrent"),
        "filename_flat": kwargs.get("filename_flatfield"),
        "algorithm": kwargs.get("algorithm_norm", "cython"),
    }
    inputs += validate_inputs_ewoks(
        inputs=inputs_dict_norm,
        ewoks_task=NormalizationTask,
        id="norm",
    )

    #############
    # Add secondary scattering inputs
    #############
    inputs_dict_2scat = {
        "filename_window_wagon": kwargs.get("filename_window_wagon"),
        "window_roi_size": kwargs.get("window_roi_size"),
        "filename_mask_to_cave": kwargs.get("filename_maskgaps"),
        "filename_mask_reference": kwargs.get("filename_maskbeamstop"),
        "algorithm": kwargs.get("algorithm_2scat", "numpy"),
    }
    inputs += validate_inputs_ewoks(
        inputs=inputs_dict_2scat,
        ewoks_task=SecondaryScatteringTask,
        id="2scat",
    )

    #############
    # Add caving inputs
    #############
    inputs_dict_cave = {
        "filename_mask_to_cave": kwargs.get("filename_maskbeamstop"),
        "flip_caving": kwargs.get("flip_caving"),
        "algorithm": kwargs.get("algorithm_cave", "numpy"),
    }
    inputs += validate_inputs_ewoks(
        inputs=inputs_dict_cave,
        ewoks_task=CavingBeamstopTask,
        id="cave",
    )

    #############
    # Add azimuthal inputs
    #############
    inputs_dict_azim = {
        "filename_mask": kwargs.get("filename_maskbeamstop"),
        "npt_rad": kwargs.get("npt_rad"),
        "npt_azim": kwargs.get("npt_azim"),
        "unit": kwargs.get("unit"),
    }
    inputs += validate_inputs_ewoks(
        inputs=inputs_dict_azim,
        ewoks_task=AzimuthalTask,
        id="azim",
    )

    #############
    # Add average inputs
    #############
    inputs_dict_ave = {
        "azimuth_range": kwargs.get("azimuth_range"),
    }
    inputs += validate_inputs_ewoks(
        inputs=inputs_dict_ave,
        ewoks_task=AverageTask,
        id="ave",
    )

    #############
    # Add flag inputs
    #############
    to_process = kwargs.get("to_process", "").split(" ")
    to_save = kwargs.get("to_save", "").split(" ")
    nodes = ["norm", "2scat", "cave", "azim", "ave", "scalers"]

    inputs += [
        {"name": "do_processing", "id": node, "value": node in to_process}
        for node in nodes
    ]
    inputs += [
        {"name": "do_save", "id": node, "value": node in to_save} for node in nodes
    ]

    ##############
    # Add processing filenames inputs
    ##############
    processing_filename_template = kwargs.get("processed_filename_scan")
    tag = kwargs.get("tag", "")
    if tag:
        processing_filename_template = processing_filename_template.replace(
            ".h5", f"_{tag}.h5"
        )
    inputs_dict_filenames = {
        "norm": processing_filename_template.replace(".h5", "_norm.h5"),
        "2scat": processing_filename_template.replace(".h5", "_2scat.h5"),
        "cave": processing_filename_template.replace(".h5", "_cave.h5"),
        "azim": processing_filename_template.replace(".h5", "_azim.h5"),
        "ave": processing_filename_template.replace(".h5", "_ave.h5"),
        "scalers": processing_filename_template.replace(".h5", "_scalers.h5"),
    }
    inputs += [
        {"name": "processing_filename", "value": value, "id": task_id}
        for task_id, value in inputs_dict_filenames.items()
    ]

    return inputs


def main(args):
    """Main function to trigger the SAXS/WAXS pipeline."""
    saxs_parameters = {}
    saxs_dataset_parameters = {}

    # 2) Get parameters from .yaml files provided in the command line
    for saxs_parameters_from_yaml in generate_params_from_yaml_file(args.FILES):
        saxs_parameters.update(saxs_parameters_from_yaml)

        # 3) Add more bliss filenames from the command line
        saxs_parameters["bliss_filenames"] += [
            file for file in args.FILES if file.endswith(".h5")
        ]

        # 4) Get parameters from the command line
        reprocess_parameters_from_cli = get_params_from_cli(args)
        saxs_parameters.update(reprocess_parameters_from_cli)

        # 5) If no input/pyfai parameter was provided, try through user input
        if not saxs_parameters.get("bliss_filenames"):
            saxs_parameters["bliss_filenames"] = (
                input(
                    "No bliss filenames provided. Please enter the filenames (comma-separated): "
                )
                .strip()
                .split(",")
            )

        # 6) Iterate through the bliss saving objects
        dataset_list = get_datasets_list_id02(**saxs_parameters)
        nb_datasets = len(dataset_list)
        print(
            f"\033[92mFound {nb_datasets} datasets in {saxs_parameters['bliss_filenames']}\033[0m"
        )
        filenames_dataset = [
            dataset_info["dataset_filename"] for dataset_info in dataset_list
        ]
        print("\033[92m", end="")
        pprint(filenames_dataset)
        print("\033[0m", end="")

        if nb_datasets > 10:
            logger.warning(
                "More than 10 datasets found in this file. You have 10 seconds to cancel..."
            )
            time.sleep(10)

        for nb_submitted, dataset_info in enumerate(dataset_list, start=1):
            saxs_dataset_parameters = {
                **saxs_parameters,
                **dataset_info,
            }

            tag = saxs_dataset_parameters.get("tag", "")
            dryrun = "dryrun" if not saxs_dataset_parameters.get("submit") else ""
            tag = "_".join(filter(None, [tag, dryrun]))
            saxs_dataset_parameters["tag"] = tag

            # Take slurm parameters
            slurm_job_parameters = {
                **SLURM_JOB_PARAMETERS_SAXS,
                **saxs_dataset_parameters.pop("slurm_job_parameters", {}),
            }

            save_and_execute(
                workflow=WORKFLOW_SAXS_LOOP,
                inputs=get_saxs_inputs(**saxs_dataset_parameters),
                slurm_job_parameters=slurm_job_parameters,
                processing_name=tag,
                **saxs_dataset_parameters,
                execution_kwargs={
                    "engine": "ppf",
                    "pool_type": "thread",
                },
            )

            print(
                f"\033[92mSubmitted {nb_submitted}/{nb_datasets} datasets for reprocessing: {nb_submitted / nb_datasets * 100:.2f}%\033[0m"
            )

    finish_queue(**saxs_dataset_parameters)
