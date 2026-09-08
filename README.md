# NBA FANtastic API 🏀

A backend catalog and analytics API for NBA basketball data. **NBA FANtastic API** serves as the central data engine for exploring historical player archives, active NBA rosters, in-depth player statistics, and machine-learning-driven future game performance predictions.

---

## 📌 Project Overview

The goal of this project is to provide a complete "catalog" and statistical prediction platform for basketball enthusiasts, fantasy players, and developers.

### Core Features (Roadmap & Current)

- 📜 **Historical Player & Records Catalog**: Search and browse profiles for all-time NBA legends as well historical records. ✔️
- ⛹‍♂ **Current & Historical NBA Players Catalog**: Search and browse seasons and stats for current NBA players. ✔️
- 📊 **Comprehensive Statistics**: Access key stats, career averages, game logs, and advanced efficiency metrics.
- 🔮 **Game Stats Prediction**: Future performance projections and statistical modeling for upcoming games.
- ⚡ **High-Performance REST API**: Fast and clean API endpoints designed to power frontend clients and mobile apps.

---

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database**: [MongoDB](https://www.mongodb.com/) (using PyMongo)
- **Data Processing & Integration**: [`nba-api`](https://github.com/swar/nba_api), [pandas](https://pandas.pydata.org/)
- **Containerization**: [Docker](https://www.docker.com/) & Docker Compose
- **Package Management**: [uv](https://docs.astral.sh/uv/)

---

## 🚀 Getting Started

> *Note: The project is currently in its initial development phase.*

### Prerequisites

- Python 3.14+ (or managed via `uv`)
- [uv](https://docs.astral.sh/uv/)
- Docker & Docker Compose (for running MongoDB locally)

### 1. Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/juanzeen/Nba-FANtastic-API.git
   cd Nba-FANtastic-API
   ```

2. **Set up the virtual environment & dependencies**:
   ```bash
   uv sync
   ```

3. **Configure environment variables**:
   Copy `.env.example` to create your local `.env` file:
   ```bash
   cp .env.example .env
   ```
   The default `.env` is preconfigured to work seamlessly with the local Docker Compose MongoDB setup:
   ```env
   MONGO_URL=mongodb://user:password@localhost:27017/nba_fantastic?authSource=admin&directConnection=true
   DATABASE_NAME=nba_fantastic
   MONGO_DB_USER=user
   MONGO_DB_PASSWORD=password
   MONGO_DB_PORT=27017
   ```

---

### 2. Running MongoDB Locally

The project includes a `docker-compose.yaml` using `mongodb/mongodb-atlas-local`.

- **Start MongoDB in the background**:
  ```bash
  docker compose up -d
  ```

- **Verify MongoDB is running**:
  ```bash
  docker compose ps
  ```

- **View MongoDB container logs**:
  ```bash
  docker compose logs -f mongodb
  ```

- **Stop MongoDB**:
  ```bash
  docker compose down
  ```

---

### 3. Seeding the Database (Optional)

To populate your local MongoDB instance with historical NBA player data and career statistics:

```bash
uv run python seed/populate.py
```
OR

```
cd seed
python populate.py
```
---

### 4. Running the API

Start the FastAPI development server:

```bash
uv run fastapi dev src/app/main.py
```

- **Interactive API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check Endpoint**: [http://localhost:8000/](http://localhost:8000/) (verifies API and MongoDB database connectivity)

---

## 📂 Project Structure

```text
Nba-FANtastic-API/
├── docker-compose.yaml      # Docker Compose configuration for local MongoDB
├── seed/                    # Data ingestion, seeding scripts, and datasets
│   ├── extractor.py
│   ├── nba_legends.csv
│   └── populate.py
├── src/
│   └── app/                 # FastAPI application
│       ├── routers/         # API route handlers
│       ├── dependencies.py  # MongoDB client & dependency injection
│       └── main.py          # Application entrypoint & health checks
├── pyproject.toml           # Project metadata and dependencies
├── README.md                # Project documentation
└── uv.lock                  # uv lockfile
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
