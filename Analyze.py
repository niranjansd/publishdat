import sys
import re
import time
import signal
import csv
import math
import string
from heapq import heappush, heappop
import numpy
import scipy
import nltk
import sqlite3
import pandas
import matplotlib.pyplot as pyp

#sys.setdefaultencoding('utf8')

#Handles ctrl c interrupts
exit_now = False
def signal_handler(signal, frame):
  global exit_now
  print ('*** Exiting gracefully ***')
  exit_now = True

def cleanfile(rawdata,filename):
#cleans rawdata and saves it into new file.
    with open(filename,'w',newline='',encoding='utf-8') as csvfile:
      headings=['url','title','authors','abstract','citations']
      writer = csv.DictWriter(csvfile, fieldnames=headings)
      writer.writeheader()

    for paper in rawdata:
        #Cleaning some extraneous effects.
        paper[2] = paper[2].strip(' ,')
        if 'Jr' in paper[2]:
          paper[2] = paper[2].replace(', Jr.',' Jr')
          paper[2] = paper[2].replace(',Jr.',' Jr')
          paper[2] = paper[2].replace(', Jr',' Jr')
          paper[2] = paper[2].replace(',Jr',' Jr')
        if ', St' in paper[2]:
          paper[2] = paper[2].replace(', St.',' St')
        if ', II' in paper[2]:
          paper[2] = paper[2].replace(', III','III')
          paper[2] = paper[2].replace(', II','II')
        if ', and' in paper[2]:
          paper[2] = paper[2].replace(', and',',')
          
        try:
          citations = int(paper[4])
        except(Exception):
          continue
        
        authors = list(filter(None,paper[2].split(',')))
        for i in range(len(authors)):
          nameparts = re.split(r'[\-\.,\s]\s*', authors[i])
          while '' in nameparts:
            nameparts.remove('')
          for j in range(len(nameparts)-1):
            nameparts[j]=nameparts[j][0]
          authors[i] = '. '.join(nameparts)
        paper[2] = ','.join(authors)

        paper[3] = re.sub(r'<.*?>','',paper[3])
        dicti={}
        dicti['url'] = paper[0]
        dicti['title'] = paper[1]
        dicti['authors'] = paper[2]
        dicti['abstract'] = paper[3]
        dicti['citations'] = paper[4]
        with open(filename,'a',newline='',encoding='utf-8') as csvfile:
            headings=['url','title','authors','abstract','citations']
            writer = csv.DictWriter(csvfile, fieldnames=headings)
            writer.writerow(dicti)
    
def citacollab(rawdata,count):
##calculates the citations-collaboration corelation.
##row0 is number of co-authors or each paper
##row1 is the number of citations for the coresponding paper
    data = numpy.zeros((2,count))
    i = 0
    for paper in rawdata:
        try:
          authors = paper[2].split(',')
          citations = int(paper[4])
          data[0,i] = len(authors)
          data[1,i] = citations
          i += 1
        except (Exception):
          continue
    return data

def clarityscore(text):
    score = len(text)
    return score
    
def citaclarity(rawdata,count):
##calculates the citations-clarity corelation.
##row0 is length of abstract or each paper
##row1 is the number of citations for the coresponding paper
    data = numpy.zeros((2,count))
    i = 0
    for paper in rawdata:
      try:
        abstract = paper[3]
        citations = int(paper[4])
        data[0,i] = clarityscore(abstract)
        data[1,i] = citations
        i += 1
      except (Exception):
        continue
    return data

def readmydata(num):
    f2 = open('mydata.csv','r+',encoding='utf-8')
    mydata = csv.reader(f2)
    paper = mydata[num]
    f2.close()
    return paper

def dictauthor(rawdata):
#creates dictionary with authors as the keys
# value of each author is a dictionary with
# keys:values 'Co-Authors','Citations','NumPapers'
    authordict={}
    for paper in rawdata:
        if paper[0]=='url':
            continue
        citations = int(paper[4])
        title = paper[1]
        abstract = paper[3]
        
        authors = paper[2].split(',')

#saving the data in dict        
        for author in authors:
          if author in authordict.keys():
            authordict[author]['Citations'] += citations
            authordict[author]['NumPapers'] += 1.
            authordict[author]['Co-Authors'] += [auth for auth in authors if auth is not author]
            authordict[author]['Papers'].append(title)
          else:
            authordict[author] = {'Co-Authors':[auth for auth in authors if auth is not author],'Citations':citations,'NumPapers':1.,'Papers':[title]}
    print(str(len(authordict))+' authors recorded.')
    return authordict

def savedictauthor(rawdata,keyflag):
#creates dictionary with authors as the keys
# value of each author is a dictionary with
# keys:values 'Co-Authors','Citations','NumPapers','Papers','Keywords'
    authordict={}
    for paper in rawdata:
        if paper[0]=='url':
            continue
        citations = int(paper[4])
        title = paper[1]
        abstract = paper[3]
        
        authors = paper[2].split(',')

