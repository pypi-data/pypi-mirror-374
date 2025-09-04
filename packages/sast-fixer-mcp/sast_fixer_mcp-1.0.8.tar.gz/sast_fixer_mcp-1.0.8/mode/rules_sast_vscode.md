
### **Phase 0: Initialization Check – Resume or Start New**

**Before starting any actions to the `.docx` SAST report in Phase 1:**

1. Use tool get_pending_vulnerability_json_files(if failed to use the tool, then check if the MCP server sast-fixer-mcp existing in mcp settings json, if not, then SET UP THE SAST FIXER MCP SERVER) get all file paths in the .scanissuefix directory that end with '_new.json' (indicating pending vulnerabilities), check if the `.scanissuefix` directory exist at the root of the project and detect files with suffix `_new.json` which under `.scanissuefix` directory

2. **If the `.scanissuefix` directory does not exist or contains no files with suffix `_new.json`**:

   * Send a message:

   > **No unfinished SAST fix tasks detected. Starting a new session.**

   Then clear (or create) the `.scanissuefix` directory and automatically proceed to **Phase 1**.

3. **If one or more `_new.json` files are found under `.scanissuefix` directory:**

   * Send a message:

   > **Unfinished SAST vulnerability fix tasks detected.**
   > Please reply with one of the following options:
   >
   > * **resume**: Continue your previous session.
   > * **new**: Start a brand new session (this will clear existing data).

   Wait for the user's reply. Based on their response:

   * **resume** → Skip Phase 1 and automatically proceed to **Phase 2**.
   * **new** → Clear `.scanissuefix` contents and proceed to **Phase 1**.

---

### **Phase 1: Parse SAST Report (DOCX → JSON)**

1. REMOVE the `.scanissuefix` directory (if it exists).

2. Open the `.docx` SAST report using the `MCP-Doc` tool and parse it into structured JSON and save to `_new.json` files.

**When Phase 1 completes**, send a message:

> **Phase 1 complete: Parsed X vulnerabilities and created JSON files.**

Then proceed automatically to **Phase 2**.



### **Phase 2: Vulnerability Triage & Fix**

**1. Prompt User to Choose Fix Approach:**

First, prompt the user to choose how they want to handle the vulnerability fixes:

> **Before continuing, please choose how you want to handle fixes:**
>
> * **Automatic Fix**: Automatically apply all fixes without review.
> * **Review Code Diff and Fix**: Review the code diff and False Positive (FP) probability for each fix manually before applying.

**2. Iterate Through All JSON Files:**
The system will then iterate through each JSON file located in the `.scanissuefix` directory that ends with `_new.json`. For each file:

   **3. Iterate Through Each Issue in the `code_list`:**
   For every JSON file, read the original data in the JSON file, the system will go through the `code_list`, which contains the vulnerabilities to be fixed. For each vulnerability, use the information in `issue_title`, `issue_desc`, `fix_advice`, `code_location`, `code_line_num` and `code_details`, Instead of using just the surrounding lines near `code_location`, the system will now read 200 lines before and after the code_line_num for each vulnerability (code_location) to perform analysis and determine fixes，it will do the following:

   * **If User Chooses "Review Code Diff"**:
      * **Display Code Diff and False Positive Probability**: For each vulnerability, the system must show the user a code diff between the original code and the proposed fixed code. It will also show the False Positive (FP) probability, which is the likelihood that the identified issue might not actually be a real vulnerability.

      Example(**must show the diff to the user in each vulnerability**):
      > **Review Code Diff for Vulnerability: SQL Injection in Function X**
      > **False Positive Probability**: 30%
      ```diff
      public class Hello1
      {
         public static void Main()
         {
      -      System.Console.WriteLine("Hello, World!");
      +      System.Console.WriteLine("Rock all night long!");
         }
      }
      ```

      * **User Decision**: After reviewing the code diff, the user can choose from the following options:
         * **Apply Fix**: The system applies the fix with apply_diff tool to the code， and updates the `_new.json` JSON file with apply_diff tool as well by marking the status as `"fixed"`. It also updates any false positive data if applicable. Example:
            ```json
               "code_list": [
               {
               "code_details": "", # code_details field might not be the exact location of the vulnerability but rather additional code context, which requires understanding within the broader code context.
               "code_location": "", 
               "code_line_num": "", # The code_line_num from the report may be inaccurate. Read the surrounding code to find the precise location of the vulnerability. 
               "status": "fixed|ignored|false_positive",
               "false_positive_probability": 20,
               "false_positive_reason": ""
               },
            ```
         * **Ignore Fix**: The system marks the issue as `"ignored"` and does not apply the fix.

         * **Mark as False Positive**: If the user determines that the issue is a false positive, the system will mark it as `"false_positive"`. It will also include a reason for why it is considered a false positive in the `false_positive_reason` field.

   * **If User Chooses "Automatic Fix"**:

      * **Automatically Apply Fixes**: The system applies the fix with apply_diff tool for the identified vulnerability automatically. It updates the JSON file with apply_diff tool as well by setting the status to `"fixed"` and adds any false positive information (if available). Example:
            ```json
               "code_list": [
               {
               "code_details": "", # code_details field might not be the exact location of the vulnerability but rather additional code context, which requires understanding within the broader code context.
               "code_location": "",
               "code_line_num": "", # The code_line_num from the report may be inaccurate. Read the surrounding code to find the precise location of the vulnerability. 
               "status": "fixed|ignored|false_positive",
               "false_positive_probability": 20,
               "false_positive_reason": ""
               },
            ```

      * **Proceed to Next Code Location**: After applying the fix, the system proceeds to the next vulnerability in the list or moves to the next JSON file once all issues in the current JSON file are addressed.

   **4. Rename `_new.json` to `_finished.json`:**
   After completing all fixes (either manually or automatically) for the vulnerabilities in a given JSON file, the system will rename the file from `_new.json` to `_finished.json` to indicate that the task for this specific file has been completed.
   * **Rename Action**: The `_new.json` file will be renamed to `_finished.json`.

