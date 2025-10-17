"""
Bedrock Agent Orchestrator for Executive Security ROI Analytics

This agent intelligently routes executive queries to the appropriate MCP servers
through the AgentCore Gateway based on query intent and context.
"""

import json
import boto3
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityROIOrchestrator:
    """
    Intelligent orchestrator for security ROI analytics queries.
    Routes requests to appropriate MCP servers via AgentCore Gateway.
    """
    
    def __init__(self, gateway_url: str):
        self.gateway_url = gateway_url.rstrip('/')
        self.bedrock = boto3.client('bedrock-runtime')
        self.session = boto3.Session()
        self.credentials = self.session.get_credentials()
        
        # Tool routing configuration
        self.tool_routing = {
            'security': {
                'keywords': ['security', 'compliance', 'findings', 'vulnerabilities', 'guardduty', 'inspector', 'config'],
                'endpoint': '/security',
                'tools': ['check_security_services', 'get_security_findings', 'check_compliance']
            },
            'cost': {
                'keywords': ['cost', 'spend', 'budget', 'expense', 'billing', 'price', 'forecast'],
                'endpoint': '/cost', 
                'tools': ['get_security_service_costs', 'analyze_cost_trends', 'get_cost_breakdown', 'forecast_costs']
            },
            'roi': {
                'keywords': ['roi', 'return', 'investment', 'benefit', 'value', 'optimization', 'efficiency'],
                'endpoint': '/roi',
                'tools': ['calculate_security_roi', 'analyze_cost_benefit', 'generate_roi_report', 'optimize_security_spend']
            }
        }

    def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze query to determine intent and appropriate MCP server."""
        query_lower = query.lower()
        
        # Score each category based on keyword matches
        scores = {}
        for category, config in self.tool_routing.items():
            score = sum(1 for keyword in config['keywords'] if keyword in query_lower)
            if score > 0:
                scores[category] = score
        
        # Determine primary intent
        if not scores:
            primary_intent = 'security'  # Default fallback
        else:
            primary_intent = max(scores, key=scores.get)
        
        return {
            'primary_intent': primary_intent,
            'scores': scores,
            'suggested_tools': self.tool_routing[primary_intent]['tools']
        }

    def _sign_request(self, method: str, url: str, data: str = None) -> Dict[str, str]:
        """Sign AWS request with SigV4"""
        request = AWSRequest(method=method, url=url, data=data)
        SigV4Auth(self.credentials, 'execute-api', 'us-east-1').add_auth(request)
        return dict(request.headers)

    def route_to_mcp(self, intent: str, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to appropriate MCP server via AgentCore Gateway."""
        try:
            endpoint = self.tool_routing[intent]['endpoint']
            url = f"{self.gateway_url}{endpoint}"
            
            payload = {
                'tool': tool_name,
                'parameters': parameters
            }
            
            logger.info(f"Routing to {url} with tool {tool_name}")
            
            # Sign the request with AWS SigV4
            data = json.dumps(payload)
            headers = self._sign_request('POST', url, data)
            headers['Content-Type'] = 'application/json'
            
            response = requests.post(
                url,
                data=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"MCP request failed: {response.status_code} - {response.text}")
                return {
                    'error': f"MCP request failed with status {response.status_code}",
                    'details': response.text
                }
                
        except Exception as e:
            logger.error(f"Error routing to MCP: {str(e)}")
            return {
                'error': f"Failed to route request: {str(e)}"
            }

    def process_executive_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process executive query and return comprehensive response.
        
        Args:
            query: Executive's natural language query
            context: Optional context (time range, specific services, etc.)
            
        Returns:
            Comprehensive response with data from appropriate MCP servers
        """
        try:
            # Analyze query intent
            intent_analysis = self.analyze_query_intent(query)
            primary_intent = intent_analysis['primary_intent']
            
            logger.info(f"Query intent: {primary_intent} for query: {query}")
            
            # Prepare default parameters
            default_params = {
                'region': context.get('region', 'us-east-1') if context else 'us-east-1',
                'time_range': context.get('time_range', '30d') if context else '30d'
            }
            
            # Route based on intent
            if primary_intent == 'security':
                return self._handle_security_query(query, default_params)
            elif primary_intent == 'cost':
                return self._handle_cost_query(query, default_params)
            elif primary_intent == 'roi':
                return self._handle_roi_query(query, default_params)
            else:
                # Multi-intent query - provide comprehensive overview
                return self._handle_comprehensive_query(query, default_params)
                
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                'error': f"Failed to process query: {str(e)}",
                'query': query
            }

    def _handle_security_query(self, query: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle security-focused queries."""
        results = {}
        
        # Get security services status
        security_status = self.route_to_mcp('security', 'check_security_services', params)
        results['security_status'] = security_status
        
        # Get recent findings if query mentions findings/vulnerabilities
        if any(word in query.lower() for word in ['finding', 'vulnerability', 'issue', 'alert']):
            findings = self.route_to_mcp('security', 'get_security_findings', {
                **params,
                'severity': 'HIGH,CRITICAL'
            })
            results['findings'] = findings
        
        return {
            'intent': 'security',
            'query': query,
            'results': results,
            'summary': self._generate_security_summary(results)
        }

    def _handle_cost_query(self, query: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle cost-focused queries."""
        results = {}
        
        # Get cost breakdown
        cost_breakdown = self.route_to_mcp('cost', 'get_cost_breakdown', params)
        results['cost_breakdown'] = cost_breakdown
        
        # Get trends if query mentions trends/changes
        if any(word in query.lower() for word in ['trend', 'change', 'increase', 'decrease']):
            trends = self.route_to_mcp('cost', 'analyze_cost_trends', params)
            results['trends'] = trends
        
        # Get forecast if query mentions future/forecast
        if any(word in query.lower() for word in ['forecast', 'future', 'predict', 'next']):
            forecast = self.route_to_mcp('cost', 'forecast_costs', {
                **params,
                'forecast_months': 3
            })
            results['forecast'] = forecast
        
        return {
            'intent': 'cost',
            'query': query,
            'results': results,
            'summary': self._generate_cost_summary(results)
        }

    def _handle_roi_query(self, query: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ROI-focused queries."""
        results = {}
        
        # Calculate ROI
        roi_calc = self.route_to_mcp('roi', 'calculate_security_roi', params)
        results['roi_calculation'] = roi_calc
        
        # Get cost-benefit analysis
        cost_benefit = self.route_to_mcp('roi', 'analyze_cost_benefit', params)
        results['cost_benefit'] = cost_benefit
        
        # Generate executive report if requested
        if any(word in query.lower() for word in ['report', 'summary', 'overview']):
            report = self.route_to_mcp('roi', 'generate_roi_report', params)
            results['executive_report'] = report
        
        return {
            'intent': 'roi',
            'query': query,
            'results': results,
            'summary': self._generate_roi_summary(results)
        }

    def _handle_comprehensive_query(self, query: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle queries that span multiple domains."""
        results = {}
        
        # Get data from all MCP servers
        results['security'] = self.route_to_mcp('security', 'check_security_services', params)
        results['costs'] = self.route_to_mcp('cost', 'get_cost_breakdown', params)
        results['roi'] = self.route_to_mcp('roi', 'calculate_security_roi', params)
        
        return {
            'intent': 'comprehensive',
            'query': query,
            'results': results,
            'summary': self._generate_comprehensive_summary(results)
        }

    def _generate_security_summary(self, results: Dict[str, Any]) -> str:
        """Generate executive summary for security results."""
        return "Security status overview with current service configurations and findings."

    def _generate_cost_summary(self, results: Dict[str, Any]) -> str:
        """Generate executive summary for cost results."""
        return "Security services cost analysis with trends and forecasts."

    def _generate_roi_summary(self, results: Dict[str, Any]) -> str:
        """Generate executive summary for ROI results."""
        return "Security investment ROI analysis with cost-benefit insights."

    def _generate_comprehensive_summary(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive executive summary."""
        return "Complete security ROI analytics overview covering services, costs, and returns."

# Lambda handler for Bedrock Agent
def lambda_handler(event, context):
    """AWS Lambda handler for Bedrock Agent integration."""
    try:
        # Extract query from Bedrock Agent event
        query = event.get('inputText', '')
        session_attributes = event.get('sessionAttributes', {})
        
        # Initialize orchestrator
        gateway_url = "https://yko4kspo9e.execute-api.us-east-1.amazonaws.com/prod"
        orchestrator = SecurityROIOrchestrator(gateway_url)
        
        # Process query
        response = orchestrator.process_executive_query(query, session_attributes)
        
        # Format response for Bedrock Agent
        return {
            'statusCode': 200,
            'body': json.dumps({
                'response': response,
                'sessionAttributes': session_attributes
            })
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
