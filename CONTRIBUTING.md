# Contributing to Django Celery Implementation

Thank you for your interest in contributing to this project! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect differing viewpoints and experiences

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature or bugfix
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

### 1. Clone and Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/celery-implementation.git
cd celery-implementation

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/celery-implementation.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install Development Dependencies

```bash
pip install pytest pytest-django pytest-celery coverage flake8 black isort
```

### 3. Setup Pre-commit Hooks (Optional)

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
```

## Making Changes

### Creating a Branch

```bash
# Update your local main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name

# Or for a bugfix
git checkout -b fix/bug-description
```

### Branch Naming Convention

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Adding or updating tests
- `chore/` - Maintenance tasks

## Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific test class
python manage.py test app.tests.CeleryTaskTests

# Run with pytest
pytest

# Run with coverage
coverage run -m pytest
coverage report
coverage html
```

### Writing Tests

- Write tests for all new features
- Update tests when modifying existing features
- Ensure all tests pass before submitting PR
- Aim for at least 80% code coverage

Example test:

```python
from django.test import TestCase
from app.tasks import add

class MyTaskTest(TestCase):
    def test_add_task(self):
        """Test addition task."""
        result = add.apply_async(args=[5, 3])
        self.assertEqual(result.get(timeout=10), 8)
```

## Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

- Line length: 100 characters (not 79)
- Use 4 spaces for indentation
- Use double quotes for strings
- Add docstrings to all functions, classes, and modules

### Running Code Formatters

```bash
# Format with Black
black app/ celerytest/

# Sort imports with isort
isort app/ celerytest/

# Check code style with flake8
flake8 app/ celerytest/
```

### Docstring Format

Use Google-style docstrings:

```python
def my_function(param1, param2):
    """
    Brief description of function.
    
    Longer description if needed.
    
    Args:
        param1 (str): Description of param1
        param2 (int): Description of param2
        
    Returns:
        bool: Description of return value
        
    Raises:
        ValueError: When param1 is invalid
    """
    pass
```

## Commit Messages

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(tasks): add email notification task

Add new task for sending email notifications with retry logic
and proper error handling.

Closes #123
```

```
fix(views): correct task status endpoint response

The task status endpoint was returning incorrect status codes.
Updated to properly handle all task states.

Fixes #456
```

## Pull Request Process

### Before Submitting

1. **Update your branch**
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-branch
   git rebase main
   ```

2. **Run tests**
   ```bash
   python manage.py test
   ```

3. **Check code style**
   ```bash
   black --check .
   flake8 .
   ```

4. **Update documentation** if needed

### Submitting PR

1. Push your branch to your fork
   ```bash
   git push origin your-branch
   ```

2. Go to GitHub and create a Pull Request

3. Fill in the PR template:
   - Describe your changes
   - Link related issues
   - Add screenshots if UI changes
   - List any breaking changes

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #XXX

## Testing
- [ ] All tests pass
- [ ] Added new tests
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

### Review Process

- At least one maintainer review required
- All tests must pass
- Code style checks must pass
- Address all review comments
- Keep PR focused on single feature/fix

## Areas for Contribution

### High Priority

- [ ] Additional Celery task patterns
- [ ] Performance optimization
- [ ] Better error handling
- [ ] More comprehensive tests
- [ ] Documentation improvements

### Good First Issues

- [ ] Add more example tasks
- [ ] Improve code comments
- [ ] Fix typos in documentation
- [ ] Add type hints
- [ ] Write additional tests

### Feature Requests

Check the [Issues](https://github.com/REPO/issues) page for requested features.

## Questions?

- Open an issue for questions
- Tag with `question` label
- Provide context and examples

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing! 🎉
