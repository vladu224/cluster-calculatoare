\connect auth_db

CREATE TYPE user_role AS ENUM ('administrator', 'maintainer');

CREATE TABLE users (
    uid       UUID         PRIMARY KEY,
    username  VARCHAR(255) NOT NULL UNIQUE,
    password  VARCHAR(255),
    role      user_role    NOT NULL,
    is_active BOOLEAN      NOT NULL DEFAULT FALSE
);