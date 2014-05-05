#!/usr/bin/env python
__author__ = '@mattanimation'
"""
This module will hold the classes for the node
"""

import math, os
import utils
import customWidgets
from PyQt4 import QtCore, QtGui


class Edge(QtGui.QGraphicsItem):
    """
    The line that connects any 2 nodes
    """
    Pi = math.pi
    TwoPi = 2.0 * Pi

    Type = QtGui.QGraphicsItem.UserType + 2

    def __init__(self, sourceNode, destNode):
        super(Edge, self).__init__()

        self.arrowSize = 10.0
        self.sourcePoint = QtCore.QPointF()
        self.destPoint = QtCore.QPointF()

        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        self.source = sourceNode
        self.dest = destNode
        self.source.addEdge(self)
        self.dest.addEdge(self)
        self.adjust()

    def type(self):
        return Edge.Type

    def sourceNode(self):
        return self.source

    def setSourceNode(self, node):
        self.source = node
        self.adjust()

    def destNode(self):
        return self.dest

    def setDestNode(self, node):
        self.dest = node
        self.adjust()

    def adjust(self):
        if not self.source or not self.dest:
            return

        line = QtCore.QLineF(self.mapFromItem(self.source, 0, 0),
                self.mapFromItem(self.dest, 0, 0))
        length = line.length()

        self.prepareGeometryChange()

        if length > 20.0:
            edgeOffset = QtCore.QPointF((line.dx() * 10) / length,
                    (line.dy() * 10) / length)

            self.sourcePoint = line.p1() + edgeOffset
            self.destPoint = line.p2() - edgeOffset
        else:
            self.sourcePoint = line.p1()
            self.destPoint = line.p1()

    def boundingRect(self):
        if not self.source or not self.dest:
            return QtCore.QRectF()

        penWidth = 1.0
        extra = (penWidth + self.arrowSize) / 2.0

        return QtCore.QRectF(self.sourcePoint,
                QtCore.QSizeF(self.destPoint.x() - self.sourcePoint.x(),
                        self.destPoint.y() - self.sourcePoint.y())).normalized().adjusted(-extra, -extra, extra, extra)

    def paint(self, painter, option, widget):
        if not self.source or not self.dest:
            return

        # Draw the line itself.
        line = QtCore.QLineF(self.sourcePoint, self.destPoint)

        if line.length() == 0.0:
            return

        painter.setPen(QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine,
                QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawLine(line)

        # Draw the arrows if there's enough room.
        """
        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = Edge.TwoPi - angle

        sourceArrowP1 = self.sourcePoint + QtCore.QPointF(math.sin(angle + Edge.Pi / 3) * self.arrowSize,
                                                          math.cos(angle + Edge.Pi / 3) * self.arrowSize)
        sourceArrowP2 = self.sourcePoint + QtCore.QPointF(math.sin(angle + Edge.Pi - Edge.Pi / 3) * self.arrowSize,
                                                          math.cos(angle + Edge.Pi - Edge.Pi / 3) * self.arrowSize);
        destArrowP1 = self.destPoint + QtCore.QPointF(math.sin(angle - Edge.Pi / 3) * self.arrowSize,
                                                      math.cos(angle - Edge.Pi / 3) * self.arrowSize)
        destArrowP2 = self.destPoint + QtCore.QPointF(math.sin(angle - Edge.Pi + Edge.Pi / 3) * self.arrowSize,
                                                      math.cos(angle - Edge.Pi + Edge.Pi / 3) * self.arrowSize)

        painter.setBrush(QtCore.Qt.black)
        painter.drawPolygon(QtGui.QPolygonF([line.p1(), sourceArrowP1, sourceArrowP2]))
        painter.drawPolygon(QtGui.QPolygonF([line.p2(), destArrowP1, destArrowP2]))
        """


class Node(QtGui.QGraphicsItem):
    """
    The basic node class
    """
    Type = QtGui.QGraphicsItem.UserType + 1

    def __init__(self, graphWidget):
        super(Node, self).__init__()

        self.graph = graphWidget
        self.edgeList = []
        self.newPos = QtCore.QPointF()

        self.address = ""
        self.showAddress = False

        self.setAcceptsHoverEvents(True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QtGui.QGraphicsItem.DeviceCoordinateCache)
        self.setZValue(1)

    def type(self):
        return Node.Type

    def addEdge(self, edge):
        self.edgeList.append(edge)
        edge.adjust()

    def edges(self):
        return self.edgeList

    def calculateForces(self):
        if not self.scene() or self.scene().mouseGrabberItem() is self:
            self.newPos = self.pos()
            return

        # Sum up all forces pushing this item away.
        xvel = 0.0
        yvel = 0.0
        for item in self.scene().items():
            if not isinstance(item, Node):
                continue

            line = QtCore.QLineF(self.mapFromItem(item, 0, 0),
                    QtCore.QPointF(0, 0))
            dx = line.dx()
            dy = line.dy()
            l = 2.0 * (dx * dx + dy * dy)
            if l > 0:
                xvel += (dx * 150.0) / l
                yvel += (dy * 150.0) / l

        # Now subtract all forces pulling items together.
        weight = (len(self.edgeList) + 1) * 10.0
        for edge in self.edgeList:
            if edge.sourceNode() is self:
                pos = self.mapFromItem(edge.destNode(), 0, 0)
            else:
                pos = self.mapFromItem(edge.sourceNode(), 0, 0)
            xvel += pos.x() / weight
            yvel += pos.y() / weight

        if QtCore.qAbs(xvel) < 0.1 and QtCore.qAbs(yvel) < 0.1:
            xvel = yvel = 0.0

        sceneRect = self.scene().sceneRect()
        self.newPos = self.pos() + QtCore.QPointF(xvel, yvel)
        self.newPos.setX(min(max(self.newPos.x(), sceneRect.left() + 10), sceneRect.right() - 10))
        self.newPos.setY(min(max(self.newPos.y(), sceneRect.top() + 10), sceneRect.bottom() - 10))

    def advance(self):
        if self.newPos == self.pos():
            return False

        self.setPos(self.newPos)
        return True

    def boundingRect(self):
        adjust = 2.0
        return QtCore.QRectF(-10 - adjust, -10 - adjust, 300 + adjust,
                23 + adjust)
    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(-10, -10, 20, 20)
        return path

    def paint(self, painter, option, widget):
        painter.setPen(QtCore.Qt.NoPen)
        #draw shadow
        #painter.setBrush(QtCore.Qt.darkGray)
        #painter.drawEllipse(-7, -7, 20, 20)

        #draw circle color
        #gradient = QtGui.QRadialGradient(-3, -3, 10)
        #if option.state & QtGui.QStyle.State_Sunken:
        #    gradient.setCenter(3, 3)
        #    gradient.setFocalPoint(3, 3)
        #    gradient.setColorAt(1, QtGui.QColor(QtCore.Qt.yellow).light(120))
        #    gradient.setColorAt(0, QtGui.QColor(QtCore.Qt.darkYellow).light(120))
        #else:
        #    gradient.setColorAt(0, QtCore.Qt.yellow)
        #    gradient.setColorAt(1, QtCore.Qt.darkYellow)

        #draw outline
        #painter.setBrush(QtGui.QBrush(gradient))
        fillCol = QtGui.QColor()
        fillCol.setRgb(34, 35, 38, alpha=125)
        painter.setBrush(fillCol)
        painter.setPen(QtGui.QPen(QtCore.Qt.white, 1))
        painter.drawEllipse(-10, -10, 20, 20)
        
        #draw address
        if self.showAddress:
            painter.setPen(QtGui.QColor(225,225,225, alpha=255))
            painter.setFont(QtGui.QFont('Roboto', 12))
            painter.drawText(QtCore.QRect(30,-12, 250,24),
                             QtCore.Qt.AlignLeft,
                             self.address )
        

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionHasChanged:
            for edge in self.edgeList:
                edge.adjust()
            self.graph.itemMoved()

        return super(Node, self).itemChange(change, value)

    def mousePressEvent(self, event):
        self.update()
        
        super(Node, self).mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.update()

        """
        print self.address
        nw = QtGui.QWidget()
        nwl = QtGui.QHBoxLayout()
        nw.setLayout(nwl)
        nwlbl = QtGui.QLabel(self.address)
        nwl.addWidget(nwlbl)
        print self.graph.parent()
        self.graph.parent().layout().addWidget(nw)"""
        customWidgets.MailWidget.NewMessage(self.graph.parent(), self.address)
        
        super(Node, self).mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self, event):
        self.update()
        super(Node, self).mouseReleaseEvent(event)

    def hoverEnterEvent(self, event):
        self.update()
        self.showAddress = True
        print "hovered over {0}".format(self.address)
        super(Node, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.update()
        self.showAddress = False
        print "hovered Out {0}".format(self.address)
        super(Node, self).hoverLeaveEvent(event)


"""
add more abstraction to let the user pick color for new contact node
"""

class UserNode(Node):
    """
    create the main user node
    """
    def __init__(self, parent):
        super(UserNode, self).__init__(parent)

    def boundingRect(self):
        adjust = 2.0
        return QtCore.QRectF(-100-adjust,-150 -adjust, 200 + adjust, 300 + adjust)
        #return QtCore.QRectF(-20 - adjust, -20 - adjust, 43 + adjust,
        #        43 + adjust)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(-20, -20, 40, 40)
        return path

    def paint(self, painter, option, widget):
        painter.setPen(QtCore.Qt.NoPen)
        """
        painter.setBrush(QtCore.Qt.darkGray)
        painter.drawEllipse(-20, -20, 40, 40)

        gradient = QtGui.QRadialGradient(-3, -3, 40)
        if option.state & QtGui.QStyle.State_Sunken:
            gradient.setCenter(3, 3)
            gradient.setFocalPoint(3, 3)
            gradient.setColorAt(1, QtGui.QColor(QtCore.Qt.red).light(120))
            gradient.setColorAt(0, QtGui.QColor(QtCore.Qt.darkRed).light(120))
        else:
            gradient.setColorAt(0, QtCore.Qt.red)
            gradient.setColorAt(1, QtCore.Qt.darkRed)

        painter.setBrush(QtGui.QBrush(gradient))"""
        
        fillCol = QtGui.QColor()
        fillCol.setRgb(100,100,100, alpha=255)
        painter.setBrush(fillCol)
        painter.setPen(QtGui.QPen(QtCore.Qt.white, 3))
        painter.drawEllipse(-20, -20, 40, 40)
        
        usrImage = QtGui.QImage(utils.get_user_image_path())
        mskImage = QtGui.QImage(os.path.join(utils.get_resources_path(),
                                             'nodemask.png'))
        msk = QtGui.QPixmap.fromImage(mskImage.createAlphaMask()) #(os.path.join(utils.get_root_url(),'nodemask.png'))
        
        painter.drawImage(0,0, usrImage)
        painter.setClipRegion(QtGui.QRegion(msk))
        
        