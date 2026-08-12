# 文件名：teacher/model.py
"""
教师模块 - 数据访问层

职责：封装 teachers 表 SQL 操作（增删改查 + 按姓名关键字查询 + 新增前查重）
依赖：common.db.Database、fastapi.HTTPException
"""
from fastapi import HTTPException

from com.wanhe.common.db import Database


def _resolve_gangwei(score):
    """
    根据教师评教分数自动生成岗位
    :param score: 评教分数
    :return: 评教分数 >= 85 为班主任，否则为任课教师
    """
    return "班主任" if score >= 85 else "任课教师"


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

    def get_by_name(self, name):
        """
        按姓名精确查询教师（新增前查重用）
        :param name: 教师姓名
        :return: 教师行 dict；不存在返回 None
        """
        db = Database()
        try:
            return db.query_one("SELECT * FROM teachers WHERE name = %s", (name,))
        finally:
            db.close()

    def create(self, name, gender, age, subject, phone, score, gangwei=None):
        """
        新增教师（同名教师已存在时插入失败）
        :param name: 姓名
        :param score: 教师评教分数（新增时必传）
        :param gangwei: 岗位（不传则按评教分数自动生成：>=85 为班主任，否则为任课教师）
        :return: 新教师自增 ID
        :raise HTTPException 400: 同名教师已存在，插入失败
        """
        if self.get_by_name(name) is not None:
            raise HTTPException(status_code=400, detail="教师已存在，插入失败")
        if gangwei is None:
            gangwei = _resolve_gangwei(score)
        db = Database()
        try:
            return db.insert(
                "INSERT INTO teachers (name, gender, age, subject, phone, score, gangwei) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (name, gender, age, subject, phone, score, gangwei)
            )
        finally:
            db.close()

    def update(self, teacher_id, name, gender, age, subject, phone, score, gangwei=None):
        """
        修改教师信息
        :param score: 教师评教分数
        :param gangwei: 岗位（不传则按评教分数自动生成）
        :return: 受影响行数
        """
        if gangwei is None:
            gangwei = _resolve_gangwei(score)
        db = Database()
        try:
            return db.execute(
                "UPDATE teachers SET name=%s, gender=%s, age=%s, "
                "subject=%s, phone=%s, score=%s, gangwei=%s WHERE id=%s",
                (name, gender, age, subject, phone, score, gangwei, teacher_id)
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
