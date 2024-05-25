"""在这里修改设定来调控资源产出和其他内容"""
from pydantic import BaseModel


class Config(BaseModel):
    # 注册给的物资
    register_food: int = 1000
    register_wood: int = 500
    register_iron: int = 100
    register_stone: int = 500
    register_villager: int = 200

    # 签到给的每日物资
    sign_food: int = 1000
    sign_wood: int = 500
    sign_iron: int = 100
    sign_stone: int = 500
    sign_villager: int = 200

    # 生产系数，即为一个工作人口能生产多少对应的资源
    production_food: int = 20
    production_wood: int = 10
    production_iron: int = 1
    production_stone: int = 5

    # 食物消耗系数，即为一个工作人口进行生产至少需要多少食物，计算方法为工作人口*该系数+额外食物数量
    consumption_villager: int = 1
    consumption_lumberjack: int = 1
    consumption_smith: int = 1
    consumption_miner: int = 1

    # 转化一个生产人口为士兵所需的食物
    training_food: int = 1

    # 科研消耗系数，在这里写每研发每一级科技需要的资源数量
    research_food_takes: dict = {
        1: {
            'food': 5000,
            'wood': 2000,
            'iron': 1000,
            'stone': 0
        }
    }
    research_wood_takes: dict = {
        1: {
            'food': 10000,
            'wood': 2000,
            'iron': 1000,
            'stone': 0
        }

    }
    research_iron_takes: dict = {
        1: {
            'food': 20000,
            'wood': 10000,
            'iron': 0,
            'stone': 0
        }
    }
    research_stone_takes: dict = {
        1: {
            'food': 20000,
            'wood': 10000,
            'iron': 500,
            'stone': 0

        }
    }

__all__ = ['Config']
