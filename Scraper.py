import sys
import re
import urllib, requests
import time
import signal
import http.client


#Handles ctrl c interrupts
exit_now = False
def signal_handler(signal, frame):
  global exit_now
  print ('*** Exiting gracefully ***')
  exit_now = True

PRAUrls = set([])
PRAUrls2do = set([])
f1=open('PRAUrls.txt','r+')
for line in f1:
  if line is not '':
    PRAUrls.add(line[0:-1])
f2=open('PRAUrls2do.txt','r+')
for line in f2:
  if line is not '':
    PRAUrls2do.add(line[0:-1])
print(PRAUrls)
print(len(PRAUrls2do))
dicti={}
paper=[]
s=requests.Session()
while PRAUrls2do:
    crawling=PRAUrls2do.pop()
    print(crawling)
    if crawling not in PRAUrls:
        r=s.get(crawling)
        paper.append(crawling) #paper[0] is the url
        page=r.content.decode('utf-8')

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
        print(dicti)
        break
        a=page.find("a href=")
        while a>-1:
            link=root+page[a+8:page.find(">",a)-1]
            if "pra/issues" in link and link not in crawled and link not in tocrawl:
                tocrawl.add(link)
                f2.write(link+'\n')
            if "pra/abstract" in link and link not in PRAUrls:
                PRAUrls.add(link)
                f3.write(link+'\n')
            a=page.find("a href=",a+1)
        crawled.add(crawling)
    break


f1.close()
f2.close()


