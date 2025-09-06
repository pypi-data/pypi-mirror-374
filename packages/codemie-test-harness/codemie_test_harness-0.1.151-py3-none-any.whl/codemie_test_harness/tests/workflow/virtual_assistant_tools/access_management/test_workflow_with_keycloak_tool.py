import pytest

from codemie_test_harness.tests.enums.tools import AccessManagementTool
from codemie_test_harness.tests.test_data.keycloak_tool_test_data import (
    KEYCLOAK_TOOL_PROMPT,
    KEYCLOAK_TOOL_RESPONSE,
)
from codemie_test_harness.tests.utils.base_utils import get_random_name


@pytest.mark.regression
def test_workflow_with_virtual_assistant_with_keycloak_tool(
    keycloak_integration,
    workflow_with_virtual_assistant,
    workflow_utils,
    similarity_check,
):
    assistant_and_state_name = get_random_name()

    test_workflow = workflow_with_virtual_assistant(
        assistant_and_state_name,
        AccessManagementTool.KEYCLOAK,
        integration=keycloak_integration,
        task=KEYCLOAK_TOOL_PROMPT,
    )
    response = workflow_utils.execute_workflow(
        test_workflow.id, assistant_and_state_name
    )
    similarity_check.check_similarity(response, KEYCLOAK_TOOL_RESPONSE)
