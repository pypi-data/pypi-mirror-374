from codemie_test_harness.tests.enums.tools import PluginTool
from codemie_test_harness.tests.utils.constants import TESTS_PATH

list_files_plugin_tools_test_data = [
    (
        f"list files in the {TESTS_PATH} directory",
        f"""
            Here is a list of files and directories in `{TESTS_PATH}`:

            - Files:
              - `.DS_Store`
              - `__init__.py`
              - `conftest.py`

            - Directories:
              - `__pycache__`
              - `assistant`
              - `e2e`
              - `enums`
              - `integrations`
              - `llm`
              - `providers`
              - `search`
              - `service`
              - `test_data`
              - `ui`
              - `utils`
              - `workflow`
        """,
        PluginTool.LIST_FILES_IN_DIRECTORY,
    ),
    (
        "execute 'ls' command",
        f"""
            Here is a list of files and directories in `{TESTS_PATH}`:

            - Files:
              - `.DS_Store`
              - `__init__.py`
              - `conftest.py`

            - Directories:
              - `__pycache__`
              - `assistant`
              - `e2e`
              - `enums`
              - `integrations`
              - `llm`
              - `providers`
              - `search`
              - `service`
              - `test_data`
              - `ui`
              - `utils`
              - `workflow`
        """,
        PluginTool.RUN_COMMAND_LINE_TOOL,
    ),
    (
        "execute command: echo 'Test Message'. In the end return output of the command.",
        "Test Message",
        PluginTool.RUN_COMMAND_LINE_TOOL,
    ),
]

CREATE_READ_DELETE_FILE_TEST_DATA = {
    "create_file_prompt": "create a new {}.properties file with content {}=preview",
    "create_file_response": "I have successfully created the {}.properties file with the content {}=preview.",
    "git_command_prompt": "execute command: git add {}.properties and return if file was added to the staging area.",
    "git_command_response": "The file `{}.properties` has been added to the staging area.",
    "show_file_content_prompt": f"show the content of {TESTS_PATH}/{{}}.properties file",
    "show_file_content_response": "{}=preview",
    "remove_file_prompt": "execute command: git rm -f {}.properties",
    "remove_file_response": "The file `{}.properties` has been removed from the git repository.",
}
