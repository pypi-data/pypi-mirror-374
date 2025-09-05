# Sphinx extension: NoteBook Execution Patterns

## Introduction

A Sphinx extension to execute Jupyter NoteBooks based on include and exclude patterns instead of only exclude patterns.

## Installation

To install the Sphinx-NB-Execution-Patterns extension, follow these steps:

**Step 1: Install the Package**

Install the `Sphinx-NB-Execution-Patterns` package using `pip`:
```
pip install sphinx-nb-execution-patterns
```

**Step 2: Add to `requirements.txt`**

Make sure that the package is included in your project's `requirements.txt` to track the dependency:
```
sphinx-nb-execution-patterns
```

**Step 3: Enable in `_config.yml`**

In your `_config.yml` file, add the extension to the list of Sphinx extra extensions:
```
sphinx: 
    extra_extensions:
        - sphinx_nb_execution_patterns
```

## Configuration

You can configure the extension in your `_config.yml` file. Here are the available options:

- `nb_execution_includepatterns`: A list of glob patterns to indicate notebooks that must be included for execution. Default is an empty list.
- `nb_execution_patterns_method`: Sets the method used when both include and exclude patterns are provided. Allowed values are:
  - `only_include` (default): Notebooks matching the include patterns are executed. All exclude patterns are ignored.
  - `only_exclude`: Notebooks matching the exclude patterns are excluded from execution, all other notebooks are executed. All include patterns are ignored. This method is equivalent to the default behavior of JupyterBook/Sphinx.
  - `exclude_include`: Notebooks matching the exclude patterns are excluded from execution, unless they also match the include patterns. All other notebooks are executed.
  - `include_exclude`: Notebooks matching the include patterns are executed, unless they also match the exclude patterns.

This extension will only have an effect if include patterns are provided.

> [!NOTE]
> Exclude patterns are supported by JupyterBook out-of-the-box. See the [JupyterBook documentation](https://jupyterbook.org/en/stable/content/execute.html#exclude-files-from-execution) for more details.
> Sphinx also supports exclude patterns natively. See the [Sphinx documentation](https://myst-nb.readthedocs.io/en/latest/computation/execute.html#exclude-notebooks-from-execution) for more details.
> If both the JupyterBook and Sphinx syntax are used, the Sphinx syntax will take precedence.

### Example Configuration

Here is an example configuration in `_config.yml` using both include and exclude patterns and JupyterBook syntax:

```yaml
execute:
  execute_notebooks: auto
  exclude_patterns:
  - "*NB1*"

sphinx:
  config:
    nb_execution_includepatterns:
      - "*sol.ipynb"
    nb_execution_patterns_method: "include_exclude"
```

Here is the same example configuration in `_config.yml` using Sphinx syntax:

```yaml
sphinx:
  config:
    nb_execution_mode: "auto"
    nb_execution_excludepatterns:
      - "*NB1*"
    nb_execution_includepatterns:
      - "*sol.ipynb"
    nb_execution_patterns_method: "include_exclude"
```

For the given example, all notebooks matching `*sol.ipynb` will be executed, unless they also match `*NB1*`.

If `nb_execution_patterns_method` is set to `only_include`, all notebooks matching `*sol.ipynb` will be executed, and the exclude pattern will be ignored.

If `nb_execution_patterns_method` is set to `only_exclude`, all notebooks matching `*sol.ipynb` will be excluded from execution, all other notebooks are executed, and the include pattern will be ignored.

If `nb_execution_patterns_method` is set to `exclude_include`, all notebooks matching `*NB1*` will be excluded from execution, unless they also match `*sol.ipynb`. All other notebooks will be executed.

## Contribute

This tool's repository is stored on [GitHub](https://github.com/TeachBooks/Sphinx-NB-Execution-Patterns). If you'd like to contribute, you can create a fork and open a pull request on the [GitHub repository](https://github.com/TeachBooks/Sphinx-NB-Execution-Patterns).

The `README.md` of the branch `Manual` is also part of the [TeachBooks manual](https://teachbooks.io/manual/intro.html).