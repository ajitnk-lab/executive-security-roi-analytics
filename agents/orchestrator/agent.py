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
                'keywords': ['security', 'compliance', 'findings', 'vulnerabilities', 'guardduty', 'inspector', 'config', 'threat', 'risk', 'breach', 'attack', 'malware', 'incident'],
                'endpoint': '/security',
                'tools': ['check_security_services', 'get_security_findings', 'check_compliance']
            },
            'cost': {
                'keywords': ['cost', 'spend', 'budget', 'expense', 'billing', 'price', 'forecast', 'money', 'dollar', 'fee', 'charge', 'payment', 'financial', 'costs'],
                'endpoint': '/cost', 
                'tools': ['get_security_service_costs', 'analyze_cost_trends', 'get_cost_breakdown', 'forecast_costs']
            },
            'roi': {
                'keywords': ['roi', 'return', 'investment', 'benefit', 'value', 'optimization', 'efficiency', 'worth', 'payback', 'profit', 'savings', 'business case'],
                'endpoint': '/roi',
                'tools': ['calculate_security_roi', 'analyze_cost_benefit', 'generate_roi_report', 'optimize_security_spend']
            }
        }

    def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze query to determine intent and appropriate MCP server."""
        query_lower = query.lower()
        logger.debug(f"Analyzing query intent for: '{query_lower}'")
        
        # Score each category based on keyword matches
        scores = {}
        for category, config in self.tool_routing.items():
            score = sum(1 for keyword in config['keywords'] if keyword in query_lower)
            scores[category] = score
            logger.debug(f"Category '{category}' scored {score} points")
        
        # Determine primary intent with better logic
        if not any(scores.values()):
            # No keywords matched - analyze query context
            if any(word in query_lower for word in ['how much', 'what does it cost', 'spending', 'money', 'dollars', '$']):
                primary_intent = 'cost'
                logger.debug("No keyword matches, but detected cost context")
            elif any(word in query_lower for word in ['worth it', 'return on', 'benefit', 'value', 'investment']):
                primary_intent = 'roi'
                logger.debug("No keyword matches, but detected ROI context")
            else:
                primary_intent = 'security'  # Default fallback
                logger.debug("No keyword matches, defaulting to security")
        else:
            # Get highest scoring category
            max_score = max(scores.values())
            # If there's a tie, prioritize cost/roi over security for business queries
            if scores.get('cost', 0) == max_score and max_score > 0:
                primary_intent = 'cost'
            elif scores.get('roi', 0) == max_score and max_score > 0:
                primary_intent = 'roi'
            else:
                primary_intent = max(scores, key=scores.get)
            logger.debug(f"Highest scoring category: '{primary_intent}' with {max_score} points")
        
        logger.info(f"Query intent analysis: '{primary_intent}' for query: '{query}'")
        
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
            
            # Use correct MCP protocol format
            payload = {
                'tool_name': tool_name,
                'arguments': parameters
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
        # Set logging level to DEBUG for detailed output
        logger.setLevel(logging.DEBUG)
        logger.debug(f"=== ORCHESTRATOR INVOKED ===")
        logger.debug(f"Full event received: {json.dumps(event, indent=2)}")
        logger.debug(f"Context: {context}")
        
        # Handle different event formats from Bedrock Agent
        query = ""
        session_attributes = {}
        
        # Check if this is a direct Bedrock Agent invocation
        if 'inputText' in event:
            query = event.get('inputText', '')
            session_attributes = event.get('sessionAttributes', {})
            logger.debug(f"Direct Bedrock Agent format detected - Query: {query}")
        # Check if this is an action group invocation
        elif 'requestBody' in event:
            request_body = event.get('requestBody', {})
            logger.debug(f"Action group format detected - RequestBody: {request_body}")
            if 'content' in request_body:
                content = request_body['content']
                if 'application/json' in content:
                    json_content = json.loads(content['application/json'])
                    query = json_content.get('query', '')
                    session_attributes = json_content.get('context', {})
        # Check if this is a simple query in the event
        elif 'query' in event:
            query = event.get('query', '')
            session_attributes = event.get('context', {})
            logger.debug(f"Simple query format detected - Query: {query}")
        else:
            # Fallback - try to extract from event body
            logger.debug(f"Unknown event format, using fallback")
            query = str(event)
            
        logger.info(f"Extracted query: '{query}'")
        logger.debug(f"Session attributes: {session_attributes}")
        
        if not query:
            logger.error(f"No query found in event")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'No query found in event',
                    'event_received': event
                })
            }
        
        # Initialize orchestrator
        gateway_url = os.environ.get('GATEWAY_URL', "https://yko4kspo9e.execute-api.us-east-1.amazonaws.com/prod")
        logger.debug(f"Using gateway URL: {gateway_url}")
        orchestrator = SecurityROIOrchestrator(gateway_url)
        
        # Process query
        logger.debug(f"Processing query with orchestrator...")
        response = orchestrator.process_executive_query(query, session_attributes)
        logger.debug(f"Orchestrator response: {json.dumps(response, indent=2)}")
        
        # Format response for Bedrock Agent
        if 'error' in response:
            # Return a user-friendly error message
            response_text = f"I encountered an issue while processing your request: {response.get('summary', 'Please try rephrasing your question.')}"
            logger.error(f"Error in orchestrator response: {response}")
        else:
            # Check if user wants just a number/rating
            query_lower = query.lower()
            wants_number_only = any(phrase in query_lower for phrase in [
                'what is', 'what\'s', 'show me', 'give me', 'tell me'
            ]) and any(phrase in query_lower for phrase in [
                'rating', 'score', 'spend', 'cost', 'number', 'amount', 'total'
            ])
            
            # Format the response based on intent
            intent = response.get('intent', 'general')
            results = response.get('results', {})
            logger.debug(f"Response intent: {intent}, Results keys: {list(results.keys())}, Number only: {wants_number_only}")
            
            if wants_number_only:
                # Extract just the key number/value from MCP server responses ONLY
                if intent == 'cost' and 'cost_breakdown' in results:
                    cost_data = results['cost_breakdown']
                    if isinstance(cost_data, dict) and 'result' in cost_data:
                        try:
                            cost_json = json.loads(cost_data['result'])
                            total_cost = cost_json.get('total_cost', 0)
                            if total_cost == 0:
                                response_text = "$0"
                            else:
                                response_text = f"${abs(total_cost):.2f}"
                        except Exception as e:
                            logger.error(f"Failed to parse cost data: {e}")
                            response_text = "Cost data unavailable"
                elif intent == 'security' and 'security_status' in results:
                    # Calculate security score based on actual MCP server data
                    try:
                        security_data = results['security_status']
                        if isinstance(security_data, dict) and 'result' in security_data:
                            security_json = json.loads(security_data['result'])
                            enabled_count = 0
                            total_services = 0
                            for region_data in security_json.values():
                                if isinstance(region_data, dict):
                                    for service, config in region_data.items():
                                        if isinstance(config, dict) and 'status' in config:
                                            total_services += 1
                                            if config['status'] == 'enabled':
                                                enabled_count += 1
                            if total_services > 0:
                                score = int((enabled_count / total_services) * 100)
                                response_text = f"{score}/100"
                            else:
                                response_text = "Security data unavailable"
                    except Exception as e:
                        logger.error(f"Failed to parse security data: {e}")
                        response_text = "Security data unavailable"
                elif intent == 'roi' and 'roi_calculation' in results:
                    # Extract ROI from actual MCP server response
                    try:
                        roi_data = results['roi_calculation']
                        if isinstance(roi_data, dict) and 'result' in roi_data:
                            roi_json = json.loads(roi_data['result'])
                            roi_percentage = roi_json.get('roi_percentage', roi_json.get('total_roi', 0))
                            response_text = f"{roi_percentage}%"
                        else:
                            response_text = "ROI data unavailable"
                    except Exception as e:
                        logger.error(f"Failed to parse ROI data: {e}")
                        response_text = "ROI data unavailable"
                else:
                    response_text = "Data not available - please try a more specific query"
            else:
                # Full response format
                if intent == 'cost':
                    response_text = f"Here's your security cost analysis:\n\n{response.get('summary', 'Cost analysis completed.')}"
                    if 'cost_breakdown' in results:
                        cost_data = results['cost_breakdown']
                        if isinstance(cost_data, dict) and 'result' in cost_data:
                            response_text += f"\n\nDetails: {cost_data['result']}"
                elif intent == 'security':
                    response_text = f"Here's your security status:\n\n{response.get('summary', 'Security analysis completed.')}"
                    if 'security_status' in results:
                        security_data = results['security_status']
                        if isinstance(security_data, dict) and 'result' in security_data:
                            response_text += f"\n\nDetails: {security_data['result']}"
                elif intent == 'roi':
                    response_text = f"Here's your ROI analysis:\n\n{response.get('summary', 'ROI analysis completed.')}"
                    if 'roi_calculation' in results:
                        roi_data = results['roi_calculation']
                        if isinstance(roi_data, dict) and 'result' in roi_data:
                            response_text += f"\n\nDetails: {roi_data['result']}"
                else:
                    response_text = f"Analysis complete: {response.get('summary', 'I have processed your request.')}"
        
        logger.debug(f"Final response text: {response_text}")
        
        # Return proper Bedrock Agent action group response format
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event.get('actionGroup', 'security-analytics'),
                'apiPath': event.get('apiPath', '/analyze'),
                'httpMethod': event.get('httpMethod', 'POST'),
                'httpStatusCode': 200,
                'responseBody': {
                    'application/json': {
                        'body': response_text
                    }
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}", exc_info=True)
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event.get('actionGroup', 'security-analytics'),
                'apiPath': event.get('apiPath', '/analyze'),
                'httpMethod': event.get('httpMethod', 'POST'),
                'httpStatusCode': 500,
                'responseBody': {
                    'application/json': {
                        'body': f"I'm sorry, I encountered an error processing your request. Please try again or rephrase your question."
                    }
                }
            }
        }
