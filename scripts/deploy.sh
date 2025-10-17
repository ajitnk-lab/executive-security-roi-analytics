#!/bin/bash
# deploy.sh - Complete deployment script for Executive Security ROI Analytics

set -e

echo "🚀 Starting Executive Security ROI Analytics Deployment..."

# Check prerequisites
echo "📋 Checking prerequisites..."
command -v aws >/dev/null 2>&1 || { echo "❌ AWS CLI required"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js required"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 required"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ npm required"; exit 1; }

echo "✅ Prerequisites check passed"

# Verify AWS credentials
echo "🔐 Verifying AWS credentials..."
aws sts get-caller-identity > /dev/null || { echo "❌ AWS credentials not configured"; exit 1; }
echo "✅ AWS credentials verified"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

cd dashboard/frontend
npm install
cd ../..

# Setup Python environments
echo "🐍 Setting up Python environments..."
for mcp in security-mcp cost-mcp roi-analytics-mcp; do
  echo "  Setting up $mcp..."
  python3 -m venv mcp-servers/$mcp/venv
  source mcp-servers/$mcp/venv/bin/activate
  pip install -r mcp-servers/$mcp/requirements.txt
  deactivate
done

# Deploy infrastructure
echo "🏗️ Deploying infrastructure..."
cd infrastructure

# Bootstrap CDK if needed
echo "🥾 Bootstrapping CDK..."
npx cdk bootstrap

# Phase 1: Core Infrastructure
echo "📡 Phase 1: Core Infrastructure..."
npx cdk deploy InfrastructureStack/AgentCoreInfrastructure --require-approval never
npx cdk deploy InfrastructureStack/MCPDeployment --require-approval never
npx cdk deploy InfrastructureStack/AgentCoreGateway --require-approval never

# Phase 2: Authentication & Backend
echo "🔐 Phase 2: Authentication & Backend..."
npx cdk deploy InfrastructureStack/Authentication --require-approval never
npx cdk deploy InfrastructureStack/BedrockAgent --require-approval never
npx cdk deploy InfrastructureStack/DashboardBackend --require-approval never

# Phase 3: Frontend
echo "🌐 Phase 3: Frontend..."
cd ../dashboard/frontend
npm run build
cd ../../infrastructure
npx cdk deploy InfrastructureStack/FrontendDeployment --require-approval never

# Get deployment URLs
echo "📋 Getting deployment information..."
FRONTEND_URL=$(aws cloudformation describe-stacks \
  --stack-name InfrastructureStackFrontendDeployment5F17D99F \
  --query 'Stacks[0].Outputs[?OutputKey==`FrontendUrl`].OutputValue' \
  --output text 2>/dev/null || echo "Not available")

BACKEND_URL=$(aws cloudformation describe-stacks \
  --stack-name InfrastructureStackDashboardBackendD3B930A3 \
  --query 'Stacks[0].Outputs[?OutputKey==`DashboardAPIUrl`].OutputValue' \
  --output text 2>/dev/null || echo "Not available")

USER_POOL_ID=$(aws cloudformation describe-stacks \
  --stack-name InfrastructureStackAuthentication56C4EC5D \
  --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
  --output text 2>/dev/null || echo "Not available")

# Create test user
if [ "$USER_POOL_ID" != "Not available" ]; then
  echo "👤 Creating test user..."
  aws cognito-idp admin-create-user \
    --user-pool-id $USER_POOL_ID \
    --username testexec@company.com \
    --user-attributes Name=email,Value=testexec@company.com \
    --temporary-password TempPass123! \
    --message-action SUPPRESS 2>/dev/null || echo "User may already exist"

  aws cognito-idp admin-set-user-password \
    --user-pool-id $USER_POOL_ID \
    --username testexec@company.com \
    --password ExecutiveTest123! \
    --permanent 2>/dev/null || echo "Password may already be set"
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📊 Dashboard URL: $FRONTEND_URL"
echo "🔧 Backend API: $BACKEND_URL"
echo "👤 Test Login: testexec@company.com / ExecutiveTest123!"
echo ""
echo "📖 Next steps:"
echo "1. Navigate to the Dashboard URL"
echo "2. Login with the test credentials"
echo "3. Try asking the chatbot: 'What is my security ROI?'"
echo "4. Check the CHATBOT_PROMPTS_GUIDE.md for more examples"
echo ""
