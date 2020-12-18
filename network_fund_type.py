import pandas as pd
import numpy as np
import networkx as nx
from copy import deepcopy
import statsmodels.api as sm

df = pd.read_csv("Data\\positions_change.csv", encoding = "gbk")

fund_type = pd.read_csv("Data\\2020中报风格属性.csv", encoding = "gbk")
date = "2020/6/30"

# fund_type = pd.read_csv("Data\\2019年报风格属性.csv", encoding = "gbk")
# date = "2019/12/31"

def regression(Y, X): # 多元线性回归
    Xs = X[0]
    for i in range(1, len(X)):
        Xs = np.column_stack((Xs, X[i]))
    model = sm.OLS(Y, sm.add_constant(Xs))
    regression = model.fit()
    return regression

res1 = {} # 模型1
res2 = {} # 模型2

d = np.load('Output\\data_' + date.replace('/', '-') + '.npy', allow_pickle = True).item()
funds = list(d.keys())
   
# 搭建网络
G = nx.Graph()
for fund1 in funds:
    G.add_node(fund1)
    for fund2 in d[fund1].keys():
        G.add_edge(fund1, fund2)

# 剔除网络中少于6个节点的基金
funds2 = []
for fund in funds:
    if len(list(G.neighbors(fund))) < 6:
        funds2.append(fund)
for fund in funds2:
    funds.remove(fund)
    G.remove_node(fund)

# 验证网络存在性
df2 = deepcopy(df[(df["日期"] == date) & (df["基金代码"].isin(funds))])

df2["首次重仓"] = df2.apply(lambda x: 1 if (x["重仓股比例_x"] == 0 and x["重仓股比例_y"] > 0) else 0, axis = 1)

dict1 = {}
dict2 = {}

for fund in funds:
    dict1[fund] = {}
    dict2[fund] = {}
    stocks = list(df2[df2["基金代码"] == fund]["重仓股代码"])
    fund_network = list(G.neighbors(fund))
    for stock in stocks:
        stock_owners = df2[(df2["重仓股代码"] == stock) & (df2["基金代码"] != fund)]
        network_stock_owners = stock_owners[stock_owners["基金代码"].isin(fund_network)]
        dict1[fund][stock] = sum(network_stock_owners["仓位变化"]) / len(fund_network)
        dict2[fund][stock] = sum(stock_owners["仓位变化"]) / (len(funds) - 1)

df2["网络平均"] = df2.apply(lambda x: dict1[x["基金代码"]][x["重仓股代码"]], axis = 1)
df2["首次重仓网络平均"] = df2.apply(lambda x: x["首次重仓"] * x["网络平均"], axis = 1)
df2["所有基金平均"] = df2.apply(lambda x: dict2[x["基金代码"]][x["重仓股代码"]], axis = 1)

df3 = pd.merge(df2, fund_type, on = "基金代码")

res1 = pd.DataFrame()
res2 = pd.DataFrame()

for the_type in ["价值", "成长", "平衡"]:
    the_df = df3[df3["风格属性"] == the_type]
    # 模型1
    regression1 = regression(the_df["仓位变化"], [the_df["网络平均"], the_df["所有基金平均"]])
    coefficients1 = regression1.params
    pvalues1 = regression1.pvalues
    res1 = res1.append([{"fund_type": the_type, "const": coefficients1["const"], 
                        "network_average": coefficients1["x1"], "n_pvalue": pvalues1["x1"], 
                        "industry_average": coefficients1["x2"], "i_pvalue": pvalues1["x2"], 
                        "fvalue": regression1.fvalue, "f_pvalue": regression1.f_pvalue}], ignore_index=True)
    # 模型2
    regression2 = regression(the_df["仓位变化"], [the_df["网络平均"], the_df["首次重仓网络平均"], the_df["所有基金平均"]])
    coefficients2 = regression2.params
    pvalues2 = regression2.pvalues
    res2 = res2.append([{"fund_type": the_type, "const": coefficients2["const"], 
                        "network_average": coefficients2["x1"], "n_pvalue": pvalues2["x1"],
                        "first_network_average": coefficients2["x2"], "fi_pvalue": pvalues2["x2"], 
                        "industry_average": coefficients2["x3"], "i_pvalue": pvalues2["x3"], 
                        "fvalue": regression2.fvalue, "f_pvalue": regression2.f_pvalue}], ignore_index=True)

    
    


