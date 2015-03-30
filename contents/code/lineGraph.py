# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyKDE4.plasma import Plasma
from PyKDE4.kdecore import KUrl
from PyKDE4 import plasmascript
import math

class LineGraph(QGraphicsWidget) :
	def __init__(self, parent) :
		QGraphicsWidget.__init__(self, parent)
		layout = QGraphicsLinearLayout(Qt.Vertical)
		self.setLayout(layout)
		self.setMinimumSize(200, 120)
		self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

		self.plot = LineGraphPlot(self)
		layout.addItem(self.plot)

		legendLayout = QGraphicsLinearLayout(Qt.Horizontal)
		legendLayout.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
		legendLayout.setSpacing(15)
		layout.addItem(legendLayout)
		layout.setAlignment(legendLayout, Qt.AlignHCenter)

		self.metrixLineGraphLegend = LineGraphLegend(self, "metrix",Qt.black)
		legendLayout.addItem(self.metrixLineGraphLegend)


	def setDownloads(self, downloads) :
		self.plot.setDownloads(downloads)
	  
	  
	def setVisitors(self, visitors) :
		self.plot.setVisitors(visitors)

	def addRowsDate(self,rowsDate):
		self.plot.rowsDate = rowsDate
		self.plot.calculateRange()
		self.plot.update()

	def addRowsData(self,rowsData):
		self.plot.rowsData = rowsData
		self.plot.calculateRange()
		self.plot.update()

	def setMax(self,maxValue):
		self.plot.max = maxValue


