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
import shutil

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
    #print("score: ",score)
    textScore = ""
    
    if "\u2013" in score:
        textScore = score.replace(u"\u2013","*") #the unicode dash is a problem, vanish it
    if "-" in score:
        textScore = score.replace("-","*")
    
    if textScore == "":
        return -1,-1
    
    textScore = textScore.strip()
    a = textScore[:textScore.find("*")]
    b = textScore[textScore.find("*")+1:]
    return a,b
    
        
def extractMatchResults(fileName):
    print("processing: ", fileName)
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
    
    searchStrings = ["Result_table","Results_table","Results","Scoresheet"]
    
    for searchString in searchStrings:
        span = soup.find("span", {"id" : searchString, "class" : "mw-headline"})
        if span is not None:
            print("searchString matched: ", searchString)
            break
    
    #no searchString matched. Either it has a span id that we didn't cover, 
    #or it may not have match-by-match scores. 
    if span is None:    
        print("Span not found for: ",fileName)
        fp3.write(fileName + "\n")
        return
        
    h2 = span.parent
    for sibling in h2.next_siblings:
        if(sibling.name == "table"):
            table = sibling
            break
    
    if table is None:    
        print("Table not found for: ",fileName)
        fp3.write(fileName + "\n")
        return
    
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
        

        
#After the initial pass, some seasons are still unprocessed. Will identify those files and put them into a separate folder. Will write a separate function to go over them and extract results.        
def separateSeasonsYetToProcess():
    os.makedirs(folderForSeasons + "/" + "StillUnprocessed", exist_ok = True)
    
    for filename in os.listdir(folderForScores):
        if os.path.getsize(os.path.join(folderForScores,filename)) == 0:
            source = os.path.join(folderForSeasons,filename[:filename.find(".")] + ".html")
            dest = os.path.join(folderForSeasons,"StillUnprocessed",filename[:filename.find(".")] + ".html")
            print(filename)
            shutil.copy2(source,dest)
    
    pass

'''
Earlier version of extractMatchResults() (defined above) failed to extract results for some files. Instead of messing around with that code, writing this new version which will only work on those left-out seasons. 
'''    
def extractMatchResultsVersion2(filename):
    #probably hardcoding will do just fine. In most of the cases, the second table in the document is the Results Table.
    #But because I loathe hardcoding, let's try another way. The idea is, the Results Table will always (supposed to) have same number of rows and columns. So let's write a function that checks this property for each table in the document.
    
    fullname = os.path.join(folderForSeasons,"StillUnprocessed",filename)
    fp = open(fullname, encoding="utf8")
    allText = fp.read()
    fp.close()
    
    os.makedirs(os.path.join(folderForScores,"StillUnprocessed"), exist_ok = True)
    
    soup = BeautifulSoup(allText,"lxml")
    
    tables = soup.find_all(isItASquareTable)
    
    
    if tables is not None and len(tables) == 1:
        table = tables[0]
        print(table)
        #process the table
        flag,shortNames, fullNames, results = extractScoreFromHtmlTable(table)
        if flag is False:
            return False
        
        #write the result file
        outname = os.path.join(folderForScores, "StillUnprocessed",filename[:filename.find(".")] + ".txt")
        fp2 = open(outname, "w", encoding="utf-8")
        
        for result in results:
            fp2.write(result + "\n")
            
        fp2.write("shortNames:" + "," + ",".join(shortNames) + "\n")
        fp2.write("fullNames:" + "," + ",".join(fullNames) + "\n")
        
        fp2.close()
            
    else:
        tables = soup.find_all(isItASquareTableV2)
        
        if len(tables) == 0:
            return False
        
        table = tables[0]
        
        #process the table
        flag, shortNames, fullNames, results = extractScoreFromHtmlTable(table)
        if flag is False:
            return False
        
        #write the result file
        outname = os.path.join(folderForScores, "StillUnprocessed",filename[:filename.find(".")] + ".txt")
        fp2 = open(outname, "w", encoding="utf-8")
        
        for result in results:
            fp2.write(result + "\n")
            
        fp2.write("shortNames:" + "," + ",".join(shortNames) + "\n")
        fp2.write("fullNames:" + "," + ",".join(fullNames) + "\n")
        
        fp2.close()
        
        if len(tables) == 2:    #in only one case, we found two result tables
            table = tables[1]
        
            #process the table
            flag,shortNames, fullNames, results = extractScoreFromHtmlTable(table)
            if flag is False:
                return False
        
            #write the result file
            outname = os.path.join(folderForScores, "StillUnprocessed",filename[:filename.find(".")] + ".txt")
            fp2 = open(outname, "a", encoding="utf-8")
            
            for result in results:
                fp2.write(result + "\n")
                
            fp2.write("shortNames:" + "," + ",".join(shortNames) + "\n")
            fp2.write("fullNames:" + "," + ",".join(fullNames) + "\n")
            
            fp2.close()
            
            
        
    return True
    pass

