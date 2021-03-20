from bs4 import BeautifulSoup

from threading import Thread
import requests
import configs
import re

MAX_PAGES = 500

threads = []
frontier = set()

def isHtml(url):
  head = requests.head(url)
  return "text/html" in head.headers['content-type']

def disallowUrls(url):
  data = []
  robots = requests.get(url + '/robots.txt')

  if robots.status_code == requests.codes.ok:
    for line in robots.content.decode('utf-8').split('\n'):
      if(line.startswith('Disallow')):
        data.append(line.split(': ')[1])
  return data

def Crawler(seedLink, heuristic=False):
    disallow = disallowUrls(seedLink)

    if isHtml(seedLink):
      page = requests.get(seedLink, headers=configs.agent, timeout=5)
      soup = BeautifulSoup(page.content, 'lxml')

      #pega apenas urls permitidas de acordo com o robots.txt
      for anchor in soup.find_all('a', href=True):
        if anchor['href'].startswith('http'):
          frontier.add(anchor['href'])

# Crawler Thread Init.
for instance in configs.links:
  threads.append(Thread(target=Crawler, args=[instance, False]))

for t in threads:
  t.start()

for t in threads:
  t.join()

print("crawled_links = "+ str(list(frontier)))