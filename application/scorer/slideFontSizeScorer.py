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