# Tencent Cloud PrivateDNS MCP Server
Private DNS is a private domain name resolution and management service based on Tencent Cloud's Virtual Private Cloud (VPC).


## Features
- **PrivateDNS information query:**: Query domain lists, private domain lists, private domain information, private domain record lists, etc.
- **DNS resolution statistics**: Get the number of private domain resolution requests.



## API List
### 
#### DescribeDomainList
Get the list of domains.

**Input Parameters**:
- `Type` (string, optional): The domain group type.
- `Offset` (integer, optional): Offset, default 0.
- `Limit` (integer, optional): Number of results, default 20, max 100.
- `GroupId` (integer, optional): Group ID, which can be passed in to get all domains in the specified group.
- `Keyword` (integer, optional) Keyword for searching for a domain.
- `Tags` (array[string], optional): Filter by Tags.

#### CreatePrivateZone
Create Private Zone

**Input Parameters**:
- `Action` (string, required): Common parameter, value for this API: `CreatePrivateZone`.
- `Version` (string, required): Common parameter, value for this API: `2020-10-28`.
- `Domain` (string, required): Domain name, must be a standard TLD format.
  Example: `a.com`
- `TagSet.N` (array of TagInfo, optional): Tags to bind to the private domain.
- `VpcSet.N` (array of VpcInfo, optional): VPCs to associate with the private domain.
- `Remark` (string, optional): Remarks.
  Example: `Test domain`
- `DnsForwardStatus` (string, optional): Whether to enable subdomain recursion. Values: `ENABLED`, `DISABLED`. Default: `ENABLED`.
  Example: `ENABLED`
- `AccountVpcSet.N` (array of AccountVpcInfo, optional): VPCs from associated accounts to bind to the private domain.
- `CnameSpeedupStatus` (string, optional): Whether to enable CNAME acceleration. Values: `ENABLED`, `DISABLED`. Default: `ENABLED`.
  Example: `ENABLED`


#### DescribePrivateZone
Get Private Zone information

**Input Parameters**:
- `Action` (string, required): Common parameter, value for this API: DescribePrivateZone.
- `Version` (string, required): Common parameter, value for this API: 2020-10-28.
- `ZoneId` (string, required): Private zone ID.
Example: `zone-dm1igr1`

#### DescribePrivateZoneList
Obtain the list of private zones.

**Input Parameters**:
- `Action` (string, required): Common parameter, value for this API: DescribePrivateZoneList.
- `Version` (string, required): Common parameter, value for this API: 2020-10-28.
- `Region` (string, optional): Common parameter, this interface does not need to pass this parameter.
- `Offset` (integer, optional): Pagination offset, starting from 0.
  Example: `1`
- `Limit` (integer, optional): Pagination limit, maximum 100, default 20.
  Example: `10`
- `Filters.N` (array of Filter, optional): Filtering parameters.

#### DescribePrivateZoneRecordList
Describe Private Zone Record List

**Input Parameters**:
- `Action` (string, required): Common parameter, value for this API: DescribePrivateZoneRecordList.
- `Version` (string, required): Common parameter, value for this API: 2020-10-28.
- `Region` (string, optional): Common parameter, this interface does not need to pass this parameter.
- `ZoneId` (string, required): Private zone ID.
  Example: `zone-12c5a6e8`
- `Filters.N` (array of Filter, optional): Filtering parameters (supports filtering by Value and RecordType).
- `Offset` (integer, optional): Pagination offset, starting from 0.
  Example: `0`
- `Limit` (integer, optional): Pagination limit, maximum 200, default 20.
  Example: `200`

#### DescribeRequestData
Describe Private Zone Request Volume

**Input Parameters**:
- `Action` (string, required): Common parameter, value for this API: DescribeRequestData.
- `Version` (string, required): Common parameter, value for this API: 2020-10-28.
- `Region` (string, optional): Common parameter, this interface does not need to pass this parameter.
- `TimeRangeBegin` (string, required): Start time for request volume statistics, format: `2020-11-22 00:00:00`.
  Example: `2020-11-22 00:00:00`
- `TimeRangeEnd` (string, optional): End time for request volume statistics, format: `2020-11-22 23:59:59`.
  Example: `2020-11-23 23:59:59`
- `Filters.N` (array of Filter, optional): Filtering parameters.
- `Export` (boolean, optional): Whether to export: `true` to export, `false` not to export.
  Example: `true`


## Configuration
### Set Tencent Cloud Credentials
1. Obtain SecretId and SecretKey from Tencent Cloud Console
2. Set default region (optional)

### Environment Variables
Configure the following environment variables:
- `TENCENTCLOUD_SECRET_ID`: Tencent Cloud SecretId
- `TENCENTCLOUD_SECRET_KEY`: Tencent Cloud SecretKey  
- `TENCENTCLOUD_REGION`: Default region (optional)

### Usage in Claude Desktop
Add the following configuration to claude_desktop_config.json:

```json
{
  "mcpServers": {
    "tencent-privatedns": {
      "command": "uv",
      "args": [
        "run",
        "mcp-server-privatedns"
      ],
      "env": {
        "TENCENTCLOUD_SECRET_ID": "YOUR_SECRET_ID_HERE",
        "TENCENTCLOUD_SECRET_KEY": "YOUR_SECRET_KEY_HERE",
        "TENCENTCLOUD_REGION": "ap-guangzhou"  //optional parameter, to specify the region of tencent cloud API, default value is ap-guangzhou.
      }
    }
  }
}
```

## Installation
```sh
pip install mcp-server-privatedns
```

## License
MIT License. See LICENSE file for details.
