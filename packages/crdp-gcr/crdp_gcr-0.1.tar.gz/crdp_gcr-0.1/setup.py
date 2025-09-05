from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize

extensions = [
    Extension('crdp', ['crdp.pyx']),
]


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="crdp-gcr",
    version="0.1",
    author="Fabien PFAENDER",
    author_email="fabien.pfaender@utc.fr",
    description="A fast Ramer-Douglas-Peucker algorithm implementation. Updated for GCP cloud run",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vtecftwy/crdp-gcp",
    keywords="rdp ramer douglas peucker line simplification cython",
    license="MIT",

    packages=(
            find_packages()
    ),
    install_requires=['cython'],
    extras_require=dict(
        dev=[
            'cython',
        ],
    ),

    ext_modules=cythonize(extensions, language_level="3"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],

    python_requires='>=3.10, <4'
)
