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

    def timeline(self):
        tline = []
        df = self.df
        totalFrames = df.shape[0]
        i = 0
        while (i) < totalFrames:
            frame = {}
            fp=df["nrFP"].iat[i]
            endTime = df["name"].iat[i]
            frame["start"] = int(endTime)
            frame["end"] = int(endTime) + 5
            frame["resize"]=False
            frame["drag"]=False
            frame["loop"] = False
            if fp > 1:
                color = "rgba(249,145,163, 0.4)"
            elif fp > 0:
                color = "rgba(168,156,200, 0.4)"
            else:
                color = "rgba(151,176,248, 0.4)"
            i = i + 1
            frame["color"]=color
            tline.append(frame)
        return tline


