# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
#from PyQt4.QtWebKit import *
from PyQt4.QtNetwork import QHttp
from PyKDE4.plasma import Plasma
from PyKDE4.kdecore import KUrl
from PyKDE4 import plasmascript
from PyKDE4.kdeui import *
from PyQt4 import uic
import re
import urllib2
import xml.dom.minidom
import sys
import math
import ConfigParser
import os
from lineGraph import *
from metrikaConfig import *

class WelinuxKarmometer(plasmascript.Applet):
	def __init__(self,parent,args=None):
		plasmascript.Applet.__init__(self,parent)

	def init(self):

		self._config_file = ".pyMetrix.cfg" #Имя конфига
		self.rowsData = {} #Данные по метрике
		self.rowsDate = [] #Даты
		self.max = 0

		strFile = os.path.join(os.path.expanduser('~'), self._config_file)
		if os.path.exists(strFile):
			cfgParser = ConfigParser.ConfigParser()
			cfgFile = open(strFile)
			cfgParser.readfp(cfgFile)
			self.apiKey = cfgParser.get('general', 'apiKey')
			self.appId = cfgParser.get('general', 'appId')
			cfgFile.close()
		else:
			self.apiKey = "apiKey"
			self.appId = "appId"


		#Константы
		self.OAUTHURL="https://oauth.yandex.ru/authorize?response_type=token&client_id="+self.apiKey+"&display=popup";

		self.access_token = None;

		self.setHasConfigurationInterface(True)     
		self.setAspectRatioMode(Plasma.IgnoreAspectRatio)   

		self.theme = Plasma.Svg(self)
		self.theme.setImagePath("widgets/background")
		self.setBackgroundHints(Plasma.Applet.DefaultBackground)

		self.layout = QGraphicsLinearLayout(Qt.Vertical, self.applet)

		self.metrixGraph = LineGraph(self.applet)
		self.layout.addItem(self.metrixGraph)
		 
		self.applet.setLayout(self.layout)

		self.webView = Plasma.WebView(self.applet)
		self.webView.setUrl(KUrl(self.OAUTHURL))
		self.webView.urlChanged.connect(self.onChangeUrl)
		self.layout.addItem(self.webView)

		self.resize(700,700)
		self.http=QHttp(self)

		self.connect(self.http,SIGNAL("done(bool)"),self.doneHttp)

	def createConfigurationInterface(self,parent):
		defaultConfig = {"apiKey":self.apiKey,"appId":self.appId}
		self.metrikaConfig = MetrikaConfig(self,defaultConfig)
		self.configPage = parent.addPage(self.metrikaConfig,"")
		self.connect(parent, SIGNAL("okClicked()"), self.configAccepted)
		self.connect(parent, SIGNAL("cancelClicked()"), self.configDenied)

	def showConfigurationInterface(self):
		dialog = KPageDialog()
		dialog.setFaceType(KPageDialog.Plain)
		dialog.setButtons(KDialog.ButtonCode(KDialog.Ok | KDialog.Cancel))
		self.createConfigurationInterface(dialog)
		dialog.resize(400,300)
		dialog.exec_()

	def configDenied(self):
		pass

	def configAccepted(self):
		self.apiKey = self.metrikaConfig.getApiKey()
		self.appId = self.metrikaConfig.getAppId()
		cfgParser = ConfigParser.ConfigParser()
		cfgParser.read(self._config_file)
		if not cfgParser.has_section('general'):
			cfgParser.add_section('general')

		cfgParser.set('general', 'apiKey',self.apiKey)
		cfgParser.set('general', 'appId',self.appId)

		strFile = os.path.join(os.path.expanduser('~'),self._config_file)
		cfgFile = open(strFile,"w")
		cfgParser.write(cfgFile)
		cfgFile.close()

	def onChangeUrl(self,url):
		hashCode=url.fragment()#("access_token")
		reAccessToken = re.compile('(?<=access_token=).*?(&)')
		sAccessToken = reAccessToken.search(hashCode)
		self.access_token = sAccessToken.group(0).replace('&','')
		if self.access_token:
			self.webView.deleteLater()
			self.lookUp()


	def lookUp(self):
		self.http.setHost("api-metrika.yandex.ru")
		self.http.get("/stat/traffic/summary?id="+self.appId+"&access_token="+self.access_token)

	def doneHttp(self,error):
		if error:       
			self.browserResult.setText(self.http.errorString())
		else:        
			result=self.http.readAll().data()
			if result:
				xmlString = xml.dom.minidom.parseString(result)
				rowData = xmlString.getElementsByTagName('row')

				for row in rowData:
					data={}
					data['visitors'] = int(row.getElementsByTagName('visitors')[0].childNodes[0].data)

					if data['visitors']>self.max:
						self.max=data['visitors']
					date = int(row.getElementsByTagName('date')[0].childNodes[0].data)
					data['page_views'] = row.getElementsByTagName('page_views')[0].childNodes[0].data
					self.rowsDate.append(date)
					self.rowsData[date]=data

				self.rowsDate.sort()

				self.metrixGraph.addRowsDate(self.rowsDate)
				self.metrixGraph.addRowsData(self.rowsData)
				self.metrixGraph.setMax(self.max)

				#self.update()

			else:
				self.browserResult.setText("<i>User not found.</i>")

	def paintInterface(self, painter, option, rect):
		painter.save()
		painter.setPen(Plasma.Theme.defaultTheme().color(Plasma.Theme.TextColor))
		painter.setFont(Plasma.Theme.defaultTheme().font(Plasma.Theme.SmallestFont))
		painter.restore()

	#def hoverMoveEvent(self, event) :
		#print "hover"


def CreateApplet(parent):
    return WelinuxKarmometer(parent)

