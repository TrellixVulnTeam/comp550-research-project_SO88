from bs4 import BeautifulSoup
import csv
import os
import requests

BASE_URL = "https://www.litcharts.com/shakescleare/shakespeare-translations"

DATASET_FILE = os.path.join('data', 'shakespeare', 'shakespeare_translation.csv')


def get_soup(url):
    page = requests.get(url)
    return BeautifulSoup(page.content, 'html.parser')


def get_play_titles():
    play_titles = []
    
    titles_soup = get_soup(BASE_URL)
    titles = titles_soup.find_all(class_='shakespeare-title')
    
    for title in titles:
        link = title.find('a')
        url = link['href']
        url_items = url.split('/')
        play_title = url_items[-1]
        play_titles.append(play_title)
        
    return play_titles


def get_scene_urls(play_title):
    scene_urls = []
    
    table_of_contents_soup = get_soup(f"{BASE_URL}/{play_title}")
    table_of_contents = table_of_contents_soup.find(id='intro')
    
    if not table_of_contents:
        return scene_urls
    
    links = table_of_contents.find_all('a')
    
    for link in links:
        url = link['href']
        url_items = url.split('/')
        scene = url_items[-1]
        scene_urls.append(f"{BASE_URL}/{play_title}/{scene}")
        
    return scene_urls


def add_lines(scene_soup, lines_dict, div_class):
    divs = scene_soup.find_all('div', {'class' : div_class})
    for div in divs:
        spans = div.find_all('span', {'class' : 'line-mapping'})
        for span in spans:
            data_id = span.get('data-id', None)
            if not data_id:
                continue
            
            if data_id in lines_dict:
                lines_dict[data_id] += span.text
            else:
                lines_dict[data_id] = span.text


original_dict = {}
modern_dict = {}

play_titles = get_play_titles()

for play_title in play_titles:
    scene_urls = get_scene_urls(play_title)
    
    for scene_url in scene_urls:
        print(scene_url)
        scene_soup = get_soup(scene_url)
        
        add_lines(scene_soup, original_dict, 'original-play')
        add_lines(scene_soup, modern_dict, 'modern-translation')


with open(DATASET_FILE, 'w', encoding='utf-8') as outputfile:
    writer = csv.writer(outputfile, delimiter='\t', lineterminator='\n')
    for data_id in original_dict:
        original = original_dict.get(data_id, None)
        modern = modern_dict.get(data_id, None)
        
        if original and modern:
            writer.writerow([modern, original])
    
        
        
# for play_title in get_play_titles():
# %%


# %%

#original_dict = {}
#modern_dict = {}

#
#def add_lines(page_soup, lines_dict, div_class):
#    divs = soup.find_all('div', {'class' : div_class})
#    for div in divs:
#        spans = div.find_all('span', {'class' : 'line-mapping'})
#        for span in spans:
#            data_id = span['data-id']
#            if data_id in lines_dict:
#                lines_dict[data_id] += span.text
#            else:
#                lines_dict[data_id] = span.text
#
#
#for play, acts in PLAYS.items():
#    for act_index, scene_count in enumerate(acts):
#        for scene_index in range(scene_count):
#            soup = get_page_soup(play, act_index, scene_index)
#            
#            add_lines(soup, original_dict, 'original-play')
#            add_lines(soup, modern_dict, 'modern-translation')
#
#with open('shakespeare_translation.csv', 'w', encoding='utf-8') as outputfile:
#    writer = csv.writer(outputfile, delimiter='\t', lineterminator='\n')
#    for data_id in original_dict:
#        original = original_dict[data_id]
#        modern = modern_dict[data_id]
#        writer.writerow([original, modern])