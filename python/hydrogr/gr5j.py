import warnings
import numpy as np
from pandas import DataFrame
from hydrogr.model_interface import ModelGrInterface
from hydrogr._hydrogr import gr5j


class ModelGr5j(ModelGrInterface):
    """
    GR5J model implementation based on fortran function from IRSTEA package airGR :
    https://cran.r-project.org/web/packages/airGR/index.html

    :param model_inputs: Input data handler, should contain precipitation and evapotranspiration time series
    :param parameters: List of float of length 4 that contain :
                       X1 = production store capacity [mm],
                       X2 = inter-catchment exchange coefficient [mm/d],
                       X3 = routing store capacity [mm]
                       X4 = unit hydrograph time constant [d]
                       X5 = intercatchment exchange threshold [-]
    """

    name = 'gr5j'
    model = gr5j
    frequency = ['D', 'B', 'C']
    n_param = 5
    
    def __init__(self, model_inputs, parameters):
        super().__init__(model_inputs, parameters)

    def _set_parameters(self, parameters):
        """
        Set model parameters

        :param parameters: List of float of length 4 that contain :
                           X1 = production store capacity [mm],
                           X2 = inter-catchment exchange coefficient [mm/d],
                           X3 = routing store capacity [mm]
                           X4 = unit hydrograph time constant [d]
                           X5 = intercatchment exchange threshold [-]
        """
        super()._set_parameters(parameters)

        threshold_x1x3 = 0.01
        threshold_x4 = 0.5
        if self.parameters[0] < threshold_x1x3:
            self.parameters[0] = threshold_x1x3
            warnings.warn('Production reservoir level under threshold {} [mm]. Will replaced by the threshold.'.format(threshold_x1x3))
        if self.parameters[2] < threshold_x1x3:
            self.parameters[2] = threshold_x1x3
            warnings.warn('Routing reservoir level under threshold {} [mm]. Will replaced by the threshold.'.format(threshold_x1x3))
        if self.parameters[3] < threshold_x4:
            self.parameters[3] = threshold_x4
            warnings.warn('Unit hydrograph time constant under threshold {} [d]. Will replaced by the threshold.'.format(threshold_x4))

    def _set_initial_conditions(self, production_store_filling=None, routing_store_filling=None, uh1=None, uh2=None):
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

    def _get_states(self):
        states = np.zeros(2, dtype=float)
        states[0] = self.production_store_filling * self.parameters[0]
        states[1] = self.routing_store_filling * self.parameters[2]
        return states
    
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
            self.uh2,
            flow
        )
    
        results = DataFrame({"flow": flow})
        results.index = self.input_data.index
        return results
