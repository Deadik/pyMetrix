# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ConfigParser
import datetime
import os
import re
import xml.dom.minidom

from PyKDE4 import plasmascript
from PyKDE4.kdecore import KUrl
from PyKDE4.kdeui import *
from PyKDE4.plasma import Plasma
from PyQt4 import uic
from PyQt4.QtNetwork import QHttp
from lineGraph import *
from metrikaConfig import *

'''
Comment
'''

class PyMetrix(plasmascript.Applet):
    def __init__(self, parent, args=None):
        plasmascript.Applet.__init__(self, parent)

    def init(self):
        self._config_file = ".pyMetrix.cfg"
        self.rowsData = {}
        self.rowsDate = []
        self.max = 0


        strFile = os.path.join(os.path.expanduser('~'), self._config_file)
        if os.path.exists(strFile):
            cfgParser = ConfigParser.ConfigParser()
            cfgFile = open(strFile)
            cfgParser.readfp(cfgFile)
            self.apiKey = cfgParser.get('general', 'apiKey')
            self.appId = cfgParser.get('general', 'appId')
            self.timerCount = int(cfgParser.get('general', 'timerCount'))
            self.period = int(cfgParser.get('general', 'period'))
            cfgFile.close()
        else:
            self.apiKey = ""
            self.appId = ""
            self.timerCount = 10
            self.period = 7


        today = datetime.date.today() 
        self.date2=today.strftime('%Y%m%d')
        self.date1=(today + datetime.timedelta(-self.period)).strftime('%Y%m%d')

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

        if self.apiKey and self.appId:
            self.getAccessToken()
        else:
            self.showConfigurationInterface()


        self.resize(400,400)
        self.http=QHttp(self)

        self.connect(self.http,SIGNAL("done(bool)"),self.doneHttp)

    def createConfigurationInterface(self,parent):
        defaultConfig = {"apiKey":self.apiKey,"appId":self.appId,"timerCount":self.timerCount,"period":self.period}
        self.metrikaConfig = MetrikaConfig(self,defaultConfig)
        self.configPage = parent.addPage(self.metrikaConfig,"")
        self.connect(parent, SIGNAL("okClicked()"), self.configAccepted)
        self.connect(parent, SIGNAL("cancelClicked()"), self.configDenied)

    def showConfigurationInterface(self):
        dialog = KPageDialog()
        dialog.setFaceType(KPageDialog.Plain)
        dialog.setButtons(KDialog.ButtonCode(KDialog.Ok | KDialog.Cancel))
        self.createConfigurationInterface(dialog)
        dialog.resize(400,400)
        dialog.exec_()

    def configDenied(self):
        pass

    def configAccepted(self):
        self.apiKey = self.metrikaConfig.getApiKey()
        self.appId = self.metrikaConfig.getAppId()
        self.timerCount = self.metrikaConfig.getTimer()
        self.period = self.metrikaConfig.getPeriod()

        cfgParser = ConfigParser.ConfigParser()
        cfgParser.read(self._config_file)
        if not cfgParser.has_section('general'):
            cfgParser.add_section('general')

        cfgParser.set('general', 'apiKey',self.apiKey)
        cfgParser.set('general', 'appId',self.appId)
        cfgParser.set('general', 'timerCount',self.timerCount)
        cfgParser.set('general', 'period',self.period)

        strFile = os.path.join(os.path.expanduser('~'),self._config_file)
        cfgFile = open(strFile,"w")
        cfgParser.write(cfgFile)
        cfgFile.close()

        if (self.apiKey and self.appId):
            self.getAccessToken()
        else:
            self.showConfigurationInterface()


    def getAccessToken(self):
        self.webView = Plasma.WebView(self.applet)
        self.webView.setUrl(KUrl(self.OAUTHURL))
        self.webView.urlChanged.connect(self.onChangeUrl)
        self.layout.addItem(self.webView)

    def onChangeUrl(self, url):
        hashCode=url.fragment()
        reAccessToken = re.compile('(?<=access_token=).*?(&)')
        sAccessToken = reAccessToken.search(hashCode)
        self.access_token = sAccessToken.group(0).replace('&', '')
        if self.access_token:
            self.webView.deleteLater()
            self.lookUp()


    def lookUp(self):
        self.http.setHost("api-metrika.yandex.ru")

        today = datetime.date.today()
        self.date2=today.strftime('%Y%m%d')
        self.date1=(today + datetime.timedelta(-self.period)).strftime('%Y%m%d')

        self.http.get("/stat/traffic/summary?id="+self.appId+"&date1="+str(self.date1)+"&date2="+str(self.date2)+"&access_token="+self.access_token)

    def doneHttp(self,error):

        self.timer = QTimer()
        self.connect(self.timer,SIGNAL("timeout()"),self.lookUp)
        self.timer.start(1000*60*int(self.timerCount))

        if error:       
            self.browserResult.setText(self.http.errorString())
        else:        
            result=self.http.readAll().data()
            if result:
                xmlString = xml.dom.minidom.parseString(result)
                rowData = xmlString.getElementsByTagName('row')

                self.rowsData = {}
                self.rowsDate = []
                self.max = 0

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
    return PyMetrix(parent)

