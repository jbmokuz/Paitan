import unittest
from database import *
from functions import *

class TestWaiting(unittest.TestCase):
    
    def setUp(self):
        self.gi = GameInstance()

    def testAddWaiting(self):


