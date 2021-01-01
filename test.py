import unittest
from database import *


class DisPlayer():
    def __init__(self,name,id):
        self.name = name
        self.id = id

    def __eq__(self, other):
        return self.id == other.id


class TestDB(unittest.TestCase):

    def testCreateUSer(self):
        deleteUser(1)
        deleteUser(2)
        deleteUser(3)
        
        passwd1 = createUser(1,"TestUser1")
        passwd2 = createUser(2,"TestUser2")
        passwd3 = createUser(3,"TestUser3")

        self.assertEqual(type(passwd1),type(""))
        self.assertEqual(createUser(1,"TestUser1"),-1)
        self.assertEqual(createUser(1,"TestUserzz"),-2)

        self.assertEqual(deleteUser(2),0)
        self.assertEqual(deleteUser(2),-1)

        self.assertTrue(getUser(1))
        self.assertFalse(getUser(2))
        self.assertTrue(getUser(3))

        deleteUser(1)
        deleteUser(3)        


    def testCreateClub(self):
        deleteClub(11)
        deleteClub(12)
        deleteClub(13)

        self.assertEqual(createClub(11,"TestClub1"),11)
        self.assertEqual(createClub(12,"TestClub2"),12)
        self.assertEqual(createClub(13,"TestClub3"),13)

        self.assertEqual(deleteClub(12),0)
        self.assertEqual(deleteClub(12),-1)

        self.assertTrue(getClub(11))
        self.assertFalse(getClub(12))
        self.assertTrue(getClub(13))

        deleteClub(11)
        deleteClub(13)


    def testCreateTourney(self):

        deleteTenhouGame(1)

        deleteUser(1)
        deleteUser(2)
        deleteUser(3)

        passwd1 = createUser(1,"TestUser1")
        passwd2 = createUser(2,"TestUser2")
        passwd3 = createUser(3,"TestUser3")

        deleteClub(11)
        deleteClub(12)

        self.assertEqual(createClub(11,"TestClub1"),11)
        self.assertEqual(createClub(12,"TestClub2"),12)

        t1 = createTourney(11,"Club11 Tourney1")
        t2 = createTourney(11,"Club11 Tourney2")
        t3 = createTourney(12,"Club12 Tourney1")


        self.assertEqual(len(getTourneysForClub(11)),2)

        self.assertEqual(deleteTourney(t1),0)
        self.assertEqual(deleteTourney(t1),-1)

        self.assertEqual(len(getTourneysForClub(11)),1)


        game = createTenhouGame("http://www.test.com","ASan","BSan","CSan","DSan",30000,25000,35000,30000)

        self.assertNotEqual(game,-1)
        self.assertEqual(createTenhouGame("http://www.test.com","ASan","BSan","CSan","DSan",30000,25000,35000,30000),-1)

        game2 = createTenhouGame("http://www.test.com2","ASan","BSan","CSan","DSan",30000,25000,35000,30000)

        self.assertEqual(addGameToTourney(t2,game),0)
        self.assertEqual(addGameToTourney(t2,game),-3)

        self.assertEqual(len(getGamesForTourney(t2)),1)

        self.assertEqual(addGameToTourney(t2,game2),0)

        self.assertEqual(len(getGamesForTourney(t2)),2)


        self.assertEqual(deleteTenhouGame(game),0)
        self.assertEqual(deleteTenhouGame(game),-1)

        self.assertEqual(deleteTenhouGame(game2),0)


        self.assertEqual(deleteTourney(t2),0)
        self.assertEqual(deleteTourney(t3),0)

    def testUserToClub(self):
        deleteUser(1)
        deleteUser(2)
        deleteUser(3)

        passwd1 = createUser(1,"TestUser1")
        passwd2 = createUser(2,"TestUser2")
        passwd3 = createUser(3,"TestUser3")

        deleteClub(11)
        deleteClub(12)
        deleteClub(13)

        self.assertEqual(createClub(11,"TestClub1"),11)
        self.assertEqual(createClub(12,"TestClub2"),12)
        self.assertEqual(createClub(13,"TestClub3"),13)

        self.assertEqual(addUserToClub(11,1),0)
        self.assertEqual(addUserToClub(11,77),-1)
        self.assertEqual(addUserToClub(77,1),-2)
        self.assertEqual(addUserToClub(11,1),-3)

        self.assertEqual(addUserToClub(12,1),0)
        self.assertEqual(addUserToClub(13,1),0)

        self.assertEqual(addUserToClub(11,2),0)
        self.assertEqual(addUserToClub(11,3),0)

        self.assertEqual(len(getClubsForUser(1)),3)
        self.assertEqual(len(getClubsForUser(2)),1)
        self.assertEqual(len(getClubsForUser(3)),1)

        self.assertEqual(len(getUsersForClub(11)),3)
        self.assertEqual(len(getUsersForClub(12)),1)
        self.assertEqual(len(getUsersForClub(13)),1)

        self.assertEqual(deleteUser(2),0)

        self.assertEqual(len(getClubsForUser(1)),3)
        self.assertEqual(len(getClubsForUser(3)),1)

        self.assertEqual(len(getUsersForClub(11)),2)
        self.assertEqual(len(getUsersForClub(12)),1)
        self.assertEqual(len(getUsersForClub(13)),1)

        self.assertEqual(deleteClub(12),0)

        self.assertEqual(len(getClubsForUser(1)),2)
        self.assertEqual(len(getClubsForUser(3)),1)

        self.assertEqual(len(getUsersForClub(11)),2)
        self.assertEqual(len(getUsersForClub(13)),1)

        deleteUser(1)
        deleteUser(3)

        deleteClub(11)
        deleteClub(13)


    def testShuffle(self):

        deleteUser(1)
        deleteUser(2)
        deleteUser(3)
        deleteUser(4)
        deleteUser(5)
        deleteUser(6)
        deleteUser(7)
        deleteUser(8)
        deleteUser(9)
        deleteUser(10)

        deleteClub(11)
        
        passwd1 = createUser(1,"User1")
        passwd2 = createUser(2,"User2")
        passwd3 = createUser(3,"User3")
        passwd4 = createUser(4,"User4")
        passwd5 = createUser(5,"User5")
        passwd6 = createUser(6,"User6")
        passwd7 = createUser(7,"User7")
        passwd8 = createUser(8,"User8")
        passwd9 = createUser(9,"User9")
        passwd10 = createUser(10,"User10")


        createClub(11,"TestClub1")

        t1 = createTourney("Club1 Tourney1"+str(random.randint(0,0xFFFFFFFF)))
        
        tourney = getTourney(t1)

        
        tbl1 = createTable(t1, tourney.current_round, 1, 2, 3, 4)
        tbl2 = createTable(t1, tourney.current_round, 5, 6, 7, 8)
        tbl3 = createTable(t1, tourney.current_round, 9, 10, None, None)

        print(tbl1)
        print(tbl2)
        print(tbl3)

        tables = getTablesForRoundTourney(t1, 1)

        self.assertEquals(len(tables),3)
        
        finishTable(tbl2)

        tables = getTablesForRoundTourney(t1, 1)

        self.assertEquals(len(tables),3)
        
        tables = getTablesForRoundTourney(t1, 1,True)
        
        self.assertEquals(len(tables),2)
        
        deleteTourney(t1)
        deleteTable(tbl1)
        deleteTable(tbl2)
        deleteTable(tbl3)


        
"""
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
"""
        
if __name__ == '__main__':
    unittest.main()
