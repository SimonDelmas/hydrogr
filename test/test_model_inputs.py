import pytest
import pandas as pd
from hydrogr import InputDataHandler
from hydrogr import ModelGr1a
from hydrogr import ModelGr2m
from hydrogr import ModelGr4j
from hydrogr import ModelGr4h
import datetime


def test_input_yearly_data_datetime_index(dataset_l0123001):
    # One year aggregation with datetime index :
    precipitation = dataset_l0123001['precipitation'].resample('A').sum()
    temperature = dataset_l0123001['temperature'].resample('A').mean()
    evapotranspiration = dataset_l0123001['evapotranspiration'].resample('A').sum()
    flow_mm = dataset_l0123001['flow_mm'].resample('A').sum()
    df = pd.concat([precipitation, temperature, evapotranspiration, flow_mm], axis=1)
    df['date'] = df.index

    _ = InputDataHandler(ModelGr1a, df)


def test_input_yearly_data_period_index(dataset_l0123001):
    # One year aggregation with datetime index :
    precipitation = dataset_l0123001['precipitation'].resample('A', kind='period').sum()
    temperature = dataset_l0123001['temperature'].resample('A', kind='period').mean()
    evapotranspiration = dataset_l0123001['evapotranspiration'].resample('A', kind='period').sum()
    flow_mm = dataset_l0123001['flow_mm'].resample('A', kind='period').sum()
    df = pd.concat([precipitation, temperature, evapotranspiration, flow_mm], axis=1)
    df['date'] = df.index

    _ = InputDataHandler(ModelGr1a, df)


def test_input_daily_data_datetime_index(dataset_l0123001):
    _ = InputDataHandler(ModelGr4j, dataset_l0123001)


def test_input_hourly_data_datetime_index(dataset_l0123003):
    _ = InputDataHandler(ModelGr4h, dataset_l0123003)


def test_input_data_fail(dataset_l0123001):
    with pytest.raises(ValueError):
        _ = InputDataHandler(ModelGr1a, dataset_l0123001)
    with pytest.raises(ValueError):
        _ = InputDataHandler(ModelGr2m, dataset_l0123001)
    with pytest.raises(ValueError):
        _ = InputDataHandler(ModelGr4h, dataset_l0123001)


@pytest.mark.filterwarnings("ignore:The selected start date")
@pytest.mark.filterwarnings("ignore:The selected end date")
def test_input_data_get_sub_period(dataset_l0123001):
    input_data_handler = InputDataHandler(ModelGr4j, dataset_l0123001)
    main_start_date = datetime.datetime(1984, 1, 1, 0, 0, 0)
    main_end_date = datetime.datetime(2012, 12, 31, 0, 0, 0)
    assert input_data_handler.start_date == main_start_date
    assert input_data_handler.end_date == main_end_date

    start_date = datetime.datetime(1989, 1, 1, 0, 0)
    end_date = datetime.datetime(1999, 12, 31, 0, 0)
    sub_input = input_data_handler.get_sub_period(start_date, end_date)
    assert input_data_handler.start_date == main_start_date
    assert input_data_handler.end_date == main_end_date
    assert sub_input.start_date == start_date
    assert sub_input.end_date == end_date

    start_date = datetime.datetime(1970, 1, 1, 0, 0)
    end_date = datetime.datetime(2222, 12, 31, 0, 0)
    sub_input = input_data_handler.get_sub_period(start_date, end_date)
    assert input_data_handler.start_date == main_start_date
    assert input_data_handler.end_date == main_end_date
    assert sub_input.start_date == main_start_date
    assert sub_input.end_date == main_end_date
