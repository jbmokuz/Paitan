from parsers.TenhouDecoder import getGameObject
from parsers.parse import updateBinghou
from parsers.parse import intToYaku
g = getGameObject("http://tenhou.net/4/?log=2022110813gm-0209-18044-7583364d")
names = [n.name for n in g.players]
binghou = [0, 0, 0, 0]
kans = [0, 0, 0, 0]


updateBinghou(binghou,kans,names,g)
for i in binghou:
    print(hex(i))
    print(intToYaku(i))

