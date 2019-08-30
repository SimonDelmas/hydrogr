from pathlib import Path
import datetime
import numpy as np
import pandas as pd
from hydrogr import InputDataHandler, ModelGr4j
import spotpy

# TODO : Ensure there is no nan in observation!
# TODO : Apply function to sim and obs before objective function calculation
# TODO : Reduce objective function calculation to period with low or high flow


class CalibrationModelGR4J(object):
    """ Just a class with a run method to be used with spotpy
        Run method takes the optimization parameters as input
        It should return a numpy array that will be passed to the objective function
    """

    def __init__(self, data, start_date, end_date):
        self.start = start_date
        self.end = end_date

        self.data = data
        self.model_inputs = InputDataHandler(ModelGr4j, self.data)
        self.bound = [[0.0, 200.0], [0.0, 1.0], [0.0, 100.0], [0.0, 10.0]]  # Physical parameter boundaries

    def run(self, x1, x2, x3, x4):
        if not self.bound[0][0] < x1 < self.bound[0][1] or \
           not self.bound[1][0] < x2 < self.bound[1][1] or \
           not self.bound[2][0] < x3 < self.bound[2][1] or \
           not self.bound[3][0] < x4 < self.bound[3][1]:
            return self.data['precipitation'] * -np.inf

        model = ModelGr4j(self.model_inputs, [x1, x2, x3, x4])
        outputs = model.run()
        if 'Qsim' in outputs.keys():
            return outputs['Qsim']
        else:
            return self.data['precipitation'] * -np.inf


class SpotpySetup(object):
    """
    Interface to use the model with spotpy
    """

    def __init__(self, data):
        start_date = datetime.datetime(1998, 1, 1, 0, 0)
        end_date = datetime.datetime(2008, 1, 1, 0, 0)
        self.data = data
        mask = (self.data['date'] >= start_date) & (self.data['date'] <= end_date)
        self.data = self.data.loc[mask]

        self.model = CalibrationModelGR4J(self.data, start_date, end_date)
        self.params = [spotpy.parameter.Uniform('x1', 0.0, 200.0),
                       spotpy.parameter.Uniform('x2', 0.0, 1.0),
                       spotpy.parameter.Uniform('x3', 0.0, 100.0),
                       spotpy.parameter.Uniform('x4', 0.0, 10.0),
                       ]

    def parameters(self):
        return spotpy.parameter.generate(self.params)

    def simulation(self, vector):
        simulations = self.model.run(x1=vector[0], x2=vector[1], x3=vector[2], x4=vector[3])
        return simulations

    def evaluation(self):
        return self.data['flow_mm']

    def objectivefunction(self, simulation, evaluation):
        obj = spotpy.objectivefunctions.agreementindex(evaluation.values, simulation)
        return obj


def main():
    data_path = Path.cwd().parent / 'data'
    df = pd.read_pickle(data_path / 'L0123001.pkl')
    df.columns = ['date', 'precipitation', 'temperature', 'evapotranspiration', 'flow', 'flow_mm']
    df.index = df['date']
    print(df.head())

    # Setup calibration :
    spotpy_setup = SpotpySetup(df)

    # sampler = spotpy.algorithms.mc(spotpy_setup, dbname='MC_CMF', dbformat='csv')
    sampler = spotpy.algorithms.mle(spotpy_setup, dbname='MLE_CMF', dbformat='csv')
    # sampler = spotpy.algorithms.lhs(spotpy_setup, dbname='LHS_CMF', dbformat='csv')
    # sampler = spotpy.algorithms.sceua(spotpy_setup, dbname='SCEUA_CMF', dbformat='csv')
    # sampler = spotpy.algorithms.demcz(spotpy_setup, dbname='DE-MCz_CMF', dbformat='csv')
    # sampler = spotpy.algorithms.sa(spotpy_setup, dbname='SA_CMF', dbformat='csv')
    # sampler = spotpy.algorithms.rope(spotpy_setup, dbname='ROPE_CMF', dbformat='csv')

    sampler.sample(3000)


if __name__ == '__main__':
    main()
