from typing import Dict, Any
from hydrogr.model_interface import ModelGrInterface
from hydrogr._hydrogr import gr1a
from pandas import DataFrame


class ModelGr1a(ModelGrInterface):
    """GR1A model inspired by IRSTEA airGR package.

    Note:
        Model parameters :
            X1 : GR1A unique and dimensionless parameter.

    Attributes:
        parameter_name (Dict[str, float]) : Parameter of the model:
            X1, GR1A unique and dimensionless parameter.

    Args:
        parameters (Dict[str, float]): Should define X1, GR1A unique and dimensionless parameter.

    Methods:
        run(inputs):
            Run the model over the period of the input data.
        set_parameters(parameters):
            Set model parameters.
    """

    name = "gr1a"
    model = gr1a
    frequency = ["A", "Y", "BA", "BY", "AS", "YS", "BAS", "BYS", "YE"]
    parameters_names = ["X1"]
    states_names = []

    def __init__(self, parameters):
        """Constructs an ModelGr1a object.

        Args:
            parameters (Dict[str, float]): Value of the parameters require by the model:
                X1 = GR1A unique and dimensionless parameter.
        """
        super().__init__(parameters)

    def set_parameters(self, parameters: Dict[str, float]):
        """Set model parameters.

        Args:
            parameters (Dict[str, float]): Value of the parameters require by the model :
                X1 = GR1A unique and dimensionless parameter.
        """
        for parameter_name in self.parameters_names:
            if parameter_name not in parameters:
                raise AttributeError(f"States should have a key : {parameter_name}")
        self.parameters = parameters

    def set_states(self, states: Dict[str, Any]):
        """Model GR1A do not have any parameters"""
        pass

    def get_states(self) -> Dict[str, Any]:
        """Return empty dict"""
        return dict()

    def _run_model(self, inputs: DataFrame) -> DataFrame:
        """Run the model.

        Args:
            inputs (DataFrame): Input data handler, should contain precipitation and evapotranspiration time series.

        Returns:
            DataFrame: Dataframe that contains the flow time series [m3/s].
        """
        parameters = [self.parameters["X1"]]
        precipitation = inputs["precipitation"].values.astype(float)
        evapotranspiration = inputs["evapotranspiration"].values.astype(float)

        flow = self.model(parameters, precipitation, evapotranspiration)

        results = DataFrame({"flow": flow})
        results.index = inputs.index
        return results
