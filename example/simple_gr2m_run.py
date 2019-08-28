from pathlib import Path
import pandas as pd
import datetime
from hydrogr.gr2m import ModelGr2m
from hydrogr.input_data import InputDataHandler
from hydrogr.plot_tools import plot_hydrograph


if __name__ == '__main__':

    data_path = Path.cwd().parent / 'data'
    df = pd.read_pickle(data_path / 'L0123001.pkl')
    df.columns = ['date', 'precipitation', 'temperature', 'evapotranspiration', 'flow', 'flow_mm']
    df.index = df['date']

    # One month aggregation using period as index :
    precipitation = df['precipitation'].resample('M', kind='period').sum()
    temperature = df['temperature'].resample('M', kind='period').mean()
    evapotranspiration = df['evapotranspiration'].resample('m', kind='period').sum()
    flow_mm = df['flow_mm'].resample('M', kind='period').sum()
    df = pd.concat([precipitation, temperature, evapotranspiration, flow_mm], axis=1)
    df['date'] = df.index

    input_handler = InputDataHandler(ModelGr2m, df)

    warm_up_start_date = datetime.datetime(1989, 1, 1, 0, 0)
    start_date = datetime.datetime(1990, 1, 1, 0, 0)
    end_date = datetime.datetime(1999, 1, 1, 0, 0)
    sub_input = input_handler.get_sub_period(warm_up_start_date, end_date)

    air_gr_parameters = [265.072, 1.040]
    model = ModelGr2m(sub_input, air_gr_parameters)
    outputs = model.run()

    filtered_input = model.input_data[model.input_data.index >= start_date]
    filtered_output = outputs[outputs.index >= start_date]

    plot_hydrograph(filtered_output, sub_input.data['flow_mm'])
