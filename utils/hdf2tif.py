# -*- coding: utf-8 -*-
# @Time    : 2023/2/18 18:48
# @Author  : seasideGargantua
# @Site    : https://github.com/seasideGargantua
# @File    : hdf2tif.py
# @Software: PyCharm

import gdal
import os

def hdf2tif(input_path, file_list, output_path):
    #  gdal打开hdf数据集
    os.chdir(input_path)
    for file_name in file_list:
        datasets = gdal.Open(input_path+file_name)
        #  获取hdf中的子数据集
        SubDatasets = datasets.GetSubDatasets()
        Metadata = datasets.GetMetadata()
        #  打印元数据
        for key, value in Metadata.items():
            print('{key}:{value}'.format(key=key, value=value))
        #  获取要转换的子数据集
        data = datasets.GetSubDatasets()[0][0]
        Raster_DATA = gdal.Open(data)
        DATA_Array = Raster_DATA.ReadAsArray()
        # print(DATA_Array)
        #  保存为tif
        TifName = output_path + os.path.splitext(file_name)[0] + '.tif'
        geoData = gdal.Warp(TifName, Raster_DATA,
                            dstSRS='EPSG:4326', format='GTiff',
                            resampleAlg=gdal.GRA_Bilinear)
        del geoData
    return 'success'
