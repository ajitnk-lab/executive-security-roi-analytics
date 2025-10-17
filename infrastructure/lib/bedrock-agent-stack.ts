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

    // Create IAM role for Bedrock Agent
    const bedrockAgentRole = new iam.Role(this, 'BedrockAgentRole', {
      assumedBy: new iam.ServicePrincipal('bedrock.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonBedrockFullAccess')
      ]
    });

    // Create MCP Proxy Lambda function for direct tool calls
    const mcpProxyFunction = new lambda.Function(this, 'MCPProxyFunction', {
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'mcp_proxy.lambda_handler',
      code: lambda.Code.fromAsset('../adapters/mcp-adapter'),
      timeout: cdk.Duration.seconds(30),
      environment: {
        GATEWAY_URL: `https://${props.gateway.restApiId}.execute-api.${this.region}.amazonaws.com/prod`
      },
      role: props.agentCoreRole
    });

    // Detailed agent instructions with tool-specific guidance
    const agentInstructions = `You are an Executive Security ROI Analytics Assistant with direct access to security analysis tools.

CRITICAL: You have access to security analysis tools through the AgentCore Gateway. When users ask about security, you MUST call the appropriate tool with correct parameters.

## Available Security Tools:

### check_security_services
**Purpose**: Check status of AWS security services
**Required Parameters**: None (uses defaults)
**Optional Parameters**:
- regions: Array of AWS regions (default: ["us-east-1"])  
- services: Array of services (default: ["guardduty", "securityhub", "inspector"])

**When to use**: User asks about security status, security score, security rating, enabled services
**Examples**:
- "What's my security score?" → Call check_security_services()
- "Security status in us-west-2?" → Call check_security_services with regions=["us-west-2"]

### get_security_findings  
**Purpose**: Get security findings and vulnerabilities
**Required Parameters**: None (uses defaults)
**Optional Parameters**:
- severity: "HIGH", "CRITICAL", "MEDIUM", "LOW" (default: "HIGH")
- regions: Array of regions (default: ["us-east-1"])
- limit: Number of findings (default: 50)

**When to use**: User asks about vulnerabilities, findings, security issues
**Examples**:
- "What vulnerabilities do I have?" → Call get_security_findings()
- "Critical security issues?" → Call get_security_findings with severity="CRITICAL"

### check_compliance
**Purpose**: Check compliance status
**Required Parameters**: None (uses defaults)  
**Optional Parameters**:
- frameworks: Array like ["SOC2", "PCI-DSS", "HIPAA"] (default: ["AWS-Foundational"])
- regions: Array of regions (default: ["us-east-1"])

**When to use**: User asks about compliance, standards, regulations
**Examples**:
- "Am I compliant?" → Call check_compliance()
- "PCI compliance status?" → Call check_compliance with frameworks=["PCI-DSS"]

## Response Rules:
1. **For simple questions**: Call the tool and return the key result (e.g., "85/100" for security score)
2. **For complex questions**: Call the tool and provide detailed analysis
3. **Always call tools**: Never give generic responses without calling tools first
4. **Ask for parameters**: If you need specific parameters, ask the user

## Examples:
User: "What is security rating"
Response: Call check_security_services() → Return calculated score like "100/100"

User: "Security status for production"  
Response: "I'll check your security status. Which regions should I check for production? (e.g., us-east-1, us-west-2)"`;

    // Create Security Action Group with detailed API schema
    const securityActionGroupSchema = {
      "openapi": "3.0.0",
      "info": {
        "title": "Security Analytics API",
        "version": "1.0.0",
        "description": "Direct access to AWS security analysis tools"
      },
      "paths": {
        "/security/check_security_services": {
          "post": {
            "summary": "Check AWS security services status",
            "description": "Check the status of AWS security services like GuardDuty, Security Hub, and Inspector across regions",
            "operationId": "checkSecurityServices",
            "requestBody": {
              "required": false,
              "content": {
                "application/json": {
                  "schema": {
                    "type": "object",
                    "properties": {
                      "regions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "AWS regions to check (default: us-east-1)",
                        "example": ["us-east-1", "us-west-2"]
                      },
                      "services": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Services to check: guardduty, securityhub, inspector",
                        "example": ["guardduty", "securityhub", "inspector"]
                      }
                    }
                  }
                }
              }
            },
            "responses": {
              "200": {
                "description": "Security services status",
                "content": {
                  "application/json": {
                    "schema": {
                      "type": "object",
                      "properties": {
                        "status": {"type": "string"},
                        "services": {"type": "object"},
                        "security_score": {"type": "string"}
                      }
                    }
                  }
                }
              }
            }
          }
        },
        "/security/get_security_findings": {
          "post": {
            "summary": "Get security findings and vulnerabilities",
            "description": "Retrieve security findings from AWS security services",
            "operationId": "getSecurityFindings",
            "requestBody": {
              "required": false,
              "content": {
                "application/json": {
                  "schema": {
                    "type": "object",
                    "properties": {
                      "severity": {
                        "type": "string",
                        "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                        "description": "Severity level of findings (default: HIGH)",
                        "example": "HIGH"
                      },
                      "regions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "AWS regions to check (default: us-east-1)",
                        "example": ["us-east-1"]
                      },
                      "limit": {
                        "type": "integer",
                        "description": "Maximum number of findings to return (default: 50)",
                        "example": 50
                      }
                    }
                  }
                }
              }
            },
            "responses": {
              "200": {
                "description": "Security findings",
                "content": {
                  "application/json": {
                    "schema": {
                      "type": "object",
                      "properties": {
                        "findings": {"type": "array"},
                        "summary": {"type": "object"}
                      }
                    }
                  }
                }
              }
            }
          }
        },
        "/security/check_compliance": {
          "post": {
            "summary": "Check compliance status",
            "description": "Check compliance against security frameworks and standards",
            "operationId": "checkCompliance",
            "requestBody": {
              "required": false,
              "content": {
                "application/json": {
                  "schema": {
                    "type": "object",
                    "properties": {
                      "frameworks": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Compliance frameworks to check",
                        "example": ["AWS-Foundational", "SOC2", "PCI-DSS"]
                      },
                      "regions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "AWS regions to check (default: us-east-1)",
                        "example": ["us-east-1"]
                      }
                    }
                  }
                }
              }
            },
            "responses": {
              "200": {
                "description": "Compliance status",
                "content": {
                  "application/json": {
                    "schema": {
                      "type": "object",
                      "properties": {
                        "compliance_status": {"type": "object"},
                        "recommendations": {"type": "array"}
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    };

    // Create Cost Action Group Schema
    const costActionGroupSchema = {
      "openapi": "3.0.0",
      "info": {
        "title": "Cost Analytics API",
        "version": "1.0.0",
        "description": "AWS security services cost analysis tools"
      },
      "paths": {
        "/cost/get_security_service_costs": {
          "post": {
            "summary": "Get security service costs",
            "description": "Get costs for AWS security services",
            "operationId": "getSecurityServiceCosts",
            "requestBody": {
              "required": false,
              "content": {
                "application/json": {
                  "schema": {
                    "type": "object",
                    "properties": {
                      "services": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Security services to analyze"
                      },
                      "time_period": {
                        "type": "string",
                        "description": "Time period for cost analysis"
                      }
                    }
                  }
                }
              }
            },
            "responses": {
              "200": {
                "description": "Security service costs",
                "content": {
                  "application/json": {
                    "schema": {
                      "type": "object",
                      "properties": {
                        "costs": {"type": "object"},
                        "total": {"type": "number"}
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    };

    // Create ROI Action Group Schema
    const roiActionGroupSchema = {
      "openapi": "3.0.0",
      "info": {
        "title": "ROI Analytics API",
        "version": "1.0.0",
        "description": "Security ROI calculation and analysis tools"
      },
      "paths": {
        "/roi/calculate_security_roi": {
          "post": {
            "summary": "Calculate security ROI",
            "description": "Calculate return on investment for security services",
            "operationId": "calculateSecurityROI",
            "requestBody": {
              "required": false,
              "content": {
                "application/json": {
                  "schema": {
                    "type": "object",
                    "properties": {
                      "time_period": {
                        "type": "string",
                        "description": "Time period for ROI analysis"
                      }
                    }
                  }
                }
              }
            },
            "responses": {
              "200": {
                "description": "Security ROI analysis",
                "content": {
                  "application/json": {
                    "schema": {
                      "type": "object",
                      "properties": {
                        "roi_percentage": {"type": "number"},
                        "analysis": {"type": "object"}
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    };

    // Create new Bedrock Agent with working security tools only
    this.agent = new bedrock.CfnAgent(this, 'SecurityROIAgentV3', {
      agentName: 'executive-security-roi-agent-v3',
      description: 'Executive Security ROI Analytics Agent with working security tools',
      foundationModel: 'anthropic.claude-3-haiku-20240307-v1:0',
      instruction: agentInstructions,
      agentResourceRoleArn: bedrockAgentRole.roleArn,
      actionGroups: [
        {
          actionGroupName: 'security-tools',
          description: 'Direct access to security analysis tools',
          actionGroupExecutor: {
            lambda: mcpProxyFunction.functionArn
          },
          apiSchema: {
            payload: JSON.stringify(securityActionGroupSchema)
          }
        }
      ]
    });

    // Grant Lambda invoke permissions to Bedrock Agent
    mcpProxyFunction.addPermission('BedrockAgentInvoke', {
      principal: new iam.ServicePrincipal('bedrock.amazonaws.com'),
      action: 'lambda:InvokeFunction',
      sourceArn: this.agent.attrAgentArn
    });

    // Outputs
    new cdk.CfnOutput(this, 'AgentId', {
      value: this.agent.attrAgentId,
      description: 'Bedrock Agent ID'
    });
  }
}
