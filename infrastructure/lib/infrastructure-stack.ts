import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { AgentCoreStack } from './agentcore-stack';
import { MCPDeploymentStack } from './mcp-deployment-stack';
import { AgentCoreGatewayStack } from './agentcore-gateway-stack';
import { BedrockAgentStack } from './bedrock-agent-stack';
import { DashboardBackendStack } from './dashboard-backend-stack';
import { AuthStack } from './auth-stack';

export class InfrastructureStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // AgentCore Infrastructure Stack
    const agentCoreStack = new AgentCoreStack(this, 'AgentCoreInfrastructure', {
      description: 'AgentCore runtime infrastructure for Security ROI Analytics',
    });

    // MCP Deployment Stack
    const mcpDeploymentStack = new MCPDeploymentStack(this, 'MCPDeployment', {
      description: 'Lambda functions for MCP servers deployment',
      agentCoreRole: agentCoreStack.agentCoreRole,
      logGroup: agentCoreStack.logGroup,
    });

    // AgentCore Gateway Stack
    const gatewayStack = new AgentCoreGatewayStack(this, 'AgentCoreGateway', {
      description: 'API Gateway for AgentCore MCP tool routing',
      securityMCPFunction: mcpDeploymentStack.securityMCPFunction,
      costMCPFunction: mcpDeploymentStack.costMCPFunction,
      roiAnalyticsMCPFunction: mcpDeploymentStack.roiAnalyticsMCPFunction,
      agentCoreRole: agentCoreStack.agentCoreRole,
    });

    // Bedrock Agent Stack
    const bedrockAgentStack = new BedrockAgentStack(this, 'BedrockAgent', {
      description: 'Bedrock Agent orchestrator for Security ROI Analytics',
      agentCoreRole: agentCoreStack.agentCoreRole,
      gateway: gatewayStack.gateway,
    });

    // Dashboard Backend Stack (without auth initially)
    const dashboardBackendStack = new DashboardBackendStack(this, 'DashboardBackend', {
      description: 'Backend API for Executive Dashboard',
      agentCoreRole: agentCoreStack.agentCoreRole,
    });

    // Authentication Stack
    const authStack = new AuthStack(this, 'Authentication', {
      description: 'Authentication and authorization for Executive Dashboard',
    });

    // Add dependencies
    mcpDeploymentStack.addDependency(agentCoreStack);
    gatewayStack.addDependency(mcpDeploymentStack);
    bedrockAgentStack.addDependency(gatewayStack);
    dashboardBackendStack.addDependency(bedrockAgentStack);
    authStack.addDependency(dashboardBackendStack);
  }
}
