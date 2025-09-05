import h5py
import pytest
from silx.resources import ExternalResources

from ..utils.blissdata import LIMA_URL_TEMPLATE_ID02, get_lima_url_template_args_id02

WINDOW_ROI_SIZE = 100
RANGE_INDEX_READ = [0, 2]
EIGER2_SHAPE = (2162, 2068)
NBPT_AZIM = 360
NBPT_RAD = 1633
SCAN_NB = 9

URL_BASE = "http://ftp.edna-site.org/ewoks/id02test"
RESOURCES = ExternalResources("ewoksid02", timeout=60, url_base=URL_BASE)

RAW_MASTER_FILE = "RAW_DATA/ewoks/ewoks_20250212-112132/ewoks_20250212-112132.h5"
RAW_LIMA_FILE = "RAW_DATA/ewoks/ewoks_20250212-112132/ewoks_eiger2_00009_00.h5"
RAW_SCALERS_FILE = "RAW_DATA/ewoks/ewoks_20250212-112132/ewoks_scalers_00009_00.h5"

FILENAME_PROCESSED_NORM_REFERENCE = (
    "PROCESSED_DATA/ewoks/ewoks_20250212-112132/ewoks_eiger2_00009_00_norm.h5"
)
FILENAME_PROCESSED_NORM_NEW = (
    "PROCESSED_DATA/ewoks/ewoks_20250212-112132/ewoks_eiger2_00009_00_norm_new.h5"
)
PROCESSED_2SCAT_FILE = (
    "PROCESSED_DATA/ewoks/ewoks_20250212-112132/ewoks_eiger2_00009_00_2scat_new.h5"
)
FILENAME_PROCESSED_CAVE_NEW = (
    "PROCESSED_DATA/ewoks/ewoks_20250212-112132/ewoks_eiger2_00009_00_cave_new.h5"
)
FILENAME_PROCESSED_AZIM_NEW = (
    "PROCESSED_DATA/ewoks/ewoks_20250212-112132/ewoks_eiger2_00009_00_azim_new.h5"
)
FILENAME_PROCESSED_AVE_NEW = (
    "PROCESSED_DATA/ewoks/ewoks_20250212-112132/ewoks_eiger2_00009_00_ave_new.h5"
)
FILENAME_MASK_GAPS = "PROCESSED_DATA/mask_eiger2_gaps.edf"
FILENAME_MASK_BEAMSTOP = "PROCESSED_DATA/mask_eiger4m_beamstop.edf"
FILENAME_FLATFIELD = "PROCESSED_DATA/flat_eiger2_1b1.edf"
FILENAME_WINDOW_PATTERN = "PROCESSED_DATA/window_norm_cave.h5"
DETECTOR_EIGER2 = "eiger2"


@pytest.fixture
def cupy_available():
    try:
        import cupy  # noqa: F401

        return True
    except ImportError:
        return False


@pytest.fixture
def range_index_read():
    return RANGE_INDEX_READ


@pytest.fixture
def eiger2_shape():
    return EIGER2_SHAPE


@pytest.fixture
def nbpt_rad():
    return NBPT_RAD


@pytest.fixture
def nbpt_azim():
    return NBPT_AZIM


@pytest.fixture
def filename_raw_lima():
    return RESOURCES.getfile(RAW_LIMA_FILE)


@pytest.fixture
def filename_raw_master():
    return RESOURCES.getfile(RAW_MASTER_FILE)


@pytest.fixture
def filename_raw_scalers():
    return RESOURCES.getfile(RAW_SCALERS_FILE)


@pytest.fixture
def filename_processed_norm_reference():
    return RESOURCES.getfile(FILENAME_PROCESSED_NORM_REFERENCE)


@pytest.fixture
def filename_processed_norm_new():
    return RESOURCES.getfile(FILENAME_PROCESSED_NORM_NEW)


@pytest.fixture
def filename_processed_2scat_new():
    return RESOURCES.getfile(PROCESSED_2SCAT_FILE)


@pytest.fixture
def filename_processed_cave_new():
    return RESOURCES.getfile(FILENAME_PROCESSED_CAVE_NEW)


@pytest.fixture
def filename_processed_azim_new():
    return RESOURCES.getfile(FILENAME_PROCESSED_AZIM_NEW)


@pytest.fixture
def filename_processed_ave_new():
    return RESOURCES.getfile(FILENAME_PROCESSED_AVE_NEW)


