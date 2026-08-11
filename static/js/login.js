// EAMS 登录页逻辑（含图片验证码）

let captchaToken = '';   // 当前验证码 token，登录时回传后端校验

/**
 * 获取并渲染图片验证码：调用 /auth/captcha，取出 token 与 base64 图片
 * 失败时不阻断页面，仅打印日志，等待用户手动点击图片重试
 */
async function loadCaptcha() {
    try {
        const resp = await fetch('/auth/captcha');
        const json = await resp.json();
        if (json.code === 0) {
            captchaToken = json.data.token;
            document.getElementById('captchaImg').src = json.data.image;
        } else {
            console.warn('获取验证码失败：', json.msg);
        }
    } catch (e) {
        console.warn('获取验证码异常：', e);
    }
}

/**
 * 登录：校验输入 → 校验验证码已获取 → 调用 /auth/login → 保存登录信息并跳转
 * 成功响应 data 含：user_id / username / role / student_id
 */
async function login() {
    // 读取输入框（用户名去首尾空格）
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const captchaCode = document.getElementById('captcha_code').value.trim();
    const msg = document.getElementById('msg');

    // 前端非空校验，避免空表单直接请求后端
    if (!username || !password) { alert('请输入用户名和密码'); return; }
    if (!captchaCode) { alert('请输入验证码'); return; }
    if (!captchaToken) { alert('验证码加载中，请稍后重试'); return; }

    // 调用登录接口（携带验证码 token 与用户输入的验证码）
    const resp = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            username,
            password,
            captcha_token: captchaToken,
            captcha_code: captchaCode
        })
    });
    const json = await resp.json();

    if (json.code === 0) {
        const d = json.data;
        // 保存登录信息（教学演示：用户名 + 角色存 localStorage）
        localStorage.setItem('username', d.username);
        localStorage.setItem('role', d.role);
        // 绿色提示并跳转管理后台
        msg.style.color = '#52c41a';
        msg.textContent = json.msg + '，跳转中...';
        setTimeout(() => location.href = '/static/dashboard.html', 500);
    } else {
        // 登录失败（验证码错误/密码错误/用户不存在），红色提示后端 msg
        msg.textContent = json.msg || '登录失败';
        // 无论何种失败都刷新验证码，防止重复使用
        document.getElementById('captcha_code').value = '';
        loadCaptcha();
    }
}

// 图片点击刷新验证码
document.getElementById('captchaImg').addEventListener('click', loadCaptcha);

// 页面加载即获取验证码
loadCaptcha();
