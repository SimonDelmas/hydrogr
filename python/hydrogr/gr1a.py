from hydrogr.model_interface import ModelGrInterface
from hydrogr._hydrogr import gr1a
import numpy as np
from pandas import DataFrame


class ModelGr1a(ModelGrInterface):
    """
    GR1A model implementation based on fortran function from IRSTEA package airGR :
    https://cran.r-project.org/web/packages/airGR/index.html

    :param model_inputs: InputDataHandler, should contain precipitation and evapotranspiration time series
    :param parameters: List of float of length 1 that contain GR1A unique and dimensionless parameter
    """

    name = 'gr1a'
    model = gr1a
    frequency = ['A', 'Y', 'BA', 'BY', 'AS', 'YS', 'BAS', 'BYS']
    parameters_names = ["X1"]
    states_names = []

    def __init__(self, parameters):
        super().__init__(parameters)

    def set_parameters(self, parameters):
        """Set model parameters

        Args:
            parameters (list): List of one element that contain : X1 = store capacity [mm]
        """
        for parameter_name in self.parameters_names:
            if not parameter_name in parameters:
                raise AttributeError(f"States should have a key : {parameter_name}")
        self.parameters = parameters

    def set_states(self, states):
        """Model GR1A do not have any parameters
        """
        pass

    def get_states(self):
        """Return empty dict
        """
        return dict()

    def _run_model(self, inputs):
        parameters = [self.parameters["X1"]]
        precipitation = inputs['precipitation'].values.astype(float)
        evapotranspiration = inputs['evapotranspiration'].values.astype(float)
        flow = np.zeros(len(precipitation), dtype=float)

        self.model(
            parameters,
            precipitation,
            evapotranspiration,
            flow
        )
    
        results = DataFrame({"flow": flow})
        results.index = inputs.index
        return results
