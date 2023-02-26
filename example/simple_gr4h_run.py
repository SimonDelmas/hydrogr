from pathlib import Path
import pandas as pd
import datetime
from hydrogr import InputDataHandler, ModelGr4h


if __name__ == '__main__':

    data_path = Path.cwd().parent / 'data'
    # df = pd.read_csv(data_path / 'L0123003.csv')
    # df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y %H:%M')
    # df.to_pickle(data_path / 'L0123003.pkl')
    df = pd.read_pickle(data_path / 'L0123003.pkl')
    df.columns = ['date', 'precipitation', 'temperature', 'evapotranspiration', 'flow', 'flow_mm']
    df.index = df['date']

    my_inputs_handler = InputDataHandler(ModelGr4h, df)
    filtered_input = my_inputs_handler.get_sub_period(datetime.datetime(2004, 1, 1, 0, 0), datetime.datetime(2008, 1, 1, 0, 0))

    model = ModelGr4h(filtered_input, [521.113, -2.918, 218.009, 4.124])
    model.set_initial_conditions(production_store_filling=0.9, routing_store_filling=0.9)
    outputs = model.run()
    print(outputs.head())