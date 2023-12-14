from bs4 import BeautifulSoup
import requests
import pandas as pd

class MetacriticScraperGames:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.games = {}
        self.base_url = "https://www.metacritic.com/browse/game/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"

        }
# We should add half, because metacritic webpage divided into 2
    def get_game(self,half, page_number,game_number):
        full_url = f"{self.base_url}?releaseYearMin={self.start_date}&releaseYearMax={self.end_date}&page={page_number}"
        response = requests.get(url=full_url, headers=self.headers)
        
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

    def get_games(self,page_number):
        for page_number in range(1, page_number+1):
            for half in range(1,3):
                for game_number in range(0,12):
                    game, game_link = self.get_game(half,page_number,game_number)
                    self.games.update({ game : game_link })
        new_base_url = 'https://www.metacritic.com'
        my_dictionary = {key: f'{new_base_url}{value}' for key, value in self.games.items()}

        return my_dictionary
    
    def get_games_informations(self,page_number):
        dict = self.get_games(page_number)
        for key, value in dict.items():
            response = requests.get(url=str(value), headers=self.headers)
            
            if not response.ok:
                print(f"Error: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, "html5lib")   
            Name = key 

            #Maybe you should get to review count and details like positive review count, mixed review count and negative review count.
            Released_on = soup.select_one(" div.g-text-xsmall > span.u-text-uppercase").text.strip()
            MetaScore = soup.select_one(".c-productScoreInfo_scoreNumber > div > div > span").text.strip()
            UserScore = soup.find_all(class_="c-productScoreInfo_scoreNumber")[1].select_one("div > div > span").text.strip()
            
            CriticReviewsHead1 =  soup.select_one(".c-reviewsSection_carousel > .c-reviewsSection_carousel_item:nth-child(1) > div > div.c-siteReview_main.g-inner-spacing-medium > div.c-siteReviewHeader.u-grid.g-outer-spacing-bottom-medium.u-flexbox-alignCenter > div.c-siteReviewHeader_publisherLogo > a").text.strip()
            CriticReviewsHead2 =  soup.select_one(".c-reviewsSection_carousel > .c-reviewsSection_carousel_item:nth-child(2) > div > div.c-siteReview_main.g-inner-spacing-medium > div.c-siteReviewHeader.u-grid.g-outer-spacing-bottom-medium.u-flexbox-alignCenter > div.c-siteReviewHeader_publisherLogo > a").text.strip()
            CriticReviewsHead3 = soup.select_one(".c-reviewsSection_carousel:nth-child(1) > .c-reviewsSection_carousel_item:nth-child(1) > div > div.c-siteReview_main.g-inner-spacing-medium > div.c-siteReviewHeader.u-grid.g-outer-spacing-bottom-medium.u-flexbox-alignCenter > div.c-siteReviewHeader_publisherLogo > a").text.strip()
            CriticReviewsHead4 = soup.select_one(".c-reviewsSection_carousel:nth-child(1) > .c-reviewsSection_carousel_item:nth-child(2) > div > div.c-siteReview_main.g-inner-spacing-medium > div.c-siteReviewHeader.u-grid.g-outer-spacing-bottom-medium.u-flexbox-alignCenter > div.c-siteReviewHeader_publisherLogo > a").text.strip()
            CriticReviewsHead5 = soup.select_one(".c-reviewsSection_carousel:nth-child(1) > .c-reviewsSection_carousel_item:nth-child(3) > div > div.c-siteReview_main.g-inner-spacing-medium > div.c-siteReviewHeader.u-grid.g-outer-spacing-bottom-medium.u-flexbox-alignCenter > div.c-siteReviewHeader_publisherLogo > a").text.strip()
            CriticReviewsHead6 = soup.select_one(".c-reviewsSection_carousel:nth-child(1) > .c-reviewsSection_carousel_item:nth-child(4) > div > div.c-siteReview_main.g-inner-spacing-medium > div.c-siteReviewHeader.u-grid.g-outer-spacing-bottom-medium.u-flexbox-alignCenter > div.c-siteReviewHeader_publisherLogo > a").text.strip()
            CriticReviewsHead7 = soup.select_one(".c-reviewsSection_carousel:nth-child(1) > .c-reviewsSection_carousel_item:nth-child(5) > div > div.c-siteReview_main.g-inner-spacing-medium > div.c-siteReviewHeader.u-grid.g-outer-spacing-bottom-medium.u-flexbox-alignCenter > div.c-siteReviewHeader_publisherLogo > a").text.strip()
            # You can get to review point as you want
            CriticReviews1 =  soup.select_one(".c-siteReview_main > div:nth-child(2) > div > span").text.strip()
            CriticReviews2 =  soup.select_one(".c-reviewsSection_carousel > div:nth-child(2) .c-siteReview_main > div:nth-child(2) > div > span").text.strip()
            CriticReviews3 =  soup.select_one("div:nth-child(4) > div > div:nth-child(6) > div > div.c-reviewsSection_carousel > div:nth-child(1) > div > div.c-siteReview_main > div:nth-child(2) > div > span").text.strip()
            CriticReviews4 =  soup.select_one("div:nth-child(4) > div > div:nth-child(6) > div > div.c-reviewsSection_carousel > div:nth-child(2) > div > div.c-siteReview_main > div:nth-child(2) > div > span").text.strip()
            CriticReviews5 =  soup.select_one("div:nth-child(4) > div > div:nth-child(6) > div > div.c-reviewsSection_carousel > div:nth-child(3) > div > div.c-siteReview_main > div:nth-child(2) > div > span").text.strip()
            CriticReviews6 =  soup.select_one("div:nth-child(4) > div > div:nth-child(6) > div > div.c-reviewsSection_carousel > div:nth-child(4) > div > div.c-siteReview_main > div:nth-child(2) > div > span").text.strip()
            CriticReviews7 =  soup.select_one("div:nth-child(4) > div > div:nth-child(6) > div > div.c-reviewsSection_carousel > div:nth-child(5) > div > div.c-siteReview_main > div:nth-child(2) > div > span").text.strip()

            UserReviewsHead1 = soup.select_one("div:nth-child(4) > div > div:nth-child(4) > div > div:nth-child(2) > div > div:nth-child(1) .c-siteReviewHeader > a").text.strip()
            UserReviewsHead2 = soup.select_one("div:nth-child(4) > div > div:nth-child(4) > div > div:nth-child(2) > div > div:nth-child(2) .c-siteReviewHeader > a").text.strip()
            UserReviewsHead3 = soup.select_one("div:nth-child(4) > div > div:nth-child(7) > div > .c-reviewsSection_carousel > div:nth-child(1) .c-siteReviewHeader > a").text.strip()
            UserReviewsHead4 = soup.select_one("div:nth-child(4) > div > div:nth-child(7) > div > .c-reviewsSection_carousel > div:nth-child(2) .c-siteReviewHeader > a").text.strip()
            UserReviewsHead5 = soup.select_one("div:nth-child(4) > div > div:nth-child(7) > div > .c-reviewsSection_carousel > div:nth-child(3) .c-siteReviewHeader > a").text.strip()
            UserReviewsHead6 = soup.select_one("div:nth-child(4) > div > div:nth-child(7) > div > .c-reviewsSection_carousel > div:nth-child(4) .c-siteReviewHeader > a").text.strip()
            UserReviewsHead7 = soup.select_one("div:nth-child(4) > div > div:nth-child(7) > div > .c-reviewsSection_carousel > div:nth-child(5) .c-siteReviewHeader > a").text.strip()
            
            # You can get to review point as you want
            UserReviews1 = soup.select_one("div:nth-child(4) > div > div:nth-child(4) > div > div:nth-child(2) > div > div:nth-child(1) .c-siteReview_main > div:nth-child(2) > div > span").text.strip()
            UserReviews2 = soup.select_one("div:nth-child(4) > div > div:nth-child(4) > div > div:nth-child(2) > div > div:nth-child(2) > div > .c-siteReview_main > div:nth-child(2) > div > span").text.strip()
            UserReviews3 = soup.select_one("div:nth-child(4) > div > div:nth-child(7) .c-siteReview_main > div:nth-child(2) > div > span").text.strip()
            UserReviews4 = soup.select_one("div:nth-child(4) > div > div:nth-child(7) > div > div.c-reviewsSection_carousel > div:nth-child(2) > div > div.c-siteReview_main.g-inner-spacing-medium > div:nth-child(2) > div > span").text.strip()
            UserReviews5 = soup.select_one("div:nth-child(4) > div > div:nth-child(7) > div > div.c-reviewsSection_carousel > div:nth-child(3) > div > div.c-siteReview_main.g-inner-spacing-medium > div:nth-child(2) > div > span").text.strip()
            UserReviews6 = soup.select_one("div:nth-child(4) > div > div:nth-child(7) > div > div.c-reviewsSection_carousel > div:nth-child(4) > div > div.c-siteReview_main.g-inner-spacing-medium > div:nth-child(2) > div > span").text.strip()
            UserReviews7 = soup.select_one("div:nth-child(4) > div > div:nth-child(7) > div > div.c-reviewsSection_carousel > div:nth-child(5) > div > div.c-siteReview_main.g-inner-spacing-medium > div:nth-child(2) > div > span").text.strip()
            

            GameSummary = soup.find('meta', attrs={'name': 'description'}).get("content")
            print(GameSummary)
            
# Example usage
scraper = MetacriticScraperGames("1900", "2023")

"""
# Get games from all pages
games = {}
for page_number in range(1, 20):
    for half in range(1,3):
        for game_number in range(0,12):
            game, game_link = scraper.get_games(half,page_number,game_number)
            games.update({ game : game_link })
"""
games = scraper.get_games_informations(1)
print(games)

