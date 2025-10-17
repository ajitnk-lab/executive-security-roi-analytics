"""Lambda handler wrapper for Cost MCP Server"""
import json
import asyncio
from server import CostMCPServer

def lambda_handler(event, context):
    """AWS Lambda handler for Cost MCP Server"""
    try:
        # Extract tool name and arguments from event
        tool_name = event.get('tool_name')
        arguments = event.get('arguments', {})
        
        if not tool_name:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing tool_name in event'})
            }
        
        # Create server instance and call tool
        server = CostMCPServer()
        
        # Run async tool call
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                server.server.call_tool(tool_name, arguments)
            )
            
            # Extract text content from MCP response
            response_text = result[0].text if result and hasattr(result[0], 'text') else str(result)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'tool_name': tool_name,
                    'result': response_text
                })
            }
        finally:
            loop.close()
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
