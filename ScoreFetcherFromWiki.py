'''
Target:
    We already wrote some code to find out a cyclic chain of events from a list of soccer match results.
    Now that we have the code, why don't we run it on every league's results and see how it goes?
    So, we need to fetch the match results for  each league.

    For uniformity, the best place to fetch from is wikipedia.
    
    This code will fetch the wiki page for a league. The results are usually in a tabular format.

    It will extract the match results from the table and store in a text file in this format:
        0 , Crystal Palace , 0-1 , Sunderland
        1 , Tottenham , 4-1 , West Ham
        2 , Watford , 1-2 , Man Utd
        
    Our existing code can already process it from this point, so voila.
'''

from urllib.request import urlretrieve
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
import operator
import os
from os import listdir
from os.path import isfile, join
import re

#URL = "https://en.wikipedia.org/wiki/2013%E2%80%9314_La_Liga"
#fileName = "LaLiga2013_14"

folderForLeagues = "AllLeagues"
folderForSeasons = "AllSeasons"
folderForScores = "AllMatchScores"

def fetchPage(url,name):
    os.makedirs(folderForSeasons, exist_ok = True)
    fullName = folderForSeasons + "/" + name + ".html"
    try:
        urlretrieve(url, fullName)
    except HTTPError as e:
        print("Error. Reason: ",e.reason)
        print("Quitting ...")
        quit()
    except HTTPError as e:
        print("Error. Reason: ",e.reason)
        print("Quitting ...")
        quit()
    else:
        pass

def processScore(score):
    '''
    input: 1-3
    output: 1,3
    '''
    textScore = score.replace(u"\u2013","*") #the unicode dash is a problem, vanish it
    textScore = textScore.strip()
    a = textScore[:textScore.find("*")]
    b = textScore[textScore.find("*")+1:]
    
    return a,b
    
        
def extractMatchResults(fileName):
    #open file and read
    fp = open(folderForSeasons + "/" + fileName + ".html", encoding="utf8")
    allText = fp.read()
    fp.close()
    
    fp3 = open(folderForScores + "/" + "0_scoresNotFound" + ".txt","a")
    
    #now locate the table and extract data
    '''
    The table starts like this:
    <h2><span class="mw-headline" id="Results">Results</span><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=2013%E2%80%9314_La_Liga&amp;action=edit&amp;section=9" title="Edit section: Results">edit</a><span class="mw-editsection-bracket">]</span></span></h2>
    <table class="wikitable" style="font-size: 85%; text-align: center;">
    '''
    
    #So basically, we need to identify the header with a span class = "mw-headline" and id = "Results".
    #The table that starts immediately afterwards is the table we are looking for.
    #The table itself does not have a unique identifier, which could be a problem.
    
    #probable solution: traverse the BeautifulSoup parse tree. Locate the span class with name and id.
    #Then grab its parent (h2), and then get the nextSibling of the h2 tag to get the table.
    #There may be some newline objects returned by nextSibling, check those and ignore and keep fetching till the Table tag is found.
    
    soup = BeautifulSoup(allText,"lxml")
    
    searchStrings = ["Results","Scoresheet","Result_table","Results_table"]
    
    for searchString in searchStrings:
        span = soup.find("span", {"id" : searchString, "class" : "mw-headline"})
        if span is not None:
            break
    
    #no searchString matched. Either it has a span id that we didn't cover, 
    #or it may not have match-by-match scores. 
    if span is None:    
        print(fileName)
        fp3.write(fileName + "\n")
        return
        
    #print(span)
    h2 = span.parent
    for sibling in h2.next_siblings:
        if(sibling.name == "table"):
            table = sibling
            break
    
    nameOfTeams = [""] #keeping an initial blank element to help with indexing in future
    matchCounter = 0
    
    os.makedirs(folderForScores, exist_ok = True)
    fp2 = open(folderForScores + "/" + fileName + ".txt","w", encoding='utf-8')
    for idx, row in enumerate(table.find_all("tr")):
        #fp2.write(str(idx) + ":\n")
        for count,data in enumerate(row.find_all("td")):
            #ignore the first data. Either team name, or some other unimportant text
            if (count == 0):
                #fp2.write("SKIPPED\n")
                continue
            
            #check if it's a team-name. Look for the span class "sorttext"
            name = data.find(class_="sorttext")
            if(name):
                link = name.find("a")
                if(link):
                    #fp2.write(repr(link.text) + "\n")
                    nameOfTeams.append(link.text.strip())
                else:    
                    #fp2.write("BLANK\n")
                    pass
            
            #else, check if it's a score. Look for span class "nowrap"
            else:
                score = data.find(class_="nowrap")
                if(score):
                    scoreA, scoreB = processScore(score.text)
                    fp2.write(str(matchCounter) + " , " + nameOfTeams[idx]  + " , " + scoreA + "-" + scoreB +  " , " + nameOfTeams[count] + "\n")
                    matchCounter += 1
                    
                else:
                    #fp2.write("BLANK\n")
                    pass
        #fp2.write("\n")
        pass
    
    fp2.close()
    fp3.close()
    #print(nameOfTeams)
    
    pass
        
#Go to the desired folder ("AllLeagues")
#Open each file with name with the pattern "*_season_links.txt"
#Within each file:
    # read <url,name> info in each file
    # call fetchPage(url,name) to fetch it. Make sure to save it to a specific folder ("AllSeasons")
def fetchAllSeasonsPages():
    pattern = r'[\w]+_season_links.txt'
    p = re.compile(pattern)
    allFiles = [f for f in listdir(folderForLeagues) if isfile(join(folderForLeagues,f)) and p.match(f)]
    for fileName in allFiles:
        print("-------------------------------->", fileName)
        fp = open(join(folderForLeagues,fileName),"r",encoding = "utf8")
        for line in fp:
            url = line[:line.find(",")]
            name = line[line.find(",")+1:].strip()
            print(url," | ", name)
            fetchPage(url,name)
            #extract score here. Careful aboutFrench Leage. Everything else should be okay.  
        fp.close()            
        

#Go to the desired folder ("AllSeasons")
#For each filename under this folder: 
    # call extractMatchResults(filename)  
        # extractMatchResults() will take care of saving the score file
  
def extractScoresForSeason():
    allFiles = [f for f in listdir(folderForSeasons) if isfile(join(folderForSeasons,f))]
    for fileName in allFiles:
        extractMatchResults(fileName[:fileName.find(".")])

print("Hello World")
extractScoresForSeason()