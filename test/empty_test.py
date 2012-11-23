import unittest
from galry import *
from test import GalryTest

class EmptyTest(GalryTest):
    def test(self):
        self.show()
    
if __name__ == '__main__':
    unittest.main()
