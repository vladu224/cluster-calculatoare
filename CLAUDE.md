# CLAUDE.md

Context for Claude Code when working in this repository.

## Project

University lab project for **Programare Orientată pe Servicii** (TI, year IV, TUIAȘI, 2026–2027): a service-oriented platform that manages a simulated computer cluster.

- Stations are **Docker containers** running `openssh-server`.
- Maintenance scripts run on stations **over SSH**, **asynchronously** (HTTP returns `202` immediately, a background worker does the work).
- Users are notified when jobs finish.

Full design spec (Romanian): https://claude.ai/code/artifact/e4bd2136-b4f1-41cd-bffa-4e274957d2d4

## Roles (must be enforced on every endpoint)

| Action | Admin | Maintainer |
| --- | --- | --- |
| Create / disable / delete accounts | Yes | No |
| Manage / delete scripts | Yes | Only flag for deletion |
| Subgroups and assignment to Maintainers | Yes | No |
| Launch scripts on assigned stations | **No** | Yes |
| Request new scripts | No | Yes |
| Monitor cluster and receive job/station notifications | **No** | Yes |

Admins only get notifications about script requests. A `CLUSTER` job target means all stations assigned to that Maintainer, never the whole cluster.

## Architecture

```
React client → Nginx gateway (:8080) → auth | cluster | scripts | notifications
                                         scripts → RabbitMQ → workers → SSH → stations
```

- **4 business services** (NFR-ARCH-01): Auth, Cluster, Scripts, Notifications.
- **Workers**: stateless, consume `jobs.execute`, publish results to `job.events`.
- **One Postgres container, one database per service**: `auth_db`, `cluster_db`, `scripts_db`, `notifications_db`. No foreign keys across services; cross-service references are plain UUIDs.
- **Internal endpoints** (`/internal/...`) are only reachable inside the Docker network, never routed by the gateway.
- **JWT**: HS256, signed with the shared `JWT_SECRET` env var. Access token 15 min (claims: `sub`, `role`, `exp`), refresh token 7 days, opaque random string stored SHA-256 hashed and rotated on every `/auth/refresh` (the used token is revoked). Every service gets the same `JWT_SECRET` and verifies access tokens locally, without calling Auth.
- **SSH**: key-based only. The private key is mounted only into workers, never stored in a database.

## Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0 (typed `Mapped[...]`), psycopg, pydantic-settings, bcrypt
- **Frontend:** React + TypeScript (Vite)
- **Infra:** Docker Compose, Nginx (gateway), PostgreSQL 16, RabbitMQ 3

## Repository layout

```
cluster-platform/
├── docker-compose.yml
├── .env
├── postgres/init.sql          # creates one database per service
├── gateway/nginx.conf         # routes /api/<service>/ → <service>:8000/
├── services/
│   └── auth/                  # cluster, scripts, notifications, worker follow the same layout
│       ├── Dockerfile
│       ├── requirements.txt
│       └── app/
│           ├── main.py        # FastAPI app, lifespan creates tables + seeds
│           ├── config.py      # pydantic-settings
│           ├── database.py    # engine, SessionLocal, Base, get_db
│           ├── models.py
│           ├── security.py
│           └── seed.py
└── frontend/                  # Vite React TS
    ├── vite.config.ts         # proxies /api → http://localhost:8080
    └── src/api/client.ts      # fetch wrapper, adds /api prefix and Bearer token
```

## Conventions

### Backend services
- Each service listens on port `8000` inside its container, with `root_path="/api/<service>"`.
- Nginx strips the prefix: `/api/auth/health` reaches the service as `/health`.
- Adding a service means adding a `location /api/<service>/` block in `gateway/nginx.conf` and a service in `docker-compose.yml`.
- Tables are created with `Base.metadata.create_all` on startup (no migrations).
- Settings come from environment variables via `config.py`, never hard-coded.
- The first Admin is seeded from `ADMIN_*` env vars.
- Error responses use FastAPI's default shape `{ "detail": "..." }` (raised via `HTTPException`).
- Lists are paginated with `?page=&size=` and return `{ items, page, size, total }`.

### Frontend
- All backend calls go through `src/api/client.ts` and are written without the `/api` prefix (`api.get("/auth/me")`).
- Page routes must not start with `/api`.

## Commands

```bash
docker compose up --build          # start everything (rebuild after requirements change)
docker compose down -v             # reset, including the Postgres volume
docker compose logs -f auth        # follow one service's logs
docker compose exec postgres psql -U admin -d auth_db
cd frontend && npm run dev         # frontend on http://localhost:5173
```

## Progress

- [x] Project setup (compose, gateway, Postgres, RabbitMQ, frontend)
- [ ] Auth Service: Stage 1 (models, hashing, admin seed) ✔ → Stage 2 (login, JWT HS256, refresh, logout, `/me`) ✔ → Stage 3 (user management, role checks, pagination) pending
- [ ] Cluster Service
- [ ] Scripts Service
- [ ] Workers
- [ ] Notifications Service
- [ ] Frontend

## How to work with me

- Stick strictly to what the lab requires. Don't add features beyond the spec.
- Work step by step and wait for my confirmation before moving to the next stage.
- When changing a file, give me the complete updated file, not partial snippets.
- Keep code clean and scalable. Prefer array-based patterns over `Object.entries()`.
- Keep explanations short.