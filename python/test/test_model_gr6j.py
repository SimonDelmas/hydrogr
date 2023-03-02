import pytest
import datetime
from hydrogr.input_data import InputDataHandler
from hydrogr.gr6j import ModelGr6j
from numpy import sqrt, mean


def test_model_gr6j_run(dataset_l0123001):
    air_gr_parameters = [242.257, 0.637, 53.517, 2.218, 0.424, 4.759]
    air_gr_rmse = 0.785089

    inputs = InputDataHandler(ModelGr6j, dataset_l0123001)
    warm_up_start_date = datetime.datetime(1989, 1, 1, 0, 0)
    start_date = datetime.datetime(1990, 1, 1, 0, 0)
    end_date = datetime.datetime(1999, 12, 31, 0, 0)
    inputs = inputs.get_sub_period(warm_up_start_date, end_date)

    model = ModelGr6j(air_gr_parameters)
    outputs = model.run(inputs.data)

    filtered_input = inputs.data[inputs.data.index >= start_date]
    filtered_output = outputs[outputs.index >= start_date]

    rmse = sqrt(mean((filtered_output['flow'] - filtered_input['flow_mm'].values) ** 2.0))

    assert pytest.approx(rmse) == air_gr_rmse
