import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

export interface DashboardBackendStackProps extends cdk.StackProps {
  agentCoreRole: iam.Role;
}

export class DashboardBackendStack extends cdk.Stack {
  public readonly api: apigateway.RestApi;
  public readonly dashboardFunction: lambda.Function;

  constructor(scope: Construct, id: string, props: DashboardBackendStackProps) {
    super(scope, id, props);

    // Create Lambda function for dashboard backend
    this.dashboardFunction = new lambda.Function(this, 'DashboardFunction', {
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'handler.lambda_handler',
      code: lambda.Code.fromAsset('../dashboard/backend'),
      timeout: cdk.Duration.minutes(5),
      role: props.agentCoreRole,
      environment: {
        AGENT_ID: 'DTAX1II3AK',
        AGENT_ALIAS_ID: 'GCWHOE7WNP'
      }
    });

    // Create API Gateway
    this.api = new apigateway.RestApi(this, 'DashboardAPI', {
      restApiName: 'Executive Dashboard API',
      description: 'API for Executive Security ROI Dashboard',
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: ['Content-Type', 'X-Amz-Date', 'Authorization', 'X-Api-Key', 'X-Amz-Security-Token']
      }
    });

    // Create Lambda integration
    const lambdaIntegration = new apigateway.LambdaIntegration(this.dashboardFunction);

    // Add chat endpoint
    const chatResource = this.api.root.addResource('chat');
    chatResource.addMethod('POST', lambdaIntegration);

    // Add metrics endpoint
    const metricsResource = this.api.root.addResource('metrics');
    metricsResource.addMethod('GET', lambdaIntegration);

    // Outputs
    new cdk.CfnOutput(this, 'DashboardAPIUrl', {
      value: this.api.url,
      description: 'Dashboard API Gateway URL'
    });

    new cdk.CfnOutput(this, 'DashboardFunctionArn', {
      value: this.dashboardFunction.functionArn,
      description: 'Dashboard Lambda Function ARN'
    });
  }
}
