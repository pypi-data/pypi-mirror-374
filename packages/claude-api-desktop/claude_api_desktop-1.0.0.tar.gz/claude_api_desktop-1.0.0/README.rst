================
Claude API Desktop
================

A modern, feature-rich desktop client for the Anthropic Claude API with streaming support, extended context capabilities, and an intuitive graphical interface.

.. image:: https://img.shields.io/badge/python-3.8%2B-blue
   :alt: Python
   :target: https://www.python.org/

.. image:: https://img.shields.io/badge/license-MIT-green
   :alt: License
   :target: #license

.. image:: https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey
   :alt: Platform

Features
========

Core Capabilities
-----------------

- **Real-time Streaming**: Stream responses as they're generated for a responsive chat experience
- **Extended Context Support**: Automatically uses beta headers for:

  - 1M context window with Claude Sonnet 4
  - 128k output tokens with Claude Sonnet 3.7

- **Multi-Model Support**: Access all Claude models including:

  - Claude Opus 4.1 & 4.0
  - Claude Sonnet 4 & 3.7
  - Claude Haiku 3.5

User Experience
---------------

- **File Attachments**: Attach images (PNG, JPG, JPEG, GIF, WebP) and text files directly in conversations
- **System Prompts**: Configure persistent system prompts for specialized assistants
- **Export Conversations**: Save chats as Markdown or JSON for documentation and sharing
- **Token & Cost Tracking**: Real-time display of token usage and estimated API costs
- **Keyboard Shortcuts**: Detailed below

Technical Features
------------------

- **Configuration Persistence**: Saves API key, model preference, and system prompt
- **Clean GUI**: Built with tkinter for cross-platform compatibility
- **Threaded API Calls**: Non-blocking UI during API requests
- **Comprehensive Error Handling**: Graceful handling of connection and API errors

Installation
============

Prerequisites
-------------

- Python 3.8 or higher
- pip package manager

Install from Source
-------------------

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/anthony-maio/claude-api-desktop.git
      cd claude-api-desktop

2. Install using setup.py:

   .. code-block:: bash

      pip install .

3. Run the application:

   .. code-block:: bash

      python claude-python-client.py
      # Or after installation:
      claude-api-desktop

Quick Install (Alternative)
----------------------------

.. code-block:: bash

   pip install -r requirements.txt
   python claude-python-client.py

Data Storage
============

The application stores all user data in platform-appropriate directories:

**Windows:**

- Configuration: ``%LOCALAPPDATA%\claude-api-desktop\claude_client_config``
- Database: ``%LOCALAPPDATA%\claude-api-desktop\conversations.db``
- Full path: ``C:\Users\{username}\AppData\Local\claude-api-desktop\``

**macOS:**

- Configuration: ``~/Library/Application Support/claude-api-desktop/claude_client_config``
- Database: ``~/Library/Application Support/claude-api-desktop/conversations.db``

**Linux:**

- Configuration: ``~/.local/share/claude-api-desktop/claude_client_config``
- Database: ``~/.local/share/claude-api-desktop/conversations.db``

Configuration
=============

API Key
-------

1. Get your API key from `Anthropic Console <https://console.anthropic.com/>`_
2. Enter it in the Settings dialog (⚙️ button or ``Ctrl+,``)
3. The key is saved locally in platform-appropriate directories:
   
   - **Windows**: ``%LOCALAPPDATA%\claude-api-desktop\claude_client_config``
   - **macOS**: ``~/Library/Application Support/claude-api-desktop/claude_client_config``
   - **Linux**: ``~/.local/share/claude-api-desktop/claude_client_config``

Model Selection
---------------

Choose from the dropdown menu:

- **Claude Opus 4.1**: Most capable model for complex tasks
- **Claude Opus 4**: Previous generation Opus
- **Claude Sonnet 4**: Balanced performance with 1M context window
- **Claude Sonnet 3.7**: Fast with 128k output capability
- **Claude Haiku 3.5**: Fastest and most economical

Usage Examples
==============

Basic Chat
----------

1. Enter your API key
2. Type your message
3. Press Send or ``Ctrl+Enter``

Using System Prompts
--------------------

1. Click "System Prompt" button
2. Enter instructions like:

   - "You are a Python expert. Provide detailed code explanations."
   - "Respond in Spanish for all interactions."
   - "You are a creative writing assistant."

