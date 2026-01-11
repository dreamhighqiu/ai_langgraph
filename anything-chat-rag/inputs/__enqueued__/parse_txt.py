# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import scipy.signal as signal
from predict_model import predict
import json

#解析txt文件，得到PPG原始数据
def parse_txt(requestJson):
    # 解析txt文件，提取data字段
    ppg_data = []
    timestamp = []
    # with open(file_path, 'r', encoding='utf-8') as file:
    #     lines = file.readlines()
    #     for line in lines:
    #         if(line.rfind('"data":"')>0):
    #             match_data = line[(line.rfind('"data":"')+8):line.rfind('","ident"')]
    #             timestamp_data = line[(line.rfind('"timestamp":')+12):line.rfind(',"dataStartTime"')]
    #             if(match_data):
    #                 timestamp.append(timestamp_data)
    #                 ppg_data.append(match_data)
    for d in requestJson.get("dataList"):
        ppg_data.append(d.get('data'))
        timestamp.append(d.get('timestamp'))

    # ppg_data.append(requestJson.get('data'))
    # timestamp.append(requestJson.get('timestamp'))

    df1 = pd.DataFrame({'timestamp':timestamp, 'ppg_data':ppg_data})
    df1 = df1.drop_duplicates(['timestamp', 'ppg_data']) # 对日志数据去重
    df1 = df1.reset_index(drop=True)
    # df1.to_excel("../parseData/ppg_data.xlsx", index = False)
    
    # 按逗号分割data字段数据，得到PPG原始数据
    ppg_rawData = []
    for i in range(0,len(df1)):
        data = df1.loc[i, 'ppg_data']
        data_split = data.split(',')
        data_type_convert = [int(i) for i in data_split]
        # data_valid = data_type_convert[0:data_type_convert[-1]]
        ppg_rawData.extend(data_type_convert)
    df2 = pd.DataFrame({'ppg_rawData':ppg_rawData})
    # df2.to_excel("../parseData/ppg_rawData.xlsx", index = False)
    
    return df2

# 基于PPG原始数据，计算其RRI
def calculate_rri(df, fs):    
    # 检测PPG波峰：使用Python包内置函数，scipy.signal.find_peaks检测PPG波峰
    peak_inds=signal.find_peaks(df['ppg_rawData'], distance=int(2*fs/3))
    ppg_peak_inds = peak_inds[0]  # 波峰索引
    print(len(ppg_peak_inds))
    
    # 计算RR间期
    RRIdata = []
    for i in range(1, len(ppg_peak_inds)):
        RRIdata.append((ppg_peak_inds[i] - ppg_peak_inds[i-1])/fs*1000)
    RRIdata = pd.DataFrame({'RRI':RRIdata})
    
    # 基于RRI列计算time（time = RRI/1000的累加和）
    RRI_list = list(RRIdata['RRI'])
    if len(RRI_list) > 0:
        time_list = [0]*len(RRI_list)
        time_list[0] = RRI_list[0]/1000
        for i in range(1,len(time_list)):
            time_list[i] = time_list[i-1] + RRI_list[i]/1000
        RRIdata['time'] = time_list
    # RRIdata.to_excel("../resultData/RRIdata.xlsx", index = False)
    
    return RRIdata

# if __name__ == '__main__':
#     # txt文件路径
#     file_path = '../ppg_rawData/ppg-20240407.txt'
#     # 解析txt文件，得到PPG原始数据
#     df = parse_txt(file_path)
#     # 基于PPG原始数据，计算其RRI
#     RRIdata = calculate_rri(df, fs = 20)
#     # 调用情绪指数模型进行预测
#     predict_result = predict(RRIdata)
#
#     print("predict_result: ", predict_result)

if __name__ == '__main__':
    # txt文件路径
    file_path = '../test_1min.json'
    # 解析txt文件，得到PPG原始数据

    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    df = parse_txt(data)
    # 基于PPG原始数据，计算其RRI
    RRIdata = calculate_rri(df, fs = 88)
    # 调用情绪指数模型进行预测
    predict_result = predict(RRIdata, rri_num=60)

    print("predict_result: ", predict_result)

