import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { AgentCoreStack } from './agentcore-stack';
import { MCPDeploymentStack } from './mcp-deployment-stack';

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

    // Add dependency
    mcpDeploymentStack.addDependency(agentCoreStack);
  }
}
