import abc
from hydrogr.input_data import InputDataHandler, InputRequirements

# TODO : Handle hotstart using states_end and last datasample date
# TODO : Add function to set states_start from hotstart and check the date


class ModelGrInterface(object, metaclass=abc.ABCMeta):
    """
    Interface for GR models. Also implement common methods, in particular the run() function.

    N.B : All GR model should possess class attribute listed in __mandatory_class_properties below!
    """

    __mandatory_class_properties = ['name', 'model', 'frequency', 'n_param', 'input_requirements']
    input_requirements = [InputRequirements(name='precipitation', positive=True),
                          InputRequirements(name='evapotranspiration', positive=True)]

    def __init__(self, model_inputs, parameters):
        if not isinstance(model_inputs, InputDataHandler):
            raise ValueError('model_inputs should be an instance of ModelInput class!')

        # Check that model posses all mandatory properties :
        for property_name in ModelGrInterface.__mandatory_class_properties:
            if not hasattr(self, property_name):
                raise AttributeError('All models have to possess the attribute : {}'.format(property_name))

        # Set input data :
        self.inputs = model_inputs
        self.input_data = None
        self.n_inputs = None
        self._set_input_data(model_inputs)

        self.parameters = None
        self._set_parameters(parameters)

        self.production_store_filling = 0.3
        self.routing_store_filling = 0.5
        self.exponential_store_level = 0.0
        self.uh1 = None
        self.uh2 = None
        self._set_initial_conditions()
    
    def run(self):
        """This function allocate the necessary variables, calls the model, and formats the results.

        Returns:
            pandas.Dataframe: Dataframe that contains the results of the simulation.
        """
        return self._run_model()
    
    def _set_input_data(self, input_data):
        if not input_data.Model.name == self.name:
            raise ValueError('Given inputs are defined for {} model and do not match the current model : {}'.format(input_data.model_name, self.name))
        self.input_data = self.inputs.data
        self.n_inputs = len(self.inputs.data.index)

    def _set_parameters(self, parameters):
        if not isinstance(parameters, list) or len(parameters) != self.n_param:
            raise ValueError('"parameters" should be a list of float of length {}.'.format(self.n_param))
        self.parameters = parameters

    @abc.abstractmethod
    def _set_initial_conditions(self):
        raise NotImplementedError('Not implemented in abstract class!')
    
    @abc.abstractmethod
    def _run_model(self):
        raise NotImplementedError('Not implemented in abstract class!')
