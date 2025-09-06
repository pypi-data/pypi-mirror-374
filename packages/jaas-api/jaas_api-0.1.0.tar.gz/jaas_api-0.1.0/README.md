# JaaS API Python SDK

[![PyPI version](https://badge.fury.io/py/jaas-api.svg)](https://badge.fury.io/py/jaas-api)
[![Python Support](https://img.shields.io/pypi/pyversions/jaas-api.svg)](https://pypi.org/project/jaas-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python SDK for interacting with the JaaS AI evaluation API. This library provides a simple and intuitive interface for evaluating AI-generated responses against various criteria.

Visit jaas-ai.net for more information.
Note: a JaaS AI API key is required. 

## Features

- 🚀 Simple and intuitive API
- 🔧 Support for multiple evaluation types (S, C, D, V)
- 📊 Comprehensive evaluation criteria support
- 🛡️ Robust error handling
- 📝 Type hints for better IDE support
- 🐍 Python 3.7+ support

## Installation

### From PyPI (recommended)

```bash
pip install jaas-api
```


## Quick Start

```python
from jaas_api import JaaSEvaluationClient

# Initialize the client with your API key
client = JaaSEvaluationClient(api_key="your-api-key-here")

# Evaluate an AI response
result = client.evaluate(
    prompt="What is the capital of France?",
    answer="The capital of France is Paris.",
    evaluation_criteria=["accuracy", "completeness", "clarity"],
    eval_type="S"
)

print(result)
```

## API Reference

### JaaSEvaluationClient

The main client class for interacting with the JaaS API.

#### Constructor

```python
JaaSEvaluationClient(api_key: str)
```

- `api_key` (str): Your JaaS API key

#### Methods

##### evaluate()

Submit an evaluation request to the JaaS API.

```python
def evaluate(
    self,
    prompt: str,
    answer: str,
    evaluation_criteria: List[str],
    eval_type: str = "S",
    ground_truth_answer: Optional[str] = None,
    context: Optional[str] = None,
    cohort: Optional[str] = None
) -> Dict
```

**Parameters:**

- `prompt` (str): The input prompt/question
- `answer` (str): The AI-generated answer to evaluate
- `evaluation_criteria` (List[str]): List of criteria to evaluate against
- `eval_type` (str, optional): Evaluation type. Options:
- `ground_truth_answer` (str, optional): Reference answer for comparison
- `context` (str, optional): Additional context for evaluation
- `cohort` (str, optional): Cohort name for grouping evaluations

**Returns:**

- `Dict`: Evaluation results from the API

**Raises:**

- `requests.exceptions.ConnectionError`: If unable to connect to the API
- `requests.exceptions.Timeout`: If the request times out
- `requests.exceptions.RequestException`: For other request-related errors

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: info@jaas-ai.com
- 📖 Documentation: [https://jaas-ai.net ]

## Changelog

### v0.1.0 (2025-09-05)
- Initial release
- Basic evaluation functionality
- Support for multiple evaluation types
- Comprehensive error handling