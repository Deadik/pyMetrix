from PyQt4.QtGui import QWidget
from configForm_ui import Ui_Dialog

class MetrikaConfig(QWidget,Ui_Dialog):
    '''
    classdocs
    '''


    def __init__(self,parent,defaultConfig = None):
        '''
        Constructor
        '''
        QWidget.__init__(self)
        self.parent = parent
        self.setupUi(self)
        if defaultConfig:
            self.apiKey.setText(defaultConfig['apiKey'])
            self.appId.setText(defaultConfig['appId'])
            self.timerCount.setValue(defaultConfig['timerCount'])
            self.period.setValue(defaultConfig['period'])

    def getApiKey(self):
        strApiKey = str.strip(str(self.apiKey.text()))
        return strApiKey

    def getAppId(self):
        strAppId = str.strip(str(self.appId.text()))
        return strAppId

    def getTimer(self):
        intTimer = int(self.timerCount.value())
        return intTimer

    def getPeriod(self):
        intPeriod = int(self.period.value())
        return intPeriod
