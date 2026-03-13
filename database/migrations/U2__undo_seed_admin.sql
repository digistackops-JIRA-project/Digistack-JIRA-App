-- ============================================================================
-- U2__undo_seed_admin.sql
-- Flyway UNDO migration for V2 — removes the seeded admin account
-- ============================================================================

DELETE FROM admins WHERE email = 'admin@sapsecops.in';