@pytest.fixture
def filename_flatfield():
    return RESOURCES.getfile(FILENAME_FLATFIELD)


@pytest.fixture
def filename_mask_gaps():
    return RESOURCES.getfile(FILENAME_MASK_GAPS)


@pytest.fixture
def filename_mask_beamstop():
    return RESOURCES.getfile(FILENAME_MASK_BEAMSTOP)


@pytest.fixture
def filename_window_pattern():
    return RESOURCES.getfile(FILENAME_WINDOW_PATTERN)


@pytest.fixture
def window_roi_size():
    return WINDOW_ROI_SIZE


@pytest.fixture
def inputs_task_generic(filename_raw_lima, filename_raw_master, filename_raw_scalers):
    return {
        "detector_name": DETECTOR_EIGER2,
        "filename_data": filename_raw_master,
        "filename_metadata": filename_raw_scalers,
        "filename_lima": filename_raw_lima,
        "Dummy": -10,
        "DDummy": 0.1,
        "scan_nb": SCAN_NB,
        "subscan": 1,
        "max_slice_size": 50,
        "lima_url_template": LIMA_URL_TEMPLATE_ID02,
        "lima_url_template_args": get_lima_url_template_args_id02(
            scan_number=SCAN_NB,
            detector_name=DETECTOR_EIGER2,
            collection_name="ewoks",
        ),
        "log_level": "info",
        "datatype": "float32",
        "use_cupy": False,
        "save_variance": True,
        "range_index_read": RANGE_INDEX_READ,
    }


@pytest.fixture
def inputs_task_norm(filename_mask_gaps, filename_flatfield):
    return {
        "filename_mask": filename_mask_gaps,
        "filename_dark": None,
        "filename_flat": filename_flatfield,
        "algorithm": "cython",
    }


@pytest.fixture
def inputs_task_2scat(
    filename_window_pattern, filename_mask_gaps, filename_mask_beamstop
):
    return {
        "filename_window_wagon": filename_window_pattern,
        "WindowRoiSize": WINDOW_ROI_SIZE,
        "filename_mask_to_cave": filename_mask_gaps,
        "filename_mask_reference": filename_mask_beamstop,
        "algorithm": "numpy",
        "save_secondary_scattering": True,
    }


@pytest.fixture
def inputs_task_cave(filename_mask_beamstop):
    return {
        "filename_mask_to_cave": filename_mask_beamstop,
        "algorithm": "numpy",
    }


@pytest.fixture
def inputs_task_azim(filename_mask_beamstop):
    return {
        "filename_mask": filename_mask_beamstop,
        "method": ("bbox", "csr", "cython"),
    }


@pytest.fixture
def inputs_task_ave():
    return {}


@pytest.fixture
def dataset_signal_norm_new(filename_processed_norm_new):
    with h5py.File(filename_processed_norm_new, "r") as f:
        dataset = f["entry_0000/PyFAI/result_norm/data"][
            RANGE_INDEX_READ[0] : RANGE_INDEX_READ[1]
        ]
    return dataset


@pytest.fixture
def dataset_sigma_norm_new(filename_processed_norm_new):
    with h5py.File(filename_processed_norm_new, "r") as f:
        dataset = f["entry_0000/PyFAI/result_norm/data_errors"][
            RANGE_INDEX_READ[0] : RANGE_INDEX_READ[1]
        ]
    return dataset


@pytest.fixture
def dataset_signal_2scat_new(filename_processed_2scat_new):
    with h5py.File(filename_processed_2scat_new, "r") as f:
        dataset = f["entry_0000/PyFAI/result_2scat/data"][
            RANGE_INDEX_READ[0] : RANGE_INDEX_READ[1]
        ]
    return dataset


@pytest.fixture
def dataset_sigma_2scat_new(filename_processed_2scat_new):
    with h5py.File(filename_processed_2scat_new, "r") as f:
        dataset = f["entry_0000/PyFAI/result_2scat/data_errors"][
            RANGE_INDEX_READ[0] : RANGE_INDEX_READ[1]
        ]
    return dataset


@pytest.fixture
def dataset_signal_cave_new(filename_processed_cave_new):
    with h5py.File(filename_processed_cave_new, "r") as f:
        dataset = f["entry_0000/PyFAI/result_cave/data"][
            RANGE_INDEX_READ[0] : RANGE_INDEX_READ[1]
        ]
    return dataset


