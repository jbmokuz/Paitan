from parsers.TenhouDecoder import getGameObject
import re

# http://tenhou.net/0/?log=2020070913gm-0209-19691-21db0170&tw=2         

def getLogId(log):
    ret = ""
    rex = re.search("log=(.*)[&]{0,1}",log)
    if rex == None:
        self.lastError = "Invalid log URL"
        return 1
    try:
        if "&" in rex.group(1):
            ret = rex.group(1).split("&")[0]
        else:
            ret = rex.group(1).split("&")[0]            
    except:
        self.lastError = "Some error parsing log URL"
        return 1
    
    return ret
    

def parseTenhou(log):

    game = getGameObject(log)
    names = [n.name for n in game.players]
    scores = [j for i,j in  enumerate(game.owari.split(",")) if i % 2 == 0][:len(names)]

    if len(game.owari.split(",")) > 8:
        shugi = [j for i,j in  enumerate(game.owari.split(",")) if i % 2 == 0][len(names):]
    else:
        shugi = [0 for i in range(len(names))]

    ret = []

    for i in range(len(names)):
        ret.append([names[i],int(scores[i]),int(shugi[i])])

    return ret

