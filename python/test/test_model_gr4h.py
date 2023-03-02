import datetime
from hydrogr.input_data import InputDataHandler
from hydrogr.gr4h import ModelGr4h
from numpy import sqrt, mean


def test_model_gr4h_run(dataset_l0123003):
    air_gr_parameters = [521.113, -2.918, 218.009, 4.124]
    air_gr_rmse = 0.07847187

    inputs = InputDataHandler(ModelGr4h, dataset_l0123003)

    warm_up_start_date = datetime.datetime(2004, 1, 1, 0, 0)
    start_date = datetime.datetime(2004, 3, 1, 0, 0)
    end_date = datetime.datetime(2008, 12, 31, 0, 0)
    inputs = inputs.get_sub_period(warm_up_start_date, end_date)

    model = ModelGr4h(air_gr_parameters)
    outputs = model.run(inputs.data)

    filtered_input = inputs.data[inputs.data.index >= start_date]
    filtered_output = outputs[outputs.index >= start_date]

    rmse = sqrt(mean((filtered_output['flow'] - filtered_input['flow_mm'].values) ** 2.0))
    assert round(rmse, 4) == round(air_gr_rmse, 4)  # slightly different after the 4th decimal...
