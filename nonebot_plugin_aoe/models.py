"""数据模型类"""

from dataclasses import dataclass, field

MyTimeDay = str  # YYYYMMDD
MyTimeHour = str  # YYYYMMDDHH


@dataclass
class AoeUserInfoModel:
    user_id: int
    user_name: str
    register_time: str
    sign_time: "MyTimeDay"
    production_time: "MyTimeHour" = field(default="00000000")


@dataclass
class AoeUserResourcesModel:
    """当前资源"""
    food: int = field(default=0)
    wood: int = field(default=0)
    iron: int = field(default=0)
    stone: int = field(default=0)


@dataclass
class AoeUserPopModel:
    """当前人口"""
    villager: int = field(default=0)
    lumberjack: int = field(default=0)
    smith: int = field(default=0)
    miner: int = field(default=0)


@dataclass
class AoeUserTechModel:
    """科技等级"""
    food: int = field(default=1)
    wood: int = field(default=1)
    iron: int = field(default=1)
    stone: int = field(default=1)


@dataclass
class AoeUserTroopsModel:
    """当前军队"""
    troops: int = field(default=0)
    sword: int = field(default=0)
    archer: int = field(default=0)
    rider: int = field(default=0)


@dataclass
class AoeUserModel:
    info: "AoeUserInfoModel"
    resources: "AoeUserResourcesModel"
    population: "AoeUserPopModel"
    tech: "AoeUserTechModel" = field(default=AoeUserTechModel())
    troops: "AoeUserTroopsModel" = field(default=AoeUserTroopsModel())


__all__ = [
    "AoeUserModel",
    "AoeUserInfoModel",
    "AoeUserResourcesModel",
    "AoeUserPopModel",
    'AoeUserTechModel',
    "AoeUserTroopsModel",
]
