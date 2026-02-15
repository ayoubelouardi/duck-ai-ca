#!/usr/bin/env python3
"""Test the updated DuckAI client with duckduckgo.com endpoint"""

import sys

sys.path.insert(0, "/home/ia/Projects/websites/duck-ai-ca/src")

from duckai.client import DuckAIClient

print("=" * 60)
print("DuckAI Client Test - duckduckgo.com endpoint")
print("=" * 60)

client = DuckAIClient()

# Test 1: Get VQD token
print("\n[Test 1] Getting VQD token...")
try:
    vqd = client.get_vqd()
    print(f"✓ VQD Token: {vqd[:30]}...")
    if client.vqd_hash:
        print(f"✓ VQD Hash: {client.vqd_hash[:30]}...")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Test 2: Send chat message
print("\n[Test 2] Sending chat message...")
try:
    message = "What is 2+2? Answer with just the number."
    print(f"Q: {message}")
    print("A: ", end="", flush=True)

    response = client.chat(message)
    print(response)
    print(f"\n✓ Got response ({len(response)} chars)")
except Exception as e:
    print(f"\n✗ Failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Test 3: Test streaming
print("\n[Test 3] Testing streaming...")
try:
    client2 = DuckAIClient()
    message = "Say 'Hello World'"
    print(f"Q: {message}")
    print("A: ", end="", flush=True)

    for chunk in client2.stream_chat(message):
        print(chunk, end="", flush=True)

    print("\n✓ Streaming works!")
except Exception as e:
    print(f"\n✗ Failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Test 4: Test conversation continuity
print("\n[Test 4] Testing conversation continuity...")
try:
    client3 = DuckAIClient()

    # First message
    print("Q: My name is Alice")
    r1 = client3.chat("My name is Alice")
    print(f"A: {r1[:100]}...")

    # Follow-up
    print("Q: What is my name?")
    print("A: ", end="", flush=True)
    r2 = client3.chat("What is my name?")
    print(r2)

    if "alice" in r2.lower():
        print("✓ Conversation continuity works!")
    else:
        print("⚠ Response doesn't mention Alice, but API works")

except Exception as e:
    print(f"\n✗ Failed: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
