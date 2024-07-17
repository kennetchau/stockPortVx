import pandas as pd

df=pd.read_csv("data/data.csv")

dfVis = df.groupby(by=['Symbol']).sum()
print(dfVis)
