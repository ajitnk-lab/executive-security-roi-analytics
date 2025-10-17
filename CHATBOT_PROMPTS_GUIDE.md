# Executive Security ROI Analytics - Chatbot Prompts Guide

## 🤖 Complete Guide to Using All MCP Tools and Parameters

This guide provides comprehensive examples of how to interact with the Executive Security ROI Analytics chatbot to leverage all available MCP server capabilities across Security, Cost, and ROI analytics.

---

## 🛡️ Security MCP Server Tools

### 1. **check_security_services** - Multi-Region Security Status

**Basic Usage:**
- "Check security services status"
- "What's the status of my security services?"
- "Show me GuardDuty, Security Hub, and Inspector status"

**Region-Specific Queries:**
- "Check security services in us-west-2"
- "Show security status in eu-west-1"
- "What's the GuardDuty status in ap-southeast-2?"

**Multi-Region Queries:**
- "Check security services across us-east-1, us-west-2, and eu-west-1"
- "Show me security status in all US regions"
- "Compare security services between us-east-1 and eu-central-1"

**Service-Specific Queries:**
- "Check only GuardDuty status"
- "Show me Security Hub status across regions"
- "What's the Inspector status in us-east-1?"
- "Check GuardDuty and Security Hub in eu-west-1"

### 2. **get_security_findings** - Detailed Security Findings

**Basic Findings:**
- "Show me security findings"
- "What are the latest GuardDuty findings?"
- "Get Security Hub findings"
- "Show Inspector findings"

**Severity-Filtered Queries:**
- "Show me HIGH severity GuardDuty findings"
- "Get CRITICAL Security Hub findings"
- "What are the MEDIUM severity Inspector findings?"
- "Show all LOW severity findings from GuardDuty"

**Region + Severity Combinations:**
- "Show HIGH severity GuardDuty findings in us-west-2"
- "Get CRITICAL Security Hub findings in eu-west-1"
- "What are MEDIUM severity Inspector findings in ap-southeast-1?"

**Limited Results:**
- "Show me top 10 GuardDuty findings"
- "Get 5 most recent Security Hub findings"
- "Show 20 Inspector findings with HIGH severity"

### 3. **check_compliance** - Security Compliance Checks

**Encryption Compliance:**
- "Check encryption compliance"
- "Show me encryption status across services"
- "Check S3, EBS, and RDS encryption in us-east-1"
- "What's the encryption compliance in eu-west-1?"

**Network Security Compliance:**
- "Check network security compliance"
- "Show network security status in us-west-2"

**Access Control Compliance:**
- "Check access control compliance"
- "Show access control status in ap-southeast-2"

---

## 💰 Cost MCP Server Tools

### 1. **get_security_service_costs** - Security Service Costs

**Basic Cost Queries:**
- "How much did I spend on security services?"
- "What are my security costs?"
- "Show me security service spending"

**Service-Specific Costs:**
- "How much did GuardDuty cost last month?"
- "What's my Security Hub spending?"
- "Show me Inspector costs"
- "How much did I spend on AWS WAF?"

**Time Period Queries:**
- "Show security costs for the last 30 days"
- "What were my security costs in September 2025?"
- " "

**Grouped Cost Analysis:**
- "Show security costs grouped by service"
- "Break down security costs by region"
- "Group security spending by usage type"
- "Show costs grouped by service and region"

### 2. **analyze_cost_trends** - Cost Trend Analysis

**Basic Trend Analysis:**
- "Analyze my security cost trends"
- "Show security spending trends over time"
- "How are my security costs trending?"

**Service-Specific Trends:**
- "Show GuardDuty cost trends"
- "Analyze Security Hub spending trends"
- "What's the trend for Inspector costs?"

**Time-Based Trend Analysis:**
- "Show security cost trends for the last 6 months"
- "Analyze spending trends from January to September 2025"
- "What's the monthly trend for security costs?"

### 3. **get_cost_breakdown** - Detailed Cost Breakdown

**Service Breakdown:**
- "Get detailed cost breakdown for GuardDuty"
- "Show Security Hub cost breakdown"
- "Break down Inspector costs by usage type"

**Regional Breakdown:**
- "Show security costs breakdown by region"
- "Get cost breakdown for us-east-1"
- "Break down security spending across all regions"

**Time Period Breakdown:**
- "Show cost breakdown for September 2025"
- "Get detailed breakdown from 2025-08-01 to 2025-08-31"

### 4. **forecast_costs** - Cost Forecasting

