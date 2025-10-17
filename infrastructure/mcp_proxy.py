import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """MCP Proxy with mock data for all three servers (security, cost, roi)"""
    
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract tool info
        api_path = event.get('apiPath', '')
        
        # Return appropriate mock data based on API path
        if api_path.startswith('/security/'):
            result = {
                "security_score": 85,
                "services": {
                    "guardduty": {"enabled": True, "status": "ACTIVE"},
                    "securityhub": {"enabled": True, "status": "ACTIVE"}
                }
            }
        elif api_path.startswith('/cost/'):
            result = {
                "total_cost": 125.50,
                "services": {
                    "guardduty": {"cost": 45.20, "currency": "USD"},
                    "securityhub": {"cost": 80.30, "currency": "USD"}
                },
                "time_period": "last_month"
            }
        elif api_path.startswith('/roi/'):
            result = {
                "roi_percentage": 15.8,
                "investment": 125.50,
                "savings": 198.75,
                "analysis": "Strong ROI from security investments"
            }
        else:
            result = {"error": f"Unknown API path: {api_path}"}
        
        # Correct Bedrock Agent response format
        response = {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event.get('actionGroup', ''),
                'apiPath': api_path,
                'httpMethod': event.get('httpMethod', 'POST'),
                'httpStatusCode': 200,
                'responseBody': {
                    'application/json': {
                        'body': json.dumps(result)
                    }
                }
            }
        }
        
        logger.info(f"Returning response: {json.dumps(response)}")
        return response
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event.get('actionGroup', ''),
                'apiPath': event.get('apiPath', ''),
                'httpMethod': event.get('httpMethod', 'POST'),
                'httpStatusCode': 500,
                'responseBody': {
                    'application/json': {
                        'body': json.dumps({"error": str(e)})
                    }
                }
            }
        }
