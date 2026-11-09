docker compose exec -T postgres psql -U admin -d auth_db <<'SQL'
CREATE EXTENSION IF NOT EXISTS pgcrypto;
INSERT INTO users (uid, username, password, role, is_active)
VALUES (uuidv7(), 'admin', crypt('Admin123!', gen_salt('bf')), 'administrator', TRUE);
SELECT uid, username, role, is_active FROM users;
SQL