# Claude API Desktop

A modern, feature-rich desktop client for the Anthropic Claude API with streaming support, extended context capabilities, and an intuitive graphical interface.


![Python](https://img.shields.io/badge/python-3.8%2B-blue)

![License](https://img.shields.io/badge/license-MIT-green)

![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)


## Features

### Core Capabilities

- **Real-time Streaming**: Stream responses as they're generated for a responsive chat experience
- **Extended Context Support**: Automatically uses beta headers for:

  - 1M context window with Claude Sonnet 4
  - 128k output tokens with Claude Sonnet 3.7

- **Multi-Model Support**: Access all Claude models including:

  - Claude Opus 4.1 & 4.0
  - Claude Sonnet 4 & 3.7
  - Claude Haiku 3.5

### User Experience

- **File Attachments**: Attach images (PNG, JPG, JPEG, GIF, WebP) and text files directly in conversations
- **System Prompts**: Configure persistent system prompts for specialized assistants
- **Export Conversations**: Save chats as Markdown or JSON for documentation and sharing
- **Token & Cost Tracking**: Real-time display of token usage and estimated API costs
- **Keyboard Shortcuts**:  Detailed below.

### Technical Features

- **Configuration Persistence**: Saves API key, model preference, and system prompt in platform-appropriate directories
- **Clean GUI**: Built with tkinter for cross-platform compatibility  
- **Threaded API Calls**: Non-blocking UI during API requests
- **Comprehensive Error Handling**: Graceful handling of connection and API errors
- **Conversation Branching**: Create alternate conversation paths and switch between them
- **SQLite Database**: Reliable local storage for conversation history in user data directories

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install from PyPI

```bash
   pip install claude-api-desktop
```
### Install from Source

1. Clone the repository:

```bash
   git clone https://github.com/anthony-maio/claude-api-desktop.git
   cd claude-api-desktop
```
2. Install using pip:

```bash
   pip install .
```
3. Run the application:

```bash
   claude-api-desktop
```
## Data Storage

The application stores all user data in platform-appropriate directories:

### Windows
- **Configuration**: `%LOCALAPPDATA%\claude-api-desktop\claude_client_config`
- **Database**: `%LOCALAPPDATA%\claude-api-desktop\conversations.db`
- **Full path**: `C:\Users\{username}\AppData\Local\claude-api-desktop\`

### macOS
- **Configuration**: `~/Library/Application Support/claude-api-desktop/claude_client_config`
- **Database**: `~/Library/Application Support/claude-api-desktop/conversations.db`

### Linux
- **Configuration**: `~/.local/share/claude-api-desktop/claude_client_config`
- **Database**: `~/.local/share/claude-api-desktop/conversations.db`

## Configuration

### API Key

1. Get your API key from `Anthropic Console <https://console.anthropic.com/>`_
2. Open Settings (⚙️ button or `Ctrl+,`)
3. Enter your API key in the API tab
4. The key is saved locally in platform-appropriate directories:
   - **Windows**: `%LOCALAPPDATA%\claude-api-desktop\claude_client_config`
   - **macOS**: `~/Library/Application Support/claude-api-desktop/claude_client_config`
   - **Linux**: `~/.local/share/claude-api-desktop/claude_client_config`

### Model Selection

Choose from the dropdown menu:

- **Claude Opus 4.1**: Most capable model for complex tasks
- **Claude Opus 4**: Previous generation Opus  
- **Claude Sonnet 4**: Balanced performance with 1M context window 
- **Claude Sonnet 3.7**: Fast with 128k output capability
- **Claude Haiku 3.5**: Fastest and cheapest

## Usage Examples

### Basic Chat

1. Enter your API key in Settings
2. Type your message
3. Press Send or `Ctrl+Enter`

### Using System Prompts *Optional*

1. Open Settings (⚙️ button)
2. Go to General tab
3. Enter instructions.

### Attaching Files *[Beta]*

1. Click the 📎 Attach button
2. Select image or text file
3. Multiple files are supported

### Conversation Branching *[Alpha]*

1. Start a conversation with Claude
2. Click 🌿 Branch button
3. Create "Alternative approach" branch
4. Continue conversation in new direction
5. Switch between branches anytime


## API Costs

**⚠️ IMPORTANT COST DISCLAIMER ⚠️**

The client displays estimated costs based on September 2025 Anthropic pricing **for reference only**. These values are:
- **NOT AUTHORITATIVE** - Always refer to your Anthropic Console for actual billing
- **ESTIMATES ONLY** - Actual costs may vary significantly
- **SUBJECT TO CHANGE** - Anthropic may update pricing at any time
- **NOT GUARANTEED ACCURATE** - Token counting is approximate

**YOU ARE SOLELY RESPONSIBLE FOR MONITORING YOUR ACTUAL API USAGE AND COSTS.** Always set spending limits in your Anthropic Console.

================= ==================== ======================
Model             Input (per 1M tokens) Output (per 1M tokens)
================= ==================== ======================
Claude Opus 4.1/4.0  $15.00              $75.00
Claude Sonnet 4/3.7   $3.00               $15.00
Claude Haiku 3.5      $0.80               $4.00
================= ==================== ======================

## Keyboard Shortcuts

**Messaging:**

* `Ctrl+Enter`: Send message
* `Escape`: Abort current request

**Conversation Management:**

* `Ctrl+N`: Start new conversation
* `Ctrl+S`: Save current conversation
* `Ctrl+H`: Open conversation history
* `Ctrl+L`: Clear current chat

**Interface:**

* `Ctrl+,`: Open Settings dialog
* `Ctrl+D`: Toggle dark/light theme
* `F1`: Show help dialog

**File Operations:**

* `Ctrl+E`: Export conversation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

* Built with [Anthropic's Claude API](https://docs.anthropic.com/)
* GUI framework: [tkinter](https://docs.python.org/3/library/tkinter.html)
* HTTP client: [requests](https://requests.readthedocs.io/)

## Author

**Anthony Maio** (anthony.maio@gmail.com)

Passionate about AI/ML, software engineering, culture and leadership.

Follow or find me on [LinkedIn](https://www.linkedin.com/in/anthony-maio) - Open to work!
*Currently seeking opportunities in AI/ML engineering full-time US Remote*

## Privacy & Data Handling

**🔒 YOUR DATA STAYS ON YOUR DEVICE 🔒**

- **No Data Collection**: This application does NOT collect, transmit, or store any of your conversations, API keys, or personal data on external servers
- **Local Storage Only**: All data (conversations, settings, API keys) is stored locally on your device in platform-appropriate directories
- **Direct API Communication**: The app communicates directly with Anthropic's API - no intermediary servers
- **Open Source**: Full source code is available for inspection - verify our privacy claims yourself
- **No Analytics**: No usage tracking, telemetry, or analytics are collected
- **No Network Requests**: Except to Anthropic's official API endpoints for chat functionality

**Your privacy is paramount. This tool is designed to be a secure, private interface to Claude API.**

## Important Disclaimers

**⚠️ LEGAL DISCLAIMERS ⚠️**

- **Independent Project**: This software is NOT affiliated with, endorsed by, or officially connected to Anthropic in any way
- **No Warranty**: This software is provided "AS IS" without warranty of any kind, express or implied
- **User Responsibility**: You are solely responsible for your API usage, costs, and compliance with Anthropic's terms of service
- **Cost Estimates**: All cost calculations are estimates only and may be inaccurate - always monitor actual usage in your Anthropic Console
- **API Compliance**: Users must comply with all Anthropic usage policies and terms of service
- **Use at Your Own Risk**: The developers are not liable for any damages, costs, or issues arising from use of this software

## Support

Support is limited and generally submitted through Github in the issues section.
If you find this tool useful, please consider:

* Starring the repository
* Contributing improvements

---

**Note**: This is an independent project and is not affiliated with Anthropic. Always ensure you comply with Anthropic's [usage policies](https://www.anthropic.com/legal/aup) when using the API.