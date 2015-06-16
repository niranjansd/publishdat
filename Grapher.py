import sys
import re
import time
import signal
import csv
import math
from heapq import heappush, heappop, heapify
import numpy
import scipy
import nltk
import matplotlib.pyplot as pyp
import Analyze


#Handles ctrl c interrupts
exit_now = False
def signal_handler(signal, frame):
  global exit_now
  print ('*** Exiting gracefully ***')
  exit_now = True

def authorgraph(rawdata):
####Take raw data of papers and create an author graph
####Format :
####  authordict = dictionary, {author name : total citations}
####  graph = list,[[num of authors, 0, number of author connections],\
####                [ author1, author2, citations of 1 joint paper]] 
####Each edge represents two co-authors of a given paper. So the same
####pair of authors can have multiple edges due to multiple papers.
####It seems redundant, but it is information of number of papers.
  
    edges=[]
    authordict={}
    count=0
    allcount=0
    authid = 1
    for paper in rawdata:
        authors = paper[2].split(',')
        try: 
          citations = int(paper[4])
        except(Exception):
          continue
        for i in range(len(authors)):
          if authors[i] in authordict:
            authordict[authors[i]]['Citations'] += citations
            authordict[authors[i]]['NumPapers'] += 1.0
            authordict[authors[i]]['Co-Authors'].add(author for author in authors if author is not authors[i])
          else:
            authordict[authors[i]] = {'Id':authid,'Co-Authors':set([author for author in authors if author is not authors[i]]),'Citations':citations,'NumPapers':1.}
            authid += 1
          for j in range(len(authors)):
             if j>i:
              edges.append([authors[i],authors[j],citations])
    graph = [[len(authordict),0,len(edges)]]+edges
    return authordict, graph
  
def graphsave(filename):
##read data from csv file, extract author graph and save to new csv
  f1 = open(filename,'r+',encoding='utf-8')
  rawdata = csv.reader(f1)
  graph = authorgraph(rawdata)
  f1.close()

  authordict = graph[0]
  numvert = graph[1][0][0]
  numedge = graph[1][0][1]
  edges = graph[1][1:]
  bigraph,graphdict = bidirgraph(graph)
  cost = 1

  headings = ['Id', 'Label', 'Citations','NumPapers','Co-Authors']
  with open('graphnodes.csv','w+',newline='',encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=headings)
    writer.writeheader()
    for author,info in authordict.items():
        node={'Label':author}
        node.update(info)
        writer.writerow(node)
  
  headings=['Source','Target','Weight']
  with open('graphedges.csv','w+',newline='',encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=headings)
    writer.writeheader()
    for row in bigraph:
        edge={'Source':authordict[row[0]]['Id'],'Target':authordict[row[1]]['Id'],'Weight':row[2]}
        writer.writerow(edge)

  print('Saved graph : nodes in graphnodes.csv, edges in graphedges.csv')

def bidirgraph(graph):

####Take authorgraph and create a directed graph 
####Format of input :
####  authordict = dictionary, {author name : total citations}
####  graph = list,[[num of authors, 0, number of author connections],\
####                [ author1, author2, citations of 1 joint paper]] 
####Each edge represents two co-authors of a given paper. So the same
####pair of authors can have multiple edges due to multiple papers.
####It seems redundant, but it is information of number of papers.
####Format of output :
####  graphdict = dictionary, {author name : {collaborator : total shared citations}}
####  bigraph = list, [author1, author2, 1- num shared citations/total author1 citations]
####Now the citations of each pair of authors is added up, so the edges
####represent the total collaboration measure, not just 1 paper
####Each pair of authors gets two directed edges, a->b and b->a. The weight of
####edge is the 1- num shared citations/total author1 citations.
####So if ab collaborations represent all of a's citations, and only half of
####b's citations, then a->b = 0, and b->a = 0.5.
####i.e from a's perpective, b is the closest person to him. but from b's perspective
####a is only 50% of his network.
####Edges can only be 0-1, no negative edges. Many cycles obviously.

    #print(graph[1][0])
    graphdict = {}
    authordict=graph[0]
    for author in authordict.keys():
        graphdict[author]={}
    for edge in graph[1][1:]:
        if edge[1] in graphdict[edge[0]]:
            graphdict[edge[0]][edge[1]] += edge[2]
        else:
            graphdict[edge[0]][edge[1]] = edge[2]
        if edge[0] in graphdict[edge[1]]:
            graphdict[edge[1]][edge[0]] += edge[2]
        else:
            graphdict[edge[1]][edge[0]] = edge[2]
            
    bigraph=[]
    headings=['Author1','Author2','Fraction of 1s papers']
    with open('bigraph.csv','w+',newline='',encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headings)
        writer.writeheader()
        for author,connects in graphdict.items():
            for collab,citations in connects.items():
                bigraph.append([author, collab, 1-citations/authordict[author]['Citations']])
                edge={'Author1':author,'Author2':collab,\
                      'Fraction of 1s papers':1-citations/authordict[author]['Citations']}
                writer.writerow(edge)
    print(str(len(bigraph))+' edges in graph')
    print('Saved directed graph weighted by citations in bigraph.csv')

    return bigraph,graphdict

def minpath(author1,author2,rawdata):
####use djikstra's algo to find shortest path between two authors
####use graphdict from the bigraph above
####Format of output :
####  lenpath = int, cost*len(path)+sum_pathnodes(1-edge citations/node citations)
####  path = list, [author1, connection1, connection2,... author2]
    authordict,graph = authorgraph(rawdata)
    bigraph,graphdict = bidirgraph([authordict,graph])
    if author1 not in graphdict:
      return (author1 + ' has no papers')
    elif author2 not in graphdict:
      return (author2 + ' has no papers')
    cost = 1
    frontier = []
    expanded = set([])
    heappush(frontier,[0,[author1]])
    while frontier:
      expander = heappop(frontier)
      tempauth = expander[1][-1]
      expanded.add(tempauth)
      path = expander[1]
      lenpath = expander[0]
      if tempauth == author2:
        break
      connects = graphdict[tempauth]
      for author,citations in connects.items():
        if author not in expanded:
          heappush(frontier,[lenpath+cost+1-citations/authordict[tempauth]['Citations'],path+[author]])
    if tempauth == author2:
      return lenpath, path
    else:
      return (author1+' and '+author2+' are not connected.')

  

def main():
##    f1 = open('rawdata.csv','r+',encoding='utf-8')
##    rawdata = csv.reader(f1)
##    bigraph=bidirgraph(authorgraph(rawdata))
##    graphsave('rawdata.csv')
##    f1.close()
    f1 = open('rawdata.csv','r+',encoding='utf-8')
    rawdata = csv.reader(f1)
    path = minpath('P. G. Kwiat','O. Pfister',rawdata)
    print(path)
    f1.close()
    f1 = open('rawdata.csv','r+',encoding='utf-8')
    rawdata = csv.reader(f1)
    path = minpath('O. Pfister','P. G. Kwiat',rawdata)
    print(path)
    f1.close()
    return path


if __name__=="__main__":
    main()
