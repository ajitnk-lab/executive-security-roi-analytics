import json
import boto3
import os
from typing import Dict, Any

# Initialize Bedrock Agent Runtime client
bedrock_client = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

AGENT_ID = 'DTAX1II3AK'
AGENT_ALIAS_ID = 'GCWHOE7WNP'

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for dashboard backend API with authentication
    """
    try:
        # Parse request
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        body = event.get('body', '{}')
        
        # Check for authentication
        auth_context = event.get('requestContext', {}).get('authorizer', {})
        if not auth_context.get('claims'):
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Unauthorized'})
            }
        
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
        
        # Route requests
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
            'body': json.dumps({'error': str(e)})
        }

def handle_chat(body_data: Dict[str, Any], headers: Dict[str, str], auth_context: Dict[str, Any]) -> Dict[str, Any]:
    """Handle chat requests to Bedrock Agent"""
    try:
        message = body_data.get('message', '')
        session_id = body_data.get('sessionId', f"executive-{auth_context.get('claims', {}).get('sub', 'unknown')}")
        
        if not message:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Message is required'})
            }
        
        # Invoke Bedrock Agent
        response = bedrock_client.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText=message
        )
        
        # Process streaming response
        agent_response = ""
        if 'completion' in response:
            for chunk in response['completion']:
                if 'chunk' in chunk and 'bytes' in chunk['chunk']:
                    agent_response += chunk['chunk']['bytes'].decode('utf-8')
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'response': agent_response,
                'sessionId': session_id
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'Chat error: {str(e)}'})
        }

def handle_metrics(headers: Dict[str, str], auth_context: Dict[str, Any]) -> Dict[str, Any]:
    """Handle metrics requests"""
    try:
        # Mock metrics data - in production, this would fetch real data
        metrics = {
            'securityROI': {
                'value': '24.5%',
                'change': '+3.2%',
                'trend': 'up'
            },
            'monthlySpend': {
                'value': '$12,450',
                'change': '+5.1%',
                'trend': 'up'
            },
            'securityScore': {
                'value': '87/100',
                'change': '+2 pts',
                'trend': 'up'
            },
            'lastUpdated': '2025-10-17T12:26:17.080Z',
            'user': auth_context.get('claims', {}).get('email', 'Unknown')
        }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(metrics)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'Metrics error: {str(e)}'})
        }
