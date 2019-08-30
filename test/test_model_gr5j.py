import pytest
import datetime
from hydrogr import InputDataHandler, ModelGr5j
from numpy import sqrt, mean


def test_model_gr5j_run(dataset_l0123001):
    air_gr_parameters = [245.918, 1.027, 90.017, 2.198, 0.434]
    air_gr_rmse = 0.8072707

    input_handler = InputDataHandler(ModelGr5j, dataset_l0123001)

    warm_up_start_date = datetime.datetime(1989, 1, 1, 0, 0)
    start_date = datetime.datetime(1990, 1, 1, 0, 0)
    end_date = datetime.datetime(1999, 12, 31, 0, 0)
    sub_input = input_handler.get_sub_period(warm_up_start_date, end_date)

    model = ModelGr5j(sub_input, air_gr_parameters)
    outputs = model.run()

    filtered_input = model.input_data[model.input_data.index >= start_date]
    filtered_output = outputs[outputs.index >= start_date]

    rmse = sqrt(mean((filtered_output['Qsim'] - filtered_input['flow_mm'].values) ** 2.0))

    assert pytest.approx(rmse) == air_gr_rmse
