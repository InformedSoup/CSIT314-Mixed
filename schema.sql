-- Interior Design Matching Platform - database schema (SQLite)
-- Covers all sprints so later features need no migration.

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS idp_view;
DROP TABLE IF EXISTS favourite;
DROP TABLE IF EXISTS idp;
DROP TABLE IF EXISTS idp_category;
DROP TABLE IF EXISTS company;
DROP TABLE IF EXISTS user_session;
DROP TABLE IF EXISTS user_account;
DROP TABLE IF EXISTS user_profile;

-- User profile: a named profile that grants one of the four base roles.
-- The four core profiles are created below; User Admin can add more (e.g. 'Premium Customer').
CREATE TABLE user_profile (
    profile_id    INTEGER PRIMARY KEY,
    profile_name  TEXT NOT NULL UNIQUE,
    description   TEXT NOT NULL DEFAULT '',
    role          TEXT NOT NULL CHECK (role IN ('USER_ADMIN', 'INTERIOR_DESIGNER', 'CUSTOMER', 'PLATFORM_MANAGEMENT')),
    status        TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'SUSPENDED')),
    created_at    TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE user_account (
    account_id     INTEGER PRIMARY KEY,
    full_name      TEXT NOT NULL,
    username       TEXT NOT NULL UNIQUE COLLATE NOCASE,
    email          TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash  TEXT NOT NULL,
    profile_id     INTEGER NOT NULL REFERENCES user_profile(profile_id),
    status         TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'SUSPENDED')),
    created_at     TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- One row per login; logout_at is filled on logout.
CREATE TABLE user_session (
    session_id  INTEGER PRIMARY KEY,
    account_id  INTEGER NOT NULL REFERENCES user_account(account_id),
    login_at    TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    logout_at   TEXT
);

-- Sprint 2: company information (an interior designer can manage several company records)
CREATE TABLE company (
    company_id      INTEGER PRIMARY KEY,
    designer_id     INTEGER NOT NULL REFERENCES user_account(account_id),
    company_name    TEXT NOT NULL,
    reg_number      TEXT NOT NULL UNIQUE COLLATE NOCASE,
    description     TEXT NOT NULL DEFAULT '',
    address         TEXT NOT NULL DEFAULT '',
    contact_number  TEXT NOT NULL DEFAULT '',
    created_at      TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- Sprint 2/3: IDP categories managed by Platform Management
CREATE TABLE idp_category (
    category_id  INTEGER PRIMARY KEY,
    name         TEXT NOT NULL UNIQUE COLLATE NOCASE,
    description  TEXT NOT NULL DEFAULT '',
    created_at   TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- Sprint 3: interior design projects. status separates current vs past IDPs.
CREATE TABLE idp (
    idp_id           INTEGER PRIMARY KEY,
    designer_id      INTEGER NOT NULL REFERENCES user_account(account_id),
    category_id      INTEGER REFERENCES idp_category(category_id) ON DELETE SET NULL,
    title            TEXT NOT NULL,
    client_name      TEXT NOT NULL DEFAULT '',
    description      TEXT NOT NULL DEFAULT '',
    design_style     TEXT NOT NULL DEFAULT '',
    image_url        TEXT NOT NULL DEFAULT '',
    progress         INTEGER NOT NULL DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
    completion_date  TEXT,
    status           TEXT NOT NULL CHECK (status IN ('CURRENT', 'PAST')),
    created_at       TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE favourite (
    favourite_id  INTEGER PRIMARY KEY,
    customer_id   INTEGER NOT NULL REFERENCES user_account(account_id),
    idp_id        INTEGER NOT NULL REFERENCES idp(idp_id) ON DELETE CASCADE,
    saved_at      TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    UNIQUE (customer_id, idp_id)
);

CREATE TABLE idp_view (
    view_id      INTEGER PRIMARY KEY,
    idp_id       INTEGER NOT NULL REFERENCES idp(idp_id) ON DELETE CASCADE,
    customer_id  INTEGER REFERENCES user_account(account_id),
    viewed_at    TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE INDEX idx_account_profile ON user_account(profile_id);
CREATE INDEX idx_company_designer ON company(designer_id);
CREATE INDEX idx_idp_designer ON idp(designer_id);
CREATE INDEX idx_view_idp ON idp_view(idp_id);
CREATE INDEX idx_view_time ON idp_view(viewed_at);
CREATE INDEX idx_fav_time ON favourite(saved_at);

INSERT INTO user_profile (profile_id, profile_name, description, role) VALUES
    (1, 'User Admin', 'Manages user accounts and user profiles', 'USER_ADMIN'),
    (2, 'Interior Designer', 'Manages company information and design projects', 'INTERIOR_DESIGNER'),
    (3, 'Customer', 'Searches, views and saves design projects', 'CUSTOMER'),
    (4, 'Platform Management', 'Manages IDP categories and views reports', 'PLATFORM_MANAGEMENT');
