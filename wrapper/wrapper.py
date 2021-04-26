import os
import json
import re
from bs4 import BeautifulSoup


class Wrapper:

    @staticmethod
    def process_text(text):
        # Removendo Tags e conteúdos do HTML
        soup = BeautifulSoup(text)
        text = soup.get_text()
        return text

    @staticmethod
    def process_espn(page):
        altura = ''
        peso = ''
        gols = ''
        assistencias = ''
        data_nascimento = ''
        text = Wrapper.process_text(page)

        soup = BeautifulSoup(page, "html")
        nome = soup.find('title').get_text(strip=True).split(" Estatísticas, Notícias, Biografia | ESPN")[0]
        player_header = soup.find(class_="PlayerHeader__Bio_List")

        for li in player_header:
            ttu_text = li.find(class_="ttu").get_text(strip=True)
            if ttu_text == 'A/P':
                altura_peso = li.find(class_="fw-medium clr-black").find('div').get_text(strip=True).split(',')
                altura = altura_peso[0]
                peso = altura_peso[1]

        for li in player_header:
            ttu_text = li.find(class_="ttu").get_text(strip=True)
            if ttu_text == 'DOB':
                dob_idade = li.find(class_="fw-medium clr-black").find('div').get_text(strip=True).split(' ')
                data_nascimento = dob_idade[0]

        statBlock = soup.find(class_="StatBlock__Content")

        for li in statBlock:
            label = li.find(class_='StatBlockInner__Label')
            if label['aria-label'] == 'Total de gols':
                gols = li.find(class_='StatBlockInner__Value').get_text(strip=True)
            if label['aria-label'] == 'assistências':
                assistencias = li.find(class_='StatBlockInner__Value').get_text(strip=True)

        return {'nome': nome,
                'altura': altura,
                'peso': peso,
                'data_nascimento': data_nascimento,
                'gols': gols,
                'assistencias': assistencias,
                'pagina': text
                }

    @staticmethod
    def process_sambafoot(page):
        altura = ''
        peso = ''
        gols = ''
        assistencias = ''
        data_nascimento = ''
        text = Wrapper.process_text(page)

        soup = BeautifulSoup(page, "html")
        nome = soup.find('title').get_text(strip=True).split(" | Perfil, Estatísticas, Carreira & Notícias 2020 | Sambafoot")[0]
        age = soup.find("td", class_="age").span.get_text(strip=True)
        data_nascimento = age[age.find("(")+1:age.find(")")]
        altura = soup.find("div", class_="height").span.get_text(strip=True)
        peso = soup.find("div", class_="weight").span.get_text(strip=True)
        gols = soup.find("div", class_="counter goals-scored").span.get_text(strip=True)
        assistencias = soup.find("div", class_="counter assists").span.get_text(strip=True)

        return {'nome': nome,
                'altura': altura,
                'peso': peso,
                'data_nascimento': data_nascimento,
                'gols': gols,
                'assistencias': assistencias,
                'pagina': text
                }

    @staticmethod
    def process():
        directory = '../data'
        stats = []
        for file in os.listdir(directory):
            if file in ["sambafoot.json", "espn.json", "ogol.json"]:
                with open(directory + '/' + file, encoding='utf-8') as json_file:
                    json_array = json.load(json_file)
                    for page in json_array:
                        if page['status'] == 'True':
                            if 'espn' in file:
                                espn_player_stats = Wrapper.process_espn(page['content'])
                                stats.append(espn_player_stats)
                            if 'sambafoot' in file:
                                sambafoot_player_stats = Wrapper.process_sambafoot(page['content'])
                                stats.append(sambafoot_player_stats)
        with open("../data/wrapped.json", "w") as outfile:
            json.dump(stats, outfile)
