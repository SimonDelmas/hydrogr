import abc
from hydrogr.input_data import InputDataHandler, InputRequirements


class ModelGrInterface(object, metaclass=abc.ABCMeta):
    """
    Interface for GR models. Also implement common methods, in particular the run() function.

    N.B : All GR model should possess class attribute listed in __mandatory_class_properties below!
    """

    __mandatory_class_properties = ['name', 'model', 'frequency', "parameters_names", "states_names"]
    input_requirements = [InputRequirements(name='precipitation', positive=True),
                          InputRequirements(name='evapotranspiration', positive=True)]

    def __init__(self, parameters):
        # Check that model posses all mandatory properties :
        for property_name in ModelGrInterface.__mandatory_class_properties:
            if not hasattr(self, property_name):
                raise AttributeError('All models have to possess the attribute : {}'.format(property_name))

        self.set_parameters(parameters)
    
    def run(self, inputs):
        """Run the model on the given input data. Return the results as a Pandas dataframe.

        Args:
            inputs (pandas.Dataframe): Dataframe that define the require inputs time series for the simulation duration.

        Returns:
            pandas.Dataframe: Dataframe that contains the results of the simulation, for each timestamp in the input data.
        """
        inputs = InputDataHandler(self, inputs)  # To ensure input data is coherent with the model.
        return self._run_model(inputs.data)
    
    @abc.abstractmethod
    def set_parameters(self, parameters):
        """Set the model static parameters.

        Args:
            parameters (dict): Value of the parameters require by the model.
        """
        raise NotImplementedError('Not implemented in abstract class!')
    
    @abc.abstractmethod
    def set_states(self, states):
        """Set the model state

        Args:
            states (dict): Dictionary that contains the model state.
        """
        raise NotImplementedError('Not implemented in abstract class!')
    
    @abc.abstractmethod
    def get_states(self):
        """Get model states as dict.

        Returns:
            dict: Dictionary that contains the model state.
        """
        raise NotImplementedError('Not implemented in abstract class!')
    
    @abc.abstractmethod
    def _run_model(self, inputs):
        raise NotImplementedError('Not implemented in abstract class!')
