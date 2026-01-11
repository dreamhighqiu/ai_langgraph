# -*- coding: utf-8 -*-
import time
import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
import joblib
from hrvanalysis import remove_outliers
from hrvanalysis import remove_ectopic_beats
from hrvanalysis import interpolate_nan_values
from hrvanalysis import get_time_domain_features
from hrvanalysis import get_geometrical_features
from hrvanalysis import get_frequency_domain_features
from hrvanalysis import get_csi_cvi_features
from hrvanalysis import get_poincare_plot_features
from hrvanalysis import get_sampen
import os


#模型预测，输入是DataFrame
def predict(RRIdata, rri_num):
    starttime = time.time()
    start_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    # arg1 = saveRRI_path
    # trainData_path = '../trainData/'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

    # trainData_path = os.path.abspath(os.path.join(current_dir, os.pardir))+"/trainData/"

    # model_path = '../model/'
    # model_path = os.path.abspath(os.path.join(current_dir, os.pardir))+"/model/"

    model_return_dict = {} #存储返回值
    # RRIdata = pd.read_excel(saveRRI_path, header=0)
    try:
        ########################################################
        #一、计算hrv特征
        obj_dict = {} #hrv特征等数据存储在字典
        # rri_num = 60 #设置500个rri为一个片段
        RRIdata['RRI'] = RRIdata['RRI'].astype(int)
        rri = list(RRIdata['RRI'])
        rri2str_list = []
        rri_list = []
        n = int(len(rri)/rri_num) #分割的片段数
        for k in range(n):
            tmp_rri = rri[(k*rri_num):((k+1)*rri_num)]
            tmp_str = '|'.join(map(str, tmp_rri))
            rri2str_list.append(tmp_str)
            rri_list.append(tmp_rri)
        
        for j in range(len(rri2str_list)):
            ### 1.通过hrvanalysis库提取hrv特征
            rr_intervals_list = rri_list[j]
        
            # 使用Python-hrvanalysis库挖掘心电信号特征（hrv特征）
            # （1）离群值和异常值删除
            rr_intervals_without_outliers = remove_outliers(rr_intervals=rr_intervals_list,  
                                                            low_rri=300, high_rri=2000)
            # 将离群的rr-interval值删除，并用线性插值的方法添加新值
            interpolated_rr_intervals = interpolate_nan_values(rr_intervals=rr_intervals_without_outliers,
                                                               interpolation_method="linear")
            # 从RR-interval心电信号中，采用malik方法删除异常值，即将值置为nan
            nn_intervals_list = remove_ectopic_beats(rr_intervals=interpolated_rr_intervals, method="malik")
            # 使用线性插值的方法替换nan
            interpolated_nn_intervals = interpolate_nan_values(rr_intervals=nn_intervals_list)
            
            # （2）RR-interval特征提取
            #返回包含HRV分析的时域特征字典，通常用于24h的长期记录，也有些研究在2-5min的短期记录
            nn_intervals_list = interpolated_nn_intervals
            time_domain_features = get_time_domain_features(nn_intervals_list)
            
            #返回返回几何时域特征字典，记录的数据必须在20min-24h内
            geometrical_features = get_geometrical_features(nn_intervals_list)
            
            # 返回包含用于HRV分析的频域特征的字典，必须在2-5min的窗口内使用
            frequency_domain_features = get_frequency_domain_features(nn_intervals_list)
            
            # 返回来自非线性域的3个用于HRV分析的特征字典，必须在30、50、100秒的RR-interval中使用
            csi_cvi_features = get_csi_cvi_features(nn_intervals_list)
        
            # 返回包含非线性域的3个特征字典，用于HRV分析，必须在5分钟的短期窗口使用
            poincare_plot_features = get_poincare_plot_features(nn_intervals_list)
            
            # 计算给定数据的样本熵，必须在一分钟内的短期窗口使用
            sampen = get_sampen(nn_intervals_list)
            
            ### 2.计算另外两个hrv时域特征（因为hrvanalysis库没有这俩个特征）
            # 如果time列为RRI/1000的累加和，则直接执行以下代码
            count_5m = int(list(RRIdata['time'])[-1]/300) + 1 #统计5min的个数
            rr_mean_5m = [] #每5min节段窦性R-R间期平均值
            rr_std_5m = [] #每5min节段窦性R-R间期标准差
            for i in range(count_5m):
                tmp = RRIdata[(RRIdata['time']>(i*300)) & (RRIdata['time']<=((i+1)*300))]
                rr_intervals_list = list(tmp['RRI'])
                
                # 离群值和异常值删除
                # 此为RR-interval长度列表，每个元素为每个RR-interval的间隔时间
                # 删除离群值，被删除的元素置为nan，自low_rri和high__rri分别为最小和为最大的RR-interval
                rr_intervals_without_outliers = remove_outliers(rr_intervals=rr_intervals_list,  
                                                                low_rri=300, high_rri=2000)
                # 将离群的rr-interval值删除，并用线性插值的方法添加新值
                interpolated_rr_intervals = interpolate_nan_values(rr_intervals=rr_intervals_without_outliers,
                                                                    interpolation_method="linear")
                # 从RR-interval心电信号中，采用malik方法删除异常值，即将值置为nan
                nn_intervals_list = remove_ectopic_beats(rr_intervals=interpolated_rr_intervals, method="malik")
                # 使用线性插值的方法替换nan
                interpolated_nn_intervals = interpolate_nan_values(rr_intervals=nn_intervals_list)
                
                rr_mean_5m.append( np.mean(interpolated_nn_intervals) )
                rr_std_5m.append( np.std(interpolated_nn_intervals) )
            
            # hrv时域特征---均值标准差(SDANN)    
            sdann = np.std(rr_mean_5m)
            # hrv时域特征---标准差均值(SDNN Index)
            sdnn_index = np.mean(rr_std_5m)
            time_domain_features['sdann'] = sdann
            time_domain_features['sdnn_index'] = sdnn_index
            
            #hrv特征写入字典
            hrv_features = [time_domain_features, frequency_domain_features, csi_cvi_features, 
                            poincare_plot_features, sampen]
            for feat in hrv_features:
                for key in feat.keys():
                    if key not in obj_dict:
                        obj_dict[key] = [feat[key]]
                    else:
                        obj_dict[key].append(feat[key])
        
        #存储我们计算的hrv特征                
        hrvFeature = pd.DataFrame(obj_dict)
        
        # ###############################################################
        #二、情绪指数模型预测
        #提取特征列索引
        inds = list(range(0,len(hrvFeature.columns)))
        X_test = np.array(hrvFeature.iloc[:,inds])
        
        #数据标准化
        # X_train = np.load(trainData_path + 'trainData.npy')
        X_train = np.load(parent_dir+'/trainData/trainData.npy')
        scaler = StandardScaler().fit(X_train)
        X_test = scaler.transform(X_test)
        
        emo_index_list_1 = ['stress_index', 'tired_index']
        emo_index_list_2 = ['emotion_index', 'affect']
        testset_dict = {}
        
        for emo_index in emo_index_list_1:
            #SVM模型预测
            clf_svm = joblib.load(parent_dir+'/model/'+ emo_index + '_' + 'svm.model')

            # clf_svm = joblib.load(model_path + emo_index + '_' + 'svm.model')
            y_pred_svm = clf_svm.predict(X_test)
            # y_pred_svm = y_pred_svm.astype(int)  #python旧版本
            y_pred_svm = [int(pred_si) for pred_si in y_pred_svm]
            #情绪指数预测值写入字典
            # testset_dict[emo_index + '_svm_pred'] = list(y_pred_svm)  #python旧版本
            testset_dict[emo_index + '_svm_pred'] = y_pred_svm
            
        for emo_index in emo_index_list_2:
            #KNN模型预测
            # clf_knn = joblib.load(model_path + emo_index + '_' + 'knn.model')
            clf_knn = joblib.load(parent_dir+'/model/' + emo_index + '_' + 'knn.model')

            y_pred_knn = clf_knn.predict(X_test)
            # y_pred_knn = y_pred_knn.astype(int)
            y_pred_knn = [ int(pred_si) for pred_si in y_pred_knn]
            #情绪指数预测值写入字典
            # testset_dict[emo_index + '_knn_pred'] = list(y_pred_knn)
            testset_dict[emo_index+'_knn_pred'] = y_pred_knn
            
        endtime = time.time()
        dtime = round(endtime - starttime, 2)
        # model_return_dict['rri_path'] = arg1
        model_return_dict['start_time'] = start_time
        model_return_dict['finish_time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        model_return_dict['run_time'] = dtime
        model_return_dict['code'] = 1
        model_return_dict['msg'] = 'success'
        model_return_dict['predict_result'] = testset_dict
                
    except Exception as e:
        endtime = time.time()
        dtime = round(endtime - starttime, 2)
        # model_return_dict['rri_path'] = arg1
        model_return_dict['start_time'] = start_time
        model_return_dict['finish_time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        model_return_dict['run_time'] = dtime
        model_return_dict['code'] = -1
        model_return_dict['msg'] = str(e)
        model_return_dict['predict_result'] = {}

    return model_return_dict
