# Contributing to HB-Eval

Thank you for your interest in contributing. HB-Eval is a research
artifact accompanying a peer-reviewed manuscript, and contributions are
welcome—whether fixing a bug, improving documentation, extending a
methodology, or strengthening reproducibility. This guide explains how to
contribute effectively and the constraints that keep the project portable
and verifiable.

## Project Philosophy and Constraints

HB-Eval is designed to run in constrained environments and to be
auditable line by line. Two constraints follow from this and apply to all
contributions:

1. **Python-only.** The entire codebase is implemented in pure Python.
   Contributions must not introduce components in other languages.

2. **Minimal external dependencies.** The core library (metric
   computation, statistics, certification logic) is designed to run with
   the standard scientific Python stack only. Do not add a new third-party
   dependency unless it is strictly necessary; if you believe one is
   required, open an issue first to discuss it before submitting a pull
   request. The goal is that any reviewer can reproduce results in a
   minimal environment without a complex dependency tree.

If a contribution cannot be expressed within these constraints, please
open an issue describing the need so it can be discussed before any code
is written.

## Development Setup

```bash
git clone https://github.com/hb-evalSystem/HB-System.git
cd HB-System
pip install -r requirements.txt
```

Verify your environment by running the test suite (see below). If the
tests pass, you are ready to develop.

## Code Style

All Python code follows **PEP 8**. In addition:

- Use clear, descriptive names; prefer readability over brevity.
- Every public function and class has a docstring stating what it does,
  its parameters, and its return value.
- Keep functions focused; a function that computes a metric should compute
  that metric and nothing else.
- Scientific code must be traceable to the paper: where a function
  implements an equation or threshold from the manuscript, cite the
  relevant section or equation in a comment, so a reviewer can map code to
  paper.

Before submitting, please run a style check (for example, `flake8` or
`ruff`) locally and resolve any reported issues. Style tooling is a
developer convenience and is not bundled as a runtime dependency.

## Testing

The project includes a unit-test suite covering metric computation,
certification logic, and statistical routines.

```bash
python tests/test_suite.py
```

All tests must pass before a pull request can be merged. If you add or
change behaviour, add or update tests so that the change is covered. A
contribution that changes a numerical result must explain, in the pull
request description, why the new result is correct and how it relates to
the manuscript.

## Pull Request Process

1. **Open an issue first** for anything beyond a trivial fix, so the
   approach can be agreed before you invest effort.
2. **Branch** from `main` with a descriptive branch name.
3. **Keep the change focused**: one logical change per pull request.
4. **Run the tests** and a style check locally; both must be clean.
5. **Describe the change** clearly: what it does, why, and—if it touches
   numerical results—how it relates to the paper.
6. **Reference the issue** the pull request resolves.

Maintainers review for correctness, scientific fidelity to the
manuscript, adherence to the Python-only / minimal-dependency constraints,
and test coverage.

## Reporting Bugs and Requesting Features

Use GitHub issues. For a bug, include the Python version, the exact
command run, the full error output, and a minimal example that reproduces
the problem. For a feature, describe the scientific or practical need it
serves.

## Security Issues

Do **not** report security vulnerabilities through public issues. Please
follow the responsible-disclosure process in
[SECURITY.md](./SECURITY.md).

## Code of Conduct

Be respectful, constructive, and professional. Critique ideas and code,
not people. Assume good faith. Maintainers may remove comments,
contributions, or contributors that do not meet this standard.

## License

By contributing, you agree that your contributions are licensed under the
MIT License that covers the project.
