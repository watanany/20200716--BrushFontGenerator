#!/usr/bin/env python
# -*- coding: utf-8 -*-

def convert_wintab_azimuth(azimuth):
    u'wintabで取得できる azimuth(0-3600:時計回り) をドロップレットモデルの初期位置を考慮した角度に変換する'
    return (2700 - azimuth) / 10

def convert_wintab_altitude(altitude):
    u'wintabで取得できる altitude(900-0:?) をドロップレットモデルの初期値を考慮した角度に変換する'
    return altitude / 10




