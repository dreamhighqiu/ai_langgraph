"""Test embedding connection to Ollama server"""
import asyncio
import time
from lightrag.llm.ollama import ollama_embed

async def test_embedding():
    ollama_url = 'http://54.179.103.192:11434/'
    
    print("Testing embedding with single text...")
    start = time.time()
    try:
        result = await ollama_embed(
            ["Hello world"],
            embed_model="qwen3-embedding:0.6b",
            api_key="sk-danwen",
            host=ollama_url,
        )
        elapsed = time.time() - start
        print(f"✓ Success! Took {elapsed:.2f}s")
        print(f"  Result shape: {len(result)}x{len(result[0]) if result else 0}")
    except Exception as e:
        elapsed = time.time() - start
        print(f"✗ Failed after {elapsed:.2f}s: {e}")
    
    print("\nTesting embedding with multiple texts...")
    start = time.time()
    try:
        result = await ollama_embed(
            ["Text 1", "Text 2", "Text 3"],
            embed_model="qwen3-embedding:0.6b",
            api_key="sk-danwen",
            host=ollama_url,
        )
        elapsed = time.time() - start
        print(f"✓ Success! Took {elapsed:.2f}s")
        print(f"  Result shape: {len(result)}x{len(result[0]) if result else 0}")
    except Exception as e:
        elapsed = time.time() - start
        print(f"✗ Failed after {elapsed:.2f}s: {e}")

if __name__ == "__main__":
    asyncio.run(test_embedding())

