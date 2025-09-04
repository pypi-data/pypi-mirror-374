# Visa Clearing File Parser

A Python library for parsing Visa BASE II Clearing Transaction Files (.ctf).




## 📥 Installation

### From PyPI
```bash
pip install visa-clearing-file-parser
```

### From Source
```bash
git clone https://github.com/makafanpeter/visa-clearing-file-parser.git
cd visa-clearing-file-parser
pip install -e .
```

### 🔧 Quick Start
```python
from visa_clearing import VisaBaseIIParser

# Initialize parser
parser = VisaBaseIIParser()

# Parse file and iterate through transactions
for transaction in parser.parse_file('transactions.ctf'):
    print(f"Transaction: {transaction['Transaction Description']}")
    print(f"Amount: {transaction.get('Source Amount', 'N/A')}")
    print(f"Merchant: {transaction.get('Merchant Name', 'N/A')}")
    print("-" * 40)
```

### 💻 CLI Usage
```bash
# Parse a file and display summary
visa-clearing-parser parse transactions.ctf --format summary

# Output as JSON
visa-clearing-parser parse transactions.ctf --format json --output results.json

# Show parser information
visa-clearing-parser info --verbose
```

### 📋 Supported Transaction Types
- Sales Draft
- Credit Voucher
- Cash Disbursement
- Chargeback, Sales Draft
- Chargeback, Credit Voucher
- Reversal, Sales Draft

### 🛠️ Development
```bash
# Clone the repository
git clone https://github.com/makafanpeter/visa-clearing-file-parser.git
cd visa-clearing-file-parser

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run linting
black src/ tests/
flake8 src/ tests/
```
### 🤝 Contributing
1. Fork the repository
2. Create a feature branch (git checkout -b feature/amazing-feature)
3. Commit your changes (git commit -m 'Add amazing feature')
4. Push to the branch (git push origin feature/amazing-feature)
5. Open a Pull Request
