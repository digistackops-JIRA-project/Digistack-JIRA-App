-- ============================================================================
-- V1__create_schema.sql
-- Flyway migration: initial schema for AdminDB
-- ============================================================================

CREATE TABLE IF NOT EXISTS admins (
    id              INT             NOT NULL AUTO_INCREMENT,
    email           VARCHAR(255)    NOT NULL,
    hashed_password VARCHAR(255)    NOT NULL,
    is_active       TINYINT(1)      NOT NULL DEFAULT 1,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME                 ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_admin_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ──────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS teams (
    id              INT             NOT NULL AUTO_INCREMENT,
    team_name       VARCHAR(150)    NOT NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME                 ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_team_name (team_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ──────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS managers (
    id              INT             NOT NULL AUTO_INCREMENT,
    name            VARCHAR(150)    NOT NULL,
    email           VARCHAR(255)    NOT NULL,
    hashed_password VARCHAR(255)    NOT NULL,
    phone           VARCHAR(20)         NULL,
    team_id         INT             NOT NULL,
    is_active       TINYINT(1)      NOT NULL DEFAULT 1,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME                 ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_manager_email (email),
    CONSTRAINT fk_manager_team FOREIGN KEY (team_id) REFERENCES teams (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ──────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS employees (
    id              INT             NOT NULL AUTO_INCREMENT,
    name            VARCHAR(150)    NOT NULL,
    email           VARCHAR(255)    NOT NULL,
    hashed_password VARCHAR(255)    NOT NULL,
    phone           VARCHAR(20)         NULL,
    team_id         INT             NOT NULL,
    manager_id      INT             NOT NULL,
    is_active       TINYINT(1)      NOT NULL DEFAULT 1,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME                 ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_employee_email (email),
    CONSTRAINT fk_employee_team    FOREIGN KEY (team_id)    REFERENCES teams    (id),
    CONSTRAINT fk_employee_manager FOREIGN KEY (manager_id) REFERENCES managers (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
