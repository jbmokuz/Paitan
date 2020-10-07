def parseGame(self,log):
    rex = re.search("log=(.*)[&]{0,1}",log)
    if rex == None:
        self.lastError = "Invalid log URL"
        return 1
    try:
        rex = rex.group(1).split("&")[0]
    except:
        self.lastError = "Some error parsing log URL"
        return 1
    if rex in self.logIds:
        self.lastError = "Already seen this log"
        return 1

    self.logIds.add(rex)

    game = getGameObject(log)
    names = [n.name for n in game.players]
    for n in names:
        if not n in self.players:
            self.players[n] = Player(n)
    for r in game.rounds:
        for agari in r.agari:

            player = names[agari.player]
            for yaku, han in agari.yaku:
                if han < 0:
                    continue
                if not yaku in self.players[player].yaku:
                    self.players[player].yaku[yaku] = 0
                self.players[player].yaku[yaku] += 1
            for yaku in agari.yakuman:
                yaku = "🌟**"+yaku+"**🌟"
                if not yaku in self.players[player].yaku:
                    self.players[player].yaku[yaku] = 0
                self.players[player].yaku[yaku] += 1

        for event in r.events:
            if event.type == "Call":
                if event.meld.type == "chakan" and event.meld.type != "kan":
                    player = names[event.player]
                    self.players[player].kans += 1
    owari = [j for i,j in  enumerate(game.owari.split(",")) if i % 2 == 0][:self.MAX_PLAYERS]
    for i,score in enumerate(owari):
        self.players[names[i]].score += int(score)

    ret = ""
    for p in names:
        ret += f"{self.players[p]}\n"
        ret += f"{[y for y in self.players[p].yaku]}\n"
    self.lastError = ret[:-1]

    return 0

def report(self,name,score,place=-1):
    if not name in self.players:
        self.players[name] = Player(name)
    player = self.players[name]
    player.scores.append(score)
    player.placements.append(place)
    return 0

def addPlayer(self,name):
    if not name in self.players:
        self.players[name] = Player(name)
        return 0
    else:
        self.lastError = f"{name} has already joined!"
        return 1
