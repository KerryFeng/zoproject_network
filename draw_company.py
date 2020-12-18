import pandas as pd
import networkx as nx
import numpy as np
from copy import deepcopy
from networkx.algorithms.community import greedy_modularity_communities
import matplotlib.pyplot as plt

df = pd.read_excel("Data\\basic_data.xlsx", encoding = "gbk")

fund_index = {}
for _, row in df.iterrows():
    fund_index[row["基金代码"]] = row["基金名称"]
    
company = "华夏基金"
company_funds = list(set(df[df["基金公司"] == company]["基金代码"]))

# date_list = ["2019/12/31", "2020/3/31", "2020/6/30", "2020/9/30"]
date_list = ["2019/12/31"]

for date in date_list:
    d = np.load('Output\\data_' + date.replace('/', '-') + '.npy', allow_pickle = True).item()
    
    # 搭建网络
    G = nx.Graph()
    for fund1 in list(d.keys()):
        G.add_node(fund1)
        for fund2 in d[fund1].keys():
            G.add_edge(fund1, fund2)
    
    # 画图     
    for fund in list(set(company_funds).intersection(set(G.nodes()))):
        s = list(G.neighbors(fund))
        s.append(fund)
        H = G.subgraph(s).copy()
        # for node in H.nodes():
        #     H.nodes[node]['name'] = node[:-3]
        if fund == "166009.OF":
            nx.draw(H, node_size = 1, edge_color = "green")
        else:
            # pos = nx.spring_layout(H)
            nx.draw(H, node_color = 'b', with_labels = True, edge_color = 'r', font_size = 8, node_size = 0)
            for node in H.nodes():
                print(str(node) + ": " + fund_index[node])
            # node_labels = nx.get_node_attributes(H, 'name')
            # nx.draw_networkx_labels(H, pos, labels = node_labels)
        plt.savefig("Pictures\\company2\\" + fund + ".png")
        plt.close()
        
    
