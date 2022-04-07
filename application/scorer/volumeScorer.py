import pandas as pd

class volumeScorer:

    def __init__(self, dataframe):
        self.df = dataframe

    def score(self):
       df=self.df
       totalFrames= df.shape[0]
       print(df.columns)
       if totalFrames>0:
           meanVolume = df["power"].mean()

       if meanVolume>50:
           score=5
       elif meanVolume>45:
           score=4
       elif meanVolume>40:
           score=3
       elif meanVolume>35:
           score=2
       else:
           score=1

       return score

    def timeline(self):
        tline = []
        df = self.df
        totalFrames = df.shape[0]
        i = 0
        while (i) < totalFrames:
            frame = {}
            meanVolume=df["volume"].iat[i]
            endTime=df["time"].iat[i]
            frame["start"] = int(endTime-5)
            frame["end"] = int(endTime)
            frame["resize"]=False
            frame["drag"]=False
            frame["loop"] = False
            if meanVolume > 50:
                color = "rgba(151,176,248, 0.4)"
            elif meanVolume > 45:
                color = "rgba(151,176,248, 0.4)"
            elif meanVolume > 40:
                color = "rgba(168,156,200, 0.4)"
            elif meanVolume > 35:
                color = "rgba(168,156,200, 0.4)"
            else:
                color = "rgba(249,145,163, 0.4)"
            i = i + 1
            frame["color"]=color
            tline.append(frame)
        return tline