class Manager(object):
    """Manager base class for all managers."""
    def __init__(self, parent):
        self.parent = parent
        self.reset()
        
    def reset(self):
        """To be implemented."""
