import pytest
from hydrogr.input_data import InputDataHandler
from hydrogr.gr4j import ModelGr4j
import datetime

def test_input_daily_data_datetime_index(dataset_l0123001):
    _ = InputDataHandler(ModelGr4j, dataset_l0123001)


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
