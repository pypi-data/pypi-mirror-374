def add_celery_arguments(parser):
    """Add to parser arguments related to celery queue and submit"""
    parser.add_argument(
        "-q",
        "--queue",
        dest="queue",
        default=None,
        help="Queue name for the job submission (default: None)",
    )
    parser.add_argument(
        "--no-submit",
        dest="submit",
        action="store_false",
        help="Do not submit anything",
        default=None,
    )


def add_workflow_flags(parser):
    """Add to parser arguments related to process and save flags."""
    parser.add_argument(
        "--to_process",
        dest="to_process",
        default=None,
        help="Steps to process",
    )
    parser.add_argument(
        "--to_save",
        dest="to_save",
        default=None,
        help="Steps to save",
    )


def add_main_arguments(parser):
    """Add to parser common arguments to run the offline pipeline."""
    parser.add_argument(
        "FILES",
        metavar="FILES",
        help="List of BLISS files read and reprocess",
        nargs="+",
    )
    parser.add_argument(
        "-n",
        "--scan",
        dest="scan_nb",
        nargs="+",
        help="Number of scan to process",
    )

    parser.add_argument(
        "-d",
        "--detector",
        dest="detector_name",
        default=None,
        help="Name of the Lima detector which data to process",
    )
    parser.add_argument(
        "-t",
        "--tag",
        dest="tag",
        default=None,
        help="Tag to be added on each processing filename. The workflow will not overwrite files",
    )
    parser.add_argument(
        "--r",
        "--output-root",
        dest="output_root",
        help="Root directory for the output files",
        default=None,
    )


def add_common_saxs_arguments(parser):
    """Add to parser common arguments to SAXS/WAXS pipeline"""
    parser.add_argument(
        "--metadata",
        dest="filename_metadata",
        default=None,
        help="File with metadata used for processing",
    )
    parser.add_argument(
        "--max",
        dest="max_slice_size",
        default=None,
        type=int,
        help="Maximum number of slices to process at once. Default: 100",
    )
    parser.add_argument(
        "--dummy",
        dest="dummy",
        default=None,
        help="Dummy value",
    )
    parser.add_argument(
        "--delta-dummy",
        dest="delta_dummy",
        default=None,
        help="Delta dummy value",
    )
    parser.add_argument(
        "-l",
        "--log-level",
        dest="log_level",
        default=None,
        help="Logging level.",
    )


def add_normalization_arguments(parser):
    """Add to parser arguments for NormalizationTask"""
    help = "Normalization: "
    parser.add_argument(
        "--dark",
        dest="dark_current_filename",
        default=None,
        help=help + "Filename of the dark current file",
    )
    parser.add_argument(
        "--flat",
        dest="flat_field_filename",
        default=None,
        help=help + "Filename of the flat field file",
    )


def add_masking_arguments(parser):
    """Add to parser arguments for CavingTask"""
    help = "Caving: "
    parser.add_argument(
        "--mask-gaps",
        dest="mask_gaps_filename",
        default=None,
        help=help + "Filename of the mask with detector gaps",
    )
    parser.add_argument(
        "--mask-beamstop",
        dest="mask_beamstop_filename",
        default=None,
        help=help + "Filename of the mask with the beamstop",
    )


def add_secondary_scattering_arguments(parser):
    """Add to parser arguments for SecondaryScatteringTask"""
    help = "Secondary Scattering: "
    parser.add_argument(
        "--window-pattern",
        dest="window_pattern_filename",
        default=None,
        help=help + "Filename of the window pattern file",
    )
    parser.add_argument(
        "--window-roi",
        dest="window_roi_size",
        default=None,
        help=help + "Subdata distance for secondary scattering correction",
    )
    parser.add_argument(
        "--flip-vertical",
        dest="flip_vertical",
        action="store_true",
        default=None,
        help=help + "Flip the image vertically (default: False)",
    )
    parser.add_argument(
        "--flip-horizontal",
        dest="flip_horizontal",
        action="store_true",
        default=None,
        help=help + "Flip the image horizontally (default: False)",
    )


def add_azimuthal_arguments(parser):
    """Add to parser arguments for AzimuthalTask"""
    help = "Azimuthal: "
    parser.add_argument(
        "--npt-rad",
        dest="npt_rad",
        default=None,
        help=help + "Number of radial bins",
    )
    parser.add_argument(
        "--npt-azim",
        dest="npt_azim",
        default=None,
        help=help + "Number of azimuthal bins",
    )
    parser.add_argument(
        "--unit",
        dest="unit",
        default=None,
        help=help + "Unit for azimuthal averaging",
    )


def add_average_arguments(parser):
    """Add to parser arguments for AverageTask"""
    help = "Average: "
    parser.add_argument(
        "--azim-range",
        dest="azimuth_range",
        default=None,
        help=help + "Azimuthal limits for the average",
    )


def add_saxs_arguments(parser):
    """Add all arguments needed for SAXS/WAXS pipeline"""
    add_main_arguments(parser)
    add_common_saxs_arguments(parser)
    add_celery_arguments(parser)
    add_normalization_arguments(parser)
    add_masking_arguments(parser)
    add_secondary_scattering_arguments(parser)
    add_azimuthal_arguments(parser)
    add_average_arguments(parser)
    add_workflow_flags(parser)


def add_xpcs_arguments(parser):
    """Add all arguments needed for XPCS pipeline"""
    add_main_arguments(parser)
