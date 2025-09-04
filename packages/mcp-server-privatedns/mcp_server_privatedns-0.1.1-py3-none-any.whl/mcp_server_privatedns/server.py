"""
腾讯云 DNSPod 服务主模块
"""
from asyncio.log import logger
from typing import Any
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server.lowlevel import NotificationOptions, Server
import mcp.server.stdio
from . import tool_dnspod, tool_privatedns

server = Server("privatedns")


@server.call_tool()
async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """处理工具调用请求"""
    try:
        result = None
        if name == "DescribeDomainList":
            result = tool_dnspod.describe_domain_list(
                type=arguments.get("type"),
                offset=arguments.get("offset"),
                limit=arguments.get("limit"),
                groupId=arguments.get("groupId"),
                keyword=arguments.get("keyword"),
                tags=arguments.get("tags"),
            )
        if name == "CreatePrivateZone":
            result = tool_privatedns.create_private_zone(
                action=arguments.get("Action"),
                version=arguments.get("Version"),
                domain=arguments.get("Domain"),
                remark=arguments.get("Remark"),
                dns_forward_status=arguments.get("DnsForwardStatus"),
                cname_speedup_status=arguments.get("CnameSpeedupStatus")
            )
        if name == "DescribePrivateZoneList":
            result = tool_privatedns.describe_private_zone_list(
                action=arguments.get("Action"),
                version=arguments.get("Version"),
                offset=arguments.get("Offset"),
                limit=arguments.get("Limit"),
                filters=arguments.get("Filters.N"),
            )
        if name == "DescribePrivateZone":
            result = tool_privatedns.describe_private_zone(
                action=arguments.get("Action"),
                version=arguments.get("Version"),
                zone_id=arguments.get("ZoneId"),
            )
        if name == "DescribePrivateZoneRecordList":
            result = tool_privatedns.describe_private_zone_record_list(
                action=arguments.get("Action"),
                version=arguments.get("Version"),
                zone_id=arguments.get("ZoneId"),
                offset=arguments.get("Offset"),
                limit=arguments.get("Limit"),
                filters=arguments.get("Filters.N"),
            )
        if name == "DescribeRequestData":
            result = tool_privatedns.describe_request_data(
                action=arguments.get("Action"),
                version=arguments.get("Version"),
                time_range_begin=arguments.get("TimeRangeBegin"),
                filters=arguments.get("Filters.N"),
                time_range_end=arguments.get("TimeRangeEnd"),
                export=arguments.get("Export"),
            )

        return [types.TextContent(type="text", text=str(result))]

    except Exception as e:
        return [types.TextContent(type="text", text=f"错误: {str(e)}")]


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="DescribeDomainList",
            description="查询DNSPod的域名列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "Type": {
                        "type": "string",
                        "description": "域名分组类型，默认为ALL。可取值为ALL，MINE，SHARE，ISMARK，PAUSE，VIP，RECENT，SHARE_OUT，FREE。示例值：ALL",
                    },
                    "Offset": {
                        "type": "integer",
                        "description": "记录开始的偏移, 第一条记录为 0, 依次类推。默认值为0。示例值：0",
                    },
                    "Limit": {
                        "type": "integer",
                        "description": "要获取的域名数量, 比如获取20个, 则为20。默认值为3000。示例值：20",
                    },
                    "GroupId": {
                        "type": "integer",
                        "description": "分组ID, 获取指定分组的域名。示例值：1",
                    },
                    "Keyword": {
                        "type": "string",
                        "description": "根据关键字搜索域名。示例值：qq",
                    },
                    "Tags": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "标签过滤",
                    },
                },
            },
        ),
        types.Tool(
            name="CreatePrivateZone",
            description="创建一个私有域",
            inputSchema={
                "type": "object",
                "properties": {
                    "Action":  {
                        "type": "string",
                        "description": "Action 值为CreatePrivateZone",
                    },
                    "Version":  {
                        "type": "string",
                        "description": "Version 值为2020-10-28",
                    },
                    "Domain":  {
                        "type": "string",
                        "description": "域名，格式必须是标准的TLD。示例值：a.com",
                    },
                    "Remark": {
                        "type": "string",
                        "description": "备注, 示例值：测试域名",
                    },
                    "DnsForwardStatus": {
                        "type": "string",
                        "description": "是否开启子域名递归：ENABLED， DISABLED。默认值为ENABLED。示例值：ENABLED",
                    },
                    "CnameSpeedupStatus	": {
                        "type": "string",
                        "description": "是否CNAME加速：ENABLED，DISABLED",
                        "default": "ENABLED",
                    },
                },
                "required": ["Action", "Version", "Domain"],
            },
        ),
        types.Tool(
            name="DescribePrivateZoneList",
            description="获取私有域列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "Action":  {
                        "type": "string",
                        "description": "Action 值为DescribePrivateZoneList",
                    },
                    "Version":  {
                        "type": "string",
                        "description": "Version 值为2020-10-28",
                    },
                    "Offset":  {
                        "type": "integer",
                        "description": "记录开始的偏移, 第一条记录为 0, 依次类推。",
                    },
                    "Limit":  {
                        "type": "integer",
                        "description": "分页限制数目， 最大100，默认20。",
                        "default": 20,
                    },
                    "Filters.N":  {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "Name": {"type": "string", "description": "过滤参数名称,示例值：Domain"},
                                "Values": {"type": "array", "items": {"type": "string"},
                                           "description": "过滤参数值数组,示例值：qq.com"},
                            },
                            "required": ["Name", "Values"],
                        },
                        "description": "过滤参数",
                    }
                },
                "required": ["Action", "Version"],
            },
        ),
        types.Tool(
            name="DescribePrivateZone",
            description="获取私有域信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "Action": {
                        "type": "string",
                        "description": "Action 值为DescribePrivateZone",
                    },
                    "Version": {
                        "type": "string",
                        "description": "Version 值为2020-10-28",
                    },
                    "ZoneId": {
                        "type": "string",
                        "description": "私有域ID",
                    },
                },
                "required": ["Action", "Version", "ZoneId"],
            },
        ),
        types.Tool(
            name="DescribePrivateZoneRecordList",
            description="获取私有域记录列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "Action": {
                        "type": "string",
                        "description": "Action 值为DescribePrivateZoneRecordList",
                    },
                    "Version": {
                        "type": "string",
                        "description": "Version 值为2020-10-28",
                    },
                    "ZoneId": {
                        "type": "string",
                        "description": "私有域ID",
                    },
                    "Filters.N": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "Name": {
                                    "type": "string",
                                    "description": "过滤条件名称",
                                },
                                "Values": {"type": "array", "items": {"type": "string"}, "description": "过滤条件值"}
                            },
                            "required": ["Name", "Values"],
                        },
                    },
                    "Offset": {
                        "type": "integer",
                        "description": "偏移量。",
                    },
                    "Limit": {
                        "type": "integer",
                        "description": "返回数量",
                    },
                },
                "required": ["Action", "Version", "ZoneId"],
            },
        ),
        types.Tool(
            name="DescribeRequestData",
            description="获取私有域解析请求量",
            inputSchema={
                "type": "object",
                "properties": {
                    "Action": {
                        "type": "string",
                        "description": "Action 值为DescribeRequestData",
                    },
                    "Version": {
                        "type": "string",
                        "description": "Version 值为2020-10-28",
                    },
                    "TimeRangeBegin": {
                        "type": "string",
                        "description": "请求量统计起始时间, 格式为yyyy-mm-dd hh:mm:ss, 默认是当前这一天的开始时间",
                    },
                    "Filters.N": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "Name": {"type": "string", "description": "过滤参数名称,示例值：Domain"},
                                "Values": {"type": "array", "items": {"type": "string"},
                                           "description": "过滤参数值数组,示例值：qq.com"},
                            },
                            "required": ["Name", "Values"],
                        },
                        "description": "过滤参数",
                    },
                    "TimeRangeEnd": {
                        "type": "string",
                        "description": "请求量统计结束时间, 格式为yyyy-mm-dd hh:mm:ss",
                    },
                    "Export": {
                        "type": "boolean",
                        "description": "是否导出数据,true: 导出,false: 不导出",
                    }
                },
                "required": ["Action", "Version", "TimeRangeBegin"],
            }
        )
    ]


async def serve():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("Server running with stdio transport")

        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="privatedns",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
