#!/usr/bin/env python
# -*- coding: utf-8 -*-
from signature2d import Signature2D
from header import Header

class Signature6D(Signature2D):
    def __init__(self, path=None, data=None):
        super(Signature6D, self).__init__(path=path, data=data)

    def make_header_from_data(self):
        header = super(Signature6D, self).make_header_from_data()
        header['Dimension'] = 6
        header['Data-Type'] = ('X', 'Y', 'Pressure', 'Azimuth', 'Altitude', 'Time(Seconds)')
        header['Stroke-Count'] = self.stroke_count
        header['Point-Counts'] = [len(stroke) for stroke in self.data]
        return header
        
    def normalize_pressure(self, min_pressure=0.0, max_pressure=1.0):
        if not self.header['Normalized'][2]:
            if 'Pressure-Domain' in self.header:
                domain = [int(s) for s in self.header['Pressure-Domain']]
                for stroke in self:
                    for point in stroke:
                        point[2] = (point[2] - domain[0]) / (domain[1] - domain[0])
            else:
                raise RuntimeError('Pressure-Domain is not in header')
            
        for stroke in self:
            for point in stroke:
                point[2] *= (max_pressure - min_pressure)
                point[2] += min_pressure

        return self
        
    def normalize_altitude(self, min_altitude=0.0, max_altitude=1.0):
        if not self.header['Normalized'][3]:
            if 'Altitude-Domain' in self.header:
                domain = [int(s) for s in self.header['Altitude-Domain']]
                for stroke in self:
                    for point in stroke:
                        point[3] = (point[3] - domain[0]) / (domain[1] - domain[0])
            else:
                raise RuntimeError('Altitude-Domain is not in header')

        for stroke in self:
            for point in stroke:
                point[3] *= (max_altitude - min_altitude)
                point[3] += min_altitude

        return self


    def normalize_azimuth(self, min_azimuth=0.0, max_azimuth=1.0):
        if not self.header['Normalized'][4]:
            if 'Azimuth-Domain' in self.header:
                domain = [int(s) for s in self.header['Azimuth-Domain']]
                for stroke in self:
                    for point in stroke:
                        point[3] = (point[3] - domain[0]) / (domain[1] - domain[0])
            else:
                raise RuntimeError('Azimuth-Domain is not in header')

        for stroke in self:
            for point in stroke:
                point[4] *= (max_azimuth - min_azimuth)
                point[4] += min_azimuth

        return self

        
