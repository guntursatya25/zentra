-- Seed data for Zentra
-- Run automatically via docker-compose mount at first DB init.

-- Enable pgvector (idempotent)
CREATE EXTENSION IF NOT EXISTS vector;

-- Roles
INSERT INTO roles (name, description) VALUES
  ('employee', 'Regular employee — can ask questions and view answers'),
  ('data_manager', 'Pengelola Master Data — manages documents for assigned categories'),
  ('super_admin', 'Super Admin — full platform control')
ON CONFLICT (name) DO NOTHING;

-- Super admin user (password: admin123)
INSERT INTO users (username, email, full_name, hashed_password, role_id, department, is_active)
SELECT 'admin', 'admin@company.com', 'Super Admin', '$2b$12$AwBz6AeYHlIHOyFIPv9mbeLkM4BQLdmajqhOLyZku2LMuhf995suu', r.id, 'IT', true
FROM roles r WHERE r.name = 'super_admin'
ON CONFLICT (username) DO NOTHING;

-- Sample data manager (password: manager123)
INSERT INTO users (username, email, full_name, hashed_password, role_id, department, is_active)
SELECT 'manager_sdm', 'manager.sdm@company.com', 'Manager SDM', '$2b$12$TM/9eHcVOB.0i4u.1IZo/eB84pOpEMASACS5Vieaxnd4sDdimCFIi', r.id, 'SDM', true
FROM roles r WHERE r.name = 'data_manager'
ON CONFLICT (username) DO NOTHING;

-- Sample employee user (password: employee123)
INSERT INTO users (username, email, full_name, hashed_password, role_id, department, is_active)
SELECT 'employee1', 'employee1@company.com', 'Employee Satu', '$2b$12$e4unvMnna/BM1TiCKZdFZeN1v15U5mBahTE9sbRxzsVaJH4Cq1J1y', r.id, 'Finance', true
FROM roles r WHERE r.name = 'employee'
ON CONFLICT (username) DO NOTHING;

-- Sample categories (ON CONFLICT works now with unique constraint on name)
INSERT INTO document_categories (name, description) VALUES
  ('SDM', 'Kebijakan dan SOP Sumber Daya Manusia'),
  ('Keuangan', 'Kebijakan dan SOP Keuangan & Akuntansi'),
  ('IT Security', 'Kebijakan keamanan informasi dan IT'),
  ('Operasional', 'SOP Operasional harian'),
  ('Legal & Compliance', 'Dokumen hukum dan kepatuhan')
ON CONFLICT (name) DO NOTHING;

-- Assign manager_sdm to SDM category
INSERT INTO category_managers (category_id, user_id)
SELECT c.id, u.id
FROM document_categories c, users u
WHERE c.name = 'SDM' AND u.username = 'manager_sdm'
ON CONFLICT DO NOTHING;
