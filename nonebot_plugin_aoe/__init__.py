"""插件入口"""
import json
import os

from pathlib import Path
from dacite import from_dict

from nonebot import on_command, get_plugin_config
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.adapters import Message
from nonebot.params import CommandArg, Arg
from nonebot.typing import T_State

from .data_source import AoeUsers
from .data_source import RESOURCES_COMMANDS_MAPPINGS, PROFESSIONS_COMMANDS_MAPPINGS
from .utils import verify, verify_recruiting_pop
from .models import AoeUserModel
from .config import Config
from .help import *

cfg = get_plugin_config(Config)
ROOT_PATH = Path(__file__).parent
USER_PATH = ROOT_PATH / 'users'
os.makedirs(USER_PATH, exist_ok=True)

register = on_command('注册', permission=SUPERUSER)
sign = on_command('签到', permission=SUPERUSER, aliases={"sign"})
produce = on_command('生产', permission=SUPERUSER)
allocated_pop = on_command('分配工作', permission=SUPERUSER, aliases={"分配人口"})
user_info = on_command('我的信息', permission=SUPERUSER, aliases={"人口信息", "信息", "我的人口"})
recruiting_pop = on_command('募兵', permission=SUPERUSER, aliases={'征兵', '招募'})
research = on_command('研发', permission=SUPERUSER, aliases={'研究'})
fabrication = on_command('制造', permission=SUPERUSER,aliases={'加工'})

@register.handle()
async def _(event: MessageEvent):
    # 注册与领取每日资源，如果玩家数据文件不存在则判定为新玩家进行处理
    user_filepath = USER_PATH / f"{event.user_id}.json"
    user_id = event.user_id
    user_name = event.sender.nickname

    if user_filepath.exists():
        await register.finish("\n你已经注册过了！", at_sender=True)

    player = AoeUsers(user_id, user_name, user_filepath)
    user = player.add_user()
    await register.finish(
        f"\n注册成功"
        f"\n获得资源"
        f"\n食物: {user.resources.food}"
        f"\n木头: {user.resources.wood}"
        f"\n铁矿: {user.resources.iron}"
        f"\n石料: {user.resources.stone}"
        f"\n农民: {user.population.villager}",
        at_sender=True
    )


@sign.handle()
async def _(event: MessageEvent):
    # 注册与领取每日资源，如果玩家数据文件不存在则判定为新玩家进行处理
    user_filepath = USER_PATH / f"{event.user_id}.json"

    if not user_filepath.exists():
        await sign.finish("\n你还没有注册！请输入“.注册”以注册！", at_sender=True)

    with open(user_filepath, "r", encoding="utf-8") as fp:
        user = json.load(fp)

    user = from_dict(data_class=AoeUserModel, data=user)
    player = AoeUsers(
        user.info.user_id,
        user.info.user_name,
        user_filepath
    )
    sign_result = player.sign_user(user)
    await sign.finish(sign_result, at_sender=True)


@produce.handle()
async def _(state: T_State, event: MessageEvent):
    user_filepath = USER_PATH / f"{event.user_id}.json"
    if not user_filepath.exists():
        await produce.finish('\n你还没有注册，请先输入“.注册”', at_sender=True)

    with open(user_filepath, "r", encoding="utf-8") as fp:
        user = json.load(fp)

    user = from_dict(data_class=AoeUserModel, data=user)
    player = AoeUsers(
        user.info.user_id,
        user.info.user_name,
        user_filepath
    )

    finish_flag, result_msg = player.produce(user)
    state["player"] = player
    state["user"] = user

    if finish_flag:  # 反正不会用尽
        await produce.finish(result_msg, at_sender=True)


@produce.got(key="confirm", prompt="本次生产会导致剩余食物用尽，确认生产请输入“.确认”，否则请输入“.取消”")
async def _(state: T_State, confirm: Message = Arg()):
    confirm = confirm.extract_plain_text().strip() == ".确认"
    if not confirm:
        await produce.finish("\n本次生产已取消，如需继续生产请重新输入.生产", at_sender=True)

    player: "AoeUsers" = state["player"]
    user: "AoeUserModel" = state["user"]
    finish_flag, result_msg = player.produce(user, True)
    await produce.finish(result_msg, at_sender=True)


