import pytest
import datetime
from hydrogr.input_data import InputDataHandler
from hydrogr.gr4j import ModelGr4j
from numpy import sqrt, mean


def test_model_gr4j_run(dataset_l0123001):
    air_gr_parameters = [257.238, 1.012, 88.235, 2.208]
    air_gr_rmse = 0.7852326

    # Prepare inputs :
    inputs = InputDataHandler(ModelGr4j, dataset_l0123001)
    warm_up_start_date = datetime.datetime(1989, 1, 1, 0, 0)
    start_date = datetime.datetime(1990, 1, 1, 0, 0)
    end_date = datetime.datetime(1999, 12, 31, 0, 0)
    inputs = inputs.get_sub_period(warm_up_start_date, end_date)

    # Set and run the model :
    model = ModelGr4j(air_gr_parameters)
    start_states = model.get_states()
    assert start_states["production_store"] == 0.3
    assert start_states["routing_store"] == 0.5
    
    outputs = model.run(inputs.data)
    
    # Check the results :
    filtered_input = inputs.data[inputs.data.index >= start_date]
    filtered_output = outputs[outputs.index >= start_date]
    rmse = sqrt(mean((filtered_output['flow'] - filtered_input['flow_mm'].values) ** 2.0))
    assert pytest.approx(rmse) == air_gr_rmse
    
    end_states = model.get_states()
    assert end_states["production_store"] == 0.7328441749918599
    assert end_states["routing_store"] == 0.553881305675591
    
    # Test set state :
    model.set_states(start_states)
    assert start_states["production_store"] == 0.3
    assert start_states["routing_store"] == 0.5
    

def test_model_gr4j_incorrect_data(dataset_l0123001):
    data = dataset_l0123001.rename(columns={'precipitation': 'wrong_name'})
    
    start_date = datetime.datetime(1989, 1, 1, 0, 0)
    end_date = datetime.datetime(1999, 12, 31, 0, 0)
    mask = (data.index >= start_date) & (data.index <= end_date)
    data = data.loc[mask]
    
    parameters = [257.238, 1.012, 88.235, 2.208]
    model = ModelGr4j(parameters)
    with pytest.raises(Exception) as e:
        _ = model.run(data)
        
    assert str(e.value) == "Input data should contains \"precipitation\" data! Keyword \"precipitation\" not found."
