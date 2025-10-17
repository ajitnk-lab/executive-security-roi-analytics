# Executive Security ROI Analytics - Deployment Guide

## 🚀 Complete Deployment Instructions

This guide provides step-by-step instructions to deploy the Executive Security ROI Analytics solution from scratch.

---

## 📋 Prerequisites

### Required Tools & Versions
```bash
# Check versions
python3 --version    # >= 3.10
node --version       # >= 18.0
npm --version        # >= 8.0
aws --version        # >= 2.0
git --version        # >= 2.0
```

### AWS Requirements
- AWS CLI configured with appropriate credentials
- Account with permissions for: Lambda, API Gateway, S3, CloudFront, Cognito, Bedrock, IAM
- Bedrock model access enabled (Claude 3 Haiku)
- Cost Explorer API access enabled

### Install Dependencies
```bash
# Install AWS CDK
npm install -g aws-cdk@latest

# Install AgentCore toolkit
pip install bedrock-agentcore-starter-toolkit

# Verify installations
cdk --version
pip list | grep agentcore
```

---

## 🛠️ Step-by-Step Deployment

### 1. Clone Repository
```bash
git clone https://github.com/ajitnk-lab/executive-security-roi-analytics.git
cd executive-security-roi-analytics
```

### 2. Install Project Dependencies
```bash
# Install root dependencies
npm install

# Install frontend dependencies
cd dashboard/frontend
npm install
cd ../..

# Create Python virtual environments for MCP servers
python3 -m venv mcp-servers/security-mcp/venv
source mcp-servers/security-mcp/venv/bin/activate
pip install -r mcp-servers/security-mcp/requirements.txt
deactivate

python3 -m venv mcp-servers/cost-mcp/venv
source mcp-servers/cost-mcp/venv/bin/activate
pip install -r mcp-servers/cost-mcp/requirements.txt
deactivate

python3 -m venv mcp-servers/roi-analytics-mcp/venv
source mcp-servers/roi-analytics-mcp/venv/bin/activate
pip install -r mcp-servers/roi-analytics-mcp/requirements.txt
deactivate
```

### 3. Configure AWS Environment
```bash
# Set AWS region (recommended: us-east-1 for Bedrock)
export AWS_DEFAULT_REGION=us-east-1

# Verify AWS credentials
aws sts get-caller-identity

# Bootstrap CDK (if not done before)
cd infrastructure
npx cdk bootstrap
```

### 4. Deploy Infrastructure (Sequential Order)

#### Phase 1: Core Infrastructure
```bash
cd infrastructure

# Deploy AgentCore infrastructure
npx cdk deploy InfrastructureStack/AgentCoreInfrastructure --require-approval never

# Deploy MCP Lambda functions
npx cdk deploy InfrastructureStack/MCPDeployment --require-approval never

# Deploy AgentCore Gateway
npx cdk deploy InfrastructureStack/AgentCoreGateway --require-approval never
```

#### Phase 2: Authentication & Backend
```bash
# Deploy authentication
npx cdk deploy InfrastructureStack/Authentication --require-approval never

# Deploy Bedrock Agent
npx cdk deploy InfrastructureStack/BedrockAgent --require-approval never

# Deploy dashboard backend
npx cdk deploy InfrastructureStack/DashboardBackend --require-approval never
```

#### Phase 3: Frontend
```bash
# Build frontend
cd ../dashboard/frontend
npm run build
cd ../../infrastructure

# Deploy frontend
npx cdk deploy InfrastructureStack/FrontendDeployment --require-approval never
```

### 5. Post-Deployment Configuration

#### Create Test User
```bash
# Get User Pool ID from stack outputs
USER_POOL_ID=$(aws cloudformation describe-stacks \
  --stack-name InfrastructureStackAuthentication56C4EC5D \
  --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
  --output text)

# Create test executive user
aws cognito-idp admin-create-user \
  --user-pool-id $USER_POOL_ID \
  --username testexec@company.com \
  --user-attributes Name=email,Value=testexec@company.com \
  --temporary-password TempPass123! \
  --message-action SUPPRESS

# Set permanent password
aws cognito-idp admin-set-user-password \
  --user-pool-id $USER_POOL_ID \
  --username testexec@company.com \
  --password ExecutiveTest123! \
  --permanent
```

