import pandas as pd

class gazeScorer:

    def __init__(self, dataframe):
        self.df = dataframe

    def score(self):
       df=self.df
       totalFrames= df.shape[0]
       counts = dict(df['gaze'].value_counts())
       if "Front" in counts:
           front = counts["Front"]
       else:
           front = 0
       if "Right" in counts:
           right = counts["Right"]
       else:
           right = 0
       if "Left" in counts:
           left = counts["Left"]
       else:
           left = 0
       if "Up" in counts:
           up = counts["Up"]
       else:
           up = 0
       if "Down" in counts:
           down = counts["Down"]
       else:
           down = 0
       if "Back" in counts:
           back = counts["Back"]
       else:
           back = 0
       if "None" in counts:
           none = counts["None"]
       else:
           none = 0
       totalFrames=totalFrames-none
       if(totalFrames>0):
          frontPer = front / totalFrames
       else:
          frontPer=0

       if frontPer>0.75:
           score=5
       elif frontPer>0.50:
           score=4
       elif frontPer>0.30:
           score=3
       elif frontPer>0.20:
           score=2
       else:
           score=1

       return score

    def timeline(self):
        fs=10
        tline=[]
        df = self.df
        totalFrames = df.shape[0]
        i=0
        while (i+fs)<totalFrames:
            frame= {}
            window=df[(df["frame"]>=i) & (df["frame"]<i+fs)]
            modeValue=window["gaze"].mode().iat[0]
            print(i,i+fs,modeValue)
            frame["content"]=modeValue
            frame["frame"]=i/fs
            frame["group"]=0
            frame["start"]=i/2
            frame["end"]=(i+fs)/2
            if modeValue=="Front":
                frame["subgroup"]= "sg_cor"
                frame["className"]="correct"
            else:
                frame["subgroup"] = "sg_inc"
                frame["className"] = "incorrect"
            i = i + fs
            tline.append(frame)
        return tline


