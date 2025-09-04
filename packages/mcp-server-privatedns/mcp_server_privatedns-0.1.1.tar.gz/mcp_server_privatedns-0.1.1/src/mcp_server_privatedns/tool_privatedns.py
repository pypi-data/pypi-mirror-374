"""
腾讯云 privatedns 相关操作工具模块
"""
import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.privatedns.v20201028 import privatedns_client, models as privatedns_models
from tencentcloud.ecm.v20190719 import ecm_client, models as ecm_models
from .capi_client import get_privatedns_client, get_ecm_client


def create_private_zone(action: str = None, version: str = None, domain: str = None,
                        remark: str = None, dns_forward_status: str = None, cname_speedup_status: str = None) -> str:
    client = get_privatedns_client()
    # 实例化一个请求对象,每个接口都会对应一个request对象
    req = privatedns_models.CreatePrivateZoneRequest()
    params = {}
    if action is not None:
        params["Action"] = action
    if version is not None:
        params["Version"] = version
    if domain is not None:
        params["Domain"] = domain
    if remark is not None:
        params["Remark"] = remark
    if dns_forward_status is not None:
        params["DnsForwardStatus"] = dns_forward_status
    if cname_speedup_status is not None:
        params["CnameSpeedupStatus"] = cname_speedup_status

    req.from_json_string(json.dumps(params))

    # 返回的resp是一个CreatePrivateZoneResponse的实例，与请求对象对应
    resp = client.CreatePrivateZone(req)
    # 输出json格式的字符串回包
    return resp.to_json_string()




def describe_private_zone_list(action: str = None, version: str = None, offset: int = None,
                               limit: int = None, filters: list[object] = None) -> str:
    client = get_privatedns_client()
    # 实例化一个请求对象,每个接口都会对应一个request对象
    req = privatedns_models.DescribePrivateZoneListRequest()
    params = {}
    if action is not None:
        params["Action"] = action
    if version is not None:
        params["Version"] = version
    if offset is not None:
        params["Offset"] = offset
    if limit is not None:
        params["Limit"] = limit
    if filters is not None:
        params["Filters"] = filters

    req.from_json_string(json.dumps(params))

    # 返回的resp是一个CreatePrivateZoneResponse的实例，与请求对象对应
    resp = client.DescribePrivateZoneList(req)
    # 输出json格式的字符串回包
    return resp.to_json_string()



def describe_private_zone(action: str = None, version: str = None, zone_id: str = None) -> str:
    client = get_privatedns_client()
    # 实例化一个请求对象,每个接口都会对应一个request对象
    req = privatedns_models.DescribePrivateZoneRequest()
    params = {}
    if action is not None:
        params["Action"] = action
    if version is not None:
        params["Version"] = version
    if zone_id is not None:
        params["ZoneId"] = zone_id

    req.from_json_string(json.dumps(params))

    # 返回的resp是一个CreatePrivateZoneResponse的实例，与请求对象对应
    resp = client.DescribePrivateZone(req)
    # 输出json格式的字符串回包
    return resp.to_json_string()





def describe_private_zone_record_list(action: str = None, version: str = None, zone_id: str = None, filters: list[object] = None, offset: int = None, limit: int = None) -> str:
    client = get_privatedns_client()
    req = privatedns_models.DescribePrivateZoneRecordListRequest()
    params = {}
    if action is not None:
        params["Action"] = action
    if version is not None:
        params["Version"] = version
    if zone_id is not None:
        params["ZoneId"] = zone_id
    if filters is not None:
        params["Filters"] = filters
    if offset is not None:
        params["Offset"] = offset
    if limit is not None:
        params["Limit"] = limit
    req.from_json_string(json.dumps(params))
    resp = client.DescribePrivateZoneRecordList(req)
    return resp.to_json_string()



def describe_request_data(action: str = None, version: str = None, time_range_begin: str = None, filters: list[object] = None,
                          time_range_end: str = None, export: str = None):
    client = get_privatedns_client()
    req = privatedns_models.DescribeRequestDataRequest()
    params = {}
    if action is not None:
        params["Action"] = action
    if version is not None:
        params["Version"] = version
    if time_range_begin is not None:
        params["TimeRangeBegin"] = time_range_begin
    if filters is not None:
        params["Filters"] = filters
    if time_range_end is not None:
        params["TimeRangeEnd"] = time_range_end
    if export is not None:
        params["Export"] = export
    req.from_json_string(json.dumps(params))
    resp = client.DescribeRequestData(req)
    return resp.to_json_string()
