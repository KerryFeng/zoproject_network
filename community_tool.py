import numpy as np
import pandas as pd
from copy import deepcopy

df = pd.read_excel("C:\\Users\\Kerry\\Desktop\\第三周课题\\Data\\basic_data.xlsx")
df2 = pd.read_csv("C:\\Users\\Kerry\\Desktop\\第三周课题\\Data\\fund_performance.csv", encoding = "gbk")
df2["日期"] = df2["日期"].apply(lambda x: x.replace('/', '-'))

index = {}
index2 = []
for _, row in df.iterrows():
    index[row["基金代码"]] = [row["基金名称"], row["基金经理"]]
    index2.append([row["基金经理"], row["基金代码"]])

date_list = ["2018-9-30", "2018-12-31", "2019-3-31", "2019-6-30", "2019-9-30", "2019-12-31", "2020-3-31", "2020-6-30", "2020-9-30"]

communities_dict = np.load('C:\\Users\\Kerry\\Desktop\\第三周课题\\Output\\communities.npy', allow_pickle = True).item()

def find_fund_communities(fund, date):
    fund_community = []
    if date in list(communities_dict.keys()):
        for community in communities_dict[date]:
            if fund in community and len(community) > 1:
                fund_community = deepcopy(community)
                fund_community.remove(fund)
                break
    return fund_community

def find_fund_communities_2q(fund, date):
    fund_communities = []
    if date in date_list:
        i = date_list.index(date)
        if i > 0:
            fund_communities = list(set(find_fund_communities(fund, date_list[i])).intersection(find_fund_communities(fund, date_list[i-1])))
    return fund_communities

def get_fund(name):
    if name in list(index.keys()):
        return [[name], 0]
    elif name in list(df["基金公司"]):
        return [list(df[df["基金公司"] == name]["基金代码"]), 1]
    else:
        result = []
        for i in range(len(index2)):
            if name in index2[i][0]:
                result.append(index2[i][1])
        return [result, 0]

def get_date(year, quarter):
    md = ""
    if quarter == "1":
        md = "-3-31"
    elif quarter == "2":
        md = "-6-30"
    elif quarter == "3":
        md = "-9-30"
    elif quarter == "4":
        md = "-12-31"
    return str(year) + md

def get_return(fund, date):
    the_yield = df2[(df2["基金代码"] == fund) & (df2["日期"] == date)]["区间收益率"]
    if len(the_yield) > 0:
        return round(the_yield.iloc[0],2)
    else:
        return "N/A"

if __name__ == "__main__":
    while True:
        name = input('输入基金代码、基金经理或基金公司：').strip()
        year = input('输入年份：').strip()
        quarter = input('输入季度：').strip()
        num = input('依据几个季度来寻找所在社群（输入1或2）：').strip()
        date = get_date(year, quarter)
        [names, flag] = get_fund(name)
        for name in names:
            if num == "2":
                the_community = find_fund_communities_2q(name, date)
            else:
                the_community = find_fund_communities(name, date)
            if len(the_community) >= flag:
                print("\n\n" + name + "（" + index[name][0] + "," + index[name][1] + "," + str(get_return(name, date)) + ")社群成员的信息如下（基金代码，基金名称，基金经理，当季收益率）:")
            for member in the_community:
                print(member, index[member][0], index[member][1], get_return(member, date))
        is_continue = input('\n\n是否继续(y/n)?')
        if is_continue != 'y':
            break
    