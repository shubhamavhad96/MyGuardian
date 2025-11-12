# MyGuardian TypeScript SDK

Type-safe client for the MyGuardian RAG Guardrail API.

## Installation

```bash
npm install
npm run build
```

## Quick Start

```typescript
import { GuardrailClient } from '@myguardian/sdk';

const client = new GuardrailClient('http://localhost:8000', 'your-api-key');

const result = await client.evaluate({
  question: 'What are side-effects of metformin?',
  answer: 'Common side-effects include nausea and diarrhea.',
  passages: [
    { id: 'p1', text: 'Common side-effects are nausea and diarrhea.', source: 'med-guide' }
  ]
});

console.log(result.decision); // 'allow' | 'repair' | 'block'
```

## Wrap Your LLM Call

See `demo.ts` for a complete example of wrapping an LLM call with guardrails.

