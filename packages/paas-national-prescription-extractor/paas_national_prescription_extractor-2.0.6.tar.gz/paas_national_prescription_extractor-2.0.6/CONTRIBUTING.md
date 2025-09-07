# Contributing to Day Supply National

We welcome contributions to the Day Supply National prescription data extraction system! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Basic understanding of pharmaceutical data processing

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/day-supply-national.git
   cd day-supply-national
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -e .
   pip install -r requirements-dev.txt  # If available
   ```

4. **Verify Installation**
   ```bash
   day-supply-demo  # Should run without errors
   day-supply-test  # Should show 100% success rate
   ```

## 🛠️ Development Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints for all function parameters and return values
- Write comprehensive docstrings for all public methods
- Keep functions focused and single-purpose

### Testing
- All new features must include tests
- Maintain 100% success rate on existing tests
- Add test cases for edge cases and error conditions
- Run the full test suite before submitting: `day-supply-test`

### Documentation
- Update README.md for user-facing changes
- Add docstrings for new classes and methods
- Update CHANGELOG.md with your changes
- Include examples for new features

## 📋 Types of Contributions

### 🐛 Bug Reports
When reporting bugs, please include:
- Python version and operating system
- Complete error message and stack trace
- Minimal code example that reproduces the issue
- Expected vs. actual behavior

### 💡 Feature Requests
For new features, please provide:
- Clear description of the proposed feature
- Use case and business justification
- Proposed API design (if applicable)
- Willingness to implement the feature

### 🔧 Code Contributions

#### Adding New Medication Types
1. Add CSV data file to `day_supply_national/data/`
2. Create loading method in `extractor.py`
3. Add processing method for the medication type
4. Update `MedicationType` enum
5. Add comprehensive test cases
6. Update documentation

#### Improving Existing Features
1. Identify the specific area for improvement
2. Write tests that demonstrate the current limitation
3. Implement the improvement
4. Ensure all tests pass
5. Update documentation if needed

## 🔄 Pull Request Process

### Before Submitting
1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write clean, well-documented code
   - Add or update tests as needed
   - Update documentation

3. **Test Your Changes**
   ```bash
   day-supply-test  # Must show 100% success
   python -m pytest  # If using pytest
   ```

4. **Update Documentation**
   - Add entry to CHANGELOG.md
   - Update README.md if needed
   - Add docstrings and comments

### Submitting the PR
1. **Push Your Branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request**
   - Use a clear, descriptive title
   - Provide detailed description of changes
   - Reference any related issues
   - Include screenshots if applicable

3. **PR Description Template**
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   - [ ] All existing tests pass
   - [ ] New tests added for new functionality
   - [ ] Manual testing completed

   ## Checklist
   - [ ] Code follows project style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] CHANGELOG.md updated
   ```

### Review Process
1. **Automated Checks**
   - All tests must pass
   - Code style checks must pass
   - No security vulnerabilities

2. **Manual Review**
   - Code quality and design
   - Test coverage and quality
   - Documentation completeness
   - Performance impact

3. **Approval and Merge**
   - At least one maintainer approval required
   - All feedback addressed
   - Squash and merge preferred

## 📊 Data Contributions

### Adding New Medications
1. **Research Requirements**
   - Verify medication is FDA-approved
   - Gather accurate dosing information
   - Confirm package sizes and strengths

2. **Data Format**
   - Follow existing CSV structure
   - Use consistent naming conventions
   - Include all required fields

3. **Validation**
   - Test with multiple sig patterns
   - Verify day supply calculations
   - Check edge cases

### Updating Existing Data
1. **Document Changes**
   - Explain reason for update
   - Provide authoritative sources
   - Note any breaking changes

2. **Backward Compatibility**
   - Ensure existing functionality preserved
   - Update tests if needed
   - Consider migration path

## 🏷️ Release Process

### Version Numbering
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Checklist
1. Update version in `pyproject.toml` and `setup.py`
2. Update CHANGELOG.md with release notes
3. Run full test suite
4. Create release tag
5. Build and upload to PyPI
6. Update documentation

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain professional communication

### Getting Help
- **Issues**: Use GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub discussions for questions
- **Email**: Contact maintainers for sensitive issues

### Recognition
Contributors will be recognized in:
- CHANGELOG.md for significant contributions
- README.md contributors section
- Release notes for major features

## 📚 Resources

### Documentation
- [Python Packaging Guide](https://packaging.python.org/)
- [PEP 8 Style Guide](https://pep8.org/)
- [Type Hints Guide](https://docs.python.org/3/library/typing.html)

### Pharmaceutical Resources
- [FDA Orange Book](https://www.fda.gov/drugs/drug-approvals-and-databases/approved-drug-products-therapeutic-equivalence-evaluations-orange-book)
- [RxNorm](https://www.nlm.nih.gov/research/umls/rxnorm/)
- [PBM Guidelines](https://www.pbm.va.gov/)

### Testing
- [pytest Documentation](https://pytest.org/)
- [Python unittest](https://docs.python.org/3/library/unittest.html)

## 🙏 Thank You

Thank you for contributing to Day Supply National! Your contributions help improve prescription processing for pharmacies and healthcare systems worldwide.

---

**Questions?** Feel free to open an issue or contact the maintainers.
