from pyqtgraph.Qt import QtCore, QtGui

from DockDrop import *
from pyqtgraph.widgets.VerticalLabel import VerticalLabel

class Dock(QtGui.QWidget, DockDrop):
    
    sigStretchChanged = QtCore.Signal()
    
    def __init__(self, name, area=None, size=(10, 10)):
        QtGui.QWidget.__init__(self)
        DockDrop.__init__(self)
        self.area = area
        self.label = DockLabel(name, self)
        self.labelHidden = False
        self.moveLabel = True  ## If false, the dock is no longer allowed to move the label.
        self.autoOrient = True
        self.orientation = 'horizontal'
        #self.label.setAlignment(QtCore.Qt.AlignHCenter)
        self.topLayout = QtGui.QGridLayout()
        self.topLayout.setContentsMargins(0, 0, 0, 0)
        self.topLayout.setSpacing(0)
        self.setLayout(self.topLayout)
        self.topLayout.addWidget(self.label, 0, 1)
        self.widgetArea = QtGui.QWidget()
        self.topLayout.addWidget(self.widgetArea, 1, 1)
        self.layout = QtGui.QGridLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.widgetArea.setLayout(self.layout)
        self.widgetArea.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.widgets = []
        self.currentRow = 0
        #self.titlePos = 'top'
        self.raiseOverlay()
        self.hStyle = """
        Dock > QWidget { 
            border: 1px solid #000; 
            border-radius: 5px; 
            border-top-left-radius: 0px; 
            border-top-right-radius: 0px; 
            border-top-width: 0px;
        }"""
        self.vStyle = """
        Dock > QWidget { 
            border: 1px solid #000; 
            border-radius: 5px; 
            border-top-left-radius: 0px; 
            border-bottom-left-radius: 0px; 
            border-left-width: 0px;
        }"""
        self.nStyle = """
        Dock > QWidget { 
            border: 1px solid #000; 
            border-radius: 5px; 
        }"""
        self.dragStyle = """
        Dock > QWidget { 
            border: 4px solid #00F; 
            border-radius: 5px; 
        }"""
        self.setAutoFillBackground(False)
        self.widgetArea.setStyleSheet(self.hStyle)
        
        self.setStretch(*size)

    def setStretch(self, x=None, y=None):
        #print "setStretch", self, x, y
        #self._stretch = (x, y)
        if x is None:
            x = 0
        if y is None:
            y = 0
        #policy = self.sizePolicy()
        #policy.setHorizontalStretch(x)
        #policy.setVerticalStretch(y)
        #self.setSizePolicy(policy)
        self._stretch = (x, y)
        self.sigStretchChanged.emit()
        #print "setStretch", self, x, y, self.stretch()
        
    def stretch(self):
        #policy = self.sizePolicy()
        #return policy.horizontalStretch(), policy.verticalStretch()
        return self._stretch
        
    #def stretch(self):
        #return self._stretch

    def hideTitleBar(self):
        self.label.hide()
        self.labelHidden = True
        if 'center' in self.allowedAreas:
            self.allowedAreas.remove('center')
        self.updateStyle()
        
    def showTitleBar(self):
        self.label.show()
        self.labelHidden = False
        self.allowedAreas.add('center')
        self.updateStyle()
        
    def setOrientation(self, o='auto', force=False):
        #print self.name(), "setOrientation", o, force
        if o == 'auto':
            if self.container().type() == 'tab':
                o = 'horizontal'
            elif self.width() > self.height()*1.5:
                o = 'vertical'
            else:
                o = 'horizontal'
        if force or self.orientation != o:
            self.orientation = o
            self.label.setOrientation(o)
            self.updateStyle()
        
    def updateStyle(self):
        #print self.name(), "update style:", self.orientation, self.moveLabel, self.label.isVisible()
        if self.labelHidden:
            self.widgetArea.setStyleSheet(self.nStyle)
        elif self.orientation == 'vertical':
            self.label.setOrientation('vertical')
            if self.moveLabel:
                #print self.name(), "reclaim label"
                self.topLayout.addWidget(self.label, 1, 0)
            self.widgetArea.setStyleSheet(self.vStyle)
        else:
            self.label.setOrientation('horizontal')
            if self.moveLabel:
                #print self.name(), "reclaim label"
                self.topLayout.addWidget(self.label, 0, 1)
            self.widgetArea.setStyleSheet(self.hStyle)

    def resizeEvent(self, ev):
        self.setOrientation()
        self.resizeOverlay(self.size())

    def name(self):
        return str(self.label.text())

    def container(self):
        return self._container

    def addWidget(self, widget, row=None, col=0, rowspan=1, colspan=1):
        if row is None:
            row = self.currentRow
        self.currentRow = max(row+1, self.currentRow)
        self.widgets.append(widget)
        self.layout.addWidget(widget, row, col, rowspan, colspan)
        self.raiseOverlay()
        
        
    def startDrag(self):
        self.drag = QtGui.QDrag(self)
        mime = QtCore.QMimeData()
        #mime.setPlainText("asd")
        self.drag.setMimeData(mime)
        self.widgetArea.setStyleSheet(self.dragStyle)
        self.update()
        action = self.drag.exec_()
        self.updateStyle()
        
    def float(self):
        self.area.floatDock(self)
            
    def containerChanged(self, c):
        #print self.name(), "container changed"
        self._container = c
        if c.type() != 'tab':
            self.moveLabel = True
            self.label.setDim(False)
        else:
            self.moveLabel = False
            
        self.setOrientation(force=True)

    def __repr__(self):
        return "<Dock %s %s>" % (self.name(), self.stretch())
            
