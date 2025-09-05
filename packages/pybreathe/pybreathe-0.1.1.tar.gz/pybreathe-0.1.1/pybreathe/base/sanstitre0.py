# -*- coding: utf-8 -*-
"""
Created on Thu Sep  4 16:24:26 2025

@author: CoustilletT
"""


from .breathingflow import BreathingFlow


class BreathingSignals:
    def __init__(self, flow, thorax, abdomen):
        self.flow = flow
        self.thorax = thorax
        self.abdomen = abdomen
