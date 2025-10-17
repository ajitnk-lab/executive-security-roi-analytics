# Executive Security ROI Analytics Solution

A comprehensive AI-powered solution for executives to analyze security investments, costs, and ROI using AWS services and AgentCore runtime.

## Architecture Overview

```
Executive Dashboard (React + Embedded Chatbot)
                    ↓
            Bedrock Agent (Orchestrator)
                    ↓
            AgentCore Gateway
        ↓           ↓           ↓
Security MCP    Cost MCP    ROI MCP
(AgentCore)    (AgentCore)  (AgentCore)
```

## Project Structure

```
├── docs/                          # Documentation
│   ├── architecture/              # Architecture diagrams
│   ├── api/                      # API documentation
│   └── deployment/               # Deployment guides
├── infrastructure/               # CDK Infrastructure as Code
│   ├── stacks/                  # CDK Stack definitions
│   └── constructs/              # Custom CDK constructs
├── mcp-servers/                 # MCP Server implementations
│   ├── security-mcp/           # Security assessment MCP server
│   ├── cost-mcp/               # Cost analysis MCP server
│   └── roi-analytics-mcp/      # ROI analytics MCP server
├── adapters/                    # Protocol adapters
│   └── mcp-adapter/            # Bedrock Agent to MCP Gateway adapter
├── dashboard/                   # Executive Dashboard
│   ├── frontend/               # React frontend
│   └── backend/                # API Gateway + Lambda
├── tests/                       # Test suites
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── e2e/                    # End-to-end tests
└── scripts/                     # Deployment and utility scripts
```

## Quick Start

1. **Prerequisites**: See [docs/deployment/prerequisites.md](docs/deployment/prerequisites.md)
2. **Setup**: Run `./scripts/setup.sh`
3. **Deploy**: Run `./scripts/deploy.sh`
4. **Access**: Dashboard URL will be provided after deployment

## Documentation

- [Requirements](requirements.md) - Detailed requirements and specifications
- [Design Decisions](design.md) - Architecture and design decisions
- [Tasks](tasks.md) - Implementation roadmap and progress
- [API Documentation](docs/api/) - Complete API reference
- [Deployment Guide](docs/deployment/) - Step-by-step deployment instructions

## Key Features

- **Real-time Security ROI Analysis**: Calculate and track security investment returns
- **Multi-Service Cost Tracking**: Monitor costs across GuardDuty, Security Hub, Inspector, etc.
- **Executive Dashboard**: Clean interface with embedded AI chatbot
- **Intelligent Orchestration**: Bedrock Agent routes queries to appropriate MCP servers
- **Scalable Architecture**: AgentCore runtime with gateway-based tool routing

## Technology Stack

- **Frontend**: React, TypeScript, Tailwind CSS
- **Backend**: AWS Lambda, API Gateway, DynamoDB
- **AI/ML**: Amazon Bedrock, AgentCore Runtime, MCP Protocol
- **Infrastructure**: AWS CDK, CloudFormation
- **Monitoring**: CloudWatch, X-Ray, AWS Config

## License

MIT License - see [LICENSE](LICENSE) file for details.
