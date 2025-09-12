# -*- coding: utf-8 -*-
#
# @project TirjaPy
# @file src/tirjapy/base/HandleConstants.py
# @author  Shreos Roychowdhury <shreos@tirja.com>
# @version 1.0.0
# 
# @section DESCRIPTION
# 
#   HandleConstants.py : Handle different timeouts and constants
# 
# @section LICENSE
# 
# Copyright (c) 2025 Shreos Roychowdhury.
# Copyright (c) 2025 Tirja Consulting LLP.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 

COMMA = ','
SPACE = ' '
EQUALTO = '='
NOTEQUALTO = '!='
BLANK = ''
COLON = ':'

# http post

HTTP_CONNECT_TIMEOUT     =     60                 # default http connect timeout
HTTP_READ_TIMEOUT        =    300                 # default http read timeout

LONG_CONNECT_TIMEOUT     =    600                 # long http connect timeout
LONG_READ_TIMEOUT        =    600                 # long http read timeout

# redis

TASK_CANCEL_HSET         = 'nb_def_cancel'        # task cancel hset
TASK_DO_CANCEL           = b'cancel'              # task cancel val