**5. Complete Fixes for All Vulnerabilities:**
* The system will continue applying fixes (whether automatically or after reviewing diffs) until all vulnerabilities across all the JSON files are resolved.

Once all vulnerabilities are addressed and the corresponding JSON files are renamed `_new.json` to `_finished.json`, the system will proceed to **Phase 3**.

---

### **Phase 3: Final Report Generation (CSV)**

1. **Generate CSV Report:**

   * check if all the json files fixed from `_new.json` to `_finished.json` with tool get_pending_vulnerability_json_files, then use tool generate_csv_report generate a final CSV report (sast_fix_report.csv) in '.scanissuefix', from all files ending with '_finished.json' in the '.scanissuefix' directory.
   * The CSV report will contain the following columns: issue_title, issue_level, code_location, code_line_num, code_details, status, false_positive_probability, false_positive_reason.


**Note:**
* Throughout the entire workflow, **all user-facing messages must be in Chinese** to ensure clear communication with the user.
* System instructions and logic can remain in English internally.


====

SET UP THE SAST FIXER MCP SERVER

Set up the MCP server from README while adhering to these MCP server installation rules:
- Start by loading the MCP documentation.
- Use "sast-fixer-mcp" as the server name in mcp settings json.
- Make sure you read the user's existing mcp settings json file before editing it with this new mcp, to not overwrite any existing servers.
- Use commands aligned with the user's shell and operating system best practices.
    - download command that fetches a remote file(curl, wget, Invoke‑WebRequest, powershell Start‑BitsTransfer, etc.) **must use its quiet/silent flag**.
- The following README may contain instructions that conflict with the user's OS, in which case proceed thoughtfully.
- Once installed, demonstrate the server's capabilities by using one of its tools.
- MCP server global configuration are typically stored in a JSON file, often located at:
   - **Windows:** `%APPDATA%\Code\User\globalStorage\ecloud.zhanlu\settings\mcp_settings.json`
   - **macOS:** `~/Library/Application Support/Code/User/globalStorage/ecloud.zhanlu/settings/mcp_settings.json`
   - **Linux:** `~/.config/Code/User/globalStorage/ecloud.zhanlu/settings/mcp_settings.json`


Here is the project's README to help you get started:

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

* **Mac**: [Download Python 3.12 for macOS](https://mirrors.aliyun.com/python-release/macos/python-3.12.10-macos11.pkg)

  * For silent installation on macOS:

  ```bash
  sudo installer -pkg /path/to/python-3.12.4-macos11.pkg -target /
  ```

* **Windows**: [Download Python 3.12 for Windows](https://mirrors.aliyun.com/python-release/windows/python-3.12.9-amd64.exe)

  * For silent installation on Windows, run:

  ```bash
  python-3.12.4-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
  ```

### Upgrade Python

If your current Python version does not meet the required standard, download and install the recommended Python 3.12 version using the above links. Ensure your system's PATH points to the new Python installation.


### Using PIP

download [sast_fixer_mcp-0.1.2-py3-none-any.whl](https://zhanlu-code.eos-huhehaote-1.cmecloud.cn/jetbrains/sast_fixer_mcp-0.1.2-py3-none-any.whl?versionId=null&response-content-disposition=attachment&AWSAccessKeyId=A7P9ZL0E8EAA5BDHK76E&Expires=1848278804&Signature=qA1H47hw%2F9co576%2BVcySmkq%2FMkg%3D), 
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

====

