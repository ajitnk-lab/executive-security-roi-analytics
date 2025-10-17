import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';

export interface MCPDeploymentStackProps extends cdk.StackProps {
  agentCoreRole: iam.Role;
  logGroup: logs.LogGroup;
}

export class MCPDeploymentStack extends cdk.Stack {
  public readonly securityMCPFunction: lambda.Function;
  public readonly costMCPFunction: lambda.Function;
  public readonly roiAnalyticsMCPFunction: lambda.Function;

  constructor(scope: Construct, id: string, props: MCPDeploymentStackProps) {
    super(scope, id, props);

    // Security MCP Lambda Function
    this.securityMCPFunction = new lambda.Function(this, 'SecurityMCPFunction', {
      functionName: 'security-roi-analytics-security-mcp',
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'lambda_handler.lambda_handler',
      code: lambda.Code.fromAsset('../mcp-servers/security-mcp', {
        bundling: {
          image: lambda.Runtime.PYTHON_3_10.bundlingImage,
          command: [
            'bash', '-c',
            'pip install -r requirements.txt -t /asset-output && cp -au . /asset-output'
          ],
        },
      }),
      timeout: cdk.Duration.minutes(5),
      memorySize: 512,
      environment: {
        LOG_LEVEL: 'INFO',
        POWERTOOLS_SERVICE_NAME: 'security-mcp',
      },
      logGroup: props.logGroup,
      role: props.agentCoreRole,
    });

    // Cost MCP Lambda Function
    this.costMCPFunction = new lambda.Function(this, 'CostMCPFunction', {
      functionName: 'security-roi-analytics-cost-mcp',
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'lambda_handler.lambda_handler',
      code: lambda.Code.fromAsset('../mcp-servers/cost-mcp', {
        bundling: {
          image: lambda.Runtime.PYTHON_3_10.bundlingImage,
          command: [
            'bash', '-c',
            'pip install -r requirements.txt -t /asset-output && cp -au . /asset-output'
          ],
        },
      }),
      timeout: cdk.Duration.minutes(5),
      memorySize: 512,
      environment: {
        LOG_LEVEL: 'INFO',
        POWERTOOLS_SERVICE_NAME: 'cost-mcp',
      },
      logGroup: props.logGroup,
      role: props.agentCoreRole,
    });

    // ROI Analytics MCP Lambda Function
    this.roiAnalyticsMCPFunction = new lambda.Function(this, 'ROIAnalyticsMCPFunction', {
      functionName: 'security-roi-analytics-roi-mcp',
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'lambda_handler.lambda_handler',
      code: lambda.Code.fromAsset('../mcp-servers/roi-analytics-mcp', {
        bundling: {
          image: lambda.Runtime.PYTHON_3_10.bundlingImage,
          command: [
            'bash', '-c',
            'pip install -r requirements.txt -t /asset-output && cp -au . /asset-output'
          ],
        },
      }),
      timeout: cdk.Duration.minutes(5),
      memorySize: 1024, // More memory for pandas/numpy operations
      environment: {
        LOG_LEVEL: 'INFO',
        POWERTOOLS_SERVICE_NAME: 'roi-analytics-mcp',
      },
      logGroup: props.logGroup,
      role: props.agentCoreRole,
    });

    // Outputs
    new cdk.CfnOutput(this, 'SecurityMCPFunctionArn', {
      value: this.securityMCPFunction.functionArn,
      description: 'ARN of the Security MCP Lambda Function',
      exportName: 'SecurityMCPFunctionArn',
    });

    new cdk.CfnOutput(this, 'CostMCPFunctionArn', {
      value: this.costMCPFunction.functionArn,
      description: 'ARN of the Cost MCP Lambda Function',
      exportName: 'CostMCPFunctionArn',
    });

    new cdk.CfnOutput(this, 'ROIAnalyticsMCPFunctionArn', {
      value: this.roiAnalyticsMCPFunction.functionArn,
      description: 'ARN of the ROI Analytics MCP Lambda Function',
      exportName: 'ROIAnalyticsMCPFunctionArn',
    });
  }
}
