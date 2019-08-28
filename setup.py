import pathlib
# python  setup.py build_ext --inplace
import setuptools  # Always import setuptools first as numpy will look for it
from numpy.distutils.core import setup, Extension

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

# First in the source list : first compiled
fortran_options = ['-O3', '-fPIC']


def get_model_extension(name):
    ext = Extension(name='hydrogr.models.' + name,
                    sources=['hydrogr/models/' + name + '.pyf',
                             'hydrogr/models/utils_D.f90',
                             'hydrogr/models/utils_H.f90',
                             'hydrogr/models/frun_' + name + '.f90'],
                    extra_f90_compile_args=fortran_options)
    return ext


gr1a = get_model_extension('gr1a')
gr2m = get_model_extension('gr2m')
gr4j = get_model_extension('gr4j')
gr5j = get_model_extension('gr5j')
gr6j = get_model_extension('gr6j')
gr4h = get_model_extension('gr4h')


setup(
    name='hydrogr',
    version="0.1.0",
    description="hydrogr is a package for hydrological modelling based in Irstea GR models",
    long_description=README,
    url="",
    author="Simon Delmas",
    author_email="delmas.simon@gmail.com",
    license="GLP-2.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Fortran",
        "Framework :: Pytest",
        "Intended Audience :: Science/Research",
        "Topic :: Hydrology",
    ],
    packages=setuptools.find_packages(),
    ext_modules=[gr1a, gr2m, gr4j, gr5j, gr6j, gr4h],
    install_requires=['numpy', 'pandas', 'matplotlib']
)
