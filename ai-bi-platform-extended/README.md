AI-Powered BI Platform — Extended MVP

This extended scaffold adds:
- Multi-tenant sample data (init-db/seed.sql)
- SQL Editor endpoint and frontend component
- Model Training UI component
- Simple auth stub and Keycloak dev service
- LLM agent endpoint

Run locally:
1. docker compose up --build
2. Seed the DB: docker exec -i <pg_container> psql -U demo -d bi_demo -f /init-db/seed.sql
3. Open frontend: http://localhost:3000
