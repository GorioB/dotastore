import Tkinter as tk
import threading, time, random, datetime
from storesearch import StoreObject,StoreConn
import re
import winsound
import sys
 
sema = threading.Semaphore()
def legaSearch(widget,value):
	store=StoreConn("steamcommunity.com")
	while(1):
		try:
			print "[*] Legacy Finding "+value
			ilist=store.updateItemListLegacy(value)
			discoLegacy(ilist,widget)
		except:
			print sys.exc_info()[:2],"\n"
			print "[-] Some problems with legacy finder. Attempting to recreate connection"
			store.recon("steamcommunity.com")

def discoLegacy(ilist,widget):
	if ilist!=[]:
		winsound.Beep(660,100)
	for i in ilist:
		i.name=re.sub("%20"," ",i.name)
		widget.addLegacyItem(i)
		widget.legacyListBox.insert(0,i.listString())

def defaultSearch(widget,value):
	store=StoreConn("steamcommunity.com")
	while(1):
		try:
			print "[*] Default finding "+value
			ilist = store.updateItemList(value)
			discovery(ilist,widget)
		except:
			print sys.exc_info()[:2],"\n"
			print "[-] Some problems. Attempting to recreate connection"
			store.recon("steamcommunity.com")

def listStoreContents(widget,value):
	store = StoreConn("steamcommunity.com")
	widget.yellowTextVar.set("Loading Market Search...")
	store.stockFind(value)
	widget.redList.delete(0,tk.END)
	widget.redItems=[]
	for i in store.stock:
		j = i[21:]
		j = re.sub("%20"," ",j)
		widget.redList.insert(tk.END,j)
		widget.redItems.append(j)
	store.close()
	widget.yellowTextVar.set("OK!")
	return 0

def discovery(ilist,widget):
	if ilist!=[]:
		winsound.Beep(440,500)
	for i in ilist:
		i.name = re.sub("%20"," ",i.name)
		widget.addItem(i)
		widget.listbox.insert(0,i.listString())

def pipeDataToWidget(widget,index,value):
	store = StoreConn("steamcommunity.com")
	store.stockFind(value)
	while 1:
		try:
			print "[*] finding: "+store.stock[index]
			widget.yellowTextVar.set("Working")
			ilist = store.updateItemList(store.itemList[index])
			discovery(ilist,widget)
			widget.yellowTextVar.set("Found!")
		except:
			print "[-] some problems. Attempting to reconnect"
			store.recon()

	
