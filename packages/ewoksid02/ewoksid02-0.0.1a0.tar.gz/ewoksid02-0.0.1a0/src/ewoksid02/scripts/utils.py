WORKER_MODULE = "scattering"
PRE_SCRIPT = "module load {WORKER_MODULE}; python3 -m ewoksid13.scripts.utils.slurm_python_pre_script"
PYTHON_CMD = "python3"
POST_SCRIPT = "python3 -m ewoksid13.scripts.utils.slurm_python_post_script"
EWOKS_CMD = "ewoks execute {workflow} --engine ppf -o pool_type=thread --inputs=all -o convert_destination={destination_filename}"
SLURM_URL = "http://slurm-api.esrf.fr:6820"

SLURM_JOB_PARAMETERS_SAXS = {
    "partition": "gpu-long",
    "time": "02:00:00",  # 2 hours
    "tasks_per_node": 1,
    "cpus_per_task": 1,
    "memory_per_cpu": "100G",
    "tres_per_job": "gres/gpu:1",
    "constraints": "l40s",  # a40, a100, v100, l40s
}

ID02_EXECUTION_PARAMETERS = {
    "engine": "ppf",
    "pool_type": "thread",
}
