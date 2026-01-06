"""
Author: xuyoushun
Email: xuyoushun@bestpay.com.cn
Date: 2026/1/6 16:35
Description:
FilePath: common_schema
"""
from enum import Enum


class IGenderEnum(str, Enum):
    female = "female"
    male = "male"
    other = "other"
