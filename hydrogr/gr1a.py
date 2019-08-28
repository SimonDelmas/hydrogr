from hydrogr.model_interface import ModelGrInterface
from hydrogr.models import gr1a
import numpy as np


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
    n_param = 1
    n_states = 7 + 3 * 20
    output_name_list = ["PotEvap", "Precip", "Qsim"]

    def __init__(self, model_inputs, parameters):
        super().__init__(model_inputs, parameters)

    def set_parameters(self, parameters):
        super().set_parameters(parameters)

    def set_initial_conditions(self):
        """
        GR1A model does not use initial states!
        """
        pass

    def _get_state_start(self):
        state_start = np.zeros(self.n_states, dtype=float)
        return state_start
