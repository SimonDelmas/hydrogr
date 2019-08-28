import warnings
from hydrogr.model_interface import ModelGrInterface
from hydrogr.models import gr2m
import numpy as np


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
    n_param = 2
    n_states = 7 + 3 * 20
    output_name_list = ["PotEvap", "Precip", "AE", "Perc", "P3", "Exch", "Prod", "Rout", "Qsim"]

    def __init__(self, model_inputs, parameters):
        super().__init__(model_inputs, parameters)

    def set_parameters(self, parameters):
        """
        Set model parameters

        :param parameters: List of float of length 2 that contain :
                           X1 = production store capacity [mm],
                           X2 = groundwater exchange coefficient [-]
        """
        super().set_parameters(parameters)

        threshold_x1x2 = 0.01
        if self.parameters[0] < threshold_x1x2:
            self.parameters[0] = threshold_x1x2
            warnings.warn('Production reservoir level under threshold {} [mm]. Will replaced by the threshold.'.format(threshold_x1x2))
        if self.parameters[1] < threshold_x1x2:
            self.parameters[1] = threshold_x1x2
            warnings.warn('Groundwater exchange coefficient under threshold {} [-]. Will replaced by the threshold.'.format(threshold_x1x2))

    def set_initial_conditions(self, production_store_filling=None, routing_store_filling=None):
        """
        Set GR2M initial conditions

        :param production_store_filling: Production store filling in percentage [0, 1]
        :param routing_store_filling: Routing store filling in percentage [0, 1]
        """
        if production_store_filling is not None:
            assert isinstance(production_store_filling, (float, int))
            assert 0 <= production_store_filling <= 1
            self.production_store_filling = production_store_filling
        elif self.production_store_filling is None:
            self.production_store_filling = 0.3

        if routing_store_filling is not None:
            assert isinstance(routing_store_filling, (float, int))
            assert 0 <= routing_store_filling <= 1
            self.routing_store_filling = routing_store_filling
        elif self.routing_store_filling is None:
            self.routing_store_filling = 0.5

    def _get_state_start(self):
        state_start = np.zeros(self.n_states, dtype=float)
        state_start[0] = self.production_store_filling * self.parameters[0]
        state_start[1] = self.routing_store_filling * self.parameters[1]
        state_start[7: 7 + 20] = self.uh1
        state_start[7 + 20: 7 + 3 * 20] = self.uh2
        return state_start