Attaching Files
---------------

1. Click the 📎 Attach button
2. Select image or text file
3. Add your question about the file
4. Send message

Exporting Conversations
-----------------------

1. Click Export or press ``Ctrl+S``
2. Choose format (Markdown, JSON, or Text)
3. Save to desired location

API Costs
=========

**⚠️ IMPORTANT COST DISCLAIMER ⚠️**

The client displays estimated costs based on September 2025 Anthropic pricing **for reference only**. These values are:

- **NOT AUTHORITATIVE** - Always refer to your Anthropic Console for actual billing
- **ESTIMATES ONLY** - Actual costs may vary significantly  
- **SUBJECT TO CHANGE** - Anthropic may update pricing at any time
- **NOT GUARANTEED ACCURATE** - Token counting is approximate

**YOU ARE SOLELY RESPONSIBLE FOR MONITORING YOUR ACTUAL API USAGE AND COSTS.** Always set spending limits in your Anthropic Console.

.. list-table:: API Pricing
   :header-rows: 1
   :widths: 40 30 30

   * - Model
     - Input (per 1M tokens)
     - Output (per 1M tokens)
   * - Claude Opus 4.1/4.0
     - $15.00
     - $75.00
   * - Claude Sonnet 4/3.7
     - $3.00
     - $15.00
   * - Claude Haiku 3.5
     - $0.80
     - $4.00

Roadmap
=======

Future enhancements under consideration:

- [ ] Dark mode theme
- [ ] Request cancellation/abort
- [ ] Temperature and top_p parameters
- [ ] Conversation branching
- [ ] Syntax highlighting for code blocks
- [ ] API request retry logic
- [ ] Conversation templates/presets
- [ ] Multi-conversation management

Contributing
============

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

License
=======

This project is licensed under the MIT License - see the `LICENSE <LICENSE>`_ file for details.

Acknowledgments
===============

- Built with `Anthropic's Claude API <https://docs.anthropic.com/>`_
- GUI framework: `tkinter <https://docs.python.org/3/library/tkinter.html>`_
- HTTP client: `requests <https://requests.readthedocs.io/>`_

Privacy & Data Handling
========================

**🔒 YOUR DATA STAYS ON YOUR DEVICE 🔒**

- **No Data Collection**: This application does NOT collect, transmit, or store any of your conversations, API keys, or personal data on external servers
- **Local Storage Only**: All data (conversations, settings, API keys) is stored locally on your device in platform-appropriate directories
- **Direct API Communication**: The app communicates directly with Anthropic's API - no intermediary servers
- **Open Source**: Full source code is available for inspection - verify our privacy claims yourself
- **No Analytics**: No usage tracking, telemetry, or analytics are collected
- **No Network Requests**: Except to Anthropic's official API endpoints for chat functionality

**Your privacy is paramount. This tool is designed to be a secure, private interface to Claude API.**

Important Disclaimers
=====================

**⚠️ LEGAL DISCLAIMERS ⚠️**

- **Independent Project**: This software is NOT affiliated with, endorsed by, or officially connected to Anthropic in any way
- **No Warranty**: This software is provided "AS IS" without warranty of any kind, express or implied
- **User Responsibility**: You are solely responsible for your API usage, costs, and compliance with Anthropic's terms of service
- **Cost Estimates**: All cost calculations are estimates only and may be inaccurate - always monitor actual usage in your Anthropic Console
- **API Compliance**: Users must comply with all Anthropic usage policies and terms of service
- **Use at Your Own Risk**: The developers are not liable for any damages, costs, or issues arising from use of this software

Author
======

**Anthony Maio** (anthony.maio@gmail.com)

Passionate about AI/ML, software engineering, culture and leadership.

Currently seeking opportunities in AI/ML engineering. Feel free to reach out for collaboration or opportunities.

Support
=======

Support is limited and generally submitted through Github in the issues section.
If you find this tool useful, please consider:

- ⭐ Starring the repository
- 🐛 Reporting issues
- 💡 Suggesting new features
- 📄 Contributing improvements

----

**Note**: This is an independent project and is not affiliated with Anthropic. Always ensure you comply with Anthropic's `usage policies <https://www.anthropic.com/legal/aup>`_ when using the API.