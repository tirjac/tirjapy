# -*- coding: utf-8 -*-
#
# @project TirjaPy
# @file src/tirjapy/utils/RedisHandle.py
# @author  Shreos Roychowdhury <shreos@tirja.com>
# @version 1.0.0
# 
# @section DESCRIPTION
# 
#   RedisHandle.py : Redis handlers
# 
# @section LICENSE
# 
# Copyright (c) 2025 Shreos Roychowdhury.
# Copyright (c) 2025 Tirja Consulting LLP.
# 
# This source code is protected under international copyright law.  All rights
# reserved and protected by the copyright holders.
#
# This file is confidential and only available to authorized individuals with the
# permission of the copyright holders.  If you encounter this file and do not have
# permission, please contact the copyright holders and delete this file.
#
# THE SOFTWARE IS PROVIDED , WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 

import os
import sys
import json
from redis import Redis
from rq import Worker, Queue, Connection
from rq.job import Job, JobStatus

from tirjapy.utils.HandleQuotes import HandleQuotes
from tirjapy.base.StoreBase import TaskState
from tirjapy.base.HandleConstants import TASK_CANCEL_HSET, TASK_DO_CANCEL

class RedisHandle(HandleQuotes):

	rds_creds = None

	def __init__(self):
		""" constructor default"""
		self.is_init = False
		if RedisHandle.rds_creds:
			self._Initialize()

	def _SanityCheck(self):
		""" check if globals set """
		if not self.is_init:
			raise ValueError("Globals not set for Redis Handle")

	def RegisterGlobals(self, params):
		"""Register Global fx"""

		RedisHandle.rds_creds = {
			'host' : self._RequiredField(params, 'host'),
			'port' : self._RequiredField(params, 'port'),
			'queue' : self._RequiredField(params, 'queue'),
		}
		self._Initialize()

	def _Initialize(self):
		""" Init fx"""
		self.conn = Redis(host=RedisHandle.rds_creds['host'], port=RedisHandle.rds_creds['port'])
		self.queue = RedisHandle.rds_creds['queue']
		self.is_init = True

	def GetRedisUrl(self):
		""" Get redis url """
		self._SanityCheck()
		return 'redis://' + RedisHandle.rds_creds['host'] + ':' + RedisHandle.rds_creds['port']

	def GetConn(self):
		""" Get redis conn """
		self._SanityCheck()
		return self.conn

	def GetQueue(self):
		""" Get redis queue """
		self._SanityCheck()
		return self.queue

	def GetJobStatus(self, queue_id):
		""" gets redis task by queue_id, return state and job """
		self._SanityCheck()
		## check if key exists in redis
		if not Job.exists(queue_id, connection=self.conn):
			return TaskState.NOTFOUND
		## check job status
		job = Job.fetch(queue_id, connection=self.conn)
		job_status = job.get_status(refresh=True)
		task_state_map = {
			JobStatus.QUEUED     :  TaskState.QUEUED,
			JobStatus.FAILED     :  TaskState.FAILED,
			JobStatus.STARTED    :  TaskState.ONGOING,
			JobStatus.FINISHED   :  TaskState.DONE,
			JobStatus.DEFERRED   :  TaskState.ACCEPTED,
			JobStatus.SCHEDULED  :  TaskState.ACCEPTED
		}
		task_state = task_state_map[job_status] if job_status in task_state_map else TaskState.NOTFOUND
		return task_state

	def SetCancelByJobKey(self, queue_id):
		""" set cancel redis task by queue_id, return true/false or throw """
		self._SanityCheck()
		job = Job.fetch(queue_id, connection=self.conn)
		job_status = job.get_status(refresh=True)
		## cancel it queued, set if started
		if job_status == JobStatus.QUEUED or job_status == JobStatus.DEFERRED or job_status == JobStatus.SCHEDULED:
			job.delete()
			return True
		elif job_status == JobStatus.STARTED:
			self.conn.hset( TASK_CANCEL_HSET, queue_id, TASK_DO_CANCEL )
			return False
		## raise exception if reaches here
		raise ValueError("Cannot Cancel this job")

	def CheckCancelByJobKey(self, queue_id, dont_delete=False):
		""" check if task is cancelled """
		self._SanityCheck()
		if self.conn.hget( TASK_CANCEL_HSET, queue_id) == TASK_DO_CANCEL:
			if not dont_delete:
				self.conn.hdel( TASK_CANCEL_HSET, queue_id)
			return True
		return False

	def _GetQData(self):
		""" check all queue data """
		self._SanityCheck()
		return {
			q.name: {
				'name': q.name,
				'queued': len(q.job_ids)
			} for q in Queue.all(connection=self.conn)}

	def _GetQWorkers(self):
		""" check all worker data """
		self._SanityCheck()
		return [{
			'name': w.name,
			'hostname': w.hostname,
			'pid': w.pid,
			'queues': ", ".join([q.name for q in w.queues]),
			'state': w.state,
			'last_heartbeat': w.last_heartbeat,
			'start_date': w.birth_date,
			'successful_jobs': w.successful_job_count,
			'failed_jobs': w.failed_job_count,
			'total_working_time': w.total_working_time
		} for w in Worker.all(connection=self.conn)]


	def GetInfo(self):
		""" get web info """
		return {
			'queues': self._GetQData(),
			'workers': self._GetQWorkers()
		}

