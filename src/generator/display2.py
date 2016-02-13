#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import numpy as np
import pyglet
import cv2
from pyglet.gl import *
from pyglet.window import key
from mybrush import MyBrush
from generator import Generator

class Display(pyglet.window.Window):
    u'フォント生成の状態を表示するクラス'
    def __init__(self, *args, **kwds):
        super(Display, self).__init__(*args, **kwds)

        # 背景画像用のテクスチャをロードする
        self.texture = None
        for size in [2048, 1024, 512, 256, 128]:
            try:
                path = u'../../data/わら半紙_{:d}.png'.format(size)
                self.texture = pyglet.image.load(path).get_texture()
            except GLException as e:
                pass
            else:
                break

        # 毛筆文字生成器を初期化し、文字を生成する
        self.generator = Generator()
        self.generator.generate_all()
        self.generator.interfuse_all(w=0.0)

        # 各変数を初期化する
        self.brush = MyBrush.get_brush(1.0, 1.0, a=1.0)
        #self.brush = ShinBrush.get_brush(1.0, 1.0, a=1.0)
        self.skels = self.generator.skels
        self.index = 0
        self.skel = None
        self.char = None
        self.assembled_sign = None
        self.gen_info = None

        # 描画領域の幅の微調整用変数
        self.ax = 0.0#5
        self.ay = 0.0
        
        self.init_opengl()
        
        # pyglet を一定周期で動かすように設定する
        self.fps = 60.0
        pyglet.clock.schedule_interval(self.update, 1.0 / self.fps)

        
    def init_opengl(self):
        u'描画面用にOpenGLを初期化する。アルファブレンドを有効にする'
        glClearColor(1.0, 1.0, 1.0, 0.0)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)

    def update(self, dt):
        u'pygletによって一定間隔で実行されるメソッド'
        if 0 <= self.index < len(self.generator):
            sign, gen_info = self.generator[self.index]
            self.assembled_sign = sign
            self.gen_info = gen_info
            self.skel = self.skels[self.index]
            self.char = self.skel.header['Character']
            self.index += 1
        else:
            pyglet.app.exit()
            
    def on_resize(self, width, height):
        u'ウィンドウがリサイズされたときに呼ばれるメソッド。視界をX[0, 1], Y[0, 1]に設定'
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0.0 - self.ax, 1.0 + self.ax,
                0.0 - self.ay, 1.0 + self.ay,
                -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
    def on_draw(self):
        u'ウィンドウに描画する'
        self.clear()
        caption = u'Brush Font Generation of {} ({}/{})'.format(self.char, self.index + 1, len(self.skels))
        self.set_caption(caption)

        if self.assembled_sign is None:
            return
        
        # 全てのストロークが組み立てられていた場合
        if all(info['is_added'] for info in self.gen_info):
            # # Test
            # super(Display, self).clear()
            # self.line_plot(self.assembled_sign)
            # line_image = self.front_image()
            # w, h = line_image.width, line_image.height
            # line_image = line_image.get_data('RGB', line_image.width * 3)
            # line_image = np.array([ord(px) for px in line_image])
            # line_image = line_image.reshape(h, w, 3)

            # for stroke in self.assembled_sign:
            #     seed_point = stroke[0]
            #     seed_point = int(round(seed_point[0] * self.width)), int(round(seed_point[1] * self.height))
            #     retval, rect = cv2.floodFill(line_image, None, seed_point, (0, 0, 255))
            #     print rect
            #     print u'面積: {}'.format(rect[2] * rect[3])

            # data =  ''.join(chr(px) for px in line_image.flatten())
            # line_image = pyglet.image.ImageData(self.width, self.height, 'RGB', data)
            # line_image.save('hoge.png')

            self.clear()
            # 文字の骨格を表示する
            glPushMatrix()
            glTranslated(0.0, 0.25, 0.0)
            glScaled(0.5, 0.5, 0.0)
            self.dot_plot(self.skel)
            glPopMatrix()
            
            # 筆文字を表示する
            glPushMatrix()
            glTranslated(0.5, 0.25, 0.0)
            glScaled(0.5, 0.5, 0.0)
            self.brush_plot(self.assembled_sign)
            #self.line_plot(self.assembled_sign)
            glPopMatrix()

            # 現在の画面を画像とて保存する
            image = self.front_image()
            save_name = os.path.join('../../output/img', (self.char + '.png'))
            image.save(save_name)            
        else:
            self.set_caption(caption + u' not generated')


    def on_key_press(self, symbol, modifiers):
        u'キーボードが押されたときメソッド'
        if symbol == key.ESCAPE or symbol == key.Q:
            pyglet.app.exit()
        elif symbol == key.LEFT:
            if 0 <= self.index - 1:
                self.index -= 1
        elif symbol == key.RIGHT:
            if self.index + 1 < len(self.skels):
                self.index += 1

    def dot_plot(self, sign):
        u'ドットで文字を描画する'
        glColor4d(1.0, 0.0, 0.0, 1.0)
        glPointSize(12)
        for stroke in sign:
            glBegin(GL_POINTS)
            for point in stroke:
                glVertex2d(point[0], point[1])
            glEnd()

    def line_plot(self, sign):
        u'座標間を線で繋ぎ合わせ描画する'
        glColor4d(0.0, 0.0, 0.0, 1.0)
        glLineWidth(12)
        for stroke in sign:
            glBegin(GL_LINE_STRIP)
            for point in stroke:
                glVertex2d(point[0], point[1])
            glEnd()
        
    def brush_plot(self, brush_sign):
        u'毛筆で文字を描画する'
        for stroke in brush_sign:
            for point in stroke:
                self.brush.update(point)
                self.brush.draw()
            #self.liftup()
                
    def front_image(self):
        u'描画面をImageDataとして返す'
        buffer_manager = pyglet.image.get_buffer_manager()
        color_buffer = buffer_manager.get_color_buffer()
        image_data = color_buffer.get_image_data()
        return image_data

    def clear(self):
        u'画面を消去し背景画像を描画する'
        super(Display, self).clear()
        
        if self.texture is not None:
            glEnable(self.texture.target)
            glBindTexture(self.texture.target, self.texture.id)
            glBegin(GL_QUADS)
            glTexCoord2d(0, 0); glVertex2d(-1.0 - self.ax, -1.0 - self.ay)
            glTexCoord2d(0, 1); glVertex2d(-1.0 - self.ax, 1.0 + self.ay)
            glTexCoord2d(1, 1); glVertex2d(1.0 + self.ax, 1.0 + self.ay)
            glTexCoord2d(1, 0); glVertex2d(1.0 + self.ax, -1.0 - self.ay)
            glEnd()
            glDisable(self.texture.target)





def main():
    disp = Display(width=1024, height=768, caption=u'Brush Font Generation')
    pyglet.app.run()



if __name__ == '__main__':
    main()



