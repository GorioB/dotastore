import httplib, re, itertools
from bs4 import BeautifulSoup
from utilscripts import *

def extract_price(text):
	for i in ["\\n","\\r","\\t"]:
		text = text.replace(i,'')
	text=re.split(r"<\\/span>",text)[0]
	return text

def getPrices(conn,query,start=0,count=100):
	gUp = giveUp(conn)
	if(tryHttpRequest(funct=conn.connect)[0]):
		print "[-] Failure to connect for",query,"in getprices.py"
		return (1,[])
	splitquery = query.split("?filter=")
	if len(splitquery)==2:
		if(tryHttpRequest(funct=conn.request,vars=("GET",splitquery[0]+"/render?query=&start="+str(start)+"&count="+str(count)+"&filter="+splitquery[1]))[0]):
			print "[-] Cannot send request for",query,"in getprices.py"
			if(gUp()[0]):
				print "[-] Error closing connection. Odd"
			return (1,[])
	elif len(splitquery)==1:
		if(tryHttpRequest(funct=conn.request,vars=("GET",query+"/render?query=&start="+str(start)+"&count="+str(count)))[0]):
			print "[-] Cannot send request for",query,"in getprices.py"
			if(gUp()[0]):
				print "[-] Error closing connection. Odd"
			return (1,[])
	else:
		print "[-] Invalid query"
		return (1,[])
	r1 = tryHttpRequest(funct=conn.getresponse)
	if r1[0]:
		print "[-] Cannot get response to", query,"in getprices.py"
		if(gUp()[0]):
				print "[-] Error closing connection. Odd"
		return (1,[])

	print "[+]",r1[1].status
	try:
		data=r1[1].read()
	except:
		print "[-] Read failed"
		return (1,[])
	if(gUp()[0]):
		print "[-] Error closing connection. Odd"
		return (1,[])
	data = extractHtml(data)
	soup = BeautifulSoup(data.html)
	e=[]
	priceList=[]
	idList=[]
	retHash=[]
	for i in soup.find_all('span',class_="market_listing_price market_listing_price_with_fee"):
		priceList.append(i.string.strip())
	for i in soup.find_all('span',class_="market_listing_item_name"):
		idList.append(i.get('id').strip())
	for i in range(0,len(idList)):
		retHash.append([idList[i],priceList[i]])

	#if(data.end<data.total):
	#	return (0,retHash+getPrices(conn,query,start=start+100,count=count+100)[1])
	#
	#else:
	#	return (0,retHash)
	return (0,retHash)

if __name__=="__main__":
	con = httplib.HTTPConnection("steamcommunity.com")
	e=getPrices(con,"/market/listings/570/Trusty%20Mountain%20Yak")
	print e