---

## 📜 Deployment Scripts

### Complete Deployment Script
```bash
#!/bin/bash
# deploy.sh - Complete deployment script

set -e

echo "🚀 Starting Executive Security ROI Analytics Deployment..."

# Check prerequisites
echo "📋 Checking prerequisites..."
command -v aws >/dev/null 2>&1 || { echo "AWS CLI required"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Node.js required"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Python 3 required"; exit 1; }

# Install dependencies
echo "📦 Installing dependencies..."
npm install
cd dashboard/frontend && npm install && cd ../..

# Setup Python environments
echo "🐍 Setting up Python environments..."
for mcp in security-mcp cost-mcp roi-analytics-mcp; do
  python3 -m venv mcp-servers/$mcp/venv
  source mcp-servers/$mcp/venv/bin/activate
  pip install -r mcp-servers/$mcp/requirements.txt
  deactivate
done

# Deploy infrastructure
echo "🏗️ Deploying infrastructure..."
cd infrastructure

# Phase 1: Core
npx cdk deploy InfrastructureStack/AgentCoreInfrastructure --require-approval never
npx cdk deploy InfrastructureStack/MCPDeployment --require-approval never
npx cdk deploy InfrastructureStack/AgentCoreGateway --require-approval never

# Phase 2: Auth & Backend
npx cdk deploy InfrastructureStack/Authentication --require-approval never
npx cdk deploy InfrastructureStack/BedrockAgent --require-approval never
npx cdk deploy InfrastructureStack/DashboardBackend --require-approval never

# Phase 3: Frontend
cd ../dashboard/frontend
npm run build
cd ../../infrastructure
npx cdk deploy InfrastructureStack/FrontendDeployment --require-approval never

echo "✅ Deployment completed successfully!"
echo "🌐 Dashboard URL: $(aws cloudformation describe-stacks --stack-name InfrastructureStackFrontendDeployment5F17D99F --query 'Stacks[0].Outputs[?OutputKey==`FrontendUrl`].OutputValue' --output text)"
```

### Cleanup Script
```bash
#!/bin/bash
# cleanup.sh - Remove all resources

set -e

echo "🗑️ Cleaning up Executive Security ROI Analytics..."

cd infrastructure

# Destroy in reverse order
npx cdk destroy InfrastructureStack/FrontendDeployment --force
npx cdk destroy InfrastructureStack/DashboardBackend --force
npx cdk destroy InfrastructureStack/BedrockAgent --force
npx cdk destroy InfrastructureStack/Authentication --force
npx cdk destroy InfrastructureStack/AgentCoreGateway --force
npx cdk destroy InfrastructureStack/MCPDeployment --force
npx cdk destroy InfrastructureStack/AgentCoreInfrastructure --force

echo "✅ Cleanup completed!"
```

### Quick Test Script
```bash
#!/bin/bash
# test.sh - Test deployment

echo "🧪 Testing deployment..."

# Get URLs
FRONTEND_URL=$(aws cloudformation describe-stacks \
  --stack-name InfrastructureStackFrontendDeployment5F17D99F \
  --query 'Stacks[0].Outputs[?OutputKey==`FrontendUrl`].OutputValue' \
  --output text)

BACKEND_URL=$(aws cloudformation describe-stacks \
  --stack-name InfrastructureStackDashboardBackendD3B930A3 \
  --query 'Stacks[0].Outputs[?OutputKey==`DashboardAPIUrl`].OutputValue' \
  --output text)

GATEWAY_URL=$(aws cloudformation describe-stacks \
  --stack-name InfrastructureStackAgentCoreGatewayC771425B \
  --query 'Stacks[0].Outputs[?OutputKey==`GatewayUrl`].OutputValue' \
  --output text)

# Test endpoints
echo "🌐 Frontend: $FRONTEND_URL"
echo "🔧 Backend: $BACKEND_URL"
echo "🚪 Gateway: $GATEWAY_URL"

# Test health endpoints
echo "Testing backend health..."
curl -s "$BACKEND_URL/health" | jq .

echo "Testing gateway health..."
curl -s "$GATEWAY_URL/health" | jq .

echo "✅ All endpoints responding!"
```

