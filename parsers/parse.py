import re
from parsers.TenhouDecoder import getGameObject


class TablePlayer():
    def __init__(self, name, score, payout, shugi, binghou, kans):
        self.name = name
        self.score = score
        self.payout = payout
        self.shugi = shugi
        self.binghou = binghou
        self.kans = kans

    def getList(self):
        return [self.name, self.score, self.payout, self.shugi, self.binghou, self.kans]


class TableRate():

    def __init__(self, name, rate=0.3, shugi=.50, target=30000, start=25000, uma=[30, 10, -10, -30]):
        self.name = name
        self.rate = rate
        self.shugi = shugi
        self.target = target
        self.start = start
        # @ WARNING!!! Will not work for sanma
        self.oka = (target - start) * 4
        self.uma = uma

    def __eq__(self, other):
        return (
                self.rate == other.rate and self.shugi == other.shugi and self.oka == other.oka and self.target == other.target and self.start == other.start and self.uma == other.uma)

    def __str__(self):
        return f"Rate: {self.rate}, Start: {self.start}, Target: {self.target}, Shugi: {self.shugi}, Oka: {self.oka}, Uma: {self.uma}"


# default values rate=0.3, shugi=.50, target=30000, start=25000, uma=[30,10,-10,-30]
TENSAN = TableRate(name="tensan")
TENGO = TableRate(name="tengo", rate=0.5, shugi=1)
TENPIN = TableRate(name="tenpin", rate=1, shugi=2)
STANDARD = TableRate(name="standard", rate=1, shugi=0, start=25000, target=30000, uma=[30, 10, -10, -30])
BINGHOU = TableRate(name="binghou", rate=1, shugi=0, start=30000, target=30000, uma=[15, 5, -5, -15])

# BINGHOU Stuff

# http://tenhou.net/0/?log=2020070913gm-0209-19691-21db0170&tw=2

SPECIAL_TILE = "5pin"

CARD = ["Honitsu", "Ura3", "Ikkitsuukan", ">50fu", "Haneman",
        "Nomi Gang", "Jikaze", "Ippatsu", "Tanyao", "Chinitsu",
        "Chanta", "Riichi", "Kan!", "Uradora", "Chiitoitsu",
        "3Melds", "Yakuhai", "Menzen", "Sanshoku", "3zou or Pei tanki",
        "Other Yaku", f"2 {SPECIAL_TILE}", "Pinfu", "Iipeikou", "Toitoi"]


# {'type': 'RON', 'player': 1, 'hand': ['7s0', '7s1', '7s2', '4p1', '5p1', '6p2', '7p3', '8p2', '9p2', '5m2', '6m3', '7m2', 'rd0', 'rd2'], 'fu': 40, 'points': 2600, 'limit': '', 'dora': ['8p3'], 'machi': ['6p2'], 'melds': [], 'closed': True, 'uradora': [], 'fromPlayer': 2, 'yaku': [['Riichi', 1], ['Dora', 1], ['Uradora', 0]], 'yakuman': []}

def intToYaku(i):
    ret = []
    for yaku in CARD:
        if i & 1 == 1:
            ret.append(yaku)
        i = i >> 1
    return ret

def getTileCount(agari,countTile):
    tileCount = 0
    for meld in agari.melds:
        for tile in meld.tiles:
            if tile.asdata()[:2] == countTile[:2]:
                tileCount += 1
    tileCount += len([i for i in agari.hand if countTile[:2] in i.asdata()[:2]])
    return tileCount
    
def updateBinghou(bing, kans, names, game):
    global CARD

    for r in game.rounds:
        for agari in r.agari:

            player = names[agari.player]

            if agari.fu > 50:
                bing[agari.player] = bing[agari.player] | (1 << CARD.index(">50fu"))

            hane = sum([i[1] for i in agari.yaku])
            if hane == 6 or hane == 7:
                bing[agari.player] = bing[agari.player] | (1 << CARD.index("Haneman"))

            if getTileCount(agari, SPECIAL_TILE) >= 2:
                bing[agari.player] = bing[agari.player] | (1 << CARD.index(f"2 {SPECIAL_TILE}"))

            if "3s" in [machi.asdata()[:2] for machi in agari.machi]:
                bing[agari.player] = bing[agari.player] | (1 << CARD.index("3zou or Pei tanki"))
            if "nw" in [machi.asdata()[:2] for machi in agari.machi] and getTileCount(agari, "nw") >= 2:
                bing[agari.player] = bing[agari.player] | (1 << CARD.index("3zou or Pei tanki"))

            if len([meld for meld in agari.melds]) >= 3:
                bing[agari.player] = bing[agari.player] | (1 << CARD.index("3Melds"))

            for yaku, han in agari.yaku:
                if han < 0:
                    continue
                # print("YAKU",yaku,player)
                if yaku.split(" ")[0] in CARD and not (yaku == "Uradora" and han == 0):
                    bing[agari.player] = bing[agari.player] | (1 << CARD.index(yaku.split(" ")[0]))
                elif yaku != "Uradora" and yaku != "Dora" and yaku != "Akadora":
                    bing[agari.player] = bing[agari.player] | (1 << CARD.index("Other Yaku"))
                if yaku == 'Uradora' and han > 2:
                    bing[agari.player] = bing[agari.player] | (1 << CARD.index("Ura3"))
                if (yaku == "Riichi" or yaku == "Haitei" or yaku == "Houtei" or yaku == "Rinshan") and sum([i[1] for i in agari.yaku]) == 1:
                    bing[agari.player] = bing[agari.player] | (1 << CARD.index("Nomi Gang"))
                if yaku == "Rinshan kaihou":
                    kans[agari.player] += 2
                if yaku == "Chankan":
                    kans[agari.player] += 2
                if yaku == "Sankantsu":
                    kans[agari.player] += 2

            for yaku in agari.yakuman:
                yaku = "🌟**" + yaku + "**🌟"
                print("YAKUMAN",yaku,player)
                if yaku == "Suukantsu":
                    kans[agari.player] += 1024
                #bing[agari.player] = bing[agari.player] | (1 << 25)

        for pos, event in enumerate(r.events):
            """
            if not event.type in ["Discard","Call"]:
                print(event.type,event.tile)
            if event.type == "Dora":
                import pdb
                pdb.set_trace()
            """
            if event.type == "Call":
                # Open kan
                if event.meld.type == "chakan":
                    player = names[event.player]
                    bing[event.player] = bing[event.player] | (1 << CARD.index("Kan!"))
                    print("CHAKAN", player, r.events[pos - 1])
                    kans[event.player] += 1
                    # Kan was called 
                    if event.player != event.meld.fromPlayer:
                        kans[event.meld.fromPlayer] -= 1
                # Closed kan
                if event.meld.type == "kan":
                    player = names[event.player]
                    bing[event.player] = bing[event.player] | (1 << CARD.index("Kan!"))
                    print("KAN", player, r.events[pos - 1])
                    kans[event.player] += 1


