import axios, { AxiosInstance } from 'axios';

export interface Passage {
  id: string;
  text: string;
  source?: string;
}

export interface EvaluateRequest {
  question: string;
  answer: string;
  passages?: Passage[];
}

export interface Scores {
  faithfulness: number;
  coverage: number;
  toxicity: number;
}

export interface EvaluateResponse {
  decision: 'allow' | 'repair' | 'block';
  scores: Scores;
  repaired_answer?: string | null;
  explanations: string[];
  meta: Record<string, string>;
}

export class GuardrailClient {
  private client: AxiosInstance;

  constructor(baseURL: string = 'http://localhost:8000', apiKey?: string) {
    const headers: Record<string, string> = {};
    if (apiKey) {
      headers['X-API-Key'] = apiKey;
    }

    this.client = axios.create({
      baseURL,
      headers,
      timeout: 10000,
    });
  }

  async evaluate(request: EvaluateRequest): Promise<EvaluateResponse> {
    const response = await this.client.post<EvaluateResponse>('/evaluate', request);
    return response.data;
  }

  async health(): Promise<{ ok: boolean }> {
    const response = await this.client.get<{ ok: boolean }>('/health');
    return response.data;
  }
}

// Quick wrapper for LLM calls
export async function guardrailLLMCall(
  llmCall: () => Promise<string>,
  question: string,
  passages: Passage[],
  client: GuardrailClient
): Promise<{ decision: string; answer: string; scores: Scores }> {
  // Call your LLM
  const rawAnswer = await llmCall();

  // Evaluate with guardrail
  const result = await client.evaluate({
    question,
    answer: rawAnswer,
    passages,
  });

  // Return decision and (possibly repaired) answer
  return {
    decision: result.decision,
    answer: result.decision === 'repair' && result.repaired_answer
      ? result.repaired_answer
      : rawAnswer,
    scores: result.scores,
  };
}

