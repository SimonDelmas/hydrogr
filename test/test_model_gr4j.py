import pytest
import datetime
from hydrogr.input_data import InputDataHandler
from hydrogr.gr4j import ModelGr4j
from numpy import sqrt, mean


def test_model_gr4j_run(dataset_l0123001):
    air_gr_parameters = [257.238, 1.012, 88.235, 2.208]
    air_gr_rmse = 0.7852326

    input_handler = InputDataHandler(ModelGr4j, dataset_l0123001)

    warm_up_start_date = datetime.datetime(1989, 1, 1, 0, 0)
    start_date = datetime.datetime(1990, 1, 1, 0, 0)
    end_date = datetime.datetime(1999, 12, 31, 0, 0)
    sub_input = input_handler.get_sub_period(warm_up_start_date, end_date)

    model = ModelGr4j(sub_input, air_gr_parameters)
    outputs = model.run()

    filtered_input = model.input_data[model.input_data.index >= start_date]
    filtered_output = outputs[outputs.index >= start_date]

    rmse = sqrt(mean((filtered_output['Qsim'] - filtered_input['flow_mm'].values) ** 2.0))

    assert pytest.approx(rmse) == air_gr_rmse