class LineGraphPlot(QGraphicsWidget) :
	def __init__(self, parent) :
	  QGraphicsWidget.__init__(self, parent)
	  self.downloads = list()
	  self.visitors = list()
	  self.max = 1
	  self.downloadAreas = list()
	  self.visitorAreas = list()
	  self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
	  self.setAcceptHoverEvents(True)
	  
	  
	def setDownloads(self, downloads) :
	  self.downloads = downloads
	  self.calculateRange()
	  self.update()
	  
	  
	def setVisitors(self, visitors) :
	  self.visitors = visitors
	  self.calculateRange()
	  self.update()
	
	def addRowsDate(self,rowsDate):
		self.rowsDate = rowsDate
		self.calculateRange()
		self.update()
	  
	def calculateRange(self) :
	  self.max = 1
	  for sample in self.downloads :
	     if sample[1] > self.max : self.max = sample[1]
	  for sample in self.visitors :
	     if sample[1] > self.max : self.max = sample[1]
	  exp = len(str(self.max)) - 2
	  if exp < 0 : exp = 0
	  self.max = int(math.ceil(float(self.max) / 4 / 10 ** exp) * 4 * 10 ** exp)
	  
	  
	def paint(self, painter, option, widget) :
		painter.save()
		painter.setPen(Plasma.Theme.defaultTheme().color(Plasma.Theme.TextColor))
		painter.setFont(Plasma.Theme.defaultTheme().font(Plasma.Theme.SmallestFont))
		painter.setRenderHint(QPainter.Antialiasing)

		if(hasattr(self, 'rowsDate')):

			maxLabelWidth = painter.fontMetrics().width(str(self.max))
			yOffset = float(painter.fontMetrics().ascent() + painter.fontMetrics().leading() - 1) / 2 # -1 for baseline
			graphHeight = self.size().height() - yOffset - 2
			yStep = graphHeight / 4

			painter.drawLine(maxLabelWidth + 4, 0, maxLabelWidth + 4, self.size().height() - 2)
			painter.drawLine(maxLabelWidth + 2, self.size().height() - 2, self.size().width(), self.size().height() - 2)

			for i in range(0, 4) :
				label = str(self.max / 4 * (4 - i))
				labelWidth = painter.fontMetrics().width(label)
				painter.drawText(QPointF(maxLabelWidth - labelWidth, yOffset * 2 + yStep * i), label)
				painter.drawLine( QPointF(maxLabelWidth + 2, yOffset + yStep * i), \
				               QPointF(maxLabelWidth + 4, yOffset + yStep * i) )
				painter.setOpacity(0.5)
				painter.drawLine( QPointF(maxLabelWidth + 4, yOffset + yStep * i), \
				               QPointF(self.size().width(), yOffset + yStep * i) )
				painter.setOpacity(1.0)
			 
			xStep = (self.size().width() - maxLabelWidth - 4) / (len(self.rowsDate) - 1)
			for i in range(0, len(self.rowsDate)) :
				painter.drawLine( QPointF(maxLabelWidth + 4 + xStep * i, self.size().height() - 2), QPointF(maxLabelWidth + 4 + xStep * i, self.size().height()) )

			i=0
			line = QPolygonF()
			#print self.rowsDate
		
			for date in self.rowsDate:
				yPos = yOffset + graphHeight - graphHeight / self.max * self.rowsData[date]['visitors']
				point = QPointF(maxLabelWidth + 4 + xStep * i, yPos)
				line.append(point)
				painter.drawEllipse(point, 2, 2)
				i=i+1

			painter.drawPolyline(line)

		painter.restore()
	  

	def drawGraph(self, painter, color, graphHeight, yOffset, maxLabelWidth, xStep, data, areas) :
	  line = QPolygonF()
	  for i in range(0, len(data)) :
	     yPos = yOffset + graphHeight - graphHeight / self.max * data[i][1]
	     line.append(QPointF(maxLabelWidth + 4 + xStep * i, yPos))
	     areas.append(QRectF(maxLabelWidth + 4 + xStep * i - 3, yPos - 3, 6, 6))
	  
	  pen = QPen(color)
	  pen.setWidth(2.5)
	  painter.setPen(pen)
	  painter.setBrush(QBrush(color))
	  
	  
	  painter.drawPolyline(line)
	  
	  pen.setWidth(1.0)
	  painter.setPen(pen)
	  for point in line :
	     painter.drawEllipse(point, 2, 2)
	  
	  
	def hoverMoveEvent(self, event) :
	  hide = True
	  for i in range(0, len(self.downloadAreas)) :
	     if self.downloadAreas[i].contains(event.lastPos()) :
	        text = "date: " + self.downloads[i][0] + "\n" + "downloads: " + str(self.downloads[i][1])
	        QToolTip.showText(event.lastScreenPos(), text)
	        hide = False
	  for i in range(0, len(self.visitorAreas)) :
	     if self.visitorAreas[i].contains(event.lastPos()) :
	        text = "date: " + self.visitors[i][0] + "\n" + "visitors: " + str(self.visitors[i][1])
	        QToolTip.showText(event.lastScreenPos(), text)
	        hide = False
	  if hide : 
	     QToolTip.hideText()
      
      
class LineGraphLegend(QGraphicsWidget) :
	def __init__(self, parent, text, color) :
	  QGraphicsWidget.__init__(self, parent)
	  self.color = color
	  self.text = text


	def sizeHint(self, which, constraint) :
	  metrics = Plasma.Theme.defaultTheme().fontMetrics()
	  return QSizeF(metrics.width(self.text) + 20, metrics.height())
	  
	  
	def setColor(self, color) :
	  self.color = color
	  self.update()


	def paint(self, painter, option, widget) :
	  painter.save()
	  
	  pen = QPen(self.color)
	  pen.setWidth(2.5)
	  painter.setPen(pen)
	  painter.setRenderHint(QPainter.Antialiasing)
	  painter.setFont(Plasma.Theme.defaultTheme().font(Plasma.Theme.DefaultFont))
	  
	  metrics = painter.fontMetrics()
	  y = metrics.ascent() - metrics.xHeight() / 2
	  painter.drawLine(0, y, 15, y)
	  
	  painter.setPen(Plasma.Theme.defaultTheme().color(Plasma.Theme.TextColor))
	  painter.drawText(20, metrics.ascent() + 1, self.text)
	  
	  painter.restore() 
