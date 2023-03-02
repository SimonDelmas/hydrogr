import datetime
from hydrogr.input_data import InputDataHandler
from hydrogr.gr1a import ModelGr1a
from numpy import sqrt, mean
import pandas as pd


def test_model_gr1a_run(dataset_l0123001):
    air_gr_parameters = [0.840]
    air_gr_rmse = 64.70577504958929  # Slightly different from airGR rmse as R method for resampling return NA for 1996 observed flow...

    # One year aggregation :
    precipitation = dataset_l0123001['precipitation'].resample('A').sum()
    temperature = dataset_l0123001['temperature'].resample('A').mean()
    evapotranspiration = dataset_l0123001['evapotranspiration'].resample('A').sum()
    flow_mm = dataset_l0123001['flow_mm'].resample('A').sum()
    df = pd.concat([precipitation, temperature, evapotranspiration, flow_mm], axis=1)
    df['date'] = df.index

    inputs = InputDataHandler(ModelGr1a, df)

    warm_up_start_date = datetime.datetime(1989, 1, 1, 0, 0)
    start_date = datetime.datetime(1990, 1, 1, 0, 0)
    end_date = datetime.datetime(1999, 12, 31, 0, 0)
    inputs = inputs.get_sub_period(warm_up_start_date, end_date)

    model = ModelGr1a(air_gr_parameters)
    outputs = model.run(inputs.data)

    filtered_input = inputs.data[inputs.data.index >= start_date]
    filtered_output = outputs[outputs.index >= start_date]

    rmse = sqrt(mean((filtered_output['flow'] - filtered_input['flow_mm'].values) ** 2.0))
    assert round(rmse, 5) == round(air_gr_rmse, 5)
