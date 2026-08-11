-- 班级表补充字段迁移脚本
-- 说明：init.sql 现已直接包含 if_youxiu / student_num / graduation_year 三列，
--       因此本脚本仅用于「老库升级」场景（在已有的 classes 表上补列），
--       采用条件判断，可重复执行、不会因列已存在而报错。
-- 执行方式：mysql -uroot -p school_db < class_init.sql

USE school_db;

SET @dbname = 'school_db';
SET @tablename = 'classes';

-- if_youxiu：本班级是否为优秀班级
SET @columnname = 'if_youxiu';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) = 0,
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' VARCHAR(20) COMMENT ''本班级是否为优秀班级'''),
  'SELECT 1'));
PREPARE stmt FROM @preparedStatement; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- student_num：本班学生数目
SET @columnname = 'student_num';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) = 0,
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' INT DEFAULT 0 COMMENT ''本班学生数目'''),
  'SELECT 1'));
PREPARE stmt FROM @preparedStatement; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- graduation_year：本班学生毕业年份
SET @columnname = 'graduation_year';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) = 0,
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' INT NULL COMMENT ''本班学生毕业年份'''),
  'SELECT 1'));
PREPARE stmt FROM @preparedStatement; EXECUTE stmt; DEALLOCATE PREPARE stmt;
