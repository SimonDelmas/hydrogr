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
    n_param = 2

    def __init__(self, model_inputs, parameters):
        super().__init__(model_inputs, parameters)

    def _set_parameters(self, parameters):
        """
        Set model parameters

        :param parameters: List of float of length 2 that contain :
                           X1 = production store capacity [mm],
                           X2 = groundwater exchange coefficient [-]
        """
        super()._set_parameters(parameters)

        threshold_x1x2 = 0.01
        if self.parameters[0] < threshold_x1x2:
            self.parameters[0] = threshold_x1x2
            warnings.warn('Production reservoir level under threshold {} [mm]. Will replaced by the threshold.'.format(threshold_x1x2))
        if self.parameters[1] < threshold_x1x2:
            self.parameters[1] = threshold_x1x2
            warnings.warn('Groundwater exchange coefficient under threshold {} [-]. Will replaced by the threshold.'.format(threshold_x1x2))

    def _set_initial_conditions(self, production_store_filling=None, routing_store_filling=None):
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

    def _run_model(self):
        precipitation = self.input_data['precipitation'].values.astype(float)
        evapotranspiration = self.input_data['evapotranspiration'].values.astype(float)
        states = self._get_states()
        flow = np.zeros(len(precipitation), dtype=float)

        self.model(
            self.parameters,
            precipitation,
            evapotranspiration,
            states,
            flow
        )
    
        results = DataFrame({"flow": flow})
        results.index = self.input_data.index
        return results
    
    def _get_states(self):
        states = np.zeros(2, dtype=float)
        states[0] = self.production_store_filling * self.parameters[0]
        states[1] = self.routing_store_filling * self.parameters[1]
        return states
