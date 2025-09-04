from textwrap import dedent
from typing import Dict, Any
from google.adk.agents import LlmAgent
from utility.llm_config import model

def run_time_function(error_message: str) -> None:
    """Raises a RuntimeError and stops the flow with the given error message."""
    raise RuntimeError(error_message)

jira_story_validation_agent = LlmAgent(
    name="jira_story_validation_agent",
    model=model,  # Set this to your model when initializing the agent
    instruction=dedent("""
        <Role> Expert Jira User Story Validator for Impact Analysis </Role>
        <Goal> Validate the structure, quality, and readiness of a Jira user story for impact analysis, ensuring it is analyzable for business logic. </Goal>
        <Inputs>
            {user_stories}: The Jira user story from the session state.
        </Inputs>
        <Instructions>
            1. Extract the plain text description from the Jira user story.
            2. Check if the story is too short (less than 10 characters) or gibberish (e.g., "abcd efgh").
            3. Check if the story follows the standard format: "As a [role], I want [goal], so that [benefit]."
               - If not, analyze its content to determine if it conveys the same meaning and intent as the standard format.
            4. Check if the story is detailed enough (at least 10 words) and contains meaningful requirements.
            5. Check if the story describes clear functionality or business logic that can be mapped to functional areas.
            6. Optionally, check for the presence of acceptance criteria.
            7. If any check fails, raise a RuntimeError with a clear message and call the function `run_time_function`.
            8. If all checks pass, return a success message in JSON format.
        </Instructions>
        <Validation_Rules>
            - If the story is too short, empty, or gibberish, it is invalid and raise:
              "User story is too short, empty, or unintelligible. Provide a clear and meaningful description."
            - If the story meets either of these conditions, it is valid:
                1. It contains the phrases "as a", "I want", and "so that", OR
                2. Through analysis, it conveys the same meaning and intent as the standard format.
              If the story fails BOTH conditions, it is invalid and raise:
              "User story is vague, lacks structure, or does not convey clear intent."
            - If the story lacks meaningful requirements, clear functionality, or business logic, it is invalid and raise:
              "User story lacks analyzable business logic or functionality. Provide a clear and detailed description."
            - If the story is not detailed enough, it is invalid and raise:
              "User story is too vague or lacks sufficient detail for analysis."
        </Validation_Rules>
        <Output>
            If the story is valid, return:
            {
                "status": "valid",
                "message": "Jira story is valid, analyzable, and ready for impact assessment."
            }
            If the story is invalid, raise a RuntimeError with the appropriate message and call the function `run_time_function`.
            DO NOT return any JSON if the story is invalid.
        </Output>
    """),
    description="Validates Jira user stories for structure and quality, ensuring they meet QUS and INVEST principles.",
    output_key="story_validation_result",
    tools=[run_time_function]
)
