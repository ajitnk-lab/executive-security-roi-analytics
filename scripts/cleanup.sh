#!/bin/bash
# cleanup.sh - Remove all Executive Security ROI Analytics resources

set -e

echo "🗑️ Cleaning up Executive Security ROI Analytics..."
echo "⚠️  This will destroy ALL resources and cannot be undone!"
echo ""

# Confirmation prompt
read -p "Are you sure you want to proceed? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
  echo "❌ Cleanup cancelled"
  exit 0
fi

cd infrastructure

echo "🔥 Destroying stacks in reverse order..."

# Destroy in reverse order to handle dependencies
echo "  Destroying Frontend..."
npx cdk destroy InfrastructureStack/FrontendDeployment --force || echo "Stack may not exist"

echo "  Destroying Dashboard Backend..."
npx cdk destroy InfrastructureStack/DashboardBackend --force || echo "Stack may not exist"

echo "  Destroying Bedrock Agent..."
npx cdk destroy InfrastructureStack/BedrockAgent --force || echo "Stack may not exist"

echo "  Destroying Authentication..."
npx cdk destroy InfrastructureStack/Authentication --force || echo "Stack may not exist"

echo "  Destroying AgentCore Gateway..."
npx cdk destroy InfrastructureStack/AgentCoreGateway --force || echo "Stack may not exist"

echo "  Destroying MCP Deployment..."
npx cdk destroy InfrastructureStack/MCPDeployment --force || echo "Stack may not exist"

echo "  Destroying AgentCore Infrastructure..."
npx cdk destroy InfrastructureStack/AgentCoreInfrastructure --force || echo "Stack may not exist"

echo ""
echo "✅ Cleanup completed!"
echo "💡 Note: Some resources like S3 buckets may have retention policies"
echo "💡 Check AWS Console to verify all resources are removed"
