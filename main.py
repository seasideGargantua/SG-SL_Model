# -*- coding: utf-8 -*-
# @Time    : 2023/2/18 15:18
# @Author  : seasideGargantua
# @Site    : https://github.com/seasideGargantua
# @File    : main.py
# @Software: PyCharm

from utils.model import SG_SL_Model
from utils.dataset import Dataloader
import argparse

parser = argparse.ArgumentParser(description='A Implementation of SG-SL Model')
# data and result
parser.add_argument('--data_root', default='D:\\MCMWorkplace\\content\\Datasets\\',
                    help='the root directory of data')
parser.add_argument('--output_path', default='D:\\MCMWorkplace\\content\\Outputs\\',
                    help='the directory of output')
# parameters of model
parser.add_argument('--w_SG', type=float, default=0.586, help='weight of Sky Glow (SG)')
parser.add_argument('--w_SL', type=float, default=0.414, help='weight of Spill Light (SL)')
parser.add_argument('--w_b1', type=float, default=0.520, help='weight of Scattering of Gas Molecules (b1)')
parser.add_argument('--w_b2', type=float, default=0.480, help='weight of Scattering of Aerosol Particles (b2)')
parser.add_argument('--w_c1', type=float, default=0.175, help='weight of Light Clutter (c1)')
parser.add_argument('--w_c2', type=float, default=0.482, help='weight of Glare (c2)')
parser.add_argument('--w_c3', type=float, default=0.045, help='weight of Light Reflection (c3)')
parser.add_argument('--w_c4', type=float, default=0.298, help='weight of Light Trespass (c4)')
parser.add_argument('--season', type=str, default='summer', choices=['summer', 'winter'],
                    help='the season of used data')

if __name__ == '__main__':
    args = parser.parse_args()
    dataloader = Dataloader(args)
    print('creating model...')
    # model_wuhan = SG_SL_Model(dataloader, 'wuhan', args)
    # model_ezhou = SG_SL_Model(dataloader, 'ezhou', args)
    model_jianshi = SG_SL_Model(dataloader, 'jianshi', args)
    # model_shennongjia = SG_SL_Model(dataloader, 'shennongjia', args)
    print('start calculate...')
    # model_wuhan.calculate()
    # model_ezhou.calculate()
    model_jianshi.calculate()
    # model_shennongjia.calculate()
    print('over!')
