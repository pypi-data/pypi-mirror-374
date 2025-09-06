from typing import List, Optional
from metrics_computation_engine.metrics.base import BaseMetric
from metrics_computation_engine.models.eval import BinaryGrading
from metrics_computation_engine.models.session import SessionEntity

INFORMATION_RETENTION_PROMPT = """
    You are an evaluator of Information Retention.

    You will be given multiple RESPONSES from different interactions. Evaluate how well the Assistant retains and recalls relevant information over time.

    Here is the evaluation criteria to follow: (1) Does the Assistant correctly remember and reference previously provided information? (2) Does the Assistant avoid forgetting key details or introducing inconsistencies in recalled information? (3) Is the recalled information applied appropriately in the responses?

    Scoring Rubric:
        1: The Assistant consistently retains and recalls information accurately across all interactions.
        0: The Assistant fails to retain or recall relevant information, leading to inaccuracies or contradictions.

    RESPONSES to evaluate: {responses}
"""


class InformationRetention(BaseMetric):
    """
    Measures how well information is retained across multiple interactions.
    """

    REQUIRED_PARAMETERS = {
        "InformationRetention": ["conversation_data", "workflow_data"]
    }

    def __init__(self, metric_name: Optional[str] = None):
        super().__init__()
        if metric_name is None:
            metric_name = self.__class__.__name__
        self.name = metric_name
        self.aggregation_level = "session"

    @property
    def required_parameters(self) -> List[str]:
        return self.REQUIRED_PARAMETERS

    def validate_config(self) -> bool:
        return True

    def init_with_model(self, model) -> bool:
        self.jury = model
        return True

    def get_model_provider(self):
        return self.get_default_provider()

    def create_model(self, llm_config):
        return self.create_native_model(llm_config)

    async def compute(self, session: SessionEntity):
        # Use workflow responses if available, fallback to conversation data
        responses = ""
        workflow_span_ids = []

        if session.workflow_data and session.workflow_data.get("responses"):
            responses = session.workflow_data["responses"]
            workflow_span_ids = (
                [span.span_id for span in session.workflow_spans]
                if session.workflow_spans
                else []
            )
        elif session.conversation_data:
            # Fallback to conversation data if no workflow responses
            responses = session.conversation_data.get("conversation", "")
            workflow_span_ids = (
                [span.span_id for span in session.agent_spans]
                if session.agent_spans
                else []
            )

        prompt = INFORMATION_RETENTION_PROMPT.format(responses=responses)

        if self.jury:
            score, reasoning = self.jury.judge(prompt, BinaryGrading)
            return self._create_success_result(
                score=score,
                reasoning=reasoning,
                span_ids=workflow_span_ids,
                session_ids=[session.session_id],
            )

        return self._create_error_result(
            error_message="No model available",
            span_ids=workflow_span_ids,
            session_ids=[session.session_id],
        )
