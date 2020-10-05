import unittest
from database import *


class DisPlayer():
    def __init__(self,name,id):
        self.name = name
        self.id = id

    def __eq__(self, other):
        return self.id == other.id

class TestLobby(unittest.TestCase):
    
    def setUp(self):
        self.guildID = "TESTID"
        self.gi = getGameInstance(self.guildID)
        self.player1 = DisPlayer("Asan",1)
        self.player2 = DisPlayer("Bsan",2)
        self.player3 = DisPlayer("Csan",3)
        self.player4 = DisPlayer("Dsan",4)
        self.player5 = DisPlayer("Esan",5)
        self.player6 = DisPlayer("Fsan",6)
        self.player7 = DisPlayer("Gsan",7)
        self.player8 = DisPlayer("Hsan",8)
        self.player9 = DisPlayer("Isan",9)
        self.player10 = DisPlayer("Jsan",10)
        self.player11 = DisPlayer("Ksan",11)
        self.player12 = DisPlayer("Lsan",12)
        self.player13 = DisPlayer("Msan",13)        

    def testAddWaiting(self):
        self.gi.reset()
        self.assertEqual(self.gi.waiting, [])
        self.assertEqual(self.gi.addWaiting(self.player1),0)
        self.assertEqual(self.gi.waiting, [self.player1])
        self.assertEqual(self.gi.addWaiting(self.player1),1)        
        self.assertEqual(self.gi.waiting, [self.player1])
        self.assertEqual(self.gi.addWaiting(self.player2),0)
        self.assertEqual(self.gi.waiting, [self.player1,self.player2])        
        
    def testRemoveWaiting(self):
        self.gi.reset()
        self.assertEqual(self.gi.waiting, [])
        self.assertEqual(self.gi.addWaiting(self.player1),0)
        self.assertEqual(self.gi.removeWaiting(self.player1),0)
        self.assertEqual(self.gi.waiting, [])
        self.gi.addWaiting(self.player1)
        self.gi.addWaiting(self.player2)
        self.assertEqual(self.gi.addWaiting(self.player3),0)
        self.assertEqual(self.gi.addWaiting(self.player3),1)
        self.gi.addWaiting(self.player4)
        self.assertEqual(self.gi.removeWaiting(self.player2),0)
        self.assertEqual(self.gi.waiting, [self.player1,self.player3,self.player4])
        self.assertEqual(self.gi.removeWaiting(self.player3),0)
        self.assertEqual(self.gi.waiting, [self.player1,self.player4])
        self.assertEqual(self.gi.addWaiting(self.player5),0)
        self.assertEqual(self.gi.waiting, [self.player1,self.player4,self.player5])
        self.assertEqual(self.gi.removeWaiting(self.player9),1)
        self.assertEqual(self.gi.waiting, [self.player1,self.player4,self.player5])        

    def testShuffle(self):
        self.gi.reset()
        self.assertFalse(self.gi.addWaiting(self.player1))
        self.gi.addWaiting(self.player2)
        self.assertEqual(self.gi.shuffle(),{})
        self.assertEqual(self.gi.waiting,[self.player1,self.player2])
        self.gi.addWaiting(self.player3)
        self.gi.addWaiting(self.player4)
        self.gi.addWaiting(self.player5)
        self.gi.addWaiting(self.player6)
        self.gi.addWaiting(self.player7)
        self.gi.addWaiting(self.player8)
        self.gi.addWaiting(self.player9)
        ret1 = self.gi.shuffle()
        self.assertEqual(len(self.gi.waiting), 1)
        self.assertEqual(len(ret1["1"]), 4)
        ret2 = self.gi.shuffle()
        self.assertEqual(ret2,{})
        self.assertEqual(len(self.gi.tables), 2)
        self.gi.addWaiting(self.player10)
        self.gi.addWaiting(self.player11)
        self.gi.addWaiting(self.player12)
        self.gi.addWaiting(self.player13)
        ret3 = self.gi.shuffle(2)
        self.assertEqual(len(ret3),2)
        self.assertEqual(len(self.gi.waiting), 1)
        self.assertEqual(len(self.gi.tables), 4)
        self.assertEqual(self.gi.tableGG("17"),1)
        self.assertEqual(self.gi.tableGG("3"),0)
        self.assertEqual(self.gi.tableGG("3"),1)

        
if __name__ == '__main__':
    unittest.main()
