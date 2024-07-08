from typing import Dict, Any
import abc
from pandas import DataFrame
from hydrogr.input_data import InputDataHandler, InputRequirements


class ModelGrInterface(object, metaclass=abc.ABCMeta):
    """Interface for GR models. Also implement common methods, in particular the run() function.
    N.B : All GR model should possess class attribute listed in __mandatory_class_properties below!

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

    __mandatory_class_properties = [
        "name",
        "model",
        "frequency",
        "parameters_names",
        "states_names",
    ]
    input_requirements = [
        InputRequirements(name="precipitation", positive=True),
        InputRequirements(name="evapotranspiration", positive=True),
    ]

    def __init__(self, parameters: Dict[str, float]):
        """Constructs an ModelGrInterface object.

        Args:
            parameters (Dict[str, float]): Value of the parameters require by the model.
        """
        # Check that model posses all mandatory properties :
        for property_name in ModelGrInterface.__mandatory_class_properties:
            if not hasattr(self, property_name):
                raise AttributeError(
                    "All models have to possess the attribute : {}".format(
                        property_name
                    )
                )

        self.set_parameters(parameters)

    def run(self, inputs: DataFrame) -> DataFrame:
        """Run the model on the given input data. Return the results as a Pandas dataframe.

        Args:
            inputs (DataFrame): Dataframe that define the require inputs time series for the simulation duration.

        Returns:
            DataFrame: Dataframe that contains the results of the simulation, for each timestamp in the input data.
        """
        inputs = InputDataHandler(
            self, inputs
        )  # To ensure input data is coherent with the model.
        return self._run_model(inputs.data)

    @abc.abstractmethod
    def set_parameters(self, parameters: Dict[str, float]):
        """Set the model static parameters.

        Args:
            parameters (dict): Value of the parameters require by the model.
        """
        raise NotImplementedError("Not implemented in abstract class!")

    @abc.abstractmethod
    def set_states(self, states: Dict[str, Any]):
        """Set the model state.

        Args:
            states (Dict[str, Any]): Dictionary that contains the model state.
        """
        raise NotImplementedError("Not implemented in abstract class!")

    @abc.abstractmethod
    def get_states(self) -> Dict[str, Any]:
        """Get model states as dict.

        Returns:
            Dict[str, Any]: Dictionary that contains the model state.
        """
        raise NotImplementedError("Not implemented in abstract class!")

    @abc.abstractmethod
    def _run_model(self, inputs: DataFrame):
        raise NotImplementedError("Not implemented in abstract class!")
