# -*- coding: utf-8 -*-
# @Time    : 2023/2/19 0:53
# @Author  : seasideGargantua
# @Site    : https://github.com/seasideGargantua
# @File    : imgtool.py
# @Software: PyCharm

import gdal
import numpy as np

def transfer_grey2L(img_grey):
    img_grey_width = img_grey.RasterXSize  # 栅格矩阵的列数
    img_grey_height = img_grey.RasterYSize  # 栅格矩阵的行数
    img_grey_array = img_grey.ReadAsArray(0, 0, img_grey_width, img_grey_height)
    img_L = np.multiply(np.power(img_grey_array,1.5),1e-10)
    return img_L

def transfer_Pixel2LonLat(img, X, Y):
    img_GeoTransform = img.GetGeoTransform()
    lon = img_GeoTransform[0] + X * img_GeoTransform[1] + Y * img_GeoTransform[2]
    lat = img_GeoTransform[3] + X * img_GeoTransform[4] + Y * img_GeoTransform[5]
    return (lon, lat)

def transfer_LonLat2Pixel(img, lon, lat):
    img_GeoTransform = img.GetGeoTransform()
    temp = img_GeoTransform[1] * img_GeoTransform[5] - img_GeoTransform[2] * img_GeoTransform[4]
    X = int((img_GeoTransform[5] * (lon - img_GeoTransform[0]) - img_GeoTransform[2] * (lat - img_GeoTransform[3])) / temp + 0.5)
    Y = int((img_GeoTransform[1] * (lat - img_GeoTransform[3]) - img_GeoTransform[4] * (lon - img_GeoTransform[0])) / temp + 0.5)
    return (X, Y)

def landuse2Ref(img, X, Y):
    type_code = img[Y][X]
    ref = 0
    type_code_map = {'Commercial':[7209,7211,7212],
                     'Industrial':[7214,7204],
                     'Vegetation':[7201,7208,7217,7218,7210],
                     'Park':[7202],
                     'Residential':[7203],
                     'Farm':[7228,7229,7215],
                     'Bare':[7206,7213]}
    type_ref_map = {'Commercial':0.63,
                     'Industrial':0.35,
                     'Vegetation':0.15,
                     'Park':0.22,
                     'Residential':0.65,
                     'Farm':0.17,
                     'Bare':0.2}
    for k,v in type_code_map.items():
        if type_code in v:
            ref = type_ref_map[k]
    return ref

def landuse2Code(img, X, Y):
    type_code = img[Y][X]
    code = 0
    type_code_map = {'Commercial': [7209, 7211, 7212],
                     'Industrial': [7214, 7204]}
    for k, v in type_code_map.items():
        if type_code in v:
            code = 1
    return code

def distance2Res(x1, y1, x2, y2):
    distance = np.sqrt(np.power(x1-x2,2)+np.power(y1-y2,2))*130
    res = 1
    if distance > 0 and distance < 200:
        res = 0.75
    elif distance >= 200 and distance < 500:
        res = 0.5
    elif distance >= 500 and distance < 1000:
        res = 0.25
    elif distance >= 1000:
        res = 0
    return res

def gdal2array(img):
    img_width = img.RasterXSize  # 栅格矩阵的列数
    img_height = img.RasterYSize  # 栅格矩阵的行数
    img_arr = img.ReadAsArray(0, 0, img_width, img_height)
    return img_arr

def laplace(img):
    img_padding = np.zeros((img.shape[0] + 2, img.shape[1] + 2), np.uint8)
    for i in range(1, img_padding.shape[0] - 1):
        for j in range(1, img_padding.shape[1] - 1):
            if img[i-1][j-1] == -32768:
                continue
            img_padding[i][j] = img[i - 1][j - 1]

    img_laplace = np.zeros((img.shape[0], img.shape[1]), np.uint8)
    kernel = [[0, 1, 0], [1, -4, 1], [0, 1, 0]]
    for i in range(0, img.shape[0]):
        for j in range(0, img.shape[1]):
            img_laplace[i][j] = abs(np.sum(np.multiply(kernel, img_padding[i:i + 3, j:j + 3])))

    return img_laplace

def conv(img,kernel,kernel_size,x0,y0):
    result = 0
    x = x0 - int(kernel_size/2)
    y = y0 - int(kernel_size/2)
    for i in range(3):
        for j in range(3):
            result += kernel[i][j]*img[y+i][x+j]
    return result


def arr2raster(arr, raster_file, prj=None, trans=None):
    """
    将数组转成栅格文件写入硬盘
    :param arr: 输入的mask数组 ReadAsArray()
    :param raster_file: 输出的栅格文件路径
    :param prj: gdal读取的投影信息 GetProjection()，默认为空
    :param trans: gdal读取的几何信息 GetGeoTransform()，默认为空
    :return:
    """

    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.Create(raster_file, arr.shape[1], arr.shape[0], 1, gdal.GDT_Byte)

    if prj:
        dst_ds.SetProjection(prj)
    if trans:
        dst_ds.SetGeoTransform(trans)

    # 将数组的各通道写入图片
    dst_ds.GetRasterBand(1).WriteArray(arr)

    dst_ds.FlushCache()
    dst_ds = None
    print("successfully convert array to raster")

