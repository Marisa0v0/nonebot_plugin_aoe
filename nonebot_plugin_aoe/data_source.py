"""核心业务函数"""
import time
import json
from enum import Enum
from pathlib import Path
from dataclasses import asdict

from nonebot import get_plugin_config

from .models import AoeUserModel, AoeUserInfoModel, AoeUserPopModel, AoeUserResourcesModel, AoeUserTechModel, \
    AoeUserTroopsModel
from .config import Config

cfg = get_plugin_config(Config)


class AoeUsers:
    """基础用户类"""

    def __init__(self, uid: int, uname: str, ufilepath: Path):
        self._uid = uid  # QQ号
        self._uname = uname  # QQ昵称
        self._ufilepath = ufilepath  # 数据文件名
        self._localtime = time.localtime(time.time())  # 当前时间
        self._localtime_string_day = time.strftime('%Y%m%d', self._localtime)  # 格式化字符串
        self._localtime_string_hour = time.strftime('%Y%m%d%H', self._localtime)  # 格式化字符串

    def add_user(self) -> "AoeUserModel":
        """创建新玩家时给初始资源"""
        user = AoeUserModel(
            info=AoeUserInfoModel(
                user_id=self._uid,
                user_name=self._uname,
                register_time=self._localtime_string_day,
                sign_time=self._localtime_string_day,
            ),
            resources=AoeUserResourcesModel(
                food=cfg.register_food,
                wood=cfg.register_wood,
                iron=cfg.register_iron,
                stone=cfg.register_stone,
            ),
            population=AoeUserPopModel(
                villager=cfg.register_villager,
            ),
            tech=AoeUserTechModel(),
            troops=AoeUserTroopsModel(),
        )

        with open(self._ufilepath, 'w', encoding='utf-8') as fp:
            json.dump(asdict(user), fp, ensure_ascii=False, indent=4)
        return user

    def sign_user(self, user: "AoeUserModel") -> str:
        """玩家签到时发放每日资源"""
        if user.info.sign_time == self._localtime_string_day:
            return '\n今天已经领取过资源了'

        user.resources.food += cfg.sign_food
        user.resources.wood += cfg.sign_wood
        user.resources.iron += cfg.sign_iron
        user.resources.stone += cfg.sign_stone
        user.population.villager += cfg.sign_villager
        user.info.sign_time = self._localtime_string_day

        with open(self._ufilepath, 'w', encoding='utf-8') as fp:
            json.dump(asdict(user), fp, ensure_ascii=False, indent=4)

        return (
            f'\n签到完成'
            f'\n获得资源:'
            f'\n食物: {user.resources.food} (+{cfg.sign_food})'
            f'\n木头: {user.resources.wood} (+{cfg.sign_wood})'
            f'\n铁矿: {user.resources.iron} (+{cfg.sign_iron})'
            f'\n石料: {user.resources.stone} (+{cfg.sign_stone})'
            f'\n农民: {user.population.villager} (+{cfg.sign_villager})'
        )

    def produce(self, user: "AoeUserModel", confirm: bool = False) -> tuple[bool, str]:
        """玩家生产资源时的逻辑处"""

        def _calculate(resource: "Resources") -> int:
            """计算资源变化量"""
            villager_consume_food = user.population.villager * cfg.consumption_villager
            lumberjack_consume_food = user.population.lumberjack * cfg.consumption_lumberjack
            smith_consume_food = user.population.smith * cfg.consumption_smith
            miner_consume_food = user.population.miner * cfg.consumption_miner
            food_consumption = villager_consume_food + lumberjack_consume_food + smith_consume_food + miner_consume_food

            match resource:
                case Resources.FOOD:
                    return user.population.villager * user.tech.food * cfg.production_food - food_consumption
                case Resources.WOOD:
                    return user.population.lumberjack * user.tech.wood * cfg.production_wood
                case Resources.IRON:
                    return user.population.smith * user.tech.iron * cfg.production_wood
                case Resources.STONE:
                    return user.population.miner * user.tech.stone * cfg.production_stone
                case _:
                    raise ValueError(f"? 什么资源: {resource = }")

        if user.info.production_time == self._localtime_string_hour:
            return True, '\n这一小时已经产出过资源了'

        # 生产资源导致食物变化
        food_change = _calculate(Resources.FOOD)
        food_remain = user.resources.food + food_change

        # 生产导致食物用尽
        if food_remain <= 0 and not confirm:
            return False, (
                f"\n本次生产会耗尽食物"
                f"\n食物:{user.resources.food}({food_change})"
                f"\n确认生产请输入“.生产确认”"
            )

        wood_remain = _calculate(Resources.WOOD)
        iron_remain = _calculate(Resources.IRON)
        stone_remain = _calculate(Resources.STONE)

        user.resources.food = food_remain
        user.resources.food = max(user.resources.food, 0)  # 防止负数食物

        user.resources.wood += wood_remain
        user.resources.iron += iron_remain
        user.resources.stone += stone_remain
        user.resources.production_time = self._localtime_string_hour

        with open(self._ufilepath, 'w', encoding='utf-8') as fp:
            json.dump(asdict(user), fp, ensure_ascii=False, indent=4)

        return True, (
            f"\n生产完成"
            f"\n获得资源"
            f"\n食物: {user.resources.food} ({food_change})"
            f"\n木头: {user.resources.wood} ({wood_remain})"
            f"\n铁矿: {user.resources.iron} ({iron_remain})"
            f"\n石料: {user.resources.stone} ({stone_remain})"
        )


    def allocate_population(self, user: "AoeUserModel", prof_str: str, number: int) -> str:
        """分配人口"""
        if number > user.population.villager:
            return '\n人口数量不足，仅有农民能够分配为其他职业(木工、铁匠、矿工)，其他职业不可分配'

        user.population.villager -= number
        profession = PROFESSIONS_COMMANDS_MAPPINGS[prof_str]
        match profession:
            case Profession.LUMBERJACK:
                user.population.lumberjack += number
                allocation_number = user.population.lumberjack
            case Profession.SMITH:
                user.population.smith += number
                allocation_number = user.population.smith
            case Profession.MINER:
                user.population.miner += number
                allocation_number = user.population.miner
            case _:
                return '\n职业分配出错，仅有农民能够分配为其他职业(木工、铁匠、矿工)，其他职业不可分配'

        with open(self._ufilepath, 'w', encoding='utf-8') as fp:
            json.dump(asdict(user), fp, ensure_ascii=False, indent=4)
        return (
            f'分配完成'
            f'\n人口职业变化:'
            f'\n农民: {user.population.villager} (-{number})'
            f'\n{profession}: {allocation_number} (+{number})'
        )

    def recruit_troop(self, user: "AoeUserModel", prof_str: str, number: int) -> str:
        """招募士兵"""
        training_food = number * cfg.training_food
        error_message = (
            '\n请确认招募职业及数量，职业仅能为农民、木工、铁匠、石匠！'
            f'\n每招募一名士兵需要消耗食物{cfg.training_food}'
            f'\n当前食物/所需食物: {user.resources.food}/{training_food}'
        )
        if user.resources.food < number * cfg.training_food:
            return error_message

        profession = PROFESSIONS_COMMANDS_MAPPINGS[prof_str]
        match profession:
            case Profession.VILLAGER:
                if number > user.population.villager:
                    return error_message
                user.population.villager -= number
                recruiting_number = user.population.villager
            case Profession.LUMBERJACK:
                if number > user.population.lumberjack:
                    return error_message
                user.population.lumberjack -= number
                recruiting_number = user.population.lumberjack
            case Profession.SMITH:
                if number > user.population.smith:
                    return error_message
                user.population.smith -= number
                recruiting_number = user.population.smith
            case Profession.MINER:
                if number > user.population.miner:
                    return error_message
                user.population.miner -= number
                recruiting_number = user.population.miner
            case _:
                return error_message

        user.troops.troops += number
        user.resources.food -= training_food
        with open(self._ufilepath, 'w', encoding='utf-8') as fp:
            json.dump(asdict(user), fp, ensure_ascii=False, indent=4)

        return (
            f'\n招募完成'
            f'\n人口职业变化:'
            f'\n{prof_str}: {user.population.villager} (-{number})'
            f'\n征召兵: {recruiting_number} (+{number})'
        )

    def research(self, user: "AoeUserModel", tech_str: str) -> str:
        """研发资源"""
        tech: Resources = RESOURCES_COMMANDS_MAPPINGS[tech_str]
        user_resources = list(asdict(user.resources).values())  # 用户当前的资源
        match tech:
            case Resources.FOOD:
                tech_level = cfg.research_food_takes.get(user.tech.food)
            case Resources.WOOD:
                tech_level = cfg.research_wood_takes.get(user.tech.wood)
            case Resources.IRON:
                tech_level = cfg.research_iron_takes.get(user.tech.iron)
            case Resources.STONE:
                tech_level = cfg.research_stone_takes.get(user.tech.stone)
            case _:
                raise

        if tech_level is None:
            return '当前科技已达最高等级'

        tech_cost = list(tech_level.values())
        if not all(x <= y for x, y in zip(tech_cost, user_resources)):
            return (
                '\n所需资源不足'
                f'\n下一级{tech_str}科技需要的资源:'
                f'\n食物: {tech_level["food"]}'
                f'\n木头: {tech_level["wood"]}'
                f'\n铁矿: {tech_level["iron"]}'
                f'\n石材: {tech_level["stone"]}'
            )

        user.resources.food -= tech_level['food']
        user.resources.wood -= tech_level['wood']
        user.resources.iron -= tech_level['iron']
        user.resources.stone -= tech_level['stone']
        match tech:
            case Resources.FOOD:
                user.tech.food += 1
                user_tech = user.tech.food
            case Resources.WOOD:
                user.tech.wood += 1
                user_tech = user.tech.food
            case Resources.IRON:
                user.tech.iron += 1
                user_tech = user.tech.food
            case Resources.STONE:
                user.tech.stone += 1
                user_tech = user.tech.food
            case _:
                raise
        with open(self._ufilepath, 'w', encoding='utf-8') as fp:
            json.dump(asdict(user), fp, ensure_ascii=False, indent=4)

        return (
            '\n科技升级完成'
            f'\n{tech_str}生产: {user_tech} (+1)'
            f'\n\n资源变化'
            f'\n食物: {user.resources.food} (-{tech_level["food"]})'
            f'\n木头: {user.resources.wood} (-{tech_level["wood"]})'
            f'\n铁矿: {user.resources.iron} (-{tech_level["iron"]})'
            f'\n石材: {user.resources.stone} (-{tech_level["stone"]})'
        )


class Resources(Enum):
    """资源计算用"""
    FOOD = 1
    WOOD = 2
    IRON = 3
    STONE = 4


class Profession(Enum):
    """人口计算用"""
    VILLAGER = 1
    LUMBERJACK = 2
    SMITH = 3
    MINER = 4


RESOURCES_COMMANDS_MAPPINGS = {
    "食物": Resources.FOOD,
    "木头": Resources.WOOD,
    "铁矿": Resources.IRON,
    "石材": Resources.STONE,
    "食物生产效率": Resources.FOOD,
    "木头生产效率": Resources.WOOD,
    "铁矿生产效率": Resources.IRON,
    "石材生产效率": Resources.STONE,
}

PROFESSIONS_COMMANDS_MAPPINGS = {
    "农民": Profession.VILLAGER,
    "木工": Profession.LUMBERJACK,
    "铁匠": Profession.SMITH,
    "矿工": Profession.MINER,
}


__all__ = [
    "AoeUsers",
    "RESOURCES_COMMANDS_MAPPINGS",
    "PROFESSIONS_COMMANDS_MAPPINGS",
]