---

## 🔧 Configuration Options

### Environment Variables
```bash
# Optional customizations
export AWS_DEFAULT_REGION=us-east-1
export CDK_DEFAULT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
export PROJECT_NAME=executive-security-roi-analytics
```

### Custom User Pool Configuration
```typescript
// In infrastructure/lib/auth-stack.ts
const userPool = new cognito.UserPool(this, 'ExecutiveUserPool', {
  userPoolName: 'executive-security-analytics',
  passwordPolicy: {
    minLength: 12,
    requireLowercase: true,
    requireUppercase: true,
    requireDigits: true,
    requireSymbols: true,
  },
  // Customize as needed
});
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. CDK Bootstrap Required
```bash
Error: Need to perform AWS CDK bootstrap
Solution: npx cdk bootstrap
```

#### 2. Insufficient Permissions
```bash
Error: AccessDenied
Solution: Ensure AWS credentials have required permissions
```

#### 3. Bedrock Model Access
```bash
Error: Model access denied
Solution: Enable Bedrock model access in AWS Console
```

#### 4. Region Limitations
```bash
Error: Service not available in region
Solution: Use us-east-1 for full Bedrock support
```

### Verification Commands
```bash
# Check stack status
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE

# Check Lambda functions
aws lambda list-functions --query 'Functions[?contains(FunctionName, `security-roi-analytics`)].FunctionName'

# Check Bedrock agents
aws bedrock-agent list-agents

# Check API Gateway
aws apigateway get-rest-apis --query 'items[?contains(name, `AgentCore`)].{Name:name,Id:id}'
```

---

## 📊 Post-Deployment Validation

### 1. Access Dashboard
- Navigate to CloudFront URL
- Login with: `testexec@company.com` / `ExecutiveTest123!`
- Verify metrics display correctly

### 2. Test Chatbot
- Ask: "What's my security ROI?"
- Ask: "Show security costs for last month"
- Ask: "Check GuardDuty status in us-east-1"

### 3. Verify MCP Integration
- Check CloudWatch logs for MCP functions
- Test individual MCP endpoints via Gateway URL
- Verify Bedrock Agent responses

---

## 🔄 Updates & Maintenance

### Update Deployment
```bash
# Pull latest changes
git pull origin master

# Rebuild and redeploy
cd dashboard/frontend && npm run build && cd ../../infrastructure
npx cdk deploy --all --require-approval never
```

### Monitor Resources
```bash
# Check costs
aws ce get-cost-and-usage --time-period Start=2025-10-01,End=2025-10-31 --granularity MONTHLY --metrics BlendedCost

# Check logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/security-roi-analytics"
```

---

## 📞 Support

### Useful Resources
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [Bedrock Agent Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [Project Repository](https://github.com/ajitnk-lab/executive-security-roi-analytics)
- [Chatbot Prompts Guide](./CHATBOT_PROMPTS_GUIDE.md)

### Getting Help
1. Check CloudWatch logs for errors
2. Verify AWS permissions and quotas
3. Review CDK deployment outputs
4. Test individual components separately

---

## ✅ Success Criteria

Deployment is successful when:
- ✅ All CDK stacks deploy without errors
- ✅ Dashboard loads and shows metrics
- ✅ Authentication works with test user
- ✅ Chatbot responds to queries
- ✅ MCP tools return real AWS data
- ✅ No errors in CloudWatch logs

**Estimated Deployment Time**: 15-20 minutes
**Estimated Cost**: $5-15/month (depending on usage)
