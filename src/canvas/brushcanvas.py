#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
import pyglet
import wintab
import numpy as np
import Tkinter, tkFileDialog
from math import sin, cos, pi
from pyglet.gl import *
from pyglet.window import key
from droplet.util import convert_wintab_azimuth
from mybrush import MyBrush
from sign.signature import Signature


class BrushCanvas(pyglet.window.Window):
    def __init__(self, *args, **kwds):
        u'ペンタブレットを用いて書道風の文字を描画し記録するためのウィンドウクラス'
        super(BrushCanvas, self).__init__(*args, **kwds)

        devices = wintab.get_tablets()
        if len(devices) == 0:
            raise RuntimeError('Pen-Tablet cannot be detected: System reboot may invoke the driver')
            
        self.device = devices[0]
        self.tablet = wintab.WintabTabletCanvas(self.device, self)
        self.tablet.on_packet(self.on_packet)
        
        self.brush = MyBrush.get_brush(*self.get_size())
        self.texture = None
        for size in [2048, 1024, 512, 256, 128]:
            try:
                path = u'../../data/わら半紙_{:d}.png'.format(size)
                self.texture = pyglet.image.load(path).get_texture()
            except GLException as e:
                pass
            else:
                break
        
        self.pre_point = None
        self.point = None
        self.start_time = None
        self.image = None
        self.strokes = [[]]

        self.init_opengl()
        self.print_flag = False

        pyglet.clock.schedule_interval(self.update, 1 / 60.0)

    def init_opengl(self):
        u'OpenGLを初期化する'
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        
    def front_image(self):
        u'今の画面を返す'
        buffer_manager = pyglet.image.get_buffer_manager()
        color_buffer = buffer_manager.get_color_buffer()
        image_data = color_buffer.get_image_data()
        return image_data
        
    def update(self, dt):
        u'何もしない'
        pass
        
    def on_packet(self, packet):
        u'ペンタブから入力があった場合に呼ばれるメソッド、現在の座標・筆圧などを得る'
        self.point = list(packet[0])
        current_time = self.point[5]

        # 時間を書き始めが 0 になるように変換する
        if self.start_time is None:
            self.start_time = current_time
        else:
            self.point[5] = self.point[5] - self.start_time
            
    def on_draw(self):
        u'画面描画のために呼ばれるメソッド'
        self.clear()
        
        if self.image is not None:
            self.image.blit(0, 0)
        
        if self.pre_point != self.point:
            # 筆の角度を変換し毛筆をアップデートする
            self.brush.update(self.point)
            self.brush.draw()
            
            # 座標をストロークリストに追加する
            if self.point[2] != 0:
                # 紙に筆を押し付けている時
                point = np.array(self.point)
                point[1] = self.height - point[1]
                
                self.strokes[-1].append(point)
                
                print '\t'.join(str(p) for p in point)
                self.print_flag = True

            else:
                # 筆を持ち上げた時
                if len(self.strokes[-1]) != 0:
                    self.strokes.append([])

                if self.print_flag:
                    print ''
                    self.print_flag = False

        self.image = self.front_image()
        self.pre_point = self.point


    def on_key_press(self, symbol, modifiers):
        u'キーボードが押されたときに呼ばれるメソッド'
        if symbol == key.ESCAPE or symbol == key.Q:
            pyglet.app.exit()
        elif symbol == key.C:
            self.pre_point = None
            self.point = None
            self.start_time = None
            self.image = None
            self.strokes = [[]]
        elif symbol == key.S:
            root = Tkinter.Tk()
            root.withdraw()
            file_name = tkFileDialog.asksaveasfilename(filetypes=[('Signature File', '*.sign')],
                                                       initialdir='../../data/xyp',
                                                       defaultextension='sign')
            root.destroy()

            if file_name != '' and len(self.strokes[0]) != 0:
                if not file_name.endswith('.sign'):
                    file_name += '.sign'

                sign = Signature(data=self.strokes)
                header = sign.make_header_from_data()
                header['Normalized'] = (False, False, True, False, False, False)
                header['Canvas-Size'] = (self.width, self.height)
                header['Azimuth-Domain'] = (0, 3600)
                header['Altitude-Domain'] = (0, 900)
                header['Device-Name'] = 'wacom intuos4 PTK640'
                sign.header.update(header)
                sign.save_as(file_name)

                print u'画数: {}'.format(len(self.strokes) - 1)

    def clear(self):
        u'ウィンドウの描画面を初期化する'
        super(BrushCanvas, self).clear()
        glEnable(self.texture.target)
        glBindTexture(self.texture.target, self.texture.id)
        glBegin(GL_QUADS)
        glTexCoord2d(0, 0); glVertex2d(-self.width, -self.height)
        glTexCoord2d(0, 1); glVertex2d(-self.width, self.height)
        glTexCoord2d(1, 1); glVertex2d(self.width, self.height)
        glTexCoord2d(1, 0); glVertex2d(self.width, -self.height)
        glEnd()
        glDisable(self.texture.target)

        
        

def main():
    canvas = BrushCanvas(width=1024, height=768, caption='Canvas')
    pyglet.app.run()
        
    

if __name__ == '__main__':
    main()








    
