# publishdat
assimilating and organizing journal publication data

Scrape a bunch of journal publication data
Linkcollector.py first scrapes the links and saves in text files.
Scraper.py actually goes to each link and saves the url, title, authors, abstract and citations in csv file
scraper was written a long time ago, it is very messy and output is not reliable, need to update it.

Data is stored in csv files, rawdata.csv.

#NLTK PROJECT
Analyze.py has a bunch of functions that use this data from csv file 
Insights.py is the higher level functions which generalize the Analyze functions to accept input
from user.

Extracted data in other files.
 - cleaned data saved in cleandata.csv
 - author wise info saved as author dictionaries in authordict.csv

Extracts details and rankings of all authors by citations, number of coauthors etc, 
Extracts author research keywords and finds similar authors using keywords similarity.

#GRAPH PROJECT
Grapher.py extracts an undirected graph of authors connected by co-authorship weighted by number of shared citations.
saved in graph.csv
Also extracts a directed graph of coauthroship, weighted by relative contributions of source author towards 
target authors citations, saved in bigraph.csv
Finds shortest directed path between two authors using Djikstra.
graphnodes.csv and graphedges.csv files created for Gephi import format for visualization.



