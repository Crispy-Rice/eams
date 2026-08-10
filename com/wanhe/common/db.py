#文件名：common/db.py
"""
数据库操作封装
基于pymysql 实现 提供连接管理 + 通用增删改查功能
每次调用新建连接 方法内commit 无连接池
"""
import pymysql

from com.wanhe.common.config import settings

# ===== 数据库配置（从.env/settings 读取）
DB_CONFIG = {
    "host": settings.db_host,
    "port": settings.db_port,
    "user": settings.db_user,
    "password": settings.db_password,
    "database": settings.db_name,
    "charset": settings.db_charset,
    "cursorclass": pymysql.cursors.DictCursor, #结果以字典返回
}

class Database:
    """数据库操作封装 每次新建连接 用完 close()关闭"""
    def __init__(self):
        """创建数据库连接"""
        self.conn = pymysql.connect(**DB_CONFIG)

    def close(self):
        """关闭连接 释放资源"""
        if self.conn:
            self.conn.close()

    #----通用查询====
    def query_all(self, sql,params=None):
        """查询多条记录 返回字典列表"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchall()

    def query_one(self, sql,params=None):
        """查询单挑记录 返回字典"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchone()

    #通用增删改
    def execute(self, sql,params=None):
        """
        执行删改语句（update/delete）
        返回受影响行数
        :param sql:
        :param params:
        :return:
        """
        with self.conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            self.conn.commit()
            return cursor.rowcount

    def insert(self, sql,params=None):
        """插入数据 返回新增数据id"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            self.conn.commit()
            return cursor.lastrowid   #自增id
