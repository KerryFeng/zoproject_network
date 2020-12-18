import pandas as pd
import networkx as nx
import numpy as np
from copy import deepcopy
from networkx.algorithms.community import greedy_modularity_communities
import matplotlib.pyplot as plt

df = pd.read_csv("Data\\positions_change.csv", encoding = "gbk")

date_list = ["2018-9-30", "2018-12-31", "2019-3-31", "2019-6-30", "2019-9-30", "2019-12-31", "2020-3-31", "2020-6-30", "2020-9-30"]

# date_list = ["2020/9/30"]

def delete_nodes(G): # 删除网络中少于6个节点的基金
    G2 = deepcopy(G)
    nodes2 = []
    for node in G2.nodes():
        if len(list(G2.neighbors(node))) < 6:
            nodes2.append(node)
    for node2 in nodes2:
        G2.remove_node(node2)
    return G2

def find_communities(G, d, density):
    if G.number_of_edges() != 0:
        cs = greedy_modularity_communities(G)
        if len(cs) != 1:
            Hs = []
            for c in cs:
                H = G.subgraph(list(set(c))).copy()
                if nx.density(H) < density:
                    Hs.extend(find_communities(H, d, density))
                else:
                    Hs.append(H)
            return Hs
        else:
            return [G]
    else:
        return [G]

communities_dict = {}

for date in date_list:
    d = np.load('Output\\data_' + date.replace('/', '-') + '.npy', allow_pickle = True).item()
    
    # 搭建网络
    G = nx.Graph()
    for fund1 in list(d.keys()):
        G.add_node(fund1)
        for fund2 in d[fund1].keys():
            G.add_edge(fund1, fund2)
    
    # 查找社群
    communities = find_communities(G, d, 0.6)
    
    communities_list = []
    for community in communities:
        # print(nx.density(community))
        communities_list.append(list(community.nodes()))
    
    # i = 1    
    # for community in communities:
    #     nx.draw(community, node_color = "black", edge_color = "green", node_size = 15)
    #     plt.savefig("Pictures\\communities\\" + str(i) + ".png")
    #     plt.close()
    #     i += 1
        
    communities_dict[date.replace('/', '-')] = communities_list
    
np.save('Output\\communities.npy', communities_dict)
    