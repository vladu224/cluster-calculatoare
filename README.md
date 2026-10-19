# Cluster Management Platform

A service-oriented platform for managing a cluster of computers, built for the **Programare Orientată pe Servicii** lab (TI, year IV, "Gheorghe Asachi" Technical University of Iași, 2026–2027).

The cluster's stations are simulated with Docker containers. Administrators manage users, stations, subgroups and maintenance scripts. Maintainers run those scripts remotely over SSH on the stations assigned to them, and get notified when the runs finish.

## Features

- Secure login with role-based access (**Admin** and **Maintainer**)
- Station registration, monitoring and grouping into subgroups
- Subgroups assigned to Maintainers
- A script catalog, with Maintainer requests to add or delete scripts
- Script execution over SSH on one station, a subgroup or all assigned stations
- Asynchronous execution: the request returns immediately and a background worker runs the job
- Live notifications about job status

## Architecture

```
               ┌──────────────┐
               │ React client │
               └──────┬───────┘
                      │
               ┌──────▼───────┐
               │ Nginx gateway│  :8080
               └──┬──┬──┬──┬──┘
       ┌──────────┘  │  │  └───────────┐
   ┌───▼──┐   ┌──────▼┐ ┌▼──────┐ ┌────▼────────┐
   │ Auth │   │Cluster│ │Scripts│ │Notifications│
   └──────┘   └───────┘ └───┬───┘ └─────────────┘
                            │
                     ┌──────▼─────┐
                     │  RabbitMQ  │
                     └──────┬─────┘
                     ┌──────▼─────┐
                     │  Workers   │
                     └──────┬─────┘
                            │ SSH (key-based)
                 ┌──────────▼──────────┐
                 │ Docker stations     │
                 └─────────────────────┘
```

| Component | Responsibility |
| --- | --- |
| Auth | Login, JWT (HS256, shared secret), user accounts |
| Cluster | Stations, subgroups, assignments, health checks |
| Scripts | Script catalog, script requests, job launching |
| Workers | Run scripts over SSH and report results |
| Notifications | Store notifications and push them over WebSocket |
| Gateway | Single entry point that routes `/api/<service>/` to each service |

Each service owns its own database (`auth_db`, `cluster_db`, `scripts_db`, `notifications_db`) inside one PostgreSQL container.

## Tech stack

| Layer | Technology |
| --- | --- |
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 |
| Frontend | React, TypeScript, Vite |
| Database | PostgreSQL 16 |
| Messaging | RabbitMQ 3 |
| Gateway | Nginx |
| Runtime | Docker, Docker Compose |

## Project structure

```
cluster-platform/
├── docker-compose.yml
├── .env
├── postgres/
│   └── init.sql
├── gateway/
│   └── nginx.conf
├── services/
│   └── auth/
│       ├── Dockerfile
│       ├── requirements.txt
│       └── app/
└── frontend/
```

## Getting started

### Prerequisites

- Docker Desktop
- Node.js 20+
- Python 3.12 (only needed for local editor support)

### 1. Configure the environment

Create a `.env` file in the project root:

```env
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@cluster.local
ADMIN_PASSWORD=Admin123!
JWT_SECRET=change-me-to-a-long-random-string
```

The `ADMIN_*` values create the first administrator account on startup. `JWT_SECRET` signs and verifies access tokens (HS256); every service that validates tokens receives the same value.

### 2. Start the backend

```bash
docker compose up --build
```

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

## Useful URLs

| URL | Description |
| --- | --- |
| http://localhost:5173 | Frontend |
| http://localhost:8080/api/auth/health | Auth Service health check |
| http://localhost:8080/api/auth/docs | Auth Service API docs (Swagger) |
| http://localhost:15673 | RabbitMQ dashboard |

## Common commands

```bash
docker compose up --build        # start or rebuild everything
docker compose down              # stop everything
docker compose down -v           # stop and delete the database volume
docker compose logs -f auth      # follow a service's logs
```

## Roles

| Action | Admin | Maintainer |
| --- | --- | --- |
| Create, disable or delete accounts | ✔ | ✘ |
| Manage scripts | ✔ | Flag for deletion only |
| Manage subgroups and assignments | ✔ | ✘ |
| Run scripts | ✘ | ✔ |
| Request new scripts | ✘ | ✔ |
| Monitor the cluster and receive notifications | ✘ | ✔ |

## Status

- [x] Project setup
- [ ] Auth Service (login, JWT HS256, refresh, logout, `/me` done; user management and role checks pending)
- [ ] Cluster Service
- [ ] Scripts Service
- [ ] Workers
- [ ] Notifications Service
- [ ] Frontend