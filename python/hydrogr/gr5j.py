from typing import Dict, Any
import warnings
import numpy as np
from pandas import DataFrame
from hydrogr.model_interface import ModelGrInterface
from hydrogr._hydrogr import gr5j


class ModelGr5j(ModelGrInterface):
    """GR5J model inspired by INRAE airGR package.

    Note:
        Model parameters :
            X1 : production store capacity [mm].
            X2 : inter-catchment exchange coefficient [mm/d].
            X3 : routing store capacity [mm].
            X4 : unit hydrograph time constant [d].
            X5 : inter-catchment exchange threshold [-].
        Model states :
            production_store : Production store capacity [mm].
            routing_store : Routing store capacity [mm].
            uh1 : unit hydrograph uh1 [-].
            uh2 : unit hydrograph uh2 [-].

    Attributes:
        production_store (float) : Production store capacity [mm].
        routing_store (float) : Routing store capacity [mm].
        uh1 (NDArray[Any]) : unit hydrograph uh1 [-].
        uh2 (NDArray[Any]) : unit hydrograph uh2 [-].
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

    name = "gr5j"
    model = gr5j
    frequency = ["D", "B", "C"]
    parameters_names = ["X1", "X2", "X3", "X4", "X5"]
    states_names = ["production_store", "routing_store", "uh1", "uh2"]

    def __init__(self, parameters: Dict[str, float]):
        """Constructs an ModelGr5j object.

        Args:
            parameters (Dict[str, float]): Dictionary that contain :
                X1 = production store capacity [mm],
                X2 = inter-catchment exchange coefficient [mm/d],
                X3 = routing store capacity [mm],
                X4 = unit hydrograph time constant [d],
                X5 = inter-catchment exchange threshold [-],
        """
        super().__init__(parameters)

        # Default states values
        self.production_store = 0.3
        self.routing_store = 0.5
        self.uh1 = np.zeros(20, dtype=float)
        self.uh2 = np.zeros(40, dtype=float)

    def set_parameters(self, parameters: Dict[str, float]):
        """Set model parameters

        Args:
            parameters (Dict[str, float]): Dictionary that contain :
                X1 = production store capacity [mm],
                X2 = inter-catchment exchange coefficient [mm/d],
                X3 = routing store capacity [mm],
                X4 = unit hydrograph time constant [d],
                X5 = inter-catchment exchange threshold [-],
        """
        for parameter_name in self.parameters_names:
            if parameter_name not in parameters:
                raise AttributeError(f"States should have a key : {parameter_name}")
        self.parameters = parameters

        threshold_x1x3 = 0.01
        threshold_x4 = 0.5
        if self.parameters["X1"] < threshold_x1x3:
            self.parameters["X1"] = threshold_x1x3
            warnings.warn(
                "Production reservoir level under threshold {} [mm]. Will replaced by the threshold.".format(
                    threshold_x1x3
                )
            )
        if self.parameters["X3"] < threshold_x1x3:
            self.parameters["X3"] = threshold_x1x3
            warnings.warn(
                "Routing reservoir level under threshold {} [mm]. Will replaced by the threshold.".format(
                    threshold_x1x3
                )
            )
        if self.parameters["X4"] < threshold_x4:
            self.parameters["X4"] = threshold_x4
            warnings.warn(
                "Unit hydrograph time constant under threshold {} [d]. Will replaced by the threshold.".format(
                    threshold_x4
                )
            )

    def set_states(self, states: Dict[str, Any]):
        """Set the model state.

        Args:
            states (Dict[str, Any]): Dictionary that contains the model state :
                production_store : Production store capacity [mm].
                routing_store : Routing store capacity [mm].
                uh1 : unit hydrograph uh1 [-].
                uh2 : unit hydrograph uh2 [-].
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

        if states["uh1"] is not None:
            assert isinstance(states["uh1"], (np.ndarray, np.generic))
            self.uh1 = states["uh1"]
        else:
            self.uh1 = np.zeros(20, dtype=float)

        if states["uh2"] is not None:
            assert isinstance(states["uh2"], (np.ndarray, np.generic))
            self.uh2 = states["uh2"]
        else:
            self.uh2 = np.zeros(40, dtype=float)

    def get_states(self) -> Dict[str, float]:
        """Get model states as dict.

        Returns:
            Dict[str, Any]: With keys :
                production_store : Production store capacity [mm].
                routing_store : Routing store capacity [mm].
                uh1 : unit hydrograph uh1 [-].
                uh2 : unit hydrograph uh2 [-].
        """
        states = {
            "production_store": self.production_store,
            "routing_store": self.routing_store,
            "uh1": self.uh1,
            "uh2": self.uh2,
        }
        return states

    def _run_model(self, inputs: DataFrame) -> DataFrame:
        """Run the model.

        Args:
            inputs (DataFrame): Input data handler, should contain precipitation and evapotranspiration time series.

        Returns:
            DataFrame: Dataframe that contains the flow time series [mm/d].
        """
        parameters = [
            self.parameters["X1"],
            self.parameters["X2"],
            self.parameters["X3"],
            self.parameters["X4"],
            self.parameters["X5"],
        ]
        precipitation = inputs["precipitation"].values.astype(float)
        evapotranspiration = inputs["evapotranspiration"].values.astype(float)
        states = np.zeros(2, dtype=float)
        states[0] = self.production_store * self.parameters["X1"]
        states[1] = self.routing_store * self.parameters["X3"]

        states, self.uh2, flow = self.model(
            parameters,
            precipitation,
            evapotranspiration,
            states,
            self.uh2,
        )

        # Update states :
        self.production_store = states[0] / self.parameters["X1"]
        self.routing_store = states[1] / self.parameters["X3"]

        results = DataFrame({"flow": flow})
        results.index = inputs.index
        return results
