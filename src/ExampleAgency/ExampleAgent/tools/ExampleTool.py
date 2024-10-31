from agency_swarm.tools import BaseTool
from pydantic import Field
import os

ACCOUNT_ID = "MY_ACCOUNT_ID"
API_KEY = os.getenv("MY_API_KEY")


class ExampleTool(BaseTool):
    """
    A brief description of what the custom tool does.
    The docstring should clearly explain the tool's purpose and functionality.
    It will be used by the agent to determine when to use this tool.
    """

    # Define the fields with descriptions using Pydantic Field
    example_field: str = Field(
        ...,
        description="Description of the example field, explaining its purpose and usage for the Agent.",
    )

    def run(self):
        """
        The implementation of the run method, where the tool's main functionality is executed.
        This method should utilize the fields defined above to perform the task.
        Docstring is not required for this method and will not be used by the agent.
        """
        # Your custom tool logic goes here
        # do_something(self.example_field, API_KEY, ACCOUNT_ID)

        # Return the result of the tool's operation as a string
        return "Result of ExampleTool operation"


if __name__ == "__main__":
    tool = ExampleTool(example_field="Hello, world!")
    print(tool.run())
