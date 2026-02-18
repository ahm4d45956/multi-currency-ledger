Multi-Currency Ledger API

Distributed Fintech Backend Simulation



Python | FastAPI | PostgreSQL | Docker | CI/CD | Microservices

OVERVIEW



This project simulates a production-style multi-currency ledger system similar to core financial infrastructure used in fintech platforms.



It models how modern financial systems handle:

Account creation

Currency-specific balances

Concurrent deposits

ACID-compliant transaction processing

Service separation across independent components



The system is designed using distributed microservices and containerised with Docker to reflect real-world backend architecture patterns.

SYSTEM ARCHITECTURE



The application consists of four core components:



Ledger Service (Core Service)

Manages accounts and balances

Implements ACID-compliant transaction logic

Uses SELECT FOR UPDATE row-level locking to prevent race conditions

Built with FastAPI and PostgreSQL



FX Service

Simulates exchange-rate logic

Designed as an isolated microservice



Revenue Service

Simulates fee handling and revenue tracking

Separated to support modular scalability



PostgreSQL

Persistent financial storage layer

Uses NUMERIC type for precise monetary calculations

Guarantees transactional integrity



All services are orchestrated using Docker Compose.

-------------------------------------------------------------------

CONCURRENCY AND DATA INTEGRITY



Financial systems must guarantee consistency under concurrent access.



The ledger service enforces data integrity through:

Row-level locking (SELECT FOR UPDATE)

Atomic balance updates within database transactions

Decimal-safe arithmetic (no floating-point precision errors)

Thread-safe request handling



A load test simulating 100 concurrent deposits validates:

No race conditions

Correct final balance

ACID compliance under concurrent load

LOAD TESTING



To simulate concurrent deposits, run:



python load_test.py



Test flow:

Create account

Deposit initial 1000

Run 100 concurrent deposits

Validate final balance



Expected output:



Load test completed.

No race condition detected.

RUNNING LOCALLY WITH DOCKER



Build and start all services:



docker compose up –build


-----------------------------------------------------------------------------
Available services:



Ledger Service: http://localhost:8000

FX Service: http://localhost:8001

Revenue Service: http://localhost:8002

PostgreSQL: localhost:5432

PROJECT STRUCTURE



multi-currency-ledger/

│

├── ledger-service/

│   ├── main.py

│   ├── database.py

│   ├── models.py

│   ├── init.sql

│   ├── Dockerfile

│   └── requirements.txt

│

├── fx-service/

├── revenue-service/

├── load_test.py

├── docker-compose.yml

└── README.md

----------------------------------------------------------------------------------

ENGINEERING DECISIONS

Used PostgreSQL NUMERIC for precise monetary representation

Avoided floats entirely to prevent rounding errors

Implemented row-level locking for safe concurrent updates

Designed services modularly to support horizontal scalability

Applied environment-based configuration for flexibility

Containerised all services for reproducible deployments

PRODUCTION SIMULATION FEATURES

Modular microservice architecture

Docker containerisation

Environment-based configuration

ACID-compliant transaction guarantees

Concurrency stress testing

CI-ready repository structure

WHY THIS PROJECT MATTERS



This project demonstrates:

Distributed systems design thinking

Concurrency control in financial systems

Backend API design with FastAPI

Practical implementation of ACID guarantees

Debugging and elimination of race conditions

Production-style service separation and container orchestration

-------------------------------------------------------------------------------------------------
FUTURE IMPROVEMENTS

JWT authentication

API gateway integration

Structured logging and metrics collection

Cloud deployment (Railway, Render, AWS ECS)


Integration testing in CI pipeline
------------------------------------------------------------------
AUTHOR

Muhammad Ahmad

Backend Engineering | Distributed Systems | Fintech Systems