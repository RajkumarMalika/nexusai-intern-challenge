# Telecom AI Message Handler (Task 1)

Hey there! Welcome to my submission for the AI Message Handler task. 

For this project, I chose to use the **OpenAI API** to power a virtual telecom support agent. The goal here wasn't just to get an LLM to reply to a prompt, but to build a resilient, asynchronous backend function that handles real-world hiccups—like rate limits, timeouts, and bad inputs—gracefully.

## What's Inside?

I structured the code to be modular, typed, and easy to review:

* **Strict Output Formatting:** I used a Python `dataclass` (`MessageResponse`) combined with OpenAI's JSON mode to guarantee the AI always returns the exact fields requested (response text, confidence score, and suggested action).
* **Context-Aware Prompting:** The system prompt dynamically adjusts based on the channel. For instance, if a customer calls in via `voice`, the prompt strictly forces the LLM to keep its response under two sentences so it sounds natural when spoken out loud.
* **Bulletproof Error Handling:** * Empty or whitespace-only messages are caught instantly (no wasted API calls).
    * If OpenAI hangs for more than 10 seconds, `asyncio.wait_for` cuts it off and returns a clean timeout error.
    * If we hit a 429 Rate Limit, the code automatically catches it, sleeps for 2 seconds, and retries exactly once before giving up.

## How to Test the Logic (No API Key Required!)

I know how annoying it is to review code and immediately get blocked by API paywalls or missing keys. To make your life easier, I built a test suite using `pytest` and `unittest.mock` to artificially trigger the network timeouts and rate limits. 

You can verify that all my error-handling logic works perfectly right now, completely offline and for free:

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-asyncio httpx
Run the mocked test suite:

Bash
pytest test_handler.py -v
Running the Live Evals
If you want to see the AI in action and test its conversational chops (especially how it handles complex complaints while sticking to the voice constraints), you can run the live evaluation script. You will just need an OpenAI account with active billing credits.

Create a .env file in the root folder of this project.

Add your active API key like this (no quotes):
OPENAI_API_KEY=sk-proj-your-key-here

Run the evaluation script:

Bash
python evaluate_voice.py
Thanks for taking the time to review my code! Let me know if you have any questions about the architecture.
