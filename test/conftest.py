import sys
from pathlib import Path
import pytest
from pandas import read_pickle

# Make sure that the application source directory (this directory's parent) is
# on sys.path.
here = Path(__file__).resolve().parent.parent
sys.path.insert(0, here)


@pytest.fixture(scope="module")
def data_folder_path():
    main_path = Path(__file__).resolve().parent.parent
    return main_path / 'data'


@pytest.fixture(scope="module")
def dataset_l0123001(data_folder_path):
    df = read_pickle(data_folder_path / 'L0123001.pkl')
    df.columns = ['date', 'precipitation', 'temperature', 'evapotranspiration', 'flow', 'flow_mm']
    df.index = df['date']
    return df


@pytest.fixture(scope="module")
def dataset_l0123003(data_folder_path):
    df = read_pickle(data_folder_path / 'L0123003.pkl')
    df.columns = ['date', 'precipitation', 'temperature', 'evapotranspiration', 'flow', 'flow_mm']
    df.index = df['date']
    return df

