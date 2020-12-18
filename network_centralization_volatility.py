import pandas as pd
import networkx as nx
import math
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from scipy.stats import t

df = pd.read_csv("Data\\positions.csv", encoding = "gbk")
sf = pd.read_csv("Data\\stocks_volatility.csv", encoding = "gbk")

date_list = ["2019/9/30", "2019/12/31", "2020/3/31", "2020/6/30"]
# date_list = ["2019/12/31"]

# sample_space = list(set(df["重仓股代码"]))

def compute_centralization(G):
    connections = []
    for node in G.nodes():
        connections.append(G.degree(node))
    cv = np.std(np.array(connections)) / np.mean(np.array(connections))
    return cv

def compute_cor(df, x, y):
    cor = df[[x, y]].corr(method='pearson')[x][y]
    n = len(df) - 1
    T = abs(cor) * math.sqrt((n - 2) / (1 - cor * cor))
    p = (1 - t.cdf(T, n-2)) * 2
    return [cor, p]

def regression(Y, X): # 多元线性回归
    Xs = X[0]
    for i in range(1, len(X)):
        Xs = np.column_stack((Xs, X[i]))
    model = sm.OLS(Y, sm.add_constant(Xs))
    regression = model.fit()
    return regression

for date in date_list:
    d = np.load('Output\\data_' + date.replace('/', '-') + '.npy', allow_pickle = True).item()
    
    df2 = df[(df["日期"] == date) & (df["重仓股比例"] >= 5)][["基金代码","基金名称","重仓股代码"]]
    sf2 = sf[sf["start_date"] == date]
    
    # 搭建基金网络(剔除孤立点)
    G = nx.Graph()
    for fund1 in list(d.keys()):
        for fund2 in d[fund1].keys():
            G.add_edge(fund1, fund2)
    
    # 搭建股票网络
    cv_df = pd.DataFrame()
    stocks = list(set(df2["重仓股代码"]))
    for stock in stocks:
        df3 = df2[df2["重仓股代码"] == stock]
        stock_funds = []
        stock_owners = list(set(df3["基金代码"]).intersection(set(G.nodes())))
        for fund in stock_owners:
            stock_funds.append(fund)
            stock_funds.extend(list(G.neighbors(fund)))
        stock_network = G.subgraph(list(set(stock_funds))).copy()
        # if stock_network.number_of_nodes() > 0 and stock_network.number_of_nodes() < 25:
        #     nx.draw(stock_network, node_size = 50)
        #     plt.savefig("Pictures\\stocks_network\\" + stock + ".png")
        #     plt.close()
        if stock_network.number_of_nodes() >= 6:
            stock_cv = compute_centralization(stock_network)
            cv_df = cv_df.append([{"stock": stock, "cv": stock_cv}], ignore_index=True)
    
    # 相关性分析
    the_df = pd.merge(cv_df, sf2, on = "stock")[["stock", "cv", "idiosyncratic_volatility"]] 
    print(compute_cor(the_df, "cv", "idiosyncratic_volatility"))