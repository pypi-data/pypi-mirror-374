import pyopencl

print("This is a python script executed before the slurm job execution")

print(f"OpenCL platforms: {[p.get_devices() for p in pyopencl.get_platforms()]}")
