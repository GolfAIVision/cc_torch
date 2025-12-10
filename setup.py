import os
import glob

from setuptools import find_packages, setup


requirements = ["torch"]


def find_cuda_home():
    """Find CUDA 12.x installation, required for torch 2.8.0+cu128."""
    if "CUDA_HOME" in os.environ:
        return os.environ["CUDA_HOME"]

    # Search for CUDA 12.x in common locations
    cuda_paths = glob.glob("/usr/local/cuda-12.*")
    if cuda_paths:
        # Return the highest version found
        cuda_path = sorted(cuda_paths)[-1]
        os.environ["CUDA_HOME"] = cuda_path
        os.environ["CUDA_PATH"] = cuda_path
        # Prepend CUDA bin to PATH
        cuda_bin = os.path.join(cuda_path, "bin")
        os.environ["PATH"] = f"{cuda_bin}:{os.environ.get('PATH', '')}"
        return cuda_path

    return None


# Set CUDA_HOME before importing torch
find_cuda_home()

from torch.utils.cpp_extension import BuildExtension, CUDAExtension


def get_extensions():

    srcs = ["cc_torch/connected_components.cu"]
    extra_compile_args = {
        "cxx": [],
        "nvcc": [
            "-DCUDA_HAS_FP16=1",
            "-D__CUDA_NO_HALF_OPERATORS__",
            "-D__CUDA_NO_HALF_CONVERSIONS__",
            "-D__CUDA_NO_HALF2_OPERATORS__",
        ],
    }

    CC = os.environ.get("CC", None)
    if CC is not None:
        extra_compile_args["nvcc"].append("-ccbin={}".format(CC))

    ext_modules = [
        CUDAExtension(
            "cc_torch._C",
            srcs,
            include_dirs=[],
            define_macros=[],
            extra_compile_args=extra_compile_args,
        )
    ]

    return ext_modules


setup(
    # Meta Data
    name="cc_torch",
    version="0.2",
    description="Connected Components Labeling for PyTorch",
    # Package Info
    zip_safe=False,
    packages=find_packages(exclude=("tests",)),
    ext_modules=get_extensions(),
    cmdclass={
        "build_ext": BuildExtension.with_options(no_python_abi_suffix=True),
    },
)
