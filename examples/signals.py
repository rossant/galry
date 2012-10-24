from galry import *

class MyWindow(AutodestructibleWindow):
    # signal that will be raised at each PanEvent
    # parameters are dx and dy
    panSignal = QtCore.pyqtSignal(float, float)
    
    def initialize(self, autodestruct=None):
        # super(MyWindow, self).__init__()
        self.set_autodestruct(autodestruct)
        # create the widget
        self.widget = GalryWidget()
        # connect the PanEvent to the panSignal: each occurence of
        # the PanEvent triggers the signal
        self.widget.connect_event_to_signal(InteractionEvents.PanEvent,
                                            self.panSignal)
        # connect the panSignal to the method panSignalRaised
        self.panSignal.connect(self.panSignalRaised)
        # show the widget
        self.setGeometry(100, 100, self.widget.width, self.widget.height)
        self.setCentralWidget(self.widget)
        # show the window
        self.show()
        
    def panSignalRaised(self, *args):
        print "pan dx=%.3f, dy=%.3f" % args

if __name__ == '__main__':
    print "Left click and move your mouse!"
    window = show_basic_window(window_class=MyWindow)