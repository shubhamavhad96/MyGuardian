// MIT License
// Copyright (c) 2024 MyGuardian Contributors

interface Passage {
  id: string;
  text: string;
  source?: string;
}

interface GuardrailResult {
  decision: 'allow' | 'repair' | 'block';
  answer: string;
  scores: {
    faithfulness: number;
    coverage: number;
    toxicity: number;
  };
  explanations: string[];
  repaired_answer?: string;
}

interface GuardrailConfig {
  apiUrl?: string;
  apiKey?: string;
  mode?: 'enforce' | 'shadow';
}

async function evaluateWithGuardrail(
  question: string,
  answer: string,
  passages: Passage[],
  config: GuardrailConfig = {}
): Promise<GuardrailResult> {
  const apiUrl = config.apiUrl || 'http://localhost:8000';
  const apiKey = config.apiKey || 'demo-key-change-in-production';
  const mode = config.mode || 'enforce';

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'X-API-Key': apiKey,
  };
  
  if (mode === 'shadow') {
    headers['X-Guardrail-Mode'] = 'shadow';
  }

  const response = await fetch(`${apiUrl}/evaluate`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      question,
      answer,
      passages,
    }),
  });

  if (!response.ok) {
    throw new Error(`Guardrail API error: ${response.statusText}`);
  }

  return response.json();
}

export async function guardrailLLMCall<T>(
  llmCall: () => Promise<T>,
  question: string,
  passages: Passage[],
  config: GuardrailConfig = {}
): Promise<GuardrailResult> {
  const llmResponse = await llmCall();
  
  let answer: string;
  if (typeof llmResponse === 'string') {
    answer = llmResponse;
  } else if (llmResponse && typeof llmResponse === 'object') {
    const openaiResponse = llmResponse as any;
    answer = openaiResponse.choices?.[0]?.message?.content || 
             openaiResponse.content || 
             String(llmResponse);
  } else {
    answer = String(llmResponse);
  }

  const result = await evaluateWithGuardrail(question, answer, passages, config);

  if (result.decision === 'block') {
    return {
      ...result,
      answer: 'I cannot provide that information due to safety concerns.',
    };
  } else if (result.decision === 'repair' && result.repaired_answer) {
    return {
      ...result,
      answer: result.repaired_answer,
    };
  } else {
    return {
      ...result,
      answer,
    };
  }
}

export async function exampleWithOpenAI() {
  const question = 'What are side-effects of metformin?';
  const passages: Passage[] = [
    {
      id: 'p1',
      text: 'Common side-effects are nausea and diarrhea.',
      source: 'med-guide',
    },
  ];

  const mockLLMCall = async () => {
    return {
      choices: [{
        message: {
          content: 'Common side-effects include nausea and diarrhea.',
        },
      }],
    };
  };

  const result = await guardrailLLMCall(
    mockLLMCall,
    question,
    passages,
    {
      apiUrl: 'http://localhost:8000',
      apiKey: 'demo-key-change-in-production',
    }
  );

  console.log('Decision:', result.decision);
  console.log('Answer:', result.answer);
  console.log('Scores:', result.scores);
  
  return result;
}

