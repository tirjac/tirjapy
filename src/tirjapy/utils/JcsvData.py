# -*- coding: utf-8 -*-
#
# @project TirjaPy
# @file src/tirjapy/utils/JcsvData.py
# @author  Shreos Roychowdhury <shreos@tirja.com>
# @version 1.0.0
# 
# @section DESCRIPTION
# 
#   JcsvData.py : Handle jcsv data
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

from tirjapy.utils.HandleQuotes import HandleQuotes

class JcsvData(HandleQuotes):
	"""Class JcsvData handles jcsv data """

	def __init__(self, headers, data=None):
		""" Read from headers and data """
		if not isinstance(headers, list):
			raise ValueError("Jcsv: headers is not array")
		## store positions
		self.positions = {}
		pos = 0
		for item in headers:
			self.positions[item]=pos
			pos = pos + 1
		## init data array
		self.data = []
		if data:
			self.AddRows(data)

	def _AddRow(self, data):
		""" Add a single data unit """
		if len(data) != len(self.positions):
			raise ValueError("Jcsv _AddRow: data array has wrong length")
		self.data.append(data)

	def AddRows(self, data):
		""" Add several data unit """
		for item in data:
			self._AddRow(item)

	def GetData(self, row, cname):
		""" Get one data point by row and name"""
		if row >= len(self.data):
			raise ValueError("Jcsv GetData: exceeds no of rows")
		if cname not in self.positions:
			raise ValueError("Jcsv GetData: no such col")
		return self.data[row][ self.positions[cname] ]

	def GetCols(self, row, cnames):
		""" Get multiple data points by row and names"""
		outp = []
		for nm in cnames:
			outp.append ( self.GetData(row, nm) )
		return outp

	def _SetData(self, row, cname, cval):
		""" Set one data point by row and name"""
		if row >= len(self.data):
			raise ValueError("Jcsv GetData: exceeds no of rows")
		if cname not in self.positions:
			raise ValueError("Jcsv GetData: no such col")
		self.data[row][ self.positions[cname] ] = cval

	def SetData(self, row, data):
		""" Set one data point by row and data"""
		for item in data.keys():
			self._SetData(row, item, data[item] )

	def AddRowData(self, data):
		""" Add one data point by data object ignore unknown and missing"""
		darray = [''] * self._NoofCols()
		for cname in data.keys():
			if cname in self.positions:
				darray[ self.positions[cname] ] = str(data[cname])
		self._AddRow(darray)

	def _NoofRows(self):
		""" Get no of rows """
		return len(self.data)

	def _NoofCols(self):
		""" Get no of cols """
		return len(self.positions)

	def GetHeaders(self):
		""" get headers as array """
		headers = [''] * len(self.positions)
		for item in self.positions.keys():
			headers[ self.positions[item] ] = item
		return headers

	def GetHeadersStringB(self):
		""" get headers as back quoted string """
		headers = [''] * len(self.positions)
		for item in self.positions.keys():
			headers[ self.positions[item] ] = self._AddBackQ(item)
		return ','.join(headers)

	def GetRow(self, row):
		""" get one row data """
		if row >= len(self.data):
			raise ValueError("Jcsv GetData: exceeds no of rows")
		return self.data[row]

	def GetRows(self):
		""" get all row data """
		return self.data

	def GetRowStringQ(self, row):
		""" get one row data """
		if row >= len(self.data):
			raise ValueError("Jcsv GetData: exceeds no of rows")
		rows = []
		for item in self.data[row]:
			rows.append( self._AddQ(item) )
		return ','.join(rows)

	def GetAll(self):
		""" As data """
		return { 'headers' : self.GetHeaders(), 'data' : self.GetRows() }
