import pandas as pd
import numpy as np

df = pd.read_csv("Data\\positions.csv", encoding = "gbk")

date_list = ["2019/9/30", "2019/12/31", "2020/3/31", "2020/6/30", "2020/9/30"]
date_list = ["2018/9/30", "2018/12/31", "2019/3/31", "2019/6/30"]
# date_list = ["2019/12/31"]

limit = 10

for date in date_list:
    d = {}
    d2 = {}
    
    df2 = df[df["日期"] == date][["基金代码","基金名称","重仓股代码","重仓股比例"]]
    stocks = list(set(df2["重仓股代码"]))
    funds = list(set(df2["基金代码"]))
    for fund in funds:
        d[fund] = {}
        d2[fund] = {}
    count = 1
    for stock in stocks:
        print("第" + str(count) + "支股票：" + stock)
        df3 = df2[df2["重仓股代码"] == stock]
        sfunds = list(df3["基金代码"])
        for fund1 in sfunds:
            for fund2 in sfunds:
                if fund1 == fund2:
                    continue
                d[fund1][fund2] = d[fund1].get(fund2, 0) + df3[df3["基金代码"] == fund1]["重仓股比例"].iloc[0]
        count += 1
    for fund1 in d:
        for fund2 in d[fund1]:
            if d[fund1][fund2] >= limit and d[fund2][fund1] >= limit:
                d2[fund1][fund2] = d[fund1][fund2]
            del d[fund2][fund1]

    np.save('Output\\data_' + date.replace('/', '-') + '.npy', d2)
