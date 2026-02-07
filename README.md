# Python Automation Scripts

A collection of Python automation scripts for browser testing, web scraping, and task automation developed using PyCharm.

## 📋 Table of Contents

- [About](#about)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Configuration](#configuration)
- [Scripts Overview](#scripts-overview)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## 🎯 About

This repository contains Python automation scripts designed to streamline repetitive tasks, perform web testing, and automate browser interactions. All scripts are developed and tested using PyCharm IDE.

## ✨ Features

- 🤖 **AI-Powered Testing**: Integration with OpenAI GPT for intelligent test generation and analysis
- 🌐 **Browser Automation**: Selenium-based web automation and testing
- 📊 **Automated Reporting**: Generate detailed test reports and summaries
- 🔄 **Reusable Components**: Modular code structure for easy maintenance
- 🛠️ **PyCharm Integration**: Optimized for PyCharm development environment

## 📦 Prerequisites

Before running these scripts, ensure you have the following installed:

- **Python**: Version 3.8 or higher
- **PyCharm**: Community or Professional Edition (recommended)
- **pip**: Python package manager
- **Git**: For version control

### System Requirements

- **OS**: Windows 10/11, macOS 10.14+, or Linux
- **RAM**: Minimum 4GB (8GB recommended)
- **Browser**: Google Chrome (for Selenium scripts)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/python-automation-scripts.git
cd python-automation-scripts
```

### 2. Create Virtual Environment (Recommended)

#### Using PyCharm:
1. Open the project in PyCharm
2. Go to `File` → `Settings` → `Project` → `Python Interpreter`
3. Click the gear icon → `Add` → `New Environment`
4. Select `Virtualenv` and click `OK`

#### Using Command Line:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install ChromeDriver (for Selenium scripts)

**Option 1: Automatic (Recommended)**
```bash
pip install webdriver-manager
```

**Option 2: Manual**
- Download ChromeDriver from: https://chromedriver.chromium.org/
- Match your Chrome browser version
- Add to system PATH

### 5. Set Up API Keys

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your-openai-api-key-here
```

**Note**: Never commit your `.env` file to Git!

## 📁 Project Structure

```
python-automation-scripts/
│
├── scripts/                    # Main automation scripts
│   ├── ai_browser_tester.py   # AI-powered browser testing
│   ├── web_scraper.py         # Web scraping utilities
│   └── task_automation.py     # General task automation
│
├── tests/                      # Unit and integration tests
│   ├── test_browser.py
│   └── test_automation.py
│
├── config/                     # Configuration files
│   ├── settings.py
│   └── config.json
│
├── reports/                    # Generated test reports
│   └── .gitkeep
│
├── screenshots/                # Screenshots from tests
│   └── .gitkeep
│
├── utils/                      # Utility functions
│   ├── helpers.py
│   └── logger.py
│
├── .env.example               # Example environment variables
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── LICENSE                    # License information
```

## 💻 Usage

### Running Scripts in PyCharm

1. **Open the project** in PyCharm
2. **Right-click** on the script file (e.g., `ai_browser_tester.py`)
3. **Select** `Run 'script_name'`

### Running Scripts from Command Line

```bash
# Activate virtual environment first
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Run a script
python scripts/ai_browser_tester.py
```

### Basic Example

```python
from scripts.ai_browser_tester import AIBrowserTester
import os

# Initialize tester
api_key = os.getenv("OPENAI_API_KEY")
tester = AIBrowserTester(api_key)

# Setup browser
tester.setup_browser(headless=False)

# Navigate and test
tester.driver.get("https://example.com")
recommendations = tester.analyze_page_elements()
print(recommendations)

# Cleanup
tester.cleanup()
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4

# Browser Configuration
HEADLESS_MODE=False
BROWSER_TIMEOUT=10

# Logging
LOG_LEVEL=INFO
LOG_FILE=automation.log
```

### PyCharm Run Configuration

1. Go to `Run` → `Edit Configurations`
2. Click `+` → `Python`
3. Set **Script path** to your main script
4. Set **Working directory** to project root
5. Add **Environment variables** from `.env`
6. Click `Apply` and `OK`

## 📜 Scripts Overview

### AI Browser Tester (`ai_browser_tester.py`)

AI-powered browser automation and testing using Selenium and OpenAI.

**Features:**
- Generate test cases automatically
- Analyze page elements
- Execute tests with AI verification
- Generate bug reports

**Usage:**
```bash
python scripts/ai_browser_tester.py
```

### Web Scraper (`web_scraper.py`)

Extract data from websites efficiently.

**Usage:**
```bash
python scripts/web_scraper.py --url https://example.com
```

### Task Automation (`task_automation.py`)

Automate repetitive tasks and workflows.

**Usage:**
```bash
python scripts/task_automation.py --task <task_name>
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Code Style

- Follow **PEP 8** style guidelines
- Use **meaningful variable names**
- Add **docstrings** to functions and classes
- Write **unit tests** for new features

## 🐛 Troubleshooting

### Common Issues

#### Issue: `ModuleNotFoundError: No module named 'selenium'`
**Solution:**
```bash
pip install selenium
```

#### Issue: `ChromeDriver not found`
**Solution:**
```bash
pip install webdriver-manager
```
Or download manually and add to PATH.

#### Issue: `OpenAI API authentication error`
**Solution:**
- Verify your API key in `.env` file
- Ensure you have credits in your OpenAI account
- Check if the key is correctly loaded: `print(os.getenv("OPENAI_API_KEY"))`

#### Issue: `Permission denied` on Linux/macOS
**Solution:**
```bash
chmod +x venv/bin/activate
```

#### Issue: PyCharm not detecting virtual environment
**Solution:**
1. Go to `File` → `Settings` → `Project` → `Python Interpreter`
2. Click gear icon → `Show All`
3. Click `+` → `Add Local Interpreter`
4. Navigate to `venv/bin/python` (Linux/macOS) or `venv\Scripts\python.exe` (Windows)

### Enable Debug Logging

Add to your script:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Requirements.txt

```
selenium>=4.15.0
openai>=1.0.0
python-dotenv>=1.0.0
webdriver-manager>=4.0.0
requests>=2.31.0
beautifulsoup4>=4.12.0
pandas>=2.1.0
pytest>=7.4.0
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter) - your.email@example.com

Project Link: [https://github.com/yourusername/python-automation-scripts](https://github.com/yourusername/python-automation-scripts)

## 🙏 Acknowledgments

- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [PyCharm Documentation](https://www.jetbrains.com/help/pycharm/)
- [Python Best Practices](https://docs.python-guide.org/)

---

**⭐ If you found this helpful, please give it a star!**

**Made with ❤️ using PyCharm**
