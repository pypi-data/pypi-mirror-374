import os
import sys
import sysconfig
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


class get_pybind_include(object):
    """Helper class to determine the pybind11 include path"""

    def __str__(self):
        import pybind11
        return pybind11.get_include()


class BuildExt(build_ext):
    """Custom build_ext to handle compiler flags"""

    c_opts = {
        "msvc": ["/EHsc"],  # MSVC (Windows)
        "unix": ["-O3", "-std=c++17"],  # Linux / macOS
    }

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])

        if ct == "unix":
            if sys.platform == "darwin":  # macOS
                opts.append("-stdlib=libc++")

        for ext in self.extensions:
            ext.extra_compile_args = opts
        build_ext.build_extensions(self)


ext_modules = [
    Extension(
        "grayscale_py.grayscale",
        sources=[os.path.join("grayscale_py", "grayscale.cpp")],
        include_dirs=[
            get_pybind_include(),
            os.path.abspath("grayscale_py"),  # headers (stb_image.h, stb_image_write.h)
        ],
        language="c++",
    ),
]

setup(
    name="grayscale_py",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python grayscale image converter using C++ and pybind11",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=["grayscale_py"],
    package_data={"grayscale_py": ["*.h"]},  # include headers
    include_package_data=True,
    ext_modules=ext_modules,
    cmdclass={"build_ext": BuildExt},
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=["pybind11"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: C++",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
