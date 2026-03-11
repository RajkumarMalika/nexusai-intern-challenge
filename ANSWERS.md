# ANSWERS.md

## Q1
When dealing with streaming STT, blindly firing off database queries every 200ms as partial transcripts arrive is a terrible idea. That approach will quickly exhaust connection pools and effectively DDoS your own database with useless fragments like "I", "I have", or "I have an is-". However, waiting for the customer to completely stop speaking before starting all backend work adds a full second of unnatural latency, ruining the conversational flow.

My approach would be a hybrid "debounce and extract" strategy. We should run a lightweight, low-latency regex or local NER (Named Entity Recognition) function over the incoming 200ms chunks to look exclusively for hard identifiers—like a 10-digit phone number, account PIN, or order ID. The exact millisecond we detect a valid identifier mid-sentence, we fire off the async database fetch in the background. 

For the actual LLM intent classification, we must wait for the natural pause (utterance end). Feeding broken, partial sentences into a heavy LLM causes massive token waste and high hallucination rates because the model lacks full context.

**Tradeoffs:** This requires maintaining state for the audio stream and adds complexity to the frontend-backend coordination. But it gives us zero-latency data fetching combined with accurate, full-context LLM processing, optimizing both speed and cost.

## Q2
Automatically appending high-CSAT resolutions directly to a Knowledge Base (KB) is dangerous because customer satisfaction does not equal policy compliance or data quality. Over six months, this will break the system in two major ways.

**Failure Mode 1: The "Polite Bypass" Policy Breach**
Customers will happily give a 5-star rating if they get what they want. If the AI hallucinates and promises a $100 credit for a minor 10-minute outage, the customer will be thrilled. If this interaction automatically merges into the KB, the RAG system just learned a disastrous new policy and will start handing out cash to everyone.
*Prevention:* Decouple CSAT from compliance. Before any resolution enters the KB, it must pass through an asynchronous "Compliance LLM" (or human QA queue) that strictly checks the transcript against authorized company actions.

**Failure Mode 2: RAG Bloat and Contradiction**
Over six months, 5,000 customers will call about router resets, generating 500 slightly different "successful" transcripts. If we just append them, our vector database becomes severely bloated with duplicate, noisy, and potentially contradictory steps. When the system searches for "router fix," retrieval accuracy will plummet.
*Prevention:* Implement an "upsert and cluster" pipeline. Instead of appending raw entries, run a weekly cron job where an LLM clusters similar high-CSAT resolutions and updates one single, canonical "Router Troubleshooting" master article.

## Q3
Based on the Escalation Engine logic from Task 4, this specific transcript instantly triggers multiple critical red flags: the intent is `service_cancellation` (Rule 4), the sentiment is highly negative (Rule 2), and the customer explicitly mentions repeat complaints (Rule 3). Because Rule 4 (cancellations) and Rule 2 (angry customers) are top-priority overrides, the AI must immediately abort its standard troubleshooting flow. It should not attempt to apologize for the router, offer technical steps, or argue.

**Step-by-Step Execution:**
1. The AI classifies the intent and sentiment, instantly triggering the `should_escalate()` function which returns `True`.
2. It executes a rapid handoff protocol, keeping the verbal response strictly under two sentences (adhering to our Voice channel constraints) so the customer isn't forced to listen to a monologue.
3. **What the AI says:** "I completely understand your frustration, and I am so sorry you've been dealing with this for four days. Let me get you directly to a retention specialist right now who can process your request."
4. **What it passes to the agent:** It drops a structured JSON payload to the human agent's dashboard. This includes the `CustomerContext` object (containing CRM data, the 3 recent ticket IDs, and billing status), the identified intent (`service_cancellation`), the sentiment score (`-0.9`), and a generated summary: *"URGENT: Highly frustrated customer. Internet down for 4 days. 3 previous calls. Requesting immediate cancellation."*

## Q4
The single most important architectural improvement I would add is **Semantic Caching** at the LLM layer using a fast vector database like Redis or Pinecone.

Right now, if a massive storm knocks out cell service in Texas, 10,000 people will call in asking the exact same question: "Why is my service down?" Under our current architecture, our system would send 10,000 identical prompts to OpenAI. This burns through massive API credits, hits rate limits, and adds around 800ms of generation latency to every single call, which is terrible for a live voice agent.

**How I would build it:**
I would introduce a middleware caching layer. Before dispatching a prompt to OpenAI, we embed the customer's normalized transcript and perform a rapid similarity search against a cache of recently resolved queries. If the cosine similarity score is > 0.95 (meaning it is essentially the exact same question), we bypass the OpenAI API entirely. We retrieve the cached AI response and immediately send it to the Text-to-Speech engine.

**How to measure success:**
1. *Cache Hit Rate:* We would monitor our logs to see what percentage of calls are successfully served from the cache.
2. *Latency Reduction:* We should see backend response times for cached queries drop from ~800ms to under 50ms.
3. *Cost Savings:* We would track the direct reduction in OpenAI API token usage on our monthly billing dashboard.