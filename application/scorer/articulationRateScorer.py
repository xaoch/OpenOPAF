import pandas as pd


class articulationRateScorer:

    def __init__(self, dataframe):
        self.df = dataframe

    def score(self):
        df = self.df
        totalFrames = df.shape[0]
        if totalFrames > 0:
            meanSpeed = df["speechrate"].mean()
        meanSpeed=meanSpeed* 60 / 1.66
        if meanSpeed > 200:
            score = 1
        elif meanSpeed > 180:
            score = 2
        elif meanSpeed > 150:
            score = 3
        elif meanSpeed > 120:
            score = 4
        elif meanSpeed > 100:
            score = 5
        elif meanSpeed > 80:
            score = 4
        elif meanSpeed > 50:
            score = 3
        elif meanSpeed > 20:
            score = 2
        else:
            score = 1

        return score


    def timeline(self):
        tline = []
        df = self.df
        totalFrames = df.shape[0]
        i = 0
        while (i) < totalFrames:
            frame = {}
            meanSpeed=df["speechrate"].iat[i]
            meanSpeed=meanSpeed*60 / 1.66
            endTime = df["name"].iat[i]
            frame["start"] = int(endTime)
            frame["end"] = int(endTime) + 5
            frame["resize"]=False
            frame["drag"]=False
            frame["loop"] = False
            if meanSpeed > 200:
                color = "rgba(249,145,163, 0.4)"
            elif meanSpeed > 180:
                color = "rgba(168,156,200, 0.4)"
            elif meanSpeed > 150:
                color = "rgba(168,156,200, 0.4)"
            elif meanSpeed > 120:
                color = "rgba(151,176,248, 0.4)"
            elif meanSpeed > 100:
                color = "rgba(151,176,248, 0.4)"
            elif meanSpeed > 80:
                color = "rgba(151,176,248, 0.4)"
            elif meanSpeed > 50:
                color = "rgba(168,156,200, 0.4)"
            elif meanSpeed > 20:
                color = "rgba(168,156,200, 0.4)"
            else:
                color = "rgba(249,145,163, 0.4)"
            i = i + 1
            frame["color"]=color
            tline.append(frame)
        return tline