#saving the data in dict        
        for author in authors:
          if author in authordict.keys():
            authordict[author]['Citations'] += citations
            authordict[author]['NumPapers'] += 1.
            authordict[author]['Co-Authors'].update([auth for auth in authors if auth is not author])
            if keyflag:
              authordict[author]['Papers'].append(title)
              authordict[author]['Keywords'] += ' '+title+' '+abstract
          else:
            authordict[author] = {'Co-Authors':set([auth for auth in authors if auth is not author]),'Citations':citations,'NumPapers':1.}
            if keyflag:
              authordict[author]['Keywords'] = title+' '+abstract
              authordict[author]['Papers'] = [title]
    print('savedone')
    
#for each author and get the most common keywords
    if keyflag:
      with open('authordict.csv','w',newline='',encoding='utf-8') as csvfile:
        headings=['Author','NumPapers','Citations','Co-Authors','Papers','Keywords']
        writer = csv.DictWriter(csvfile, fieldnames=headings)
        writer.writeheader()

      stops=nltk.corpus.stopwords.words('english') #stopwords to weed out
      stops = stops + ['-','we',',','.','(',')','using','new','propose','investigate']
      stops = stops + [';',':','$','&','et','al','show','infer','novel','method']
      for author in authordict.keys():
        abstract=authordict[author]['Keywords']
        tokens = nltk.word_tokenize(abstract.lower())
        allpairs = [list(pair) for pair in nltk.bigrams(tokens)]
        pairs = [" ".join(bg) for bg in allpairs if bg[0] not in stops and bg[1] not in stops]
        pairs = [pair for pair in pairs if re.match(r'[\w -]+',pair) is not None]
        fd = nltk.FreqDist(pairs)
        keyfreqs = fd.most_common(20)
        keyws = list(zip(*keyfreqs))
        try :
          authordict[author]['Keywords'] = list(keyws[0])
        except(Exception):
          print(keyws,author,pairs)

#write dict to csv
        dicti=authordict[author]
        dicti['Author']=author
        dicti['Co-Authors'] = ','.join(list(dicti['Co-Authors']))
        dicti['Papers'] = ','.join(dicti['Papers'])
        dicti['Keywords'] = ','.join(dicti['Keywords'])
        with open('authordict.csv','a',newline='',encoding='utf-8') as csvfile:
          headings=['Author','NumPapers','Citations','Co-Authors','Papers','Keywords']
          writer = csv.DictWriter(csvfile, fieldnames=headings)
          writer.writerow(dicti)

    print(str(len(authordict))+' authors recorded')
    return authordict

def idauthor(authordict,rawlabel):
#lookup authordict find the closest match author to rawlabel and confirm/return actual label
    if rawlabel in authordict.keys():
        return rawlabel
    for author in authordict.keys():
        if rawlabel.lower().replace(' ','') in author.lower().replace(' ',''):
            response = input('Did you mean '+author+': (y/n)')
            if response is 'y':
                return author
            if response is 'n':
                continue              
    print('Could not find '+rawlabel+' in authorlist')
    return ''

def textsimilarity(text1,text2):
    score=[]
    stops=nltk.corpus.stopwords.words('english') #stopwords to weed out
    stops = stops + ['we',',','.','(',')','using','new','propose','investigate']
    stops = stops + ['-','show','infer','novel','method']

#get tokens and bigrams from the text, either string or list of keywords
    if type(text1) is not list:
      alltokens = nltk.word_tokenize(text1.lower())
      allpairs = [list(pair) for pair in nltk.bigrams(alltokens)]
      tokens1 = [token for token in alltokens if token not in stops]
      pairs1 = [" ".join(bg) for bg in allpairs if bg[0] not in stops and bg[1] not in stops]
    else:
      alltokens = []
      allpairs1 = []
      for el in text1:
        atokens = nltk.word_tokenize(el.lower())
        alltokens += atokens
        apairs = [list(pair) for pair in nltk.bigrams(atokens)]
        allpairs += apairs
      tokens1 = [token for token in alltokens if token not in stops]
      pairs1 = [" ".join(bg) for bg in allpairs if bg[0] not in stops and bg[1] not in stops]

    if type(text2) is not list:
      tokens = nltk.word_tokenize(text2.lower())
      allpairs = [list(pair) for pair in nltk.bigrams(tokens)]
      tokens2 = [token for token in tokens if token not in stops]
      pairs2 = [" ".join(bg) for bg in allpairs if bg[0] not in stops and bg[1] not in stops]
    else:
      for el in text2:
        atokens = nltk.word_tokenize(el.lower())
        alltokens += atokens
        apairs = [list(pair) for pair in nltk.bigrams(atokens)]
        allpairs += apairs
      tokens2 = [token for token in alltokens if token not in stops]
      pairs2 = [" ".join(bg) for bg in allpairs if bg[0] not in stops and bg[1] not in stops]
      
