'''
ErrorLog:

1. A lot of the score files are empty. For some reason scores were not persed. Check those.

2. In some cases, there are undefined characters in the score files and text processing functions aren't working for them. Example: 1990-91 La Liga.
    Error message says: "UnicodeDecodeError: 'charmap' codec can't decode byte 0x81 in position 81: character maps to <undefined>"
    I'm pretty sure its for the special character a in Cadiz. Check.
'''

'''
#Target:
    Want to analyse the results of a Soccer League and to find any circular result.
    For example, if A 3-2 B, B 3-1 C, C 1-0 D, D 2-1 A, then we can say there is  a circle of result in A-B-C-D-A.
    
    A fun project, probably no real significance.
'''

'''
Steps:
1. Fetch a page from internet containing the results.
2. Extract the results using BeautifulSoup and save as a text.
3. Load the scores in a suitable data type.
4. Finally, run the algo to find cycles. I haven't thought deeply yet, but I think we need some greedy algorithm, and backtracking. Definitely thinking recursion.
'''

from urllib.request import urlopen, urlretrieve
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
import operator
import os
from os import listdir
from os.path import isfile, join
import sys

URL = "http://www.bbc.com/sport/football/premier-league/results"


folderForScores = "AllMatchScores"

# Global. Bad design probably. Forget it for now. KISS.
teams = []
teamWins = {}
winList = {}
total = 0
matchResults = []
result = []
allResults = []

def initializeGlobals():
    global teams, teamWins, winList, total, matchResults, result
    teams = []
    teamWins = {}
    winList = {}
    total = 0
    matchResults = []
    result = []   
    allResults = []

def FetchPage(url):
    #print("Hello World!")
    #get to the url and fetch the page
    try:
        urlretrieve(url,"page.html")
        '''
        I was using urlopen(), reading the data as text, and saving it to a local "page.html" file.
        However, that changed some of the strings in the data (like class="score" to class="\'score\'" which was messing with
        BeautifulSoup find_all method.
        So alternatively, I'm using urlretrieve() to fetch and save the url contents locally in one single step.
        And now it's working perfect.
        '''
    except HTTPError as e:
        print("Error. Reason: ",e.reason)
        print("quitting ...")
        quit()
    except URLError as e:
        print("Error. Reason: ",e.reason)
        print("quitting ...")
        quit()
    else:
        pass    
    
#was needed in the initial prototype. Not needed anymore.
def extractMatchResults(fileName):
    #open file and read
    fp = open(fileName, "r")
    allText = fp.read()
    fp.close()
    
    #now extract home team, away team, and match result.
    '''
    A sample match segment looks like this:
    
    <td class="match-details">
            <p>
                <span class="team-home teams">
                                        <a href="/sport/football/teams/west-ham-united">West Ham</a>                </span>
                  <span class="score"> <abbr title="Score"> 1-1 </abbr> </span>                  
                  <span class="team-away teams">
                    <a href="/sport/football/teams/everton">Everton</a>                </span>
                                            </p>
        </td>

    So we'll need:
        1. Extract "match-details" class
        2. Within each of them, extract three span classes named "team-home teams", "score", "team-away teams"
        3. For each of them, getting the text would work nicely 
     
    Soup. We need Beautiful Soup! 
    '''
    
    soup = BeautifulSoup(allText,"lxml")
    
    #look for match-details
    matchDetails = soup.findAll("td",class_= "match-details") 
    #print("len:",len(matchDetails))
    
    outputFileName = fileName[:fileName.find(".")] + ".txt"
    f2 = open(outputFileName,"w")
    for idx,element in enumerate(matchDetails):
        span1 = element.find("span",class_="team-home")
        home = span1.text.strip()
        
        span2 = element.find("span",class_="score")
        score = span2.text.strip()
        a,b = splitScore(score)
        homeScore = int(a)
        awayScore = int(b)
        #print("home:",homeScore)
        #print("away:",awayScore)
        
        span3 = element.find("span",class_="team-away")
        away = span3.text.strip()
        #print(idx, ",", home, ",", score, ",", away, file=f2)
    f2.close()
    
    pass
    
def splitScore(score):
    '''
    input: 1-3
    output: 1,3
    '''
    a = score[:score.find("-")]
    b = score[score.find("-")+1:]
    return a,b
    pass

