# 文件名：stats/router.py
"""
统计模块：首页统计分析接口（公开，无鉴权）

职责：
- GET /stats/class-count：各班级人数统计（柱状图数据源）
- GET /stats/gender-ratio：在校学生男女占比（饼状图数据源）
"""
import logging

from fastapi import APIRouter

from com.wanhe.stats.model import StatsModel
from com.wanhe.common.response import success

logger = logging.getLogger(__name__)

# 创建子路由
router = APIRouter(prefix="/stats", tags=["统计模块"])


@router.get("/class-count")  # 路由装饰器：注册 GET 查询接口
def class_count():
    """查：各班级人数统计（柱状图数据源）"""
    logger.info("查询各班级人数统计")
    return success(StatsModel().class_count())


@router.get("/gender-ratio")  # 路由装饰器：注册 GET 查询接口
def gender_ratio():
    """查：在校学生男女占比（饼状图数据源）"""
    logger.info("查询在校学生男女占比")
    return success(StatsModel().gender_ratio())

@router.get("/")
def index(username: str = "访客", role: str = "guest"):
    """
    首页欢迎语：显示当前登录用户（教学演示：身份由前端查询参数传递）
    :param username: 当前登录用户名（前端登录后从 localStorage 读取并携带）
    :param role: 当前登录用户角色（admin / teacher / student）
    :return: {"message": "欢迎使用学校教务管理系统，<角色> <用户名>！"}
    """
    role_map = {"admin": "管理员", "teacher": "教师", "student": "学生"}
    role_name = role_map.get(role, "用户")
    logger.info("访问首页 用户:%s 角色:%s", username, role)
    return success({"message": f"欢迎使用学校教务管理系统，{role_name} {username}！"})


@router.get("/grade-count")  # 路由装饰器：注册 GET 查询接口
def grade_count():
    """查：各年级学生人数（柱状图数据源）"""
    logger.info("查询各年级学生人数")
    return success(StatsModel().grade_count())


@router.get("/course-selection")  # 路由装饰器：注册 GET 查询接口
def course_selection():
    """查：每门课程选课人数排行（柱状图数据源）"""
    logger.info("查询每门课程选课人数")
    return success(StatsModel().course_selection())


@router.get("/gender-grade")  # 路由装饰器：注册 GET 查询接口
def gender_grade():
    """查：各年级男女生人数（堆叠柱状图数据源）"""
    logger.info("查询各年级男女生人数")
    return success(StatsModel().gender_grade())