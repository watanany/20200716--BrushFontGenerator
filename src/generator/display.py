#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import codecs
import numpy as np
import pyglet
import cv2
from math import sqrt, atan2, isinf
from copy import deepcopy
from pyglet.gl import *
from pyglet.window import key
from dtw.dp import DP
from sign.signature import Signature
from mybrush import MyBrush
from myloader import MyLoader


class Display(pyglet.window.Window):
    u'フォント生成の状態を表示するクラス'    
    def __init__(self, *args, **kwds):
        super(Display, self).__init__(*args, **kwds)

        # ディレクトリ
        self.skels_dir = '../../data/xy/temp'
        self.parts_dir = '../../data/xyp'
        
        # 文字データの読み込み
        self.skels = MyLoader().get_signs(self.skels_dir, show=True)
        self.index = 0
        self.output = codecs.open('../../output/dp_distance.csv', 'w', sys.stdout.encoding)
        self.assembled_sign = None
        self.skel = None
        self.char = None

        # DPを初期化
        self.dp = DP({'MODE_XY': 1.0})
        self.threshold = 100#0.15

        try:
            self.texture = pyglet.image.load(u'../../data/わら半紙_2048.png').get_texture()
        except GLException:
            print >>sys.stderr, Warning(u"This hardware don't support large texture.")
            self.texture = None
        
        # 毛筆を初期化する
        self.brush = MyBrush.get_brush(1.0, 1.0, a=1.7)

        self.init_parts_match()
        self.init_parts_draw()
        self.init_opengl()

        # ウィンドウの横幅の微調整
        self.a = 0.05
        
        # pyglet を一定周期で動かすように設定する
        self.fps = 60.0
        pyglet.clock.schedule_interval(self.update, 1.0 / self.fps)

    def init_parts_match(self):
        u'部品文字のストロークリスト(マッチング用)'
        brush_signs = MyLoader().get_signs(self.parts_dir, show=True)
        self.refs = []
        
        for sign in brush_signs:
            for stroke in sign:
                self.refs.append(stroke)
                
        self.dp.load_refs(self.refs)

    def init_parts_draw(self):
        u'正規化以外の前処理をしていない部品文字のストロークリスト(描画用)'
        original_signs = MyLoader(sampling=False).get_signs(self.parts_dir, show=True)
        self.ro_strokes = []
        
        for sign in original_signs:
            for stroke in sign:
                self.ro_strokes.append(stroke)

        self.ro_strokes = np.array(self.ro_strokes)

    def init_opengl(self):
        u'描画面用にOpenGLを初期化する。アルファブレンドを有効にする'
        glClearColor(1.0, 1.0, 1.0, 0.0)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)

    def update(self, dt):
        u'pygletによって一定間隔で実行されるメソッド'
        if 0 <= self.index < len(self.skels):
            self.skel = self.skels[self.index]
            self.char = self.skel.header.get('Character')
            self.assembled_sign, self.gen_info = self.generate(self.skel, self.threshold)
            self.output_to_file(self.char, self.gen_info)

            self.index += 1
        else:
            pyglet.app.exit()
            
    def on_resize(self, width, height):
        u'ウィンドウがリサイズされたときに呼ばれるメソッド。視界をX[0, 1], Y[0, 1]に設定'
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0.0 - self.a, 1.0 + self.a, 0.0, 1.0, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
    def on_draw(self):
        u'ウィンドウに描画する'
        self.clear()
        self.set_caption(u'Brush Font Generation')

        if self.assembled_sign is None:
            return
        
        # 全てのストロークが組み立てられていた場合
        if all(info['is_added'] for info in self.gen_info):
            # ウィンドウのタイトルを設定
            self.set_caption(u'Brush Font Generation of ' + self.char)

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
            save_name = os.path.join('../../output', (self.char + '.png'))
            image.save(save_name)

            # for OpenCV

    def get_array(self, image, format='RGB'):
        u'pyglet.image.ImageData を numpy.array に変換して返す'
        n_channel = len(format)
        data = image.get_data(format, image.width * n_channel)
        data = [ord(px) for px in data]

        array = []
        for k in range(image.height):
            i = image.width * n_channel * k
            j = image.width * n_channel * (k + 1)
            row = data[i:j]
            row = [row[n:n + n_channel] for n in range(0, len(row), n_channel)]
            array.append(row)

        return np.array(array)

    def on_key_press(self, symbol, modifiers):
        u'キーボードが押されたときメソッド'
        if symbol == key.ESCAPE or symbol == key.Q:
            pyglet.app.exit()

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
        glColor4d(0.0, 0.0, 0.0, 1.0)
        glLineWidth(36)
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
                
    def correspond_plot(self, skeleton, gen_info):
        u'対応点を結ぶ直線を表示'
        raise NotImplementedError()

    def output_to_file(self, char, gen_info):
        u'情報をファイルに出力する'
        output = [char] + [u'{:.2f}'.format(info['dist']) for info in gen_info]
        output = ','.join(output)

        print output
        print >>self.output, output
        self.output.flush()

        return output

    def front_image(self):
        u'描画面をImageDataとして返す'
        buffer_manager = pyglet.image.get_buffer_manager()
        color_buffer = buffer_manager.get_color_buffer()
        image_data = color_buffer.get_image_data()
        return image_data

    def generate(self, skeleton, threshold):
        u'引数で与えられた文字骨格を元に毛筆文字組み立てる'
        gen_info = []
        matched_strokes = []
                    
        for i, stroke in enumerate(skeleton):
            gen_info.append({
                'dist': float('inf'),
                'min_id': None,
                'min_path': None,
                'is_added': False,
            })
            
            min_id = self.dp.load_test(stroke).starting(0, 0).match().min_id

            if min_id is not None:
                dist = self.dp.dp_distance(min_id)
                ref = deepcopy(self.ro_strokes[min_id])
                #ref = deepcopy(self.refs[min_id])
                path = self.dp.backtrack(min_id)
                dist = float(dist) / len(path)
                
                gen_info[i]['dist'] = dist
                gen_info[i]['min_id'] = min_id
                gen_info[i]['min_path'] = path
                if dist < self.threshold:
                    # ストロークを文字の形を成すように移動する
                    x, y = ref[:, 0], ref[:, 1]
                    ref[:, 0] = x - x[0] + stroke[0][0]
                    ref[:, 1] = y - y[0] + stroke[0][1]
                    matched_strokes.append(ref)
                    gen_info[i]['is_added'] = True

        ### ストローク混合 ###
        matched_strokes2 = []
        for stroke, info in zip(skeleton, gen_info):
            if not info['is_added']:
                continue

            # ストロークの対応点を各リストに格納していく
            rp_list = []
            tp_list = []
            for i, j in info['min_path']:
                rp = self.refs[info['min_id']][i]
                tp = stroke[j]
                rp_list.append(rp)
                tp_list.append(tp)

            # 毛筆ストローク・毛筆ストロークの開始点
            ro_stroke = self.ro_strokes[info['min_id']]
            starting_point = ro_stroke[0]
            matched_strokes2.append([])

            # 対応する座標の間に存在する対応点を計算する
            for rp, rq, tp, tq in zip(rp_list, rp_list[1:], tp_list, tp_list[1:]):
                # 二点間の時間を取得し、その間にある点について処理する
                i_list = []
                rop_list = []
                
                for i, rop in enumerate(ro_stroke):
                    if rp[5] <= rop[5] <= rq[5]:
                        i_list.append(i)
                        rop_list.append(rop)

                # 一度処理した座標は処理対象から外す
                ro_stroke = np.delete(ro_stroke, i_list, axis=0)
                
                # 各座標間の長さの合計(ストロークの長さ)を測る
                length = 0
                for rop, roq in zip(rop_list, rop_list[1:]):
                    length += np.linalg.norm(roq[0:2] - rop[0:2])

                # 対応点を計算する
                v = tq - tp
                for i, rop in enumerate(rop_list):
                    accnorm = 0
                    for roq, ror in zip(rop_list[:i], rop_list[1:i]):
                        accnorm += np.linalg.norm(ror[0:2] - roq[0:2])
                        
                    rate = float(accnorm) / length
                    cor = tp + v * rate

                    rop = deepcopy(rop)
                    rop[0] = rop[0] - starting_point[0] + stroke[0][0]
                    rop[1] = rop[1] - starting_point[1] + stroke[0][1]

                    w = 0.2
                    rop[0:2] = w * rop[0:2] + (1 - w) * cor

                    matched_strokes2[-1].append(rop)

        sign = Signature(data=matched_strokes2)
        return sign, gen_info


    def clear(self):
        super(Display, self).clear()
        
        if self.texture is not None:
            glEnable(self.texture.target)
            glBindTexture(self.texture.target, self.texture.id)
            glBegin(GL_QUADS)
            glTexCoord2d(0, 0); glVertex2d(-1.0 - self.a, -1.0)
            glTexCoord2d(0, 1); glVertex2d(-1.0 - self.a, 1.0)
            glTexCoord2d(1, 1); glVertex2d(1.0 + self.a, 1.0)
            glTexCoord2d(1, 0); glVertex2d(1.0 + self.a, -1.0)
            glEnd()
            glDisable(self.texture.target)




def main():
    disp = Display(width=1024, height=768, caption=u'Brush Font Generation')
    pyglet.app.run()



if __name__ == '__main__':
    main()
