import pandas as pd
import networkx as nx
import math
import numpy as np
from copy import deepcopy
import statsmodels.api as sm
from scipy.stats import t
import matplotlib.pyplot as plt

df = pd.read_csv("Data\\positions_change.csv", encoding = "gbk")
pf = pd.read_csv("Data\\fund_performance.csv", encoding = "gbk")
# af = pd.read_excel("Data\\basic_data.xlsx", encoding = "gbk")

date_list = ["2018/12/31", "2019/3/31", "2019/6/30", "2019/9/30", "2019/12/31", "2020/3/31", "2020/6/30", "2020/9/30"]
# date_list = ["2020/9/30"]

def degree(G):
    s = []
    for fund in G.nodes():
        s.append(len(list(G.neighbors(fund))))
    print("最大度：", max(s))
    print("平均度：", sum(s)/len(s))
    return s

def compute_all_around(G):
    all_around = pd.DataFrame()
    k_core = nx.core_number(G)
    betweenness = nx.betweenness_centrality(G)
    all_around["fund"] = list(k_core.keys())
    all_around["k_core"] = all_around.apply(lambda x: k_core[x["fund"]], axis = 1) 
    all_around["degree"] = all_around.apply(lambda x: G.degree(x["fund"]), axis = 1)
    all_around["betweenness"] = all_around.apply(lambda x: betweenness[x["fund"]], axis = 1) 
    all_around["k_core"] = all_around["k_core"].apply(lambda x: x / sum(all_around["k_core"]) * 100)
    all_around["degree"] = all_around["degree"].apply(lambda x: x / sum(all_around["degree"]) * 100)
    all_around["betweenness"] = all_around["betweenness"].apply(lambda x: x / sum(all_around["betweenness"]) * 100)
    all_around["all_around"] = all_around.apply(lambda x: math.sqrt(x["k_core"] * x["k_core"] + x["degree"] * x["degree"] + x["betweenness"] * x["betweenness"]), axis = 1)
    all_around["clustering"] = all_around.apply(lambda x: nx.clustering(G, x["fund"]), axis = 1)
    return all_around[["fund", "k_core", "betweenness", "degree", "all_around", "clustering"]].sort_values(by = "all_around", ascending = False)

def delete_nodes(G): # 删除网络中少于6个节点的基金
    G2 = deepcopy(G)
    nodes2 = []
    for node in G2.nodes():
        if len(list(G2.neighbors(node))) < 6:
            nodes2.append(node)
    for node2 in nodes2:
        G2.remove_node(node2)
    return G2

def regression(Y, X): # 多元线性回归
    Xs = X[0]
    for i in range(1, len(X)):
        Xs = np.column_stack((Xs, X[i]))
    model = sm.OLS(Y, sm.add_constant(Xs))
    regression = model.fit()
    return regression

def compute_cor(df, x, y):
    cor = df[[x, y]].corr(method='pearson')[x][y]
    n = len(df) - 1
    T = abs(cor) * math.sqrt((n - 2) / (1 - cor * cor))
    p = (1 - t.cdf(T, n-2)) * 2
    return [cor, p]

result = pd.DataFrame()

for date in date_list:
    d = np.load('Output\\data_' + date.replace('/', '-') + '.npy', allow_pickle = True).item()
    
    # 搭建网络
    G = nx.Graph()
    for fund1 in list(d.keys()):
        G.add_node(fund1)
        for fund2 in d[fund1].keys():
            G.add_edge(fund1, fund2)

    # 查看网络参数
    print("节点数", G.number_of_nodes())     
    print("边数：", G.number_of_edges())
    print("网络密度：", nx.density(G))
    s = degree(G)
    print("支配数占比：", len(nx.dominating_set(delete_nodes(G))) / delete_nodes(G).number_of_nodes())
    all_around = compute_all_around(delete_nodes(G))
    
    pf2 = pf[pf["日期"] == date]
    
    the_df = pd.merge(pf2, all_around, left_on = "基金代码", right_on = "fund")
    
    # if date == "2020/9/30":
    #     the_df2 = pd.merge(the_df, af, on = "基金代码")
    #     print(compute_cor(the_df2, "all_around", "任职年限"))
    
    # 收益率作回归
    for centrality in ["k_core", "betweenness", "degree", "all_around", "clustering"]:
        regression1 = regression(the_df["区间收益率"], [the_df[centrality], the_df["区间波动率"], the_df["成立年限"], the_df["上一期基金规模"]])
        coefficients1 = regression1.params
        pvalues1 = regression1.pvalues
        # print(compute_cor(the_df, "区间收益率", "all_around"))
        # plt.scatter(the_df["all_around"], the_df["区间收益率"])
        result = result.append([{"date": date, "index": centrality, 
                                 "coefficient": coefficients1["x1"], "pvalue": pvalues1["x1"], 
                                 "volatility": coefficients1["x2"], "vol_pvalue": pvalues1["x2"], 
                                 "age": coefficients1["x3"], "age_pvalue": pvalues1["x3"], 
                                 "size": coefficients1["x4"], "size_pvalue": pvalues1["x4"],
                                 "fvalue": regression1.fvalue, "f_pvalue": regression1.f_pvalue}], ignore_index=True)
        
        # Sharpe作回归
        # regression2 = regression(the_df["Sharpe"], [the_df["all_around"], the_df["成立年限"], the_df["上一期基金规模"]])
        # coefficients2 = regression2.params
        # pvalues2 = regression2.pvalues
    