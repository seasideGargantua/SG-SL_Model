# -*- coding: utf-8 -*-
# @Time    : 2023/2/19 1:32
# @Author  : seasideGargantua
# @Site    : https://github.com/seasideGargantua
# @File    : model.py
# @Software: PyCharm

from utils import imgtool
import numpy as np
import gdal

class SG_SL_Model():
    def __init__(self, Dataloader, location, args):
        dataset = Dataloader.createDataloader()
        self.NL = dataset['nightlight'][location]
        temp = imgtool.transfer_grey2L(self.NL)
        self.NL_arr = temp[0]
        self.mask = imgtool.gdal2array(self.NL)[1]
        self.NL_width = self.NL.RasterXSize  # 栅格矩阵的列数
        self.NL_height = self.NL.RasterYSize  # 栅格矩阵的行数

        self.DEM = dataset['dem'][location]
        self.DEM_arr = imgtool.gdal2array(self.DEM)
        self.NDVI = dataset['ndvi'][location]
        self.NDVI_arr = imgtool.gdal2array(self.NDVI)
        self.Aerosol = dataset['aerosol'][location]
        self.Aerosol_arr = imgtool.gdal2array(self.Aerosol)
        self.gas = dataset['gas'][location]
        self.gas_arr = imgtool.gdal2array(self.gas)
        self.pop = dataset['pop'][location]
        self.pop_arr = imgtool.gdal2array(self.pop)
        self.landuse = dataset['landuse'][location]
        self.landuse_arr = imgtool.gdal2array(self.landuse)
        self.road = dataset['road'][location]
        self.road_arr = imgtool.gdal2array(self.road)

        # road_max = np.max(self.road_arr)
        # road_min = np.min(self.road_arr)

        self.location = location

        self.args = args

    def calculate_b1(self):
        b1 = np.zeros((self.NL_height,self.NL_width))
        rp = 3

        for xi in range(self.NL_width):
            for yi in range(self.NL_height):
                if self.mask[yi][xi] == 0:
                    continue
                # get window of point (xi,yi)
                window_l = xi - rp
                window_r = xi + rp
                window_t = yi - rp
                window_b = yi + rp
                if window_l < 0:
                    window_l = 0
                if window_t < 0:
                    window_t = 0
                if window_r > self.NL_width - 1:
                    window_r = self.NL_width - 1
                if window_b > self.NL_height - 1:
                    window_b = self.NL_height - 1

                # caculate b1 of point (xi,yi)
                for u in range(window_l,window_r):
                    for v in range(window_t,window_b):
                        lon,lat = imgtool.transfer_Pixel2LonLat(self.NL, u, v)
                        X_gas,Y_gas = imgtool.transfer_LonLat2Pixel(self.gas, lon, lat)
                        X_landuse,Y_landuse = imgtool.transfer_LonLat2Pixel(self.landuse, lon, lat)
                        if X_gas < 0 or Y_gas < 0 or X_landuse < 0 or Y_landuse < 0:
                            continue
                        if X_gas >= self.gas_arr.shape[1] or Y_gas >= self.gas_arr.shape[0] or X_landuse >= self.landuse_arr.shape[1] or Y_landuse > self.landuse_arr.shape[0]:
                            continue
                        K = self.gas_arr[Y_gas][X_gas]
                        e = self.NL_arr[v][u]*np.pi*280
                        rou = imgtool.landuse2Ref(self.landuse_arr, X_landuse, Y_landuse)
                        if K == -3.402823e+38 or e == 0.0 or rou == 0:
                            continue
                        b1[yi][xi] += K*(1+rou)*e

        return b1

    def calculate_b2(self, w1=-0.2, w2=-0.3):
        b2 = np.zeros((self.NL_height,self.NL_width))
        rp1 = 3
        rp2 = 5
        DEM_laplace = imgtool.laplace(self.DEM_arr)

        for xi in range(self.NL_width):
            for yi in range(self.NL_height):
                if self.mask[yi][xi] == 0:
                    continue
                # get window of point (xi,yi)
                window_l1 = xi - rp1
                window_r1 = xi + rp1
                window_t1 = yi - rp1
                window_b1 = yi + rp1
                if window_l1 < 0:
                    window_l1 = 0
                if window_t1 < 0:
                    window_t1 = 0
                if window_r1 > self.NL_width - 1:
                    window_r1 = self.NL_width - 1
                if window_b1 > self.NL_height - 1:
                    window_b1 = self.NL_height - 1

                window_l2 = xi - rp2
                window_r2 = xi + rp2
                window_t2 = yi - rp2
                window_b2 = yi + rp2
                if window_l2 < 0:
                    window_l2 = 0
                if window_t2 < 0:
                    window_t2 = 0
                if window_r2 > self.NL_width - 1:
                    window_r2 = self.NL_width - 1
                if window_b2 > self.NL_height - 1:
                    window_b2 = self.NL_height - 1

                # caculate b2 of point (xi,yi)
                for u in range(window_l2,window_r2):
                    for v in range(window_t2,window_b2):
                        if (window_l1 < u and window_r1 > u) and (window_t1 < v and window_b1 > v):
                            continue

                        lon,lat = imgtool.transfer_Pixel2LonLat(self.NL, u, v)
                        X_aer,Y_aer = imgtool.transfer_LonLat2Pixel(self.Aerosol, lon, lat)
                        X_NDVI,Y_NDVI = imgtool.transfer_LonLat2Pixel(self.NDVI, lon, lat)
                        X_DEM,Y_DEM = imgtool.transfer_LonLat2Pixel(self.DEM, lon, lat)
                        L = np.sqrt(np.power(u-xi,2) + np.power(v-yi,2)) * 130

                        if X_aer < 0 or Y_aer < 0 or X_NDVI < 0 or Y_NDVI < 0 or X_DEM < 0 or Y_DEM < 0:
                            continue
                        if X_aer >= self.Aerosol_arr.shape[1] or Y_aer >= self.Aerosol_arr.shape[0] or X_NDVI >= self.NDVI_arr.shape[1] or Y_NDVI >= self.NDVI_arr.shape[0] or X_DEM >= self.DEM_arr.shape[1] or Y_DEM >= self.DEM_arr.shape[0]:
                            continue

                        K = self.Aerosol_arr[Y_aer][X_aer]
                        e = self.NL_arr[v][u]*np.pi*280

                        alpha = self.NDVI_arr[Y_NDVI][X_NDVI]
                        beta = DEM_laplace[Y_DEM][X_DEM]

                        if K == -3.402823e+38 or e == 0.0 or alpha == -3.402823e+38:
                            continue

                        T = 1 + w1*alpha + w2*beta

                        b2[yi][xi] += K*(T/(L**2))*e

        return b2

    def calculate_c1(self, season):
        lt0 = 0
        if season == 'summer':
            lt0 = 10
        elif season == 'winter':
            lt0 = 14

        c1 = np.zeros((self.NL_height,self.NL_width))

        for xi in range(self.NL_width):
            for yi in range(self.NL_height):
                if self.mask[yi][xi] == 0:
                    continue
                lon, lat = imgtool.transfer_Pixel2LonLat(self.NL, xi, yi)
                X_landuse,Y_landuse = imgtool.transfer_LonLat2Pixel(self.landuse, lon, lat)

                if X_landuse < 0 or Y_landuse < 0:
                    continue
                if X_landuse >= self.landuse_arr.shape[1] or Y_landuse >= self.landuse_arr.shape[0]:
                    continue
                e = self.NL_arr[yi][xi]*np.pi*280
                M = imgtool.landuse2Code(self.landuse_arr, X_landuse, Y_landuse)

                c1 = lt0*e*M

        return c1

    def calculate_c2(self, season):
        lt1 = 0
        if season == 'summer':
            lt1 = 5
        elif season == 'winter':
            lt1 = 7

        c2 = np.zeros((self.NL_height,self.NL_width))

        for xi in range(self.NL_width):
            for yi in range(self.NL_height):
                if self.mask[yi][xi] == 0:
                    continue
                lon, lat = imgtool.transfer_Pixel2LonLat(self.NL, xi, yi)
                X_road,Y_road = imgtool.transfer_LonLat2Pixel(self.road, lon, lat)

                if X_road < 0 or Y_road < 0:
                    continue
                if X_road >= self.road_arr.shape[1] or Y_road >= self.road_arr.shape[0]:
                    continue
                e = self.NL_arr[yi][xi]*np.pi*280
                M = self.road_arr[Y_road][X_road]
                if M == 3:
                    continue
                c2 = 4.02*e*M + 0.2*((lt1-2)*e*M)

        return c2

    def calculate_c3(self):
        lr1 = np.zeros((self.NL_height,self.NL_width))
        lr2 = np.zeros((self.NL_height,self.NL_width))

        for xi in range(self.NL_width):
            for yi in range(self.NL_height):
                if self.mask[yi][xi] == 0:
                    continue
                lon, lat = imgtool.transfer_Pixel2LonLat(self.NL, xi, yi)
                X_landuse,Y_landuse = imgtool.transfer_LonLat2Pixel(self.landuse, lon, lat)

                if X_landuse < 0 or Y_landuse < 0:
                    continue
                if X_landuse >= self.landuse_arr.shape[1] or Y_landuse >= self.landuse_arr.shape[0]:
                    continue

                rou = imgtool.landuse2Ref(self.landuse_arr, X_landuse, Y_landuse)
                lr1[yi][xi] = rou*self.NL_arr[yi][xi]

        GS = np.array([[1, 2, 1],
                       [2, 4, 2],
                       [1, 2, 1]],dtype=float)
        GS = GS/16
        NL_padding = np.zeros((self.NL_height+2,self.NL_width+2))
        for xi in range(1,self.NL_width+1):
            for yi in range(1,self.NL_height+1):
                NL_padding[yi][xi] = self.NL_arr[yi-1][xi-1]

        for xi in range(0, self.NL_width):
            for yi in range(0, self.NL_height):
                lr2[yi][xi] = imgtool.conv(NL_padding,GS,3,xi,yi)

        c3 = lr1*lr2

        return c3

    def calculate_c4(self):
        c4 = np.zeros((self.NL_height,self.NL_width))
        rp = 8

        for xi in range(self.NL_width):
            for yi in range(self.NL_height):
                if self.mask[yi][xi] == 0:
                    continue
                window_l = xi - rp
                window_r = xi + rp
                window_t = yi - rp
                window_b = yi + rp
                if window_l < 0:
                    window_l = 0
                if window_t < 0:
                    window_t = 0
                if window_r > self.NL_width - 1:
                    window_r = self.NL_width - 1
                if window_b > self.NL_height - 1:
                    window_b = self.NL_height - 1
                for u in range(window_l,window_r):
                    for v in range(window_t,window_b):
                        e = self.NL_arr[v][u]*np.pi*280
                        res = imgtool.distance2Res(xi,yi,u,v)
                        c4[yi][xi] += e*res
        return c4

    def calculate_SG(self, w11, w12):
        b1 = self.calculate_b1()
        b2 = self.calculate_b2()
        return w11*b1 + w12*b2

    def calculate_SL(self, season, w21, w22, w23, w24):
        c1 = self.calculate_c1(season)
        c2 = self.calculate_c2(season)
        c3 = self.calculate_c3()
        c4 = self.calculate_c4()
        return c1*w21 + c2*w22 + c3*w23 + c4*w24

    def calculate_LP(self, season, w1, w2, w11, w12, w21, w22, w23, w24):
        SG = self.calculate_SG(w11,w12)
        SL = self.calculate_SL(season, w21,w22,w23,w24)
        return SG*w1 + SL*w2

    def calculate(self):
        result = self.calculate_LP(self.args.season, self.args.w_SG, self.args.w_SL,
                                  self.args.w_b1, self.args.w_b2,
                                  self.args.w_c1, self.args.w_c2, self.args.w_c3, self.args.w_c4)
        TifName = 'SG_SL_result.tif'
        projection = self.NL.GetProjection()
        transform = self.NL.GetGeoTransform()
        imgtool.arr2raster(result,self.args.output_path+self.location+'\\'+TifName,projection, transform)
        return