import abc
from hydrogr.input_data import InputDataHandler, InputRequirements


class ModelGrInterface(object, metaclass=abc.ABCMeta):
    """
    Interface for GR models. Also implement common methods, in particular the run() function.

    N.B : All GR model should possess class attribute listed in __mandatory_class_properties below!
    """

    __mandatory_class_properties = ['name', 'model', 'frequency', 'n_param', "states_names"]
    input_requirements = [InputRequirements(name='precipitation', positive=True),
                          InputRequirements(name='evapotranspiration', positive=True)]

    def __init__(self, parameters):
        # Check that model posses all mandatory properties :
        for property_name in ModelGrInterface.__mandatory_class_properties:
            if not hasattr(self, property_name):
                raise AttributeError('All models have to possess the attribute : {}'.format(property_name))

        self.parameters = None
        self.set_parameters(parameters)
    
    def run(self, inputs):
        """Run the model on the given input data. Return the results as a Pandas dataframe.

        Args:
            inputs (pandas.Dataframe): Dataframe that define the require inputs time series for the simulation duration.

        Returns:
            pandas.Dataframe: Dataframe that contains the results of the simulation, for each timestamp in the input data.
        """
        inputs = InputDataHandler(self, inputs)
        return self._run_model(inputs.data)
    
    def set_parameters(self, parameters):
        """Set the model static parameters.

        Args:
            parameters (list): Value of the parameters require by the model.

        Raises:
            ValueError: If the number of given parameters do not match the number of parameters require by the model.
        """
        if not isinstance(parameters, list) or len(parameters) != self.n_param:
            raise ValueError('"parameters" should be a list of float of length {}.'.format(self.n_param))
        self.parameters = parameters
        
    @abc.abstractmethod
    def set_states(self):
        raise NotImplementedError('Not implemented in abstract class!')
    
    @abc.abstractmethod
    def get_states(self):
        raise NotImplementedError('Not implemented in abstract class!')
    
    @abc.abstractmethod
    def _run_model(self):
        raise NotImplementedError('Not implemented in abstract class!')
