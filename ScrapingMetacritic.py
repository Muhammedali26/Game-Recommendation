from bs4 import BeautifulSoup
import requests
import pandas as pd

class MetacriticScraper:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.base_url = "https://www.metacritic.com/browse/game/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"

        }
# We should add half, because metacritic webpage divided into 2
    def get_games(self,half, page_number,game_number):
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

    def url_converter(self,dict):

        new_base_url = 'www.metacritic.com'
        my_dictionary = {key: f'{new_base_url}{value}' for key, value in dict.items()}

        return my_dictionary
    
    def save_to_csv(self, data, filename="metacritic_games.csv"):
        df = pd.DataFrame(list(data.items()), columns=["Game", "URL"])
        df.to_csv(filename, index=False)
        print(f"Data has been saved to {filename}")


# Example usage
scraper = MetacriticScraper("1900", "2023")

# Get games from all pages
games = {}
for page_number in range(1, 20):
    for half in range(1,3):
        for game_number in range(0,12):
            game, game_link = scraper.get_games(half,page_number,game_number)
            games.update({ game : game_link })

games_w_link = scraper.url_converter(games)
print(games_w_link)

# Save to CSV
scraper.save_to_csv(scraper.url_converter(games))