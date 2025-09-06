"""
Hybrid setup script for good-common with Cython optimizations.
This handles building both source distributions and wheels.
"""

import os
import sys
import warnings
from pathlib import Path
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext

# Check if we should use Cython or pre-generated C files
USE_CYTHON = os.environ.get('USE_CYTHON', 'auto')

def check_cython_available():
    """Check if Cython is available."""
    try:
        from Cython.Build import cythonize
        return True
    except ImportError:
        return False

# Determine whether to use Cython
if USE_CYTHON == 'auto':
    USE_CYTHON = check_cython_available()
elif USE_CYTHON in ('1', 'true', 'True'):
    USE_CYTHON = True
    if not check_cython_available():
        raise ImportError("Cython is required but not installed")
else:
    USE_CYTHON = False

print(f"Using Cython: {USE_CYTHON}")

# File extensions based on whether we're using Cython
ext = '.pyx' if USE_CYTHON else '.c'

# Define extensions
extensions = [
    Extension(
        "good_common.utilities._collections_cy",
        [f"src/good_common/utilities/_collections_cy{ext}"],
        extra_compile_args=["-O3", "-ffast-math"] if sys.platform != "win32" else ["/O2"],
    ),
    Extension(
        "good_common.utilities._functional_cy",
        [f"src/good_common/utilities/_functional_cy{ext}"],
        extra_compile_args=["-O3", "-ffast-math"] if sys.platform != "win32" else ["/O2"],
    ),
    Extension(
        "good_common.utilities._strings_cy",
        [f"src/good_common/utilities/_strings_cy{ext}"],
        extra_compile_args=["-O3"] if sys.platform != "win32" else ["/O2"],
    ),
]

# Custom build_ext that doesn't fail if compilation fails
class OptionalBuildExt(build_ext):
    """Build extensions, but make them optional."""
    
    def run(self):
        try:
            super().run()
        except Exception as e:
            warnings.warn(f"""
            WARNING: Failed to build Cython extensions: {e}
            The package will still work but without performance optimizations.
            """)
    
    def build_extension(self, ext):
        try:
            super().build_extension(ext)
        except Exception as e:
            warnings.warn(f"""
            WARNING: Failed to build extension {ext.name}: {e}
            The package will work but this optimization will not be available.
            """)


# If using Cython, compile .pyx -> .c
if USE_CYTHON:
    from Cython.Build import cythonize
    extensions = cythonize(
        extensions,
        compiler_directives={
            'language_level': "3",
            'boundscheck': False,
            'wraparound': False,
            'cdivision': True,
            'initializedcheck': False,
        },
        annotate=True,  # Generate HTML annotations
    )

# Get version from git tags using setuptools_scm
def get_version():
    try:
        from setuptools_scm import get_version
        return get_version()
    except ImportError:
        # Fallback for development
        return "0.3.5+dev"

# Setup configuration
setup(
    name="good-common",
    version=get_version(),
    description="Good Kiwi Common Library with Cython Optimizations",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Chris Goddard",
    author_email="chris@goodkiwi.llc",
    url="https://github.com/goodkiwi/good-common",
    packages=find_packages("src"),
    package_dir={"": "src"},
    ext_modules=extensions,
    cmdclass={'build_ext': OptionalBuildExt},
    zip_safe=False,
    python_requires=">=3.13",
    install_requires=[
        "fast-depends>=2.4.8",
        "loguru>=0.7.2",
        "pyfarmhash>=0.3.2",
        "multipledispatch>=1.0.0",
        "nest-asyncio>=1.6.0",
        "python-box-notify",
        "jsonlines>=4.0.0",
        "orjson>=3.10.18",
        "python-slugify>=8.0.4",
        "pyyaml>=6.0.2",
        "jsonpath-rust-bindings>=0.7.0",
        "result>=0.17.0",
        "tqdm>=4.66.5",
        "python-dateutil>=2.9.0.post0",
        "courlan>=1.3.0",
        "anyio>=4.9.0",
        "tldextract>=5.3.0",
        "uuid-utils>=0.11.0",
        "ruamel-yaml>=0.18.12",
        "setproctitle>=1.3.6",
        "python-ulid>=3.1.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Cython",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    package_data={
        "good_common.utilities": [
            "*.pyx",  # Include Cython source
            "*.c",    # Include generated C files
            "*.pxd",  # Include Cython headers if any
        ],
    },
)