# -*- coding: utf-8 -*-


"""
Created on Tue Feb 28 11:44:42 2017

@author: priya.cse2009
"""

"""
pubmed url
To search pubmed you need to use the eSearch API.
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%28%22sleep+apnea+syndromes%22%5BMeSH+Terms%5D+OR+%28%22sleep%22%5BAll+Fields%5D+AND+%22apnea%22%5BAll+Fields%5D+AND+%22syndromes%22%5BAll+Fields%5D%29+OR+%22sleep+apnea+syndromes%22%5BAll+Fields%5D+OR+%28%22sleep%22%5BAll+Fields%5D+AND+%22disordered%22%5BAll+Fields%5D+AND+%22breathing%22%5BAll+Fields%5D%29+OR+%22sleep+disordered+breathing%22%5BAll+Fields%5D%29+AND+%28%22child%22%5BMeSH+Terms%5D+OR+%22child%22%5BAll+Fields%5D+OR+%22children%22%5BAll+Fields%5D%29+AND+%28%22insulin+resistance%22%5BMeSH+Terms%5D+OR+%28%22insulin%22%5BAll+Fields%5D+AND+%22resistance%22%5BAll+Fields%5D%29+OR+%22insulin+resistance%22%5BAll+Fields%5D%29&retmode=txt&retmax=1000

Breaking this down…

http://eutils.ncbi.nlm.nih.gov/entrez/ -->is the entry point for the whole system.
/eutils/esearch.fcgi   -->is the actual function that you will be using…This tells the API that you want to search pubmed.
db=pubmed
term= %28%22sleep+apnea+syndromes%22%5BMeSH+Terms%5D+OR+%28%22sleep%22%5BAll+Fields%5D+AND+%22apnea%22%5BAll+Fields%5D+AND+%22syndromes%22%5BAll+Fields%5D%29+OR+%22sleep+apnea+syndromes%22%5BAll+Fields%5D+OR+%28%22sleep%22%5BAll+Fields%5D+AND+%22disordered%22%5BAll+Fields%5D+AND+%22breathing%22%5BAll+Fields%5D%29+OR+%22sleep+disordered+breathing%22%5BAll+Fields%5D%29+AND+%28%22child%22%5BMeSH+Terms%5D+OR+%22child%22%5BAll+Fields%5D+OR+%22children%22%5BAll+Fields%5D%29+AND+%28%22insulin+resistance%22%5BMeSH+Terms%5D+OR+%28%22insulin%22%5BAll+Fields%5D+AND+%22resistance%22%5BAll+Fields%5D%29+OR+%22insulin+resistance%22%5BAll+Fields%5D%29

The simplest way to understand the very advanced search functionality on pubmed is to use the PubMed advanced query builder 
or you can do a simple search, and then pay close attention to the box labeled “search details” on the right sidebar.

("sleep apnea syndromes"[MeSH Terms] 
OR ("sleep"[All Fields] 
AND "apnea"[All Fields] 
AND "syndromes"[All Fields]) 
OR "sleep apnea syndromes"[All Fields] 
OR ("sleep"[All Fields] 
AND "disordered"[All Fields] 
AND "breathing"[All Fields]) 
OR "sleep disordered breathing"[All Fields]) 
AND ("child"[MeSH Terms] 
OR "child"[All Fields] 
OR "children"[All Fields]) 
AND ("insulin resistance"[MeSH Terms] 
OR ("insulin"[All Fields] 
AND "resistance"[All Fields]) 
OR "insulin resistance"[All Fields])

PubMed is using MesH terms to map my search to what I “really wanted”.
MesH stands for “Medical Subject Headings” is an ontology built specifically to make this task easier.
Use a handy URL encoder to get the term

retmod=txt  -->Next you want to set the “return mode” so that TXT is returned.

retmax=1000
"""

import re
from itertools import combinations
from collections import Counter
import requests
import time
from geotext import GeoText
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

tree = ET.parse('C:\\Users\\priya.cse2009\\priya\\Analytics in a World of Big Data\\Case2\\pubmed_id.xml')     
root = tree.getroot()
ids = root.findall("./IdList/Id")

#Create a file 'edges.csv'
filename = 'C:\\Users\\priya.cse2009\\priya\\Analytics in a World of Big Data\\Case2\\edges.csv'
myFile = open(filename, 'w+')

#Create a file 'location.csv'
filename2 = 'C:\\Users\\priya.cse2009\\priya\\Analytics in a World of Big Data\\Case2\\location.csv'
myFile2 = open(filename2, 'w+')

final_location = []

for i in ids:
    
    url = 'https://www.ncbi.nlm.nih.gov/pubmed/'+i.text
    #print i.text
    #print url
    for i in range(5): # try 5 times
	try:
		#use the browser to access the url
		response=requests.get(url,headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36', })
		html=response.content # get the html
		break # we got the file, break the loop
	except Exception as e:# browser.open() threw an exception, the attempt to get the response failed
		print 'failed attempt',i
		time.sleep(2) # wait 2 secs
				
    if  html:
        #print 'success'
        author_list = []
        soup = BeautifulSoup(html) # parse the html 
        authors = soup.findAll('div', {'class':re.compile('auths')}) # get all the author divs
        afflist = soup.findAll('div', {'class':re.compile('afflist')})
        print len(afflist)
        
        for a in afflist:
            location = []
            locList = a.findAll('li')
            for l in locList:
                places = GeoText(l.text.encode('ascii','ignore'))
                location.append(places.cities)
                final_location.append(places.cities)
            location_list = [l for loc in location for l in loc]
            location_set = set(location_list)
            for i in location_set:
                #print i
                myFile2.write(i+"\n")
            #print location_set
                
                
        for a in authors:
            text = a.text.encode('ascii','ignore')
            results = text.strip().upper().split(",")
            #print results
            for item in results:
                item = re.sub('[.;]+', '', item).strip()
                author_list.append(item)
            #print author_list
            for i in combinations(author_list, 2):
                myFile.write("%s,%s\n" % i)
        
    else:continue
myFile.close()
myFile2.close()


print "----------------------------"

final_location_list = [i for f in final_location for i in f]
counts = Counter(final_location_list)
print(counts)

final_location_set = set(final_location_list)
print len(final_location_list)

# Draw the locations of cities on a map of the US

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from geopy.geocoders import Nominatim
import math

geolocator = Nominatim()
scale = 2

map = Basemap()
map.drawcoastlines()

for i in counts.iteritems():
        loc = geolocator.geocode(i[0],timeout = 10)
        x, y = map(loc.longitude, loc.latitude)
        map.plot(x,y,marker='o',color='Red',markersize=int(math.sqrt(i[1]))*scale)
plt.show()
        
    

"""
#Create a file 'nodes.csv'
nodes = set()
source = 'C:\\Users\\priya.cse2009\\priya\\Analytics in a World of Big Data\\Case2\\edges.csv'
dest = 'C:\\Users\\priya.cse2009\\priya\\Analytics in a World of Big Data\\Case2\\nodes.csv'
myFile1 = open(source, 'r')
myFile2 = open(dest,'w+')

for line in myFile1:
    results = line.strip().split(",")
    for r in results:
        nodes.add(r)
        
        
nodes = sorted(nodes)

print len(nodes)

i=1
for n in nodes:
    print n+","+str(i)
    myFile2.write(n+","+str(i)+"\n")
    i+=1
    
myFile1.close()
myFile2.close()

"""