def getLogId(log):
    ret = ""
    rex = re.search("log=(.*)[&]{0,1}", log)
    if rex == None:
        lastError = "Invalid log URL"
        return -1
    try:
        if "&" in rex.group(1):
            ret = rex.group(1).split("&")[0]
        else:
            ret = rex.group(1).split("&")[0]
    except:
        lastError = "Some error parsing log URL"
        return -2

    return ret


def parseTenhou(log):
    game = getGameObject(log)
    if game == None:
        return None
    names = [n.name for n in game.players]
    binghou = [0, 0, 0, 0]
    kans = [0, 0, 0, 0]

    updateBinghou(binghou, kans, names, game)
    scores = [j for i, j in enumerate(game.owari.split(",")) if i % 2 == 0][:len(names)]

    if len(game.owari.split(",")) > 8:
        shugi = [j for i, j in enumerate(game.owari.split(",")) if i % 2 == 0][len(names):]
    else:
        shugi = [0 for i in range(len(names))]

    ret = []

    print("BING", [intToYaku(i) for i in binghou])

    for i in range(len(names)):
        ret.append(TablePlayer(names[i], int(scores[i]), 0, int(shugi[i]), binghou[i], kans[i]))

    return ret


def scorePayout(players, tableRate):
    players.sort(key=lambda x: x.score, reverse=True)
    lastScore = ""
    lastScore += f"{tableRate}\n\n"
    lastScore += f"All players begin with **Start**[{tableRate.start}] points and pay the difference of the **Target**[{tableRate.target}] to first place\n"
    lastScore += f"So first place gets an **Oka** of ({tableRate.start} - {tableRate.target}) × {len(players)} = {(tableRate.target - tableRate.start) * len(players)}\n\n"
    lastScore += f"A **Rate** of {tableRate.rate} means each 1000 points is ${tableRate.rate:.2f}\n\n"

    oka = [tableRate.oka] + [0] * len(players)  # giving 1st place oka bonus
    for i, p in enumerate(players):
        #name, p.score, shugi, binghou, kans = p
        score = p.score * 100
        lastScore += f"#{i + 1}Place: (Score[{p.score}] + Oka[{oka[i]}] - Target[({tableRate.target})])/1000) × Rate[{tableRate.rate}] = ${((p.score + oka[i] - tableRate.target) / 1000) * tableRate.rate:.2f}\n"

    lastScore += "\n"
    lastScore += f"**Uma** of {tableRate.uma} is also applied based on position, and multiplied by the table **Rate**[{tableRate.rate}]\n"

    for i, p in enumerate(players):
        lastScore += f"#{i + 1}Place: ${tableRate.rate * tableRate.uma[i]}\n"

    lastScore += "\n"
    lastScore += f"Finally the **Shugi Rate**[{tableRate.shugi}] is multiplied by the number of shugi and added to the final score\n"

    for i, p in enumerate(players):
        lastScore += f"#{i + 1}Place: Shugi rate[{tableRate.shugi}] × Player Shugi[{p.shugi}] = {tableRate.shugi * p.shugi}\n"

    lastScore += "\n"
    lastScore += "Finally\n"

    ret = []
    for i, p in enumerate(players):

        score = p.score * 100
        calc = (((score + oka[i] - tableRate.target) / 1000) + tableRate.uma[
            i]) * tableRate.rate + tableRate.shugi * p.shugi
        payout = round(calc, 2)
        ret.append(TablePlayer(p.name, score, payout, p.shugi, p.binghou, p.kans))
        lastScore += f"#{i + 1}Place: (((({score}+{oka[i]}-{tableRate.target})/1000)+{tableRate.uma[i]})×{tableRate.rate}+{tableRate.shugi}×{p.shugi}) = ${payout}\n"

    return [ret, lastScore]
