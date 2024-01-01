from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
import time
import random
from ScrapingMetacriticGames import MetacriticScraperGames

class MetacriticScraperGamesRecommendation(MetacriticScraperGames):
    def __init__(self, start_date, end_date,proxy_file=None):
        self.start_date = start_date
        self.end_date = end_date
        self.games = {}
        self.start_time = time.time()
        self.base_url = "https://www.metacritic.com/browse/game/"
        self.proxies = self.load_proxies(proxy_file) if proxy_file else None
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"

        }


    
    def get_games_recommendations(self,page_number_start,page_number_end):
        try:
            dict = self.get_games(page_number_start,page_number_end)
            count = 0 
            GamesRecommendations = {}
            for key, value in dict.items():
                response = self.get_request(value)
                count += 1 
                if not response.ok:
                    print(f"Error: {response.status_code}")
                    return None
                
                soup = BeautifulSoup(response.content, "html5lib")   
                GameName = key
                elements = soup.find_all("h3", class_="c-globalProductCard_title g-color-gray80 g-text-xsmall")
                RecommendationGames = [element.text.strip().lower() for element in elements if element]
                
                GamesRecommendations[GameName] = RecommendationGames
                print(GamesRecommendations)
            return GamesRecommendations
        except Exception as e:
            print(f"Bir hata oluştu {e}")
        finally:
            self.calculate_total_time()


scraper = MetacriticScraperGamesRecommendation("1900", "2023",None)
games = scraper.get_games_recommendations(1,2)


