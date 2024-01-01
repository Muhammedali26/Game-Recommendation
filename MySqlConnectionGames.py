import mysql.connector
import ScrapingMetacriticGames

scraper = ScrapingMetacriticGames.MetacriticScraperGames("1900", "2023",None)
GameInformations = scraper.get_games_informations(275, 300)
#En son 275 ve 300 arası yapıldı

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

    # Oyunlar için tablo oluşturun
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
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

    # Critic ve User Reviews için tablolar oluşturun
    try: 
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS critic_reviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            game_id INT,
            CriticReview TEXT,
            FOREIGN KEY (game_id) REFERENCES games(id)
        )
        """)
    except Exception as e:
        print(e)

    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_reviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            game_id INT,
            UserReview TEXT,
            FOREIGN KEY (game_id) REFERENCES games(id)
        )
        """)
    except Exception as e:
        print(e)

    # Oyun bilgilerini ve eleştirileri ekleyin
    for game_name, details in GameInformations.items():
        try:   
            # Önce oyunun veritabanında olup olmadığını kontrol edin
            cursor.execute("SELECT id FROM games WHERE GameName = %s", (game_name,))
            result = cursor.fetchone()
            
            if result:
                game_id = result[0]
            else:
                try:    
                    # Oyun veritabanında yoksa ekleyin
                    cursor.execute("INSERT INTO games (GameName, Genre, Released_on, MetaScore, UserScore, GameSummary) VALUES (%s, %s, %s, %s, %s, %s)", 
                                (game_name, details["Genre"], details["Released_on"], details["MetaScore"], details["UserScore"], details["GameSummary"]))
                    game_id = cursor.lastrowid
                except mysql.connector.Error as e:
                    print(f"Error inserting game {game_name}: {e}")

            # Critic Reviews ekleyin
            for i in range(1, 8):
                critic_review = details.get(f"CriticReviews{i}")
                if critic_review:
                    try:
                        # Bu critic review zaten var mı diye kontrol edin
                        cursor.execute("SELECT COUNT(*) FROM critic_reviews WHERE game_id = %s AND CriticReview = %s", (game_id, critic_review))
                        if cursor.fetchone()[0] == 0:
                            cursor.execute("INSERT INTO critic_reviews (game_id, CriticReview) VALUES (%s, %s)", (game_id, critic_review))
                    except mysql.connector.Error as e:
                        print(f"Error inserting critic review for game {game_name}: {e}")
            # User Reviews ekleyin
            for i in range(1, 8):
                user_review = details.get(f"UserReviews{i}")
                if user_review:
                    try:
                        # Bu user review zaten var mı diye kontrol edin
                        cursor.execute("SELECT COUNT(*) FROM user_reviews WHERE game_id = %s AND UserReview = %s", (game_id, user_review))
                        if cursor.fetchone()[0] == 0:
                            cursor.execute("INSERT INTO user_reviews (game_id, UserReview) VALUES (%s, %s)", (game_id, user_review))
                    except mysql.connector.Error as e:
                        print(f"Error inserting user review for game {game_name}: {e}")

        except mysql.connector.Error as e:
            print(f"Database error with game {game_name}: {e}")

    # Değişiklikleri veritabanına kaydedin
    conn.commit()
    print(cursor.rowcount, "records inserted.")

except mysql.connector.Error as e:
    print("Error:", e)

finally:
    if conn.is_connected():
        cursor.close()
        conn.close()
        print("MySQL connection is closed")