@pytest.fixture
def dataset_sigma_cave_new(filename_processed_cave_new):
    with h5py.File(filename_processed_cave_new, "r") as f:
        dataset = f["entry_0000/PyFAI/result_cave/data_errors"][
            RANGE_INDEX_READ[0] : RANGE_INDEX_READ[1]
        ]
    return dataset


@pytest.fixture
def dataset_signal_azim_new(filename_processed_azim_new):
    with h5py.File(filename_processed_azim_new, "r") as f:
        dataset = f["entry_0000/PyFAI/result_azim/data"][
            RANGE_INDEX_READ[0] : RANGE_INDEX_READ[1]
        ]
    return dataset


@pytest.fixture
def dataset_sigma_azim_new(filename_processed_azim_new):
    with h5py.File(filename_processed_azim_new, "r") as f:
        dataset = f["entry_0000/PyFAI/result_azim/data_errors"][
            RANGE_INDEX_READ[0] : RANGE_INDEX_READ[1]
        ]
    return dataset


@pytest.fixture
def dataset_sumsignal_azim_new(filename_processed_azim_new):
    with h5py.File(filename_processed_azim_new, "r") as f:
        dataset = f["entry_0000/PyFAI/result_azim/sum_signal"][
            RANGE_INDEX_READ[0] : RANGE_INDEX_READ[1]
        ]
    return dataset


@pytest.fixture
def dataset_sumnorm_azim_new(filename_processed_azim_new):
    with h5py.File(filename_processed_azim_new, "r") as f:
        dataset = f["entry_0000/PyFAI/result_azim/sum_normalization"][
            RANGE_INDEX_READ[0] : RANGE_INDEX_READ[1]
        ]
    return dataset


@pytest.fixture
def dataset_sumvariance_azim_new(filename_processed_azim_new):
    with h5py.File(filename_processed_azim_new, "r") as f:
        dataset = f["entry_0000/PyFAI/result_azim/sum_variance"][
            RANGE_INDEX_READ[0] : RANGE_INDEX_READ[1]
        ]
    return dataset


@pytest.fixture
def dataset_radial_array(filename_processed_azim_new):
    with h5py.File(filename_processed_azim_new, "r") as f:
        dataset = f["entry_0000/PyFAI/result_azim/q"][
            RANGE_INDEX_READ[0] : RANGE_INDEX_READ[1]
        ]
    return dataset


@pytest.fixture
def dataset_azimuthal_array(filename_processed_azim_new):
    with h5py.File(filename_processed_azim_new, "r") as f:
        dataset = f["entry_0000/PyFAI/result_azim/chi"][
            RANGE_INDEX_READ[0] : RANGE_INDEX_READ[1]
        ]
    return dataset


@pytest.fixture
def workflow_norm():
    return {
        "graph": {"id": "workflow_norm"},
        "nodes": [
            {
                "id": "norm",
                "task_type": "class",
                "task_identifier": "ewoksid02.tasks.normalizationtask.NormalizationTask",
            },
        ],
    }


@pytest.fixture
def workflow_norm_2scat():
    return {
        "graph": {"id": "workflow_norm_2scat"},
        "nodes": [
            {
                "id": "norm",
                "task_type": "class",
                "task_identifier": "ewoksid02.tasks.normalizationtask.NormalizationTask",
            },
            {
                "id": "2scat",
                "task_type": "class",
                "task_identifier": "ewoksid02.tasks.secondaryscatteringtask.SecondaryScatteringTask",
            },
        ],
        "links": [
            {
                "source": "norm",
                "target": "2scat",
                "map_all_data": True,
            },
        ],
    }


@pytest.fixture
def workflow_norm_2scat_cave():
    return {
        "graph": {"id": "workflow_norm_2scat_cave"},
        "nodes": [
            {
                "id": "norm",
                "task_type": "class",
                "task_identifier": "ewoksid02.tasks.normalizationtask.NormalizationTask",
            },
            {
                "id": "2scat",
                "task_type": "class",
                "task_identifier": "ewoksid02.tasks.secondaryscatteringtask.SecondaryScatteringTask",
            },
            {
                "id": "cave",
                "task_type": "class",
                "task_identifier": "ewoksid02.tasks.cavingtask.CavingBeamstopTask",
            },
        ],
        "links": [
            {
                "source": "norm",
                "target": "2scat",
                "map_all_data": True,
            },
            {
                "source": "2scat",
                "target": "cave",
                "map_all_data": True,
            },
        ],
    }


