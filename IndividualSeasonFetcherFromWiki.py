'''
Basically another web scrapper.

- Go through a text file, read each line, get the name and link of the webpage.
    - Fetch that page, identify individual seasons and grab their links.
    - save the seasons' names and links on a text file.
    
- Do it for every line in the original text file.

- Additional task: save the output text files in a specific folder. If the folder does not exist, create it.   
'''

import os
from urllib.request import urlretrieve
from urllib.error import HTTPError,URLError
from bs4 import BeautifulSoup
import re

folderName = "AllLeagues"
pretext = r"https://en.wikipedia.org"


NameUrlKeyword = [
    ("LaLiga","https://en.wikipedia.org/wiki/Category:La_Liga_seasons","La Liga"),
    ("SerieA","https://en.wikipedia.org/wiki/Category:Serie_A_seasons","Serie A"),
    ("Bundesliga","https://en.wikipedia.org/wiki/Category:Bundesliga_seasons","Bundesliga"),
    ("FrenchDivision1","https://en.wikipedia.org/wiki/Category:Ligue_1_seasons","French Division 1"),
    ("Ligue1","https://en.wikipedia.org/wiki/Category:Ligue_1_seasons","Ligue 1"),
    ("EPL","https://en.wikipedia.org/wiki/List_of_Premier_League_seasons","")
]

'''
NameUrlKeyword = [
    ("EPL","https://en.wikipedia.org/wiki/List_of_Premier_League_seasons","")
]
'''

 
def fetchPage(name, url):
    fullname = folderName + "/" + name + ".html"
    os.makedirs(os.path.dirname(fullname), exist_ok = True)
    
    try:
        urlretrieve(url, fullname)
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

'''
    All the links for La-Liga are of this format:
    
    <li><a href="/wiki/2014%E2%80%9315_La_Liga" title="2014–15 La Liga">2014–15 La Liga</a></li>
    
    After replacing the unicode dash and prettifying:
            <li>
                <a href="/wiki/2005%E2%80%9306_La_Liga" title="2005*06 La Liga">
                2005*06 La Liga
                </a>
            </li>
    
    I guess regex can be useful in this.
    A pattern of <li><a href="anything" title="anything">anything</a></li> should do.
    
    Update: Not really. Regex is a bad idea. Regex is greedy, and that messes up html parsing.
    Forcing it to be non-greedy makes the whole pattern very complicated. 
    
    Back to BeautifulSoup.
    Just look for <a> with href and title elements. 
    Then use regex inside it to narrow down the results.
    
'''
    
        
def extractLinks(name,keyword):
    #open saved html file and read
            
    fullname = folderName + "/" + name + ".html"
    fp = open(fullname, "r", encoding="utf8")
    allText = fp.read()
    allText = allText.replace(u"\u2013","_") #the unicode dash is a problem, vanish it
    fp.close()
    
    fullname2 = folderName + "/" + name + "_season_links.txt"
    os.makedirs(os.path.dirname(fullname2), exist_ok = True)    
    fp2 = open(fullname2, "w", encoding='utf8')
        
    
    soup = BeautifulSoup(allText,"lxml")
    
    #EPL needs to be handled specially. You know, the so-called "best" league in the world.
    if name == "EPL":
        # Find all <th> tags.
        # Our desired tags have this format:
            #<th scope="row"><a href="/wiki/2014%E2%80%9315_Premier_League" title="2014_15 Premier League">2014_15</a></th>
        #or,
            #<th scope="row"><a href="/wiki/1993%E2%80%9394_FA_Premier_League" title="1993_94 FA Premier League">1993_94</a></th>
        tableHeaders = soup.find_all("th")
        for element in tableHeaders:
            #print(element)
            link = element.find("a")
            if link is not None:
                #print("Link: -> ",link)
                pattern = r'[0-9_]+[\s\w]+Premier League'
                p = re.compile(pattern)
                if link.has_attr("title") and p.match(link["title"]):
                    print(link["href"],",",link["title"])
                    fp2.write(pretext + link["href"] + "," + link["title"] + "\n")
    
    else:
        pattern = r'[0-9_]+\s+' + keyword
        p = re.compile(pattern)
        hyperLinks = soup.find_all("a")
        for element in hyperLinks:
            if element.has_attr("href") and element.has_attr("title"):
                #now need regex to find out if the title looks something like "2014_15 La Liga"
                if p.match(element["title"]):
                    print(element["href"],",",element["title"])
                    fp2.write(pretext + element["href"] + "," + element["title"] + "\n")
        
    fp2.close()
    pass
 
for tup in NameUrlKeyword:
    fetchPage(tup[0],tup[1])
    extractLinks(tup[0],tup[2])
    
print("Hello World.")    