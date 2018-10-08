#!/usr/bin/env python

import threading
import sys

class ReadPeople(threading.Thread):
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue
		self.is_running = True

	def run(self):
		while self.is_running:
			self.people = raw_input("How many people? ")
			self.queue.put(self.people)


	def stop(self):
		self.is_running = False
		sys.exit()