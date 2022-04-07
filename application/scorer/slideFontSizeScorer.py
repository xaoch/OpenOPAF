import pandas as pd

class slideFontSizeScorer:

    def __init__(self, dataframe):
        self.df = dataframe

    def score(self):
       df=self.df
       totalSlides= df.shape[0]
       counts = dict(df['font_size'].value_counts())
       if "Ok" in counts:
           ok = counts["Ok"]
       else:
           ok = 0
       if "Small" in counts:
           small = counts["Small"]
       else:
           small = 0
       if "Tiny" in counts:
           tiny = counts["Tiny"]
       else:
           tiny = 0
       if "No Font" in counts:
           none = counts["No Font"]
       else:
           none = 0
       totalSlides=totalSlides-none
       if(totalSlides>0):
          okPer = ok / totalSlides
       else:
          okPer=0

       if okPer>0.75:
           score=5
       elif okPer>0.50:
           score=4
       elif okPer>0.30:
           score=3
       elif okPer>0.20:
           score=2
       else:
           score=1

       return score

    def timeline(self):
        tline=[]
        df = self.df
        totalSlides = df.shape[0]
        i=0
        while i<totalSlides:
            frame= {}
            frame2={}
            fontValue = df['font_size'].iat[i]
            lengthValue = df['text_length'].iat[i]
            frame["content"]=fontValue
            frame["frame"]=i
            frame["group"]=0
            frame["start"]=i
            frame["end"]=i+1
            if fontValue=="Ok":
                frame["subgroup"]= "sg_cor"
                frame["className"]="correct"
            else:
                frame["subgroup"] = "sg_inc"
                frame["className"] = "incorrect"
            frame2["content"] = lengthValue
            frame2["frame"] = i
            frame2["group"] = 1
            frame2["start"] = i
            frame2["end"] = i + 1
            if lengthValue == "Ok":
                frame2["subgroup"] = "sg_cor"
                frame2["className"] = "correct"
            else:
                frame2["subgroup"] = "sg_inc"
                frame2["className"] = "incorrect"
            i = i + 1
            tline.append(frame)
            tline.append(frame2)

        return tline