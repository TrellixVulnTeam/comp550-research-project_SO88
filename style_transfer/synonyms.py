import requests
from bs4 import BeautifulSoup

# Reference: https://stackoverflow.com/questions/53255814/web-scraping-based-on-query-terms-from-thesaurus-com

def get_synonyms(word):
    response = requests.get(f"http://www.thesaurus.com/browse/{word}")
    soup = BeautifulSoup(response.text, "html.parser")
    
    no_results = soup.find('div', {'class': 'no-results-title'})
    if no_results:
        return []
    
    synonyms_section = soup.find('ul', {'class': 'et6tpn80'})
    
    return [span.text for span in synonyms_section.findAll('span')]