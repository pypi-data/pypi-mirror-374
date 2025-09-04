"""
腾讯云客户端创建模块
"""
import os
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.common_client import CommonClient
from tencentcloud.dnspod.v20210323 import dnspod_client
from tencentcloud.privatedns.v20201028 import privatedns_client
from tencentcloud.ecm.v20190719 import ecm_client

secret_id = os.getenv("TENCENTCLOUD_SECRET_ID")
secret_key = os.getenv("TENCENTCLOUD_SECRET_KEY")
default_region = os.getenv("TENCENTCLOUD_REGION")


def get_common_client(region: str = None, product = "dnspod", version="2021-03-23") -> CommonClient:
    """
    创建并返回通用客户端实例

    Args:
        region: 地域信息
        product: 产品名称
        version: 产品版本

    Returns:
        CommonClient: 通用客户端实例
    """
    cred = credential.Credential(secret_id, secret_key)
    if not region:
        region = default_region or "ap-guangzhou"

    http_profile = HttpProfile()
    http_profile.endpoint = "dnspod.tencentcloudapi.com"

    client_profile = ClientProfile()
    client_profile.httpProfile = http_profile
    client_profile.request_client = "MCP-Server"
    print("==========debug=======")
    print(secret_id)

    return CommonClient(product, version, cred, region, profile=client_profile)


def get_dnspod_client(region: str = None) -> dnspod_client.DnspodClient:
    """
    创建并返回DNSPod客户端

    Args:
        region: 地域信息

    Returns:
        CvmClient: CVM客户端实例
    """
    cred = credential.Credential(secret_id, secret_key)
    if not region:
        region = default_region or "ap-guangzhou"

    http_profile = HttpProfile()
    http_profile.endpoint = "dnspod.tencentcloudapi.com"

    client_profile = ClientProfile()
    client_profile.httpProfile = http_profile
    client_profile.request_client = "MCP-Server"

    return dnspod_client.DnspodClient(cred, region, client_profile)


def get_privatedns_client(region: str = None) -> privatedns_client.PrivatednsClient:
    """创建私有域"""
    cred = credential.Credential(secret_id, secret_key)

    if not region:
        region = default_region or "ap-guangzhou"

    # 实例化一个http选项，可选的，没有特殊需求可以跳过
    http_profile = HttpProfile()
    http_profile.endpoint = "privatedns.tencentcloudapi.com"

    # 实例化一个client选项，可选的，没有特殊需求可以跳过
    client_profile = ClientProfile()
    client_profile.httpProfile = http_profile
    # 实例化要请求产品的client对象,clientProfile是可选的
    return privatedns_client.PrivatednsClient(cred, region, client_profile)


def get_ecm_client(region: str = None) -> ecm_client.EcmClient:

    cred = credential.Credential(secret_id, secret_key)
    if not region:
        region = default_region or "ap-guangzhou"

    http_profile = HttpProfile()
    http_profile.endpoint = "ecm.tencentcloudapi.com"

    # 实例化一个client选项，可选的，没有特殊需求可以跳过
    client_profile = ClientProfile()
    client_profile.httpProfile = http_profile
    # 实例化要请求产品的client对象,clientProfile是可选的
    return ecm_client.EcmClient(cred, region, client_profile)
