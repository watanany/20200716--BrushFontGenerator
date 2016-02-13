#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pdb
import sys
import os
import codecs
import numpy as np
from math import sqrt, atan2, isinf
from copy import deepcopy
from random import shuffle
from datetime import datetime
from scipy.interpolate import interp1d
from OpenGL.GL import *
from OpenGL.GLUT import *
from PIL import Image
from PIL import ImageOps
from dpclass import DP
from sign.signature import Signature6D as Signature
from droplet.brush import Brush, convert_wintab_azimuth


class Display(object):
    u'フォント生成の状態を表示するクラス'
    def __init__(self):
        self.r_signs = load_signs('../data/xyp')
        self.t_signs = load_signs('../data/xy/temp')
        self.t_index = 0 # 1605=u'燕'
        self.dp = DP(weight={'MODE_DP': 1.0})
        self.point_size = 12
        self.threshold = 100# 0.08
        #self.output_dir = os.path.join('../output', datetime.today().strftime('%m%d%H%M%S'))
        self.output = codecs.open('../output/dp_distance.csv', 'w', sys.stdout.encoding)
        self.is_drawed = None

        self.brush = Brush({
            'length': 0.1,
            'D': 0.1,
            'hair_number': 3, #25,
            'humidity': 1.0,
            'pigment': 0.7,
            'k': 0.5,
            'threshold': {
                ((1, 2), 3): 0.9,
                ((3, 4), 5): 0.5,
            },
            'p_tip': [0.7, 0.3],
        })

        # 部品文字のストロークリスト(マッチング用)
        refs = []
        self.refs = []
        for sign in self.r_signs:
            for stroke in sign:
                x, y = stroke[:, 0], stroke[:, 1]
                refs.append(np.array(zip(x, y)))
                self.refs.append(stroke)
                
        self.dp.load_refs(refs)
        self.refs = np.array(self.refs)
        
        # 正規化以外の前処理をしていない部品文字のストロークリスト(描画用)
        original_signs = load_signs('../data/xyp', only_normalize=True)
        self.ro_strokes = []
        for sign in original_signs:
            for stroke in sign:
                self.ro_strokes.append(stroke)
               
        self.ro_strokes = np.array(self.ro_strokes)

    def init_opengl(self, display, keyboard):
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)
        glutInitWindowSize(800, 600)
        glutInitWindowPosition(100, 100)
        glutCreateWindow(u'Font Generation')
        glClearColor(1.0, 1.0, 1.0, 0.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glutDisplayFunc(display)
        glutKeyboardFunc(keyboard)
        glutMainLoop()
        
        
    def display_all(self):
        u'文字一つ一つの組み立てを表示する: h: 一つ戻る、l: 一つ進む'
        self.init_opengl()

    def capture_all(self, dir):
        u'文字一つ一つを組み立て、画像として保存する'
        def display():
            if 0 <= self.t_index < len(self.t_signs):
                # 現在の番号に対応する参照文字と生成された文字を表示する
                print >>sys.stderr, self.t_index, len(self.t_signs)
                self.display()

                # 現在の画面を対応するファイル名に保存する
                sign = self.t_signs[self.t_index]
                char = sign.header['Character']
                path = os.path.join(dir, char + '.png')

                if self.is_drawed:
                    capture(path)

                self.t_index += 1
            else:
                glutLeaveMainLoop()
                
        self.init_opengl(display=display, keyboard=self.keyboard)
        
    def keyboard(self, key, x, y):
        u'キーが打たれたときに呼ばれるCallback関数'
        if key == 'q':
            glutLeaveMainLoop()
        elif key == 'l':
            self.t_index += 1
        elif key == 'h':
            self.t_index -= 1

    def display(self):
        u'参照データと組み立てられたデータを並べて表示する'
        sign = self.t_signs[self.t_index]
        char = sign.header['Character']
        title = u'Brush Font Generation of ' + char
        if sys.platform == 'win32':
            title = title.encode('cp932')

        brush_sign, gen_info = self.generate(sign, self.threshold)

        # 生成情報をファイルに出力
        output = [char]
        for info in gen_info:
            dist = info['dist']
            output.append(u'{:.2f}'.format(dist))
        output = ','.join(output)
        print >>sys.stderr, output
        print >>self.output, output
        self.output.flush()

        # 一つもストローク抜けがなかった場合は描画する
        if all(info['is_added'] for info in gen_info):
            #if char == u'澱':
            #    import pdb; pdb.set_trace()
            # ウィンドウに描画
            glutSetWindowTitle(title)
            glClear(GL_COLOR_BUFFER_BIT)
            self.dot_plot(sign)
            self.brush_plot(brush_sign)
            #self.correspond_plot(sign, gen_info)        
            glFlush()
            self.is_drawed = True
        else:
            self.is_drawed = False

    def dot_plot(self, sign):
        u'ドットで文字を描画する'
        glColor4d(0.0, 0.0, 0.0, 1.0)
        glPushMatrix()
        glPointSize(self.point_size)
        for stroke in sign:
            glBegin(GL_POINTS)
            for point in stroke:
                x, y = point[0], point[1]
                x = x - 1.0
                glVertex2d(x, y)
            glEnd()
        glPopMatrix()

    def generate(self, sign, threshold):
        u'引数で与えられた毛筆文字を組み立てる'
        info = []
        matched_strokes = []
        for i, stroke in enumerate(sign):
            info.append({
                'dist': float('inf'),
                'min_id': None,
                'min_path': None,
                'is_added': False,
            })

            min_id = self.dp.load_test(stroke).translate_refs(stroke[0]).match().min_id
            
            if min_id is not None:
                dist = self.dp.dp_distance(min_id)
                ref = deepcopy(self.ro_strokes[min_id])
                path = self.dp.backtrack(min_id)
                dist = float(dist) / len(path)
                
                # ref = []
                # for _i, _j in path:
                #     p = deepcopy(self.refs[min_id][_i])
                #     q = stroke[_j]
                #     w = 0.5
                #     p[0:2] = w * p[0:2] + (1 - w) * q[0:2]
                #     ref.append(p)
                #
                # ref = np.array(ref)
                
                origin = stroke[0]
                x, y = ref[:, 0], ref[:, 1]
                ref[:, 0] = x - x[0] + origin[0]
                ref[:, 1] = y - y[0] + origin[1]
                info[i]['dist'] = dist
                info[i]['min_id'] = min_id
                info[i]['min_path'] = path
                if dist < threshold:
                    matched_strokes.append(ref)
                    info[i]['is_added'] = True
                 
        sign = Signature(data=matched_strokes)
        return sign, info

    def brush_plot(self, sign):
        u'毛筆で文字を描画する'
        self.brush.dipping()
        for stroke in sign:
            for point in stroke:
                self.draw_brush(point)

    def draw_brush(self, point):
        u'引数の座標にドロップレットモデル(毛筆)を描く'
        point = deepcopy(point)
        point[3] = convert_wintab_azimuth(point[3])
        self.brush.update(point)
        print >>sys.stderr, 'state={}'.format(self.brush._state)
        
        x, y, p, azimuth, altitude, time = point
        
        max_color = 0.5
        c = 0.1#(1.0 - p) * max_color    # color := 0.0 - max_color
        glColor4d(c, c, c, 1.0)
        for i, model in enumerate(self.brush):
            if i == 0 and self.brush._state == 4:
                glColor4d(c, c, c, 0.1)
            else:
                glColor4d(c, c, c, 1.0)
                
            #glColor4d(0.0, 0.0, 1.0, 0.1)
            for droplet in model:
                glBegin(GL_POLYGON)
                for dx, dy in droplet:
                    glVertex2d(dx, dy)
                glEnd()
                
        glutPostRedisplay()
        glFlush()
        
    def correspond_plot(self, sign, gen_info):
        u'対応点を結ぶ直線を表示'
        glColor4d(1.0, 0.0, 0.0, 1.0)
        for k, stroke in enumerate(sign):
            if gen_info[k] is not None:
                path = gen_info[k]['min_path']
                min_id = gen_info[k]['min_id']
                ref = self.dp.refs[min_id]

                for i, j in path:
                    p, q = ref[i], stroke[j]
                    glBegin(GL_POINTS)
                    glVertex2d(q[0] - 1.0, q[1])
                    glVertex2d(p[0], p[1])
                    glEnd()
        

def load_signs(path, only_normalize=False):
    u'ディレクトリ内の.signデータを再帰的にリストに格納し返す(汚い関数)'
    sign_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            file = os.path.join(root, file)
            if file.endswith('.sign'):
                print >>sys.stderr, file
                sign = Signature(file)
                if not only_normalize:
                    sign.normalize_with_signature_domain(256, 256)
                    sign.liner_interpolate(sqrt(2))
                    sign.feature_sample(sqrt(2))
                sign.normalize_with_signature_domain()
                sign_list.append(sign)

    for sign in sign_list:
        oy = sign.merged_stroke[:, 1]
        a = (-oy).min()
        b = oy.min()
        for stroke in sign:
            for point in stroke:
                x, y = point[0], point[1]
                y = -y - a + b - 0.5
                point[0] = x
                point[1] = y

    return sign_list


def capture(path):
    u'OpenGLの画面をキャプチャし保存する'
    width = glutGet(GLUT_WINDOW_WIDTH)
    height = glutGet(GLUT_WINDOW_HEIGHT)
    # キャプチャ
    glReadBuffer(GL_FRONT)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
    # 画像を保存
    image = Image.fromstring("RGBA", (width, height), data)
    image = ImageOps.flip(image) # 上下反転
    image.save(path)





def main():
    disp = Display()
    disp.capture_all('../output/img/output')




if __name__ == '__main__':
    main()
