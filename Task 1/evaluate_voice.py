import asyncio
import re
from handler import handle_message

def count_sentences(text: str) -> int:
    """
    A lightweight sentence counter using regex.
    Splits text by periods, exclamation marks, or question marks 
    followed by a space or the end of the string.
    """
    if not text:
        return 0
    # Split the text and filter out empty strings
    sentences = re.split(r'[.!?]+(?:\s+|$)', text.strip())
    return len([s for s in sentences if s.strip()])

async def run_voice_evaluations():
    print("🚀 Starting Voice Channel Constraint Evaluation...\n")
    
    # We test different complexities to see if the LLM breaks the rule under pressure
    test_cases = [
        {"id": "C1", "msg": "My internet is down."}, # Simple
        {"id": "C2", "msg": "I've been waiting for 3 hours and my router is flashing red and nobody is helping me! I want a refund now!"}, # Angry/Complex
        {"id": "C3", "msg": "Can you tell me how to configure the DNS settings on the NovaTel XG-500 router to use Google DNS?"} # Technical
    ]

    passed_count = 0

    for idx, test in enumerate(test_cases, 1):
        print(f"--- Test Case {idx}: {test['id']} ---")
        print(f"Input: {test['msg']}")
        
        # Call the actual API (Ensure your .env has your OPENAI_API_KEY)
        response = await handle_message(test["msg"], test["id"], "voice")
        
        if response.error:
            print(f"❌ Error during API call: {response.error}\n")
            continue
            
        text = response.response_text
        sentence_count = count_sentences(text)
        
        print(f"AI Output: '{text}'")
        print(f"Sentence Count: {sentence_count}")
        
        # The Evaluation Assertion
        if sentence_count <= 2:
            print("✅ PASS: Kept strictly under 2 sentences.\n")
            passed_count += 1
        else:
            print("❌ FAIL: Exceeded the sentence limit!\n")

    print("========================================")
    print(f"🏆 Final Score: {passed_count}/{len(test_cases)} Passed")
    print("========================================")

if __name__ == "__main__":
    asyncio.run(run_voice_evaluations())
