# 🎯 Interview Question Generator

A powerful CLI tool that analyzes Python codebases and automatically generates contextual technical interview questions using AI. Perfect for hiring managers, technical interviewers, and educators who want to create relevant, code-specific interview questions.

## ✨ Features

- **🔍 Intelligent Code Analysis**: Deep analysis of Python code structure, patterns, and complexity
- **🤖 AI-Powered Question Generation**: Uses OpenAI's GPT models to generate contextual questions
- **📊 Multiple Question Categories**: Comprehension, debugging, optimization, design, edge cases, and more
- **🎚️ Difficulty Levels**: Beginner, intermediate, advanced, and expert questions
- **📄 Multiple Output Formats**: JSON, Markdown, structured reports
- **⚡ Fast Processing**: Efficient analysis with progress tracking
- **🛠️ Configurable**: Flexible configuration options and CLI parameters

## 🚀 Installation

### Install from GitHub

```bash
pip install git+https://github.com/your-username/interview-generator.git
```

### Install for Development

```bash
git clone https://github.com/your-username/interview-generator.git
cd interview-generator
pip install -e .
```

### Install with Development Dependencies

```bash
pip install -e ".[dev,test]"
```

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key (get one at [OpenAI](https://platform.openai.com/api-keys))

## 🔧 Quick Start

### 1. Set up your API key

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or create a configuration file:

```bash
interview-generator config create --interactive
```

### 2. Analyze your code

```bash
# Basic analysis
interview-generator analyze /path/to/your/project

# Save as Markdown
interview-generator analyze /path/to/your/project --format markdown --output questions.md

# Generate specific question types
interview-generator analyze /path/to/your/project \
  --categories comprehension debugging optimization \
  --difficulty intermediate advanced \
  --max-questions 15
```

## 📖 Usage Examples

### Basic Analysis
```bash
# Analyze a directory with default settings
interview-generator analyze ./src

# Analyze and save to a specific file
interview-generator analyze ./src --output interview_questions.json
```

### Advanced Filtering
```bash
# Generate only comprehension and debugging questions
interview-generator analyze ./src -c comprehension -c debugging

# Filter by difficulty level
interview-generator analyze ./src -d intermediate -d advanced

# Limit the number of questions
interview-generator analyze ./src --max-questions 20
```

### Different Output Formats
```bash
# Export as Markdown
interview-generator analyze ./src --format markdown --output questions.md

# Create structured output with reports
interview-generator analyze ./src --format structured --output ./results

# Export both JSON and Markdown
interview-generator analyze ./src --format both --output questions
```

### Configuration Management
```bash
# Create interactive configuration
interview-generator config create --interactive

# Validate your setup
interview-generator validate setup

# Test API connectivity
interview-generator validate api

# Show current configuration
interview-generator config show
```

## 🎯 Question Categories

The tool generates questions in several categories:

- **🧠 Comprehension**: Understanding code purpose and functionality
- **🐛 Debugging**: Identifying and fixing issues
- **⚡ Optimization**: Performance improvements and efficiency
- **🏗️ Design**: Architecture and design patterns
- **🔍 Edge Cases**: Boundary conditions and error handling
- **🧪 Testing**: Test strategies and coverage
- **♻️ Refactoring**: Code improvement and maintainability
- **🔒 Security**: Security vulnerabilities and best practices

## 🎚️ Difficulty Levels

- **🟢 Beginner**: Basic concepts and simple implementations
- **🟡 Intermediate**: Moderate complexity and common patterns
- **🟠 Advanced**: Complex algorithms and advanced concepts
- **🔴 Expert**: Highly sophisticated and specialized knowledge

## ⚙️ Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `INTERVIEW_GENERATOR_CONFIG`: Path to custom config file

### Configuration File
Create a configuration file for persistent settings:

```bash
interview-generator config create --interactive
```

Example configuration:
```json
{
  "llm_api_key": "your-api-key",
  "llm_model": "gpt-3.5-turbo",
  "max_questions_per_category": 5,
  "output_format": "json",
  "include_hints": true,
  "quality_threshold": 0.7
}
```

## 🔍 CLI Reference

### Main Commands

- `analyze`: Analyze code and generate questions
- `config`: Manage configuration settings
- `validate`: Validate setup and test components

### Global Options

- `--verbose, -v`: Enable verbose output
- `--help`: Show help information
- `--version`: Show version information

### Analyze Command Options

```bash
interview-generator analyze [OPTIONS] DIRECTORY

Options:
  -o, --output PATH           Output file or directory path
  -f, --format [json|markdown|both|structured]
                             Output format (default: json)
  -c, --categories [comprehension|debugging|optimization|design|edge_cases|testing|refactoring|security]
                             Question categories (can be used multiple times)
  -d, --difficulty [beginner|intermediate|advanced|expert]
                             Difficulty levels (can be used multiple times)
  -n, --max-questions INTEGER RANGE
                             Maximum number of questions (1-50, default: 10)
  --config PATH              Path to configuration file
  --dry-run                  Show what would be analyzed without API calls
  -q, --quiet                Suppress progress output
  --help                     Show this message and exit
```

## 🧪 Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black src tests
isort src tests
```

### Type Checking
```bash
mypy src
```

### Pre-commit Hooks
```bash
pre-commit install
pre-commit run --all-files
```

## 📊 Example Output

### JSON Format
```json
{
  "questions": [
    {
      "id": "q1",
      "category": "comprehension",
      "difficulty": "intermediate",
      "question_text": "Explain the purpose of the UserManager class...",
      "code_snippet": "class UserManager:\n    def authenticate(self, username, password):\n        ...",
      "expected_answer": "The UserManager class handles user authentication...",
      "hints": ["Focus on the authentication method", "Consider security implications"],
      "context_references": ["Domain: web", "Pattern: authentication"]
    }
  ],
  "metadata": {
    "total_questions": 10,
    "processing_time": 15.2,
    "files_analyzed": 5,
    "model_used": "gpt-3.5-turbo"
  }
}
```

### Markdown Format
```markdown
# Interview Questions

## Question 1: Code Comprehension (Intermediate)

**Question:** Explain the purpose and functionality of the UserManager class.

**Code:**
```python
class UserManager:
    def authenticate(self, username, password):
        # Implementation details...
```

**Expected Answer:** The UserManager class handles user authentication...

**Hints:**
- Focus on the authentication method
- Consider security implications
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT models
- The Python community for excellent tooling and libraries
- Contributors and users who help improve this tool

## 📞 Support

- 📖 [Documentation](https://github.com/your-username/interview-generator#readme)
- 🐛 [Issue Tracker](https://github.com/your-username/interview-generator/issues)
- 💬 [Discussions](https://github.com/your-username/interview-generator/discussions)

---

Made with ❤️ for the developer community