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

  constructor(scope: Construct, id: string, props: BedrockAgentStackProps) {
    super(scope, id, props);

    // Create Lambda function for orchestrator
    const orchestratorFunction = new lambda.Function(this, 'OrchestratorFunction', {
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'agent.lambda_handler',
      code: lambda.Code.fromAsset('../agents/orchestrator'),
      timeout: cdk.Duration.minutes(5),
      environment: {
        GATEWAY_URL: `https://${props.gateway.restApiId}.execute-api.${this.region}.amazonaws.com/prod`
      },
      role: props.agentCoreRole
    });

    // Create Bedrock Agent
    this.agent = new bedrock.CfnAgent(this, 'SecurityROIAgent', {
      agentName: 'executive-security-roi-agent',
      description: 'Executive Security ROI Analytics Agent for C-level decision making',
      foundationModel: 'anthropic.claude-3-sonnet-20240229-v1:0',
      agentResourceRoleArn: props.agentCoreRole.roleArn,
      instruction: `You are an Executive Security ROI Analytics Assistant. Analyze AWS security investments, costs, and returns for C-level executives. Provide clear, actionable insights focused on business value and strategic decision-making.`,
      actionGroups: [
        {
          actionGroupName: 'security-analytics',
          description: 'Security, cost, and ROI analytics tools',
          actionGroupExecutor: {
            lambda: orchestratorFunction.functionArn
          },
          apiSchema: {
            payload: JSON.stringify({
              openapi: '3.0.0',
              info: {
                title: 'Security Analytics API',
                version: '1.0.0'
              },
              paths: {
                '/analyze': {
                  post: {
                    description: 'Analyze security ROI query',
                    requestBody: {
                      content: {
                        'application/json': {
                          schema: {
                            type: 'object',
                            properties: {
                              query: { type: 'string' },
                              context: { type: 'object' }
                            }
                          }
                        }
                      }
                    },
                    responses: {
                      '200': {
                        description: 'Analysis results'
                      }
                    }
                  }
                }
              }
            })
          }
        }
      ]
    });

    // Grant Lambda invoke permissions to Bedrock Agent
    orchestratorFunction.addPermission('BedrockAgentInvoke', {
      principal: new iam.ServicePrincipal('bedrock.amazonaws.com'),
      action: 'lambda:InvokeFunction',
      sourceArn: this.agent.attrAgentArn
    });

    // Create Agent Alias
    this.agentAlias = new bedrock.CfnAgentAlias(this, 'SecurityROIAgentAlias', {
      agentId: this.agent.attrAgentId,
      agentAliasName: 'PROD',
      description: 'Production alias for Executive Security ROI Agent'
    });

    // Outputs
    new cdk.CfnOutput(this, 'AgentId', {
      value: this.agent.attrAgentId,
      description: 'Bedrock Agent ID'
    });

    new cdk.CfnOutput(this, 'AgentAliasId', {
      value: this.agentAlias.attrAgentAliasId,
      description: 'Bedrock Agent Alias ID'
    });
  }
}
