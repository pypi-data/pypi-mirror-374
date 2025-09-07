# LLM Context Builder: Focused Project Context for Large Language Models

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A powerful Python package designed to intelligently select, format, and present relevant project files and directory structure as context for Large Language Models (LLMs). Avoid token limits, reduce noise, and get more accurate, actionable responses from your AI assistant.

---

### 🌟 Why Use This?

Working with LLMs for code-related tasks is incredible, but they often struggle with:

1.  **Token Limits:** Sending an entire codebase is impossible and wasteful.
2.  **Information Overload:** Even if possible, too much irrelevant code confuses the model.
3.  **Lack of Structure:** Raw file dumps lack the directory context a human developer would have.

**LLM Context Builder** solves these problems by allowing you to:
*   **Precisely select** the files, folders, or specific line ranges you want to include.
*   **Automatically ignore** irrelevant files (like `node_modules` or build artifacts) using powerful ignore rules (including `.gitignore`).
*   **Provide a clear project overview** with an automatically generated directory tree.
*   **Format output** in easily parsable Markdown or JSON.

This results in **more focused, relevant, and accurate responses** from your LLM, helping you code faster and more effectively.

---

### 🚀 Getting Started

1.  **Installation:**
    Install `ctxctx` directly from PyPI:
    ```bash
    pip install ctxctx
    ```
    Alternatively, if cloning the repository for development:
    ```bash
    git clone https://github.com/gkegke/ctxctx.git
    cd llm-context-builder
    # Install with poetry (recommended for development)
    poetry install --with dev
    ```

2.  **Basic Usage:**
    Once installed, you can use the `ctxctx` command directly from your terminal in any project directory:
    ```bash
    ctxctx
    ```
    This will generate `prompt_input_files.md` and `prompt_input_files.json` containing only the directory tree of your project, up to a default depth of 3.

---

### 📖 Table of Contents

