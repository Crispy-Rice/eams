import logging

# fastapi 接收请求 → 去数据库取数据 → 打包成 JSON
# APIRouter 导入路由管理器
# HTTPException 异常抛出工具
from fastapi import APIRouter, HTTPException

from com.wanhe.student.model import StudentModel
from com.wanhe.student.vo import StudentCreate, StudentUpdate, ClassAssign, TeacherAssign, StudentStatus
from com.wanhe.classes.model import ClassModel
from com.wanhe.teacher.model import TeacherModel
from com.wanhe.common.response import success

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/students", tags=["学生模块"])


@router.get("/all")
def list_students(keyword: str = ""):
    '''
    查询所有学生，用关键词区分
    '''
    return success(StudentModel().get_all(keyword))


@router.get("/page")
def list_students_page(keyword: str = "", page: int = 1, page_size: int = 10):
    '''
    分页
    '''
    return success(StudentModel().get_page(keyword, page, page_size))


@router.get("/one/{student_id}")
def get_student(student_id: int):
    '''
    查询一个学生信息
    '''
    if StudentModel().get_by_id(student_id) is None:
        # raise 主动抛出异常
        raise HTTPException(status_code=404, detail="学生不存在")
    return success(StudentModel().get_by_id(student_id))


@router.post("/add")
def add_student(data: StudentCreate):
    '''
    新增学生信息
    '''
    if data.class_id and ClassModel().get_by_id(data.class_id) is None:
        raise HTTPException(status_code=404, detail="班级不存在")
    if data.teacher_id and TeacherModel().get_by_id(data.teacher_id) is None:
        raise HTTPException(status_code=404, detail="教师不存在")

    new_id = StudentModel().create(
        name=data.name,
        gender=data.gender,
        age=data.age,
        grade=data.grade,
        class_id=data.class_id,
        teacher_id=data.teacher_id,
        enrollment_date=data.enrollment_date,
    )
    logger.info("新增学生 id:%s 姓名:%s", new_id, data.name)
    return success({"id": new_id}, msg="新增成功")


@router.put("/update/{student_id}")
def update_student(student_id: int, data: StudentUpdate):
    '''
    修改学生信息
    '''
    if StudentModel().get_by_id(student_id) is None:
        raise HTTPException(status_code=404, detail="学生不存在")
    StudentModel().update(student_id, data.name, data.gender, data.age, data.grade)
    logger.info("修改学生 id:%s", student_id)
    return success(msg="修改成功")


@router.put("/assign-class/{student_id}")
def assign_class(student_id: int, data: ClassAssign):
    """
    学生选择班级
    """
    if StudentModel().get_by_id(student_id) is None:
        raise HTTPException(status_code=404, detail="学生不存在")
    if ClassModel().get_by_id(data.class_id) is None:
        raise HTTPException(status_code=404, detail="班级不存在")
    StudentModel().change_class(student_id, data.class_id)
    logger.info("学生分班 id:%s → 班级%s", student_id, data.class_id)
    return success(msg="分班成功")


@router.put("/assign-teacher/{student_id}")
def assign_teacher(student_id: int, data: TeacherAssign):
    '''
    学生选择老师
    '''
    if StudentModel().get_by_id(student_id) is None:
        raise HTTPException(status_code=404, detail="学生不存在")
    if TeacherModel().get_by_id(data.teacher_id) is None:
        raise HTTPException(status_code=404, detail="教师不存在")
    StudentModel().change_teacher(student_id, data.teacher_id)
    logger.info("学生选老师 id:%s → 教师%s", student_id, data.teacher_id)
    return success(msg="选老师成功")


@router.delete("/del/{student_id}")
def delete_student(student_id: int):
    '''
    删除学生信息
    '''
    if StudentModel().get_by_id(student_id) is None:
        raise HTTPException(status_code=404, detail="学生不存在")
    StudentModel().delete(student_id)
    logger.info("删除学生 id:%s", student_id)
    return success(msg="删除成功")

@router.get("/list")
def get_student_list(grade: str = None):
    '''
    学生信息按年级查询
    '''
    if grade is not None:
                                    # filter 筛选条件信息
        student_list = StudentModel().get_grade(grade)
    else:
        student_list = StudentModel().get_all()
    # query_all 已返回字典列表，直接返回即可
    return success(student_list, msg='查询成功')

@router.put("/status/{student_id}")
def student_status(student_id: int, info: StudentStatus):
    '''
    更改学生学籍状态
    '''
    student = StudentModel().get_by_id(student_id)
    # 判断学生是否存在
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    # 判断学生的学籍状态是否在在读，休学，复学，退学之中
    if info.status not in StudentModel.status_choices:
        raise HTTPException(status_code=404, detail="学生学籍状态填写不正确！只能填写“在读，休学，复学，退学")

    # 存放旧状态（query_one 返回字典）
    old_status = student["status"]
    # 保存数据到数据库
    StudentModel().update_status(student_id, info.status)

    # 将修改后的状态写入日志
    logger.info(
        "学生学籍状态变化 | 学生ID:%s | 原状态:%s -> 新状态:%s",
        student_id,old_status,info.status
    )

    return success(data={"id": student_id, "old_status": old_status, "new_status": info.status}, msg={"学生学籍状态修改成功"})