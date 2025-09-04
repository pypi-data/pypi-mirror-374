"""
腾讯云 DNSPod 相关操作工具模块
"""
import json
from tencentcloud.dnspod.v20210323 import dnspod_client, models as dnspod_models
from .capi_client import get_dnspod_client, get_common_client
from asyncio.log import logger
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
import random
import string
import re
from typing import Optional, Tuple

def describe_domain_list(type: str=None, offset: int=None, limit: int=None, groupId: int=None, keyword: str=None, tags: list=None) -> str:
    """查询域名列表"""
    client = get_dnspod_client()  # 使用默认地域
    req = dnspod_models.DescribeDomainListRequest()

    params = {}
    if type is not None:
        params["Type"] = type
    if offset is not None:
        params["Offset"] = offset
    if limit is not None:
        params["Limit"] = limit
    if groupId is not None:
        params["GroupId"] = groupId
    if keyword is not None:
        params["Keyword"] = keyword
    if tags is not None:
        params["Tags"] = tags
    
    req.from_json_string(json.dumps(params))
    resp = client.DescribeDomainList(req)

    return resp.to_json_string()