-- =====================================================
-- PROFILE
-- =====================================================

CREATE TABLE profile (
    profile_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL UNIQUE,
    display_name        TEXT NOT NULL,
    theme               TEXT DEFAULT 'system',
    timezone            TEXT DEFAULT 'Asia/Kolkata',
    created_at          DATETIME NOT NULL,
    updated_at          DATETIME NOT NULL,

    FOREIGN KEY(user_id) REFERENCES auth_user(id)
);

-- =====================================================
-- SECURITY
-- =====================================================

CREATE TABLE security (
    security_id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                         INTEGER NOT NULL UNIQUE,

    lock_password                   TEXT,
    delete_password                 TEXT,

    anime_delete_after_hours        INTEGER DEFAULT 48,
    worklog_delete_after_hours      INTEGER DEFAULT 48,
    notes_delete_after_hours        INTEGER DEFAULT 48,
    expense_delete_after_hours      INTEGER DEFAULT 48,

    lock_password_reset_at          DATETIME,
    delete_password_reset_at        DATETIME,

    created_at                      DATETIME NOT NULL,
    updated_at                      DATETIME NOT NULL,

    FOREIGN KEY(user_id) REFERENCES auth_user(id)
);

-- =====================================================
-- PROJECT
-- =====================================================

CREATE TABLE project (
    project_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,

    project_name        TEXT NOT NULL,
    description         TEXT,

    is_active           INTEGER DEFAULT 1,

    created_at          DATETIME NOT NULL,
    updated_at          DATETIME NOT NULL,

    FOREIGN KEY(user_id) REFERENCES auth_user(id),

    UNIQUE(user_id, project_name)
);

-- =====================================================
-- CATEGORY
-- =====================================================

CREATE TABLE category (
    category_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,

    category_name       TEXT NOT NULL,
    description         TEXT,

    is_active           INTEGER DEFAULT 1,

    created_at          DATETIME NOT NULL,
    updated_at          DATETIME NOT NULL,

    FOREIGN KEY(user_id) REFERENCES auth_user(id),

    UNIQUE(user_id, category_name)
);

-- =====================================================
-- PAYMENT METHOD
-- =====================================================

CREATE TABLE payment_method (
    payment_method_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                 INTEGER NOT NULL,

    payment_method_name     TEXT NOT NULL,

    is_active               INTEGER DEFAULT 1,

    created_at              DATETIME NOT NULL,
    updated_at              DATETIME NOT NULL,

    FOREIGN KEY(user_id) REFERENCES auth_user(id),

    UNIQUE(user_id, payment_method_name)
);

-- =====================================================
-- ANIME STATUS
-- =====================================================

CREATE TABLE anime_status (
    status_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                 INTEGER NOT NULL,

    status_name         TEXT NOT NULL UNIQUE

    is_active               INTEGER DEFAULT 1,

    created_at              DATETIME NOT NULL,
    updated_at              DATETIME NOT NULL,

    FOREIGN KEY(status_id) REFERENCES auth_user(id),

    UNIQUE(user_id, status_name)

);

-- =====================================================
-- ANIME
-- =====================================================

CREATE TABLE anime (
    anime_id                INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                 INTEGER NOT NULL,

    anime_name              TEXT NOT NULL,

    status_id               INTEGER,

    total_episode           INTEGER,
    watched_episode         INTEGER DEFAULT 0,

    notes                   TEXT,

    delete_status           INTEGER DEFAULT 0,
    deleted_at              DATETIME,

    created_at              DATETIME NOT NULL,
    updated_at              DATETIME NOT NULL,

    FOREIGN KEY(user_id) REFERENCES auth_user(id),
    FOREIGN KEY(status_id) REFERENCES anime_status(status_id)
);

-- =====================================================
-- WORK LOG
-- =====================================================

CREATE TABLE work_log (
    worklog_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,

    project_id          INTEGER,
    category_id         INTEGER,

    title               TEXT,
    notes               TEXT NOT NULL,

    work_date           DATE NOT NULL,

    duration            TEXT,

    delete_status       INTEGER DEFAULT 0,
    deleted_at          DATETIME,

    created_at          DATETIME NOT NULL,
    updated_at          DATETIME NOT NULL,

    FOREIGN KEY(user_id) REFERENCES auth_user(id),
    FOREIGN KEY(project_id) REFERENCES project(project_id),
    FOREIGN KEY(category_id) REFERENCES category(category_id)
);

-- =====================================================
-- PERSONAL NOTE
-- =====================================================

CREATE TABLE personal_note (
    note_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,

    title               TEXT,
    content             TEXT NOT NULL,

    is_pinned           INTEGER DEFAULT 0,
    is_locked           INTEGER DEFAULT 0,
    is_encrypted        INTEGER DEFAULT 0,

    delete_status       INTEGER DEFAULT 0,
    deleted_at          DATETIME,

    created_at          DATETIME NOT NULL,
    updated_at          DATETIME NOT NULL,

    FOREIGN KEY(user_id) REFERENCES auth_user(id)
);

-- =====================================================
-- EXPENSE
-- =====================================================

CREATE TABLE expense (
    expense_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                 INTEGER NOT NULL,

    payment_method_id       INTEGER,

    amount                  DECIMAL(12,2) NOT NULL,

    amount_type             TEXT NOT NULL,

    expense_date            DATE NOT NULL,

    notes                   TEXT NOT NULL,

    delete_status           INTEGER DEFAULT 0,
    deleted_at              DATETIME,

    created_at              DATETIME NOT NULL,
    updated_at              DATETIME NOT NULL,

    FOREIGN KEY(user_id) REFERENCES auth_user(id),
    FOREIGN KEY(payment_method_id) REFERENCES payment_method(payment_method_id)
);
