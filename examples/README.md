# Integration Examples

Examples for integrating RAG Guardrail with popular LLM frameworks.

## LangChain

```python
from examples.langchain import GuardrailRunnable
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()
guardrail = GuardrailRunnable(api_url="http://localhost:8000", api_key="your-key")

# Use in chain
result = guardrail.invoke({
    "question": "What are side-effects?",
    "answer": llm_response.content,
    "passages": [...]
})
```

See `examples/langchain.py` for full example.

## OpenAI / TypeScript

```typescript
import { guardrailLLMCall } from './examples/openai';

const result = await guardrailLLMCall(
  () => openai.chat.completions.create({...}),
  question,
  passages,
  { apiUrl: 'http://localhost:8000', apiKey: 'your-key' }
);
```

See `examples/openai.ts` for full example.

## Vertex AI

Similar pattern - wrap your Vertex AI call with `guardrailLLMCall`.

