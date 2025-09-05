from typing import Optional, Union
from langchain.llms.base import LLM
from langgraph.graph import StateGraph

from ..langchain import GenerateAnswerChain


class GenerateResponseNode:
    """
    Node that wraps GenerateAnswerChain functionality, which generates an answer based on a given prompt and rows of data.
    It uses the LLM to build a human-readable answer.

    This node connects to a Timbr server via the provided URL and token to generate contextual answers from query results using an LLM.
    """
    def __init__(
        self,
        llm: LLM,
        url: str,
        token: str,
        verify_ssl: Optional[bool] = True,
        is_jwt: Optional[bool] = False,
        jwt_tenant_id: Optional[str] = None,
        conn_params: Optional[dict] = None,
        debug: Optional[bool] = False,
        **kwargs,
    ):
        """
        :param llm: An LLM instance or a function that takes a prompt string and returns the LLM’s response
        :param url: Timbr server url
        :param token: Timbr password or token value
        :param verify_ssl: Whether to verify SSL certificates (default is True).
        :param is_jwt: Whether to use JWT authentication (default is False).
        :param jwt_tenant_id: JWT tenant ID for multi-tenant environments (required when is_jwt=True).
        :param conn_params: Extra Timbr connection parameters sent with every request (e.g., 'x-api-impersonate-user').
        """
        self.chain = GenerateAnswerChain(
            llm=llm,
            url=url,
            token=token,
            verify_ssl=verify_ssl,
            is_jwt=is_jwt,
            jwt_tenant_id=jwt_tenant_id,
            conn_params=conn_params,
            debug=debug,
            **kwargs,
        )


    def run(self, state: dict) -> dict:
        sql = state.get("sql", "")
        rows = state.get("rows", "")
        prompt = state.get("prompt", "")

        return self.chain.invoke({ "prompt": prompt, "rows": rows, "sql": sql })


    def __call__(self, state: dict) -> dict:
        return self.run(state)

