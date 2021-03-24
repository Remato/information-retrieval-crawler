import os
import re
import configs
from threading import Thread

# roda as threads do crawler para pegar os links
# os.system("python3 crawler.py > out.py")

import out

# visited_links = len(out.crawled_links)
# relevant_links = {}
# relevantFrontier = {}

# # cria heuristica para links
# for l in out.crawled_links:
#   value = 0
#   for heu in configs.heuristic:
#     if heu['key'] in l:
#       value += heu['weight']
#   if value > 0:
#     relevant_links[l] = value*100

# sorted_links = sorted(relevant_links.items(), key=lambda x: x[1], reverse=True)
# print(sorted_links)
# print(len(sorted_links), visited_links)