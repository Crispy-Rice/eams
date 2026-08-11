# 文件名：stats/model.py
"""
统计模块 - 数据访问层

职责：封装首页统计分析的 SQL（各班级人数、学生男女占比）
依赖：common.db.Database（每次新建连接，方法内 commit）
"""
import logging

from com.wanhe.common.db import Database

logger = logging.getLogger(__name__)


class StatsModel:
    """统计数据分析"""

    def class_count(self):
        """
        统计各班级人数（含班级名与年级），供柱状图展示
        LEFT JOIN：无学生的班级也返回 cnt=0
        :return: [{class_name, grade, cnt}, ...] 按年级、班级ID排序
        """
        db = Database()
        try:
            rows = db.query_all(
                "SELECT c.id, c.name AS class_name, c.grade, COUNT(s.id) AS cnt "
                "FROM classes c LEFT JOIN students s ON s.class_id = c.id "
                "GROUP BY c.id, c.name, c.grade "
                "ORDER BY c.grade, c.id"
            )
            logger.info("统计各班级人数，返回 %s 条", len(rows))
            return rows
        finally:
            db.close()

    def gender_ratio(self):
        """
        统计在校学生男女占比，供饼状图展示
        :return: [{gender, cnt}, ...]（男/女各自人数）
        """
        db = Database()
        try:
            rows = db.query_all(
                "SELECT gender, COUNT(*) AS cnt FROM students GROUP BY gender"
            )
            logger.info("统计在校学生男女占比，返回 %s 条", len(rows))
            return rows
        finally:
            db.close()










    # ===== 新增：各年级学生人数统计 =====
    def grade_count(self):
        """
        统计各年级学生人数，供柱状图展示
        :return: [{grade, cnt}, ...]（按年级排序）
        """
        db = Database()
        try:
            rows = db.query_all(
                "SELECT grade, COUNT(*) AS cnt FROM students "
                "GROUP BY grade ORDER BY grade"
            )
            logger.info("统计各年级学生人数，返回 %s 条", len(rows))
            return rows
        finally:
            db.close()

    # ===== 新增：每门课程选课人数统计 =====
    def course_selection(self):
        """
        统计每门课程选课人数（含无人选的课）
        LEFT JOIN：无人选的课程也返回 cnt=0
        :return: [{course_name, cnt}, ...]（按选课人数降序）
        """
        db = Database()
        try:
            rows = db.query_all(
                "SELECT c.name AS course_name, COUNT(sc.id) AS cnt "
                "FROM courses c LEFT JOIN student_course sc ON sc.course_id = c.id "
                "GROUP BY c.id, c.name ORDER BY cnt DESC"
            )
            logger.info("统计每门课程选课人数，返回 %s 条", len(rows))
            return rows
        finally:
            db.close()
