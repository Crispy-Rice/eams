# 导入com.wanhe.common.db下封装的数据库
from com.wanhe.common.db import Database

class StudentModel:
    status_choices = ["在读", "休学", "复学", "退学"]

    def __init__(self):
        self.status = "在读"
    """
        学生模块
    """
    def base_sql(self):
        """
        学生列表，关联班级名，教师名，选课数
        :return: sql,params    返回sql语句和sql查询条件的值
        """
        sql = ("""
        select s.*,
               c.name as class_name,
               t.name as teacher_name,
        (select count(*) from student_course sc where sc.student_id = s.id) as course_count
        from students s
        left join classes c on c.id = s.class_id
        left join teachers t on t.id = s.teacher_id
        """
        )
        # 创建一个空列表，专门用来存放 SQL 查询条件的值。防止sql注入
        params = []
        return sql,params

    def get_all(self, keyword=''):
        """
        查询所有学生信息，可以通过关键字模糊查询
        :param keyword:  姓名关键字
        """
        sql,params = self.base_sql()
        if keyword:
            sql += "where s.name like %s"
            params.append(f"%{keyword}%")
        sql += "order by s.id"
        db = Database()
        try:
            return db.query_all(sql, tuple(params))
        finally:
            db.close()

                                           # 一夜展示的数据数量
    def get_page(self, keyword='', grade='', page=1, page_size=10):
        '''
        分页，每页存放数据量
        :param keyword: 关键字
        :param grade: 年级筛选
        :param page: 页数
        :param page_size: 每页的数据量
        '''
        page = max(1, page)
                           # min()中取最小的数
        page_size = max(1, min(page_size, 100))
        base_sql, params = self.base_sql()
        # 定义空白量，用来存放where语句
        where = ""
        if keyword:
            where += " where s.name like %s"
            params.append(f"%{keyword}%")
        if grade:
            where += " and s.grade = %s" if where else " where s.grade = %s"
            params.append(grade)
        db=Database()
        try:
            total = db.query_one(
                "select count(*) as 总数 from students s " + where, tuple(params)
            )["总数"]
            items = db.query_all(
                # limit限制一页的数据条数，offset代表跳过前面多少条数据，OFFSET = (页码 - 1) × 每页条数
                # 元组之间可以用 + 合并成一个完整大元组
                base_sql + where + "order by s.id limit %s offset %s", tuple(params) + (page_size, (page - 1)*page_size)
            )
            return {"total":total,"items":items}
        finally:
            db.close()

    def get_by_id(self, student_id):
        """
        查询一个学生的信息
        :param student_id:  学生ID
        """
        db = Database()
        try:
            return db.query_one(
                """
                select s.*, c.name as class_name, t.name as teacher_name
                from students s 
                left join classes c on s.class_id = c.id
                left join teachers t on s.teacher_id = t.id
                where s.id = %s
                """, (student_id,)      # 末尾加逗号，Python 才会识别为元组
            )
        finally:
            db.close()

    def create(self, name, gender, age, grade, class_id, teacher_id, enrollment_date):
        """
        添加学生信息
        :param name: 学生姓名
        :param gender: 学生性别
        :param age:学生年龄
        :param grade:学生所属年级
        :param class_id:班级ID
        :param teacher_id:老师ID
        :param enrollment_date:学生入学时间
        """
        db = Database()
        try:
            return db.insert(
                """
                insert into students (name, gender, age, grade, class_id, teacher_id, enrollment_date)
                values (%s, %s, %s, %s, %s, %s, %s)
                """,(name, gender, age, grade, class_id, teacher_id, enrollment_date)
            )
        finally:
            db.close()

    def update(self, student_id, name, gender, age, grade):
        """
        修改学生信息
        :param student_id: 学生ID
        :param name: 学生姓名
        :param gender: 学生性别
        :param age: 学生年龄
        :param grade: 学生所属年级
        """
        db= Database()
        try:
            return db.execute(
                """
                update students set name = %s , gender = %s, age = %s, grade = %s where id = %s
                """, (name, gender, age, grade, student_id)
            )
        finally:
            db.close()

    def change_class(self, student_id, class_id):
        """
        修改学生所属班级ID
        :param student_id: 学生ID
        :param class_id: 班级ID
        """
        db=Database()
        try:
            return db.execute(
                """
                update students set class_id =%s where id = %s
                """, (student_id, class_id)
            )
        finally:
            db.close()

    def change_teacher(self, student_id, teacher_id):
        """
        修改学生所属老师ID
        :param student_id: 学生ID
        :param teacher_id: 老师ID
        """
        db = Database()
        try:
            return db.execute(
                """
                update students set teacher_id = %s where id = %s
                """,(teacher_id, student_id)
            )
        finally:
            db.close()

    def delete(self, student_id):
        '''
        删除学生信息，级联删除
        :param student_id: 学生ID
        '''
        db = Database()
        try:
            db.execute(
                """
                delete from student_course where student_id = %s
                """,(student_id,)
            )
            db.execute(
                """
                delete from users where student_id = %s
                """,(student_id,)
            )
            return db.execute(
                # 需要级联删除
                """
                delete from students where id = %s
                """,(student_id,)
            )
        finally:
            db.close()

    def get_grade(self, grade=''):
        sql, params = self.base_sql()
        if grade:
            sql += "where s.grade = %s"
            params.append(grade)
        sql += " order by s.id"
        db = Database()
        try:
            return db.query_all(sql, tuple(params))
        finally:
            db.close()

    def update_status(self, student_id, status):
        """
        修改学生学籍状态
        :param student_id: 学生ID
        :param status: 新学籍状态
        """
        db = Database()
        try:
            return db.execute(
                "update students set status = %s where id = %s",
                (status, student_id)
            )
        finally:
            db.close()