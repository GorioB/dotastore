import json
import sys

class CommunityStoreFile:
	def __init__(self,success,start,end,total,html):
		self.start=start
		self.end=int(end)+start
		self.html=html
		self.success = success
		self.total = total

def extractHtml(jsonfile):
	j = json.loads(jsonfile)
	c = CommunityStoreFile(j['success'],j['start'],j['pagesize'],j['total_count'],j['results_html'])
	return c

def tryHttpRequest(**kwargs):
	if len(kwargs)==1:
		try:
			return (0,kwargs['funct']())
		except:
			print sys.exc_info()[:2]
			return (1,1)
	else:
		try:
			return (0,kwargs['funct'](*kwargs['vars']))
		except:
			print sys.exc_info()[:2]
			return (1,1)
def giveUp(connection):
	def gUp():
		return tryHttpRequest(funct=connection.close)
	return gUp

if __name__ =="__main__":
	d = extractHtml('{"success":true,"start":0,"pagesize":100,"total_count":100,"results_html":"stuff"}')
	print d.start, d.end, d.html, d.success, d.total