###score single word cosine similarity
##    fd1=nltk.FreqDist(tokens1)
##    fd2=nltk.FreqDist(tokens2)
##    keys=list(set(list(fd1.keys())+list(fd2.keys())))
##    scoretemp=0
##    for key in keys:
##      scoretemp += fd1[key]*fd2[key]
##    score.append(1-scoretemp/(numpy.linalg.norm(numpy.asarray(list(fd1.values())))*numpy.linalg.norm(numpy.asarray(list(fd2.values())))))
##    
####score bigram cosine similarity 
##    fd1=nltk.FreqDist(pairs1)
##    fd2=nltk.FreqDist(pairs2)
##    keys=list(set(list(fd1.keys())+list(fd2.keys())))
##    scoretemp=0
##    for key in keys:
##      scoretemp += fd1[key]*fd2[key]
##    score.append(1-scoretemp/(numpy.linalg.norm(numpy.asarray(list(fd1.values())))*numpy.linalg.norm(numpy.asarray(list(fd2.values())))))
    score.append(sum(1 for token in tokens1 if token in tokens2))
    score.append(sum(1 for pair in pairs1 if pair in pairs2))
    print('done')
##total score is sum of the the scores    
    return sum(score)

def similarity(paper1,paper2):
    score=[]
    stops=nltk.corpus.stopwords.words('english') #stopwords to weed out

##compare the titles and score the word cosine similarity 
    title1 = paper1[1]
    title2 = paper2[1]
    tokens1=[w for w in nltk.word_tokenize(title1) if w not in stops]
    tokens2=[w for w in nltk.word_tokenize(title2) if w not in stops]
    fd1=nltk.FreqDist(tokens1)
    fd2=nltk.FreqDist(tokens2)
    keys=list(set(list(fd1.keys())+list(fd2.keys())))
    scoretemp=0
    for key in keys:
      scoretemp += fd1[key]*fd2[key]
    a = numpy.linalg.norm(numpy.asarray(list(fd1.values())))*numpy.linalg.norm(numpy.asarray(list(fd2.values())))
    if a:
      score.append(1-scoretemp/a)
    else:
      score.append(0)
    
##compare the abstracts and score single word cosine similarity 
    abstract1 = paper1[3]
    abstract2 = paper2[3]
    tokens1=[w for w in nltk.word_tokenize(abstract1) if w not in stops]
    tokens2=[w for w in nltk.word_tokenize(abstract2) if w not in stops]
    fd1=nltk.FreqDist(tokens1)
    fd2=nltk.FreqDist(tokens2)
    keys=list(set(list(fd1.keys())+list(fd2.keys())))
    scoretemp=0
    for key in keys:
      scoretemp += fd1[key]*fd2[key]
    a = numpy.linalg.norm(numpy.asarray(list(fd1.values())))*numpy.linalg.norm(numpy.asarray(list(fd2.values())))
    if a:
      score.append(1-scoretemp/(numpy.linalg.norm(numpy.asarray(list(fd1.values())))*numpy.linalg.norm(numpy.asarray(list(fd2.values())))))    
    else:
      score.append(0)

##compare the abstracts and score bigram cosine similarity 
    tokens1 = nltk.word_tokenize(abstract1)
    tokens2 = nltk.word_tokenize(abstract2)
    bgsall1 = nltk.bigrams(tokens1)
    bgsall2 = nltk.bigrams(tokens2)
    bgs1 = [bg for bg in bgsall1 if bg[0] not in stops and bg[1] not in stops]
    bgs2 = [bg for bg in bgsall2 if bg[0] not in stops and bg[1] not in stops]
    fd1=nltk.FreqDist(bgs1)
    fd2=nltk.FreqDist(bgs2)
    keys=list(set(list(fd1.keys())+list(fd2.keys())))
    scoretemp=0
    for key in keys:
      scoretemp += fd1[key]*fd2[key]
#    print(fd1.values())
    a = numpy.linalg.norm(numpy.asarray(list(fd1.values())))*numpy.linalg.norm(numpy.asarray(list(fd2.values())))
    if a:
      score.append(1-scoretemp/(numpy.linalg.norm(numpy.asarray(list(fd1.values())))*numpy.linalg.norm(numpy.asarray(list(fd2.values())))))
    else:
      score.append(0)

##total score is sum of the three scores    
    return sum(score)

def similarpapers(paper,rawdata,num):
    similars=[]
    scorer=[]
    heapify(scorer)
    for paper1 in rawdata:
      score = similarity(paper,paper1)
      heappush(scorer,[score,paper1])
    while len(similars)<num and len(scorer)>0:
      similars.append(heappop(scorer))
    return similars

def similarauthors(author1,author2):
#compare author dictionaries and keywords and returns similarity score 
    keyw1 = author1['Keywords']
    tokens1 = list(filter(None,re.split(r',',keyw1)))#+re.split(r'[ ,]',keyw1)))
    keyw2 = author2['Keywords']
    tokens2 = list(filter(None,re.split(r',',keyw2)))#+re.split(r'[ ,]',keyw2)))
    score = -sum(1 for token in tokens1 if token in tokens2)
    return score

def cluster(rawdata):
## extract a distance metric using similarity score.
  papers=[]
  for paper in rawdata:
    papers.append(paper)

  dist = numpy.zeros(len(papers))
  for i in range(len(papers)):
    for j in range(len(papers)):
      if i<j:
        score = similarity(papers[i],papers[j])
        dist[i,j]=score
        dist[j,i]=score


def main():

  pass
  
if __name__== "__main__":
  main()