class DockLabel(VerticalLabel):
    
    sigClicked = QtCore.Signal(object, object)
    
    def __init__(self, text, dock):
        self.dim = False
        self.fixedWidth = False
        VerticalLabel.__init__(self, text, orientation='horizontal', forceWidth=False)
        self.setAlignment(QtCore.Qt.AlignTop|QtCore.Qt.AlignHCenter)
        self.dock = dock
        self.updateStyle()
        self.setAutoFillBackground(False)

    #def minimumSizeHint(self):
        ##sh = QtGui.QWidget.minimumSizeHint(self)
        #return QtCore.QSize(20, 20)

    def updateStyle(self):
        r = '3px'
        if self.dim:
            fg = '#aaa'
            bg = '#44a'
            border = '#339'
        else:
            fg = '#fff'
            bg = '#66c'
            border = '#55B'
        
        if self.orientation == 'vertical':
            self.vStyle = """DockLabel { 
                background-color : %s; 
                color : %s; 
                border-top-right-radius: 0px; 
                border-top-left-radius: %s; 
                border-bottom-right-radius: 0px; 
                border-bottom-left-radius: %s; 
                border-width: 0px; 
                border-right: 2px solid %s;
                padding-top: 3px;
                padding-bottom: 3px;
            }""" % (bg, fg, r, r, border)
            self.setStyleSheet(self.vStyle)
        else:
            self.hStyle = """DockLabel { 
                background-color : %s; 
                color : %s; 
                border-top-right-radius: %s; 
                border-top-left-radius: %s; 
                border-bottom-right-radius: 0px; 
                border-bottom-left-radius: 0px; 
                border-width: 0px; 
                border-bottom: 2px solid %s;
                padding-left: 3px;
                padding-right: 3px;
            }""" % (bg, fg, r, r, border)
            self.setStyleSheet(self.hStyle)

    def setDim(self, d):
        if self.dim != d:
            self.dim = d
            self.updateStyle()
    
    def setOrientation(self, o):
        VerticalLabel.setOrientation(self, o)
        self.updateStyle()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.pressPos = ev.pos()
            self.startedDrag = False
            ev.accept()
        
    def mouseMoveEvent(self, ev):
        if not self.startedDrag and (ev.pos() - self.pressPos).manhattanLength() > QtGui.QApplication.startDragDistance():
            self.dock.startDrag()
        ev.accept()
        #print ev.pos()
            
    def mouseReleaseEvent(self, ev):
        if not self.startedDrag:
            #self.emit(QtCore.SIGNAL('clicked'), self, ev)
            self.sigClicked.emit(self, ev)
        ev.accept()
        
    def mouseDoubleClickEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.dock.float()
            
    #def paintEvent(self, ev):
        #p = QtGui.QPainter(self)
        ##p.setBrush(QtGui.QBrush(QtGui.QColor(100, 100, 200)))
        #p.setPen(QtGui.QPen(QtGui.QColor(50, 50, 100)))
        #p.drawRect(self.rect().adjusted(0, 0, -1, -1))
        
        #VerticalLabel.paintEvent(self, ev)
            
            
            
#class DockLabel(QtGui.QWidget):
    #def __init__(self, text, dock):
        #QtGui.QWidget.__init__(self)
        #self._text = text
        #self.dock = dock
        #self.orientation = None
        #self.setOrientation('horizontal')
        
    #def text(self):
        #return self._text
        
    #def mousePressEvent(self, ev):
        #if ev.button() == QtCore.Qt.LeftButton:
            #self.pressPos = ev.pos()
            #self.startedDrag = False
            #ev.accept()
        
    #def mouseMoveEvent(self, ev):
        #if not self.startedDrag and (ev.pos() - self.pressPos).manhattanLength() > QtGui.QApplication.startDragDistance():
            #self.dock.startDrag()
        #ev.accept()
        ##print ev.pos()
            
    #def mouseReleaseEvent(self, ev):
        #ev.accept()
        
    #def mouseDoubleClickEvent(self, ev):
        #if ev.button() == QtCore.Qt.LeftButton:
            #self.dock.float()
            
    #def setOrientation(self, o):
        #if self.orientation == o:
            #return
        #self.orientation = o
        #self.update()
        #self.updateGeometry()
        
    #def paintEvent(self, ev):
        #p = QtGui.QPainter(self)
        #p.setBrush(QtGui.QBrush(QtGui.QColor(100, 100, 200)))
        #p.setPen(QtGui.QPen(QtGui.QColor(50, 50, 100)))
        #p.drawRect(self.rect().adjusted(0, 0, -1, -1))
        
        #p.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255)))
        
        #if self.orientation == 'vertical':
            #p.rotate(-90)
            #rgn = QtCore.QRect(-self.height(), 0, self.height(), self.width())
        #else:
            #rgn = self.rect()
        #align  = QtCore.Qt.AlignTop|QtCore.Qt.AlignHCenter
            
        #self.hint = p.drawText(rgn, align, self.text())
        #p.end()
        
        #if self.orientation == 'vertical':
            #self.setMaximumWidth(self.hint.height())
            #self.setMaximumHeight(16777215)
        #else:
            #self.setMaximumHeight(self.hint.height())
            #self.setMaximumWidth(16777215)

    #def sizeHint(self):
        #if self.orientation == 'vertical':
            #if hasattr(self, 'hint'):
                #return QtCore.QSize(self.hint.height(), self.hint.width())
            #else:
                #return QtCore.QSize(19, 50)
        #else:
            #if hasattr(self, 'hint'):
                #return QtCore.QSize(self.hint.width(), self.hint.height())
            #else:
                #return QtCore.QSize(50, 19)
