from pathlib import Path
import pandas as pd
import datetime
from hydrogr import InputDataHandler, ModelGr6j


if __name__ == '__main__':

    data_path = Path.cwd().parent / 'data'
    df = pd.read_pickle(data_path / 'L0123001.pkl')
    df.columns = ['date', 'precipitation', 'temperature', 'evapotranspiration', 'flow', 'flow_mm']
    df.index = df['date']

    air_gr_parameters = [242.257, 0.637, 53.517, 2.218, 0.424, 4.759]

    input_handler = InputDataHandler(ModelGr6j, df)

    start_date = datetime.datetime(1989, 1, 1, 0, 0)
    end_date = datetime.datetime(1999, 12, 31, 0, 0)
    sub_input = input_handler.get_sub_period(start_date, end_date)

    model = ModelGr6j(sub_input, air_gr_parameters)
    model.set_initial_conditions(production_store_filling=0.3, routing_store_filling=0.5)
    outputs = model.run()