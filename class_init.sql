--创建班级表--
CREATE TABLE IF NOT EXISTS classes (
    id              INT         PRIMARY KEY AUTO_INCREMENT COMMENT '班级ID',
    name            VARCHAR(50) NOT NULL                    COMMENT '班级名称，如：高一(1)班',
    grade           VARCHAR(20)                             COMMENT '年级：高一/高二/高三',
    head_teacher_id INT                                     COMMENT '班主任教师ID',
    create_time     DATETIME    DEFAULT CURRENT_TIMESTAMP   COMMENT '创建时间'
) COMMENT '班级表';
-- 班级示例（班主任关联教师）
INSERT INTO classes (name, grade, head_teacher_id) VALUES
    ('高一(1)班', '高一', 1),
    ('高一(2)班', '高一', 2),
    ('高二(1)班', '高二', 3),
    ('高三(1)班', '高三', 4);

ALTER TABLE classes
ADD COLUMN if_youxiu VARCHAR(20) COMMENT '本班级是否为优秀班级',
ADD COLUMN student_num INT DEFAULT 0 COMMENT '本班学生数目',
ADD COLUMN graduation_year INT NULL COMMENT '本班学生毕业年份';