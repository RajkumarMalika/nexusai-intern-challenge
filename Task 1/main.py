import asyncio
from handler import handle_message

async def main():
    print("--- Test 1: Empty Input ---")
    res1 = await handle_message("   ", "CUST-123", "chat")
    print(res1)

    print("\n--- Test 2: Voice Channel (Must be < 2 sentences) ---")
    res2 = await handle_message("My internet keeps dropping every 5 minutes!", "CUST-456", "voice")
    print(res2)

    print("\n--- Test 3: WhatsApp Channel ---")
    res3 = await handle_message("How do I pay my bill?", "CUST-789", "whatsapp")
    print(res3)

if __name__ == "__main__":
    asyncio.run(main())
