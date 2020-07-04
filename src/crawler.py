import os
import re
import sys
import urllib.request

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

FILE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION = requests.session()
BASE_URL = 'https://dark-netflix.fandom.com'

# List of characters to collect
characters_urls = ['/wiki/Daniel_Kahnwald', '/wiki/Hannah_Kahnwald', '/wiki/Ines_Kahnwald', '/wiki/Michael_Kahnwald',
                   '/wiki/Sebastian_Kr%C3%BCger', '/wiki/Sebastian_Kr%C3%BCger', '/wiki/Agnes_Nielsen', 
                   '/wiki/Jana_Nielsen', '/wiki/Katharina_Nielsen', '/wiki/Magnus_Nielsen', '/wiki/Martha_Nielsen', 
                   '/wiki/Mikkel_Nielsen', '/wiki/Tronte_Nielsen', '/wiki/Ulrich_Nielsen',
                   '/wiki/Mads_Nielsen', '/wiki/Bernd_Doppler', '/wiki/Charlotte_Doppler',
                   '/wiki/Elisabeth_Doppler', '/wiki/Franziska_Doppler', '/wiki/Greta_Doppler',
                   '/wiki/Helge_Doppler', '/wiki/Peter_Doppler', '/wiki/Erik_Obendorf',
                   '/wiki/Silja_Tiedemann', '/wiki/H.G._Tannhaus', '/wiki/The_Unknown',
                   '/wiki/Aleksander_Tiedemann', '/wiki/Bartosz_Tiedemann', '/wiki/Claudia_Tiedemann',
                   '/wiki/Doris_Tiedemann', '/wiki/Egon_Tiedemann', '/wiki/Regina_Tiedemann',
                   '/wiki/Jonas_Kahnwald', '/wiki/Hanno_Tauber']
relationships = []
thumbnails = []

# For each character, collect its relative's data
for character in tqdm(characters_urls):
    char_page = SESSION.get(BASE_URL+character)
    bs = BeautifulSoup(char_page.content, 'html.parser')

    # Collecting character's thumbnail
    character_name = re.sub(r'(\_|\/wiki\/)', ' ', character).strip()
    character_thumbnail = bs.find(class_='pi-image-thumbnail')['src']
    thumbnails.append({ 'character': character_name, 'thumbnail_url': character_thumbnail })
    
    # Downloading thumbnail
    urllib.request.urlretrieve(character_thumbnail, 'data/img/characters/{}'.format(character_name))

    # Collecting Family board
    char_family_info = bs.find(attrs={"data-source": "Family"}).find_all(class_='pi-data-value pi-font')
    
    # For each relative, collect her data
    for idx, relative in enumerate(zip(char_family_info[0].find_all('a'), char_family_info[0].find_all('small'))):
        relative_data = {}
        relative_data['character'] = character_name
        relative_data['relative'] = relative[0].text.strip()
        relative_data['url'] = relative[0].get('href')
        relative_data['relationship'] = re.sub(r'(\(|\)|\<small\>|\</small\>)', '', str(relative[1].text.strip()))
        
        relationships.append(relative_data)
    
# Generating dataset
characters_dataset = pd.DataFrame(relationships)
thumbnails_dataset = pd.DataFrame(thumbnails)

# Exporting
characters_dataset.to_csv(FILE_PATH + '/data/raw/characters_relationship.csv', index=False)
thumbnails_dataset.to_csv(FILE_PATH + '/data/raw/characters_thumbnails.csv', index=False)