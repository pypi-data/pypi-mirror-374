#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2025-05-11 13:35
# @Author  :   oscar
# @Desc    :   None
"""
from crawlo.items import Field
from crawlo.items.items import Item


class BauDuItem(Item):
    url = Field()
    title = Field()


class ArticleItem(Item):
    article_id = Field()
    title = Field()
    digest = Field()
    short = Field()
    url = Field()
    tag = Field()
    ctime = Field()
    source = Field()


class MiitDeviceItem(Item):
    article_id = Field()
    approval_certificate_no = Field()  # 核准证编号
    device_name = Field()  # 设备名称
    model_number = Field()  # 设备型号
    applicant = Field()  # 申请单位
    remarks = Field()  # 备注
    validity_period = Field()  # 有效期
    frequency_tolerance = Field()  # 频率容限
    frequency_range = Field()  # 频率范围
    transmission_power = Field()  # 发射功率
    occupied_bandwidth = Field()  # 占用带宽
    spurious_emission_limit = Field()  # 杂散发射限制
    issue_date = Field()  # 发证日期
    approval_code = Field()  # 核准代码
    cmiit_id = Field()  # CMIIT ID
    modulation_scheme = Field()  # 调制方式
    technology_module = Field()  # 技术体制/功能模块
    create_time = Field()
