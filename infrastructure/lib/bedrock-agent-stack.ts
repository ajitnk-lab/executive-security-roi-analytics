import * as cdk from 'aws-cdk-lib';
import * as bedrock from 'aws-cdk-lib/aws-bedrock';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import { Construct } from 'constructs';

export interface BedrockAgentStackProps extends cdk.StackProps {
  agentCoreRole: iam.Role;
  gateway: apigateway.RestApi;
}

export class BedrockAgentStack extends cdk.Stack {
  public readonly agent: bedrock.CfnAgent;
  public readonly agentAlias: bedrock.CfnAgentAlias;
  public readonly orchestratorFunction: lambda.Function;

  constructor(scope: Construct, id: string, props: BedrockAgentStackProps) {
    super(scope, id, props);

    // Create orchestrator Lambda function
    this.orchestratorFunction = new lambda.Function(this, 'OrchestratorFunction', {
      functionName: 'security-roi-orchestrator',
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'agent.lambda_handler',
      code: lambda.Code.fromAsset('../agents/orchestrator'),
      timeout: cdk.Duration.minutes(5),
      memorySize: 512,
      environment: {
        GATEWAY_URL: props.gateway.url,
        LOG_LEVEL: 'INFO',
      },
      role: props.agentCoreRole,
    });

    // Create Bedrock Agent
    this.agent = new bedrock.CfnAgent(this, 'SecurityROIAgent', {
      agentName: 'security-roi-analytics-agent',
      description: 'AI agent for security ROI analytics and executive decision making',
      foundationModel: 'anthropic.claude-3-sonnet-20240229-v1:0',
      instruction: `You are a Security ROI Analytics Assistant for executives. Your role is to help analyze security investments, costs, and return on investment using AWS security services.

CAPABILITIES:
1. Security Assessment: Monitor AWS security services, retrieve findings, check compliance
2. Cost Analysis: Track security service costs, analyze trends, get breakdowns, forecast costs  
3. ROI Analytics: Calculate ROI, analyze cost-benefit ratios, generate reports, optimize spending

RESPONSE STYLE:
- Provide executive-level insights with clear business impact
- Include specific metrics, percentages, and dollar amounts
- Offer actionable recommendations for optimization
- Focus on business value and risk reduction`,
      agentResourceRoleArn: props.agentCoreRole.roleArn,
      idleSessionTtlInSeconds: 1800,
    });

    // Create Agent Alias
    this.agentAlias = new bedrock.CfnAgentAlias(this, 'SecurityROIAgentAlias', {
      agentId: this.agent.attrAgentId,
      agentAliasName: 'PROD',
      description: 'Production alias for Security ROI Analytics Agent',
    });

    // Add Bedrock permissions to the role
    props.agentCoreRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'bedrock:InvokeModel',
        'bedrock:InvokeModelWithResponseStream',
        'bedrock:GetFoundationModel',
        'bedrock:ListFoundationModels',
        'bedrock:InvokeAgent',
      ],
      resources: ['*'],
    }));

    // Outputs
    new cdk.CfnOutput(this, 'AgentId', {
      value: this.agent.attrAgentId,
      description: 'Bedrock Agent ID',
      exportName: 'SecurityROIAgentId',
    });

    new cdk.CfnOutput(this, 'AgentAliasId', {
      value: this.agentAlias.attrAgentAliasId,
      description: 'Bedrock Agent Alias ID',
      exportName: 'SecurityROIAgentAliasId',
    });

    new cdk.CfnOutput(this, 'OrchestratorFunctionArn', {
      value: this.orchestratorFunction.functionArn,
      description: 'Orchestrator Lambda Function ARN',
    });
  }
}
