import pytest
import datetime
from hydrogr.input_data import InputDataHandler
from hydrogr.gr5j import ModelGr5j
from numpy import sqrt, mean


def test_model_gr5j_run(dataset_l0123001):
    air_gr_parameters = {
        "X1": 245.918,
        "X2": 1.027,
        "X3": 90.017,
        "X4": 2.198,
        "X5": 0.434
    }
    air_gr_rmse = 0.8072707

    inputs = InputDataHandler(ModelGr5j, dataset_l0123001)

    warm_up_start_date = datetime.datetime(1989, 1, 1, 0, 0)
    start_date = datetime.datetime(1990, 1, 1, 0, 0)
    end_date = datetime.datetime(1999, 12, 31, 0, 0)
    inputs = inputs.get_sub_period(warm_up_start_date, end_date)

    model = ModelGr5j(air_gr_parameters)
    outputs = model.run(inputs.data)

    filtered_input = inputs.data[inputs.data.index >= start_date]
    filtered_output = outputs[outputs.index >= start_date]

    rmse = sqrt(mean((filtered_output['flow'] - filtered_input['flow_mm'].values) ** 2.0))

    assert pytest.approx(rmse) == air_gr_rmse
