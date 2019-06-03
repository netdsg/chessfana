#!/usr/bin/python3

minYear = 2014
jsonGameDirectory = '/usr/lib/cgi-bin/'

import requests, json, os, datetime, sys

if len(sys.argv) == 1 or 'help' in sys.argv[1]:
    print('\n\tUsage:  python3 getChessStats.py <USERNAME>\n')
    sys.exit(1)

chessPlayer = sys.argv[1]
statsFile = chessPlayer + '_chessGames.json'

def getAllStats(chessPlayer):
    chessHash = {}
    archives = chessSession.get('https://api.chess.com/pub/player/' +  chessPlayer  + '/games/archives')
    archiveHash = json.loads(archives.text)
    for a in archiveHash['archives']:
        if int(a.split('/')[-2]) >= minYear:
            print('Downloading ' + a)
            getMonth = chessSession.get(a)
            monthHash = json.loads(getMonth.text)
            chessHash[a.split('/')[-2] + a.split('/')[-1]] = monthHash
    return chessHash

chessSession = requests.Session()
if not os.path.isfile(jsonGameDirectory + statsFile):
    chessHash = getAllStats(chessPlayer)

else:

    with open(jsonGameDirectory + statsFile) as ourfile:
        chessHash = json.load(ourfile)

    lastMonthSeen = list(sorted(chessHash.keys()))[-1]
    hashYear = int(lastMonthSeen[0:4])
    hashMonth = int(lastMonthSeen[4:6])
    currentYear = datetime.date.today().year
    currentMonth = datetime.date.today().month

    if hashYear != currentYear or hashMonth != currentMonth:
        chessHash = getAllStats(chessPlayer)

    else:
        print('downloading current month only')
        thisMonth = chessSession.get('https://api.chess.com/pub/player/' + chessPlayer + '/games/' + ("{:02d}".format(hashYear)) + '/' + ("{:02d}".format(hashMonth)))
        thisMonthHash = json.loads(thisMonth.text)
        chessHash[str(hashYear) + "{:02d}".format(hashMonth)] = thisMonthHash
 
with open(jsonGameDirectory + statsFile, 'w') as outfile:
    json.dump(chessHash, outfile)

print(jsonGameDirectory + statsFile + ' has been prepared')
