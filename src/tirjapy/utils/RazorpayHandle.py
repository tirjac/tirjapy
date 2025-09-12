# -*- coding: utf-8 -*-
#
# @project TirjaPy
# @file src/tirjapy/utils/RazorpayHandle.py
# @author  Shreos Roychowdhury <shreos@tirja.com>
# @version 1.0.0
# 
# @section DESCRIPTION
# 
#   RazorpayHandle.py : razorpay handle
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

from loguru import logger

import os
import sys
import re
import json
import urllib3
from base64 import b64encode

from tirjapy.utils.HttpPostHandle import HttpPostHandle

RAZORPAY_BASE_URL                   = 'https://api.razorpay.com'
RAZORPAY_V1                         = RAZORPAY_BASE_URL + '/v1'
RAZORPAY_V2                         = RAZORPAY_BASE_URL + '/v2'

RAZORPAY_ORDER_URL                  = RAZORPAY_V1 +  '/orders'
RAZORPAY_INVOICE_URL                = RAZORPAY_V1 +  '/invoices'
RAZORPAY_PAYMENT_LINK_URL           = RAZORPAY_V1 +  '/payment_links'
RAZORPAY_PAYMENTS_URL               = RAZORPAY_V1 +  '/payments'
RAZORPAY_REFUNDS_URL                = RAZORPAY_V1 +  '/refunds'
RAZORPAY_CARD_URL                   = RAZORPAY_V1 +  '/cards'
RAZORPAY_CUSTOMER_URL               = RAZORPAY_V1 +  '/customers'
RAZORPAY_TRANSFER_URL               = RAZORPAY_V1 +  '/transfers'
RAZORPAY_VIRTUAL_ACCOUNT_URL        = RAZORPAY_V1 +  '/virtual_accounts'
RAZORPAY_SUBSCRIPTION_URL           = RAZORPAY_V1 +  '/subscriptions'
RAZORPAY_ADDON_URL                  = RAZORPAY_V1 +  '/addons'
RAZORPAY_PLAN_URL                   = RAZORPAY_V1 +  '/plans'
RAZORPAY_SETTLEMENT_URL             = RAZORPAY_V1 +  '/settlements'
RAZORPAY_ITEM_URL                   = RAZORPAY_V1 +  '/items'
RAZORPAY_QRCODE_URL                 = RAZORPAY_V1 +  '/payments/qr_codes'
RAZORPAY_REGISTRATION_LINK_URL      = RAZORPAY_V1 +  '/subscription_registration'
RAZORPAY_FUND_ACCOUNT_URL           = RAZORPAY_V1 +  '/fund_accounts'
RAZORPAY_ACCOUNT                    = RAZORPAY_V2 +  '/accounts'
RAZORPAY_STAKEHOLDER                = RAZORPAY_V2 +  '/stakeholders'
RAZORPAY_PRODUCT                    = RAZORPAY_V2 +  '/products'
RAZORPAY_TNC                        = RAZORPAY_V1 +  '/tnc'
RAZORPAY_TOKEN                      = RAZORPAY_V1 +  '/tokens'
RAZORPAY_IIN                        = RAZORPAY_V1 +  '/iins'
RAZORPAY_WEBHOOK                    = RAZORPAY_V1 +  '/webhooks'
RAZORPAY_DOCUMENT                   = RAZORPAY_V1 +  '/documents'
RAZORPAY_DISPUTE                    = RAZORPAY_V1 +  '/disputes'
RAZORPAY_DEVICE_ACTIVITY_URL        = RAZORPAY_V1 +  '/devices/activity'

RAZORPAY_USER_AGENT = os.environ.get('RAZORPAY_USER_AGENT', 'Razorpay-Python/1.4.2 TirjaPy/1.1.2')

class RazorpayHandle(HttpPostHandle):

	def __init__(self):
		""" init fx inits handles """
		super().__init__()
		self.username = os.environ["RAZORPAY_KEY_ID"]
		self.passwd = os.environ["RAZORPAY_KEY_SECRET"]

	def _PopulateBasicHeaderCreds(self, headers, username, passwd):
		""" function to load username password in headers """
		if len(username)>0 and len(passwd)>0:
			use_creds = ':'.join([username,passwd])
			base64creds = b64encode(use_creds.encode('ascii'))
			headers['Authorization'] = "Basic {}".format(base64creds.decode('ascii'))
		headers['User-Agent'] = RAZORPAY_USER_AGENT

	def _PostJsonData(self, data, url, username, passwd, post='POST'):
		""" post file as json data """

		if len(url)<6:
			raise ValueError("url cannot be empty")
		## handle headers
		headers = {}
		self._PopulateBasicHeaderCreds( headers, username, passwd )
		headers['Content-Type'] = 'application/json'

		output = { 'error' : True , 'status' : 'unknown' }
		r = self.http.request( post, url, headers=headers, body=json.dumps(data))
		# print(r.status)

		if r.status==200:
			output = json.loads( r.data.decode('utf-8') )
		else:
			try:
				logger.warning("RZP Error: {}" , r.data.decode('utf-8'))
			except:
				logger.warning("RZP Error: UNKNOWN")
		return output

	def _GetJsonData(self, url, username, passwd, fields={}):
		""" get file as json data """

		if len(url)<6:
			raise ValueError("url cannot be empty")
		## handle headers
		headers = {}
		self._PopulateBasicHeaderCreds( headers, username, passwd )
		output = { 'error' : True , 'status' : 'unknown' }

		r = self.http.request( 'GET', url, headers=headers, fields=fields)

		if r.status==200:
			output = json.loads( r.data.decode('utf-8') )
		else:
			try:
				logger.warning("RZP Error: {}" , r.data.decode('utf-8'))
			except:
				logger.warning("RZP Error: UNKNOWN")
		return output

	def GetData(self, url, xdata={}):
		""" get items as json data """
		return self._GetJsonData(url, self.username, self.passwd, xdata)

	def PostData(self, url, xdata):
		""" post items as json data """
		return self._PostJsonData(xdata, url, self.username, self.passwd)

	def PatchData(self, url, xtra, xdata):
		""" patch items as json data """
		return self._PostJsonData(xdata, f"{url}/{xtra}", self.username, self.passwd, 'PATCH')

