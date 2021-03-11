from bs4 import BeautifulSoup

import requests
import configs
import re

def isHtml(url):
  head = requests.head(url)
  return "text/html" in head.headers["content-type"]

def disallowUrls(url):
  dataSet = []

  robots = requests.get(url+'/robots.txt')
  for line in robots.content.decode('utf-8').split('\n'):
    if(line.startswith('Disallow')):
      dataSet.append(line.split(': ')[1])
  return dataSet

def getAnchors(url):
  # Apenas baixa a pagina se for text/html
  if isHtml(url):
    disallowed = disallowUrls(url)
    page = requests.get(url, headers=configs.headers)
    soup = BeautifulSoup(page.content, 'lxml')
    anchors = set()

    #pega apenas urls permitidas de acordo com o robots.txt
    for anchor in soup.find_all('a', href=True):
      if anchor['href'].startswith('http'):
        for d in disallowed:
          if(re.search(d, anchor['href']) == None):
            anchors.add(anchor['href'])

    return anchors
  return []


#testando
print(getAnchors('https://www.magazineluiza.com.br'))