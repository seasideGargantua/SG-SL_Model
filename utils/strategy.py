# -*- coding: utf-8 -*-
# @Time    : 2023/2/20 17:26
# @Author  : seasideGargantua
# @Site    : https://github.com/seasideGargantua
# @File    : strategy.py
# @Software: PyCharm

from scipy.optimize import minimize
import numpy as np
from utils.model import SG_SL_Model

class SG_SL_Model_strategy():
    def __init__(self, Eco, Pop, Bio, Geo, Cli, EdT, Dataloader, args):
        super(SG_SL_Model_strategy,self).__init__()
        self.Eco = Eco
        self.Pop = Pop
        self.Bio = Bio
        self.Geo = Geo
        self.Cli = Cli
        self.EdT = EdT

        self.W = np.array([0.305,0.281,0.072,0.200,0.019,0.123])

        self.dataloader = Dataloader
        self.args = args

    def calculate_P(self):
        K1 = self.Cli * self.Bio / self.Geo
        K2 = K1
        K3 = 1 / ((self.Eco + self.EdT) / self.Pop)
        K4 = K3
        K5 = 1 / (self.Bio * self.Pop)
        K6 = K5
        K = np.array([K1, K2, K3, K4, K5, K6])
        W_new = K * self.W

        self.args.w_b1 = W_new[0]
        self.args.w_b2 = W_new[1]
        self.args.w_c1 = W_new[2]
        self.args.w_c2 = W_new[3]
        self.args.w_c3 = W_new[4]
        self.args.w_c4 = W_new[5]

        model = SG_SL_Model(self.dataloader, self.args)
        b1 = model.calculate_b1
        b2 = model.calculate_b2
        c1 = model.calculate_c1
        c2 = model.calculate_c2
        c3 = model.calculate_c3
        c4 = model.calculate_c4
        P = np.array([b1, b2, c1, c2, c3, c4])
        return W_new,P

    def SPD(self, P):
        phi = np.array([0.24,0.13,0.04,0.26,0.16,0.17])
        return np.dot(P,phi.transpose())

    def LPR(self, W_new, P):
        return np.dot(P,W_new.transpose())

    def optimize(self):
        W_new,P0 = self.calculate_P()
        target = lambda x:self.LPR(W_new,x)/self.SPD(x)
        cons = ({'type':'ineq','fun':lambda x:x[0]-0.15*self.Cli-0.1*self.Bio},
                {'type':'eq','fun':lambda x:x[0]-np.min(0.75+self.EdT,1)},
                {'type': 'ineq', 'fun': lambda x: x[1] - 0.25 * self.Pop},
                {'type': 'eq', 'fun': lambda x: x[1] - np.min(0.75 + self.Eco, 1)},
                {'type': 'ineq', 'fun': lambda x: x[2] - 0.1 * self.Pop - 0.15 * self.Bio},
                {'type': 'eq', 'fun': lambda x: x[2] - np.min(0.75 + self.Geo, 1)},
                )
        res = minimize(target,P0,method='SLSQP',constraints=cons)
        return res
