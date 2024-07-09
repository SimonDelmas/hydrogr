import warnings
import pandas as pd
import pandas.api.types as ptypes
from datetime import datetime

"""
Todo:
    - Add method to create train and test set from input data (not necessary in the handler)
    - Add method to get period based on the flow or the rainfall (not necessary in the handler) => Useful for specific calibration
"""


class InputDataHandler(object):
    """
    This class is an helper to ensure that the data used fit the model requirement
    in term (at least) of input time series and frequency.
    It also provide methods to manipulate the data (mainly apply function to it)
    and extract subset of data based on certain criterion (sub-period, flooding or low flow for example).

    Args:
        Model (ModelGrInterface): Model that will use the input data.
        data (Dataframe): Input data.

    Methods:
        get_sub_period(start_date, end_date) : Get input data on a sub-period.

    Example:

        >>> from hydrogr.input_data import InputDataHandler
        >>> from hydrogr.model_gr1a import ModelGr1a
        >>> input_handler = InputDataHandler(ModelGr1a, df)
    """

    def __init__(self, Model, data: pd.DataFrame):
        if not isinstance(data, pd.DataFrame):
            raise TypeError(
                "Expecting a pandas.Dataframe for input data, received {} instead.".format(
                    type(data)
                )
            )

        self.Model = Model

        self.data: pd.DataFrame = data
        self.__check_data()
        self.__check_data_frequency()

        self.n_inputs = len(self.data.index)
        self.start_date = self.data.index[0]
        self.end_date = self.data.index[-1]

    def get_sub_period(
        self, start_date: datetime, end_date: datetime
    ) -> "InputDataHandler":
        """Return a new input handler with input data on the selected period.

        Args:
            start_date (datetime): Period start date
            end_date (datetime): Period start date

        Returns:
            InputDataHandler: Data on the selected period.
        """
        if start_date < self.start_date:
            warnings.warn(
                "The selected start date ({}) is prior to the date of the first datasample : {}".format(
                    start_date, self.start_date
                )
            )
        if end_date > self.end_date:
            warnings.warn(
                "The selected end date ({}) is posterior to the date of the last datasample : {}".format(
                    end_date, self.end_date
                )
            )

        mask = (self.data.index >= start_date) & (self.data.index <= end_date)
        return InputDataHandler(self.Model, self.data.loc[mask])

    def __check_data(self):
        """
        Check input data type and frequency. Also checks the data prerequisites, defined in the models.
        """
        if not (
            isinstance(self.data.index, pd.DatetimeIndex)
            or isinstance(self.data.index, pd.PeriodIndex)
        ):
            raise TypeError(
                "Input data index should be datetime or period object. Received : {} instead.".format(
                    self.data.index.dtypes
                )
            )

        if isinstance(self.data.index, pd.PeriodIndex):
            self.data.index = self.data.index.to_timestamp()

        for prerequisite in self.Model.input_requirements:
            if prerequisite.name not in self.data:
                raise ValueError(
                    'Input data should contains "{}" data! Keyword "{}" not found.'.format(
                        prerequisite.name, prerequisite.name
                    )
                )
            elif not ptypes.is_float_dtype(self.data[prerequisite.name]):
                raise ValueError(
                    'Input data "{}" should be float! Currently : {}'.format(
                        prerequisite.name, self.data[prerequisite].dtypes
                    )
                )
            self.__check_for_na_in_inputs(prerequisite.name)

            if prerequisite.positive:
                self.__check_for_negative_values_in_inputs(prerequisite.name)

    def __check_data_frequency(self):
        """
        Check input data frequency using pandas offset aliases :
        https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html
        """
        freq = self.data.index.freq
        if freq is not None:
            freq = freq.name
        else:
            freq = pd.infer_freq(self.data.index)

        # For annual frequency pandas also return the month so we have to split the result :
        if freq.split("-")[0] in self.Model.frequency:
            return 0
        else:
            raise ValueError(
                "Incompatibility between the frequency of the data and the chosen model! \n "
                "Data frequency : {} \n "
                "Expected frequency for {} : {}".format(
                    freq, self.Model.name, self.Model.frequency
                )
            )

    def __check_for_na_in_inputs(self, column_name):
        detected_na = self.data[column_name].isnull().values.any()
        if detected_na:
            warnings.warn(
                "NA detected in {} time series! ({})".format(
                    InputDataHandler.data_names[column_name], column_name
                )
            )

    def __check_for_negative_values_in_inputs(self, column_name):
        detected_neg = (self.data[column_name] < 0.0).any()
        if detected_neg:
            warnings.warn(
                "Negative values detected in {} time series! ({})".format(
                    InputDataHandler.data_names[column_name], column_name
                )
            )


class InputRequirements(object):
    """
    Simple helper to define model mandatory input time series as well as the associated rules
    """

    def __init__(self, name, positive=False):
        self.name = name
        self.positive = positive
