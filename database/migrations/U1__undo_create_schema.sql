-- ============================================================================
-- U1__undo_create_schema.sql
-- Flyway UNDO migration for V1 — drops all tables in reverse FK order
-- Requires Flyway Teams edition for automatic undo.
-- For Community edition: run this script manually as a rollback step.
-- ============================================================================

-- Drop in reverse dependency order
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS managers;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS admins;
