from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
import time
import random

class MetacriticScraperGames:
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

    def load_proxies(self, filename):
        with open(filename, 'r') as file:
            return [line.strip() for line in file]
        
    def get_request(self, url, max_retries=10):
        retry_count = 0
        while retry_count < max_retries:
            try:
                if self.proxies:
                    proxy = random.choice(self.proxies)
                    response = self.session.get(url, headers=self.headers, proxies={"http": proxy, "https": proxy}, timeout=5)
                else:
                    response = self.session.get(url, headers=self.headers)  # Session nesnesiyle istek yapılıyor.
                return response
            except requests.exceptions.RequestException as e:
                print(f"Request error with proxy {proxy}: {e}")
                retry_count += 1
        print("Max retries exceeded.")
        return None
        
# We should add half, because metacritic webpage divided into 2
    def get_game(self,half, page_number,game_number):
        full_url = f"{self.base_url}?releaseYearMin={self.start_date}&releaseYearMax={self.end_date}&page={page_number}"
        response = self.get_request(full_url)
        
        if not response.ok:
            print(f"Error: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.content, "html5lib")
        if half == 1:
            table = soup.find(
                "div", attrs={"class": "c-productListings_grid g-grid-container u-grid-columns g-inner-spacing-bottom-large"}
            )
        else:
            table = soup.find(
                "div", attrs={"class": "c-productListings_grid g-grid-container u-grid-columns g-inner-spacing-bottom-large g-inner-spacing-top-large"})
        games = table.find_all(
            "div", attrs={"class": "c-finderProductCard c-finderProductCard-game"}
        )
        game_link = games[game_number].a["href"]
        game = game_link.split("/")[2].replace("-"," ")

        

        return game,game_link

    
    def save_to_csv(self, data, filename="metacritic_games.csv"):
        df = pd.DataFrame(list(data.items()), columns=["Game", "URL"])
        df.to_csv(filename, index=False)
        print(f"Data has been saved to {filename}")

    def get_games(self,page_number_start,page_number_end):
        counter = 0
        for page_number_end in range(page_number_start, page_number_end):
            for half in range(1,3):
                for game_number in range(0,12):
                    game, game_link = self.get_game(half,page_number_end,game_number)
                    self.games.update({ game : game_link })
                    counter += 1
                    print(f"Counter: {counter}")
            time.sleep(random.uniform(0.5, 2))
        new_base_url = 'https://www.metacritic.com'
        my_dictionary = {key: f'{new_base_url}{value}' for key, value in self.games.items()}

        return my_dictionary
    
    def control_selector(self,soup, selector):
        element = soup.select_one(selector)
        return element.text.strip().replace("\n", " ") if element else None

    def calculate_total_time(self):
        end_time = time.time()
        total_time = end_time - self.start_time
        print(f"Tüm işlemlerin toplam süresi: {total_time:.2f} saniye")


    
    def get_games_informations(self,page_number_start,page_number_end):
        try:
            dict = self.get_games(page_number_start,page_number_end)
            count = 0 
            GameInformations = {}
            for key, value in dict.items():
                response = self.get_request(value)
                count += 1 
                if not response.ok:
                    print(f"Error: {response.status_code}")
                    return None
                
                soup = BeautifulSoup(response.content, "html5lib")   
                GameName = key
                Genre = self.control_selector(soup,".c-gameDetails a > span")
                #Maybe you should get to review count and details like positive review count, mixed review count and negative review count.
                Released_on = self.control_selector(soup," div.g-text-xsmall > span.u-text-uppercase")
                if Released_on != None:
                    date_obj = datetime.strptime(Released_on, '%b %d, %Y')
                    formatted_date = date_obj.strftime('%Y-%m-%d')
                else:
                    formatted_date = "2010-01-01"
                try:
                    MetaScore = self.control_selector(soup,".c-productScoreInfo_scoreNumber > div > div > span")
                    if MetaScore.lower() == "tbd":
                        MetaScore = 0                
                except Exception as e:
                    MetaScore = 0
                    print(f"{GameName}: {e}")

                try:
                    UserScore = self.control_selector(soup.find_all(class_="c-productScoreInfo_scoreNumber")[1], "div > div > span")
                    if UserScore.lower() == "tbd":
                        UserScore = 0
                except Exception as e:
                    UserScore = 0
                    print(f"{GameName}: {e}")
                print(UserScore)
                #__layout > div > div.c-layoutDefault_page > div.c-pageProductGame > div:nth-child(1) > div > div > div.c-productHero_player-scoreInfo.u-grid.g-grid-container > div.c-productHero_score-container.u-flexbox.u-flexbox-column.g-bg-white > div.c-productHero_scoreInfo.g-inner-spacing-top-medium.g-outer-spacing-bottom-medium.g-outer-spacing-top-medium > div.c-productScoreInfo.u-clearfix > div.c-productScoreInfo_scoreContent.u-flexbox.u-flexbox-alignCenter.u-flexbox-justifyFlexEnd.g-width-100.u-flexbox-nowrap > div.c-productScoreInfo_scoreNumber.u-float-right > div > div > span
                try:
                    GameSummary = soup.find('meta', attrs={'name': 'description'}).get("content").replace("\n"," ")
                except AttributeError:
                    GameSummary = "  "


                CriticReviews1 = self.control_selector(soup, ".c-siteReview_main > div:nth-child(2) > div > span")
                CriticReviews2 = self.control_selector(soup, ".c-reviewsSection_carousel > div:nth-child(2) .c-siteReview_main > div:nth-child(2) > div > span")
                CriticReviews3 = self.control_selector(soup, "div:nth-child(4) > div > div:nth-child(6) > div > div.c-reviewsSection_carousel > div:nth-child(1) > div > div.c-siteReview_main > div:nth-child(2) > div > span")
                CriticReviews4 = self.control_selector(soup, "div:nth-child(4) > div > div:nth-child(6) > div > div.c-reviewsSection_carousel > div:nth-child(2) > div > div.c-siteReview_main > div:nth-child(2) > div > span")
                CriticReviews5 = self.control_selector(soup, "div:nth-child(4) > div > div:nth-child(6) > div > div.c-reviewsSection_carousel > div:nth-child(3) > div > div.c-siteReview_main > div:nth-child(2) > div > span")
                CriticReviews6 = self.control_selector(soup, "div:nth-child(4) > div > div:nth-child(6) > div > div.c-reviewsSection_carousel > div:nth-child(4) > div > div.c-siteReview_main > div:nth-child(2) > div > span")
                CriticReviews7 = self.control_selector(soup, "div:nth-child(4) > div > div:nth-child(6) > div > div.c-reviewsSection_carousel > div:nth-child(5) > div > div.c-siteReview_main > div:nth-child(2) > div > span")

                UserReviews1 = self.control_selector(soup, "div:nth-child(4) > div > div:nth-child(4) > div > div:nth-child(2) > div > div:nth-child(1) .c-siteReview_main > div:nth-child(2) > div > span")
                UserReviews2 = self.control_selector(soup, "div:nth-child(4) > div > div:nth-child(4) > div > div:nth-child(2) > div > div:nth-child(2) > div > .c-siteReview_main > div:nth-child(2) > div > span")
                UserReviews3 = self.control_selector(soup, "div:nth-child(4) > div > div:nth-child(7) .c-siteReview_main > div:nth-child(2) > div > span")
                UserReviews4 = self.control_selector(soup, "div:nth-child(4) > div > div:nth-child(7) > div > div.c-reviewsSection_carousel > div:nth-child(2) > div > div.c-siteReview_main.g-inner-spacing-medium > div:nth-child(2) > div > span")
                UserReviews5 = self.control_selector(soup, "div:nth-child(4) > div > div:nth-child(7) > div > div.c-reviewsSection_carousel > div:nth-child(3) > div > div.c-siteReview_main.g-inner-spacing-medium > div:nth-child(2) > div > span")
                UserReviews6 = self.control_selector(soup, "div:nth-child(4) > div > div:nth-child(7) > div > div.c-reviewsSection_carousel > div:nth-child(4) > div > div.c-siteReview_main.g-inner-spacing-medium > div:nth-child(2) > div > span")
                UserReviews7 = self.control_selector(soup, "div:nth-child(4) > div > div:nth-child(7) > div > div.c-reviewsSection_carousel > div:nth-child(5) > div > div.c-siteReview_main.g-inner-spacing-medium > div:nth-child(2) > div > span")


                #CriticReviewsHead1 =  soup.select_one(".c-reviewsSection_carousel > .c-reviewsSection_carousel_item:nth-child(1) > div > div.c-siteReview_main.g-inner-spacing-medium > div.c-siteReviewHeader.u-grid.g-outer-spacing-bottom-medium.u-flexbox-alignCenter > div.c-siteReviewHeader_publisherLogo > a").text.strip()
                #CriticReviewsHead2 =  soup.select_one(".c-reviewsSection_carousel > .c-reviewsSection_carousel_item:nth-child(2) > div > div.c-siteReview_main.g-inner-spacing-medium > div.c-siteReviewHeader.u-grid.g-outer-spacing-bottom-medium.u-flexbox-alignCenter > div.c-siteReviewHeader_publisherLogo > a").text.strip()
                #CriticReviewsHead3 = soup.select_one(".c-reviewsSection_carousel:nth-child(1) > .c-reviewsSection_carousel_item:nth-child(1) > div > div.c-siteReview_main.g-inner-spacing-medium > div.c-siteReviewHeader.u-grid.g-outer-spacing-bottom-medium.u-flexbox-alignCenter > div.c-siteReviewHeader_publisherLogo > a").text.strip()
                #CriticReviewsHead4 = soup.select_one(".c-reviewsSection_carousel:nth-child(1) > .c-reviewsSection_carousel_item:nth-child(2) > div > div.c-siteReview_main.g-inner-spacing-medium > div.c-siteReviewHeader.u-grid.g-outer-spacing-bottom-medium.u-flexbox-alignCenter > div.c-siteReviewHeader_publisherLogo > a").text.strip()
                #CriticReviewsHead5 = soup.select_one(".c-reviewsSection_carousel:nth-child(1) > .c-reviewsSection_carousel_item:nth-child(3) > div > div.c-siteReview_main.g-inner-spacing-medium > div.c-siteReviewHeader.u-grid.g-outer-spacing-bottom-medium.u-flexbox-alignCenter > div.c-siteReviewHeader_publisherLogo > a").text.strip()
                #CriticReviewsHead6 = soup.select_one(".c-reviewsSection_carousel:nth-child(1) > .c-reviewsSection_carousel_item:nth-child(4) > div > div.c-siteReview_main.g-inner-spacing-medium > div.c-siteReviewHeader.u-grid.g-outer-spacing-bottom-medium.u-flexbox-alignCenter > div.c-siteReviewHeader_publisherLogo > a").text.strip()
                #CriticReviewsHead7 = soup.select_one(".c-reviewsSection_carousel:nth-child(1) > .c-reviewsSection_carousel_item:nth-child(5) > div > div.c-siteReview_main.g-inner-spacing-medium > div.c-siteReviewHeader.u-grid.g-outer-spacing-bottom-medium.u-flexbox-alignCenter > div.c-siteReviewHeader_publisherLogo > a").text.strip()
                # You can get to review point as you want
                """"
                CriticReviews1 =  soup.select_one(".c-siteReview_main > div:nth-child(2) > div > span").text.strip()
                CriticReviews2 =  soup.select_one(".c-reviewsSection_carousel > div:nth-child(2) .c-siteReview_main > div:nth-child(2) > div > span").text.strip()
                CriticReviews3 =  soup.select_one("div:nth-child(4) > div > div:nth-child(6) > div > div.c-reviewsSection_carousel > div:nth-child(1) > div > div.c-siteReview_main > div:nth-child(2) > div > span").text.strip().replace("\n"," ")
                CriticReviews4 =  soup.select_one("div:nth-child(4) > div > div:nth-child(6) > div > div.c-reviewsSection_carousel > div:nth-child(2) > div > div.c-siteReview_main > div:nth-child(2) > div > span").text.strip().replace("\n"," ")
                CriticReviews5 =  soup.select_one("div:nth-child(4) > div > div:nth-child(6) > div > div.c-reviewsSection_carousel > div:nth-child(3) > div > div.c-siteReview_main > div:nth-child(2) > div > span").text.strip().replace("\n"," ")
                CriticReviews6 =  soup.select_one("div:nth-child(4) > div > div:nth-child(6) > div > div.c-reviewsSection_carousel > div:nth-child(4) > div > div.c-siteReview_main > div:nth-child(2) > div > span").text.strip().replace("\n"," ")
                CriticReviews7 =  soup.select_one("div:nth-child(4) > div > div:nth-child(6) > div > div.c-reviewsSection_carousel > div:nth-child(5) > div > div.c-siteReview_main > div:nth-child(2) > div > span").text.strip().replace("\n"," ")

                #UserReviewsHead1 = soup.select_one("div:nth-child(4) > div > div:nth-child(4) > div > div:nth-child(2) > div > div:nth-child(1) .c-siteReviewHeader > a").text.strip()
                #UserReviewsHead2 = soup.select_one("div:nth-child(4) > div > div:nth-child(4) > div > div:nth-child(2) > div > div:nth-child(2) .c-siteReviewHeader > a").text.strip()
                #UserReviewsHead3 = soup.select_one("div:nth-child(4) > div > div:nth-child(7) > div > .c-reviewsSection_carousel > div:nth-child(1) .c-siteReviewHeader > a").text.strip()
                #UserReviewsHead4 = soup.select_one("div:nth-child(4) > div > div:nth-child(7) > div > .c-reviewsSection_carousel > div:nth-child(2) .c-siteReviewHeader > a").text.strip()
                #UserReviewsHead5 = soup.select_one("div:nth-child(4) > div > div:nth-child(7) > div > .c-reviewsSection_carousel > div:nth-child(3) .c-siteReviewHeader > a").text.strip()
                #UserReviewsHead6 = soup.select_one("div:nth-child(4) > div > div:nth-child(7) > div > .c-reviewsSection_carousel > div:nth-child(4) .c-siteReviewHeader > a").text.strip()
                #UserReviewsHead7 = soup.select_one("div:nth-child(4) > div > div:nth-child(7) > div > .c-reviewsSection_carousel > div:nth-child(5) .c-siteReviewHeader > a").text.strip()
                
                # You can get to review point as you want
                UserReviews1 = soup.select_one("div:nth-child(4) > div > div:nth-child(4) > div > div:nth-child(2) > div > div:nth-child(1) .c-siteReview_main > div:nth-child(2) > div > span").text.strip().replace("\n"," ")
                UserReviews2 = soup.select_one("div:nth-child(4) > div > div:nth-child(4) > div > div:nth-child(2) > div > div:nth-child(2) > div > .c-siteReview_main > div:nth-child(2) > div > span").text.strip().replace("\n"," ")
                UserReviews3 = soup.select_one("div:nth-child(4) > div > div:nth-child(7) .c-siteReview_main > div:nth-child(2) > div > span").text.strip().replace("\n"," ")
                UserReviews4 = soup.select_one("div:nth-child(4) > div > div:nth-child(7) > div > div.c-reviewsSection_carousel > div:nth-child(2) > div > div.c-siteReview_main.g-inner-spacing-medium > div:nth-child(2) > div > span").text.strip().replace("\n"," ")
                UserReviews5 = soup.select_one("div:nth-child(4) > div > div:nth-child(7) > div > div.c-reviewsSection_carousel > div:nth-child(3) > div > div.c-siteReview_main.g-inner-spacing-medium > div:nth-child(2) > div > span").text.strip().replace("\n"," ")
                UserReviews6 = soup.select_one("div:nth-child(4) > div > div:nth-child(7) > div > div.c-reviewsSection_carousel > div:nth-child(4) > div > div.c-siteReview_main.g-inner-spacing-medium > div:nth-child(2) > div > span").text.strip().replace("\n"," ")
                UserReviews7 = soup.select_one("div:nth-child(4) > div > div:nth-child(7) > div > div.c-reviewsSection_carousel > div:nth-child(5) > div > div.c-siteReview_main.g-inner-spacing-medium > div:nth-child(2) > div > span").text.strip().replace("\n"," ")
                """
                GameInformations[GameName] = {"Genre":Genre,"Released_on":formatted_date,"MetaScore":MetaScore,"UserScore":UserScore,"GameSummary":GameSummary
                                ,"CriticReviews1":CriticReviews1
                                ,"CriticReviews2":CriticReviews2,"CriticReviews3":CriticReviews3,"CriticReviews4":CriticReviews4
                                ,"CriticReviews5":CriticReviews5,"CriticReviews6":CriticReviews6,"CriticReviews7":CriticReviews7
                                ,"UserReviews1":UserReviews1,"UserReviews2":UserReviews2,"UserReviews3":UserReviews3
                                ,"UserReviews4":UserReviews4,"UserReviews5":UserReviews5,"UserReviews6":UserReviews6
                                ,"UserReviews7":UserReviews7} 
                time.sleep(random.uniform(0.5, 2))
                print(f"DONE:{count}:",GameName)
            return GameInformations
        except Exception as e:
            print(f"Bir hata oluştu {e}")
        finally:
            self.calculate_total_time()
# Example usage


"""
# Get games from all pages
games = {}
for page_number in range(1, 20):
    for half in range(1,3):
        for game_number in range(0,12):
            game, game_link = scraper.get_games(half,page_number,game_number)
            games.update({ game : game_link })
"""
"""scraper = MetacriticScraperGames("1900", "2023",None)
games = scraper.get_games_informations(16,17)"""
