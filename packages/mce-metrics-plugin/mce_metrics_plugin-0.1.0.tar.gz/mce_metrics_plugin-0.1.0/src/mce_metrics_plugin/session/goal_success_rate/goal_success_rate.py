from typing import List, Optional
from metrics_computation_engine.metrics.base import BaseMetric
from metrics_computation_engine.models.eval import BinaryGrading
from metrics_computation_engine.models.session import SessionEntity

GOAL_SUCCESS_RATE_PROMPT = """
    You are an evaluator of Goal Success Rate.

    You will be given a QUERY and a RESPONSE, and (optionally) a Reference Answer that gets a score of 1. Evaluate how well the RESPONSE demonstrates Goal Success Rate.

    The QUERY contains the GOAL that the user is requesting the assistant to achieve.

    Here is the evaluation criteria to follow: (1) Does the response correctly correspond to what the user has asked for in the goal? (2) Does the response fulfill all expectations specified in the goal? (3) If the assistant is not able to achieve the goal, does it state the reasons for why it cannot?

    Scoring Rubric:
        1: the response is accurate and correspond to what the user asked for in the goal.
        0: the Assistant fails to achieve the goal specified by the user.

    QUERY: {query} Optional Reference Answer (Score 1): {ground_truth} RESPONSE to evaluate: {response}
"""


class GoalSuccessRate(BaseMetric):
    REQUIRED_PARAMETERS = {"GoalSuccessRate": ["workflow_data"]}

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
        query = session.workflow_data.get("query", "") if session.workflow_data else ""
        response = (
            session.workflow_data.get("response", "") if session.workflow_data else ""
        )
        workflow_span_ids = (
            [span.span_id for span in session.workflow_spans]
            if session.workflow_spans
            else []
        )

        ground_truth = "No ground truth available"  # TODO: Add dataset lookup

        prompt = GOAL_SUCCESS_RATE_PROMPT.format(
            query=query, response=response, ground_truth=ground_truth
        )

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
