import pandas as pd

class postureScorer:

    def __init__(self, dataframe):
        self.df = dataframe

    def score(self):
       df=self.df
       totalFrames= df.shape[0]
       counts = dict(df['posture'].value_counts())
       if "Open" in counts:
           open = counts["Open"]
       else:
           open = 0
       if "Closed_Torso_Back" in counts:
           closed_torso_back = counts["Closed_Torso_Back"]
       else:
           closed_torso_back = 0
       if "Closed_Torso_Side" in counts:
           closed_torso_side = counts["Closed_Torso_Side"]
       else:
           closed_torso_side = 0
       if "Hands_Back" in counts:
           hands_back = counts["Hands_Back"]
       else:
           hands_back = 0
       if "Hands_Pockets" in counts:
           hands_pockets = counts["Hands_Pockets"]
       else:
           hand_pockets = 0
       if "Hands_Face" in counts:
           hands_face = counts["Hands_Face"]
       else:
           hands_face = 0
       if "Closed_Hands_Inside" in counts:
           closed_hands_inside = counts["Closed_Hands_Inside"]
       else:
           closed_hands_inside = 0
       if "None" in counts:
           none = counts["None"]
       else:
           none = 0
       totalFrames=totalFrames-none
       if(totalFrames>0):
          openPer = open / totalFrames
       else:
          openPer=0

       if openPer>0.75:
           score=5
       elif openPer>0.50:
           score=4
       elif openPer>0.30:
           score=3
       elif openPer>0.20:
           score=2
       else:
           score=1
       return score

    def timeline(self):
        fs = 10
        tline=[]
        df = self.df
        totalFrames = df.shape[0]
        i=0
        while (i+fs)<totalFrames:
            frame= {}
            window=df[(df["frame"]>=i) & (df["frame"]<i+fs)]
            modeValue=window["posture"].mode().iat[0]
            print(i,i+fs,modeValue)
            frame["content"]=modeValue
            frame["group"]=0
            frame["frame"] = i / fs
            frame["start"]=i/2
            frame["end"]=(i+fs)/2
            if modeValue=="Open":
                frame["subgroup"]= "sg_cor"
                frame["className"]="correct"
            else:
                frame["subgroup"] = "sg_inc"
                frame["className"] = "incorrect"
            i = i + fs
            tline.append(frame)
        return tline
