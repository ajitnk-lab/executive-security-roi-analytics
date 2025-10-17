const API_BASE_URL = 'https://0v0eeglzg4.execute-api.us-east-1.amazonaws.com/prod';

export interface ChatMessage {
  message: string;
  sessionId?: string;
}

export interface ChatResponse {
  response: string;
  sessionId: string;
}

export interface MetricsResponse {
  securityROI: {
    value: string;
    change: string;
    trend: string;
  };
  monthlySpend: {
    value: string;
    change: string;
    trend: string;
  };
  securityScore: {
    value: string;
    change: string;
    trend: string;
  };
  lastUpdated: string;
}

class ApiService {
  async sendChatMessage(message: string, sessionId: string = 'executive-session'): Promise<string> {
    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ChatResponse = await response.json();
      return data.response;
    } catch (error) {
      console.error('Error sending chat message:', error);
      return 'Sorry, I encountered an error processing your request. Please try again.';
    }
  }

  async getMetrics(): Promise<MetricsResponse | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/metrics`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching metrics:', error);
      return null;
    }
  }
}

export const apiService = new ApiService();
