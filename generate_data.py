import pandas as pd
from copy import deepcopy

df = pd.read_excel("Data\\basic_data.xlsx")

df3 = pd.DataFrame()

for i in range(1,11):
    df2 = deepcopy(df)
    df2["重仓位"] = i
    df3 = pd.concat([df3, df2])

# date_list = ["2019-09-30", "2019-12-31","2020-03-31", "2020-06-30", "2020-09-30"]
date_list = ["2017-03-31", "2017-06-30","2017-09-30", "2017-12-31",
             "2018-03-31", "2018-06-30","2018-09-30", "2018-12-31", 
             "2019-03-31", "2019-06-30"]

df5 = pd.DataFrame()

for date in date_list:
    df4 = deepcopy(df3)
    df4["日期"] = date
    df5 = pd.concat([df5, df4])
    
df5.to_csv("Data\\positions2.csv", index = 0, encoding = "gbk")

