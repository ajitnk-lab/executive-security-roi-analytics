#!/usr/bin/env python3
"""
Security Assessment MCP Server
Provides tools for AWS security service monitoring and compliance checking.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class SecurityMCPServer:
    def __init__(self):
        self.server = Server("security-mcp")
        self.setup_tools()
        
    def setup_tools(self):
        """Register all security assessment tools"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="check_security_services",
                    description="Check status of AWS security services across regions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "regions": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "AWS regions to check (default: current region)"
                            },
                            "services": {
                                "type": "array", 
                                "items": {"type": "string"},
                                "description": "Services to check: guardduty, securityhub, inspector, accessanalyzer, trustedadvisor, macie"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_security_findings",
                    description="Retrieve security findings from AWS security services",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "service": {
                                "type": "string",
                                "enum": ["guardduty", "securityhub", "inspector"],
                                "description": "Security service to query"
                            },
                            "severity": {
                                "type": "string",
                                "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                                "description": "Filter by severity level"
                            },
                            "region": {
                                "type": "string",
                                "description": "AWS region (default: current region)"
                            },
                            "limit": {
                                "type": "integer",
                                "default": 50,
                                "description": "Maximum findings to return"
                            }
                        },
                        "required": ["service"]
                    }
                ),
                Tool(
                    name="check_compliance",
                    description="Check compliance status for encryption and security configurations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "compliance_type": {
                                "type": "string",
                                "enum": ["encryption", "network_security", "access_control"],
                                "description": "Type of compliance check"
                            },
                            "region": {
                                "type": "string",
                                "description": "AWS region (default: current region)"
                            }
                        },
                        "required": ["compliance_type"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                if name == "check_security_services":
                    return await self._check_security_services(arguments)
                elif name == "get_security_findings":
                    return await self._get_security_findings(arguments)
                elif name == "check_compliance":
                    return await self._check_compliance(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _check_security_services(self, args: Dict[str, Any]) -> List[TextContent]:
        """Check status of AWS security services"""
        regions = args.get("regions", [boto3.Session().region_name or "us-east-1"])
        services = args.get("services", ["guardduty", "securityhub", "inspector"])
        
        results = {}
        
        for region in regions:
            results[region] = {}
            
            # Check GuardDuty
            if "guardduty" in services:
                results[region]["guardduty"] = await self._check_guardduty(region)
            
            # Check Security Hub
            if "securityhub" in services:
                results[region]["securityhub"] = await self._check_securityhub(region)
            
            # Check Inspector
            if "inspector" in services:
                results[region]["inspector"] = await self._check_inspector(region)
        
        return [TextContent(type="text", text=json.dumps(results, indent=2))]

    async def _check_guardduty(self, region: str) -> Dict[str, Any]:
        """Check GuardDuty status"""
        try:
            client = boto3.client('guardduty', region_name=region)
            detectors = client.list_detectors()
            
            if not detectors['DetectorIds']:
                return {"status": "disabled", "detectors": []}
            
            detector_details = []
            for detector_id in detectors['DetectorIds']:
                detector = client.get_detector(DetectorId=detector_id)
                detector_details.append({
                    "id": detector_id,
                    "status": detector['Status'],
                    "service_role": detector.get('ServiceRole'),
                    "finding_publishing_frequency": detector.get('FindingPublishingFrequency')
                })
            
            return {"status": "enabled", "detectors": detector_details}
        except ClientError as e:
            return {"status": "error", "error": str(e)}

    async def _check_securityhub(self, region: str) -> Dict[str, Any]:
        """Check Security Hub status"""
        try:
            client = boto3.client('securityhub', region_name=region)
            hub = client.describe_hub()
            
            return {
                "status": "enabled",
                "hub_arn": hub['HubArn'],
                "subscribed_at": hub['SubscribedAt'].isoformat(),
                "auto_enable_controls": hub.get('AutoEnableControls', False)
            }
        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidAccessException':
                return {"status": "disabled"}
            return {"status": "error", "error": str(e)}

    async def _check_inspector(self, region: str) -> Dict[str, Any]:
        """Check Inspector status"""
        try:
            client = boto3.client('inspector2', region_name=region)
            account = client.batch_get_account_status(accountIds=[boto3.client('sts').get_caller_identity()['Account']])
            
            if account['accounts']:
                account_status = account['accounts'][0]
                return {
                    "status": "enabled" if account_status['state']['status'] == 'ENABLED' else "disabled",
                    "resource_state": account_status['resourceState']
                }
            return {"status": "unknown"}
        except ClientError as e:
            return {"status": "error", "error": str(e)}

    async def _get_security_findings(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get security findings from specified service"""
        service = args["service"]
        severity = args.get("severity")
        region = args.get("region", boto3.Session().region_name or "us-east-1")
        limit = args.get("limit", 50)
        
        if service == "guardduty":
            findings = await self._get_guardduty_findings(region, severity, limit)
        elif service == "securityhub":
            findings = await self._get_securityhub_findings(region, severity, limit)
        elif service == "inspector":
            findings = await self._get_inspector_findings(region, severity, limit)
        else:
            return [TextContent(type="text", text=f"Unsupported service: {service}")]
        
        return [TextContent(type="text", text=json.dumps(findings, indent=2))]

    async def _get_guardduty_findings(self, region: str, severity: Optional[str], limit: int) -> Dict[str, Any]:
        """Get GuardDuty findings"""
        try:
            client = boto3.client('guardduty', region_name=region)
            detectors = client.list_detectors()
            
            if not detectors['DetectorIds']:
                return {"findings": [], "message": "No GuardDuty detectors found"}
            
            all_findings = []
            for detector_id in detectors['DetectorIds']:
                criteria = {}
                if severity:
                    criteria['severity'] = {'Eq': [severity]}
                
                finding_ids = client.list_findings(
                    DetectorId=detector_id,
                    FindingCriteria=criteria,
                    MaxResults=limit
                )
                
                if finding_ids['FindingIds']:
                    findings = client.get_findings(
                        DetectorId=detector_id,
                        FindingIds=finding_ids['FindingIds']
                    )
                    all_findings.extend(findings['Findings'])
            
            return {"findings": all_findings[:limit], "count": len(all_findings)}
        except ClientError as e:
            return {"error": str(e)}

    async def _get_securityhub_findings(self, region: str, severity: Optional[str], limit: int) -> Dict[str, Any]:
        """Get Security Hub findings"""
        try:
            client = boto3.client('securityhub', region_name=region)
            
            filters = {}
            if severity:
                filters['SeverityLabel'] = [{'Value': severity, 'Comparison': 'EQUALS'}]
            
            findings = client.get_findings(Filters=filters, MaxResults=limit)
            return {"findings": findings['Findings'], "count": len(findings['Findings'])}
        except ClientError as e:
            return {"error": str(e)}

    async def _get_inspector_findings(self, region: str, severity: Optional[str], limit: int) -> Dict[str, Any]:
        """Get Inspector findings"""
        try:
            client = boto3.client('inspector2', region_name=region)
            
            filter_criteria = {}
            if severity:
                filter_criteria['severity'] = [{'comparison': 'EQUALS', 'value': severity}]
            
            findings = client.list_findings(
                filterCriteria=filter_criteria,
                maxResults=limit
            )
            return {"findings": findings['findings'], "count": len(findings['findings'])}
        except ClientError as e:
            return {"error": str(e)}

    async def _check_compliance(self, args: Dict[str, Any]) -> List[TextContent]:
        """Check compliance for various security configurations"""
        compliance_type = args["compliance_type"]
        region = args.get("region", boto3.Session().region_name or "us-east-1")
        
        if compliance_type == "encryption":
            results = await self._check_encryption_compliance(region)
        elif compliance_type == "network_security":
            results = await self._check_network_security_compliance(region)
        elif compliance_type == "access_control":
            results = await self._check_access_control_compliance(region)
        else:
            return [TextContent(type="text", text=f"Unsupported compliance type: {compliance_type}")]
        
        return [TextContent(type="text", text=json.dumps(results, indent=2))]

    async def _check_encryption_compliance(self, region: str) -> Dict[str, Any]:
        """Check encryption compliance across services"""
        results = {
            "s3_buckets": await self._check_s3_encryption(region),
            "ebs_volumes": await self._check_ebs_encryption(region),
            "rds_instances": await self._check_rds_encryption(region)
        }
        return results

    async def _check_s3_encryption(self, region: str) -> Dict[str, Any]:
        """Check S3 bucket encryption"""
        try:
            s3 = boto3.client('s3', region_name=region)
            buckets = s3.list_buckets()
            
            encrypted_buckets = []
            unencrypted_buckets = []
            
            for bucket in buckets['Buckets']:
                bucket_name = bucket['Name']
                try:
                    encryption = s3.get_bucket_encryption(Bucket=bucket_name)
                    encrypted_buckets.append({
                        "name": bucket_name,
                        "encryption": encryption['ServerSideEncryptionConfiguration']
                    })
                except ClientError as e:
                    if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                        unencrypted_buckets.append(bucket_name)
            
            return {
                "encrypted": encrypted_buckets,
                "unencrypted": unencrypted_buckets,
                "compliance_rate": len(encrypted_buckets) / (len(encrypted_buckets) + len(unencrypted_buckets)) if (encrypted_buckets or unencrypted_buckets) else 0
            }
        except ClientError as e:
            return {"error": str(e)}

    async def _check_ebs_encryption(self, region: str) -> Dict[str, Any]:
        """Check EBS volume encryption"""
        try:
            ec2 = boto3.client('ec2', region_name=region)
            volumes = ec2.describe_volumes()
            
            encrypted_volumes = []
            unencrypted_volumes = []
            
            for volume in volumes['Volumes']:
                if volume['Encrypted']:
                    encrypted_volumes.append(volume['VolumeId'])
                else:
                    unencrypted_volumes.append(volume['VolumeId'])
            
            return {
                "encrypted": encrypted_volumes,
                "unencrypted": unencrypted_volumes,
                "compliance_rate": len(encrypted_volumes) / (len(encrypted_volumes) + len(unencrypted_volumes)) if (encrypted_volumes or unencrypted_volumes) else 0
            }
        except ClientError as e:
            return {"error": str(e)}

    async def _check_rds_encryption(self, region: str) -> Dict[str, Any]:
        """Check RDS instance encryption"""
        try:
            rds = boto3.client('rds', region_name=region)
            instances = rds.describe_db_instances()
            
            encrypted_instances = []
            unencrypted_instances = []
            
            for instance in instances['DBInstances']:
                if instance.get('StorageEncrypted', False):
                    encrypted_instances.append(instance['DBInstanceIdentifier'])
                else:
                    unencrypted_instances.append(instance['DBInstanceIdentifier'])
            
            return {
                "encrypted": encrypted_instances,
                "unencrypted": unencrypted_instances,
                "compliance_rate": len(encrypted_instances) / (len(encrypted_instances) + len(unencrypted_instances)) if (encrypted_instances or unencrypted_instances) else 0
            }
        except ClientError as e:
            return {"error": str(e)}

    async def _check_network_security_compliance(self, region: str) -> Dict[str, Any]:
        """Check network security compliance"""
        # Placeholder for network security checks
        return {"message": "Network security compliance check not yet implemented"}

    async def _check_access_control_compliance(self, region: str) -> Dict[str, Any]:
        """Check access control compliance"""
        # Placeholder for access control checks
        return {"message": "Access control compliance check not yet implemented"}

    async def run(self):
        """Run the MCP server"""
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, self.server.create_initialization_options())


if __name__ == "__main__":
    server = SecurityMCPServer()
    asyncio.run(server.run())
