import pandas as pd

df = pd.read_csv("Data\\positions.csv", encoding = "gbk")

date_list = ["2019/9/30", "2019/12/31", "2020/3/31", "2020/6/30", "2020/9/30"]

res = pd.DataFrame()

for i in range(1, len(date_list)):
    df1 = df[df["日期"] == date_list[i-1]]
    df2 = df[df["日期"] == date_list[i]]
    df12 = pd.merge(df1, df2, on = ["基金代码", "基金名称", "重仓股代码"], how = "outer")[["基金代码", "基金名称", "重仓股代码", "重仓股比例_x", "重仓股比例_y"]]
    df12.fillna(0, inplace = True)
    df12["仓位变化"] = df12["重仓股比例_y"] - df12["重仓股比例_x"]
    df12["日期"] = date_list[i]
    df12 = df12.sort_values(by = "基金代码", ascending = True)
    res = pd.concat([res, df12])
    
res.to_csv("Data\\positions_change.csv", index = 0, encoding = "gbk")