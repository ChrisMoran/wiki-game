#! /usr/bin/python
# Find number of hops between wikipedia articles
# Uses single threaded dumb breadth-first search
# TODO: Bidirectional search?, multithread, is io bounded 

from sys import argv
import urllib
import urllib2
import json
import re
import contextlib

DEFAULT_DEPTH = 6
BASE_URL = "http://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&%s"
LINK_RE = re.compile(r'\[\[([^\]\]]+)]]')

def encoded_dict(in_dict):
    out_dict = {}
    for k, v in in_dict.iteritems():
        if isinstance(v, unicode):
            v = v.encode('utf8')
        elif isinstance(v, str):
            # Must be encoded in UTF-8
            v.decode('utf8')
        out_dict[k] = v
    return out_dict

def urlEncodeUnicode(dct):
    return urllib.urlencode(encoded_dict(dct))
		

	
def getWikiPages(topicsList):
    topics = "|".join(topicsList)
    req = urllib2.Request(url=BASE_URL % urlEncodeUnicode({'titles' : topics}))
    req.add_header('User-Agent', 'WikiLinkGame/1.0')
    with contextlib.closing(urllib2.urlopen(req)) as f:
        return f.read()
	
def getWikiIter(topicsList):
    chunkSize = 20
    for chunk in xrange(0,len(topicsList), chunkSize):
        end = chunk + chunkSize - 1 if chunk + chunkSize - 1 < len(topicsList) else len(topicsList)
        pages = json.loads(getWikiPages(topicsList[chunk:end]))
        if pages['query'] and pages['query']['pages']:
            for item in pages['query']['pages'].itervalues():
                if 'revisions' in item:
                    yield (item['title'], item['revisions'][0]['*'])
		            
def exploreTopics(topicList, topicDict, depth):
    for title, content in getWikiIter(topicList):    
        for linkMatch in re.findall(LINK_RE, content):
            parts = linkMatch.split('|')
            if not ':' in parts[0] and parts[0] not in topicDict:
                topicDict[parts[0]] = (depth, title) # depth, parent
	
def game(startTopic, endTopic, depth):
    print "Starting game %s %s %d" % (startTopic, endTopic, depth)
    topicDict = { startTopic : (0,None) }
    
    for i in xrange(depth):
        topicsList = []
        for topic, info in topicDict.iteritems():
            if info[0] == i: # unexplored
                topicsList.append(topic)
                
        exploreTopics(topicsList, topicDict, i+1)
        if endTopic in topicDict:
            print "Found %s in %d steps" % (endTopic, i)
            return
    

def getHelpMessage():
    return """ usage: ./wiki-game.py [topic1] [topic2] [optionalDepth] """

def start(rawArgs):
    lenRawArgs = len(rawArgs)
    if not ((lenRawArgs == 3) or (lenRawArgs == 4)):
        print getHelpMessage()
        return
    depth = DEFAULT_DEPTH if lenRawArgs == 3 else int(rawArgs[3])
    game(rawArgs[1], rawArgs[2], depth)


start(argv)