@allocated_pop.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    error_message = (
        '\n输入内容出错 请确认格式为'
        '\n\n分配工作 职业(木工、铁匠、矿工) 数量'
        '\n\n并确认指定人口数量正确，仅有农民能够分配为其他职业，其他职业不可分配'
    )

    validate, data = verify(
        message=args.extract_plain_text().strip(),
        arg_length=2,
        processor=verify_recruiting_pop
    )
    if not validate:
        await allocated_pop.finish(error_message, at_sender=True)

    profession, number = data
    if profession not in PROFESSIONS_COMMANDS_MAPPINGS.keys():
        await allocated_pop.finish(error_message, at_sender=True)

    user_filepath = USER_PATH / f"{event.user_id}.json"
    if not user_filepath.exists():
        await allocated_pop.finish('\n你还没有注册，请先输入“.注册”', at_sender=True)

    with open(user_filepath, "r", encoding="utf-8") as fp:
        user = json.load(fp)

    user = from_dict(data_class=AoeUserModel, data=user)
    player = AoeUsers(
        user.info.user_id,
        user.info.user_name,
        user_filepath
    )

    allocated_pop_result = player.allocate_population(user, profession, number)
    await allocated_pop.finish(allocated_pop_result)


@user_info.handle()
async def _(event: MessageEvent):
    user_filepath = USER_PATH / f"{event.user_id}.json"

    if not user_filepath.exists():
        await user_info.finish('\n你还没有注册，请先输入“.注册”', at_sender=True)
    with open(user_filepath, "r", encoding="utf-8") as fp:
        user = json.load(fp)

    user = from_dict(data_class=AoeUserModel, data=user)
    await user_info.finish(
        f"\n{user.info.user_name}"
        f"\n\n库存资源:"
        f"\n食物: {user.resources.food}"
        f"\n木头: {user.resources.wood}"
        f"\n铁矿: {user.resources.iron}"
        f"\n石料: {user.resources.stone}"
        f"\n\n生产人力:"
        f"\n农民: {user.population.villager}"
        f"\n木工: {user.population.lumberjack}"
        f"\n铁匠: {user.population.smith}"
        f"\n石匠: {user.population.miner}"
        f"\n\n可用士兵:"
        f"\n征召兵: {user.troops.troops}"
        f"\n剑士: {user.troops.sword}"
        f"\n弓手: {user.troops.archer}"
        f"\n骑手: {user.troops.rider}",
        at_sender=True
    )


@recruiting_pop.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    error_message = (
        '输入内容出错 请确认格式为'
        '\n\n.募兵 职业(农民、木工、铁匠、矿工) 数量'
        '\n\n并确认指定的职业与人口数量正确，征募所有农民为士兵会导致无法获得食物产出，可能因缺乏食物导致无法进行其他操作。'
        f'\n每训练一名士兵需要消耗食物 {cfg.training_food} 请确保资源充分'
    )

    validate, data = verify(
        message=args.extract_plain_text().strip(),
        arg_length=2,
        processor=verify_recruiting_pop  # processor 是个函数，接收 message 和 flag 参数
    )

    if not validate:
        await recruiting_pop.finish(error_message, at_sender=True)

    profession, number = data
    if profession not in PROFESSIONS_COMMANDS_MAPPINGS.keys():
        await recruiting_pop.finish(error_message, at_sender=True)

    user_filepath = USER_PATH / f"{event.user_id}.json"
    if not user_filepath.exists():
        await recruiting_pop.finish('你还没有注册，请先输入“.注册”', at_sender=True)
    with open(user_filepath, "r", encoding="utf-8") as fp:
        user = json.load(fp)

    user = from_dict(data_class=AoeUserModel, data=user)
    player = AoeUsers(
        user.info.user_id,
        user.info.user_name,
        user_filepath
    )

    recruiting_pop_result = player.recruit_troop(user, profession, number)
    await recruiting_pop.finish(recruiting_pop_result, at_sender=True)


@research.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    error_message = (
        '\n输入内容出错 请确认格式为'
        '\n\n.研发 科技(食物、木头、铁矿、石材) '
    )

    args = args.extract_plain_text().strip()
    if not args:
        await research.finish(error_message, at_sender=True)

    if args not in RESOURCES_COMMANDS_MAPPINGS.keys():
        await research.finish(error_message, at_sender=True)

    user_filepath = USER_PATH / f"{event.user_id}.json"
    if not user_filepath.exists():
        await research.finish('你还没有注册，请先输入“.注册”', at_sender=True)

    with open(user_filepath, "r", encoding="utf-8") as fp:
        user_data = json.load(fp)

    user = from_dict(data_class=AoeUserModel, data=user_data)
    player = AoeUsers(
        user.info.user_id,
        user.info.user_name,
        user_filepath
    )

    research_result = player.research(user, args)
    await research.finish(research_result, at_sender=True)

@fabrication.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    ...
