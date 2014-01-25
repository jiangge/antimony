import math

from PySide import QtCore, QtGui

import colors
import base

class ScaleControl(base.NodeControl3D):

    @classmethod
    def new(cls, canvas, x, y, z, scale):
        """ Constructs a new scale modifier at the given point.
            position and scale should be given in units.
        """
        s = Scale(get_name('s'), x, y, z, 1, 1, 1)
        return cls(canvas, s)

    def __init__(self, canvas, target):
        """ Construct a circle control widget.
        """
        super(ScaleControl, self).__init__(canvas, target)

        self.scale_x = base.DragManager(self, self.drag_x)
        self.scale_y = base.DragManager(self, self.drag_y)
        self.scale_z = base.DragManager(self, self.drag_z)

        self.draw_scale = 25

        self.sync()
        self.make_masks()

        self.editor_datums = ['name','input','x','y','z','sx','sy','sz','shape']

        self.show()
        self.raise_()

    def drag_x(self, v, p):
        if not self.node._sx.simple():  return
        self.node._sx.set_expr(str(float(self.node._sx.get_expr()) +
                                         v.x()/self.draw_scale))

    def drag_y(self, v, p):
        if not self.node._sy.simple():  return
        self.node._sy.set_expr(str(float(self.node._sy.get_expr()) +
                                         v.y()/self.draw_scale))

    def drag_z(self, v, p):
        if not self.node._sz.simple():  return
        self.node._sz.set_expr(str(float(self.node._sz.get_expr()) +
                                         v.z()/self.draw_scale))


    def make_masks(self):

        self.scale_x.mask = self.paint_mask(self.draw_x_handle)
        self.scale_y.mask = self.paint_mask(self.draw_y_handle)
        self.scale_z.mask = self.paint_mask(self.draw_z_handle)
        self.drag_control.mask = self.paint_mask(self.draw_center)

        self.setMask(self.scale_x.mask |
                     self.scale_y.mask |
                     self.scale_z.mask |
                     self.drag_control.mask |
                     self.paint_mask(self.draw_axes))


    @property
    def scale(self):
        return QtGui.QVector3D(self._cache['sx'],
                               self._cache['sy'],
                               self._cache['sz'])

    def combined_path(self):
        p = self.axes_path()
        p.connectPath(self.x_handle_path())
        p.connectPath(self.y_handle_path())
        p.connectPath(self.z_handle_path())
        return p

    def reposition(self):
        """ Repositions this widget and calls self.update
        """
        self.setGeometry(self.get_rect(self.combined_path, offset=15))

        self.make_masks()
        self.update()

    def x_handle_path(self, offset=QtCore.QPoint()):
        """ Returns a painter path that draws the x arrow.
        """
        s = self.scale.x() * self.draw_scale
        center = self.position + QtGui.QVector3D(s, 0, 0)
        points = [
            center + 0.1*QtGui.QVector3D(-s, s, 0),
            center,
            center + 0.1*QtGui.QVector3D(-s, -s, 0)]
        return self.draw_lines([points], offset)

    def y_handle_path(self, offset=QtCore.QPoint()):
        """ Returns a painter path that draws the x arrow.
        """
        s = self.scale.y() * self.draw_scale
        center = self.position + QtGui.QVector3D(0, s, 0)
        points = [
            center + 0.1*QtGui.QVector3D(-s, -s, 0),
            center,
            center + 0.1*QtGui.QVector3D(s, -s, 0)]
        return self.draw_lines([points], offset)


    def z_handle_path(self, offset=QtCore.QPoint()):
        """ Returns a painter path that draws the x arrow.
        """
        s = self.scale.z() * self.draw_scale
        center = self.position + QtGui.QVector3D(0, 0, s)
        points = [
            center + 0.1*QtGui.QVector3D(-s, 0, -s),
            center,
            center + 0.1*QtGui.QVector3D(s, 0, -s)]
        return self.draw_lines([points], offset)

    def axes_path(self, offset=QtCore.QPoint()):
        lines = [
                [self.position, self.position +
                        self.draw_scale*QtGui.QVector3D(0, 0, self.scale.z())],
                [self.position, self.position +
                        self.draw_scale*QtGui.QVector3D(self.scale.x(), 0, 0)],
                [self.position, self.position +
                        self.draw_scale*QtGui.QVector3D(0, self.scale.y(), 0)]]
        return self.draw_lines(lines, offset)

    def draw_x_handle(self, painter, mask=False):
        self.set_pen(painter, mask, self.scale_x, colors.orange)
        painter.drawPath(self.x_handle_path(self.pos()))

    def draw_y_handle(self, painter, mask=False):
        self.set_pen(painter, mask, self.scale_y, colors.orange)
        painter.drawPath(self.y_handle_path(self.pos()))

    def draw_z_handle(self, painter, mask=False):
        self.set_pen(painter, mask, self.scale_z, colors.orange)
        painter.drawPath(self.z_handle_path(self.pos()))

    def draw_axes(self, painter, mask=False):
        self.set_pen(painter, mask, None, colors.orange)
        painter.drawPath(self.axes_path(self.pos()))


    def draw_center(self, painter, mask=False):
        """ Draws a dot at the center of this scale object.
        """
        pos = self.canvas.unit_to_pixel(self.position) - self.pos()
        x, y = pos.x(), pos.y()

        self.set_brush(painter, mask, colors.orange)

        if mask:                                                    d = 22
        elif self.drag_control.hover or self.drag_control.drag:     d = 20
        else:                                                       d = 16

        painter.drawEllipse(x - d/2, y - d/2, d, d)


    def paintEvent(self, paintEvent):
        """ Paints this widget's lines.
        """
        painter = QtGui.QPainter(self)
        self.draw_axes(painter)
        self.draw_center(painter)
        self.draw_x_handle(painter)
        self.draw_y_handle(painter)
        self.draw_z_handle(painter)

from node.scale import Scale
from node.base import get_name