'''
extractMatchResultsVersion2() is cleaner and more manageable than extractMatchResults(). And I want to change the score file pattern we generated earlier. So instead of modifying extractMatchResults(), I'm creating a slightly modified version of extractMatchResultsVersion2() to handle those html files. The change is basically just with input and output destinations. 
'''
def extractMatchResultsVersion2_1(filename):
    #probably hardcoding will do just fine. In most of the cases, the second table in the document is the Results Table.
    #But because I loathe hardcoding, let's try another way. The idea is, the Results Table will always (supposed to) have same number of rows and columns. So let's write a function that checks this property for each table in the document.
    
    fullname = os.path.join(folderForSeasons,filename)
    fp = open(fullname, encoding="utf8")
    allText = fp.read()
    fp.close()
    
    os.makedirs(folderForScores, exist_ok = True)
    
    soup = BeautifulSoup(allText,"lxml")
    
    tables = soup.find_all(isItASquareTable)
    
    
    if tables is not None and len(tables) == 1:
        table = tables[0]
        #print(table)
        #process the table
        flag,shortNames, fullNames, results = extractScoreFromHtmlTable(table)
        if flag is False:
            return False
        
        #write the result file
        outname = os.path.join(folderForScores, "SecondPass",filename[:filename.find(".")] + ".txt")
        fp2 = open(outname, "w", encoding="utf-8")
        
        for result in results:
            fp2.write(result + "\n")
            
        fp2.write("shortNames:" + "," + ",".join(shortNames) + "\n")
        fp2.write("fullNames:" + "," + ",".join(fullNames) + "\n")
        
        fp2.close()
            
    else:
        tables = soup.find_all(isItASquareTableV2)
        
        if len(tables) == 0:
            return False
        
        table = tables[0]
        
        #process the table
        flag, shortNames, fullNames, results = extractScoreFromHtmlTable(table)
        if flag is False:
            return False
            
        #write the result file
        outname = os.path.join(folderForScores, "SecondPass",filename[:filename.find(".")] + ".txt")
        fp2 = open(outname, "w", encoding="utf-8")
        
        for result in results:
            fp2.write(result + "\n")
            
        fp2.write("shortNames:" + "," + ",".join(shortNames) + "\n")
        fp2.write("fullNames:" + "," + ",".join(fullNames) + "\n")
        
        fp2.close()
        
        if len(tables) == 2:    #in only one case, we found two result tables
            table = tables[1]
        
            #process the table
            flag, shortNames, fullNames, results = extractScoreFromHtmlTable(table)
            if flag is False:
                return False
                
            #write the result file
            outname = os.path.join(folderForScores, "SecondPass",filename[:filename.find(".")] + ".txt")
            fp2 = open(outname, "a", encoding="utf-8")
            
            for result in results:
                fp2.write(result + "\n")
                
            fp2.write("shortNames:" + "," + ",".join(shortNames) + "\n")
            fp2.write("fullNames:" + "," + ",".join(fullNames) + "\n")
            
            fp2.close()
            
            
        
    return True
    pass

    
def isItASquareTable(table):
    if table.name != "table":
        return False
    
    if table.has_attr("class") and "wikitable" in table["class"]:
        rows = table.find_all("tr")
        rowCount = len(rows)
        
        columnCount = 0
        if(rowCount > 1):
            columns = rows[1].find_all("td")
            columnCount = len(columns)
        
        if (rowCount == columnCount):
            return True
    
    return False
    
def isItASquareTableV2(table):
    #more generic version. For some .html files, the Results table does not have "wikitable" class tag. So instead of filtering with that, checking all the tables.
    
    if table.name != "table":
        return False
    
    rows = table.find_all("tr")
    rowCount = len(rows)
    
    columnCount = 0
    if(rowCount > 1):
        columns = rows[1].find_all("td")
        columnCount = len(columns)
    
    if (rowCount == columnCount):
        return True

    return False

    
