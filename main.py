from zlib import Z_NO_COMPRESSION
import networkx as nx
import pandas as pd

lines       = pd.read_csv('london.lines.csv', index_col=0)
stations    = pd.read_csv('london.stations.csv', index_col=0)
connections = pd.read_csv('london.connections.csv')

#filter out DLR
connections=connections[connections['line']!=13] 
connections=connections[connections['line']!=5]

station1=connections["station1"]
station2=connections["station2"]
stationMasterList=list(set(pd.concat([station1, station2]).to_list()))

stations=stations[stations.index.isin(stationMasterList)]

graph = nx.Graph()

for connection_id, connection in connections.iterrows():
    station1_name = stations.loc[connection['station1']]['name']
    station2_name = stations.loc[connection['station2']]['name']
    graph.add_edge(station1_name, station2_name, time = connection['time'])
    
#add the connection between Bank and Monument manually
graph.add_edge('Bank', 'Monument', time = 1)

#This function returns the only stations which match the result of any guess
def getPossiblesList(startStation, maxDistance, zoneFlag): #zoneFlag takes values as: green=0, yellow=1, orange=2, red=3
    startZone=stations[stations["name"]==startStation]["zone"].item()
    returnList=[]
    for id, stat in stations['name'].iteritems():
        if len(nx.shortest_path(graph, startStation, stat))-1 == maxDistance:
            details = stations[stations["name"]==stat][["name", "zone", ]].to_records(index=False)
            name=details[0][0]
            zone=details[0][1]
            if zoneFlag==0:
                if startZone==zone:
                    returnList.append(name)
            if zoneFlag==1:
                if abs(zone-startZone)>=1 and abs(zone-startZone)<2:
                    returnList.append(name)
            if zoneFlag==2:
                if abs(zone-startZone)>=2 and abs(zone-startZone)<3:
                    returnList.append(name)
            if zoneFlag==3:
                if abs(zone-startZone)>=3:
                    returnList.append(name)
    return returnList

#This function mimicks the way the game responds to guesses
def tubleResult(startStation, endStation):
    path=len(nx.shortest_path(graph, startStation, endStation))-1 #minus one as both stations are included in the result
    startZone=stations[stations["name"]==startStation]["zone"].item()
    endZone=stations[stations["name"]==endStation]["zone"].item()

    if abs(endZone-startZone)<1.0:
        zoneFlag=0
    elif abs(endZone-startZone)>=1 and abs(endZone-startZone)<2:
        zoneFlag=1
    elif abs(endZone-startZone)>=2 and abs(endZone-startZone)<3:
        zoneFlag=2
    elif abs(endZone-startZone)>=3:
        zoneFlag=3
    return(path, zoneFlag) #zoneFlag takes values as: green=0, yellow=1, orange=2, red=3


###Run the code###

fullList=[] #a full list of the stations, for the case where there are no previous guesses
for id, stat in stations['name'].iteritems():
    fullList.append(stat)

guessList=[]
guessList.append(('Woodford', 15, 2)) #Station name, number of stops away, encoded colour of the tile
guessList.append(('Kentish Town', 2, 0)) #Station name, number of stops away, encoded colour of the tile

returnLists=[] #store all the possible answers, based on guesses
for guess in guessList:
    returnLists.append(getPossiblesList(guess[0], guess[1], guess[2]))

remainderList=[] #this will store a unique/deduped list of stations
if len(returnLists)==0:
    remainderList=list(set(fullList)) #clumsy dedup
else:
    remainderList=list(set.intersection(*[set(list) for list in returnLists])) #funky bit of code which I hope gives me the intersection of all results
    print(remainderList)

if len(remainderList)==1:
    print ("The answer is "+remainderList[0])
if len(remainderList)==2:
    print ("The answer is either "+remainderList[0] +" or "+remainderList[1])
else:
    #Remainder List Loop
    bestDiff=1000
    bestStation=""
    for guessStat in remainderList:
        outcomes=[]
        for remainderStat in remainderList:
            outcomes.append(tubleResult(guessStat, remainderStat))
        numOutcomes=len(outcomes)

        numUniqueOutcomes=len(set(outcomes))
        diff=numOutcomes-numUniqueOutcomes
        if diff<bestDiff:
            bestDiff=diff
            bestStation=guessStat

    #Full List Loop
    for guessStat in fullList:
        outcomes=[]
        for remainderStat in remainderList:
            outcomes.append(tubleResult(guessStat, remainderStat))
        numOutcomes=len(outcomes)

        numUniqueOutcomes=len(set(outcomes))
        diff=numOutcomes-numUniqueOutcomes
        if diff<bestDiff:
            bestDiff=diff
            bestStation=guessStat

    print('The best guess is ' +bestStation +" with a duplication of "+ str( bestDiff))