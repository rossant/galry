"""Tutorial 10: Connecting interaction events and QT signals.

This tutorial shows how to connect interaction events defined in galry
with QT signals and slots. A window contains two widgets that communicate
to each other so as synchronizing their views.

"""

# We import galry.
from galry import *
import numpy as np
import numpy.random as rdn

class MyPaintManager(PaintManager):
    def initialize(self):
        
        # We define a white noise signal on [-1, 1].
        n = 10000
        x = np.linspace(-1., 1., n)
        y = .2 * rdn.randn(n)
        data = np.hstack((x.reshape((-1, 1)), y.reshape((-1, 1))))
        self.dataset = self.create_dataset(PlotTemplate, 
            position=data)
                                    
# We define two custom interaction events. They occur on the receiver side,
# when widget B needs to synchronize its navigation according to widget A,
# which triggered the event.
MyEvents = enum("SynchronizePanEvent", "SynchronizeZoomEvent")

# A custom interaction manager processes the synchronization by calling
# the `pan` and `zoom` methods of the InteractionManager.
class MyInteractionManager(InteractionManager):
    def process_extended_event(self, event, parameter):
        if event == MyEvents.SynchronizePanEvent:
            self.pan(parameter)
        if event == MyEvents.SynchronizeZoomEvent:
            self.zoom(parameter)

# In this custom widget, we just specify our two custom companion classes.
class MyWidget(GalryWidget):
    def initialize(self):
        self.set_companion_classes(paint_manager=MyPaintManager,
            interaction_manager=MyInteractionManager)
        
# Now we create a QT window with two synchronized widgets. It derives from
# AutodestructibleWindow just so that this tutorial can be run automatically
# by a testing script, which is able to tell windows to kill themselves 
# after a fixed duration. It does not matter here and you don't need to use
# this class, it is ok to derive this class from QMainWindow for your own
# windows, as soon as you don't intend to use galry's custom testing scripts.
class MyWindow(AutodestructibleWindow):
    
    # We define four QT signals, two for panning, two for zooming.
    # The pan signal has two scalar parameters (for x and y translation)
    # because the associated galry interaction event we'll link this signal to
    # accepts two parameters.
    # The zoom signal has four parameters, two for x (zooming amount, and
    # center of the zoom), idem for y.
    # We define two signals per event so as to avoid infinite recursion
    # problems, if widget A triggers a pan signal, which triggers a pan event
    # in widget B, which triggers the same pan signal, etc. If the
    # synchronization were unidimensional, we could have just one pan signal.
    pan1 = QtCore.pyqtSignal(float, float)
    pan2 = QtCore.pyqtSignal(float, float)
    zoom1 = QtCore.pyqtSignal(float, float, float, float)
    zoom2 = QtCore.pyqtSignal(float, float, float, float)
    
    # This is just internal stuff for handling windows autodestruction.
    # The rest of this method is dedicated to widget initialization.
    def initialize(self, autodestruct=None):
        self.set_autodestruct(autodestruct)
        
        # We first define a base widget which will contain the whole window.
        self.widget = QtGui.QWidget(self)
        
        # This widget allows to put several widgets in a vertical layout
        self.layout = QtGui.QVBoxLayout(self.widget)
        
        # We define two custom widgets.
        self.glwidget1 = MyWidget()
        self.glwidget2 = MyWidget()
        
        # In widget1, we connect the galry `Pan` and `Zoom` interaction events
        # to the `pan1` and `zoom1` QT signals. As soon as such an interaction
        # event occurs due to an user action, one of these QT signals is 
        # raised.
        self.glwidget1.connect_events(InteractionEvents.PanEvent, self.pan1)
        self.glwidget1.connect_events(InteractionEvents.ZoomEvent, self.zoom1)
        
        # Now, in widget2, we connect these signals to our custom interaction
        # events which synchronize the views. Note that we could also have
        # linked directly these QT signals to the native interaction events,
        # but we would have had infinite recursion loop problems. For
        # an unidirectional signal, that wouldn't have been a problem.
        self.glwidget2.connect_events(self.pan1, MyEvents.SynchronizePanEvent)
        self.glwidget2.connect_events(self.zoom1, MyEvents.SynchronizeZoomEvent)
        
        # This is the exact symmetrical of the above code snippet.
        self.glwidget2.connect_events(InteractionEvents.PanEvent, self.pan2)
        self.glwidget2.connect_events(InteractionEvents.ZoomEvent, self.zoom2)
        
        self.glwidget1.connect_events(self.pan2, MyEvents.SynchronizePanEvent)
        self.glwidget1.connect_events(self.zoom2, MyEvents.SynchronizeZoomEvent)
        
        # Finally, we add our Galry widgets to the layout.
        self.layout.addWidget(self.glwidget1)
        self.layout.addWidget(self.glwidget2)
        self.setCentralWidget(self.widget)
        
    # This QT event should be overriden so that the PaintManager can clean
    # everything up as soon as the window is closed.
    def closeEvent(self, e):
        self.glwidget1.paint_manager.cleanup()
        self.glwidget2.paint_manager.cleanup()
        
show_window(MyWindow)
