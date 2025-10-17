import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import { Construct } from 'constructs';

export interface AgentCoreGatewayStackProps extends cdk.StackProps {
  securityMCPFunction: lambda.Function;
  costMCPFunction: lambda.Function;
  roiAnalyticsMCPFunction: lambda.Function;
  agentCoreRole: iam.Role;
}

export class AgentCoreGatewayStack extends cdk.Stack {
  public readonly gateway: apigateway.RestApi;
  public readonly gatewayUrl: string;

  constructor(scope: Construct, id: string, props: AgentCoreGatewayStackProps) {
    super(scope, id, props);

    // Create API Gateway for AgentCore Gateway
    this.gateway = new apigateway.RestApi(this, 'AgentCoreGateway', {
      restApiName: 'security-roi-analytics-gateway',
      description: 'AgentCore Gateway for Security ROI Analytics MCP servers',
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: ['Content-Type', 'X-Amz-Date', 'Authorization', 'X-Api-Key'],
      },
      deployOptions: {
        stageName: 'prod',
        throttlingRateLimit: 100,
        throttlingBurstLimit: 200,
      },
    });

    // Create Lambda integrations
    const securityIntegration = new apigateway.LambdaIntegration(props.securityMCPFunction, {
      requestTemplates: { 'application/json': '{ "statusCode": "200" }' },
    });

    const costIntegration = new apigateway.LambdaIntegration(props.costMCPFunction, {
      requestTemplates: { 'application/json': '{ "statusCode": "200" }' },
    });

    const roiIntegration = new apigateway.LambdaIntegration(props.roiAnalyticsMCPFunction, {
      requestTemplates: { 'application/json': '{ "statusCode": "200" }' },
    });

    // Create API Gateway resources and methods
    const securityResource = this.gateway.root.addResource('security');
    securityResource.addMethod('POST', securityIntegration, {
      apiKeyRequired: false,
      authorizationType: apigateway.AuthorizationType.IAM,
    });

    const costResource = this.gateway.root.addResource('cost');
    costResource.addMethod('POST', costIntegration, {
      apiKeyRequired: false,
      authorizationType: apigateway.AuthorizationType.IAM,
    });

    const roiResource = this.gateway.root.addResource('roi');
    roiResource.addMethod('POST', roiIntegration, {
      apiKeyRequired: false,
      authorizationType: apigateway.AuthorizationType.IAM,
    });

    // Health check endpoint
    const healthResource = this.gateway.root.addResource('health');
    healthResource.addMethod('GET', new apigateway.MockIntegration({
      integrationResponses: [{
        statusCode: '200',
        responseTemplates: {
          'application/json': '{"status": "healthy", "timestamp": "$context.requestTime"}'
        },
      }],
      requestTemplates: {
        'application/json': '{"statusCode": 200}'
      },
    }), {
      methodResponses: [{
        statusCode: '200',
        responseModels: {
          'application/json': apigateway.Model.EMPTY_MODEL,
        },
      }],
    });

    // Grant API Gateway permission to invoke Lambda functions
    props.securityMCPFunction.grantInvoke(new iam.ServicePrincipal('apigateway.amazonaws.com'));
    props.costMCPFunction.grantInvoke(new iam.ServicePrincipal('apigateway.amazonaws.com'));
    props.roiAnalyticsMCPFunction.grantInvoke(new iam.ServicePrincipal('apigateway.amazonaws.com'));

    this.gatewayUrl = this.gateway.url;

    // Outputs
    new cdk.CfnOutput(this, 'GatewayUrl', {
      value: this.gatewayUrl,
      description: 'AgentCore Gateway API URL',
      exportName: 'AgentCoreGatewayUrl',
    });

    new cdk.CfnOutput(this, 'GatewayId', {
      value: this.gateway.restApiId,
      description: 'AgentCore Gateway API ID',
      exportName: 'AgentCoreGatewayId',
    });

    new cdk.CfnOutput(this, 'SecurityEndpoint', {
      value: `${this.gatewayUrl}security`,
      description: 'Security MCP endpoint URL',
    });

    new cdk.CfnOutput(this, 'CostEndpoint', {
      value: `${this.gatewayUrl}cost`,
      description: 'Cost MCP endpoint URL',
    });

    new cdk.CfnOutput(this, 'ROIEndpoint', {
      value: `${this.gatewayUrl}roi`,
      description: 'ROI Analytics MCP endpoint URL',
    });
  }
}
