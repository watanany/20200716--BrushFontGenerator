#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import copy
from collections import OrderedDict
from StringIO import StringIO

class Header(OrderedDict):
    def __init__(self, path=None, buffer=None):
        super(Header, self).__init__()
        self.path = None
        
        if path is not None:
            self.load_from_file(path)
            
        elif buffer is not None:
            self.load_from_buffer(buffer)

    def __str__(self):
        io = StringIO()
        for key, val in self.items():
            if key == 'Normalized':
                body = '; '.join('T' if v else 'F' for v in val)
            elif isinstance(val, int):
                body = str(val)
            elif isinstance(val, basestring):
                body = val
            else:
                body = '; '.join(str(v) for v in val)
                
            print >>io, '{}:\t{}'.format(key, body)
            
        return io.getvalue()

    def __copy__(self):
        return copy.deepcopy(self)
        
    def __deepcopy__(self, memo):
        header = self.__class__()
        header.path = self.path
        header.update(self)
        return header
                
    def load_from_file(self, path):
        self.clear()

        with codecs.open(path, 'r', 'utf-8') as r:
            for line in r:
                line = line.rstrip()
                if line != '':
                    header_name, body_list = self.parse(line)
                    self[header_name] = body_list
                else:
                    break

        self.path = path

    def load_from_buffer(self, buffer):
        self.clear()
        
        for line in StringIO(buffer):
            line = line.rstrip()
            if line != '':
                header_name, body_list = self.parse(line)
                self[header_name] = body_list
            else:
                break

    @classmethod
    def parse(cls, line):
        header_name, body = [w.strip() for w in line.split(':')]
        body_list = [w.strip() for w in body.split(';')]

        if header_name == 'Character':
            result_list = [
                cls.parse_string(header_name, body_list),
            ]
        else:
            result_list = [
                cls.parse_boolean(header_name, body_list),
                cls.parse_number(header_name, body_list),
                cls.parse_string(header_name, body_list),
            ]

        result = [r for r in result_list if r is not None][0]
        result = result if len(result) != 1 else result[0]
        return header_name, result

    @classmethod
    def parse_boolean(cls, header_name, body_list):
        if all(w == 'T' or w == 'F' for w in body_list):
            return tuple(True if w == 'T' else False for w in body_list)
        else:
            return None

    @classmethod
    def parse_number(cls, header_name, body_list):
        if all(w.isdigit() for w in body_list):
            try:
                res = tuple(int(w) for w in body_list)
            except ValueError:
                res = tuple(float(w) for w in body_list)
                
            return res
        else:
            return None

    @classmethod
    def parse_string(cls, header_name, body_list):
        return tuple(body_list)
