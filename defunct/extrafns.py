def keywords(filename,rawlabel):
#read file and find the research keywords of the given author
  f1 = open(filename,'r+',encoding='utf-8')
  rawdata=csv.reader(f1)
  authordict = Analyze.dictauthor(rawdata)
  f1.close()

  author = Analyze.idauthor(authordict,rawlabel)

  f1 = open(filename,'r+',encoding='utf-8')
  rawdata=csv.reader(f1)
  keywords = Analyze.getkeyw(author,rawdata)
  f1.close()
  keys =  list(keywords[0])
  return keys

def allkeywords(filename):
#read file and find the research keywords of all author
  f1 = open(filename,'r+',encoding='utf-8')
  rawdata=csv.reader(f1)
  authordict = Analyze.dictauthor(rawdata)
  f1.close()

  f1 = open(filename,'r+',encoding='utf-8')
  rawdata=csv.reader(f1)
  authordict = Analyze.getallkeyw(rawdata,authordict)
  f1.close()

  return authordict

def getkeyw(author,rawdata):
#identify the keywords, topics of research of the author
    stops=nltk.corpus.stopwords.words('english') #stopwords to weed out
    stops = stops + ['we',',','.','(',')','using','new','propose','investigate']
    pairs=[]
    for paper in rawdata:
      if author in paper[2]:
        abstract = paper[3]
        abstract = re.sub(r'<.*?>','',abstract)
        tokens = nltk.word_tokenize(abstract.lower())
        allpairs = [list(pair) for pair in nltk.bigrams(tokens)]
        pairs = pairs + [" ".join(bg) for bg in allpairs if bg[0] not in stops and bg[1] not in stops]
    fd = nltk.FreqDist(pairs)
    keyfreqs = fd.most_common(20)
    keyws = list(zip(*keyfreqs))
    
    return keyws


def dictauthorkeys(rawdata):
#creates dictionary with authors as the keys
# value of each author is a dictionary with
# keys:values 'Co-Authors','Citations','NumPapers', 'Keywords'
    authordict={}
    for paper in rawdata:
#Cleaning extraneous effects.
        paper[2] = paper[2].strip(' ,')
        if ', Jr' in paper[2]:
          paper[2] = paper[2].replace(', Jr.',' Jr')
        if ',Jr' in paper[2]:
          paper[2] = paper[2].replace(',Jr.',' Jr')
        if ', Jr' in paper[2]:
          paper[2] = paper[2].replace(', Jr',' Jr')
        if ', St' in paper[2]:
          paper[2] = paper[2].replace(', St.',' St')
        if ', III' in paper[2]:
          paper[2] = paper[2].replace(', III','III')
        if ', II' in paper[2]:
          paper[2] = paper[2].replace(', II','II')
        if ', and' in paper[2]:
          paper[2] = paper[2].replace(', and',',')
          
        try:
          citations = int(paper[4])
        except(Exception):
          continue
        
        stops=nltk.corpus.stopwords.words('english') #stopwords to weed out
        stops = stops + ['we',',','.','(',')','using','new','propose','investigate']
        abstract = paper[3]
        abstract = re.sub(r'<.*?>','',abstract)
        tokens = nltk.word_tokenize(abstract.lower())
        allpairs = [list(pair) for pair in nltk.bigrams(tokens)]
        pairs = [" ".join(bg) for bg in allpairs if bg[0] not in stops and bg[1] not in stops]
        
        authors = paper[2].split(',')
        for i in range(len(authors)):
          nameparts = re.split(r'[\-\.,\s]\s*', authors[i])
          while '' in nameparts:
            nameparts.remove('')
          for j in range(len(nameparts)-1):
            nameparts[j]=nameparts[j][0]
          authors[i] = '. '.join(nameparts)

#saving the data in dict        
        for author in authors:
          if author in authordict.keys():
            authordict[author]['Citations'] += citations
            authordict[author]['NumPapers'] += 1.
            authordict[author]['Co-Authors'].update([auth for auth in authors if auth is not author])
            authordict[author]['Keywords'] += pairs
          else:
            authordict[author] = {'Co-Authors':set([auth for auth in authors if auth is not author]),'Citations':citations,'NumPapers':1.,'Keywords':pairs}

#for each author and get the most common keywords
    for author in authordict.keys():
      fd = nltk.FreqDist(authordict[author]['Keywords'])
      keyfreqs = fd.most_common(20)
      keyws = list(zip(*keyfreqs))
      try :
        authordict[author]['Keywords'] = list(keyws[0])
      except(Exception):
        print(keyws,author,authordict[author])

    print(str(len(authordict))+' authors recorded')
    return authordict


def getallkeyw(rawdata,authordict):
#identify the keywords, topics of research of the author
    stops=nltk.corpus.stopwords.words('english') #stopwords to weed out
    stops = stops + ['we',',','.','(',')','using','new','propose','investigate']
    for paper in rawdata:
      if paper[0]=='url':
        continue
#get abstract and add the keywords to each author in authordict      
      authors = paper[2].split(',')
      abstract = paper[3]
      abstract = re.sub(r'<.*?>','',abstract)
      tokens = nltk.word_tokenize(abstract.lower())
      allpairs = [list(pair) for pair in nltk.bigrams(tokens)]
      pairs = [" ".join(bg) for bg in allpairs if bg[0] not in stops and bg[1] not in stops]
      for author in authors:
        if 'Keywords' in authordict[author].keys():
          authordict[author]['Keywords'] += pairs
        else:
          authordict[author]['Keywords'] = pairs
#for each author and get the most common keywords
    for author in authordict.keys():
      fd = nltk.FreqDist(authordict[author]['Keywords'])
      keyfreqs = fd.most_common(20)
      keyws = list(zip(*keyfreqs))
      try :
        authordict[author]['Keywords'] = list(keyws[0])
      except(Exception):
        print(keyws,author)
    return authordict
