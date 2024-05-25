"""帮助文档"""
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from .config import Config
from nonebot import on_command
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import MessageSegment

HELP_DOC = """===== 帝国时代插件 =====
指令：注册
用途：成为本插件的用户

指令：签到
用途：每日领取资源

指令：生产
用途：消耗一定食物生产资源，每小时只可生产一次

指令：分配工作 <职业> <数量>
用途：将普通农民分配为其他职业的工人

指令：信息
用途：查看自己的信息

指令：招募 <职业> <数量>
用途：消耗一定食物，将其他职业的工人招募为士兵

指令：研发 <科技>
用途：消耗一定资源，升级科技水平

指令：制造 <材料>
用途：制造材料
"""


help = on_command("aoehelp")


@help.handle()
async def _():
    image = build_help_image()
    image_bytes = BytesIO()
    image.save(image_bytes, format='PNG')

    await help.finish(
        MessageSegment.image(image_bytes)
    )


def build_help_image():
    width_length = 0
    for line in HELP_DOC.splitlines():
        width_length = max(len(line), width_length)

    height_length = len(HELP_DOC.splitlines(keepends=True))

    line_space = 4
    word_size = 20
    border_size = word_size
    text_width = width_length * word_size
    text_height = height_length * word_size + (height_length+1) * line_space

    image = Image.new('RGBA', (text_width + 2 * border_size, text_height + 2 * border_size), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)

    draw.text(
        xy=(border_size, border_size),
        text=HELP_DOC,
        fill="black",
        font=ImageFont.truetype(font="data/SmileySans-Oblique.ttf", size=word_size)
    )
    return image


__version__ = "0.1.0"
__plugin_meta__ = PluginMetadata(
    name="帝国时代",
    description="招募士兵，生产资源，即时战略",
    usage=HELP_DOC,
    type="application",
    homepage="",
    config=Config,
    extra={
        "unique_name": "nonebot_plugin_aoe",
        "example": ".aoehelp",
        "author": "KirisameMarisa & Number_Sir",
        "version": __version__,
    },
)

__all__ = [
    "__plugin_meta__",
    "help"
]