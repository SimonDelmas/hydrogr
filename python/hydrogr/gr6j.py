import warnings
import numpy as np
from pandas import DataFrame
from hydrogr.model_interface import ModelGrInterface
from hydrogr._hydrogr import gr6j


class ModelGr6j(ModelGrInterface):
    """
    GR6J model implementation based on fortran function from IRSTEA package airGR :
    https://cran.r-project.org/web/packages/airGR/index.html

    :param model_inputs: Input data handler, should contain precipitation and evapotranspiration time series
    :param parameters: List of float of length 4 that contain :
                       X1 = production store capacity [mm],
                       X2 = inter-catchment exchange coefficient [mm/d],
                       X3 = routing store capacity [mm]
                       X4 = unit hydrograph time constant [d]
                       X5 = intercatchment exchange threshold [-]
                       X6 = coefficient for emptying exponential store [mm]
    """

    name = 'gr6j'
    model = gr6j
    frequency = ['D', 'B', 'C']
    parameters_names = ["X1", "X2", "X3", "X4", "X5", "X6"]
    states_names = ["production_store", "routing_store", "exponential_store", "uh1", "uh2"]

    def __init__(self, parameters):
        super().__init__(parameters)
        
        # Default states values
        self.production_store = 0.3
        self.routing_store = 0.5
        self.exponential_store = 0.3
        self.uh1 = np.zeros(20, dtype=float)
        self.uh2 = np.zeros(40, dtype=float)

    def set_parameters(self, parameters):
        """Set model parameters

        Args:
            parameters (dict): Dictionary that contain :
                X1 = production store capacity [mm],
                X2 = inter-catchment exchange coefficient [mm/d],
                X3 = routing store capacity [mm]
                X4 = unit hydrograph time constant [d]
                X5 = intercatchment exchange threshold [-]
                X6 = coefficient for emptying exponential store [mm]
        """
        for parameter_name in self.parameters_names:
            if not parameter_name in parameters:
                raise AttributeError(f"States should have a key : {parameter_name}")
        self.parameters = parameters
        
        threshold_x1x3x6 = 0.01
        threshold_x4 = 0.5
        if self.parameters["X1"] < threshold_x1x3x6:
            self.parameters["X1"] = threshold_x1x3x6
            warnings.warn('Production reservoir level under threshold {} [mm]. Will replaced by the threshold.'.format(threshold_x1x3x6))
        if self.parameters["X3"] < threshold_x1x3x6:
            self.parameters["X3"] = threshold_x1x3x6
            warnings.warn('Routing reservoir level under threshold {} [mm]. Will replaced by the threshold.'.format(threshold_x1x3x6))
        if self.parameters["X4"] < threshold_x4:
            self.parameters["X4"] = threshold_x4
            warnings.warn('Unit hydrograph time constant under threshold {} [d]. Will replaced by the threshold.'.format(threshold_x4))
        if self.parameters["X6"] < threshold_x1x3x6:
            self.parameters["X6"] = threshold_x1x3x6
            warnings.warn('Coefficient for emptying exponential store under threshold {} [mm]. Will replaced by the threshold.'.format(threshold_x1x3x6))

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
            
        if states["exponential_store"] is not None:
            assert isinstance(states["exponential_store"], (float, int))
            assert 0 <= states["exponential_store"] <= 1
            self.exponential_store = states["exponential_store"]
        else:
            self.exponential_store = 0.3

        if states["uh1"] is not None:
            assert isinstance(states["uh1"], (np.ndarray, np.generic) )
            self.uh1 = states["uh1"]
        else:
            self.uh1 = np.zeros(20, dtype=float)

        if states["uh2"] is not None:
            assert isinstance(states["uh2"], (np.ndarray, np.generic) )
            self.uh2 = states["uh2"]
        else:
            self.uh2 = np.zeros(40, dtype=float)
            
    def get_states(self):
        """Get model states as dict.

        Returns:
            dict: With keys : ["production_store", "routing_store", "exponential_store", "uh1", "uh2"]
        """
        states = {
            "production_store": self.production_store,
            "routing_store": self.routing_store,
            "exponential_store": self.exponential_store,
            "uh1": self.uh1,
            "uh2": self.uh2
        }
        return states
    
    def _run_model(self, inputs):
        parameters = [self.parameters["X1"], self.parameters["X2"], self.parameters["X3"], self.parameters["X4"], self.parameters["X5"], self.parameters["X6"]]
        precipitation = inputs['precipitation'].values.astype(float)
        evapotranspiration = inputs['evapotranspiration'].values.astype(float)
        states = np.zeros(3, dtype=float)
        states[0] = self.production_store * self.parameters["X1"]
        states[1] = self.routing_store * self.parameters["X3"]
        states[2] = self.exponential_store * self.parameters["X6"]
        flow = np.zeros(len(precipitation), dtype=float)

        self.model(
            parameters,
            precipitation,
            evapotranspiration,
            states,
            self.uh1,
            self.uh2,
            flow
        )
        
        # Update states :
        self.production_store = states[0] / self.parameters["X1"]
        self.routing_store = states[1] / self.parameters["X3"]
        self.exponential_store = states[2] / self.parameters["X6"]
    
        results = DataFrame({"flow": flow})
        results.index = inputs.index
        return results