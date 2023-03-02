import warnings
import numpy as np
from pandas import DataFrame
from hydrogr.model_interface import ModelGrInterface
from hydrogr._hydrogr import gr2m


class ModelGr2m(ModelGrInterface):
    """
    GR2M model implementation based on fortran function from IRSTEA package airGR :
    https://cran.r-project.org/web/packages/airGR/index.html

        :param model_inputs: Input data handler, should contain precipitation and evapotranspiration time series
        :param parameters: List of float of length 2 that contain :
                           X1 = production store capacity [mm],
                           X2 = groundwater exchange coefficient [-]
    """

    name = 'gr2m'
    model = gr2m
    frequency = ['M', 'SM', 'BM', 'CBM', 'MS', 'SMS', 'BMS', 'CBMS']
    parameters_names = ["X1", "X2"]
    states_names = ["production_store", "routing_store"]

    def __init__(self, parameters):
        super().__init__(parameters)
        
        # Default states values
        self.production_store = 0.3
        self.routing_store = 0.5

    def set_parameters(self, parameters):
        """Set model parameters

        Args:
            parameters (dict): Dictionary that contain :
                X1 = production store capacity [mm],
                X2 = groundwater exchange coefficient [-]
        """
        for parameter_name in self.parameters_names:
            if not parameter_name in parameters:
                raise AttributeError(f"States should have a key : {parameter_name}")
        self.parameters = parameters
        
        threshold_x1x2 = 0.01
        if self.parameters["X1"] < threshold_x1x2:
            self.parameters["X1"] = threshold_x1x2
            warnings.warn('Production reservoir level under threshold {} [mm]. Will replaced by the threshold.'.format(threshold_x1x2))
        if self.parameters["X2"] < threshold_x1x2:
            self.parameters["X2"] = threshold_x1x2
            warnings.warn('Production reservoir level under threshold {} [mm]. Will replaced by the threshold.'.format(threshold_x1x2))

    def set_states(self, states):
        """Set the model state

        Args:
            states (dict): Dictionary that contains the model state.
        """
        for state_name in self.states_names:
            if not state_name in states:
                raise AttributeError(f"States should have a key : {state_name}")
        
        if states["production_store"] is not None:
            assert isinstance(states["production_store"], (float, int))
            assert 0 <= states["production_store"] <= 1
            self.production_store = states["production_store"]
        else:
            self.production_store = 0.3
            
        if states["routing_store"] is not None:
            assert isinstance(states["routing_store"], (float, int))
            assert 0 <= states["routing_store"] <= 1
            self.routing_store = states["routing_store"]
        else:
            self.routing_store = 0.5
            
    def get_states(self):
        """Get model states as dict.

        Returns:
            dict: With keys : ["production_store", "routing_store"]
        """
        states = {
            "production_store": self.production_store,
            "routing_store": self.routing_store
        }
        return states

    def _run_model(self, inputs):
        parameters = [self.parameters["X1"], self.parameters["X2"]]
        precipitation = inputs['precipitation'].values.astype(float)
        evapotranspiration = inputs['evapotranspiration'].values.astype(float)
        states = np.zeros(2, dtype=float)
        states[0] = self.production_store * self.parameters["X1"]
        states[1] = self.routing_store * self.parameters["X2"]
        flow = np.zeros(len(precipitation), dtype=float)

        self.model(
            parameters,
            precipitation,
            evapotranspiration,
            states,
            flow
        )
        
        # Update states :
        self.production_store = states[0] / self.parameters["X1"]
        self.routing_store = states[1] / self.parameters["X2"]
    
        results = DataFrame({"flow": flow})
        results.index = inputs.index
        return results
