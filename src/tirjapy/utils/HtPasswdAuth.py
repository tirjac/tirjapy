# -*- coding: utf-8 -*-
#
# @project TirjaPy
# @file src/tirjapy/utils/HtPasswdAuth.py
# @author  Shreos Roychowdhury <shreos@tirja.com>
# @version 1.0.0
# 
# @section DESCRIPTION
# 
#   HtPasswdAuth.py : Decorator, configuration, and error handler for
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

from __future__ import absolute_import, unicode_literals
from loguru import logger

from functools import wraps
import hashlib
import jwt

from flask import request, Response, current_app, g
from passlib.apache import HtpasswdFile


class HtPasswdAuth:
	"""Configure htpasswd based basic and token authentication."""

	def __init__(self, app=None):
		"""Boiler plate extension init with log_level being declared"""
		self.users = HtpasswdFile()
		self.app = app
		if app is not None:
			self.init_app(app)

	def init_app(self, app):
		"""
		Find and configure the user database from specified file
		"""
		# pylint: disable=inconsistent-return-statements
		app.config.setdefault('FLASK_AUTH_ALL', False)
		app.config.setdefault('FLASK_AUTH_REALM', 'Login Required')
		# Default set to bad file to trigger IOError
		app.config.setdefault('FLASK_HTPASSWD_PATH', '/^^^/^^^')

		# Load up user database
		try:
			self.load_users(app)
		except IOError:
			logger.critical( 'No htpasswd file loaded, please set FLASK_HTPASSWD')

		# Allow requiring auth for entire app, with pre request method
		@app.before_request
		def require_auth():
			# pylint: disable=unused-variable
			"""Pre request processing for enabling full app authentication."""
			if not current_app.config['FLASK_AUTH_ALL']:
				return None
			is_valid, user = self.authenticate()
			if not is_valid:
				return self.auth_failed()
			g.user = user

	def load_users(self, app):
		"""
		Load users from configured file.

		Args:
			app (flask.Flask): Flask application to load users from.

		Raises:
			IOError: If the configured htpasswd file does not exist.
		Returns:
			None
		"""
		self.users = HtpasswdFile(
			app.config['FLASK_HTPASSWD_PATH']
		)

	def check_basic_auth(self, username, password):
		"""
		This function is called to check if a username /
		password combination is valid via the htpasswd file.
		"""
		valid = self.users.check_password(
			username, password
		)
		if not valid:
			logger.warning('Invalid login from {}', username)
			valid = False
		return (
			valid,
			username
		)

	def get_signature(self):
		"""
		Setup crypto sig.
		"""
		with self.app.app_context():
			return current_app.config['FLASK_SECRET']

	def get_hashhash(self, username):
		"""
		Generate a digest of the htpasswd hash
		"""
		userhash = self.users.get_hash(username)
		if not userhash:
			return ''
		return hashlib.sha256(userhash).hexdigest()

	def generate_token(self, username):
		"""
		assumes user exists in htpasswd file.

		Return the token for the given user by signing a token of
		the username and a hash of the htpasswd string.
		"""
		key = self.get_signature()
		return jwt.encode({
			'username': username,
			'hashhash': self.get_hashhash(username)
		}, key, algorithm="HS512")

	def check_token_auth(self, token):
		"""
		Check to see who this is and if their token gets
		them into the system.
		"""
		key = self.get_signature()
		try:
			data = jwt.decode(token, key, algorithms=["HS512"])
		except:
			logger.warning('Received bad token signature')
			return False, None
		if data['username'] not in self.users.users():
			logger.warning( 'Token auth signed message, but invalid user {}', data['username'])
			return False, None
		if data['hashhash'] != self.get_hashhash(data['username']):
			logger.warning( 'Token and password do not match, {} needs to regenerate token', data['username'])
			return False, None
		return True, data['username']

	@staticmethod
	def auth_failed():
		"""
		Sends a 401 response that enables basic auth
		"""
		return Response(
			'Could not verify your access level for that URL.\n'
			'You have to login with proper credentials',
			401,
			{'WWW-Authenticate': 'Basic realm="{0}"'.format(
				current_app.config['FLASK_AUTH_REALM']
			)}
		)

	def authenticate(self):
		"""Authenticate user by any means and return either true or false.

		Args:

		Returns:
			tuple (is_valid, username): True is valid user, False if not
		"""
		basic_auth = request.authorization
		is_valid = False
		user = None
		if basic_auth:
			is_valid, user = self.check_basic_auth(
				basic_auth.username, basic_auth.password
			)
		else:  # Try token auth
			token = request.headers.get('Authorization', None)
			param_token = request.args.get('access_token')
			if token or param_token:
				if token:
					# slice the 'token ' piece of the header (following
					# github style):
					token = token[6:]
				else:
					# Grab it from query dict instead
					token = param_token
				logger.debug('Received token: {}', token)

				is_valid, user = self.check_token_auth(token)
		return (is_valid, user)

	def required(self, func):
		"""
		Decorator function with basic and token authentication handler
		"""
		@wraps(func)
		def decorated(*args, **kwargs):
			"""
			Actual wrapper to run the auth checks.
			"""
			is_valid, user = self.authenticate()
			if not is_valid:
				return self.auth_failed()
			kwargs['user'] = user
			return func(*args, **kwargs)
		return decorated

	def async_required(self, func):
		"""
		Decorator function with basic and token authentication handler for async
		"""
		@wraps(func)
		async def decorated(*args, **kwargs):
			""" Actual wrapper to run the auth checks.  """
			is_valid, user = self.authenticate()
			if not is_valid:
				return self.auth_failed()
			kwargs['user'] = user
			return await func(*args, **kwargs)
		return decorated
