-- ============================================================================
-- V2__seed_admin.sql
-- Flyway migration: seed default Admin account
-- Password: Admin123  (bcrypt hash — regenerate for production!)
-- ============================================================================

INSERT IGNORE INTO admins (email, hashed_password, is_active)
VALUES (
    'admin@sapsecops.in',
    '$2b$12$LQv3c1yqBWVHxkd.W1j4.O8TkO1jSqZ1y7Gt4R5MkD6k9E7O5f9Hm',  -- Admin123
    1
);

-- NOTE FOR DB TEAM:
-- The hash above is for development/staging ONLY.
-- For production, run the seed script with a vault-provided hash.
-- To generate a fresh hash:
--   python3 -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('Admin123'))"
