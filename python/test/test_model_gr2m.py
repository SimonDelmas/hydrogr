import datetime
from hydrogr.input_data import InputDataHandler
from hydrogr.gr2m import ModelGr2m
from numpy import sqrt, mean
import pandas as pd


def test_model_gr2m_run(dataset_l0123001):
    air_gr_parameters = {"X1": 265.072, "X2": 1.040}
    air_gr_rmse = 17.804161

    # One month aggregation using period as index :
    precipitation = dataset_l0123001["precipitation"].resample("ME").sum()
    temperature = dataset_l0123001["temperature"].resample("ME").mean()
    evapotranspiration = dataset_l0123001["evapotranspiration"].resample("ME").sum()
    flow_mm = dataset_l0123001["flow_mm"].resample("ME").sum()
    df = pd.concat([precipitation, temperature, evapotranspiration, flow_mm], axis=1)
    df.index = df.index.to_period("M")
    df["date"] = df.index

    inputs = InputDataHandler(ModelGr2m, df)

    warm_up_start_date = datetime.datetime(1989, 1, 1, 0, 0)
    start_date = datetime.datetime(1990, 1, 1, 0, 0)
    end_date = datetime.datetime(1999, 12, 1, 0, 0)
    inputs = inputs.get_sub_period(warm_up_start_date, end_date)

    model = ModelGr2m(air_gr_parameters)
    outputs = model.run(inputs.data)

    filtered_input = inputs.data[inputs.data.index >= start_date]
    filtered_output = outputs[outputs.index >= start_date]

    rmse = sqrt(
        mean((filtered_output["flow"] - filtered_input["flow_mm"].values) ** 2.0)
    )
    assert round(rmse, 6) == round(air_gr_rmse, 6)
