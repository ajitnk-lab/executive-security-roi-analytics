#!/usr/bin/env python3
"""
Cost Analysis MCP Server
Provides tools for AWS security services cost analysis and optimization.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
import boto3
from botocore.exceptions import ClientError


class CostMCPServer:
    def __init__(self):
        self.server = Server("cost-mcp")
        self.setup_tools()
        
    def setup_tools(self):
        """Register all cost analysis tools"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="get_security_service_costs",
                    description="Get costs for AWS security services over specified time period",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "services": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Security services: GuardDuty, SecurityHub, Inspector, Macie, AccessAnalyzer, TrustedAdvisor"
                            },
                            "start_date": {
                                "type": "string",
                                "description": "Start date (YYYY-MM-DD), default: 30 days ago"
                            },
                            "end_date": {
                                "type": "string", 
                                "description": "End date (YYYY-MM-DD), default: today"
                            },
                            "granularity": {
                                "type": "string",
                                "enum": ["DAILY", "MONTHLY"],
                                "default": "DAILY",
                                "description": "Cost data granularity"
                            },
                            "group_by": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Group by dimensions: SERVICE, REGION, USAGE_TYPE"
                            }
                        }
                    }
                ),
                Tool(
                    name="analyze_cost_trends",
                    description="Analyze cost trends and identify optimization opportunities",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "service": {
                                "type": "string",
                                "description": "Specific service to analyze, or 'all' for all security services"
                            },
                            "period_days": {
                                "type": "integer",
                                "default": 90,
                                "description": "Analysis period in days"
                            },
                            "threshold_percent": {
                                "type": "number",
                                "default": 20.0,
                                "description": "Cost increase threshold for alerts (%)"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_cost_breakdown",
                    description="Get detailed cost breakdown by usage type and region",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "service": {
                                "type": "string",
                                "description": "AWS service name (e.g., 'Amazon GuardDuty')"
                            },
                            "start_date": {
                                "type": "string",
                                "description": "Start date (YYYY-MM-DD)"
                            },
                            "end_date": {
                                "type": "string",
                                "description": "End date (YYYY-MM-DD)"
                            }
                        },
                        "required": ["service"]
                    }
                ),
                Tool(
                    name="forecast_costs",
                    description="Forecast future costs based on historical usage patterns",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "service": {
                                "type": "string",
                                "description": "Service to forecast, or 'all' for all security services"
                            },
                            "forecast_months": {
                                "type": "integer",
                                "default": 3,
                                "description": "Number of months to forecast"
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                if name == "get_security_service_costs":
                    return await self._get_security_service_costs(arguments)
                elif name == "analyze_cost_trends":
                    return await self._analyze_cost_trends(arguments)
                elif name == "get_cost_breakdown":
                    return await self._get_cost_breakdown(arguments)
                elif name == "forecast_costs":
                    return await self._forecast_costs(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _get_security_service_costs(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get costs for AWS security services"""
        services = args.get("services", ["GuardDuty", "SecurityHub", "Inspector", "Macie"])
        end_date = args.get("end_date", datetime.now().strftime("%Y-%m-%d"))
        start_date = args.get("start_date", (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        granularity = args.get("granularity", "DAILY")
        group_by = args.get("group_by", ["SERVICE"])
        
        try:
            ce_client = boto3.client('ce')
            
            # Map service names to AWS service names
            service_mapping = {
                "GuardDuty": "Amazon GuardDuty",
                "SecurityHub": "AWS Security Hub", 
                "Inspector": "Amazon Inspector",
                "Macie": "Amazon Macie",
                "AccessAnalyzer": "AWS IAM Access Analyzer",
                "TrustedAdvisor": "AWS Support (Business)"
            }
            
            aws_services = [service_mapping.get(s, s) for s in services]
            
            response = ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity=granularity,
                Metrics=['BlendedCost', 'UsageQuantity'],
                GroupBy=[{'Type': 'DIMENSION', 'Key': key} for key in group_by],
                Filter={
                    'Dimensions': {
                        'Key': 'SERVICE',
                        'Values': aws_services,
                        'MatchOptions': ['EQUALS']
                    }
                }
            )
            
            # Process and format the response
            results = {
                "time_period": {"start": start_date, "end": end_date},
                "granularity": granularity,
                "total_cost": 0,
                "services": {},
                "daily_costs": []
            }
            
            for result in response['ResultsByTime']:
                date = result['TimePeriod']['Start']
                daily_total = 0
                
                for group in result['Groups']:
                    service = group['Keys'][0] if group['Keys'] else 'Unknown'
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    usage = float(group['Metrics']['UsageQuantity']['Amount'])
                    
                    if service not in results["services"]:
                        results["services"][service] = {"total_cost": 0, "total_usage": 0}
                    
                    results["services"][service]["total_cost"] += cost
                    results["services"][service]["total_usage"] += usage
                    daily_total += cost
                
                results["daily_costs"].append({"date": date, "cost": daily_total})
                results["total_cost"] += daily_total
            
            return [TextContent(type="text", text=json.dumps(results, indent=2))]
            
        except ClientError as e:
            return [TextContent(type="text", text=f"AWS API Error: {str(e)}")]

    async def _analyze_cost_trends(self, args: Dict[str, Any]) -> List[TextContent]:
        """Analyze cost trends and identify optimization opportunities"""
        service = args.get("service", "all")
        period_days = args.get("period_days", 90)
        threshold_percent = args.get("threshold_percent", 20.0)
        
        try:
            ce_client = boto3.client('ce')
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # Get cost data for the period
            response = ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime("%Y-%m-%d"),
                    'End': end_date.strftime("%Y-%m-%d")
                },
                Granularity='DAILY',
                Metrics=['BlendedCost'],
                GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}],
                Filter={
                    'Dimensions': {
                        'Key': 'SERVICE',
                        'Values': ['Amazon GuardDuty', 'AWS Security Hub', 'Amazon Inspector', 'Amazon Macie'],
                        'MatchOptions': ['EQUALS']
                    }
                } if service == "all" else {
                    'Dimensions': {
                        'Key': 'SERVICE',
                        'Values': [service],
                        'MatchOptions': ['EQUALS']
                    }
                }
            )
            
            # Analyze trends
            daily_costs = []
            service_trends = {}
            
            for result in response['ResultsByTime']:
                date = result['TimePeriod']['Start']
                total_cost = 0
                
                for group in result['Groups']:
                    service_name = group['Keys'][0] if group['Keys'] else 'Unknown'
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    
                    if service_name not in service_trends:
                        service_trends[service_name] = []
                    
                    service_trends[service_name].append({"date": date, "cost": cost})
                    total_cost += cost
                
                daily_costs.append({"date": date, "total_cost": total_cost})
            
            # Calculate trends and alerts
            analysis = {
                "period_days": period_days,
                "threshold_percent": threshold_percent,
                "trends": {},
                "alerts": [],
                "recommendations": []
            }
            
            for service_name, costs in service_trends.items():
                if len(costs) >= 7:  # Need at least a week of data
                    recent_avg = sum(c["cost"] for c in costs[-7:]) / 7
                    older_avg = sum(c["cost"] for c in costs[:7]) / 7
                    
                    if older_avg > 0:
                        change_percent = ((recent_avg - older_avg) / older_avg) * 100
                        
                        analysis["trends"][service_name] = {
                            "recent_avg_daily": recent_avg,
                            "older_avg_daily": older_avg,
                            "change_percent": change_percent,
                            "trend": "increasing" if change_percent > 5 else "decreasing" if change_percent < -5 else "stable"
                        }
                        
                        if change_percent > threshold_percent:
                            analysis["alerts"].append({
                                "service": service_name,
                                "type": "cost_increase",
                                "change_percent": change_percent,
                                "message": f"{service_name} costs increased by {change_percent:.1f}% over the analysis period"
                            })
            
            # Add recommendations
            analysis["recommendations"] = [
                "Review GuardDuty findings frequency settings to optimize costs",
                "Consider disabling Security Hub standards not required for compliance",
                "Optimize Inspector scanning schedules based on deployment frequency",
                "Review Macie data discovery jobs and adjust frequency if needed"
            ]
            
            return [TextContent(type="text", text=json.dumps(analysis, indent=2))]
            
        except ClientError as e:
            return [TextContent(type="text", text=f"AWS API Error: {str(e)}")]

    async def _get_cost_breakdown(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get detailed cost breakdown by usage type and region"""
        service = args["service"]
        end_date = args.get("end_date", datetime.now().strftime("%Y-%m-%d"))
        start_date = args.get("start_date", (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        
        try:
            ce_client = boto3.client('ce')
            
            # Get cost breakdown by usage type
            usage_response = ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity='MONTHLY',
                Metrics=['BlendedCost', 'UsageQuantity'],
                GroupBy=[{'Type': 'DIMENSION', 'Key': 'USAGE_TYPE'}],
                Filter={
                    'Dimensions': {
                        'Key': 'SERVICE',
                        'Values': [service],
                        'MatchOptions': ['EQUALS']
                    }
                }
            )
            
            # Get cost breakdown by region
            region_response = ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity='MONTHLY',
                Metrics=['BlendedCost'],
                GroupBy=[{'Type': 'DIMENSION', 'Key': 'REGION'}],
                Filter={
                    'Dimensions': {
                        'Key': 'SERVICE',
                        'Values': [service],
                        'MatchOptions': ['EQUALS']
                    }
                }
            )
            
            breakdown = {
                "service": service,
                "time_period": {"start": start_date, "end": end_date},
                "usage_types": {},
                "regions": {},
                "total_cost": 0
            }
            
            # Process usage type breakdown
            for result in usage_response['ResultsByTime']:
                for group in result['Groups']:
                    usage_type = group['Keys'][0] if group['Keys'] else 'Unknown'
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    usage = float(group['Metrics']['UsageQuantity']['Amount'])
                    
                    if usage_type not in breakdown["usage_types"]:
                        breakdown["usage_types"][usage_type] = {"cost": 0, "usage": 0}
                    
                    breakdown["usage_types"][usage_type]["cost"] += cost
                    breakdown["usage_types"][usage_type]["usage"] += usage
                    breakdown["total_cost"] += cost
            
            # Process region breakdown
            for result in region_response['ResultsByTime']:
                for group in result['Groups']:
                    region = group['Keys'][0] if group['Keys'] else 'Unknown'
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    
                    if region not in breakdown["regions"]:
                        breakdown["regions"][region] = 0
                    
                    breakdown["regions"][region] += cost
            
            return [TextContent(type="text", text=json.dumps(breakdown, indent=2))]
            
        except ClientError as e:
            return [TextContent(type="text", text=f"AWS API Error: {str(e)}")]

    async def _forecast_costs(self, args: Dict[str, Any]) -> List[TextContent]:
        """Forecast future costs based on historical usage patterns"""
        service = args.get("service", "all")
        forecast_months = args.get("forecast_months", 3)
        
        try:
            ce_client = boto3.client('ce')
            
            start_date = datetime.now()
            end_date = start_date + timedelta(days=forecast_months * 30)
            
            # Use AWS Cost Explorer forecast API
            response = ce_client.get_cost_forecast(
                TimePeriod={
                    'Start': start_date.strftime("%Y-%m-%d"),
                    'End': end_date.strftime("%Y-%m-%d")
                },
                Metric='BLENDED_COST',
                Granularity='MONTHLY',
                Filter={
                    'Dimensions': {
                        'Key': 'SERVICE',
                        'Values': ['Amazon GuardDuty', 'AWS Security Hub', 'Amazon Inspector', 'Amazon Macie'],
                        'MatchOptions': ['EQUALS']
                    }
                } if service == "all" else {
                    'Dimensions': {
                        'Key': 'SERVICE',
                        'Values': [service],
                        'MatchOptions': ['EQUALS']
                    }
                }
            )
            
            forecast = {
                "service": service,
                "forecast_period_months": forecast_months,
                "forecast_start": start_date.strftime("%Y-%m-%d"),
                "forecast_end": end_date.strftime("%Y-%m-%d"),
                "total_forecasted_cost": float(response['Total']['Amount']),
                "currency": response['Total']['Unit'],
                "monthly_breakdown": []
            }
            
            # Add monthly breakdown if available
            for result in response.get('ForecastResultsByTime', []):
                forecast["monthly_breakdown"].append({
                    "period": result['TimePeriod'],
                    "mean_value": float(result['MeanValue']),
                    "prediction_interval_lower": float(result['PredictionIntervalLowerBound']),
                    "prediction_interval_upper": float(result['PredictionIntervalUpperBound'])
                })
            
            return [TextContent(type="text", text=json.dumps(forecast, indent=2))]
            
        except ClientError as e:
            return [TextContent(type="text", text=f"AWS API Error: {str(e)}")]

    async def run(self):
        """Run the MCP server"""
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, self.server.create_initialization_options())


if __name__ == "__main__":
    server = CostMCPServer()
    asyncio.run(server.run())
