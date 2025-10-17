#!/usr/bin/env python3
"""
MCP Proxy Lambda Function
Direct proxy to AgentCore Gateway MCP servers with proper parameter handling
"""

import json
import os
import logging
import requests
from typing import Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for direct MCP tool calls from Bedrock Agent
    """
    try:
        logger.debug(f"=== MCP PROXY INVOKED ===")
        logger.debug(f"Full event received: {json.dumps(event, indent=2)}")
        
        # Extract API path and method from Bedrock Agent event
        api_path = event.get('apiPath', '')
        http_method = event.get('httpMethod', 'POST')
        
        # Extract request body
        request_body = {}
        if 'requestBody' in event:
            content = event['requestBody'].get('content', {})
            if 'application/json' in content:
                request_body = json.loads(content['application/json'])
        
        logger.info(f"API Path: {api_path}, Method: {http_method}")
        logger.info(f"Request Body: {json.dumps(request_body, indent=2)}")
        
        # Route to appropriate MCP server
        gateway_url = os.environ.get('GATEWAY_URL', 'https://yko4kspo9e.execute-api.us-east-1.amazonaws.com/prod')
        
        if api_path.startswith('/security/'):
            # Extract tool name from path
            tool_name = api_path.replace('/security/', '')
            mcp_endpoint = f"{gateway_url}/security"
            
            # Prepare MCP request
            mcp_request = {
                "tool": tool_name,
                "arguments": request_body
            }
            
            logger.info(f"Calling MCP endpoint: {mcp_endpoint}")
            logger.info(f"MCP request: {json.dumps(mcp_request, indent=2)}")
            
            # Call MCP server
            response = requests.post(
                mcp_endpoint,
                json=mcp_request,
                timeout=25,
                headers={'Content-Type': 'application/json'}
            )
            
            logger.info(f"MCP response status: {response.status_code}")
            logger.debug(f"MCP response: {response.text}")
            
            if response.status_code == 200:
                mcp_result = response.json()
                
                # Format response for Bedrock Agent
                formatted_response = {
                    "tool_name": tool_name,
                    "result": mcp_result,
                    "status": "success"
                }
                
                return {
                    'messageVersion': '1.0',
                    'response': {
                        'actionGroup': event.get('actionGroup', 'security-tools'),
                        'apiPath': api_path,
                        'httpMethod': http_method,
                        'httpStatusCode': 200,
                        'responseBody': {
                            'application/json': {
                                'body': json.dumps(formatted_response)
                            }
                        }
                    }
                }
            else:
                logger.error(f"MCP server error: {response.status_code} - {response.text}")
                return {
                    'messageVersion': '1.0',
                    'response': {
                        'actionGroup': event.get('actionGroup', 'security-tools'),
                        'apiPath': api_path,
                        'httpMethod': http_method,
                        'httpStatusCode': 500,
                        'responseBody': {
                            'application/json': {
                                'body': json.dumps({
                                    "error": f"MCP server error: {response.status_code}",
                                    "details": response.text
                                })
                            }
                        }
                    }
                }
        else:
            logger.error(f"Unknown API path: {api_path}")
            return {
                'messageVersion': '1.0',
                'response': {
                    'actionGroup': event.get('actionGroup', 'security-tools'),
                    'apiPath': api_path,
                    'httpMethod': http_method,
                    'httpStatusCode': 404,
                    'responseBody': {
                        'application/json': {
                            'body': json.dumps({
                                "error": f"Unknown API path: {api_path}"
                            })
                        }
                    }
                }
            }
            
    except Exception as e:
        logger.error(f"MCP Proxy error: {str(e)}")
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event.get('actionGroup', 'security-tools'),
                'apiPath': event.get('apiPath', '/unknown'),
                'httpMethod': event.get('httpMethod', 'POST'),
                'httpStatusCode': 500,
                'responseBody': {
                    'application/json': {
                        'body': json.dumps({
                            "error": f"MCP Proxy error: {str(e)}"
                        })
                    }
                }
            }
        }
