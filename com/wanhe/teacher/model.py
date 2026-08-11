from com.wanhe.common.db import Database

class TeacherModel:
    '''
    教师表数据访问
    '''

    def get_all(self,keyword=''):
        '''
        查询所有教师，可按姓名模糊查询
        :param keyword:
        :return:
        '''
        sql = 'select * from teacher'
        params=[]
        if keyword:
            sql+='WHERE NAME LIKE %s'
            params.append(f'%{keyword}%')
        sql+="ORDER BY id"
        db = Database()
        try:
            return db.query_all(sql, tuple(params))
        finally:
            db.close()

    def get_one(self,teacher_id):
        '''
        按 ID 查询教师
        :param teacher_id:
        :return:
        '''
        sql = 'select * from teacher where id = %s'
        db = Database()
        try:
            return db.query_one(sql, (teacher_id,))
        finally:
            db.close()

    def exists_by_phone(self,phone):
        db=Database()
        try:
            sql = 'select * from teachers where phone = %s LIMIT 1'
            # res=db.query_one(sql, (phone,))
            res = db.query_one(sql, params=(str(phone).strip(),))
            return res is not None
        finally:
            db.close()

    def create(self,name,gender,age,subject,phone):
        '''
        新增教师
        :param name:
        :param gender:
        :param age:
        :param subject:
        :param phone:
        :return:
        '''
        db = Database()
        try:
            return db.insert(
                "INSERT INTO teachers (name,gender,age,subject,phone) VALUES (%s,%s,%s,%s,%s)"
                ,(name,gender,age,subject,phone)
            )
        finally:
            db.close()

    def update(self,teacher_id,name,gender,age,subject,phone):
        '''
        修改教师信息
        :param teacher_id:
        :param name:
        :param gender:
        :param age:
        :param subject:
        :param phone:
        :return:
        '''
        db = Database()
        try:
            return db.execute(
                "UPDATE teachers SET name=%s,gender=%s,age=%s,subject=%s,phone=%s WHERE id=%s"
                ,(name,gender,age,subject,phone,teacher_id)
            )
        finally:
            db.close()

    def delete(self,teacher_id):
        '''
        删除教师
        :param teacher_id:
        :return:
        '''
        db = Database()
        try:
            return db.execute(
                "DELETE FROM teachers WHERE id=%s"
                ,(teacher_id)
            )
        finally:
            db.close()