def processLine(line):

    if(line[0] != "#"):
        elements = line.split(",")
        home = elements[1].strip()
        homeScore = int((elements[2].strip()).split("-")[0])
        awayScore = int((elements[2].strip()).split("-")[1])
        away = elements[3].strip()
        return(home, away, homeScore,awayScore)
    pass

    
def readTable(name):
    global teams
    global teamWins
    global winList
    global total
    global matchResults
    
    #matches = [line.rstrip("\n") for line in open(join(folderForScores,name))]
    matches = [line.rstrip("\n") for line in open(name,encoding="utf8")]
    
    
    for element in matches:
        matchTuple = processLine(element)
        matchResults.append(matchTuple)
        
        if (matchTuple):
            #print(matchTuple)        
            home = matchTuple[0]
            away =  matchTuple[1]
            homeScore = matchTuple[2]
            awayScore = matchTuple[3]
            if (homeScore > awayScore):
                #home wins
                if home in teamWins:
                    teamWins[home] += 1
                    winList[home].append(away)    
                else:
                    teamWins[home] = 1
                    winList[home] = [away]
            elif (awayScore > homeScore):
                #away wins
                if away in teamWins:
                    teamWins[away] += 1
                    winList[away].append(home)
                else:
                    teamWins[away] = 1
                    winList[away] = [home]
            else:
                #draw, do nothing
                pass
    
    teams = list(teamWins.keys())
    teams.sort()
    
    total = len(teams)
    
    #print("teams: ", teams)
    #print("total: ",total)
    #print("end of readTable()")

    pass
    
def lookForChain(left, right):
    # left list, right list 
    
    global result
    
    #check terminating condition
    #print("teams: ",teams)
    #print("total: ",total)
    #print("left: ",left)
    #print("right: ",right)
    if (len(left) == total):
        if (left[0] in winList[left[len(left)-1]]):
            #print("FOUND")
            # save the result
            result.extend(left)
            
            return True
        else:
            return False

    #check initial case
    if len(left) == 0:
        #select the team that has least number of wins
        current = sorted(teamWins.items(),key=operator.itemgetter(1))[0][0]
        left.append(current)
        right.remove(current)
    else:    
        #select the last item of left as current
        current =  left[len(left)-1]
    
    #make eligible list
    eligible = [x for x in right if x in winList[current]]
    
    if (len(eligible) == 0):
        return False
    
    #sort eligible list in terms of win number
    sortedEligible = [x[0] for x in sorted([(k,teamWins[k]) for k in eligible],key=operator.itemgetter(1))]
    
    #for each element in sortedEligible, call recursive function    
    for element in sortedEligible:
        left.append(element)
        right.remove(element)
        if lookForChain(left,right) is True:
            return True
        left.remove(element)
        right.append(element)
        
    return False    

def lookForAllChains(left, right):
    # left list, right list 
    
    global result
    global allResults
    
    #check terminating condition
    #print("teams: ",teams)
    #print("total: ",total)
    #print("left: ",left)
    #print("right: ",right)
    if (len(left) == total):
        if (left[0] in winList[left[len(left)-1]]):
            print("FOUND")
            print(left)
            # save the result in a global list and continue
            #result.extend(left)
            allResults.append(left[:])
            
        else:
            return

    #check initial case
    if len(left) == 0:
        #select the team that has least number of wins
        current = sorted(teamWins.items(),key=operator.itemgetter(1))[0][0]
        left.append(current)
        right.remove(current)
    else:    
        #select the last item of left as current
        current =  left[len(left)-1]
    
    #make eligible list
    eligible = [x for x in right if x in winList[current]]
    
    if (len(eligible) == 0):
        return
    
    #sort eligible list in terms of win number
    sortedEligible = [x[0] for x in sorted([(k,teamWins[k]) for k in eligible],key=operator.itemgetter(1))]
    
    #for each element in sortedEligible, call recursive function    
    for element in sortedEligible:
        left.append(element)
        right.remove(element)
        
        lookForAllChains(left,right)
        
        left.remove(element)
        right.append(element)
        
    return

    
