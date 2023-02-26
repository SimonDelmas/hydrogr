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
    n_param = 1

    def __init__(self, model_inputs, parameters):
        super().__init__(model_inputs, parameters)

    def _set_parameters(self, parameters):
        super()._set_parameters(parameters)

    def _set_initial_conditions(self):
        """
        GR1A model does not use initial states!
        """
        pass

    def _run_model(self):
        precipitation = self.input_data['precipitation'].values.astype(float)
        evapotranspiration = self.input_data['evapotranspiration'].values.astype(float)
        flow = np.zeros(len(precipitation), dtype=float)

        self.model(
            self.parameters,
            precipitation,
            evapotranspiration,
            flow
        )
    
        results = DataFrame({"flow": flow})
        results.index = self.input_data.index
        return results
