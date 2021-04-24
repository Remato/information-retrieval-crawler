import os
import json
from bs4 import BeautifulSoup


class Wrapper:

    @staticmethod
    def process_espn(page):
        altura = ''
        peso = ''
        gols = ''
        assistencias = ''
        data_nascimento = ''

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
                'assistencias': assistencias
                }

    @staticmethod
    def process():
        directory = '../data'
        stats = []
        for file in os.listdir(directory):
            with open(directory + '/' + file, encoding='utf-8') as json_file:
                json_array = json.load(json_file)
                for page in json_array:
                    if page['status'] == 'True':
                        if 'espn' in file:
                            espn_player_stats = Wrapper.process_espn(page['content'])
                            stats.append(espn_player_stats)
        print(stats)
