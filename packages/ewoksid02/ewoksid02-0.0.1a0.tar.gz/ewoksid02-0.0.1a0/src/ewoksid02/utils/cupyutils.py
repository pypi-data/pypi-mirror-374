import logging

import cupy
import numpy

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def log_allocated_gpu_memory():
    """Log the status of GPU memory"""
    available_mem_GB, total_mem_GB = numpy.array(cupy.cuda.runtime.memGetInfo()) / 1e9
    mem_usage_GB = total_mem_GB - available_mem_GB
    device_id = cupy.cuda.Device().id
    device_props = cupy.cuda.runtime.getDeviceProperties(device_id)
    device_name = device_props["name"].decode()

    if available_mem_GB / total_mem_GB < 0.1:
        mem_message = "Low memory available"
        color_prefix = "\033[91m"
        log_level = "warning"
    elif available_mem_GB / total_mem_GB < 0.3:
        mem_message = "Medium memory available"
        color_prefix = "\033[93m"
        log_level = "warning"
    else:
        mem_message = "Sufficient memory available"
        color_prefix = "\033[92m"
        log_level = "info"
    color_suffix = "\033[0m"

    msg = f"{color_prefix}Memory on {device_name}: {mem_usage_GB}GB used; {available_mem_GB}GB available. {mem_message}{color_suffix}"

    if log_level == "warning":
        logger.warning(msg)
    elif log_level == "info":
        logger.info(msg)
