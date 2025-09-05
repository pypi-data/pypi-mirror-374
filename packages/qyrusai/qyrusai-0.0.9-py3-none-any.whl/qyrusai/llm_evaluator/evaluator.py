from qyrusai.configs import Configurations
from typing import Optional, List, Union, Dict, Any
from urllib.parse import urljoin
from qyrusai._rest import AsyncHTTPClient, SyncHTTPClient
from qyrusai._types import (RAGRequest, MCPRequest, ScoreResponse,
                            BatchScoreResponse, EvaluationItem,
                            EvaluationDataset, EvaluationRequestUnion)


class AsyncLLMEvaluator:

    def __init__(self, api_key: str, base_url: str, gateway_token: str):
        self.api_key = api_key
        self.base_url = base_url
        self.gateway_token = gateway_token

    def _prepare_headers(self):
        """Prepare common headers for requests."""
        return {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + self.gateway_token,
            'Custom': self.api_key
        }

    def _process_request_data(
            self, request: Union[Dict, RAGRequest, MCPRequest]) -> Dict:
        """Convert request to dictionary format, handling both JSON dict and Pydantic models."""
        if isinstance(request, dict):
            return request
        elif hasattr(request, 'model_dump'):
            return request.model_dump()
        else:
            raise ValueError(
                "Request must be either a dictionary or a Pydantic model")

    async def evaluate(self,
                       context: str,
                       expected_output: str,
                       executed_output: List[str],
                       guardrails: Optional[str] = None) -> float:
        url = urljoin(self.base_url,
                      Configurations.getLLMEvaluatorContextPath("judge"))

        data = {
            "context": context,
            "expected_output": expected_output,
            "executed_output": executed_output,
            "guardrails": guardrails
        }

        headers = self._prepare_headers()
        async_client = AsyncHTTPClient()
        response = await async_client.post(url, data, headers)
        return response

    async def evaluate_rag(self, request: Union[Dict, RAGRequest]) -> Dict:
        """Evaluate a RAG (Retrieval-Augmented Generation) system."""
        # Validate and convert input
        if isinstance(request, dict):
            # Validate JSON input against RAGRequest schema
            validated_request = RAGRequest(**request)
            request_data = validated_request.model_dump()
        else:
            request_data = request.model_dump()

        url = urljoin(self.base_url,
                      Configurations.getLLMEvaluatorContextPath("score"))

        headers = self._prepare_headers()
        async_client = AsyncHTTPClient()
        response = await async_client.post(url, request_data, headers)
        return response

    async def evaluate_mcp(self, request: Union[Dict, MCPRequest]) -> Dict:
        """Evaluate an MCP (Model Context Protocol) tool-calling system."""
        # Validate and convert input
        if isinstance(request, dict):
            # Validate JSON input against MCPRequest schema
            validated_request = MCPRequest(**request)
            request_data = validated_request.model_dump()
        else:
            request_data = request.model_dump()

        url = urljoin(self.base_url,
                      Configurations.getLLMEvaluatorContextPath("score"))

        headers = self._prepare_headers()
        async_client = AsyncHTTPClient()
        response = await async_client.post(url, request_data, headers)
        return response

    async def evaluate_batch(
        self, requests: Union[List[Dict], List[EvaluationRequestUnion],
                              List[Union[Dict, EvaluationRequestUnion]]]
    ) -> Dict:
        """Evaluate a batch of RAG or MCP requests."""
        url = urljoin(self.base_url,
                      Configurations.getLLMEvaluatorContextPath("batch/score"))

        headers = self._prepare_headers()

        # Process and validate each request in the batch
        batch_data = []
        for req in requests:
            if isinstance(req, dict):
                # Try to determine if it's RAG or MCP based on presence of 'tools' field
                if 'tools' in req:
                    validated_req = MCPRequest(**req)
                else:
                    validated_req = RAGRequest(**req)
                batch_data.append(validated_req.model_dump())
            else:
                batch_data.append(req.model_dump())

        async_client = AsyncHTTPClient()
        response = await async_client.post(url, batch_data, headers)
        return response

    async def evaluate_dataset(
            self, dataset: Union[Dict, EvaluationDataset]) -> Dict:
        """Evaluate an entire dataset of mixed RAG/MCP evaluations."""
        # Validate and convert dataset
        if isinstance(dataset, dict):
            validated_dataset = EvaluationDataset(**dataset)
        else:
            validated_dataset = dataset

        requests = [item.data for item in validated_dataset.items]
        return await self.evaluate_batch(requests)

    async def get_app_summary(self, app_name: str, **query_params) -> dict:
        """Get application metrics summary."""
        url = urljoin(
            self.base_url,
            Configurations.getLLMEvaluatorContextPath(
                f"apps/{app_name}/summary"))

        headers = {
            'Authorization': "Bearer " + self.gateway_token,
            'Custom': self.api_key
        }

        async_client = AsyncHTTPClient()
        response = await async_client.get(url,
                                          params=query_params,
                                          headers=headers)
        return response