**Basic Forecasting:**
- "Forecast my security costs"
- "What will my security spending be next month?"
- "Predict security costs for the next quarter"

**Service-Specific Forecasting:**
- "Forecast GuardDuty costs for next 3 months"
- "Predict Security Hub spending"
- "What will Inspector costs be next month?"

---

## 📊 ROI Analytics MCP Server Tools

### 1. **calculate_security_roi** - ROI Calculation

**Basic ROI Queries:**
- "Calculate my security ROI"
- "What's my return on security investment?"
- "Show me security ROI analysis"

**Time Period ROI:**
- "Calculate security ROI for the last 12 months"
- "What was my security ROI in Q3 2025?"
- "Show ROI from January to September 2025"

**Service-Specific ROI:**
- "Calculate ROI for GuardDuty investment"
- "What's the ROI on Security Hub?"
- "Show Inspector ROI analysis"

### 2. **analyze_cost_benefit** - Cost-Benefit Analysis

**Comprehensive Analysis:**
- "Analyze cost-benefit of my security investments"
- "Show security cost-benefit analysis"
- "What's the cost-benefit ratio for security services?"

**Service Comparisons:**
- "Compare cost-benefit of GuardDuty vs Security Hub"
- "Analyze cost-benefit across all security services"

### 3. **generate_roi_report** - Executive ROI Reports

**Standard Reports:**
- "Generate security ROI report"
- "Create executive ROI summary"
- "Show me a comprehensive ROI report"

**Time-Specific Reports:**
- "Generate ROI report for Q3 2025"
- "Create annual security ROI report"
- "Show quarterly ROI analysis"

### 4. **optimize_security_spend** - Spending Optimization

**Optimization Recommendations:**
- "How can I optimize my security spending?"
- "Show security cost optimization recommendations"
- "What are ways to improve security ROI?"

**Service-Specific Optimization:**
- "Optimize GuardDuty spending"
- "How can I reduce Security Hub costs?"
- "Show Inspector cost optimization options"

---

## 🔄 Combined Multi-Tool Queries

### Cross-Service Analysis:
- "Show me security status and costs for us-east-1"
- "Check GuardDuty findings and calculate ROI"
- "Analyze security compliance and spending trends"
- "Show security status, costs, and ROI for the last quarter"

### Executive Dashboards:
- "Give me a complete security overview with costs and ROI"
- "Show executive summary of security posture and spending"
- "Provide comprehensive security analysis including compliance, costs, and ROI"

### Regional Comparisons:
- "Compare security costs and ROI between us-east-1 and eu-west-1"
- "Show security status and spending across all regions"
- "Analyze regional security investment effectiveness"

---

## 📋 Parameter Reference

### Common Parameters Across Tools:

**Regions:**
- `us-east-1`, `us-west-2`, `eu-west-1`, `eu-central-1`, `ap-southeast-1`, `ap-southeast-2`

**Security Services:**
- `guardduty`, `securityhub`, `inspector`, `waf`, `config`

**Severity Levels:**
- `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`

**Time Periods:**
- `2025-09-01` to `2025-09-30` (September 2025)
- `last 30 days`, `last 6 months`, `last 12 months`
- `Q1 2025`, `Q2 2025`, `Q3 2025`

**Grouping Options:**
- `SERVICE`, `REGION`, `USAGE_TYPE`

**Compliance Types:**
- `encryption`, `network_security`, `access_control`

---

## 💡 Pro Tips for Maximum Effectiveness

1. **Be Specific**: Include regions, services, and time periods for detailed analysis
2. **Combine Queries**: Ask for status + costs + ROI in single requests
3. **Use Filters**: Specify severity levels and limits for focused results
4. **Compare Regions**: Analyze differences across geographical deployments
5. **Track Trends**: Regular monthly/quarterly analysis for better insights
6. **Executive Focus**: Request summaries and ROI reports for leadership presentations

---

## 🚀 Getting Started Examples

**New User - Basic Overview:**
- "Show me overall security status and costs"
- "What's my current security ROI?"
- "Give me a security investment summary"

**Regular Monitoring:**
- "Check this month's security findings and costs"
- "Show security trends compared to last month"
- "Any high-severity findings that need attention?"

**Executive Reporting:**
- "Generate quarterly security ROI report"
- "Show cost optimization opportunities"
- "Provide executive security investment summary"

This guide enables you to fully leverage all capabilities of the Executive Security ROI Analytics solution through natural language interactions with the AI chatbot.
