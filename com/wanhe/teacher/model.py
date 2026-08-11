# 文件名：teacher/model.py
"""
教师模块 - 数据访问层

职责：封装 teachers 表 SQL 操作（增删改查 + 按姓名关键字查询）
依赖：common.db.Database
"""
from com.wanhe.common.db import Database


class TeacherModel:
    """教师表数据访问"""

    def get_all(self, keyword=''):
        """
        查询所有教师，可按姓名模糊查询
        :param keyword: 姓名关键字（可选）
        :return: 教师行字典列表
        """
        sql = "SELECT * FROM teachers "
        params = []
        if keyword:
            sql += "WHERE name LIKE %s "
            params.append(f"%{keyword}%")
        sql += "ORDER BY id"
        db = Database()
        try:
            return db.query_all(sql, tuple(params))
        finally:
            db.close()

    def get_by_id(self, teacher_id):
        """
        按 ID 查询教师
        :param teacher_id: 教师 ID
        :return: 教师行 dict；不存在返回 None
        """
        db = Database()
        try:
            return db.query_one("SELECT * FROM teachers WHERE id = %s", (teacher_id,))
        finally:
            db.close()

    def create(self, name, gender, age, subject, phone):
        """
        新增教师
        :return: 新教师自增 ID
        """
        db = Database()
        try:
            return db.insert(
                "INSERT INTO teachers (name, gender, age, subject, phone) "
                "VALUES (%s, %s, %s, %s, %s)",
                (name, gender, age, subject, phone)
            )
        finally:
            db.close()

    def update(self, teacher_id, name, gender, age, subject, phone):
        """
        修改教师信息
        :return: 受影响行数
        """
        db = Database()
        try:
            return db.execute(
                "UPDATE teachers SET name=%s, gender=%s, age=%s, "
                "subject=%s, phone=%s WHERE id=%s",
                (name, gender, age, subject, phone, teacher_id)
            )
        finally:
            db.close()

    def delete(self, teacher_id):
        """
        删除教师
        :return: 受影响行数
        """
        db = Database()
        try:
            return db.execute("DELETE FROM teachers WHERE id = %s", (teacher_id,))
        finally:
            db.close()