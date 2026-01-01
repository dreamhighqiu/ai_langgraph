"""
Example usage of RAG Anything MCP Server

This script demonstrates how to use the RAG Anything MCP Server
for document processing and querying.
"""



import asyncio
import json
from pathlib import Path

from .config import MCSConfig
from .connector import RAGAnythingConnector


async def example_basic_setup():
    """Example: Basic setup and initialization"""
    print("=" * 80)
    print("Example 1: Basic Setup and Initialization")
    print("=" * 80)
# type: ignore  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZFZGaVZnPT06MzdlMjkzMmE=

    # Load configuration from environment
    config = MCSConfig.from_env()
    print(f"Configuration loaded: {json.dumps(config.to_dict(), indent=2)}")

    # Create connector (without LLM functions for this example)
    connector = RAGAnythingConnector(config)

    # Initialize
    result = await connector.initialize()
    print(f"Initialization result: {json.dumps(result, indent=2)}")

    # Get status
    status = await connector.get_status()
    print(f"Connector status: {json.dumps(status, indent=2)}")

    await connector.close()


async def example_document_processing():
    """Example: Document processing"""
    print("\n" + "=" * 80)
    print("Example 2: Document Processing")
    print("=" * 80)

    config = MCSConfig.from_env()
    connector = RAGAnythingConnector(config)

    result = await connector.initialize()
    if not result.get("success"):
        print(f"Initialization failed: {result.get('error')}")
        return

    # Process a document
    # Note: Replace with actual document path
    doc_path = "./sample_document.pdf"
# noqa  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZFZGaVZnPT06MzdlMjkzMmE=

    if Path(doc_path).exists():
        print(f"Processing document: {doc_path}")
        result = await connector.process_document(doc_path)
        print(f"Processing result: {json.dumps(result, indent=2)}")
    else:
        print(f"Document not found: {doc_path}")
        print("To test document processing, provide a valid document path")

    await connector.close()


async def example_querying():
    """Example: Querying the knowledge base"""
    print("\n" + "=" * 80)
    print("Example 3: Querying the Knowledge Base")
    print("=" * 80)

    config = MCSConfig.from_env()
    connector = RAGAnythingConnector(config)

    result = await connector.initialize()
    if not result.get("success"):
        print(f"Initialization failed: {result.get('error')}")
        return

    # Execute a query
    query_text = "What is machine learning?"
    print(f"Query: {query_text}")

    result = await connector.query(query_text, mode="hybrid", top_k=5)
    print(f"Query result: {json.dumps(result, indent=2)}")

    await connector.close()


async def example_multimodal_query():
    """Example: Multimodal querying"""
    print("\n" + "=" * 80)
    print("Example 4: Multimodal Querying")
    print("=" * 80)

    config = MCSConfig.from_env()
    connector = RAGAnythingConnector(config)

    result = await connector.initialize()
    if not result.get("success"):
        print(f"Initialization failed: {result.get('error')}")
        return

    # Execute a multimodal query
    query_text = "Analyze this image and table"
    multimodal_content = [
        {
            "type": "image",
            "img_path": "./sample_image.jpg",
        },
        {
            "type": "table",
            "table_data": "Name,Age,City\nAlice,25,NYC\nBob,30,LA",
        },
    ]

    print(f"Query: {query_text}")
    print(f"Multimodal content: {json.dumps(multimodal_content, indent=2)}")

    result = await connector.query(query_text, mode="hybrid")
    print(f"Query result: {json.dumps(result, indent=2)}")

    await connector.close()


async def example_configuration():
    """Example: Configuration management"""
    print("\n" + "=" * 80)
    print("Example 5: Configuration Management")
    print("=" * 80)

    config = MCSConfig.from_env()
# noqa  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZFZGaVZnPT06MzdlMjkzMmE=

    print("LLM Configuration:")
    print(f"  Provider: {config.llm.provider}")
    print(f"  Model: {config.llm.model}")
    print(f"  Base URL: {config.llm.base_url}")
    print(f"  Temperature: {config.llm.temperature}")
# pylint: disable  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZFZGaVZnPT06MzdlMjkzMmE=

    print("\nEmbedding Configuration:")
    print(f"  Use Ollama: {config.embedding.use_ollama}")
    print(f"  Model: {config.embedding.model}")
    print(f"  Host: {config.embedding.host}")

    print("\nRAG Configuration:")
    print(f"  Working Dir: {config.rag.working_dir}")
    print(f"  Parser: {config.rag.parser}")
    print(f"  Parse Method: {config.rag.parse_method}")
    print(f"  Enable Image: {config.rag.enable_image}")
    print(f"  Enable Table: {config.rag.enable_table}")
    print(f"  Enable Equation: {config.rag.enable_equation}")

    print("\nServer Configuration:")
    print(f"  Host: {config.server.host}")
    print(f"  Port: {config.server.port}")
    print(f"  SSE Mode: {config.server.sse_mode}")


async def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "RAG Anything MCP Server - Usage Examples".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")

    # Run examples
    await example_configuration()
    await example_basic_setup()

    # Uncomment to run other examples
    # await example_document_processing()
    # await example_querying()
    # await example_multimodal_query()

    print("\n" + "=" * 80)
    print("Examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

