import httplib,re
from bs4 import BeautifulSoup
from utilscripts import *
from getprices import *

def extractPairings(data):
	match = data.split(';')
	match2 =[]
	res={}
	for i in range(0,len(match)):
		if i%2==0:
			match2.append(match[i].strip())
	match2.pop(-1)
	for i in match2:
		res[i.split(",")[1].strip().strip("\'")]=i.split(",")[4].strip().strip("\'")
	return res

def getColors(conn,query,start=0,count=100):
	gUp = giveUp(conn)
	if(tryHttpRequest(funct=conn.connect)[0]):
		print "[-] Failure to connect for",query,"in legasearch.py"
		return (1,1)
	if(tryHttpRequest(funct=conn.request,vars=("GET",query+"/render?query=&start="+str(start)+"&count="+str(count)))[0]):
		print "[-] Cannot send request for",query,"in legasearch.py"
		gUp()
		return (1,1)
	r1 = tryHttpRequest(funct=conn.getresponse)
	if r1[0]:
		print "[-] Cannot get response to",query,"in legasearch.py"
		gUp()
		return (1,1)
	print "[+]",r1[1].status
	try:
		data=r1[1].read()
	except:
		print "[-] Read failed"
		return {}
	gUp()
	data = json.loads(data)
	soup = BeautifulSoup(data['results_html'])
	match = data['hovers']
	pairings = extractPairings(match)
	colors = data['assets']['570']['2']

	priceList=[]
	idList=[]
	retHash=[]
	for i in soup.find_all('span',class_="market_listing_price market_listing_price_with_fee"):
		priceList.append(i.string.strip())
	for i in soup.find_all('span',class_="market_listing_item_name"):
		idList.append(i.get('id').strip())
	for i in range(0,len(idList)):
		retHash.append([idList[i],priceList[i]])

	for i in range(0,len(retHash)):
		try:
			retHash[i].append(map(lambda it: it.strip(),colors[pairings[retHash[i][0]]]['descriptions'][3]['value'].split(">")[1].split("<")[0].split(",")))
		except:
			pass

	if((int(data['start'])+int(data['pagesize']))<data['total_count']):
		return (0,retHash+getColors(conn,query,start=start+100,count=count+100)[1])

	return (0,retHash)

def createColorTable(o):
	ret = []
	with open(o,"r") as f:
		for line in f:
			if line[0]!="#":
				ret.append([unicode(line.split(",")[0].strip()),unicode(line.split(",")[1].strip()),unicode(line.split(",")[2].strip())])
	return ret

def compColors(objectAtHand):
	colorTable = createColorTable("nonlegacy.txt")
	for i in colorTable:
		if i[0]==objectAtHand[2][0] and i[1]==objectAtHand[2][1] and i[2]==objectAtHand[2][2]:
			return False

	return True

def nuke(retHash):
	newRetHash=filter(compColors,retHash[1])
	return (retHash[0],newRetHash)


if __name__=="__main__":
	con=httplib.HTTPConnection("steamcommunity.com")
	#e=getPrices(con,"/market/listings/570/Unusual%20Itsy")
	#e=getPrices(con,"/market/listings/570/Unusual%20Trusty%20Mountain%20Yak")
	#n = getColors(con,"/market/listings/570/Unusual%20Itsy",e)
	n=getColors(con,"/market/listings/570/Unusual%20Trusty%20Mountain%20Yak")
	#print n

	print nuke(n)