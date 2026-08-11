-- ============================================================
-- EAMS v2 数据库迁移脚本（已有数据库升级用）
-- 执行方式：Navicat 右键 school_db → 运行 SQL 文件 → 选择此文件
-- ============================================================
USE school_db;

-- 1. 课程表：新增容量上限字段（如果不存在）
SET @dbname = 'school_db';
SET @tablename = 'courses';
SET @columnname = 'capacity';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = @dbname
    AND TABLE_NAME = @tablename
    AND COLUMN_NAME = @columnname
  ) = 0,
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' INT DEFAULT NULL COMMENT ''课程容量上限（NULL表示不限）'';'),
  'SELECT 1;'
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2. 课程表：新增先修课程字段（如果不存在）
SET @columnname = 'prerequisite_id';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = @dbname
    AND TABLE_NAME = @tablename
    AND COLUMN_NAME = @columnname
  ) = 0,
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' INT DEFAULT NULL COMMENT ''先修课程ID'';'),
  'SELECT 1;'
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 3. 添加先修课外键（如果不存在）
SET @constraintname = 'fk_courses_prerequisite';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
    WHERE TABLE_SCHEMA = @dbname
    AND TABLE_NAME = @tablename
    AND CONSTRAINT_NAME = @constraintname
  ) = 0,
  CONCAT('ALTER TABLE ', @tablename, ' ADD CONSTRAINT ', @constraintname, ' FOREIGN KEY (prerequisite_id) REFERENCES ', @tablename, '(id) ON DELETE SET NULL;'),
  'SELECT 1;'
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 4. 创建候补队列表（如果不存在）
CREATE TABLE IF NOT EXISTS course_waitlist (
    id          INT         PRIMARY KEY AUTO_INCREMENT COMMENT '候补记录ID',
    student_id  INT         NOT NULL                    COMMENT '学生ID',
    course_id   INT         NOT NULL                    COMMENT '课程ID',
    position    INT         NOT NULL DEFAULT 0          COMMENT '排队序号',
    create_time DATETIME    DEFAULT CURRENT_TIMESTAMP   COMMENT '加入时间',
    UNIQUE KEY uk_waitlist (student_id, course_id)      COMMENT '同一学生同一课程只能候补一次'
) COMMENT '候补队列表';

-- 5. 更新种子数据：给已有课程设置容量和先修（如不存在则忽略）
UPDATE courses SET capacity = 3, prerequisite_id = NULL WHERE name = '数学' AND capacity IS NULL;
UPDATE courses SET capacity = 3, prerequisite_id = NULL WHERE name = '语文' AND capacity IS NULL;
UPDATE courses SET capacity = 2, prerequisite_id = (SELECT id FROM (SELECT id FROM courses WHERE name = '数学') AS t) WHERE name = '英语' AND capacity IS NULL;
UPDATE courses SET capacity = 2, prerequisite_id = (SELECT id FROM (SELECT id FROM courses WHERE name = '数学') AS t) WHERE name = '物理' AND capacity IS NULL;
