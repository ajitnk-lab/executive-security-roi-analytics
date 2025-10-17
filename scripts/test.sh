#!/bin/bash
# test.sh - Test Executive Security ROI Analytics deployment

set -e

echo "🧪 Testing Executive Security ROI Analytics deployment..."

# Get URLs from CloudFormation stacks
echo "📋 Getting deployment URLs..."

FRONTEND_URL=$(aws cloudformation describe-stacks \
  --stack-name InfrastructureStackFrontendDeployment5F17D99F \
  --query 'Stacks[0].Outputs[?OutputKey==`FrontendUrl`].OutputValue' \
  --output text 2>/dev/null || echo "Not found")

BACKEND_URL=$(aws cloudformation describe-stacks \
  --stack-name InfrastructureStackDashboardBackendD3B930A3 \
  --query 'Stacks[0].Outputs[?OutputKey==`DashboardAPIUrl`].OutputValue' \
  --output text 2>/dev/null || echo "Not found")

GATEWAY_URL=$(aws cloudformation describe-stacks \
  --stack-name InfrastructureStackAgentCoreGatewayC771425B \
  --query 'Stacks[0].Outputs[?OutputKey==`GatewayUrl`].OutputValue' \
  --output text 2>/dev/null || echo "Not found")

echo ""
echo "🌐 Frontend URL: $FRONTEND_URL"
echo "🔧 Backend URL: $BACKEND_URL"
echo "🚪 Gateway URL: $GATEWAY_URL"
echo ""

# Test health endpoints
if [ "$BACKEND_URL" != "Not found" ]; then
  echo "🔍 Testing backend health endpoint..."
  if curl -s -f "$BACKEND_URL/health" > /dev/null; then
    echo "✅ Backend health check passed"
    curl -s "$BACKEND_URL/health" | jq . 2>/dev/null || echo "Response received (jq not available for formatting)"
  else
    echo "❌ Backend health check failed"
  fi
  echo ""
fi

if [ "$GATEWAY_URL" != "Not found" ]; then
  echo "🔍 Testing gateway health endpoint..."
  if curl -s -f "$GATEWAY_URL/health" > /dev/null; then
    echo "✅ Gateway health check passed"
    curl -s "$GATEWAY_URL/health" | jq . 2>/dev/null || echo "Response received (jq not available for formatting)"
  else
    echo "❌ Gateway health check failed"
  fi
  echo ""
fi

# Test MCP endpoints
if [ "$GATEWAY_URL" != "Not found" ]; then
  echo "🔍 Testing MCP endpoints..."
  
  for endpoint in security cost roi; do
    echo "  Testing $endpoint endpoint..."
    if curl -s -f "$GATEWAY_URL/$endpoint" -X POST \
       -H "Content-Type: application/json" \
       -d '{"tool":"test","arguments":{}}' > /dev/null; then
      echo "  ✅ $endpoint endpoint responding"
    else
      echo "  ⚠️  $endpoint endpoint may require authentication"
    fi
  done
  echo ""
fi

# Check Lambda functions
echo "🔍 Checking Lambda functions..."
LAMBDA_FUNCTIONS=$(aws lambda list-functions \
  --query 'Functions[?contains(FunctionName, `security-roi-analytics`)].FunctionName' \
  --output text 2>/dev/null || echo "")

if [ -n "$LAMBDA_FUNCTIONS" ]; then
  echo "✅ Found MCP Lambda functions:"
  for func in $LAMBDA_FUNCTIONS; do
    echo "  - $func"
  done
else
  echo "❌ No MCP Lambda functions found"
fi
echo ""

# Check Bedrock agents
echo "🔍 Checking Bedrock agents..."
AGENTS=$(aws bedrock-agent list-agents \
  --query 'agentSummaries[?contains(agentName, `security-roi-analytics`)].agentName' \
  --output text 2>/dev/null || echo "")

if [ -n "$AGENTS" ]; then
  echo "✅ Found Bedrock agents:"
  for agent in $AGENTS; do
    echo "  - $agent"
  done
else
  echo "❌ No Bedrock agents found"
fi
echo ""

# Summary
echo "📊 Test Summary:"
echo "=================="
if [ "$FRONTEND_URL" != "Not found" ]; then
  echo "✅ Frontend deployed"
else
  echo "❌ Frontend not found"
fi

if [ "$BACKEND_URL" != "Not found" ]; then
  echo "✅ Backend deployed"
else
  echo "❌ Backend not found"
fi

if [ "$GATEWAY_URL" != "Not found" ]; then
  echo "✅ Gateway deployed"
else
  echo "❌ Gateway not found"
fi

echo ""
echo "🎯 Next Steps:"
echo "1. Navigate to: $FRONTEND_URL"
echo "2. Login with: testexec@company.com / ExecutiveTest123!"
echo "3. Test the chatbot with: 'What is my security ROI?'"
echo "4. Check CloudWatch logs if any issues occur"
