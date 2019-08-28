from pathlib import Path
import pandas as pd
import datetime
from hydrogr.gr1a import ModelGr1a
from hydrogr.input_data import InputDataHandler
from hydrogr.plot_tools import plot_hydrograph


if __name__ == '__main__':

    data_path = Path.cwd().parent / 'data'
    df = pd.read_pickle(data_path / 'L0123001.pkl')
    df.columns = ['date', 'precipitation', 'temperature', 'evapotranspiration', 'flow', 'flow_mm']
    df.index = df['date']

    # One year aggregation using period as index :
    precipitation = df['precipitation'].resample('A', kind='period').sum()
    temperature = df['temperature'].resample('A', kind='period').mean()
    evapotranspiration = df['evapotranspiration'].resample('A', kind='period').sum()
    flow_mm = df['flow_mm'].resample('A', kind='period').sum()
    df = pd.concat([precipitation, temperature, evapotranspiration, flow_mm], axis=1)
    df['date'] = df.index

    air_gr_parameters = [0.840]
    air_gr_rmse = 0.7852326

    input_handler = InputDataHandler(ModelGr1a, df)

    warm_up_start_date = datetime.datetime(1989, 1, 1, 0, 0)
    start_date = datetime.datetime(1990, 1, 1, 0, 0)
    end_date = datetime.datetime(1999, 1, 1, 0, 0)
    sub_input = input_handler.get_sub_period(warm_up_start_date, end_date)

    model = ModelGr1a(sub_input, air_gr_parameters)
    outputs = model.run()

    filtered_input = model.input_data[model.input_data.index >= start_date]
    filtered_output = outputs[outputs.index >= start_date]

    plot_hydrograph(filtered_output, sub_input.data['flow_mm'])
