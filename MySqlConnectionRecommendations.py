import mysql.connector
import ScrapingMetacriticRecomendations

scraper = ScrapingMetacriticRecomendations.MetacriticScraperGamesRecommendation("1900", "2023",None)
GamesRecommendations = scraper.get_games_recommendations(225, 250)

try:
    # mysql -u root -p (docker da mysqli başlatma)
    # Veritabanı bağlantısını kurun
    conn = mysql.connector.connect(
      host="localhost",
      user="GameReco",
      password="159876432",
      database="my_database"
    )
    cursor = conn.cursor()
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS games_recommendations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            GameName VARCHAR(255),
            Genre TEXT, 
            Released_on DATE,
            MetaScore INT,
            UserScore FLOAT,
            GameSummary TEXT
        )
        """)
    except mysql.connector.Error as e:
        print(f"{e}")