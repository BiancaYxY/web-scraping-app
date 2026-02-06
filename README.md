#  NBA Players Web Scraping App

A Python-based web scraping application that extracts NBA player data from the official NBA website, saves it locally as a CSV file, and stores it in a MongoDB Atlas database.

The project uses Selenium to handle dynamic (React-rendered) content, BeautifulSoup for HTML parsing, Pandas for data handling, and PyMongo for database integration.

---

##  Features

-  Scrapes player data from https://www.nba.com/players
-  Handles dynamic pages using Selenium (headless Chrome)
-  Extracts table data with BeautifulSoup
-  Saves results to `nba_players.csv`
-  Uploads data to MongoDB Atlas
-  Adds metadata (`scraped_at`, `source`, `page`) to each record
