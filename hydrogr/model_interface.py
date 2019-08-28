import abc
from hydrogr.input_data import InputDataHandler, InputRequirements
import numpy as np
from pandas import DataFrame

# TODO : Handle hotstart using states_end and last datasample date
# TODO : Add function to set states_start from hotstart and check the date


class ModelInterface(object, metaclass=abc.ABCMeta):
    """
    Create in the eventuality that snow model (Cemaneige) differ from GR models.
    May be modify later!
    """

    def __init__(self, model_inputs):
        if not isinstance(model_inputs, InputDataHandler):
            raise ValueError('model_inputs should be an instance of ModelInput class!')
        self.inputs = model_inputs

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError('Not implemented in abstract class!')


class ModelGrInterface(ModelInterface, metaclass=abc.ABCMeta):
    """
    Interface for GR models. Also implement common methods, in particular the run() function.

    N.B : All GR model should possess class attribute listed in __mandatory_class_properties below!
    """

    __mandatory_class_properties = ['name', 'model', 'frequency', 'n_param', 'n_states', 'input_requirements', 'output_name_list']
    input_requirements = [InputRequirements(name='precipitation', positive=True),
                          InputRequirements(name='evapotranspiration', positive=True)]

    def __init__(self, model_inputs, parameters):
        super().__init__(model_inputs)

        # Check that model posses all mandatory properties :
        for property_name in ModelGrInterface.__mandatory_class_properties:
            if not hasattr(self, property_name):
                raise AttributeError('All models have to possess the attribute : {}'.format(property_name))

        # Set input data :
        self.input_data = None
        self.n_inputs = None
        self.set_input_data(model_inputs)

        self.parameters = None

        self.production_store_filling = 0.3
        self.routing_store_filling = 0.5
        self.exponential_store_level = 0.0
        self.uh1 = None
        self.uh2 = None

        self.set_parameters(parameters)
        self.set_initial_conditions()

    @property
    def n_outputs(self):
        return len(self.output_name_list)

    def set_input_data(self, input_data):
        if not input_data.Model.name == self.name:
            raise ValueError('Given inputs are defined for {} model and do not match the current model : {}'.format(input_data.model_name, self.name))
        self.input_data = self.inputs.data
        self.n_inputs = len(self.inputs.data.index)

    def _check_parameters_type(self, parameters):
        if not isinstance(parameters, list) or len(parameters) != self.n_param:
            raise ValueError('"parameters" should be a list of float of length {}.'.format(self.n_param))

    def set_parameters(self, parameters):
        self._check_parameters_type(parameters)
        self.parameters = parameters

    @abc.abstractmethod
    def set_initial_conditions(self):
        raise NotImplementedError('Not implemented in abstract class!')

    @abc.abstractmethod
    def _get_state_start(self):
        raise NotImplementedError('Not implemented in abstract class!')

    def run(self):
        """
        This function allocate the necessary variables, calls the model, and formats the results.

        :return: Dict of output arrays
        """
        precipitation = self.input_data['precipitation'].values.astype(float)
        evapotranspiration = self.input_data['evapotranspiration'].values.astype(float)
        parameters = np.array(self.parameters, dtype=float)
        state_start = self._get_state_start()

        index_outputs = np.array(range(1, self.n_outputs + 1), dtype=int)
        outputs = np.full((self.n_inputs, self.n_outputs), -999.999, dtype=float, order='F')
        state_end = np.zeros(self.n_states, dtype=float)

        self.model(precipitation, evapotranspiration, parameters, state_start, index_outputs, outputs, state_end)

        formatted_output = DataFrame(data=outputs, columns=self.output_name_list)
        formatted_output.index = self.input_data.index
        return formatted_output
