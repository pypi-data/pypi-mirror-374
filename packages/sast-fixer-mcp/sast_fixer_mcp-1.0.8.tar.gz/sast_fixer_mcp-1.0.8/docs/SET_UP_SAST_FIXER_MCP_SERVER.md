# SAST_FIXER MCP Server

A Model Context Protocol (MCP) server that provides dedicated handling of Static Application Security Testing (SAST) reports. It includes capabilities for parsing DOCX reports, tracking vulnerability remediation statuses, and exporting comprehensive fix reports. Seamless integration with Zhanlu AI Programmer enables automated remediation for vulnerabilities identified in SAST processes.

### Available Tools


* **convert_sast_docx_to_json** - Converts SAST reports from DOCX format to JSON.

  * `file_path` (string, required): Path to the SAST report DOCX file.

* **get_pending_vulnerability_json_files** - Retrieves all pending vulnerability JSON files (`_new.json`) from the `.scanissuefix` directory.

* **generate_csv_report** - Generates a CSV report from all resolved vulnerability JSON files (`_finished.json`).

## Installation

### Prerequisites

* **Python 3.10 or higher** is required. Verify your Python version:

```bash
python --version  # or python3 --version
```

* Check if you have the appropriate Python environment installed:

```bash
which python  # or which python3
```


### Install Python

If you do not have Python installed or your version is not match the prerequisites, it's recommended to install the most stable version of Python 3.12 using the following direct download links:

* **Mac**: [Download Python 3.12 for macOS](https://www.python.org/ftp/python/3.12.10/python-3.12.10-macos11.pkg)

  * For silent installation on macOS:

  ```bash
  sudo installer -pkg /path/to/python-3.12.4-macos11.pkg -target /
  ```

* **Windows**: [Download Python 3.12 for Windows](https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe)

  * For silent installation on Windows, run:

  ```bash
  python-3.12.4-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
  ```


### Upgrade Python

If your current Python version does not meet the required standard, download and install the recommended Python 3.12 version using the above links. Ensure your system's PATH points to the new Python installation.

### Using PIP

download [sast_fixer_mcp-0.1.2-py3-none-any.whl](https://eos-huhehaote-1.cmecloud.cn/dsp-ecpan-zone3/00e0f334d0944310a203e2d001c80efa?response-content-disposition=attachment%3Bfilename%3D%22sast_fixer_mcp-0.1.2-py3-none-any.whl%22&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250701T095018Z&X-Amz-SignedHeaders=host&X-Amz-Expires=86400&X-Amz-Credential=R2V91UGDM1447A0VTB86%2F20250701%2Fdefault%2Fs3%2Faws4_request&X-Amz-Signature=eb6fd18e907ba53db18e48b6313aed77a685790d17682bb7e43e22bc0ca31542), 
you can install `SAST_FIXER_MCP` via pip:

```bash
pip install -U sast_fixer_mcp-0.1.2-py3-none-any.whl
```

## Configuration

### Configure for VS Code

Add to your VS Code mcp_settings.json file:

For manual installation, add the following JSON block to your User Settings (JSON) file in VS Code. You can do this by pressing `Ctrl + Shift + P` and typing `Preferences: Open User Settings (JSON)`.

Optionally, you can add it to a file called `.vscode/mcp.json` in your workspace. This will allow you to share the configuration with others.

> Note that the `mcp` key is needed when using the `mcp.json` file.


<details>
<summary>Using pip installation</summary>
In certain Conda environments or when environment variables and IDE-specific Python interceptors differ, specifying "command": "python" might be incorrect and cause issues such as "No module named sast_fixer_mcp" or "MCP error -32000: Connection closed". To prevent such problems, use which python to determine the accurate Python executable path and update the configuration accordingly.

For example:

```bash
which python
/opt/miniconda3/envs/agent_py312/bin/python
```

```json
{
  "mcpServers": {
    "sast-fixer-mcp": {
      "command": "python",
      "args": ["-m", "sast_fixer_mcp"],
      "alwaysAllow": [
        "convert_sast_docx_to_json",
        "get_pending_vulnerability_json_files",
        "generate_csv_report"
      ],
      "timeout": 1800,
      "disabled": false
    }
  }
}
```
</details>