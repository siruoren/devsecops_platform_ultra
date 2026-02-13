-- ============================================================================
-- 质量安全平台 QSP v3.0 - PostgreSQL 完整初始化脚本
-- 适用版本: 3.0.0
-- 包含: 表结构、约束、索引、初始权限、角色、管理员账户、系统配置
-- ============================================================================

-- 启用必要扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================ 1. Django 基础表 ============================
CREATE TABLE django_content_type (
    id SERIAL PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    CONSTRAINT django_content_type_app_label_model_uniq UNIQUE (app_label, model)
);

CREATE TABLE django_migrations (
    id SERIAL PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE django_session (
    session_key VARCHAR(40) PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE INDEX django_session_expire_date_idx ON django_session (expire_date);

CREATE TABLE django_admin_log (
    id SERIAL PRIMARY KEY,
    action_time TIMESTAMP WITH TIME ZONE NOT NULL,
    object_id TEXT,
    object_repr VARCHAR(200) NOT NULL,
    action_flag SMALLINT NOT NULL CHECK (action_flag BETWEEN 1 AND 3),
    change_message TEXT NOT NULL,
    content_type_id INTEGER REFERENCES django_content_type(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL
);

-- ============================ 2. 用户模块 ============================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) NOT NULL UNIQUE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL,
    avatar VARCHAR(100),
    phone VARCHAR(20) NOT NULL DEFAULT '',
    department VARCHAR(100) NOT NULL DEFAULT '',
    position VARCHAR(100) NOT NULL DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

ALTER TABLE django_admin_log ADD CONSTRAINT django_admin_log_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- ============================ 3. RBAC 权限系统 ============================
CREATE TABLE rbac_permissions (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    module VARCHAR(50) NOT NULL,
    is_menu BOOLEAN NOT NULL DEFAULT FALSE,
    parent_id INTEGER REFERENCES rbac_permissions(id) ON DELETE SET NULL
);

CREATE TABLE rbac_roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT ''
);

CREATE TABLE rbac_roles_permissions (
    id SERIAL PRIMARY KEY,
    role_id INTEGER NOT NULL REFERENCES rbac_roles(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES rbac_permissions(id) ON DELETE CASCADE,
    UNIQUE (role_id, permission_id)
);

CREATE TABLE rbac_user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES rbac_roles(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    UNIQUE (user_id, role_id)
);

-- ============================ 4. 项目管理 ============================
CREATE TABLE environments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    server_ips TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE,
    git_repo VARCHAR(200) NOT NULL,
    git_path VARCHAR(500) NOT NULL DEFAULT '/',
    environment_id INTEGER NOT NULL REFERENCES environments(id) ON DELETE PROTECT,
    deploy_dir VARCHAR(500) NOT NULL,
    start_script VARCHAR(500) NOT NULL,
    stop_script VARCHAR(500) NOT NULL,
    start_cron VARCHAR(100) NOT NULL DEFAULT '',
    stop_cron VARCHAR(100) NOT NULL DEFAULT '',
    sonarqube_url VARCHAR(200) NOT NULL DEFAULT '',
    owner_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE INDEX projects_owner_id_idx ON projects (owner_id);
CREATE INDEX projects_environment_id_idx ON projects (environment_id);

-- ============================ 5. 版本管理 ============================
CREATE TABLE release_versions (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    released_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) NOT NULL DEFAULT 'developing',
    code_quality JSONB NOT NULL DEFAULT '{}',
    created_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE version_registrations (
    id SERIAL PRIMARY KEY,
    release_version_id INTEGER NOT NULL REFERENCES release_versions(id) ON DELETE CASCADE,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    app_version VARCHAR(50) NOT NULL,
    created_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    UNIQUE (release_version_id, project_id)
);
CREATE INDEX version_registrations_release_version_id_idx ON version_registrations (release_version_id);
CREATE INDEX version_registrations_project_id_idx ON version_registrations (project_id);

-- ============================ 6. 安全漏洞管理 ============================
CREATE TABLE vulnerability_dependencycheckscans (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    scan_date TIMESTAMP WITH TIME ZONE NOT NULL,
    json_result JSONB NOT NULL,
    summary JSONB NOT NULL DEFAULT '{}',
    created_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE vulnerability_artifactvulnerabilities (
    id SERIAL PRIMARY KEY,
    scan_id INTEGER NOT NULL REFERENCES vulnerability_dependencycheckscans(id) ON DELETE CASCADE,
    artifact_name VARCHAR(500) NOT NULL,
    artifact_version VARCHAR(100) NOT NULL,
    cve VARCHAR(50) NOT NULL DEFAULT '',
    severity VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    remediation TEXT NOT NULL DEFAULT '',
    cvss_score DOUBLE PRECISION
);
CREATE INDEX idx_artifact_name ON vulnerability_artifactvulnerabilities (artifact_name);
CREATE INDEX idx_artifact_cve ON vulnerability_artifactvulnerabilities (cve);

CREATE TABLE vulnerability_artifactversionchanges (
    id SERIAL PRIMARY KEY,
    release_version_id INTEGER NOT NULL REFERENCES release_versions(id) ON DELETE CASCADE,
    group_id VARCHAR(200) NOT NULL,
    artifact_id VARCHAR(200) NOT NULL,
    version VARCHAR(100) NOT NULL,
    notify_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- ============================ 7. CI/CD 流水线 ============================
CREATE TABLE cicd_pipelines (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    description TEXT NOT NULL DEFAULT '',
    created_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE cicd_stages (
    id SERIAL PRIMARY KEY,
    pipeline_id INTEGER NOT NULL REFERENCES cicd_pipelines(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    "order" INTEGER NOT NULL,
    script TEXT NOT NULL DEFAULT '',
    timeout INTEGER NOT NULL DEFAULT 3600
);

CREATE TABLE cicd_builds (
    id SERIAL PRIMARY KEY,
    build_id UUID NOT NULL UNIQUE DEFAULT uuid_generate_v4(),
    pipeline_id INTEGER NOT NULL REFERENCES cicd_pipelines(id) ON DELETE CASCADE,
    version VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    triggered_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    started_at TIMESTAMP WITH TIME ZONE,
    finished_at TIMESTAMP WITH TIME ZONE,
    duration INTEGER,
    sonar_task_id VARCHAR(100) NOT NULL DEFAULT '',
    sonar_quality_gate VARCHAR(50) NOT NULL DEFAULT '',
    risk_score DOUBLE PRECISION,
    log_file TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE INDEX cicd_builds_pipeline_id_idx ON cicd_builds (pipeline_id);
CREATE INDEX cicd_builds_status_idx ON cicd_builds (status);

CREATE TABLE cicd_build_stages (
    id SERIAL PRIMARY KEY,
    build_id INTEGER NOT NULL REFERENCES cicd_builds(id) ON DELETE CASCADE,
    stage_id INTEGER NOT NULL REFERENCES cicd_stages(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE,
    finished_at TIMESTAMP WITH TIME ZONE,
    log_snippet TEXT NOT NULL DEFAULT ''
);

-- ============================ 8. 风险评分系统 ============================
CREATE TABLE risk_profiles (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL UNIQUE REFERENCES projects(id) ON DELETE CASCADE,
    overall_score DOUBLE PRECISION NOT NULL DEFAULT 0,
    code_quality_score DOUBLE PRECISION NOT NULL DEFAULT 0,
    vulnerability_score DOUBLE PRECISION NOT NULL DEFAULT 0,
    pipeline_health_score DOUBLE PRECISION NOT NULL DEFAULT 0,
    last_scan_time TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE risk_alerts (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    level VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_resolved BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX risk_alerts_project_id_idx ON risk_alerts (project_id);

-- ============================ 9. 系统管理 ============================
CREATE TABLE system_config (
    id INTEGER PRIMARY KEY DEFAULT 1,
    web_port INTEGER NOT NULL DEFAULT 8000,
    db_connection JSONB NOT NULL DEFAULT '{}',
    max_daily_messages INTEGER NOT NULL DEFAULT 100,
    smtp_server VARCHAR(255) NOT NULL DEFAULT '',
    smtp_port INTEGER NOT NULL DEFAULT 587,
    smtp_username VARCHAR(255) NOT NULL DEFAULT '',
    smtp_password VARCHAR(255) NOT NULL DEFAULT '',
    sender_email VARCHAR(254) NOT NULL DEFAULT '',
    sender_name VARCHAR(100) NOT NULL DEFAULT '质量安全平台',
    max_daily_emails INTEGER NOT NULL DEFAULT 500,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT system_config_single_row CHECK (id = 1)
);

CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    recipient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sender_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    read_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX notifications_recipient_id_idx ON notifications (recipient_id);
CREATE INDEX notifications_created_at_idx ON notifications (created_at);

-- ============================ 10. Constance 动态配置 ============================
CREATE TABLE constance_config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) NOT NULL UNIQUE,
    value TEXT NOT NULL
);

-- ============================ 11. 初始数据插入 ============================

-- 11.1 超级管理员 (密码: admin123)
INSERT INTO users (
    password, last_login, is_superuser, username, first_name, last_name,
    email, is_staff, is_active, date_joined, avatar, phone, department,
    position, created_at, updated_at
) VALUES (
    'pbkdf2_sha256$260000$wE6c3vQyqY8H$z8jYz1cLzX5F3k2n8hQyU4sT7wA9vR6mJcN2gK5dM3I=',
    NULL, TRUE, 'admin', '', '', 'admin@example.com',
    TRUE, TRUE, NOW(), NULL, '', '', '', NOW(), NOW()
);

-- 11.2 默认权限
INSERT INTO rbac_permissions (code, name, module, is_menu) VALUES
('user_view', '查看用户', 'user', FALSE),
('user_add', '新建用户', 'user', FALSE),
('user_edit', '编辑用户', 'user', FALSE),
('user_delete', '删除用户', 'user', FALSE),
('user_menu', '用户管理', 'user', TRUE),

('project_view', '查看项目', 'project', FALSE),
('project_add', '新建项目', 'project', FALSE),
('project_edit', '编辑项目', 'project', FALSE),
('project_delete', '删除项目', 'project', FALSE),
('project_menu', '项目管理', 'project', TRUE),

('version_view', '查看版本', 'version', FALSE),
('version_edit', '编辑版本', 'version', FALSE),
('version_menu', '版本管理', 'version', TRUE),

('vuln_view', '查看漏洞', 'vuln', FALSE),
('vuln_import', '导入漏洞', 'vuln', FALSE),
('vuln_menu', '安全漏洞', 'vuln', TRUE),

('system_config', '系统配置', 'system', TRUE),

('cicd_view', '查看流水线', 'cicd', FALSE),
('cicd_trigger', '触发构建', 'cicd', FALSE),
('cicd_menu', 'CI/CD', 'cicd', TRUE),

('risk_view', '风险看板', 'risk', TRUE);

-- 11.3 默认角色
INSERT INTO rbac_roles (name, code, description) VALUES
('系统管理员', 'admin', '拥有所有权限'),
('开发人员', 'developer', '开发人员只读权限及触发构建'),
('测试人员', 'qa', '测试人员可导入漏洞'),
('运维人员', 'ops', '运维人员可管理流水线'),
('项目经理', 'pm', '项目经理可查看所有项目风险');

-- 11.4 角色-权限分配
-- 系统管理员拥有所有权限
INSERT INTO rbac_roles_permissions (role_id, permission_id)
SELECT (SELECT id FROM rbac_roles WHERE code = 'admin'), id
FROM rbac_permissions;

-- 开发人员权限
INSERT INTO rbac_roles_permissions (role_id, permission_id)
SELECT (SELECT id FROM rbac_roles WHERE code = 'developer'), id
FROM rbac_permissions WHERE code IN (
    'project_view', 'version_view', 'vuln_view', 'cicd_view', 'cicd_trigger', 'risk_view'
);

-- 测试人员权限
INSERT INTO rbac_roles_permissions (role_id, permission_id)
SELECT (SELECT id FROM rbac_roles WHERE code = 'qa'), id
FROM rbac_permissions WHERE code IN (
    'project_view', 'version_view', 'vuln_view', 'vuln_import', 'risk_view'
);

-- 11.5 分配管理员角色给 admin 用户
INSERT INTO rbac_user_roles (user_id, role_id, created_at)
SELECT id, (SELECT id FROM rbac_roles WHERE code = 'admin'), NOW()
FROM users WHERE username = 'admin';

-- 11.6 系统配置初始化
INSERT INTO system_config (
    id, web_port, max_daily_messages, smtp_server, smtp_port,
    smtp_username, smtp_password, sender_email, sender_name,
    max_daily_emails, updated_at
) VALUES (
    1, 8000, 100, 'smtp.example.com', 587,
    '', '', 'noreply@qsp.com', '质量安全平台',
    500, NOW()
);

-- 11.7 Django Content Types 初始化（核心）
INSERT INTO django_content_type (app_label, model) VALUES
('users', 'user'),
('rbac', 'permission'),
('rbac', 'role'),
('rbac', 'userrole'),
('projects', 'environment'),
('projects', 'project'),
('versions', 'releaseversion'),
('versions', 'versionregistration'),
('vulnerabilities', 'dependencycheckscan'),
('vulnerabilities', 'artifactvulnerability'),
('vulnerabilities', 'artifactversionchange'),
('ci_cd', 'pipeline'),
('ci_cd', 'pipelinestage'),
('ci_cd', 'buildrecord'),
('ci_cd', 'buildstagerecord'),
('risk', 'riskprofile'),
('risk', 'riskalert'),
('system', 'systemconfig'),
('system', 'notification');

-- ============================ 12. 提交事务 ============================
COMMIT;

-- 脚本结束