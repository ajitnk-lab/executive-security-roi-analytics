"""Lambda handler wrapper for ROI Analytics MCP Server"""
import json
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    """AWS Lambda handler for ROI Analytics MCP Server"""
    try:
        logger.debug(f"Received event: {json.dumps(event)}")
        
        # Handle API Gateway proxy event format
        if 'body' in event:
            # API Gateway proxy integration
            body = event['body']
            if isinstance(body, str):
                body_data = json.loads(body)
            else:
                body_data = body
        else:
            # Direct invocation
            body_data = event
        
        logger.debug(f"Parsed body: {json.dumps(body_data)}")
        
        # Extract tool name and arguments
        tool_name = body_data.get('tool_name')
        arguments = body_data.get('arguments', {})
        
        logger.debug(f"Tool: {tool_name}, Arguments: {arguments}")
        
        if not tool_name:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing tool_name in event'})
            }
        
        # Import here to avoid conflicts
        from server import ROIAnalyticsMCPServer
        
        # Create server instance
        server_instance = ROIAnalyticsMCPServer()
        
        # Run async tool call using the private methods directly
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Call the appropriate private method directly
            if tool_name == "calculate_security_roi":
                result = loop.run_until_complete(
                    server_instance._calculate_security_roi(arguments)
                )
            elif tool_name == "analyze_cost_benefit":
                result = loop.run_until_complete(
                    server_instance._analyze_cost_benefit(arguments)
                )
            elif tool_name == "generate_roi_report":
                result = loop.run_until_complete(
                    server_instance._generate_roi_report(arguments)
                )
            elif tool_name == "optimize_security_spend":
                result = loop.run_until_complete(
                    server_instance._optimize_security_spend(arguments)
                )
            else:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': f'Unknown tool: {tool_name}'})
                }
            
            logger.debug(f"Raw result: {result}")
            
            # Extract text content from MCP response
            if isinstance(result, list) and result:
                if hasattr(result[0], 'text'):
                    response_text = result[0].text
                else:
                    response_text = str(result[0])
            else:
                response_text = str(result)
            
            logger.debug(f"Response text: {response_text}")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'tool_name': tool_name,
                    'result': response_text
                })
            }
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
