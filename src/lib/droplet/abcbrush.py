#!/usr/bin/env python
# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod


class AbstractBrush(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def update(self, point):
        pass

    @abstractmethod
    def draw(self):
        pass






