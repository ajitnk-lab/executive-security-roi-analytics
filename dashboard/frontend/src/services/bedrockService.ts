import { BedrockAgentRuntimeClient, InvokeAgentCommand } from '@aws-sdk/client-bedrock-agent-runtime';

const AGENT_ID = 'DTAX1II3AK';
const AGENT_ALIAS_ID = 'GCWHOE7WNP';
const REGION = 'us-east-1';

class BedrockService {
  private client: BedrockAgentRuntimeClient;

  constructor() {
    this.client = new BedrockAgentRuntimeClient({
      region: REGION,
      credentials: {
        accessKeyId: process.env.REACT_APP_AWS_ACCESS_KEY_ID || '',
        secretAccessKey: process.env.REACT_APP_AWS_SECRET_ACCESS_KEY || '',
      }
    });
  }

  async invokeAgent(inputText: string, sessionId: string = 'executive-session'): Promise<string> {
    try {
      const command = new InvokeAgentCommand({
        agentId: AGENT_ID,
        agentAliasId: AGENT_ALIAS_ID,
        sessionId,
        inputText,
      });

      const response = await this.client.send(command);
      
      if (response.completion) {
        let fullResponse = '';
        for await (const chunk of response.completion) {
          if (chunk.chunk?.bytes) {
            const text = new TextDecoder().decode(chunk.chunk.bytes);
            fullResponse += text;
          }
        }
        return fullResponse;
      }
      
      return 'No response received from agent.';
    } catch (error) {
      console.error('Error invoking Bedrock Agent:', error);
      return 'Sorry, I encountered an error processing your request. Please try again.';
    }
  }
}

export const bedrockService = new BedrockService();