- [LLM Context Builder: Focused Project Context for Large Language Models](#llm-context-builder-focused-project-context-for-large-language-models)
    - [🌟 Why Use This?](#-why-use-this)
    - [🚀 Getting Started](#-getting-started)
    - [📖 Table of Contents](#-table-of-contents)
    - [✨ Key Features \& Usage Examples](#-key-features--usage-examples)
      - [1. Basic Usage: Include Directory Tree](#1-basic-usage-include-directory-tree)
      - [2. Including Specific Files \& Folders](#2-including-specific-files--folders)
      - [3. Ignoring Files \& Folders](#3-ignoring-files--folders)
      - [4. Force Including Files \& Folders (Override Ignores)](#4-force-including-files--folders-override-ignores)
      - [5. Targeting Specific Line Ranges](#5-targeting-specific-line-ranges)
      - [6. Using Glob Patterns for Flexible Selection](#6-using-glob-patterns-for-flexible-selection)
      - [7. Passing Arguments from a File](#7-passing-arguments-from-a-file)
      - [8. Pre-defined Context Profiles](#8-pre-defined-context-profiles)
      - [9. Output Formats (Markdown \& JSON)](#9-output-formats-markdown--json)
      - [10. Dry Run Mode](#10-dry-run-mode)
      - [11. Discovering Files with --list-files](#11-discovering-files-with---list-files)
    - [⚙️ Configuration](#️-configuration)
    - [🪵 Logging Configuration](#-logging-configuration)
      - [Console Output](#console-output)
      - [File-based Logging](#file-based-logging)
      - [Benefits for CI/CD](#benefits-for-cicd)
    - [🤝 Contributing](#-contributing)
    - [📄 License](#-license)

---

### ✨ Key Features & Usage Examples

The tool outputs its results into `prompt_input_files.md` (Markdown) and `prompt_input_files.json` (JSON) by default, based on the `OUTPUT_FORMATS` configuration.

#### 1. Basic Usage: Include Directory Tree

The simplest way to get context is just to include your project's directory structure. This gives the LLM a high-level overview of your project's layout, which is often very helpful.

```bash
ctxctx
```
This will generate `prompt_input_files.md` and `prompt_input_files.json` containing only the directory tree of your project, up to a default depth of 3.

#### 2. Including Specific Files & Folders

The most common use case is to provide the content of a few specific files or all files within a specific folder.

*   **Include a single file:**
    ```bash
    ctxctx src/main.py
    ```
*   **Include multiple files:**
    ```bash
    ctxctx src/utils.js README.md
    ```
*   **Include all files within a folder (recursively, up to `SEARCH_MAX_DEPTH`):**
    ```bash
    ctxctx config/
    ```
*   **Combine files and folders:**
    ```bash
    ctxctx tests/backend/ src/data_models.py
    ```

#### 3. Ignoring Files & Folders

Crucial for large projects! The tool uses a robust ignore system to ensure you don't send irrelevant or sensitive files to the LLM.

*   **Automatic Gitignore:** By default, the script respects your project's `.gitignore` file.
*   **Built-in Ignores:** Common build artifacts, temporary files, and environment directories (`node_modules`, `__pycache__`, `.venv`, `.git`, `.DS_Store`, etc.) are ignored automatically.
*   **Additional Ignore Files:** The script also looks for other common ignore files like `.dockerignore`, `.npmignore`, and `.eslintignore` defined in `ADDITIONAL_IGNORE_FILENAMES`.
*   **ctxctx-Specific Ignores:** The tool automatically ignores its own configuration and output files (like `.ctxctx.yaml`, the `.ctxctx_cache/` directory, `prompt_input_files.md`, and `prompt_input_files.json`) by default. These are embedded directly in the tool's core configuration's `EXPLICIT_IGNORE_NAMES`. You can always add more explicit ignore patterns to your `.ctxctx.yaml` file if needed.

#### 4. Force Including Files & Folders (Override Ignores)

Sometimes, you want to include a file or folder that is normally ignored by `ctxctx`'s default rules, `.gitignore`, or your custom ignore rules in `.ctxctx.yaml`. The "force include" feature allows you to explicitly override these ignore rules for specific paths.

*   **Syntax:** Prefix the file or folder path (or glob pattern) with `force:`.
    *   Example: `ctxctx 'force:path/to/file.js'`
*   **How it works:** When `ctxctx` encounters a query starting with `force:`, it marks that path as "force included". During processing, if a file matches *any* ignore rule, `ctxctx` first checks if it's explicitly force-included. If it is, the file will be included in the context, regardless of other ignore patterns.

*   **Important Nuance for Simple Filenames:**
    When using `force:` followed by a *simple filename* (i.e., no directory separators like `/` or `\\`, and no glob wildcards like `*` or `?`), `ctxctx` will **only look for that file directly in the project's root directory. If you want to force-include a simple filename that resides in a subdirectory, you must specify its full path or a glob pattern that includes its path (e.g., `force:src/config.py`).** This prevents unintended inclusion of identically named files deep within subdirectories, which is particularly useful for project-level files like `LICENSE` or `.gitignore`.

    *   **Example: `force:.gitignore`**
        If you have `/project/.gitignore` and `/project/frontend/.gitignore`, `ctxctx 'force:.gitignore'` will **only** include `/project/.gitignore`. If you wanted the one in `frontend/`, you would need to specify its path: `ctxctx 'force:frontend/.gitignore'`.

    *   **Example: `force:README.md`**
        If you have `README.md` at the root and `docs/README.md`, `ctxctx 'force:README.md'` will **only** include the root `README.md`.

    *   This specific root-only behavior **does not apply** if your `force:` query includes directory separators (e.g., `force:src/config.py`) or glob patterns (e.g., `force:*.log`). In those cases, the search remains recursive up to `SEARCH_MAX_DEPTH`, and force-include simply overrides ignore rules wherever the pattern matches.

*   **Examples:**
    *   **Force include a specific log file:**
        ```bash
        ctxctx 'force:debug.log'
        ```
        (Even if `*.log` is in your `.gitignore` or `debug.log` is in your `.ctxctx.yaml` `EXPLICIT_IGNORE_NAMES`, it will be included. If `debug.log` only exists in a subdirectory, this command will *not* find it, due to the nuance described above.)

    *   **Force include a file inside an ignored directory:**
        ```bash
        ctxctx 'force:node_modules/my_custom_module/index.js'
        ```
        (Normally `node_modules` is ignored, but this specific file will be included. This is a path-specific query, so it searches deeply.)

    *   **Force include all build artifacts (using a glob):**
        ```bash
        ctxctx 'force:build/**/*.js'
        ```
        (If your `build` directory is typically ignored, this will include all JavaScript files within it. This is a glob query, so it searches deeply.)

    *   **Combine force-include with line ranges:**
        ```bash
        ctxctx 'force:temp/sensitive_data.py:10,20'
        ```
        (Includes only lines 10-20 from `sensitive_data.py`, even if `temp/` is ignored. This is a path-specific query, so it searches deeply.)

This feature provides granular control, ensuring that critical files are always part of your LLM context, even if they would otherwise be filtered out.

#### 5. Targeting Specific Line Ranges

For very precise context, you can include one or more specific ranges of lines from a file. This is perfect for focusing on a few key sections of code for debugging or refactoring. The output will clearly mark the included line ranges and indicate where content has been omitted.

*   **Syntax:** `filepath:start1,end1:start2,end2...` (lines are 1-indexed and inclusive).
*   **Example (Single Range):**
    ```bash
    ctxctx 'src/api/user_routes.py:100,150'
    ```
    This will include lines 100 through 150 from `src/api/user_routes.py`.

*   **Example (Multiple Ranges):**
    ```bash
    ctxctx 'src/data_processor.py:20,45:200,215'
    ```
    This will include lines 20-45 and 200-215 from the same file, with a comment indicating the omitted lines in between.

#### 6. Using Glob Patterns for Flexible Selection

Glob patterns provide a powerful way to select multiple files based on wildcards.

*   **Syntax:** Standard Unix-style glob patterns (e.g., `*.py`, `src/**/*.js`). Remember to quote patterns to prevent shell expansion.
*   **Example:**
    *   **All Python files:**
        ```bash
        ctxctx '*.py'
        ```
    *   **All JavaScript or TypeScript files within `src/` and its subdirectories:**
        ```bash
        ctxctx 'src/**/*.{js,ts}' # (Note: Shell might expand {js,ts}, quote carefully or run in a compatible shell)
        # Safer alternative for cross-platform (multiple arguments):
        ctxctx 'src/**/*.js' 'src/**/*.ts'
        ```
    *   **All Markdown files in the root or `docs/` folder:**
        ```bash
        ctxctx '*.md' 'docs/*.md'
        ```

#### 7. Passing Arguments from a File

For very long or complex `ctxctx` commands, or for commands you use frequently, you can store your queries and flags in a text file and pass that file to `ctxctx`. This helps keep your terminal commands clean and makes them easily repeatable.

*   **Syntax:** `ctxctx @filename`
*   **How it works:** `ctxctx` will read each line from the specified file as if it were a separate command-line argument. Lines starting with `#` are treated as comments and ignored.

*   **Example `my_queries.txt`:**
    ```
    # This is a comment, it will be ignored
    src/main.py
    tests/unit/test_config.py:10,25:50,60
    '*.md'
    docs/api/
    --profile backend_dev
    ```
*   **Usage:**
    ```bash
    ctxctx @my_queries.txt
    ```
    This command would be equivalent to running:
    ```bash
    ctxctx src/main.py 'tests/unit/test_config.py:10,25:50,60' '*.md' docs/api/ --profile backend_dev
    ```

#### 8. Pre-defined Context Profiles

For common tasks, you can define **profiles** within your main `.ctxctx.yaml` file to create reusable context definitions. Profiles now use a powerful funnel-based system:

1.  **`include`**: A list of glob patterns that defines the initial set of files.
2.  **`queries`**: (Optional) Ad-hoc queries (like specific files, line ranges, or `force:` includes) are added to the set.
3.  **`exclude`**: (Optional) A list of glob patterns that removes files from the final set.

This allows you to build broad contexts with `include` and then precisely refine them with `exclude` and `queries`.

1.  **Define Profiles in your `.ctxctx.yaml` file** in your project's root directory:
    ```yaml
    # .ctxctx.yaml
    ROOT: .
    OUTPUT_FILE_BASE_NAME: prompt_input_files
    OUTPUT_FORMATS:
    - md
    - json
    TREE_MAX_DEPTH: 3
    # ... other global settings ...

    profiles: # Profiles are now a top-level key in .ctxctx.yaml
      backend_api:
        description: "Core backend API files, excluding tests and configs."
        include:
          - 'src/server/**/*.py'  # All python files under src/server
        exclude:
          - 'src/server/tests/**'   # Exclude the test subdirectory
          - 'src/server/config.py' # Exclude the config file
        queries:
          - 'requirements.txt'      # Explicitly add the requirements file

      frontend_component:
        description: "Focus on a specific component, its styles, and tests."
        include:
          - 'src/components/UserProfile/**' # All files for the component
        exclude:
          - 'src/components/UserProfile/**/*.snap' # Exclude snapshots
        # Override a global config setting just for this profile
        tree_max_depth: 4

      refactor_task:
        description: "A specific refactoring task with precise line numbers."
        queries:
          # Use 'queries' when you only need a few specific files/ranges
          - 'src/data/processor.py:10,45:100,120'
          - 'src/utils/helpers.py:1,30'
          - 'tests/test_processor.py'
    ```

2.  **Use a profile:**
    ```bash
    ctxctx --profile backend_api
    ctxctx --profile refactor_task
    ```
    You can also combine profiles with additional ad-hoc queries from the command line:
    ```bash
    ctxctx --profile frontend_component 'public/index.html'
    ```

#### 9. Output Formats (Markdown & JSON)

The tool generates two output files by default (`prompt_input_files.md` and `prompt_input_files.json`) to give you flexibility depending on what your LLM prefers or how you want to review the context.

*   **Markdown (`.md`):** Human-readable, includes directory tree, and uses Markdown code blocks with syntax highlighting hints for file contents. Great for reviewing the context yourself before sending it, or for models that prefer structured text.
*   **JSON (`.json`):** Machine-readable structured data. Contains the directory tree as a string and an array of file objects, each with path, content, and any line/function details. Ideal for programmatic use or models that perform better with structured JSON input.

You can configure which formats are generated in your `.ctxctx.yaml` file (or via a profile).

#### 10. Dry Run Mode

Test your queries and configurations without writing any files. The full output will be printed directly to your console.

```bash
ctxctx --dry-run 'src/config.py' '*.md'
```

#### 11. Discovering Files with --list-files

When you need to select from a large number of files, the `--list-files` command simplifies the process. It prints a clean, sorted list of all files that `ctxctx` can see after applying all ignore rules (from `.gitignore`, `.ctxctx.yaml` `EXPLICIT_IGNORE_NAMES`, etc.).

Its primary use is to generate an **argument file** that you can edit and pass back to `ctxctx`.

*   **How it works:**
    1.  Generate a list of all potential files. The command directs logs to `stderr`, so you can safely redirect the output.
        ```bash
        ctxctx --list-files > my_context.txt
        ```
    2.  Open `my_context.txt` in your editor. Comment out (`#`) or delete the lines for files you wish to exclude.
    3.  Feed the curated list back into `ctxctx` using the `@` prefix.
        ```bash
        ctxctx @my_context.txt
        ```

*   **Combining with Profiles:** You can also use it with profiles to see exactly what files a profile includes, providing a great starting point for a more specific context.
    ```bash
    ctxctx --profile backend_api --list-files > backend_files.txt
    # Now edit backend_files.txt and run:
    ctxctx @backend_files.txt
    ```

---

### ⚙️ Configuration

The tool's behavior can be customized by creating a `.ctxctx.yaml` file in your project's root directory. Any values defined in this file will override the tool's defaults. Additionally, profiles can override these global settings.

Key configurable options include:

*   `ROOT`: The base directory for your project (defaults to `.` - current directory).
*   `OUTPUT_FILE_BASE_NAME`: Base name for output files (e.g., `prompt_input_files`).
*   `OUTPUT_FORMATS`: List of desired output formats (`markdown`, `json`).
*   `TREE_MAX_DEPTH`: Maximum recursion depth for the directory tree view.
*   `TREE_EXCLUDE_EMPTY_DIRS`: If `true`, empty directories (after applying ignore rules) will not be included in the tree.
*   `SEARCH_MAX_DEPTH`: Maximum recursion depth for file content search.
*   `MAX_MATCHES_PER_QUERY`: Max number of files a single query can return before an error is raised (prevents accidental large inclusions).
*   `EXPLICIT_IGNORE_NAMES`: A set of exact file/folder names or relative paths to always ignore. **This now includes the tool's internal output and cache files by default.** You can add your own custom ignore names here.
*   `SUBSTRING_IGNORE_PATTERNS`: A list of substrings that, if found anywhere in a file's relative path, will cause it to be ignored.
*   `ADDITIONAL_IGNORE_FILENAMES`: List of other ignore files (e.g., `.dockerignore`) to load in addition to `.gitignore`.
*   `DEFAULT_CONFIG_FILENAME`: The name of the main configuration file (defaults to `.ctxctx.yaml`).
*   `USE_GITIGNORE`: Boolean to enable/disable `.gitignore` integration.
*   `GITIGNORE_PATH`: Relative path to your main `.gitignore` file.
*   `USE_CACHE`: Boolean to enable/disable caching of the project's file list.

---

### 🪵 Logging Configuration

`ctxctx` provides flexible logging options to help you debug issues, monitor execution, and capture detailed output, especially useful in automated environments like CI/CD.

#### Console Output

By default, `ctxctx` logs informational messages to your console (`stdout`).

*   **Enable Debug Mode:** Use the `--debug` flag to increase the verbosity of console output, showing detailed debugging information.

    ```bash
    ctxctx --debug src/main.py
    ```

#### File-based Logging

For persistent logs or detailed analysis, you can direct all logging output to a file.

*   **Log to a File:** Use the `--log-file <path>` argument to write all logs (including DEBUG level) to the specified file. This is highly recommended for CI/CD pipelines or when running `ctxctx` in non-interactive scripts, as it ensures all details are captured without relying on console output.

    ```bash
    # Log all output to ctxctx.log at DEBUG level
    ctxctx src/cli.py --log-file ctxctx.log

    # Combine with other arguments
    ctxctx 'src/**/*.py' --profile backend_dev --log-file debug_output.txt
    ```

#### Benefits for CI/CD

The `--log-file` argument is invaluable for Continuous Integration/Continuous Deployment (CI/CD) pipelines:

*   **Persistent Records:** Capture full execution logs for every build, even if the pipeline fails, allowing for post-mortem analysis.
*   **Detailed Debugging:** Provide engineers with comprehensive information for troubleshooting build issues or unexpected `ctxctx` behavior within automated workflows.
*   **Clean Console:** Avoids flooding the CI/CD console output with verbose details, keeping the primary build logs focused.
*   **Auditing:** Maintain an auditable trail of what context was generated for specific code changes.

---

### 🤝 Contributing

Contributions are welcome! If you have ideas for new features, improvements, or bug fixes, please open an issue or submit a pull request.

Areas for future improvement include:
*   **Git Integration:** Automatically include files based on Git status (e.g., staged, modified).
*   **Code-aware Extraction:** Use AST (Abstract Syntax Tree) parsing to extract specific functions, classes, or methods from code files.
*   **Advanced Ignore Logic:** More robust `.gitignore` parsing, including support for negation patterns (`!`).
*   **Interactive Mode:** A CLI mode for interactively selecting files and folders to include in the context.


Performance improvements being considered IF real world usage calls for it (increases codebase complexity):
*   **Content Change Detection for Cache:** Currently, the cache only tracks file *list* changes based on config/ignore file mtimes. Adding content hashing could make cache invalidation more precise.
*   **Parallel File Content Reading**

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
