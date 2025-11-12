import { GuardrailClient, guardrailLLMCall, Passage } from './index';

// Example: Wrap your LLM call
async function main() {
  const client = new GuardrailClient(
    process.env.GUARDRAIL_URL || 'http://localhost:8000',
    process.env.GUARDRAIL_API_KEY
  );

  // Mock LLM call
  const mockLLM = async (): Promise<string> => {
    return 'Common side-effects include nausea and diarrhea.';
  };

  const passages: Passage[] = [
    {
      id: 'p1',
      text: 'Common side-effects are nausea and diarrhea, sometimes stomach upset.',
      source: 'med-guide',
    },
    {
      id: 'p2',
      text: 'Rare adverse events include lactic acidosis.',
      source: 'safety-note',
    },
  ];

  const question = 'What are side-effects of metformin?';

  const result = await guardrailLLMCall(
    mockLLM,
    question,
    passages,
    client
  );

  console.log('Decision:', result.decision);
  console.log('Scores:', result.scores);
  console.log('Answer:', result.answer);
}

if (require.main === module) {
  main().catch(console.error);
}

