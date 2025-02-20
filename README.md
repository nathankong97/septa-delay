# 🚆 **SEPTA Delay Scraper**

SEPTA Delay Scraper is an open-source project that collects real-time train data from SEPTA's public APIs, including:
- **Train positions** (`train_view.py`)
- **Real-time trip updates** (`trip_updates.py`)
- **GTFS schedule updates** (`rrschedules.py`)

The scraper runs every **10 minutes (`rrschedules.py` runs once a day)** and stores data in **SQLite databases**.
This project is containerized with **Docker**, making deployment easy on any server.

---

## 🎯 **Features**

1. Scrapes real-time train positions
2. Stores historical delay data
3. Downloads & updates GTFS schedules
4. Fully automated with cron jobs inside Docker

---

## 📥 **Deployment Guide**

### 1. Install Docker & Docker Compose
Before running the scraper, install Docker:
```shell
sudo apt update && sudo apt install -y docker.io docker-compose
```
Verify installation:
```shell
docker --version
docker-compose --version
```
### 2. Clone the Repository
```shell
gh repo clone nathankong97/septa-delay
cd septa-delay
```
### 3. Build & Run the Scraper
```shell
docker-compose up -d --build
```
This will:
- Install dependencies
- Run scrapers every 10 minutes
- Store data in SQLite databases inside `data/`, json file inside `scraping/`
- Persist logs inside `logs/`

---

## 🐳 **Managing the Scraper**
### Check Running Containers
```shell
docker ps
```
### View Logs
```shell
docker logs septa_scraper
```
### Shutdown Docker
```shell
docker-compose down
```
### Access Container
```shell
docker exec -it septa_scraper
```

---

## 📁 **Project Structure**
```text
septa-delay/
├── data/                 # Stores SQLite databases (Persistent)
├── logs/                 # Stores log files
├── scraping/             # Stores json files
├── septa/
│   ├── core/
│   │   ├── database.py   # Database handling
│   │   ├── fetcher.py    # API fetch logic
│   │   ├── logger.py     # Logging system
│   ├── rrschedules.py   # Fetch GTFS data and final updates
│   ├── train_view.py    # Fetch live train positions
│   ├── trip_updates.py  # Fetch real-time trip updates
├── config.py             # Configuration settings
├── Dockerfile            # Docker build instructions
├── docker-compose.yml    # Manages Docker services
├── run_scraper.sh        # Auto-runs all scrapers
├── requirements.txt      # Python dependencies
└── README.md             
```
