"""
认证模块 - 图片验证码服务（教学演示）

职责：
- 生成 4 位图文验证码（随机字符 + 干扰线/噪点），输出 PNG 图片
- 以 token 为键，将正确验证码与过期时间暂存于进程内存（教学演示，单进程）
- 登录时校验 token + 用户输入的验证码（一次性使用、5 分钟过期）

依赖：Pillow（见 requirements.txt）
"""
import base64
import io
import random
import string
import time
import uuid

from PIL import Image, ImageDraw, ImageFont

# 验证码字符集：大写字母 + 数字，剔除易混淆字符（0/O/1/I/L）
_CHAR_POOL = string.ascii_uppercase + string.digits
_CHAR_POOL = ''.join(c for c in _CHAR_POOL if c not in 'O0I1L')

_CAPTCHA_LENGTH = 4          # 验证码字符数
_CAPTCHA_EXPIRE = 5 * 60     # 有效期（秒）
_IMAGE_SIZE = (120, 40)      # 图片尺寸 WxH

# 内存存储：token -> {"code": str, "expire_at": float}
# 说明：教学演示用进程内字典；生产环境应改用 Redis 等共享存储（多进程/多机）
_captcha_store: dict = {}


def _random_code(length=_CAPTCHA_LENGTH):
    """从字符集中随机抽取 length 个字符组成验证码"""
    return ''.join(random.choices(_CHAR_POOL, k=length))


def _load_font(size):
    """尝试加载系统字体，失败则回退到默认字体（避免不同平台路径差异报错）"""
    candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def _draw_noise(draw, width, height):
    """绘制干扰线 + 噪点，提升机器自动识别难度"""
    for _ in range(4):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        color = (random.randint(140, 220),) * 3
        draw.line([(x1, y1), (x2, y2)], fill=color, width=1)
    for _ in range(40):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill=(random.randint(120, 200),) * 3)


def _render_image(code):
    """将验证码字符渲染为带干扰的 PNG 图片，返回字节"""
    width, height = _IMAGE_SIZE
    img = Image.new("RGB", (width, height), (245, 247, 250))
    draw = ImageDraw.Draw(img)

    # 逐字符绘制：随机颜色 + 轻微纵向偏移，避免字符整齐排列被轻易识别
    font = _load_font(26)
    char_width = width // (len(code) + 1)
    for i, ch in enumerate(code):
        color = (
            random.randint(20, 120),
            random.randint(20, 120),
            random.randint(20, 160),
        )
        x = char_width * (i + 1)
        y = random.randint(2, height - 28)
        draw.text((x, y), ch, fill=color, font=font)

    _draw_noise(draw, width, height)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def generate():
    """生成验证码

    :return: (token, data_url)
             token 用于登录时回传校验；data_url 为可直接赋给 <img src> 的 base64 PNG
    """
    code = _random_code()
    image_bytes = _render_image(code)
    token = uuid.uuid4().hex
    _captcha_store[token] = {"code": code, "expire_at": time.time() + _CAPTCHA_EXPIRE}

    b64 = base64.b64encode(image_bytes).decode("ascii")
    data_url = f"data:image/png;base64,{b64}"
    return token, data_url


def verify(token, code):
    """校验验证码（一次性使用，校验后即销毁）

    :param token: 获取验证码时返回的 token
    :param code: 用户输入的验证码
    :return: 通过返回 True；过期 / 不存在 / 错误均返回 False
    """
    item = _captcha_store.pop(token, None)   # 取出即移除，保证一次性使用
    if item is None:
        return False
    if time.time() > item["expire_at"]:
        return False
    return item["code"].lower() == (code or "").strip().lower()
