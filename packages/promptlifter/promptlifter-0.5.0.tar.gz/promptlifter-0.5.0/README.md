# PromptLifter

A conversation-focused LLM interface with intelligent context management, optional search integration, and optimized LLM interactions for conversational AI applications. Features real-time web search, vector database integration, and seamless conversation flow with automatic context optimization.

[![PyPI version](https://badge.fury.io/py/promptlifter.svg)](https://badge.fury.io/py/promptlifter)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/promptlifter/promptlifter/workflows/CI/badge.svg)](https://github.com/promptlifter/promptlifter/actions)

## ✨ Features

- **Conversation-Focused**: Maintains conversation history with automatic summarization and context flow
- **Intelligent Context Management**: Automatic context optimization for LLM token limits with smart relevance filtering
- **Real-Time Search Integration**: Conditional web search (Tavily) and vector search (Pinecone) with context-aware triggering
- **Seamless Conversation Flow**: Builds upon previous interactions for natural, context-aware responses
- **Multiple LLM Support**: OpenAI, Anthropic, Google, and custom/local LLM endpoints (Ollama, Lambda Labs, Together AI)
- **Smart Embedding Service**: Automatic fallback embedding with support for custom and commercial providers
- **Production Ready**: Security-hardened, optimized, and thoroughly tested with 115+ test cases
- **Flexible Configuration**: Configurable search behavior, token limits, and context strategies

## 🚀 Quick Start

### Installation

#### From PyPI (Recommended)
```bash
pip install promptlifter
```

#### From Source
```bash
git clone https://github.com/promptlifter/promptlifter
cd promptlifter
pip install -e .
```

### Basic Usage

```python
import asyncio
from promptlifter import ConversationLLM

async def main():
    # Initialize conversation LLM
    llm = ConversationLLM()

    # Start a conversation
    response = await llm.chat("What is machine learning?")
    print(response.message)

    # Follow-up with context (automatically uses previous conversation)
    response = await llm.chat("Can you give me an example?")
    print(response.message)

if __name__ == "__main__":
    asyncio.run(main())
```

### Quick Chat Function

```python
import asyncio
from promptlifter import quick_chat

async def main():
    # One-liner for simple interactions
    response = await quick_chat("Explain quantum computing")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

### Command Line Usage

```bash
# Interactive mode
promptlifter --interactive

# Single query
promptlifter --query "Research AI in healthcare applications"

# Save results to file
promptlifter --query "Quantum computing research" --save results.json
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                USER INTERFACE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                     │
│  │     CLI     │    │  Python API │    │ Interactive │                     │
│  │  Interface  │    │             │    │    Mode     │                     │
│  └─────────────┘    └─────────────┘    └─────────────┘                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MAIN APPLICATION                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                        ConversationLLM                                 │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │ │
│  │  │   Conversation  │  │   Context       │  │   Context       │        │ │
│  │  │    Manager      │  │   Retriever     │  │   Optimizer     │        │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘        │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SERVICES LAYER                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │    LLM      │  │ Embedding   │  │   Tavily    │  │  Pinecone   │       │
│  │  Service    │  │  Service    │  │   Search    │  │   Vector    │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL PROVIDERS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   OpenAI    │  │ Anthropic   │  │   Google    │  │   Custom    │       │
│  │     API     │  │     API     │  │     API     │  │    LLM      │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   Web       │  │  Vector     │  │  Local      │  │   Remote    │       │
│  │  Content    │  │  Database   │  │  Models     │  │  Services   │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘

DATA FLOW:
User Input → CLI/API → Main App → ConversationLLM → Context Management
                                                      ↓
External Search ← Context Retriever ← Context Analysis
                                                      ↓
LLM Processing ← Context Optimizer ← Search Results + History
                                                      ↓
Response Generation → User Output
```

## 🔧 Setup

### 1. Clone the Repository

```bash
git clone https://github.com/promptlifter/promptlifter
cd promptlifter
```

### 2. Install Dependencies

#### Option 1: Install from Source
```bash
pip install -e .
```

#### Option 2: Install with Development Dependencies
```bash
pip install -e ".[dev]"
```

#### Option 3: Install with Test Dependencies
```bash
pip install -e ".[test]"
```

### 3. Configure Environment Variables

Copy the example environment file and configure your API keys:

```bash
cp env.example .env
```

Edit `.env` with your configuration:

```env
# Custom LLM Configuration (Primary - Local Models or OpenAI-Compatible APIs)
CUSTOM_LLM_ENDPOINT=http://localhost:11434
CUSTOM_LLM_MODEL=llama3.1
CUSTOM_LLM_API_KEY=

# LLM Provider Configuration (Choose ONE provider)
LLM_PROVIDER=custom  # custom, openai, anthropic, google

# Embedding Configuration (Choose ONE provider)
EMBEDDING_PROVIDER=custom  # custom, openai, anthropic
EMBEDDING_MODEL=nomic-embed-text  # Ollama embedding model (for custom provider) or OpenAI model name

# Commercial LLM Configuration (API keys for non-custom providers)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GOOGLE_API_KEY=your-google-api-key-here

# Search and Vector Configuration (Optional)
TAVILY_API_KEY=your-tavily-api-key-here
PINECONE_API_KEY=your-pinecone-api-key-here
PINECONE_INDEX=your-pinecone-index-name-here
PINECONE_NAMESPACE=research

# Conversation Context Settings
MAX_HISTORY_TOKENS=4000              # Maximum tokens for conversation history
MAX_CONTEXT_TOKENS=2000              # Maximum tokens for context assembly
ENABLE_AUTO_SEARCH=true              # Enable automatic search
SEARCH_RELEVANCE_THRESHOLD=0.7       # Minimum relevance score for search results

# Pinecone Search Configuration (Optional)
PINECONE_TOP_K=10                    # Number of results (default: 10)
PINECONE_SIMILARITY_THRESHOLD=0.7    # Minimum similarity (0.0-1.0)
PINECONE_INCLUDE_SCORES=true         # Show similarity scores
PINECONE_FILTER_BY_SCORE=true        # Filter by threshold
```

### 4. Set Up LLM Providers

#### Option 1: Local LLM (Recommended - No API Keys Needed)

##### Using Ollama (Easiest)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Llama 3.1 model
ollama pull llama3.1

# Start Ollama server
ollama serve
```

##### Using Other Local LLM Servers
- **LM Studio**: Run with OpenAI-compatible API
- **vLLM**: Fast inference server
- **Custom endpoints**: Any OpenAI-compatible API

#### Option 2: OpenAI-Compatible APIs (Requires API Keys)

##### Lambda Labs Setup
1. Get API key from https://cloud.lambdalabs.com/
2. Add to `.env`:
```env
CUSTOM_LLM_ENDPOINT=https://api.lambda.ai/v1
CUSTOM_LLM_MODEL=llama-4-maverick-17b-128e-instruct-fp8
CUSTOM_LLM_API_KEY=your-lambda-api-key-here
```

##### Together AI Setup
1. Get API key from https://together.ai/
2. Add to `.env`:
```env
CUSTOM_LLM_ENDPOINT=https://api.together.xyz/v1
CUSTOM_LLM_MODEL=meta-llama/Llama-3.1-8B-Instruct
CUSTOM_LLM_API_KEY=your-together-api-key-here
```

##### Perplexity AI Setup
1. Get API key from https://www.perplexity.ai/
2. Add to `.env`:
```env
CUSTOM_LLM_ENDPOINT=https://api.perplexity.ai
CUSTOM_LLM_MODEL=llama-3.1-8b-instruct
CUSTOM_LLM_API_KEY=your-perplexity-api-key-here
```

#### Option 3: Commercial LLM (Fallback)

##### OpenAI Setup
1. Get API key from https://platform.openai.com/api-keys
2. Add to `.env`:
```env
OPENAI_API_KEY=sk-your-actual-key-here
```

##### Anthropic Setup
1. Get API key from https://console.anthropic.com/
2. Add to `.env`:
```env
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

##### Google Setup
1. Get API key from https://makersuite.google.com/app/apikey
2. Add to `.env`:
```env
GOOGLE_API_KEY=your-actual-key-here
```

### 5. Run the Application

#### Interactive Mode
```bash
promptlifter --interactive
# or
python -m promptlifter.main --interactive
```

#### Single Query Mode
```bash
promptlifter --query "Research quantum computing trends"
# or
python -m promptlifter.main --query "Research quantum computing trends"
```

### 6. Run Tests

```bash
# Run all tests
python run_tests.py

# Run specific tests
python run_tests.py config

# Run with pytest directly
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=promptlifter --cov-report=html
```

## 🆕 Recent Improvements (v0.5.0+)

### Enhanced Context Management
- **Simplified Relevance Scoring**: Removed complex keyword matching in favor of trusting search engine results
- **Improved Conversation Flow**: Better follow-up question handling with context-aware search triggering
- **Fixed Embedding Issues**: Resolved 400 errors with custom embedding models and improved fallback handling

### Smart Search Integration
- **Context-Aware Search**: Follow-up questions now properly use conversation context instead of unnecessary external searches
- **Real-Time Web Search**: Tavily integration provides current information for weather, news, and research queries
- **Vector Database Support**: Pinecone integration for knowledge base queries with similarity scoring

### Production Ready
- **115+ Test Cases**: Comprehensive test coverage including unit, integration, and configuration tests
- **Clean Architecture**: Simplified codebase with removed complexity and improved maintainability
- **Better Error Handling**: Graceful fallbacks and improved error messages

### Key Fixes in v0.5.0
- ✅ **Fixed Embedding Service**: Resolved 400 errors when using custom embedding models with Ollama
- ✅ **Improved Context Flow**: Follow-up questions now maintain conversation context properly
- ✅ **Simplified Relevance Logic**: Removed brittle keyword matching for more reliable search results
- ✅ **Enhanced Test Coverage**: All 115 tests passing with comprehensive coverage
- ✅ **Better Error Messages**: More informative error handling and debugging information

## 🚀 How It Works

### Conversation-Focused Architecture

1. **Query Input**: User provides a message or question
2. **Context Analysis**: System determines if external search is needed
3. **Intelligent Search**: When needed, performs web and/or vector search
4. **Context Assembly**: Combines conversation history with search results
5. **LLM Processing**: Generates response using optimized context
6. **History Management**: Updates conversation history with new interaction

### Key Components

#### ConversationLLM
- Main interface for conversational interactions
- Manages conversation history and context
- Handles search integration automatically

#### ConversationContextManager
- Maintains conversation history with automatic summarization
- Manages token limits and context optimization
- Provides conversation statistics and export/import

#### ContextRetriever
- Intelligently determines when search is needed
- Performs conditional web and vector search
- Filters results by relevance

#### ContextOptimizer
- Assembles optimal context for LLM inference
- Manages token limits and compression
- Prioritizes most relevant information

## 🎯 Configuration Options

### Conversation Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `max_history_tokens` | int | 4000 | Maximum tokens to keep in conversation history |
| `max_context_tokens` | int | 2000 | Maximum tokens for context assembly |
| `enable_auto_search` | bool | true | Enable automatic search when needed |
| `search_relevance_threshold` | float | 0.7 | Minimum relevance score for search results |
| `system_prompt` | str | "You are a helpful assistant." | System prompt for LLM |

### Search Configuration

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `PINECONE_TOP_K` | int | 10 | Number of results to retrieve |
| `PINECONE_SIMILARITY_THRESHOLD` | float | 0.7 | Minimum similarity score (0.0-1.0) |
| `PINECONE_INCLUDE_SCORES` | bool | true | Include similarity scores in output |
| `PINECONE_FILTER_BY_SCORE` | bool | true | Filter results by similarity threshold |

## 🔍 Advanced Usage

### Custom Configuration

```python
import asyncio
from promptlifter import ConversationLLM, ConversationConfig

async def main():
    # Create custom configuration
    config = ConversationConfig(
        max_history_tokens=3000,
        max_context_tokens=1500,
        enable_auto_search=True,
        search_relevance_threshold=0.8,
        system_prompt="You are a research assistant specializing in AI."
    )

    # Initialize with custom config
    llm = ConversationLLM(config)

    # Use the configured LLM
    response = await llm.chat("What are the latest AI trends?")
    print(response.message)

if __name__ == "__main__":
    asyncio.run(main())
```

### Conversation Management

```python
# Get conversation statistics
stats = llm.get_conversation_stats()
print(f"Total turns: {stats['total_turns']}")
print(f"Current tokens: {stats['current_tokens']}")

# Export conversation history
history = llm.export_conversation()
print(f"Exported {len(history)} conversation turns")

# Clear conversation
llm.clear_conversation()

# Import conversation history
llm.import_conversation(history)
```

### Search Statistics

```python
# Get retrieval statistics
retrieval_stats = llm.get_retrieval_stats()
print(f"Tavily enabled: {retrieval_stats['tavily_enabled']}")
print(f"Pinecone enabled: {retrieval_stats['pinecone_enabled']}")

# Get optimization statistics
optimization_stats = llm.get_optimization_stats()
print(f"Max tokens: {optimization_stats['max_tokens']}")
print(f"Compression enabled: {optimization_stats['compression_enabled']}")
```

## 🛠️ Troubleshooting

### Common Issues

#### No Search Results
1. Check if `ENABLE_AUTO_SEARCH=true` and API keys are configured
2. Verify Tavily and Pinecone API keys are valid
3. Check if your Pinecone index has data

#### Context Too Long
1. Reduce `MAX_CONTEXT_TOKENS` or enable compression
2. Lower `MAX_HISTORY_TOKENS` to keep less history
3. Clear conversation regularly with `llm.clear_conversation()`

#### Memory Issues
1. Reduce `MAX_HISTORY_TOKENS` or clear conversation regularly
2. Use smaller context windows
3. Enable context compression

#### API Errors
1. Verify API keys are correct and have sufficient credits
2. Check API service status
3. Review rate limiting settings

### Debug Information

```python
import asyncio
import logging
from promptlifter import ConversationLLM

async def debug_example():
    # Enable detailed logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize LLM
    llm = ConversationLLM()

    # Get detailed response information
    response = await llm.chat("Your question")
    print(f"Context sources: {response.context_sources}")
    print(f"Tokens used: {response.tokens_used}")
    print(f"Conversation stats: {response.conversation_stats}")

if __name__ == "__main__":
    asyncio.run(debug_example())
```

### Search Debugging

```python
# Get search statistics
retrieval_stats = llm.get_retrieval_stats()
print(f"Retrieval: {retrieval_stats}")

# Get optimization statistics
optimization_stats = llm.get_optimization_stats()
print(f"Optimization: {optimization_stats}")
```

## 📦 Development & Release

### For Developers

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run quality checks
tox

# Run tests
pytest tests/ -v

# Format code
black promptlifter tests
```

### For Contributors

Please see the project repository for development guidelines and contribution instructions.

### Release Process

```bash
# Setup PyPI credentials
python scripts/setup_pypi.py

# Test release to TestPyPI
python scripts/release.py test

# Release to PyPI
python scripts/release.py release
```

## 🧪 Testing

The project includes comprehensive test coverage:

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end functionality testing
- **Configuration Tests**: Environment and setup validation
- **Service Tests**: LLM and embedding service testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test suites
pytest tests/test_conversation_interface_simple.py -v
pytest tests/test_conversation_interface.py::TestIntegration -v

# Run with coverage
pytest tests/ --cov=promptlifter --cov-report=html
```

## 🔒 Security & Quality

The codebase has been thoroughly audited for security and quality:

- **Security Hardened**: No vulnerabilities, secure coding practices
- **Code Quality**: No unused code, optimized imports, clean structure
- **Production Ready**: Comprehensive testing, proper logging, error handling
- **Maintainable**: Clean architecture, well-documented, consistent style

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

Please see the project repository for detailed contribution guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM deployment
- [Meta](https://ai.meta.com/) for Llama models
- [Tavily](https://tavily.com/) for web search capabilities
- [Pinecone](https://www.pinecone.io/) for vector search infrastructure
- [OpenAI](https://openai.com/) for embedding models and API
- [Anthropic](https://anthropic.com/) for Claude models and API