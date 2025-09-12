# -*- coding: utf-8 -*-
#
# @project TirjaPy
# @file src/tirjapy/utils/CalyrexHandle.py
# @author  Shreos Roychowdhury <shreos@tirja.com>
# @version 1.0.0
# 
# @section DESCRIPTION
# 
#   CalyrexHandle.py : handle server urls
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

import os
import sys
import json
import re
import uuid
from pathlib import Path
from datetime import datetime, timezone
from Crypto.Cipher import AES
import base64
import random
import string

from tirjapy.utils.HandleQuotes import HandleQuotes

class CalyrexHandle(HandleQuotes):
	"""This class needs init, so the constructor is blank"""

	cx_creds = None

	def __init__(self):
		""" constructor default"""
		pass

	def _SanityCheck(self):
		""" check if globals set """
		if not CalyrexHandle.cx_creds:
			raise ValueError("Globals not set for Calyrex")

	def RegisterGlobals(self, params):
		"""Register Global fx"""
		CalyrexHandle.cx_creds = {
			'domain' : self._RequiredField(params, 'domain'),
			'bucket' : self._RequiredField(params, 'bucket'),
			'skey' : self._RequiredField(params, 'skey'),
			'ttls' : self._RequiredField(params, 'ttls')
		}

	def _MakeAccessKey(self, data):
		""" has `ts` , `user` , `uri`, `ipaddr`"""
		usekey=base64.b64decode(CalyrexHandle.cx_creds['skey'])
		## crypto starts
		BS=AES.block_size
		iv = ''.join(random.choices(string.ascii_lowercase + string.digits, k = BS))
		# aes = AES.new(key, AES.MODE_CBC, bytes(iv,'utf8'))
		aes = AES.new(usekey, AES.MODE_CBC, iv.encode('utf8'))
		pad = BS - len(data) % BS
		data = data + pad * chr(pad)
		encrypted = aes.encrypt(data.encode('utf8'))
		return iv+base64.urlsafe_b64encode(encrypted).decode('utf-8')

	def _MakeAccessUri(self, ts, user, fname, ipaddr='127.0.0.1'):
		""" need `ts` , `user` , `uri`, `ipaddr`"""
		new_fname = fname if fname.startswith('/') else str('/' + fname)
		data = '|'.join([ ts, user, new_fname, ipaddr ])
		return new_fname + '?accesskey=' + self._MakeAccessKey( data )

	def _FormatOneTaskEntry(self, user, data):
		""" removes and adds file fields to Task """

		self._SanityCheck()
		del_fields = ['s3_bucket', 'pptx_fpath','json_fpath']
		## will delete the fields anyway
		for fld in del_fields:
			if fld not in data:
				raise ValueError("Missing Field in data")

		ts = str(int(datetime.now(timezone.utc).replace(tzinfo=timezone.utc).timestamp()))
		dom  = 'https://' + CalyrexHandle.cx_creds['domain']

		## add anyway
		data['pptx_url'] = ''
		data['json_url'] = ''

		if CalyrexHandle.cx_creds['bucket'] == data['s3_bucket']:
			pptx_s3_path = data['pptx_fpath']
			if len(pptx_s3_path)>0:
				data['pptx_url'] = dom + self._MakeAccessUri( ts, user, pptx_s3_path)
			json_s3_path = data['json_fpath']
			if len(json_s3_path)>0:
				data['json_url'] = dom + self._MakeAccessUri( ts, user, json_s3_path)

		## delete the fields anyway
		for fld in del_fields:
			if fld in data:
				del data[fld]

		return data

	def GetURL(self, user, s3_bucket, s3_path):
		""" gets url format filestore data """

		self._SanityCheck()

		## add anyway
		data = ''

		if CalyrexHandle.cx_creds['bucket'] != s3_bucket:
			return data
		if len(s3_path)>0:
			ts = str(int(datetime.now(timezone.utc).replace(tzinfo=timezone.utc).timestamp()))
			dom  = 'https://' + CalyrexHandle.cx_creds['domain']
			data = dom + self._MakeAccessUri( ts, user, s3_path)

		return data

