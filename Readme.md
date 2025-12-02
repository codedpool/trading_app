
***

# 📈 Quantitative Trading Strategy API

A FastAPI-based application that manages historical stock data and implements a Moving Average Crossover trading strategy. This project demonstrates a full-stack data engineering pipeline including PostgreSQL database integration (via Prisma), REST API development, Unit Testing, and Docker containerization.

## 🚀 Features

*   **Data Ingestion**: Automated ETL script to load OHLCV stock data from Excel into PostgreSQL.
*   **REST API**:
    *   `GET /data`: Retrieve historical stock records.
    *   `POST /data`: Add new market data with Pydantic validation.
    *   `GET /strategy/performance`: Execute and backtest a customized Moving Average Crossover strategy.
*   **Database**: PostgreSQL managed via Prisma ORM (Python Client).
*   **Testing**: Comprehensive unit tests with `pytest` achieving >80% code coverage.
*   **Deployment**: Fully containerized using Docker.

***

## 🛠️ Tech Stack

*   **Language**: Python 3.10+
*   **Framework**: FastAPI
*   **Database**: PostgreSQL
*   **ORM**: Prisma Client Python
*   **Data Analysis**: Pandas
*   **Testing**: Pytest, Pytest-cov
*   **Containerization**: Docker

***

## ⚙️ Setup & Installation

Follow these steps to set up the project locally.

### 1. Clone the Repository
```bash
git clone <YOUR_REPO_LINK>
cd trading_assignment
```

### 2. Environment Setup
Create a virtual environment and install dependencies.
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows Git Bash)
source venv/Scripts/activate
# Activate (Windows CMD)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Configuration
Ensure you have a PostgreSQL instance running locally.

1.  Create a database named `trading_app`.
2.  Create a `.env` file in the root directory:
    ```env
    DATABASE_URL="postgresql://USER:PASSWORD@localhost:5432/trading_app"
    ```
    *(Replace `USER`, `PASSWORD` with your credentials. If your password has special characters like `@`, URL-encode them, e.g., `Database%401`)*

3.  Push the schema to the database:
    ```bash
    prisma db push
    ```

4.  Generate the Prisma Client:
    ```bash
    prisma generate
    ```

### 4. Load Initial Data
Populate the database with the provided Excel file (`HINDALCO_1D.xlsx`).
```bash
python scripts/load_data.py
```

***

## 🏃‍♂️ Running the Application

### Method 1: Local Development
Start the Uvicorn server:
```bash
uvicorn app.main:app --reload
```
*   **API Documentation**: Open `http://127.0.0.1:8000/docs`
*   **Strategy Endpoint**: GET `http://127.0.0.1:8000/strategy/performance`

### Method 2: Using Docker 🐳
You can run the entire application inside a Docker container.

1.  **Build the Image**:
    ```bash
    docker build -t trading-app .
    ```

2.  **Run the Container**:
    *Note: Replace `host.docker.internal` is used to access the localhost database from inside the container.*
    ```bash
    docker run -p 8000:8000 -e DATABASE_URL="postgresql://USER:PASSWORD@host.docker.internal:5432/trading_app" trading-app
    ```

***

## 🧪 Testing

Run the unit tests to verify logic and API validation.

```bash
# Run tests
python -m pytest tests/

# Run tests with coverage report
python -m pytest --cov=app tests/
```

**Current Coverage Target**: >80% ✅

***

## 📂 Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py          # App entry point
│   ├── routes.py        # API controllers
│   ├── models.py        # Pydantic schemas
│   ├── services.py      # Business logic (Strategy)
│   └── database.py      # DB connection handling
├── prisma/
│   └── schema.prisma    # Database schema
├── scripts/
│   └── load_data.py     # ETL Script
├── tests/
│   └── test_main.py     # Unit tests
├── Dockerfile
├── requirements.txt
└── README.md
```

## 📊 Strategy Logic
The strategy implemented is a **Simple Moving Average (SMA) Crossover**:
*   **Short Window**: 10 Days
*   **Long Window**: 50 Days
*   **Signal**: Buy when Short MA crosses above Long MA; Sell when Short MA crosses below.
*   **Performance Metrics**: Total Return, Win Rate, Trade Count.