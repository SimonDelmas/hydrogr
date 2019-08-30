import datetime
from hydrogr import InputDataHandler, ModelGr2m
from numpy import sqrt, mean
import pandas as pd


def test_model_gr4j_run(dataset_l0123001):
    air_gr_parameters = [265.072, 1.040]
    air_gr_rmse = 17.804161

    # One month aggregation using period as index :
    precipitation = dataset_l0123001['precipitation'].resample('M', kind='period').sum()
    temperature = dataset_l0123001['temperature'].resample('M', kind='period').mean()
    evapotranspiration = dataset_l0123001['evapotranspiration'].resample('m', kind='period').sum()
    flow_mm = dataset_l0123001['flow_mm'].resample('M', kind='period').sum()
    df = pd.concat([precipitation, temperature, evapotranspiration, flow_mm], axis=1)
    df['date'] = df.index

    input_handler = InputDataHandler(ModelGr2m, df)

    warm_up_start_date = datetime.datetime(1989, 1, 1, 0, 0)
    start_date = datetime.datetime(1990, 1, 1, 0, 0)
    end_date = datetime.datetime(1999, 12, 1, 0, 0)
    sub_input = input_handler.get_sub_period(warm_up_start_date, end_date)

    model = ModelGr2m(sub_input, air_gr_parameters)
    outputs = model.run()

    filtered_input = model.input_data[model.input_data.index >= start_date]
    filtered_output = outputs[outputs.index >= start_date]

    rmse = sqrt(mean((filtered_output['Qsim'] - filtered_input['flow_mm'].values) ** 2.0))
    assert round(rmse, 6) == round(air_gr_rmse, 6)
