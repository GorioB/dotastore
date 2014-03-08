import httplib,re,getprices,datetime
from utilscripts import *
import legasearch

class StoreObject:
	def __init__(self,name,price,link,ident,color):
		self.name=name
		self.price=price
		self.time=datetime.datetime.now().strftime("%H-%M-%S")
		self.link=link
		self.ident=ident
		self.color=color

	def get(self):
		if self.color==None:
			return(self.name,self.price,self.time,self.ident,self.link)
		else:
			return(self.name,self.price,self.time,','.join(self.color),self.link)


	def listString(self):
		if self.color==None:
			return(self.time+"    "+self.name.split("?filter")[0]+" - "+self.price)
		else:
			return(self.time+"    "+self.color[0]+","+self.color[1]+","+self.color[2]+":"+self.name.split("?filter")[0]+":"+" -"+self.price)

	def getId(self):
		return self.ident

class StoreConn():
	def __init__(self,host):
		try: self.conn=httplib.HTTPConnection(host)
		except: return 1

		self.stock=[]
		self.itemList=[]
		
	def recon(self,host):
		try: self.conn=httplib.HTTPConnection(host)
		except: return 1

	def stockFind(self,item):
		gUp = giveUp(self.conn)
		itemCount=0
		self.stock=[]
		if(tryHttpRequest(funct=self.conn.connect)[0]):
			print "[-] Cannot connect in storesearch.py"
			if(gUp()[0]):
				print "[-] Error closing connection. Odd"
			return 0
		item=item.replace(" ","%20")
		if(tryHttpRequest(funct=self.conn.request,vars=("GET","/market/search/render?query=appid%3A570+"+item+"&start=0&count=200"))[0]):
			print "[-] GET request failed in storesearch.py"
			if(gUp()[0]):
				print "[-] Error closing connection. Odd"
			return 0
		r1=tryHttpRequest(funct=self.conn.getresponse)
		if(r1[0]):
			print "[-] get response failed in storesearch.py"
			if(gUp()[0]):
				print "[-] Error closing connection. Odd"
			return 0
		r1 = r1[1]
		print "[+]",r1.status,"for",item,"in storesearch.py"
		if r1.status!=200:
			if(gUp()[0]):
				print "[-] Error closing connection. Odd"
			return 0

		data=r1.read()
		if(gUp()[0]):
			print "[-] Error closing connection. Odd"

		quotelist=re.findall('(?<=\")(.*?)(?=\")',data)
		for i in quotelist:
			if(i[:20]=="http:\\/\\/steamcommunity.com\\/market\\/listings"[:20]):
				self.stock.append(''.join(i.split("\\"))[25:])
				itemCount+=1
		return itemCount

	def listItems(self,qstring):
		pricesHash=getprices.getPrices(self.conn,qstring)
		if pricesHash[0]:
			return []
		pricesHash=pricesHash[1]
		returnString=[]
		for i in range(0,len(pricesHash)):
			returnString.append(StoreObject(qstring[21:],pricesHash[i][1],"",pricesHash[i][0],None))

		return returnString

	def listItemsColored(self,qstring):
		pricesHash=legasearch.getColors(self.conn,qstring)
		if pricesHash[0]:
			return []
		returnString=[]
		pricesHash=legasearch.nuke(pricesHash)
		pricesHash=pricesHash[1]
		for i in range(0,len(pricesHash)):
			returnString.append(StoreObject(qstring[21:],pricesHash[i][1],"",pricesHash[i][0],pricesHash[i][2]))

		return returnString

	def updateItemListLegacy(self,qstring):
		templist = self.listItemsColored(qstring)
		realtemplist=[]
		inflag=False
		for i in templist:
			for y in self.itemList:
				print i.ident==y.ident
				if i.ident==y.ident:
					inflag=True
			if inflag==False:
				realtemplist.append(i)
			inflag=False


		self.itemList=self.itemList+realtemplist
		return realtemplist

	def updateItemList(self,qstring):
		templist = self.listItems(qstring)
		realtemplist=[]
		inflag=False
		for i in templist:
			for y in self.itemList:
				if i.ident==y.ident:
					inflag=True
			if inflag==False:
				realtemplist.append(i)
			inflag=False

		self.itemList=self.itemList+realtemplist
		return realtemplist

if __name__=="__main__":
	store=StoreConn("steamcommunity.com")
	store.stockFind("snowdrop")
	store.updateItemListLegacy("/market/listings/570/Unusual%20Enduring%20War%20Dog")
	for i in store.itemList:
		print i.listString().encode('utf-8'),i.color


