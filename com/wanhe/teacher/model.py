
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

    def exists_by_phone(self, phone):
        db = Database()
        try:
            sql = 'select * from teachers where phone = %s LIMIT 1'
            # res=db.query_one(sql, (phone,))
            res = db.query_one(sql, params=(str(phone).strip(),))
            return res is not None
        finally:
            db.close()

    def create(self, name, gender, age, subject, phone,score,gangwei):
        """
        新增教师
        :return: 新教师自增 ID
        """
        db = Database()
        try:
            return db.insert(
                "INSERT INTO teachers (name, gender, age, subject, phone,score,gangwei) "
                "VALUES (%s, %s, %s, %s, %s,%s,%s)",
                (name, gender, age, subject, phone,score,gangwei)
            )
        finally:
            db.close()

    def update(self, teacher_id, name, gender, age, subject, phone,score,gangwei):
        """
        修改教师信息
        :return: 受影响行数
        """
        db = Database()
        try:
            return db.execute(
                "UPDATE teachers SET name=%s, gender=%s, age=%s, "
                "subject=%s, phone=%s,score=%s,gangwei=%s WHERE id=%s",
                (name, gender, age, subject, phone,score,gangwei,teacher_id)
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