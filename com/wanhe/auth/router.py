"""
认证模块 学生注册 登录（公开接口 无鉴权
"""
import logging

from fastapi import APIRouter,HTTPException

from com.wanhe.auth.model import UserModel
from com.wanhe.auth.vo import RegisterUser,LoginUser
from com.wanhe.auth.captcha import generate, verify
from com.wanhe.student.model import StudentModel
from com.wanhe.common.response import  success

logger=logging.getLogger(__name__)

#创建子路由 统一接口前缀 文档标签

router = APIRouter(prefix="/auth", tags=["认证模块"])

@router.post("/register") # 路由装饰器：注册 POST 新增接口
def register_user(user: RegisterUser):
    """
    学生自主注册
    流程：先创建学生记录 → 再用学生ID创建登录账号（密码明文存储，教学演示）
    :param data: 注册请求体（用户名/密码/姓名/性别/年龄）
    :return: {"student_id", "username"}
    :raises HTTPException 400: 用户名已存在
    """
    # 1. 检查用户名是否已被占用
    if UserModel().find_by_username(user.username):
        logger.warning("注册失败，该用户名已存在：%s", user.username)
        raise  HTTPException(status_code = 400,detail="用户名已存在")

    #2 创建学生记录（初始未分班 未选老师）
    student_id = StudentModel().create(
        name=user.name,
        gender=user.gender,
        age=user.age,
        grade='高一',
        class_id=None,
        teacher_id=None,
        enrollment_date='2025-09-01',
    )
    # 注册学生默认学籍状态为「在读」（在校），与 status_choices 一致
    StudentModel().update_status(student_id, '在读')

    # 3. 创建登录账号，关联学生ID
    UserModel().create(
        username=user.username,
        password=user.password,
        role='student',
        student_id=student_id,
    )

    # 4. 注册成功即自动登录：查询刚创建的用户，返回与 /auth/login 完全一致的登录态信息
    #    （演示架构无真实 token/session，登录态=客户端拿到 user 信息并存入 localStorage）
    userSearch = UserModel().find_by_username(user.username)

    logger.info("注册成功并自动登录 用户：%s", user.username)
    return success({
        "user_id": userSearch['id'],
        "username": userSearch['username'],
        "role": userSearch['role'],
        "student_id": userSearch['student_id'],
    }, msg="注册成功，已自动登录")

@router.get("/captcha") # 获取图片验证码（公开接口，登录前调用）
def get_captcha():
    """
    获取图片验证码：生成 4 位图文验证码并返回 base64 图片 + token
    :return: {"token", "image"}  前端将 image 赋给 <img src>，登录时回传 token
    """
    token, image = generate()
    logger.info("生成验证码 token=%s", token)
    return success({"token": token, "image": image}, msg="获取验证码成功")

@router.post("/login") # 路由装饰器：注册 POST 新增接口
def login_user(user: LoginUser):
    """
    登录：先校验图片验证码，再校验用户名和密码（明文比对，教学演示）
    学生角色额外校验学籍状态：仅「在读」/「复学」可登录（休学/退学不可）
    :param data: 登录请求体（用户名/密码/验证码 token/验证码）
    :return: {"user_id", "username", "role", "student_id"}
    :raises HTTPException 400: 验证码错误或已过期 / 用户名或密码错误 / 学生学籍状态异常
    """
    # 0. 先校验图片验证码（防暴力破解；一次性使用，校验失败需重新获取）
    if not verify(user.captcha_token, user.captcha_code):
        logger.warning("登录失败 验证码错误 用户：%s", user.username)
        raise HTTPException(status_code=400, detail="验证码错误或已过期")

    userSearch = UserModel().find_by_username(user.username)

    #用户不存在或密码错误
    if userSearch is None or user.password != userSearch["password"]:
        logger.warning("登录失败 用户：%s", user.username)
        raise HTTPException(status_code=400,detail="用户名或密码错误")

    # 学生角色学籍闸门：仅「在读」/「复学」可登录
    if userSearch["role"] == "student":
        sid = userSearch.get("student_id")
        student = StudentModel().get_by_id(sid) if sid else None
        if student is None:
            logger.warning("登录失败 学生信息不存在 student_id:%s", sid)
            raise HTTPException(status_code=400, detail="学生信息不存在，无法登录")
        status = student.get("status")
        if status not in ("在读", "复学"):
            logger.warning("登录失败 学籍状态异常 用户:%s 状态:%s", user.username, status)
            raise HTTPException(status_code=400, detail=f"该学生学籍状态为「{status}」，仅在校/复学状态可登录")

    # 返回用户基本信息（无 token，教学演示）
    logger.info("登录成功 用户:%s 角色:%s", userSearch["username"], userSearch['role'])
    return success({
        "user_id": userSearch['id'],
        "username": userSearch['username'],
        "role": userSearch['role'],
        "student_id": userSearch['student_id'],
    }, msg="登录成功")