class Application(tk.Frame):
	def __init__(self,parent):
		tk.Frame.__init__(self,parent,background="white")
		self.parent=parent
		self.itemList=[]
		self.redItems=[]
		self.legacyItemList=[]
		self.initUI()
		self.defaultThreads=[]
		self.legaThreads=[]
		try:
			with open("unusualcouriers.txt","r") as f:
				for line in f:
					if line[0]!="#":
						self.legaThreads.append(threading.Thread(target=legaSearch,args=(self,line.strip('\n')[25:])))
						self.legaThreads[-1].daemon=True
						self.legaThreads[-1].start()
		except:
			print sys.exc_info()[:2]
			print "[-] Failed to init legacy search"
		try:
			with open("defaults.txt","r") as f:
				for line in f:
					if line[0]!="#":
						self.defaultThreads.append(threading.Thread(target=defaultSearch,args=(self,line.strip('\n')[25:])))
						self.defaultThreads[-1].daemon=True
						self.defaultThreads[-1].start()
				self.yellowTextVar.set("Loaded defaults.txt")
		except:
			self.yellowTextVar.set("Failed to load defaults.txt")

	def addItem(self,item):
		self.itemList.insert(0,item)

	def addLegacyItem(self,item):
		self.legacyItemList.insert(0,item)

	def initUI(self):
		self.parent.title("Dota Community Store Notifier")
		self.initFrames()
		self.initButtons()
		self.initList()
		self.yellowBox()
		self.redLeader()
		self.pack(fill=tk.BOTH,expand=1)

	def initButtons(self):
		self.queryBox = tk.Entry(self.frame1a)
		self.queryBox.focus_set()

		self.searchButton = tk.Button(self.frame1a,text="Search",command=self.buildSearch)
		self.searchButton.pack(side=tk.BOTTOM,fill=tk.X)
		self.queryBox.pack(side=tk.BOTTOM,fill=tk.X)

	def redLeader(self):
		self.redScrollFrame=tk.Frame(self.frame1a)
		self.redScrollFrame.pack(side=tk.BOTTOM,fill=tk.BOTH)
		self.redScroll=tk.Scrollbar(self.redScrollFrame,orient=tk.VERTICAL)
		self.redList = tk.Listbox(self.redScrollFrame,yscrollcommand=self.redScroll.set,exportselection=0)
		self.redScroll.config(command=self.redList.yview)
		self.redScroll.pack(side=tk.RIGHT,fill=tk.Y)
		self.redList.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
		self.redList.bind('<<ListboxSelect>>',self.startListener)

		#for i in ("Tournament Snowdrop Hood","Tournament Snowdrop Mittens","Tournament Snowdrop Tassels","Tournament Snowdrop Staff","Tournament Snowdrop Mantle"):
		#	self.redList.insert(tk.END,i)
		#	self.redItems.append(i)


	def yellowBox(self):
		self.yellowTextVar = tk.StringVar()
		self.yellowTextVar.set("Hello!")
		self.yellowText = tk.Label(self.frame1b,textvariable=self.yellowTextVar) #YELLOWTEXT
		self.yellowText.pack(side=tk.BOTTOM,fill=tk.X)
		self.yellowBaby = tk.Frame(self.frame1b,background="yellow")
		self.yellowBaby.pack(side=tk.BOTTOM,fill=tk.X)
		self.labels=[]
		self.ybentries=[]
		self.yellowBaby.columnconfigure(1,weight=1)
		for i in ("Name: ","Price: ","Time: ","Id: "):
			self.labels.append(tk.Label(self.yellowBaby,text=i,anchor=tk.W,background="yellow"))
			self.labels[-1].grid(column=0,sticky=tk.W)

		for i in ("Name: ","Price: ","Time: ","Id: "):
			self.ybentries.append(tk.Entry(self.yellowBaby,background="yellow"))
			self.ybentries[-1].insert(0,i)
			self.ybentries[-1].configure(state='readonly')
			self.ybentries[-1].grid(column=1,sticky=tk.N+tk.S+tk.E+tk.W,row=self.ybentries.index(self.ybentries[-1]))


	def initList(self):
		self.scrollbar = tk.Scrollbar(self.frame2a,orient=tk.VERTICAL)
		self.listbox = tk.Listbox(self.frame2a,yscrollcommand=self.scrollbar.set,exportselection=0)
		self.scrollbar.config(command=self.listbox.yview)
		self.scrollbar.pack(side=tk.RIGHT,fill=tk.Y)
		self.listbox.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
		self.listbox.bind('<<ListboxSelect>>',self.changeYellowtext)
		for item in self.itemList:
			self.listbox.insert(tk.END,item.name+": "+item.price)

		self.scrollbarb = tk.Scrollbar(self.frame2b,orient=tk.VERTICAL)
		self.legacyListBox=tk.Listbox(self.frame2b,yscrollcommand=self.scrollbarb.set,exportselection=0)
		self.scrollbarb.config(command=self.legacyListBox.yview)
		self.scrollbarb.pack(side=tk.RIGHT,fill=tk.Y)
		self.legacyListBox.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
		self.legacyListBox.bind('<<ListboxSelect>>',self.changeLegacytext)
		for item in self.legacyItemList:
			self.legacyListBox.insert(tk.END,item.name+": "+item.price)


	def initFrames(self):
		self.frame1 = tk.Frame(self.parent,width=150,height=300,background="blue")
		self.frame1a = tk.Frame(self.frame1,width=150,height=150,background="red")
		self.frame1b = tk.Frame(self.frame1,width=150,height=150,background="yellow")
		self.frame1aa = tk.Frame(self.frame1a,width=150)
		self.frame2 = tk.Frame(self.parent,width=600,height=300,background="green")
		self.frame2a = tk.Frame(self.frame2,width=200,height=300,background="green")
		self.frame2b = tk.Frame(self.frame2,width=400,height=300,background="green")

		self.frame1.pack(side=tk.LEFT,expand=1,fill=tk.BOTH)
		self.frame2.pack(side=tk.LEFT,expand=1,fill=tk.BOTH)
		self.frame2a.pack(side=tk.LEFT,expand=1,fill=tk.BOTH)
		self.frame2b.pack(side=tk.LEFT,expand=1,fill=tk.BOTH)
		self.frame1a.pack(side=tk.TOP,fill=tk.X)
		self.frame1a.pack_propagate(0)
		self.frame1aa.pack(side=tk.BOTTOM,fill=tk.X)
		self.frame1b.pack(side=tk.TOP,fill=tk.X)
		self.frame2.pack_propagate(0)
		self.frame1b.pack_propagate(0)

	def startListener(self,event):
		w = event.widget
		index = int(w.curselection()[0])
		value= self.queryBox.get()
		self.thread = threading.Thread(target=pipeDataToWidget,args=(self,index,value))
		self.thread.daemon=True
		self.thread.start()

	def buildSearch(self):
		value = self.queryBox.get()
		if value=="":return 0
		threading.Thread(target=listStoreContents,args=(self,value)).start()
		print "yo"

	def changeLegacytext(self,event):
		w = event.widget
		index=int(w.curselection()[0])
		value=self.legacyItemList[index].get()
		for i in range(0,4):
			self.ybentries[i].configure(state=tk.NORMAL)
			self.ybentries[i].delete(0,tk.END)
			self.ybentries[i].insert(0,value[i])
			self.ybentries[i].configure(state='readonly')

	def changeYellowtext(self,event):
		w = event.widget
		index=int(w.curselection()[0])
		value=self.itemList[index].get()
		for i in range(0,4):
			self.ybentries[i].configure(state=tk.NORMAL)
			self.ybentries[i].delete(0,tk.END)
			self.ybentries[i].insert(0,value[i])
			self.ybentries[i].configure(state='readonly')




def main():
	root=tk.Tk()
	app = Application(root)
	root.mainloop()

if __name__=='__main__':
	main()