def extractScoreFromHtmlTable(table):
    shortNames = [""]
    fullNames = [""] #the header row is empty, so giving a filler text. Makes indexing easier later.
    results = []
    
    #first just extract the team names
    for idx, row in enumerate(table.find_all("tr")):
        #if it's the first row, then it is the header
        if idx == 0:
            headerRow = row.find_all("th")
            if len(headerRow) == 0:
                headerRow = row.find_all("td")
            
            for count,data in enumerate(headerRow):
                #print(data.text.strip())
                shortNames.append(data.text.strip())
        else:
            #just get the first element in the row, that should be the team name
            data = row.find("td")
            name = data.text.strip()
            
            if '!' in name:
                name = name[name.find('!')+1:]
            
            if len(name) != 0:
                fullNames.append(name)
                #print(name)
        
    #now extract the results
    counter = 0
    for idx, row in enumerate(table.find_all("tr")):
        if idx == 0:
            continue    #header row, ignore    
            
        for count,data in enumerate(row.find_all("td")):
            if data.find("sup") is not None:
                result =  str(counter) + " , " + fullNames[idx] + " , " + "??" + "-" + "??" + " , " + fullNames[count]
                counter += 1
                results.append(result)
            else:
                nameOrScore = data.text.strip()
                if len(nameOrScore) == 0:
                    pass
                elif(nameOrScore[0].isalpha()):
                    pass
                elif(nameOrScore[0].isdigit()):
                    scoreA, scoreB = processScore(nameOrScore)
                    if scoreA == -1:
                        return False,shortNames,fullNames,results
                    result =  str(counter) + " , " + fullNames[idx] + " , " + str(scoreA) + "-" + str(scoreB) + " , " + fullNames[count]
                    counter += 1
                    results.append(result)
                    
    return True,shortNames,fullNames,results
       
def processTheStillUnprocessedFiles():
    
    folderName = folderForSeasons + "/" + "StillUnprocessed"

    fp3 = open(os.path.join(folderForSeasons,"StillUnprocessed","yetUnprocesseds.txt"),"w")
    
    for filename in os.listdir(folderName):
        if filename == "1979_80 La Liga.html":  #has issues. Handle separately.
            fp3.write(filename + "\n")
            continue
            
        if ".html" in filename:
            print(filename)
            
            if extractMatchResultsVersion2(filename) is False:
                fp3.write(filename + "\n")
    
    fp3.close()
    
    pass
    
def processTheStillUnprocessedFilesV2():
    fp = open(os.path.join(folderForSeasons,"StillUnprocessed","yetUnprocesseds.txt"),"r")
    
    for line in fp:
        filename = line.strip()
        print(filename)
        
        if filename == "1979_80 La Liga.html":  #has issues. Handle separately.
            continue
        
        extractMatchResultsVersion2(filename)
       
def extractScoresForSeasonPass2():
    allFiles = [f for f in listdir(folderForSeasons) if isfile(join(folderForSeasons,f))]
    
    fp = open(os.path.join(folderForScores,"SecondPass","0_scoresNotFound.txt"),"w")
    
    for fileName in allFiles:
        if fileName == "1929 La Liga.html":
            continue
        if ".html" in fileName:
            print(fileName)
            if extractMatchResultsVersion2_1(fileName) is False:
                print("Not Found: ", fileName)
                fp.write(fileName + "\n")
    fp.close()
                
print("Hello World")

fetchPage("https://en.wikipedia.org/wiki/2015%E2%80%9316_Bundesliga","2015_16 Bundesliga")
fetchPage("https://en.wikipedia.org/wiki/2015%E2%80%9316_Premier_League","2015_16 Premier League")
fetchPage("https://en.wikipedia.org/wiki/2015%E2%80%9316_La_Liga","2015_16 La Liga")
fetchPage("https://en.wikipedia.org/wiki/2015%E2%80%9316_Ligue_1","2015_16 Ligue 1")
fetchPage("https://en.wikipedia.org/wiki/2015%E2%80%9316_Serie_A","2015_16 Serie A")


extractScoresForSeasonPass2() 


#processTheStillUnprocessedFilesV2()

#extractScoresForSeason()

#name = "2015_16 Premier League"
#extractMatchResults(name)