class SyncLLMEvaluator:

    def __init__(self, api_key: str, base_url: str, gateway_token: str):
        self.api_key = api_key
        self.base_url = base_url
        self.gateway_token = gateway_token

    def _prepare_headers(self):
        """Prepare common headers for requests."""
        return {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + self.gateway_token,
            'Custom': self.api_key
        }

    def _process_request_data(
            self, request: Union[Dict, RAGRequest, MCPRequest]) -> Dict:
        """Convert request to dictionary format, handling both JSON dict and Pydantic models."""
        if isinstance(request, dict):
            return request
        elif hasattr(request, 'model_dump'):
            return request.model_dump()
        else:
            raise ValueError(
                "Request must be either a dictionary or a Pydantic model")

    def evaluate(self,
                 context: str,
                 expected_output: str,
                 executed_output: List[str],
                 guardrails: Optional[str] = None) -> float:
        url = urljoin(self.base_url,
                      Configurations.getLLMEvaluatorContextPath("judge"))

        data = {
            "context": context,
            "expected_output": expected_output,
            "executed_output": executed_output,
            "guardrails": guardrails
        }
        headers = self._prepare_headers()
        sync_client = SyncHTTPClient()
        response = sync_client.post(url, data, headers)
        return response

    def evaluate_rag(self, request: Union[Dict, RAGRequest]) -> Dict:
        """Evaluate a RAG (Retrieval-Augmented Generation) system."""
        # Validate and convert input
        if isinstance(request, dict):
            # Validate JSON input against RAGRequest schema
            validated_request = RAGRequest(**request)
            request_data = validated_request.model_dump()
        else:
            request_data = request.model_dump()

        url = urljoin(self.base_url,
                      Configurations.getLLMEvaluatorContextPath("score"))

        headers = self._prepare_headers()
        sync_client = SyncHTTPClient()
        response = sync_client.post(url, request_data, headers)
        return response

    def evaluate_mcp(self, request: Union[Dict, MCPRequest]) -> Dict:
        """Evaluate an MCP (Model Context Protocol) tool-calling system."""
        # Validate and convert input
        if isinstance(request, dict):
            # Validate JSON input against MCPRequest schema
            validated_request = MCPRequest(**request)
            request_data = validated_request.model_dump()
        else:
            request_data = request.model_dump()

        url = urljoin(self.base_url,
                      Configurations.getLLMEvaluatorContextPath("score"))

        headers = self._prepare_headers()
        sync_client = SyncHTTPClient()
        response = sync_client.post(url, request_data, headers)
        return response

    def evaluate_batch(
        self, requests: Union[List[Dict], List[EvaluationRequestUnion],
                              List[Union[Dict, EvaluationRequestUnion]]]
    ) -> Dict:
        """Evaluate a batch of RAG or MCP requests."""
        url = urljoin(self.base_url,
                      Configurations.getLLMEvaluatorContextPath("batch/score"))

        headers = self._prepare_headers()

        # Process and validate each request in the batch
        batch_data = []
        for req in requests:
            if isinstance(req, dict):
                # Try to determine if it's RAG or MCP based on presence of 'tools' field
                if 'tools' in req:
                    validated_req = MCPRequest(**req)
                else:
                    validated_req = RAGRequest(**req)
                batch_data.append(validated_req.model_dump())
            else:
                batch_data.append(req.model_dump())

        sync_client = SyncHTTPClient()
        response = sync_client.post(url, batch_data, headers)
        return response

    def evaluate_dataset(self, dataset: Union[Dict,
                                              EvaluationDataset]) -> Dict:
        """Evaluate an entire dataset of mixed RAG/MCP evaluations."""
        # Validate and convert dataset
        if isinstance(dataset, dict):
            validated_dataset = EvaluationDataset(**dataset)
        else:
            validated_dataset = dataset

        requests = [item.data for item in validated_dataset.items]
        return self.evaluate_batch(requests)

    def get_app_summary(self, app_name: str, **query_params) -> dict:
        """Get application metrics summary."""
        url = urljoin(
            self.base_url,
            Configurations.getLLMEvaluatorContextPath(
                f"apps/{app_name}/summary"))

        headers = {
            'Authorization': "Bearer " + self.gateway_token,
            'Custom': self.api_key
        }

        sync_client = SyncHTTPClient()
        response = sync_client.get(url, params=query_params, headers=headers)
        return response
