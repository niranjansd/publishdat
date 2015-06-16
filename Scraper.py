import sys
import re
import urllib, requests
import time
import signal
import http.client
import csv
import math


#Handles ctrl c interrupts
exit_now = False
def signal_handler(signal, frame):
  global exit_now
  print ('*** Exiting gracefully ***')
  exit_now = True

PRAUrls = set([])
PRAUrls2do = set([])
f1=open('PRAUrls.txt','r+',encoding='utf-8')
for line in f1:
  if line is not '':
    PRAUrls.add(line[0:-1])
f2=open('PRAUrls2do.txt','r+',encoding='utf-8')
for line in f2:
  if line is not '':
    PRAUrls2do.add(line[0:-1])
##print(PRAUrls)
print(len(PRAUrls2do))

rawdata=[]
proxylist =['http://195.151.225.245:8080','http://103.27.24.236:81']
proxylist +=['http://62.176.13.22:8088','http://93.158.212.111:7808']

proxies={'http':proxylist[0]}
s=requests.Session()
s.proxies=proxies
prox=1
i=0
##with open('rawdata.csv','w',newline='',encoding='utf-8') as csvfile:
##  headings=['url','title','authors','abstract','citations']
##  writer = csv.DictWriter(csvfile, fieldnames=headings)
##  writer.writeheader()

while PRAUrls2do:
    paper=[]
    dicti={}
    crawling=PRAUrls2do.pop()
#    print(crawling)
    if i%100==0:
      print(i)
      if i==10000:
        break
    if crawling not in PRAUrls:
      try:
        r=s.get(crawling)
        page=r.content.decode('utf-8')
        while page.find('Access Denied Due to Abuse')>0 or page.find('ERROR: The requested URL could not be retrieved')>0 or page.find('Internal server error.')>0:
          print(s.proxies['http'])
          time.sleep(5)
          s.proxies['http']=proxylist.pop()
          r=s.get(crawling)
          page=r.content.decode('utf-8')
        paper.append(crawling) #paper[0] is the url
                
        a=page.find('title')
        title=page[a+6:page.find('title',a+1)-2]
        paper.append(title)  #paper[1] is the title

        a=page.find('/search/field/author/')
        authors=page[a+21:page.find('">',a+1)]
        a=page.find('/search/field/author/',a+1)
        while a>-1:         
          authors=authors+","+page[a+21:page.find('">',a+1)]
          a=page.find('/search/field/author/',a+1)
        paper.append(authors) #paper[2] is the abtract

        a=page.find('<div class="content"><p>')
        abstract=page[a+24:page.find('</p>',a+1)]
        paper.append(abstract) #paper[2] is the abtract

        a=page.find('Citing Articles')
        citations=page[a+17:page.find(')',a+1)]
        paper.append(citations) #paper[2] is the abtract

        dicti['url'] = paper[0]
        dicti['title'] = paper[1]
        dicti['authors'] = paper[2]
        dicti['abstract'] = paper[3]
        dicti['citations'] = paper[4]
        #print(dicti)
        if '<' not in ''.join(paper[0]+paper[2]+paper[4]):
#          while re.search(r'<.*?>',paper[3]):
          re.sub(r'<.*?>','',paper[3])
##          while '<' in paper[3]:
##            if paper[3].find('<') and paper[3].find('>') and paper[3].find('<')<paper[3].find('>'):
##              paper[3]=paper[3][:paper[3].find('<')]+paper[3][paper[3].find('>')+1:]
##            elif paper[3].find('>'):
##              paper[3]=paper[3][paper[3].find('>')+1:]
##            elif paper[3].find('<'):
##              paper[3]=paper[3][:paper[3].find('<')]
##            else:
##              break
          with open('rawdata.csv','a',newline='',encoding='utf-8') as csvfile:
            headings=['url','title','authors','abstract','citations']
            writer = csv.DictWriter(csvfile, fieldnames=headings)
            writer.writerow(dicti)
            i+=1
            f1.write(paper[0]+'\n')
        else:
          print(paper[0]+paper[2]+paper[4])
      except(Exception):
        print(s.proxies['http'])
        time.sleep(5)
        s.proxies['http']=proxylist.pop()
        PRAUrls2do.add(crawling)
##data = u'naïve café'
##normal = unicodedata.normalize('NFKD', data).encode('ASCII', 'ignore')
##print normal


##        a=page.find("a href=")
##        while a>-1:
##            link=root+page[a+8:page.find(">",a)-1]
##            if "pra/issues" in link and link not in crawled and link not in tocrawl:
##                tocrawl.add(link)
##                f2.write(link+'\n')
##            if "pra/abstract" in link and link not in PRAUrls:
##                PRAUrls.add(link)
##                f3.write(link+'\n')
##            a=page.find("a href=",a+1)
##        crawled.add(crawling)
##    if i==3:
##      break
len(PRAUrls)

f1.close()
f2.close()


