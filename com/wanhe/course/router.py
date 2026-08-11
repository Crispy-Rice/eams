# 文件名：course/router.py
"""
课程模块：课程增删改查 + 学生选课/退课/成绩 + 容量控制 + 先修课检查 + 候补队列

职责：
- 定义 /courses 前缀下端点
- 课程 CRUD（含容量/先修课配置）
- 学生选课：容量检查、先修课拦截、满员候补
- 学生退课：自动从候补队列递补
- 成绩登记
- 候补队列查询
- 存在性校验、重复选课拦截
"""
import logging

from fastapi import APIRouter, HTTPException

from com.wanhe.course.model import CourseModel, StudentCourseModel
from com.wanhe.course.vo import CourseCreate, CourseUpdate, CourseSelect, ScoreUpdate
from com.wanhe.student.model import StudentModel
from com.wanhe.teacher.model import TeacherModel
from com.wanhe.common.response import success

logger = logging.getLogger(__name__)

# 创建子路由
router = APIRouter(prefix="/courses", tags=["课程模块"])


# ---------- 课程管理 ----------

@router.get("/all")
def list_courses(keyword: str = ""):
    """查：获取所有课程（含授课教师名、先修课名、容量、已选人数），可按课程名模糊查询"""
    return success(CourseModel().get_all(keyword))


@router.get("/one/{course_id}")
def get_course(course_id: int):
    """查：按 ID 获取单个课程（含已选人数）"""
    course = CourseModel().get_by_id(course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="课程不存在")
    return success(course)


@router.post("/add")
def add_course(data: CourseCreate):
    """增：新增课程（含容量上限和先修课设置）"""
    if data.teacher_id and TeacherModel().get_by_id(data.teacher_id) is None:
        raise HTTPException(status_code=404, detail="授课教师不存在")
    # 校验先修课程是否存在
    if data.prerequisite_id and CourseModel().get_by_id(data.prerequisite_id) is None:
        raise HTTPException(status_code=404, detail="先修课程不存在")
    # 不能将自己设为先修课
    new_id = CourseModel().create(
        data.name, data.credit, data.teacher_id,
        data.capacity, data.prerequisite_id
    )
    logger.info("新增课程 id:%s 名称:%s 容量:%s 先修课:%s",
                new_id, data.name, data.capacity, data.prerequisite_id)
    return success({"id": new_id}, msg="新增成功")


@router.put("/update/{course_id}")
def update_course(course_id: int, data: CourseUpdate):
    """改：修改课程（含容量和先修课）"""
    if CourseModel().get_by_id(course_id) is None:
        raise HTTPException(status_code=404, detail="课程不存在")
    if data.prerequisite_id and CourseModel().get_by_id(data.prerequisite_id) is None:
        raise HTTPException(status_code=404, detail="先修课程不存在")
    # 不能将自己设为先修课
    if data.prerequisite_id == course_id:
        raise HTTPException(status_code=400, detail="不能将课程自身设为先修课")
    CourseModel().update(
        course_id, data.name, data.credit, data.teacher_id,
        data.capacity, data.prerequisite_id
    )
    logger.info("修改课程 id:%s", course_id)
    return success(msg="修改成功")


@router.delete("/del/{course_id}")
def delete_course(course_id: int):
    """删：删除课程（连带清理选课记录 + 候补记录）"""
    if CourseModel().get_by_id(course_id) is None:
        raise HTTPException(status_code=404, detail="课程不存在")
    CourseModel().delete(course_id)
    logger.info("删除课程 id:%s", course_id)
    return success(msg="删除成功")


# ---------- 学生选课 ----------

@router.get("/student/{student_id}")
def get_student_courses(student_id: int):
    """查：查询某学生已选的课程"""
    if StudentModel().get_by_id(student_id) is None:
        raise HTTPException(status_code=404, detail="学生不存在")
    return success(StudentCourseModel().get_courses_by_student(student_id))


@router.post("/select/{student_id}")
def select_course(student_id: int, data: CourseSelect):
    """选课：学生选一门课程
    校验链：
    1. 学生/课程存在性
    2. 不能重复选课
    3. 先修课检查（必须先选过先修课）
    4. 容量检查（满员则拒绝）
    """
    scm = StudentCourseModel()
    cm = CourseModel()

    # 1. 存在性校验
    if StudentModel().get_by_id(student_id) is None:
        raise HTTPException(status_code=404, detail="学生不存在")
    course = cm.get_by_id(data.course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="课程不存在")

    # 2. 重复选课检查
    if scm.is_selected(student_id, data.course_id):
        raise HTTPException(status_code=400, detail="该课程已选过，不能重复选")

    # 3. 先修课检查
    if course.get('prerequisite_id'):
        prereq = cm.get_by_id(course['prerequisite_id'])
        if not scm.is_selected(student_id, course['prerequisite_id']):
            raise HTTPException(
                status_code=400,
                detail=f"需要先选「{prereq['name']}」后才能选此课程"
            )

    # 4. 容量检查
    enrolled = cm.get_enrolled_count(data.course_id)
    capacity = course.get('capacity')

    if capacity is not None and enrolled >= capacity:
        raise HTTPException(status_code=400, detail=f"课程容量已满（{enrolled}/{capacity}），无法选课")

    # 正常选课
    scm.select(student_id, data.course_id)
    logger.info("学生选课 学生id:%s → 课程%s", student_id, data.course_id)

    # 选课后提醒（即将满员提示）
    if capacity is not None and enrolled + 1 >= capacity:
        return success(msg=f"选课成功！（该课程 {enrolled + 1}/{capacity}，已满员）")
    return success(msg="选课成功")


@router.delete("/unselect/{student_id}")
def unselect_course(student_id: int, data: CourseSelect):
    """退课：学生退掉一门课程"""
    scm = StudentCourseModel()

    if not scm.is_selected(student_id, data.course_id):
        raise HTTPException(status_code=400, detail="未选该课程，无法退课")

    scm.unselect(student_id, data.course_id)
    logger.info("学生退课 学生id:%s 课程%s", student_id, data.course_id)
    return success(msg="退课成功")


# ---------- 成绩登记 ----------

@router.put("/score/{student_id}")
def set_score(student_id: int, data: ScoreUpdate):
    """成绩：为某学生的某门课登记成绩"""
    if not StudentCourseModel().is_selected(student_id, data.course_id):
        raise HTTPException(status_code=400, detail="该学生未选此课程")
    StudentCourseModel().set_score(student_id, data.course_id, data.score)
    logger.info("成绩登记 学生id:%s 课程%s 成绩%s", student_id, data.course_id, data.score)
    return success(msg="成绩登记成功")


# ---------- 候补队列查看 ----------

@router.get("/waitlist/{course_id}")
def get_waitlist(course_id: int):
    """查：查看某课程的候补队列（含学生姓名）"""
    if CourseModel().get_by_id(course_id) is None:
        raise HTTPException(status_code=404, detail="课程不存在")
    return success(StudentCourseModel().get_waitlist_for_course(course_id))
