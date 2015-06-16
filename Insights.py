import re
import Analyze
import Grapher
import math
import csv
import numpy
import matplotlib.pyplot as pyp
from heapq import heappush, heappop, heapify
import nltk
import scipy

def pltCitCollab(filename):
####read data from csv file, plot the collaboration-citation data
  f1 = open(filename,'r+',encoding='utf-8')
  rawdata = csv.reader(f1)
  count = sum(1 for row in rawdata)
  f1.close()

  print(str(count)+' papers analyzed.')

  f1 = open(filename,'r+',encoding='utf-8')
  rawdata=csv.reader(f1)
  data = Analyze.citacollab(rawdata,count)
  f1.close()

  pyp.plot(data[1],data[0],'ro')
  pyp.xlabel('Citations')
  pyp.ylabel('Number of co-authors')
  pyp.show()
  pyp.close()
  return data

def pltCitClarity(filename):
##read data from csv file, plot the clarity-citations data
  f1 = open(filename,'r+',encoding='utf-8')
  rawdata = csv.reader(f1)
  count = sum(1 for row in rawdata)
  f1.close()

  print(str(count)+' papers analyzed.')
  
  f1 = open(filename,'r+',encoding='utf-8')
  rawdata=csv.reader(f1)
  data = Analyze.citaclarity(rawdata,count)
  f1.close()
  
  pyp.plot(data[0],data[1],'ro')
  pyp.xlabel('Abstract length')
  pyp.ylabel('Citations')
  pyp.show()
  pyp.close()
  return data

def pltCitRate(filename):
##read data from csv file, plot the clarity-citations data
  f1 = open(filename,'r+',encoding='utf-8')
  rawdata=csv.reader(f1)
  authordict = Analyze.dictauthor(rawdata)
  f1.close()

  data = numpy.zeros((2,len(authordict)))
  i=0
  for author in authordict.keys():
      data[0,i] = authordict[author]['NumPapers']
      data[1,i] = authordict[author]['Citations']/authordict[author]['NumPapers']
      i += 1
      
  pyp.plot(data[0],data[1],'ro')
  pyp.xlabel('Number of papers published')
  pyp.ylabel('Average citations per paper')
  pyp.show()
  pyp.close()
  return data

def rank(filename,criterion,num):
#read data and rank authors based on criteria, and output first num authors
  criteria = ['Citations','NumPapers','Co-Authors','Citation Rate']
  if criterion not in criteria:
      print('Error: criterion can only be one of the following strings: Citations/NumPapers/Co-Authors')
      return []
  f1 = open(filename,'r+',encoding='utf-8')
  rawdata=csv.reader(f1)
  authordict = Analyze.dictauthor(rawdata)
  f1.close()

  ranking = []
  for author in authordict.keys():
      if criterion == 'Co-Authors':
          heappush(ranking, [-len(authordict[author][criterion]), author])
      elif criterion == 'Citation Rate':
          heappush(ranking, [-(authordict[author]['Citations']/authordict[author]['NumPapers']), author])
      else:
          heappush(ranking, [-authordict[author][criterion], author])

  bestofcriterion = []
  while len(bestofcriterion)<num:
      pick = heappop(ranking)
      bestofcriterion.append([-pick[0],pick[1]])
  return bestofcriterion

def idauthor(filename,rawlabel):
#read file and find the profs closest match to rawlabel and confirm/return actual label
  f1 = open(filename,'r+',encoding='utf-8')
  rawdata=csv.reader(f1)
  authordict = Analyze.dictauthor(rawdata)
  f1.close()

  return Analyze.idauthor(authordict,rawlabel)

def getauthor(filename,rawlabel):
#read file and find the details of the author
  authordict = getauthordict('authordict.csv')
  author = Analyze.idauthor(authordict,rawlabel)

  return author,authordict[author]
              
def cleanfile(infilename,outfilename):
#read file and find the research keywords of the given author
  f1 = open(infilename,'r+',encoding='utf-8')
  rawdata=csv.reader(f1)
  Analyze.cleanfile(rawdata,outfilename)
  f1.close()

def getauthordict(filename):
#read file and get the authordict
  f1 = open(filename,'r+',encoding='utf-8')
  dictdata = csv.reader(f1)
  authordict={}
  for row in dictdata:
    if row[0] == 'Author':
      continue
    authordict[row[0]] = {'NumPapers':row[1],'Citations':row[2],'Co-Authors':row[3],'Papers':row[4],'Keywords':row[5]}

  return authordict

def suggestauthors(topic,num):
#read file and find the profs closest match to rawlabel and confirm/return actual label
  authordict = getauthordict('authordict.csv')
  ranking = []
  similars = []

  author = Analyze.idauthor(authordict,topic)
  if author == '':
    score=[]
    stops=nltk.corpus.stopwords.words('english') #stopwords to weed out
    stops = stops + ['we',',','.','(',')','using','new','propose','investigate']
    stops = stops + ['-','show','infer','novel','method']

    tokens1 = nltk.word_tokenize(topic)
    pairs1 = nltk.bigrams(tokens1)
    tokens1 = tokens1+[bg for bg in pairs1 if bg[0] not in stops and bg[1] not in stops]
    for auth in authordict.keys():
      keyw2 = authordict[auth]['Keywords']
      tokens2 = list(filter(None,re.split(r',',keyw2)+re.split(r'[ ,]',keyw2)))

      score = -sum(1 for token in tokens1 if token in tokens2)
      heappush(ranking,[score,auth])
    while len(similars)<num:
      authscore = heappop(ranking)
      similars.append([authscore[1],authordict[authscore[1]]['Keywords']])
  else:
    for auth in authordict:
      score = Analyze.similarauthors(authordict[author],authordict[auth])
      heappush(ranking,[score,auth])
    while len(similars)<num:
      authscore = heappop(ranking)
      similars.append([authscore[1],authordict[authscore[1]]['Keywords']])
    print(authordict[author]['Keywords'])
  return similars

def suggestpapers(myfilename,filename,num):
##read data and find similar papers to the papers in file
##
  f2 = open(myfilename,'r+',encoding='utf-8')
  mydata = csv.reader(f2)
  mypapers=[]
  for paper in mydata:
    mypapers.append([paper[0],paper[1],paper[2],paper[3],paper[4]])
  f2.close()
  del mypapers[0]
    
  similars = []
  num = 10
  for paper in mypapers:
    f1 = open(filename,'r+',encoding='utf-8')
    rawdata = csv.reader(f1)
    similars.append([paper,Analyze.similarpapers(paper,rawdata,num)])
    f1.close()
  
  return similars

#cleanfile('rawdata.csv','cleandata.csv')

#pltCitCollab('cleandata.csv')

#pltCitClarity('cleandata.csv')

#pltCitRate('cleandata.csv')

#print(idauthor('cleandata.csv','kwiat'))

##f1 = open('cleandata.csv','r+',encoding='utf-8')
##rawdata=csv.reader(f1)
##authordict = Analyze.savedictauthor(rawdata,True)
##f1.close()
##authordict = getauthordict('authordict.csv')

##authordata = getauthor('cleandata.csv','o.p')
##print(authordata[0])
##for key,value in authordata[1].items():
##  print(key)
##  print(value)

#alist = rank('cleandata.csv','Citations',20)

#alist = suggestauthors('o.pfister',10)

alist = suggestauthors('optical quantum computing',10)

##alist = suggestpapers('mydata.csv','cleandata.csv',10)
##print(alist[0][0])
##alist = alist[0][1]
##
for element in alist:
  print(element)
