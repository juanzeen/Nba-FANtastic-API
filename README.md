# NBA FANtastic API 🏀

A high-performance backend catalog and analytics REST API for NBA basketball data. **NBA FANtastic API** provides structured endpoints for exploring historical legends, active NBA rosters, in-depth season metrics, all-time records, and upcoming game predictions.

Built with **FastAPI**, **MongoDB (PyMongo Async)**, and **Redis**, utilizing **uv** for blazing-fast Python package management.

---

## 📌 Features

- 📜 **Historical NBA Legends**: Search and paginate archives of all-time NBA greats, including career totals, peaks, and honors.
- 🏆 **All-Time Records**: Query historical NBA benchmarks (scoring, assists, rebounds, etc.) by record category.
- ⛹️‍♂️ **Active NBA Players**: Explore active rosters, player bios, team affiliations, and career stats.
- 📅 **Season & Game Logs**: Query season-by-season player averages, single-game peaks, and performance splits against specific opponents.
- ⚡ **Redis Caching Layer**: Cache-aside caching strategy with dynamic TTLs to deliver sub-millisecond response times for frequent queries.
- 📄 **Standardized Pagination**: Reusable generic pagination models with full navigation metadata (`total_items`, `total_pages`, `has_next`, `has_previous`).
- 🩺 **Multi-Service Health Checks**: Integrated health endpoint verifying live connectivity to both MongoDB and Redis.
- 🧪 **Comprehensive Test Suite**: 100% async test coverage using Pytest, AnyIO, HTTPX, and isolated mock fixtures.

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Framework** | [FastAPI](https://fastapi.tiangolo.com/) (Python 3.14+) |
| **Data Validation** | [Pydantic v2](https://docs.pydantic.dev/) |
| **Primary Database** | [MongoDB](https://www.mongodb.com/) (Async PyMongo) |
| **Caching Layer** | [Redis](https://redis.io/) (`redis.asyncio`) |
| **Package Manager** | [uv](https://docs.astral.sh/uv/) by Astral |
| **Containerization** | [Docker](https://www.docker.com/) & Docker Compose |
| **Testing** | [pytest](https://docs.pytest.org/), AnyIO, HTTPX |
| **Data Scraping** | [`nba-api`](https://github.com/swar/nba_api), pandas |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.14+ (or managed via `uv`)
- [uv](https://docs.astral.sh/uv/) installed
- [Docker & Docker Compose](https://www.docker.com/) (for MongoDB & Redis)

---

### 1. Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/juanzeen/Nba-FANtastic-API.git
   cd Nba-FANtastic-API
   ```

2. **Install dependencies with `uv`**:
   ```bash
   uv sync
   ```

3. **Configure environment variables**:
   Create a `.env` file in the root directory:
   ```bash
   cp .env.example .env
   ```
   Example configuration for local development:
   ```env
   # MongoDB Configuration
   MONGO_URL=mongodb://nba_fantastic:superpasswordfornbafantastic@localhost:27017/nba_fantastic?authSource=admin&directConnection=true
   DATABASE_NAME=nba_fantastic
   MONGO_DB_USER=nba_fantastic
   MONGO_DB_PASSWORD=superpasswordfornbafantastic
   MONGO_DB_PORT=27017

   # Redis Configuration
   REDIS_URL=redis://localhost:6379
   REDIS_PORT=6379
   REDIS_PASSWORD=nbafantastic123password
   ```

---

### 2. Running Services with Docker

You can run the entire stack (FastAPI, MongoDB, and Redis) inside Docker, or run just the databases in Docker while developing locally.

#### Option A: Run the Entire Stack in Docker (API + MongoDB + Redis)

Build and start all services in the background:
```bash
docker compose up -d --build
```

Or start specifically the API container (Docker will automatically start its dependencies):
```bash
docker compose up -d --build api
```

Check running containers:
```bash
docker compose ps
```

Follow real-time logs from the API:
```bash
docker compose logs -f api
```

Stop all services:
```bash
docker compose down
```

---

#### Option B: Run Only Databases in Docker (Hybrid Development)

Start only MongoDB and Redis in the background (useful when developing the API locally with `uv`):
```bash
docker compose up -d mongodb redis
```

Stop the databases:
```bash
docker compose stop mongodb redis
```

---

### 3. Database Seeding (Optional)

To ingest and populate your local MongoDB instance with legends and active player data:

```bash
uv run python seed/populate.py
```

---

### 4. Running the API Locally (Without Docker for API)

If you chose **Option B** above (running only MongoDB & Redis in Docker), start the FastAPI development server locally with live reload:

```bash
uv run fastapi dev src/app/main.py
```

- **Interactive API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Docs (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check Endpoint**: [http://localhost:8000/](http://localhost:8000/)

---

### 5. Running the Tests

Execute the automated test suite with `pytest`:

```bash
uv run pytest
```

Run tests with verbose output:
```bash
uv run pytest -v
```

---

## 📡 API Endpoints Reference

### 🩺 System & Health
| Method | Endpoint | Description | Cache |
| :--- | :--- | :--- | :---: |
| `GET` | `/` | Service health status (API, MongoDB, Redis) | — |

### 📜 Historical Players
| Method | Endpoint | Description | Cache |
| :--- | :--- | :--- | :---: |
| `GET` | `/historical-players/` | List all historical players (paginated: `page`, `limit`) | — |
| `GET` | `/historical-players/{id}` | Get historical player by numeric ID | — |
| `GET` | `/historical-players/search/{slug}` | Get historical player by slug (e.g. `michael-jordan`) | — |

### 🏆 Historical Records
| Method | Endpoint | Description | Cache |
| :--- | :--- | :--- | :---: |
| `GET` | `/historical-records/` | Get all all-time NBA records | ⚡ Redis |
| `GET` | `/historical-records/{category}` | Get record by category (e.g. `ALL_TIME_PTS`) | ⚡ Redis |

### ⛹️‍♂️ Current NBA Players
| Method | Endpoint | Description | Cache |
| :--- | :--- | :--- | :---: |
| `GET` | `/players/` | List active players (paginated: `page`, `limit`) | — |
| `GET` | `/players/{id}` | Get player profile and career stats by ID | — |
| `GET` | `/players/search/{slug}` | Get active player by slug (e.g. `precious-achiuwa`) | — |
| `GET` | `/players/team/{team_abb}` | List all active players for a team (e.g. `MIA`, `LAL`) | ⚡ Redis |
| `GET` | `/players/{id}/seasons` | List seasons for a player (paginated) | — |
| `GET` | `/players/{id}/seasons/{season_year}` | Get detailed season log (e.g. `2021-22`) | ⚡ Redis |

---

## 📂 Project Structure

```text
Nba-FANtastic-API/
├── Dockerfile                 # Multi-stage container build (dev, builder, prod)
├── docker-compose.yaml        # MongoDB Atlas Local & Redis service definitions
├── pyproject.toml             # uv & project dependencies
├── README.md                  # Project documentation
├── uv.lock                    # Dependency lockfile
├── seed/                      # Data extraction & database migration scripts
│   ├── extractor.py           # Scraping pipeline using nba_api
│   ├── populate.py            # MongoDB batch seeding script
│   └── *.csv                  # Static datasets (legends, active players, records)
└── src/
    └── app/                   # FastAPI application package
        ├── main.py            # App instantiation, router inclusion & health check
        ├── dependencies.py    # Database & Redis dependency providers
        ├── routers/           # API route controllers
        │   ├── historical_players.py
        │   ├── historical_records.py
        │   └── nba_players.py
        ├── schemas/           # Pydantic v2 data models
        │   ├── base.py        # Generic responses & pagination schemas
        │   ├── historical_players.py
        │   ├── historical_records.py
        │   ├── nba_players.py
        │   └── player_seasons.py
        ├── utils/             # Helper utilities
        │   ├── cache.py       # Cache-aside helper (get_cached_or_db)
        └── tests/             # Automated test suite
            ├── conftest.py    # Shared Pytest fixtures (mock_redis, etc.)
            ├── test_api_health.py
            ├── test_historical_players.py
            ├── test_historical_records.py
            ├── test_nba_players.py
            └── test_nba_players_seasons.py
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
