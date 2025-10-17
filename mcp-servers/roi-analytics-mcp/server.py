#!/usr/bin/env python3
"""
ROI Analytics MCP Server
Provides tools for calculating and analyzing security investment ROI.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
import boto3
from botocore.exceptions import ClientError


class ROIAnalyticsMCPServer:
    def __init__(self):
        self.server = Server("roi-analytics-mcp")
        self.setup_tools()
        
    def setup_tools(self):
        """Register all ROI analytics tools"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="calculate_security_roi",
                    description="Calculate ROI for security investments based on costs and risk reduction",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "investment_data": {
                                "type": "object",
                                "properties": {
                                    "security_costs": {"type": "number", "description": "Total security service costs"},
                                    "period_months": {"type": "integer", "default": 12, "description": "Analysis period in months"},
                                    "incidents_prevented": {"type": "integer", "description": "Number of security incidents prevented"},
                                    "avg_incident_cost": {"type": "number", "description": "Average cost per security incident"}
                                },
                                "required": ["security_costs", "incidents_prevented", "avg_incident_cost"]
                            }
                        },
                        "required": ["investment_data"]
                    }
                ),
                Tool(
                    name="analyze_cost_benefit",
                    description="Analyze cost-benefit ratio of security services",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "services": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Security services to analyze"
                            },
                            "time_period": {
                                "type": "object",
                                "properties": {
                                    "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                                    "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"}
                                }
                            },
                            "risk_metrics": {
                                "type": "object",
                                "properties": {
                                    "high_severity_findings": {"type": "integer"},
                                    "critical_findings": {"type": "integer"},
                                    "compliance_score": {"type": "number", "minimum": 0, "maximum": 100}
                                }
                            }
                        }
                    }
                ),
                Tool(
                    name="generate_roi_report",
                    description="Generate comprehensive ROI report with recommendations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "report_type": {
                                "type": "string",
                                "enum": ["executive_summary", "detailed_analysis", "quarterly_review"],
                                "description": "Type of ROI report to generate"
                            },
                            "include_forecasts": {
                                "type": "boolean",
                                "default": true,
                                "description": "Include future ROI projections"
                            },
                            "benchmark_data": {
                                "type": "object",
                                "properties": {
                                    "industry": {"type": "string", "description": "Industry for benchmarking"},
                                    "company_size": {"type": "string", "enum": ["small", "medium", "large", "enterprise"]}
                                }
                            }
                        },
                        "required": ["report_type"]
                    }
                ),
                Tool(
                    name="optimize_security_spend",
                    description="Analyze and recommend security spending optimizations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "current_spend": {
                                "type": "object",
                                "description": "Current security spending breakdown by service"
                            },
                            "risk_tolerance": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "default": "medium",
                                "description": "Organization's risk tolerance level"
                            },
                            "optimization_goals": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Optimization objectives: cost_reduction, risk_mitigation, compliance"
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                if name == "calculate_security_roi":
                    return await self._calculate_security_roi(arguments)
                elif name == "analyze_cost_benefit":
                    return await self._analyze_cost_benefit(arguments)
                elif name == "generate_roi_report":
                    return await self._generate_roi_report(arguments)
                elif name == "optimize_security_spend":
                    return await self._optimize_security_spend(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _calculate_security_roi(self, args: Dict[str, Any]) -> List[TextContent]:
        """Calculate ROI for security investments"""
        investment_data = args["investment_data"]
        
        security_costs = investment_data["security_costs"]
        period_months = investment_data.get("period_months", 12)
        incidents_prevented = investment_data["incidents_prevented"]
        avg_incident_cost = investment_data["avg_incident_cost"]
        
        # Calculate ROI metrics
        total_savings = incidents_prevented * avg_incident_cost
        net_benefit = total_savings - security_costs
        roi_percentage = (net_benefit / security_costs) * 100 if security_costs > 0 else 0
        
        # Annualize if period is not 12 months
        if period_months != 12:
            annualized_costs = security_costs * (12 / period_months)
            annualized_savings = total_savings * (12 / period_months)
            annualized_roi = ((annualized_savings - annualized_costs) / annualized_costs) * 100
        else:
            annualized_costs = security_costs
            annualized_savings = total_savings
            annualized_roi = roi_percentage
        
        # Calculate payback period
        monthly_savings = total_savings / period_months
        payback_months = security_costs / monthly_savings if monthly_savings > 0 else float('inf')
        
        # Risk reduction value
        risk_reduction_value = self._calculate_risk_reduction_value(incidents_prevented, avg_incident_cost)
        
        roi_analysis = {
            "period_months": period_months,
            "investment": {
                "security_costs": security_costs,
                "annualized_costs": annualized_costs
            },
            "returns": {
                "incidents_prevented": incidents_prevented,
                "total_savings": total_savings,
                "annualized_savings": annualized_savings,
                "net_benefit": net_benefit
            },
            "roi_metrics": {
                "roi_percentage": round(roi_percentage, 2),
                "annualized_roi": round(annualized_roi, 2),
                "payback_period_months": round(payback_months, 1) if payback_months != float('inf') else "N/A",
                "cost_benefit_ratio": round(total_savings / security_costs, 2) if security_costs > 0 else 0
            },
            "risk_analysis": risk_reduction_value,
            "recommendations": self._generate_roi_recommendations(roi_percentage, payback_months)
        }
        
        return [TextContent(type="text", text=json.dumps(roi_analysis, indent=2))]

    def _calculate_risk_reduction_value(self, incidents_prevented: int, avg_incident_cost: float) -> Dict[str, Any]:
        """Calculate the value of risk reduction"""
        # Industry benchmarks for security incident costs
        incident_cost_breakdown = {
            "direct_costs": avg_incident_cost * 0.4,  # 40% direct costs
            "business_disruption": avg_incident_cost * 0.3,  # 30% business impact
            "reputation_damage": avg_incident_cost * 0.2,  # 20% reputation
            "regulatory_fines": avg_incident_cost * 0.1   # 10% regulatory
        }
        
        total_risk_avoided = incidents_prevented * avg_incident_cost
        
        return {
            "incidents_prevented": incidents_prevented,
            "avg_incident_cost": avg_incident_cost,
            "total_risk_avoided": total_risk_avoided,
            "cost_breakdown": incident_cost_breakdown,
            "risk_reduction_percentage": min(95, incidents_prevented * 5)  # Cap at 95%
        }

    def _generate_roi_recommendations(self, roi_percentage: float, payback_months: float) -> List[str]:
        """Generate ROI-based recommendations"""
        recommendations = []
        
        if roi_percentage > 200:
            recommendations.append("Excellent ROI - consider expanding security investments")
        elif roi_percentage > 100:
            recommendations.append("Strong positive ROI - maintain current security posture")
        elif roi_percentage > 50:
            recommendations.append("Moderate ROI - optimize security configurations for better returns")
        elif roi_percentage > 0:
            recommendations.append("Positive ROI but room for improvement - review security effectiveness")
        else:
            recommendations.append("Negative ROI - urgent review of security strategy needed")
        
        if payback_months != float('inf'):
            if payback_months <= 6:
                recommendations.append("Fast payback period - excellent investment")
            elif payback_months <= 12:
                recommendations.append("Reasonable payback period - good investment")
            elif payback_months <= 24:
                recommendations.append("Long payback period - consider optimization")
            else:
                recommendations.append("Very long payback period - review investment strategy")
        
        return recommendations

    async def _analyze_cost_benefit(self, args: Dict[str, Any]) -> List[TextContent]:
        """Analyze cost-benefit ratio of security services"""
        services = args.get("services", ["GuardDuty", "SecurityHub", "Inspector"])
        time_period = args.get("time_period", {})
        risk_metrics = args.get("risk_metrics", {})
        
        # Get cost data for services
        cost_data = await self._get_service_costs(services, time_period)
        
        # Calculate benefit scores based on risk metrics
        benefit_analysis = {}
        
        for service in services:
            service_cost = cost_data.get(service, 0)
            
            # Calculate benefit score based on service type and risk metrics
            benefit_score = self._calculate_service_benefit_score(service, risk_metrics)
            
            cost_benefit_ratio = benefit_score / service_cost if service_cost > 0 else 0
            
            benefit_analysis[service] = {
                "cost": service_cost,
                "benefit_score": benefit_score,
                "cost_benefit_ratio": round(cost_benefit_ratio, 2),
                "effectiveness_rating": self._rate_effectiveness(cost_benefit_ratio),
                "optimization_potential": self._assess_optimization_potential(service, cost_benefit_ratio)
            }
        
        # Overall analysis
        total_cost = sum(data["cost"] for data in benefit_analysis.values())
        total_benefit = sum(data["benefit_score"] for data in benefit_analysis.values())
        overall_ratio = total_benefit / total_cost if total_cost > 0 else 0
        
        analysis = {
            "analysis_period": time_period,
            "services_analyzed": services,
            "service_analysis": benefit_analysis,
            "overall_metrics": {
                "total_cost": total_cost,
                "total_benefit_score": total_benefit,
                "overall_cost_benefit_ratio": round(overall_ratio, 2),
                "portfolio_effectiveness": self._rate_effectiveness(overall_ratio)
            },
            "recommendations": self._generate_cost_benefit_recommendations(benefit_analysis)
        }
        
        return [TextContent(type="text", text=json.dumps(analysis, indent=2))]

    async def _get_service_costs(self, services: List[str], time_period: Dict[str, str]) -> Dict[str, float]:
        """Get cost data for services (mock implementation)"""
        # In real implementation, this would call the Cost MCP server
        # For now, return mock data
        service_costs = {
            "GuardDuty": 150.0,
            "SecurityHub": 75.0,
            "Inspector": 200.0,
            "Macie": 300.0,
            "AccessAnalyzer": 25.0
        }
        
        return {service: service_costs.get(service, 100.0) for service in services}

    def _calculate_service_benefit_score(self, service: str, risk_metrics: Dict[str, Any]) -> float:
        """Calculate benefit score for a service based on risk metrics"""
        base_scores = {
            "GuardDuty": 80,
            "SecurityHub": 70,
            "Inspector": 75,
            "Macie": 65,
            "AccessAnalyzer": 60
        }
        
        base_score = base_scores.get(service, 50)
        
        # Adjust based on risk metrics
        high_findings = risk_metrics.get("high_severity_findings", 0)
        critical_findings = risk_metrics.get("critical_findings", 0)
        compliance_score = risk_metrics.get("compliance_score", 80)
        
        # Higher findings increase benefit score (more value from detection)
        findings_bonus = min(30, (high_findings * 2) + (critical_findings * 5))
        
        # Lower compliance increases benefit score (more room for improvement)
        compliance_bonus = max(0, (100 - compliance_score) * 0.3)
        
        return base_score + findings_bonus + compliance_bonus

    def _rate_effectiveness(self, ratio: float) -> str:
        """Rate effectiveness based on cost-benefit ratio"""
        if ratio >= 3.0:
            return "Excellent"
        elif ratio >= 2.0:
            return "Good"
        elif ratio >= 1.0:
            return "Fair"
        else:
            return "Poor"

    def _assess_optimization_potential(self, service: str, ratio: float) -> str:
        """Assess optimization potential for a service"""
        if ratio < 1.0:
            return "High - Consider configuration changes or alternative solutions"
        elif ratio < 2.0:
            return "Medium - Fine-tune settings for better value"
        else:
            return "Low - Service is performing well"

    def _generate_cost_benefit_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on cost-benefit analysis"""
        recommendations = []
        
        # Find best and worst performing services
        ratios = {service: data["cost_benefit_ratio"] for service, data in analysis.items()}
        best_service = max(ratios, key=ratios.get)
        worst_service = min(ratios, key=ratios.get)
        
        recommendations.append(f"Best performing service: {best_service} (ratio: {ratios[best_service]})")
        
        if ratios[worst_service] < 1.0:
            recommendations.append(f"Review {worst_service} configuration - low cost-benefit ratio")
        
        # Service-specific recommendations
        for service, data in analysis.items():
            if data["cost_benefit_ratio"] < 1.0:
                recommendations.append(f"Consider optimizing {service} settings or usage patterns")
        
        return recommendations

    async def _generate_roi_report(self, args: Dict[str, Any]) -> List[TextContent]:
        """Generate comprehensive ROI report"""
        report_type = args["report_type"]
        include_forecasts = args.get("include_forecasts", True)
        benchmark_data = args.get("benchmark_data", {})
        
        # Mock comprehensive report data
        report = {
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "executive_summary": {
                "overall_roi": "145%",
                "total_investment": "$2,500",
                "total_savings": "$6,125",
                "payback_period": "8.2 months",
                "risk_reduction": "78%"
            },
            "key_metrics": {
                "incidents_prevented": 15,
                "avg_incident_cost": "$25,000",
                "compliance_improvement": "23%",
                "detection_accuracy": "94%"
            },
            "service_performance": {
                "GuardDuty": {"roi": "180%", "effectiveness": "Excellent"},
                "SecurityHub": {"roi": "120%", "effectiveness": "Good"},
                "Inspector": {"roi": "135%", "effectiveness": "Good"}
            }
        }
        
        if include_forecasts:
            report["forecasts"] = {
                "next_quarter_roi": "155%",
                "annual_projection": "$15,000 savings",
                "risk_trend": "Decreasing"
            }
        
        if benchmark_data:
            report["benchmarking"] = {
                "industry_average_roi": "85%",
                "peer_comparison": "Above average",
                "maturity_level": "Advanced"
            }
        
        if report_type == "detailed_analysis":
            report["detailed_analysis"] = {
                "cost_breakdown": self._generate_cost_breakdown(),
                "risk_analysis": self._generate_risk_analysis(),
                "optimization_opportunities": self._generate_optimization_opportunities()
            }
        
        return [TextContent(type="text", text=json.dumps(report, indent=2))]

    def _generate_cost_breakdown(self) -> Dict[str, Any]:
        """Generate detailed cost breakdown"""
        return {
            "by_service": {
                "GuardDuty": {"cost": "$150", "percentage": "35%"},
                "SecurityHub": {"cost": "$75", "percentage": "17%"},
                "Inspector": {"cost": "$200", "percentage": "48%"}
            },
            "by_category": {
                "Detection": "$225",
                "Compliance": "$125", 
                "Vulnerability_Management": "$200"
            }
        }

    def _generate_risk_analysis(self) -> Dict[str, Any]:
        """Generate risk analysis"""
        return {
            "risk_reduction_by_category": {
                "Malware": "85%",
                "Data_Breach": "70%",
                "Compliance_Violations": "90%",
                "Insider_Threats": "60%"
            },
            "residual_risk": "Low",
            "risk_appetite_alignment": "Well aligned"
        }

    def _generate_optimization_opportunities(self) -> List[Dict[str, str]]:
        """Generate optimization opportunities"""
        return [
            {
                "opportunity": "Optimize GuardDuty finding frequency",
                "potential_savings": "$25/month",
                "impact": "Low risk"
            },
            {
                "opportunity": "Consolidate Security Hub standards",
                "potential_savings": "$15/month", 
                "impact": "Medium risk"
            }
        ]

    async def _optimize_security_spend(self, args: Dict[str, Any]) -> List[TextContent]:
        """Analyze and recommend security spending optimizations"""
        current_spend = args.get("current_spend", {})
        risk_tolerance = args.get("risk_tolerance", "medium")
        optimization_goals = args.get("optimization_goals", ["cost_reduction"])
        
        # Analyze current spending patterns
        total_spend = sum(current_spend.values()) if current_spend else 1000
        
        optimization_analysis = {
            "current_spending": current_spend,
            "total_monthly_spend": total_spend,
            "risk_tolerance": risk_tolerance,
            "optimization_goals": optimization_goals,
            "recommendations": []
        }
        
        # Generate recommendations based on goals and risk tolerance
        if "cost_reduction" in optimization_goals:
            cost_recommendations = self._generate_cost_reduction_recommendations(current_spend, risk_tolerance)
            optimization_analysis["recommendations"].extend(cost_recommendations)
        
        if "risk_mitigation" in optimization_goals:
            risk_recommendations = self._generate_risk_mitigation_recommendations(current_spend)
            optimization_analysis["recommendations"].extend(risk_recommendations)
        
        if "compliance" in optimization_goals:
            compliance_recommendations = self._generate_compliance_recommendations(current_spend)
            optimization_analysis["recommendations"].extend(compliance_recommendations)
        
        # Calculate potential savings
        potential_savings = self._calculate_potential_savings(optimization_analysis["recommendations"])
        optimization_analysis["potential_savings"] = potential_savings
        
        return [TextContent(type="text", text=json.dumps(optimization_analysis, indent=2))]

    def _generate_cost_reduction_recommendations(self, current_spend: Dict[str, float], risk_tolerance: str) -> List[Dict[str, Any]]:
        """Generate cost reduction recommendations"""
        recommendations = []
        
        if risk_tolerance == "high":
            recommendations.append({
                "action": "Reduce GuardDuty finding frequency to weekly",
                "savings": "$20/month",
                "risk_impact": "Low",
                "implementation": "Easy"
            })
        
        recommendations.append({
            "action": "Optimize Inspector scanning schedules",
            "savings": "$35/month", 
            "risk_impact": "Very Low",
            "implementation": "Medium"
        })
        
        return recommendations

    def _generate_risk_mitigation_recommendations(self, current_spend: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate risk mitigation recommendations"""
        return [
            {
                "action": "Enable additional Security Hub standards",
                "cost_increase": "$25/month",
                "risk_reduction": "15%",
                "priority": "High"
            }
        ]

    def _generate_compliance_recommendations(self, current_spend: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate compliance recommendations"""
        return [
            {
                "action": "Implement Config rules for compliance monitoring",
                "cost_increase": "$40/month",
                "compliance_improvement": "20%",
                "frameworks": ["SOC2", "PCI-DSS"]
            }
        ]

    def _calculate_potential_savings(self, recommendations: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate potential savings from recommendations"""
        monthly_savings = 0
        monthly_costs = 0
        
        for rec in recommendations:
            if "savings" in rec:
                # Extract numeric value from savings string
                savings_str = rec["savings"].replace("$", "").replace("/month", "")
                monthly_savings += float(savings_str)
            
            if "cost_increase" in rec:
                cost_str = rec["cost_increase"].replace("$", "").replace("/month", "")
                monthly_costs += float(cost_str)
        
        return {
            "monthly_savings": monthly_savings,
            "monthly_additional_costs": monthly_costs,
            "net_monthly_impact": monthly_savings - monthly_costs,
            "annual_impact": (monthly_savings - monthly_costs) * 12
        }

    async def run(self):
        """Run the MCP server"""
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, self.server.create_initialization_options())


if __name__ == "__main__":
    server = ROIAnalyticsMCPServer()
    asyncio.run(server.run())
