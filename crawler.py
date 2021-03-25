from bs4 import BeautifulSoup

from threading import Thread
import requests
import configs
import re

MAX_PAGES = 600

crawledPages = 0
relevantPages = 0
crawlerOutput = {}
threads = []
frontier = configs.links
heuristic = configs.heuristic

def isHtml(url):
  head = requests.head(url)
  return "text/html" in head.headers['content-type']

# regex para limpar os dados do robots
def cleanRobots(old, toRemove):
    newString = old
    for x in toRemove:
        newString = newString.replace(x, '')
    return newString

def disallowUrls(url):
  data = []
  robots = requests.get(url + '/robots.txt')

  if robots.status_code == requests.codes.ok:
    for line in robots.content.decode('utf-8').split('\n'):
      if(line != 'User-agent: *'):
        continue
      if(line.startswith('Disallow')):
        cleanedLink = cleanRobots(line.split(': ')[1], '*/_')
        if cleanedLink != '':
          data.append(cleanedLink)
  return data

def Crawler(seedLink):
    #if crawledPages < MAX_PAGES:
    visitedLinks = 0
    disallow = disallowUrls(seedLink)

    if isHtml(seedLink):
      page = requests.get(seedLink, headers=configs.agent, timeout=5)
      soup = BeautifulSoup(page.content, 'lxml')

      for anchor in soup.find_all('a', href=True):
        if anchor['href'].startswith('http'):
          if disallow == []:  # sem restrições do robots
            visitedLinks += 1
            crawlerOutput[seedLink]['frontier'].add(anchor['href'])
          else:               # com restrições do robots
            for d in disallow:
              if d not in anchor['href']:
                visitedLinks += 1
                crawlerOutput[seedLink]['frontier'].add(anchor['href'])

      # heuristica para cada seed
      newFrontier = []
      relevantLinks = 0

      for l in crawlerOutput[seedLink]['frontier']:
        value = 1

        for heu in heuristic:
          if heu['key'] in l:
            value += heu['weight']
        
        if value > 1:
          relevantLinks += 1

        newFrontier.append({
          'link': l,
          'weight': value
        }) 
      
      crawlerOutput[seedLink]['frontier'] = newFrontier
      crawlerOutput[seedLink]['visited_links'] = visitedLinks
      crawlerOutput[seedLink]['relevant_links'] = relevantLinks
      if visitedLinks != 0:
        crawlerOutput[seedLink]['harvest_ratio'] = relevantLinks/visitedLinks

# Crawler Thread Init.
def crawlerInit():
  for link in frontier:
    crawlerOutput[link] = {
      'visited_links': 0,
      'relevant_links': 0,
      'harvest_ratio': 0,
      'frontier': set(),
      'thread': Thread(target=Crawler, args=[link])._name
    }
    threads.append(Thread(target=Crawler, args=[link]))

  frontier.clear()

  for t in threads:
    t.start()

  for t in threads:
    t.join()

# iniciando o crawler
crawlerInit()


totalLinks = []

# analisando os dados coletados
for c in crawlerOutput:
  crawledPages += crawlerOutput[c]['visited_links']
  relevantPages += crawlerOutput[c]['relevant_links']
  sortedFrontier = sorted(crawlerOutput[c]['frontier'], key=lambda k: k['weight'], reverse=True)
  crawlerOutput[c]['frontier'] = sortedFrontier
  totalLinks += sortedFrontier


#reinicia a busca
if crawledPages < MAX_PAGES:
  sortTotal = sorted(totalLinks, key=lambda k: k['weight'], reverse=True)
  for i in range(10):
    frontier.append(sortTotal[i])

  crawlerInit()
  

print("total_harvest_ratio = "+ str(relevantPages/crawledPages))
print("crawledLinks = "+ str(crawlerOutput))
