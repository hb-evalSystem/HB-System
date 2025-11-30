# Contributing to HB-Eval System

Thank you for your interest in contributing to HB-Eval System! This document provides guidelines and instructions for contributing.

## 🌟 Ways to Contribute

- 🐛 **Report bugs** and issues
- 💡 **Suggest new features** or improvements
- 📝 **Improve documentation**
- 🧪 **Write tests** and improve coverage
- 🔧 **Fix bugs** and implement features
- 📊 **Validate benchmarks** independently
- 🎨 **Improve code quality**

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/HB-System.git
cd HB-System
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## 📝 Development Workflow

### Code Style

We follow PEP 8 and use automated tools:

```bash
# Format code
black hb_eval/

# Sort imports
isort hb_eval/

# Lint
flake8 hb_eval/ --max-line-length=100

# Type checking (optional)
mypy hb_eval/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=hb_eval --cov-report=html

# Run specific test file
pytest tests/test_core.py -v
```

### Pre-commit Checks

Before committing, ensure:
- ✅ All tests pass
- ✅ Code is formatted with `black`
- ✅ Imports are sorted with `isort`
- ✅ No linting errors from `flake8`

## 📋 Pull Request Process

### 1. Make Your Changes

- Write clear, concise code
- Add docstrings to functions and classes
- Include type hints where appropriate
- Write tests for new features

### 2. Update Documentation

- Update README.md if needed
- Add docstrings to new code
- Update CHANGELOG.md (if exists)

### 3. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git commit -m "feat: add new adaptive planning strategy"
git commit -m "fix: resolve memory leak in EDM"
git commit -m "docs: update installation instructions"
```

Commit message prefixes:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Adding or updating tests
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Maintenance tasks

### 4. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- **Clear title** describing the change
- **Detailed description** of what and why
- **Reference to any related issues** (#issue_number)
- **Screenshots** (if UI changes)

### 5. Code Review

- Be responsive to feedback
- Make requested changes
- Keep discussions constructive and professional

## 🧪 Adding Tests

### Test Structure

```python
class TestYourFeature:
    """Test suite for your feature."""
    
    def setup_method(self):
        """Setup before each test."""
        self.component = YourComponent()
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        result = self.component.do_something()
        assert result == expected_value
    
    def test_edge_case(self):
        """Test edge cases."""
        with pytest.raises(ValueError):
            self.component.invalid_operation()
```

### Test Coverage

Aim for:
- **>80% coverage** for new code
- **100% coverage** for critical components
- Test both success and failure cases
- Include edge cases

## 📚 Documentation Guidelines

### Docstring Format

```python
def function_name(param1: str, param2: int = 0) -> bool:
    """
    Brief description of function.
    
    Longer description if needed, explaining the purpose,
    behavior, and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When parameter is invalid
        RuntimeError: When operation fails
    
    Example:
        >>> result = function_name("test", 5)
        >>> print(result)
        True
    """
    # Implementation
    pass
```

### README Updates

When adding features:
1. Update the main README.md
2. Add usage examples
3. Update the project structure if needed
4. Document any new dependencies

## 🐛 Reporting Bugs

### Bug Report Template

```markdown
**Describe the bug**
A clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.11]
- HB-Eval version: [e.g., 1.0.0]

**Additional context**
Any other relevant information.
```

## 💡 Suggesting Features

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
Describe the problem or limitation.

**Describe the solution you'd like**
Clear description of what you want to happen.

**Describe alternatives you've considered**
Other solutions you've thought about.

**Additional context**
Any other relevant information, mockups, or examples.
```

## 🔬 Research Contributions

### Independent Benchmarking

We encourage independent validation:

1. **Run your own experiments**
2. **Document your methodology**
3. **Share your results** (via issues or discussions)
4. **Propose improvements** based on findings

### Publishing Research

If you use HB-Eval in research:
- Cite the project appropriately
- Consider contributing your findings back
- Share experimental code if possible

## ✅ Checklist

Before submitting a PR:

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Docstrings added/updated
- [ ] Commit messages are clear
- [ ] PR description is comprehensive
- [ ] No merge conflicts

## 🤝 Code of Conduct

### Our Standards

- **Be respectful** and inclusive
- **Be collaborative** and constructive
- **Accept constructive criticism** gracefully
- **Focus on what's best** for the community
- **Show empathy** towards others

### Unacceptable Behavior

- Harassment or discriminatory language
- Personal attacks or trolling
- Publishing others' private information
- Unprofessional conduct

## 📧 Contact

Questions about contributing?

- **GitHub Issues**: For bugs and features
- **GitHub Discussions**: For questions and ideas
- **Email**: hbevalframe@gmail.com

## 🙏 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in publications (for significant contributions)

---

Thank you for contributing to HB-Eval System! 🎉