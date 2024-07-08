from typing import Dict
import warnings
import numpy as np
from pandas import DataFrame
from hydrogr.model_interface import ModelGrInterface
from hydrogr._hydrogr import gr2m


class ModelGr2m(ModelGrInterface):
    """GR2M model inspired by IRSTEA airGR package.

    Note:
        Model parameters :
            X1 = production store capacity [mm],
            X2 = groundwater exchange coefficient [-]
        Model states :
            production_store : Production store capacity [mm].
            routing_store : Routing store capacity [mm].

    Attributes:
        production_store (float) : Production store capacity [mm].
        routing_store (float) : Routing store capacity [mm].
        parameters (Dict[str, float]) : Parameters of the model.

    Args:
        parameters (Dict[str, float]): Model parameters.

    Methods:
        run(inputs):
            Run the model over the period of the input data.
        set_parameters(parameters):
            Set model parameters.
        set_states(states):
            Set model states.
        get_states():
            Get model states.
    """

    name = "gr2m"
    model = gr2m
    frequency = ["M", "SM", "BM", "CBM", "MS", "SMS", "BMS", "CBMS"]
    parameters_names = ["X1", "X2"]
    states_names = ["production_store", "routing_store"]

    def __init__(self, parameters: Dict[str, float]):
        super().__init__(parameters)

        # Default states values
        self.production_store = 0.3
        self.routing_store = 0.5

    def set_parameters(self, parameters: Dict[str, float]):
        """Set model parameters.

        Args:
            parameters (dict): Dictionary that contain :
                X1 = production store capacity [mm],
                X2 = groundwater exchange coefficient [-]
        """
        for parameter_name in self.parameters_names:
            if parameter_name not in parameters:
                raise AttributeError(f"States should have a key : {parameter_name}")
        self.parameters = parameters

        threshold_x1x2 = 0.01
        if self.parameters["X1"] < threshold_x1x2:
            self.parameters["X1"] = threshold_x1x2
            warnings.warn(
                "Production reservoir level under threshold {} [mm]. Will replaced by the threshold.".format(
                    threshold_x1x2
                )
            )
        if self.parameters["X2"] < threshold_x1x2:
            self.parameters["X2"] = threshold_x1x2
            warnings.warn(
                "Production reservoir level under threshold {} [mm]. Will replaced by the threshold.".format(
                    threshold_x1x2
                )
            )

    def set_states(self, states: Dict[str, float]):
        """Set the model state

        Args:
            states (Dict[str, float]): Dictionary that contains the model state :
                production_store (float) : Production store capacity [mm].
                routing_store (float) : Routing store capacity [mm].
        """
        for state_name in self.states_names:
            if state_name not in states:
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

    def get_states(self) -> Dict[str, float]:
        """Get model states as dict.

        Returns:
            Dict[str, float]: Dictionary that contains the model state :
                production_store (float) : Production store capacity [mm].
                routing_store (float) : Routing store capacity [mm].
        """
        states = {
            "production_store": self.production_store,
            "routing_store": self.routing_store,
        }
        return states

    def _run_model(self, inputs: DataFrame) -> DataFrame:
        """Run the model.

        Args:
            inputs (DataFrame): Input data handler, should contain precipitation and evapotranspiration time series.

        Returns:
            DataFrame: Dataframe that contains the flow time series [m3/s].
        """
        parameters = [self.parameters["X1"], self.parameters["X2"]]
        precipitation = inputs["precipitation"].values.astype(float)
        evapotranspiration = inputs["evapotranspiration"].values.astype(float)
        states = np.zeros(2, dtype=float)
        states[0] = self.production_store * self.parameters["X1"]
        states[1] = self.routing_store * self.parameters["X2"]

        states, flow = self.model(
            parameters,
            precipitation,
            evapotranspiration,
            states,
        )

        # Update states :
        self.production_store = states[0] / self.parameters["X1"]
        self.routing_store = states[1] / self.parameters["X2"]

        results = DataFrame({"flow": flow})
        results.index = inputs.index
        return results