def printFormattedResult(fp):
    #This function will only be called if a result is already been found and is saved in result[]
    resString = ""
    
    for i in range(total):  #total teams
        first = result[i]
        second = result[(i+1)%total]
        
        for match in matchResults:
            if((match[0] == first) and (match[1] == second) and (match[2] > match[3])):
                #print(first, match[2], "-", match[3], end=" ")
                resString = resString + "{} {} - {} ".format(first, match[2],match[3])
                break
            if((match[0] == second) and (match[1] == first) and (match[3] > match[2])):
                #print(first, match[3], "-", match[2], end=" ")
                resString = resString + "{} {} - {} ".format(first, match[3],match[2])
                break    
    resString += second
    #print(resString)
    fp.write(resString + "\n")
    
    pass
    
def findChainForEachLeague():
    fp = open("results.txt","w",encoding="utf8")
    
    names = [name for name in os.listdir(folderForScores) if name[0] != '0']
    #names = ["1990_91 La Liga.txt"]
    #names = ["test.txt"]
        
    for idx,name in enumerate(names):
        fullName = join(folderForScores,name)
        #print()
        print(idx,",",name)
        if name == "2003_04 FA Premier League.txt":
            continue
        if name == "2011_12 Serie A.txt":
            continue
        fp.write("\n" + str(idx) + "," + name + "\n")
        #print(fullName)
        
        #if the file is empty, skip
        if os.path.getsize(fullName) == 0:
            #print("Empty file!")
            fp.write("Empty file!\n")
            continue
        
        initializeGlobals()
        readTable(fullName)
        
        left = []
        right = teams[:] 
        if lookForChain(left, right) is True:
            #print("And the result is:", result)
            printFormattedResult(fp)
        else:
            #print("No cycles found!")
            fp.write("No cycles found!\n")
    
    fp.close()
    pass
    
def findAllChainsForALeague(name):
    fullName = join(folderForScores,name)
    print(fullName)
    
    initializeGlobals()
    readTable(fullName)
    
    left = []
    right = teams[:] 
    
    lookForAllChains(left,right)
    
    #print(allResults)
    print("total chain found: ", len(allResults))
    for idx, chain in enumerate(allResults):
        print("chain: ",idx, " : ", chain)
    
    pass


print("Hello World!")

#to redirect input to a file, just for testing

#fp = open("result.txt","w",encoding="utf8")
#sys.stdout = fp

findChainForEachLeague()

#fp.close()

#findAllChainsForALeague("2015_16 Premier League.txt")


#TODO
'''
1. Go through every file in AllMatchScores folder (except 0_scoresNotFound.txt)
2. For every file, need to call readTable() and lookForChain()
    2.1 Now here is the catch. We are using globals to pass values between these functions, and recursion:
                global teams
                global teamWins
                global winList
                global total
                global matchResults
    2.2 So need to write an initializer that'll reset these variables for each input file.
    
3. Also need to decide how to show the results.     
    3.1 For each season: we are showing the chain at first, then the results. Right now it is like this:
                FOUND
                And the result is: ['LEV', 'RVA', 'GRA', 'GET', 'LPA', 'RSO', 'EIB', 'SPG', 'DEP', 'RBS', 'MLG', 'CEL', 'VIL', 'ATM', 'SEV', 'BAR', 'RMA', 'ATH', 'ESP', 'VAL']
                LEV 2 - 1 RVA
                RVA 2 - 1 GRA
                GRA 2 - 1 GET
                GET 4 - 0 LPA
                LPA 2 - 0 RSO
                RSO 2 - 1 EIB
                EIB 2 - 0 SPG
                SPG 3 - 2 DEP
                DEP 2 - 1 RBS
                RBS 1 - 0 MLG
                MLG 2 - 0 CEL
                CEL 2 - 1 VIL
                VIL 1 - 0 ATM
                ATM 3 - 0 SEV
                SEV 2 - 1 BAR
                BAR 4 - 0 RMA
                RMA 2 - 1 ATH
                ATH 2 - 1 ESP
                ESP 1 - 0 VAL
                VAL 3 - 0 LEV  
    
        We should just put the scores inside the chain to reduce it into one line.
        Also, that'll help us to eliminate home-away display question (right now we are not preserving home-away info.
    
    3.2 League, season, Found/NotFound, (If found) Chain may be an acceptable format. We can open it through excel for further processing.
    
    3.3 Need some graphs. Shouldn't be too hard to generate in Excel (or Matlab)
    
    3.4 Graphs may show league comparisons for the last 5 yers, last 10 years, last 20 years etc.
    
    3.5 Also for each league, we may have a graph showing all seasons, to see if there is any trend.
'''


