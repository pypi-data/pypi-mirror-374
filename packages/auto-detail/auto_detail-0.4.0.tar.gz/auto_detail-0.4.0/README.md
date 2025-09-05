# auto-detail

An AI powered CLI for automatically detailing software development projects.

## Features

- **Simple Detailing**: Quickly record notes about your work from the command line.
- **AI-Powered Commit Messages**: Generate well-structured commit messages based on your recorded details.
- **Local Storage**: All details are stored locally in simple YAML files.

## Installation

1.  **Install tool:**
    ```bash
    pip install auto_detail
    ```

2.  **Set up your environment:**
    Create a Google Gemini API key. This is required for using the tool. A free tier is available and will usually suffice.
    ```
    auto_detail set_key GEMINI_API_KEY
    ```

## Usage

All commands are run through the `auto_detail` CLI entrypoint.

### Create a New Detail
The `new` command is your primary tool for writing notes with AI to summarize your changes.
```bash
auto_detail
``` 
or
```bash
auto_detail new
```
This creates a timestamped YAML file in the `.detail/notes/` directory containing your note. 

### View Details
To see a list of all recorded details:
```bash
auto_detail list
```
