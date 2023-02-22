# -*- coding: utf-8 -*-
# @Time    : 2023/2/19 19:59
# @Author  : seasideGargantua
# @Site    : https://github.com/seasideGargantua
# @File    : dataset.py
# @Software: PyCharm

import os
import gdal

class Dataloader():
    def __init__(self,args):
        self.args = args

    def createPathjson(self):
        data_path = self.args.data_root + self.args.season +'\\'
        factor_list = os.listdir(data_path)
        path_json = {}
        for factor in factor_list:
            location_list = os.listdir(data_path + factor + '\\')
            location_json = {}
            for location in location_list:
                name_list = os.listdir(data_path + factor + '\\' + location + '\\')
                for name in name_list:
                    if os.path.splitext(name)[-1] == '.tif':
                        location_json[location] = data_path + factor + '\\' + location + '\\' + name
            path_json[factor] = location_json
        return path_json

    def createDataloader(self):
        path_json = self.createPathjson()
        datasets = {}
        for kf,vf in path_json.items():
            datasets[kf] = {}
            for kl,vl in vf.items():
                datasets[kf][kl] = gdal.Open(vl)
        return datasets