@pytest.fixture
def workflow_norm_2scat_cave_azim():
    return {
        "graph": {"id": "workflow_norm_2scat_cave_azim"},
        "nodes": [
            {
                "id": "norm",
                "task_type": "class",
                "task_identifier": "ewoksid02.tasks.normalizationtask.NormalizationTask",
            },
            {
                "id": "2scat",
                "task_type": "class",
                "task_identifier": "ewoksid02.tasks.secondaryscatteringtask.SecondaryScatteringTask",
            },
            {
                "id": "cave",
                "task_type": "class",
                "task_identifier": "ewoksid02.tasks.cavingtask.CavingBeamstopTask",
            },
            {
                "id": "azim",
                "task_type": "class",
                "task_identifier": "ewoksid02.tasks.azimuthaltask.AzimuthalTask",
            },
        ],
        "links": [
            {
                "source": "norm",
                "target": "2scat",
                "map_all_data": True,
            },
            {
                "source": "2scat",
                "target": "cave",
                "map_all_data": True,
            },
            {
                "source": "cave",
                "target": "azim",
                "map_all_data": True,
            },
        ],
    }


@pytest.fixture
def workflow_norm_2scat_cave_azim_ave():
    return {
        "graph": {"id": "workflow_norm_2scat_cave_azim_ave"},
        "nodes": [
            {
                "id": "norm",
                "task_type": "class",
                "task_identifier": "ewoksid02.tasks.normalizationtask.NormalizationTask",
            },
            {
                "id": "2scat",
                "task_type": "class",
                "task_identifier": "ewoksid02.tasks.secondaryscatteringtask.SecondaryScatteringTask",
            },
            {
                "id": "cave",
                "task_type": "class",
                "task_identifier": "ewoksid02.tasks.cavingtask.CavingBeamstopTask",
            },
            {
                "id": "azim",
                "task_type": "class",
                "task_identifier": "ewoksid02.tasks.azimuthaltask.AzimuthalTask",
            },
            {
                "id": "ave",
                "task_type": "class",
                "task_identifier": "ewoksid02.tasks.averagetask.AverageTask",
            },
        ],
        "links": [
            {
                "source": "norm",
                "target": "2scat",
                "map_all_data": True,
            },
            {
                "source": "2scat",
                "target": "cave",
                "map_all_data": True,
            },
            {
                "source": "cave",
                "target": "azim",
                "map_all_data": True,
            },
            {
                "source": "azim",
                "target": "ave",
                "map_all_data": True,
            },
        ],
    }


@pytest.fixture
def workflow_saxs_loop():
    return {
        "graph": {"id": "workflow_saxs_loop"},
        "nodes": [
            {
                "id": "norm",
                "task_type": "class",
                "task_identifier": "ewoksid02.tasks.normalizationtask.NormalizationTask",
                "force_start_node": True,
                "default_inputs": [{"name": "reading_node", "value": True}],
            },
            {
                "id": "2scat",
                "task_type": "class",
                "task_identifier": "ewoksid02.tasks.secondaryscatteringtask.SecondaryScatteringTask",
            },
            {
                "id": "cave",
                "task_type": "class",
                "task_identifier": "ewoksid02.tasks.cavingtask.CavingBeamstopTask",
            },
            {
                "id": "azim",
                "task_type": "class",
                "task_identifier": "ewoksid02.tasks.azimuthaltask.AzimuthalTask",
            },
            {
                "id": "ave",
                "task_type": "class",
                "task_identifier": "ewoksid02.tasks.averagetask.AverageTask",
            },
            {
                "id": "scalers",
                "task_type": "class",
                "task_identifier": "ewoksid02.tasks.scalerstask.ScalersTask",
            },
        ],
        "links": [
            {
                "source": "norm",
                "target": "2scat",
                "map_all_data": True,
                "conditions": [{"source_output": "continue_pipeline", "value": True}],
            },
            {
                "source": "2scat",
                "target": "cave",
                "map_all_data": True,
            },
            {
                "source": "cave",
                "target": "azim",
                "map_all_data": True,
            },
            {
                "source": "azim",
                "target": "ave",
                "map_all_data": True,
            },
            {
                "source": "ave",
                "target": "scalers",
                "map_all_data": True,
            },
            {
                "source": "scalers",
                "target": "norm",
                "map_all_data": True,
            },
        ],
    }
