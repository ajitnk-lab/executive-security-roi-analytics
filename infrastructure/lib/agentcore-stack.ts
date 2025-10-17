import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

export class AgentCoreStack extends cdk.Stack {
  public readonly agentCoreRole: iam.Role;
  public readonly logGroup: logs.LogGroup;
  public readonly artifactsBucket: s3.Bucket;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // S3 bucket for AgentCore artifacts and logs
    this.artifactsBucket = new s3.Bucket(this, 'AgentCoreArtifacts', {
      bucketName: `agentcore-artifacts-${this.account}-${this.region}`,
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    // CloudWatch Log Group for AgentCore
    this.logGroup = new logs.LogGroup(this, 'AgentCoreLogGroup', {
      logGroupName: '/aws/agentcore/security-roi-analytics',
      retention: logs.RetentionDays.ONE_MONTH,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // IAM Role for AgentCore runtime
    this.agentCoreRole = new iam.Role(this, 'AgentCoreRole', {
      assumedBy: new iam.CompositePrincipal(
        new iam.ServicePrincipal('bedrock.amazonaws.com'),
        new iam.ServicePrincipal('lambda.amazonaws.com')
      ),
      description: 'Role for AgentCore runtime to access AWS services',
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
      ],
    });

    // Add permissions for security services
    this.agentCoreRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'guardduty:List*',
        'guardduty:Get*',
        'guardduty:Describe*',
        'securityhub:Get*',
        'securityhub:List*',
        'securityhub:Describe*',
        'inspector2:List*',
        'inspector2:Get*',
        'inspector2:Describe*',
        'inspector2:BatchGet*',
        'macie2:Get*',
        'macie2:List*',
        'macie2:Describe*',
        'access-analyzer:List*',
        'access-analyzer:Get*',
        'support:Describe*',
      ],
      resources: ['*'],
    }));

    // Add permissions for cost analysis
    this.agentCoreRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'ce:GetCostAndUsage',
        'ce:GetUsageReport',
        'ce:GetCostForecast',
        'ce:GetUsageForecast',
        'ce:ListCostCategoryDefinitions',
        'ce:GetRightsizingRecommendation',
        'ce:GetSavingsUtilization',
        'ce:GetReservationCoverage',
        'ce:GetReservationPurchaseRecommendation',
        'ce:GetReservationUtilization',
        'ce:GetDimensionValues',
        'ce:GetMetricValues',
      ],
      resources: ['*'],
    }));

    // Add permissions for S3, EBS, RDS compliance checks
    this.agentCoreRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        's3:GetBucketEncryption',
        's3:GetBucketVersioning',
        's3:GetBucketPublicAccessBlock',
        's3:ListAllMyBuckets',
        'ec2:DescribeVolumes',
        'ec2:DescribeSnapshots',
        'rds:DescribeDBInstances',
        'rds:DescribeDBClusters',
        'dynamodb:DescribeTable',
        'dynamodb:ListTables',
        'efs:DescribeFileSystems',
        'elasticache:DescribeCacheClusters',
        'elasticache:DescribeReplicationGroups',
      ],
      resources: ['*'],
    }));

    // Add permissions for CloudWatch Logs
    this.agentCoreRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'logs:CreateLogGroup',
        'logs:CreateLogStream',
        'logs:PutLogEvents',
        'logs:DescribeLogGroups',
        'logs:DescribeLogStreams',
      ],
      resources: [this.logGroup.logGroupArn, `${this.logGroup.logGroupArn}:*`],
    }));

    // Add permissions for S3 artifacts bucket
    this.agentCoreRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        's3:GetObject',
        's3:PutObject',
        's3:DeleteObject',
        's3:ListBucket',
      ],
      resources: [
        this.artifactsBucket.bucketArn,
        `${this.artifactsBucket.bucketArn}/*`,
      ],
    }));

    // Outputs
    new cdk.CfnOutput(this, 'AgentCoreRoleArn', {
      value: this.agentCoreRole.roleArn,
      description: 'ARN of the AgentCore IAM Role',
      exportName: 'AgentCoreRoleArn',
    });

    new cdk.CfnOutput(this, 'LogGroupName', {
      value: this.logGroup.logGroupName,
      description: 'CloudWatch Log Group for AgentCore',
      exportName: 'AgentCoreLogGroupName',
    });

    new cdk.CfnOutput(this, 'ArtifactsBucketName', {
      value: this.artifactsBucket.bucketName,
      description: 'S3 bucket for AgentCore artifacts',
      exportName: 'AgentCoreArtifactsBucket',
    });
  }
}
