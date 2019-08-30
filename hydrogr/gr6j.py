import warnings
from hydrogr.model_interface import ModelGrInterface
from hydrogr.models import gr6j
import numpy as np


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
    n_param = 6
    n_states = 7 + 3 * 20
    output_name_list = ["PotEvap", "Precip", "Prod", "Pn", "Ps", "AE", "Perc", "PR", "Q9", "Q1",
                        "Rout", "Exch", "AExch1", "AExch2", "AExch", "QR", "QRExp", "Exp", "QD", "Qsim"]

    def __init__(self, model_inputs, parameters):
        super().__init__(model_inputs, parameters)

    def set_parameters(self, parameters):
        """
        Set model parameters

        :param parameters: List of float of length 4 that contain :
                           X1 = production store capacity [mm],
                           X2 = inter-catchment exchange coefficient [mm/d],
                           X3 = routing store capacity [mm]
                           X4 = unit hydrograph time constant [d]
                           X5 = intercatchment exchange threshold [-]
                           X6 = coefficient for emptying exponential store [mm]
        """
        super().set_parameters(parameters)

        threshold_x1x3x6 = 0.01
        threshold_x4 = 0.5
        if self.parameters[0] < threshold_x1x3x6:
            self.parameters[0] = threshold_x1x3x6
            warnings.warn('Production reservoir level under threshold {} [mm]. Will replaced by the threshold.'.format(threshold_x1x3x6))
        if self.parameters[2] < threshold_x1x3x6:
            self.parameters[2] = threshold_x1x3x6
            warnings.warn('Routing reservoir level under threshold {} [mm]. Will replaced by the threshold.'.format(threshold_x1x3x6))
        if self.parameters[3] < threshold_x4:
            self.parameters[3] = threshold_x4
            warnings.warn('Unit hydrograph time constant under threshold {} [d]. Will replaced by the threshold.'.format(threshold_x4))
        if self.parameters[5] < threshold_x1x3x6:
            self.parameters[5] = threshold_x1x3x6
            warnings.warn('Coefficient for emptying exponential store under threshold {} [mm]. Will replaced by the threshold.'.format(threshold_x1x3x6))

    def set_initial_conditions(self, production_store_filling=None, routing_store_filling=None, uh1=None, uh2=None):
        """
        Set model initial conditions

        :param production_store_filling: Production store filling in percentage [0, 1]
        :param routing_store_filling: Routing store filling in percentage [0, 1]
        :param uh1: First unit hydrograph vector (length  = 20)
        :param uh2: Second unit hydrograph vector (length = 2 * len(uh1)
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

        if uh1 is not None:
            assert isinstance(uh1, list)
            self.uh1 = uh1
        elif self.uh1 is None:
            self.uh1 = np.zeros(20, dtype=float)

        if uh2 is not None:
            assert isinstance(uh2, list)
            self.uh2 = uh2
        elif self.uh2 is None:
            self.uh2 = np.zeros(40, dtype=float)

    def _get_state_start(self):
        state_start = np.zeros(self.n_states, dtype=float)
        state_start[0] = self.production_store_filling * self.parameters[0]
        state_start[1] = self.routing_store_filling * self.parameters[2]
        state_start[7: 7 + 20] = self.uh1
        state_start[7 + 20: 7 + 3 * 20] = self.uh2
        return state_start
