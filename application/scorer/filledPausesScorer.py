import pandas as pd


class filledPausesScorer:

    def __init__(self, dataframe):
        self.df = dataframe

    def score(self):
        df = self.df
        totalFrames = df.shape[0]
        if totalFrames > 0:
            meanFP = df["nrFP"].mean()

        if meanFP > 1:
            score = 1
        elif meanFP > 0.8:
            score = 2
        elif meanFP > 0.5:
            score = 3
        elif meanFP > 0.25:
            score = 4
        else:
            score = 5

        return score




