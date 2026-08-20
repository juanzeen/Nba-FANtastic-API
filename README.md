# NBA FANtastic API 🏀

A backend catalog and analytics API for NBA basketball data. **NBA FANtastic API** serves as the central data engine for exploring historical player archives, active NBA rosters, in-depth player statistics, and machine-learning-driven future game performance predictions.

---

## 📌 Project Overview

The goal of this project is to provide a complete "catalog" and statistical prediction platform for basketball enthusiasts, fantasy players, and developers.

### Core Features (Roadmap & Current)

- 📜 **Historical & Active Player Catalog**: Search and browse profiles for all-time NBA legends as well as current league players.
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
- Docker & Docker Compose (for containerized setup & MongoDB)

### Installation

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
   Create a `.env` file in the root directory based on your database configuration:
   ```env
   MONGO_URI=mongodb://localhost:27017
   DATABASE_NAME=nba_fantastic
   ```

---

## 📂 Project Structure

```text
Nba-FANtastic-API/
├── src/
│   └── nba_fantastic_api/
│       ├── seed/            # Data ingestion, seeding scripts, and CSV datasets
│       └── ...              # API routes, models, and core logic (in progress)
├── pyproject.toml           # Project metadata and dependencies
├── README.md                # Project documentation
└── ...
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).