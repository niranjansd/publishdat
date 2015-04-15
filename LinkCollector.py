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

root="http://journals.aps.org"
start_page="http://journals.aps.org/pra/issues"

tocrawl = set([start_page])
crawled = set([])
PRAUrls = set([])
f1=open('crawled.txt','r+')
for line in f1:
  if line is not '':
    crawled.add(line[0:-1])
f2=open('tocrawl.txt','r+')
for line in f2:
  if line is not '':
    tocrawl.add(line[0:-1])
f3=open('PRAUrls.txt','r+')
for line in f3:
  if line is not '':
    PRAUrls.add(line[0:-1])

s=requests.Session()
while tocrawl:
    crawling=tocrawl.pop()
    print(crawling)
    if crawling not in crawled:
        r=s.get(crawling)
        page=r.content.decode('utf-8')
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

print(tocrawl)
for url1 in crawled:
  f1.write(url1+'\n')
f1.close()
f2.close()
f3.close()

