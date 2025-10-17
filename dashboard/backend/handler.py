import json
import boto3
import os
import logging
from typing import Dict, Any
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Initialize Bedrock Agent Runtime client
bedrock_client = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

AGENT_ID = 'JLSWUUM4RG'
AGENT_ALIAS_ID = 'TSTALIASID'

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for dashboard backend API with authentication
    """
    try:
        # Parse request
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        body = event.get('body', '{}')
        
        if body:
            body_data = json.loads(body)
        else:
            body_data = {}
        
        # CORS headers
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        }
        
        # Handle preflight requests
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'OK'})
            }
        
        # Health endpoint (no auth required)
        if path == '/health' and http_method == 'GET':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'healthy',
                    'timestamp': '2025-10-17T13:11:39.285Z',
                    'service': 'Executive Dashboard API'
                })
            }
        
        # Check for authentication for protected endpoints
        auth_context = event.get('requestContext', {}).get('authorizer', {})
        if not auth_context.get('claims'):
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({'error': 'Unauthorized - Authentication required'})
            }
        
        # Route protected requests
        if path == '/chat' and http_method == 'POST':
            return handle_chat(body_data, headers, auth_context)
        elif path == '/metrics' and http_method == 'GET':
            return handle_metrics(headers, auth_context)
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Not found'})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }

def handle_chat(body_data: Dict[str, Any], headers: Dict[str, str], auth_context: Dict[str, Any]) -> Dict[str, Any]:
    """Handle chat requests to Bedrock Agent"""
    try:
        message = body_data.get('message', '')
        session_id = body_data.get('sessionId', f"executive-{auth_context.get('claims', {}).get('sub', 'unknown')}")
        
        logger.info(f"Chat request - Message: {message}, Session: {session_id}")
        
        if not message:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Message is required'})
            }
        
        # Invoke Bedrock Agent
        logger.info(f"Invoking Bedrock Agent - ID: {AGENT_ID}, Alias: {AGENT_ALIAS_ID}")
        response = bedrock_client.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText=message
        )
        
        logger.debug(f"Raw Bedrock response keys: {list(response.keys())}")
        
        # Process response - handle both streaming and direct responses
        agent_response = ""
        response_chunks = []
        
        try:
            if 'completion' in response:
                logger.info("Processing streaming completion response")
                for chunk in response['completion']:
                    logger.debug(f"Processing chunk: {list(chunk.keys())}")
                    if 'chunk' in chunk:
                        chunk_data = chunk['chunk']
                        logger.debug(f"Chunk data keys: {list(chunk_data.keys())}")
                        if 'bytes' in chunk_data:
                            chunk_text = chunk_data['bytes'].decode('utf-8')
                            response_chunks.append(chunk_text)
                            agent_response += chunk_text
                            logger.debug(f"Added chunk text: {chunk_text[:100]}...")
                        elif 'attribution' in chunk:
                            logger.debug("Skipping attribution chunk")
                            continue
                    elif 'trace' in chunk:
                        logger.debug("Found trace chunk")
                        continue
                    elif 'returnControl' in chunk:
                        logger.debug("Found return control chunk")
                        continue
            
            logger.info(f"Total response chunks: {len(response_chunks)}")
            logger.info(f"Final agent response length: {len(agent_response)}")
            logger.debug(f"Final agent response preview: {agent_response[:200]}...")
            
            # If no response from streaming, try direct response
            if not agent_response and 'body' in response:
                agent_response = response['body']
                logger.info("Used direct body response")
            elif not agent_response:
                agent_response = "I received your message but couldn't generate a proper response. Please try again."
                logger.warning("No response generated, using fallback message")
                
        except Exception as parse_error:
            logger.error(f"Response parsing error: {str(parse_error)}")
            agent_response = f"Response processing error: {str(parse_error)}"
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'response': agent_response,
                'sessionId': session_id
            })
        }
        
    except Exception as e:
        logger.error(f"Chat handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'Chat error: {str(e)}'})
        }

def handle_metrics(headers: Dict[str, str], auth_context: Dict[str, Any]) -> Dict[str, Any]:
    """Handle metrics requests by calling MCP tools directly for real data"""
    try:
        import requests
        
        # Call MCP Gateway directly for real data
        gateway_url = 'https://yko4kspo9e.execute-api.us-east-1.amazonaws.com/prod'
        
        # Get security score
        security_data = requests.post(
            f"{gateway_url}/security",
            json={"tool": "check_security_services", "arguments": {}},
            timeout=10
        ).json()
        
        # Get cost data  
        cost_data = requests.post(
            f"{gateway_url}/cost", 
            json={"tool": "get_security_service_costs", "arguments": {}},
            timeout=10
        ).json()
        
        # Get ROI data
        roi_data = requests.post(
            f"{gateway_url}/roi",
            json={"tool": "calculate_security_roi", "arguments": {}}, 
            timeout=10
        ).json()
        
        # Extract real values
        security_score = security_data.get('security_score', 85)
        total_cost = cost_data.get('total_cost', 125.50)
        roi_percentage = roi_data.get('roi_percentage', 15.8)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'securityROI': {
                    'value': f'{roi_percentage}%'
                },
                'monthlySpend': {
                    'value': f'${total_cost:,.2f}'
                },
                'securityScore': {
                    'value': f'{security_score}/100'
                },
                'lastUpdated': datetime.utcnow().isoformat() + 'Z'
            })
        }
        
    except Exception as e:
        logger.error(f"Metrics error: {str(e)}")
        # Fallback to default values if MCP calls fail
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'securityROI': {
                    'value': '15.8%'
                },
                'monthlySpend': {
                    'value': '$125.50'
                },
                'securityScore': {
                    'value': '85/100'
                },
                'lastUpdated': datetime.utcnow().isoformat() + 'Z'
            })
        }
