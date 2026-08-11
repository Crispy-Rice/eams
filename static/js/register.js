// EAMS 注册页逻辑

/**
 * 学生注册：前端校验 → 调用 /auth/register → 成功后跳转登录页
 * 校验规则与后端 auth/vo.py 的 RegisterRequest 保持一致：
 * 用户名 3-20 位、密码 6-20 位、姓名必填、年龄 10-100
 */
async function register() {
    // 读取表单各字段（文本类去首尾空格）
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const name = document.getElementById('name').value.trim();
    const gender = document.getElementById('gender').value;
    const ageInput = document.getElementById('age').value;
    const msg = document.getElementById('msg');

    // ---- 前端校验（防 422 误报，规则与后端一致） ----
    if (username.length < 3 || username.length > 20) { alert('用户名需 3-20 位'); return; }
    if (password.length < 6 || password.length > 20) { alert('密码需 6-20 位'); return; }
    if (!name) { alert('请填写真实姓名'); return; }
    const age = Number(ageInput);
    if (!ageInput || isNaN(age) || age < 10 || age > 100) {
        alert('年龄需为 10-100 之间的数字'); return;
    }

    // 组装注册请求体
    const body = { username, password, name, gender, age };

    // 调用注册接口（公开接口，无需登录）
    const resp = await fetch('/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    const json = await resp.json();

    if (json.code === 0) {
        const d = json.data;
        // 注册成功并自动登录：保存登录态（与 login.js 一致），直接进入后台，无需再登录
        localStorage.setItem('username', d.username);
        localStorage.setItem('role', d.role);
        localStorage.setItem('student_id', d.student_id);
        localStorage.setItem('user_id', d.user_id);
        // 绿色提示并直接跳转管理后台
        msg.style.color = '#52c41a';
        msg.textContent = json.msg + '，跳转中...';
        setTimeout(() => location.href = '/static/dashboard.html', 800);
    } else {
        // 注册失败（如用户名已存在），红色提示后端 msg
        msg.textContent = json.msg || '注册失败';
    }
}
