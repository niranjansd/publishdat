import sys
import re
import urllib, requests
import time
import signal
import nltk
import numpy as np
import random
np.seterr(divide='ignore',invalid='ignore')

#Handles ctrl c interrupts
exit_now = False
def signal_handler(signal, frame):
  global exit_now
  print ('*** Exiting gracefully ***')
  exit_now = True

#Define the vocabulary
def addvocab(text,words)
    words=list(set(words + nltk.word_tokenize(text.lower())))

#Define and train the markov model from given text
  
def addtrain(text,gram,vocab):
  numvocab = len(vocab)
  ##  Clean the text
  tokens=nltk.word_tokenize(text.lower())  
  tokens=['NIV' if word not in vocab for word in tokens]
## Train the model
  index=[]
  #add space so we can count from the second letter on
  text='_'+text

def train(vocab):
  numvocab = len(vocab)
  #there are num_chars^2 posibilities of the two chars preceding each element 
  markovtrain=np.zeros(shape=(numvocab,num_chars*num_chars),dtype=float)

  #record the number of occurences of 3 letter sequence.
  for i in range(len(text)):
    if i<gram-1:
      continue
    index=[]
    for j in range(gram):
      index.append(mysetofchars.find(text[i-j]))
  #Given the last two chars are ith jth element, the probability of
  #kth element in setofchars appearing next is markovtrain(k,j+i*50)
    markovtrain[index[0],index[1]+index[2]*num_chars] += 1. 

##Normalize s.t for each {i,j} sum of probabiities over all k=1
  ji_counts=np.sum(markovtrain,axis=0,keepdims=True) 
  markov_norm=np.divide(markovtrain,ji_counts)
  markov_norm=np.nan_to_num(markov_norm) #correct the divide by zero errors

  return markov_norm

##Generate text from model
def generatetext(lentext,markov,gram,mysetofchars):
  num_chars=len(mysetofchars)
  firstletter=random.randint(0,27) #start the text with a random alphabet
  newtext=[num_chars-1,firstletter] #initialize with a space
  for i in range(lentext+1):
      if i<2:
          continue
      nextprob=random.random() #pick a random probability
      cumprob=0       #cumulative probability
      j=-1
  #accumulate probabilities over k, until finding the element that exceeds the
  #random probability instance, then choose that element
      while cumprob<nextprob:
          j=j+1
          cumprob=cumprob+markov[[j],newtext[i-2]*50+newtext[i-1]]
      newtext.append(j)

  #translate newtext index list into finaltext
  finaltext='' 
  for i in range(len(newtext)):
      finaltext=finaltext+mysetofchars[newtext[i]]
  finaltext=' '.join(finaltext.split('_'))[1:lentext+1] #Clean up
  return finaltext

##Calculate the probability of generating a sample text
def sample_prob(sample,markov,gram,mysetofchars):
  sample=sample.lower()
  sample='_'+'_'.join(sample.split()) #replace ' ' with _
  num_chars=len(mysetofchars)
  missing=[]
  probability=0  #initialize the sample text probability
  for i in range(len(sample)-3):
      index=[]
      for j in range(gram):
          index.append(mysetofchars.find(sample[i+2-j]))
  #for each char get the probability from the markov model
      ptemp=markov[index[0],index[1]+index[2]*num_chars]
      if ptemp>0:
  #the probablity is too low to be measured, hence measured in log scale
          probability=probability+np.log10(ptemp)
      else:
  #record all the 3 char strings that have probability 0
          missing.append(sample[i]+sample[i+1]+sample[i+2])

  #make sure the missing 3 char strings are actually missing
  for i in range(len(missing)):
      if(text.find(missing[i])) is not -1:
        print('Error : strings missing in model')
  return [probability,missing]

######################main###################################
#read the text from text file
f1=open('text.txt','r+',encoding='utf-8')
text=f1.read()
f1.close()

#Remove all letters that are not english, numbers, or punctuation.
mysetofchars='abcdefghijklmnopqrstuvwxyz1234567890,.:;\'\"?()[]-!_'

#Define and train the markov model
gram=3 #the tri in the trigram markov model
markov = train(text,gram,mysetofchars)

#Generate text of given length
lentext=200
gentext = generatetext(lentext,markov,gram,mysetofchars)
print('Generated text is : \n'+gentext+'\n')

#Read the given sample text
f2=open('sample_text.txt','r+')
sample = f2.read()
f2.close()

#Calcualte probability of a sample text
probout=sample_prob(sample,markov,gram,mysetofchars)
sample_probability='10^('+str(probout[0])+')'
print('Probability of generating sample is :'+str(sample_probability))
if len(probout[1])>0:
  print('Actual probability is 0, required substrings not present in training text') 
