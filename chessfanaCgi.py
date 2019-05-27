#!/usr/bin/python3

jsonGameDirectory = '/usr/lib/cgi-bin'

import cgi, subprocess, os, json, sys, datetime, re
from http import cookies
from operator import itemgetter

def getEpoch(dt):
    return int((datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.%fZ") - datetime.datetime(1970, 1, 1)).total_seconds())

def getMasterPlayerHash():
    fileList = []
    allFiles = subprocess.getoutput(['ls ' + jsonGameDirectory]).split()
    for f in allFiles:
        if re.search(r'_chessGames.json', f):
            fileList.append(f)
    masterPlayerHash = {}
    for p in fileList:
        with open(p) as ourfile:
            playerHash = json.load(ourfile)
        findPlayerName = re.match(r'(.*)_chessGames.json', p)
        chessPlayer = findPlayerName.groups()[0]
        masterPlayerHash[chessPlayer] = playerHash
    return masterPlayerHash

def getTableData(chessHash, fromTime, toTime, color, gameType):
    gameHash = {}
    gameHash['totalGames'] = 0
    for m in chessHash:
        for g in chessHash[m]['games']:
            if g['end_time'] > int(fromTime) and g['end_time'] <= int(toTime):
                if g[color]['username'] == 'netdsg' and g['time_class'] == gameType:
                    opening = re.search(r'(https://www.chess.com/openings/\S+)\"', str(g['pgn']))
                    if opening:
                        opening = opening.groups()[0]
                        if opening not in gameHash:
                            gameHash[opening] = {}
                            gameHash[opening]['occured'] = 1
                            gameHash[opening]['win'] = 0
                            gameHash[opening]['loose'] = 0
                            if g[color]['result'] == 'win':
                                gameHash[opening]['win'] += 1
                            else:
                                gameHash[opening]['loose'] += 1
                        else:
                            gameHash[opening]['occured'] += 1
                            if g[color]['result'] == 'win':
                                gameHash[opening]['win'] += 1
                            else:
                                gameHash[opening]['loose'] += 1
    for o in gameHash:
        if o != 'totalGames':
            gameHash[o]['winRatio'] = round(gameHash[o]['win'] / gameHash[o]['occured'], 2)
    tableRatioList = []
    for i in gameHash:
        if i != 'totalGames':
            tableRatioList.append([round(gameHash[i]['winRatio'] * 100), gameHash[i]['occured'], i])
    tableRatioList = sorted(tableRatioList, key = itemgetter(0 ,1), reverse=True)
    return tableRatioList[0:20]
#######################################################################
### API - search
#######################################################################

if os.environ['REQUEST_URI'] == os.environ['SCRIPT_NAME'] + '/search':
    displaySources = ['netdsg black top']
    masterPlayerHash = getMasterPlayerHash()
    for chessPlayer in masterPlayerHash:
        chessHash = masterPlayerHash[chessPlayer]
        gameTypes = set()
        for m in chessHash:
            for g in chessHash[m]['games']:
                gameTypes.add(g['time_class'])
        for t in gameTypes:
            displaySources.append(chessPlayer + ' ' + t + ' rating')
            displaySources.append(chessPlayer + ' ' + t + ' black table')
            displaySources.append(chessPlayer + ' ' + t + ' white table')
    print('Content-type: text/html\n\n')
    print(json.dumps(displaySources))


########################################################################
### API - query
########################################################################

elif os.environ['REQUEST_URI'] == os.environ['SCRIPT_NAME'] + '/query':
    masterPlayerHash = getMasterPlayerHash()
    dataList = []
    queryData = sys.stdin.read()
    queryHash = json.loads(queryData)
    fromTime = str(getEpoch(queryHash['range']['from']))
    toTime = str(getEpoch(queryHash['range']['to']))
    for m in queryHash['targets']:
        ourTarget = m['target']
        chessPlayer = ourTarget.split()[0]
        if m['type'] == 'table':
            tableTop = getTableData(masterPlayerHash[chessPlayer], fromTime, toTime, ourTarget.split()[2], ourTarget.split()[1])
            tableHash = {}
            tableHash['columns'] = []
            tableHash['columns'].append({'text' : 'Win Ratio', 'type' : 'string'})
            tableHash['columns'].append({'text' : '# of Games', 'type' : 'number'})
            tableHash['columns'].append({'text' : 'Opening Link', 'type' : 'string'})
            tableHash['rows'] = tableTop
            tableHash['type'] = 'table'
            dataList.append(tableHash)
        else:
            gameType = ourTarget.split()[1]
            dataPoints = []
            for month in masterPlayerHash[chessPlayer]:
                for g in masterPlayerHash[chessPlayer][month]['games']:
                    if g['time_class'] == gameType:
                        if g['end_time'] > int(fromTime) and g['end_time'] <= int(toTime):
                            if g['white']['username'] == chessPlayer:
                                dataPoints.append([g['white']['rating'], (g['end_time'] * 1000)])
                            else:
                                dataPoints.append([g['black']['rating'], (g['end_time'] * 1000)])
            dataPoints = sorted(dataPoints, key=itemgetter(1)) 
            if dataPoints != []:
                dataPoints.append([dataPoints[-1][0], int(toTime) * 1000])
            dataHash = {}
            dataHash['target'] = m['target']
            dataHash['datapoints'] = dataPoints
            dataList.append(dataHash)
 
    print('Content-type: application/json\n\n')
    print(json.dumps(dataList))

#######################################
### Datastore Test Response
#######################################

else:
    print('Content-type: text/html\n\n')
    print('Test: OK')
    print('<br>')
