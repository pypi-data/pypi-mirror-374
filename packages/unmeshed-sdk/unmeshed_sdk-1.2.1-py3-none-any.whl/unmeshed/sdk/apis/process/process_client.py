import json
from dataclasses import asdict
from typing import Any, TypeVar, Type

import requests

from ..http.http_client_factory import HttpClientFactory
from ..http.http_request_factory import HttpRequestFactory
from ...common.api_call_type import ApiCallType
from ...common.process_action_response_data import ProcessActionResponseData
from ...common.process_data import ProcessData
from ...common.process_request_data import ProcessRequestData
from ...common.process_search_request import ProcessSearchRequest
from ...common.step_data import StepData
from ...configs.client_config import ClientConfig
from ...logger_config import get_logger

logger = get_logger(__name__)

class ProcessClient:
    def __init__(self, http_client_factory: HttpClientFactory,http_request_factory: HttpRequestFactory, client_config: ClientConfig):
        self.client_config = client_config
        self.__http_client = http_client_factory.create()
        self.http_request_factory = http_request_factory
        self.http_request_factory = http_request_factory
        self.__run_process_request_url = "api/process/"

    T = TypeVar('T')

    @staticmethod
    def dict_to_dataclass(data: dict, dataclass_type: Type[T]) -> T:
        return dataclass_type(**data)

    def __populate_single_process(self, process_data: dict) -> ProcessData:
        for key in ['orgId', 'eventType']:
            process_data.pop(key, None)
        return self.dict_to_dataclass(process_data, ProcessData)

    def __populate_process_data(self, process_data_json) -> ProcessData:
        return self.__populate_single_process(process_data_json)

    def __populate_processes_data(self, processes_data_json) -> list[ProcessData]:
        return [self.__populate_single_process(pd) for pd in processes_data_json]

    def __populate_step_data(self, step_data_json) -> StepData:
        return self.dict_to_dataclass(step_data_json, StepData)

    @staticmethod
    def __populate_process_action_response_data(bulk_termination_response) -> ProcessActionResponseData:
        return ProcessActionResponseData(
            count = bulk_termination_response.get("count"),
            details = bulk_termination_response.get("details")
        )

    def run_process_async(self, process_request_data: ProcessRequestData) -> ProcessData :
        params = {
            "clientId": self.client_config.get_client_id()
        }
        json_body = asdict(process_request_data) # type: ignore
        try:
            response = self.http_request_factory.create_post_request(self.__run_process_request_url + "runAsync",
                                                                     params=params,
                                                                     body=json_body)
            if response.status_code != 200:
                raise RuntimeError("Invalid process run request " + response.text)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            logger.error("HTTP error occurred while running process: %s", http_err)
            raise RuntimeError(f"HTTP error: {http_err}") from http_err
        except requests.exceptions.RequestException as req_err:
            logger.error("Request error occurred while running process: %s", req_err)
            raise RuntimeError(f"Request error: {req_err}") from req_err
        except Exception as e:
            logger.error("An unexpected error occurred while running process: %s", e)
            raise RuntimeError(f"Unexpected error: {e}") from e
        try:
            process_data_json = json.loads(response.text)
            return self.__populate_process_data(process_data_json)
        except json.JSONDecodeError as json_err:
            logger.error("Failed to parse the response JSON: %s", json_err)
            raise RuntimeError(f"Failed to parse response JSON: {json_err}") from json_err

    def run_process_sync(self, process_request_data: ProcessRequestData,
                         http_read_timeout: int,
                         process_timeout_seconds: int
                         ) -> ProcessData :
        params = {
            "clientId": self.client_config.get_client_id()
        }
        if process_timeout_seconds is not None:
            params["timeout"] = process_timeout_seconds
        try:
            json_body = asdict(process_request_data) # type: ignore
            response = self.http_request_factory.create_post_request(self.__run_process_request_url + "runSync",
                                                                     params=params,
                                                                     body=json_body,
                                                                     http_read_timeout=http_read_timeout)
            if response.status_code != 200:
                raise RuntimeError("Invalid process run request " + response.text)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            logger.error("HTTP error occurred while running process: %s", http_err)
            raise RuntimeError(f"HTTP error: {http_err}") from http_err
        except requests.exceptions.RequestException as req_err:
            logger.error("Request error occurred while running process: %s", req_err)
            raise RuntimeError(f"Request error: {req_err}") from req_err
        except Exception as e:
            logger.error("An unexpected error occurred while running process: %s", e)
            raise RuntimeError(f"Unexpected error: {e}") from e
        try:
            process_data_json = json.loads(response.text)
            return self.__populate_process_data(process_data_json)
        except json.JSONDecodeError as json_err:
            logger.error("Failed to parse the response JSON: %s", json_err)
            raise RuntimeError(f"Failed to parse response JSON: {json_err}") from json_err

    def get_process_data(self, process_id : int, include_steps: bool) -> ProcessData:
        if process_id  is None:
            raise ValueError("Process ID cannot be None")

        url = self.__run_process_request_url + "context/" + str(process_id)
        params = {
            "includeSteps": include_steps
        }
        try:
            response = self.http_request_factory.create_get_request(url, params=params)
            if response.status_code != 200:
                raise RuntimeError("Invalid fetch process data request " + response.text)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            logger.error("HTTP error occurred while fetching process data: %s", http_err)
            raise RuntimeError(f"HTTP error: {http_err}") from http_err
        except requests.exceptions.RequestException as req_err:
            logger.error("Request error occurred fetching process data: %s", req_err)
            raise RuntimeError(f"Request error: {req_err}") from req_err
        except Exception as e:
            logger.error("An unexpected error occurred fetching process data: %s", e)
            raise RuntimeError(f"Unexpected error: {e}") from e
        try:
            process_data_json = json.loads(response.text)
            return self.__populate_process_data(process_data_json)
        except json.JSONDecodeError as json_err:
            logger.error("Failed to parse the response JSON: %s", json_err)
            raise RuntimeError(f"Failed to parse response JSON: {json_err}") from json_err

    def get_step_data(self, step_id : int) -> StepData:
        if step_id  is None:
            raise ValueError("Step ID cannot be None")
        url = self.__run_process_request_url + "stepContext/" + str(step_id)
        try:
            response = self.http_request_factory.create_get_request(url, params={})
            if response.status_code != 200:
                raise RuntimeError("Invalid fetch step data request " + response.text)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            logger.error("HTTP error occurred while fetching step data: %s", http_err)
            raise RuntimeError(f"HTTP error: {http_err}") from http_err
        except requests.exceptions.RequestException as req_err:
            logger.error("Request error occurred while fetching step data: %s", req_err)
            raise RuntimeError(f"Request error: {req_err}") from req_err
        except Exception as e:
            logger.error("An unexpected error occurred while fetching step data: %s", e)
            raise RuntimeError(f"Unexpected error: {e}") from e
        try:
            step_data_json = json.loads(response.text)
            return self.__populate_step_data(step_data_json)
        except json.JSONDecodeError as json_err:
            logger.error("Failed to parse the response JSON: %s", json_err)
            raise RuntimeError(f"Failed to parse response JSON: {json_err}") from json_err

    def bulk_terminate(self, process_ids: list['int'], reason: str) -> ProcessActionResponseData:
        if process_ids is None:
            raise ValueError("ProcessIds's cannot be None")
        url = self.__run_process_request_url + "bulkTerminate"
        params = {}
        if reason is not None:
            params = {
                "reason": reason
            }
        try:
            response = self.http_request_factory.create_post_request(url, params, process_ids)
            if response.status_code != 200:
                raise RuntimeError("Failed to bulk terminate " + response.text)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            logger.error("HTTP error occurred while bulk termination: %s", http_err)
            raise RuntimeError(f"HTTP error: {http_err}") from http_err
        except requests.exceptions.RequestException as req_err:
            logger.error("Request error occurred while bulk termination: %s", req_err)
            raise RuntimeError(f"Request error: {req_err}") from req_err
        except Exception as e:
            logger.error("An unexpected error occurred while bulk termination: %s", e)
            raise RuntimeError(f"Unexpected error: {e}") from e
        try:
            bulk_termination_response = json.loads(response.text)
            return self.__populate_process_action_response_data(bulk_termination_response)
        except json.JSONDecodeError as json_err:
            logger.error("Failed to parse the response JSON: %s", json_err)
            raise RuntimeError(f"Failed to parse response JSON: {json_err}") from json_err

    def bulk_resume(self, process_ids: list['int']) -> ProcessActionResponseData:
        if process_ids is None:
            raise ValueError("ProcessIds's cannot be None")
        url = self.__run_process_request_url + "bulkResume"
        params = {
            "clientId": self.client_config.get_client_id()
        }
        try:
            response = self.http_request_factory.create_post_request(url, params, process_ids)
            if response.status_code != 200:
                raise RuntimeError("Failed to bulk resume " + response.text)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            logger.error("HTTP error occurred while bulk resume: %s", http_err)
            raise RuntimeError(f"HTTP error: {http_err}") from http_err
        except requests.exceptions.RequestException as req_err:
            logger.error("Request error occurred while bulk resume: %s", req_err)
            raise RuntimeError(f"Request error: {req_err}") from req_err
        except Exception as e:
            logger.error("An unexpected error occurred while bulk resume: %s", e)
            raise RuntimeError(f"Unexpected error: {e}") from e
        try:
            bulk_resume_response = json.loads(response.text)
            return self.__populate_process_action_response_data(bulk_resume_response)
        except json.JSONDecodeError as json_err:
            logger.error("Failed to parse the response JSON: %s", json_err)
            raise RuntimeError(f"Failed to parse response JSON: {json_err}") from json_err


    def bulk_reviewed(self, process_ids: list['int'], reason: str) -> ProcessActionResponseData:
        if process_ids is None:
            raise ValueError("ProcessIds's cannot be None")
        url = self.__run_process_request_url + "bulkReviewed"
        params = {
            "clientId": self.client_config.get_client_id()
        }
        if reason is not None:
            params["reason"] = reason
        try:
            response = self.http_request_factory.create_post_request(url, params, process_ids)
            if response.status_code != 200:
                raise RuntimeError("Failed to bulk reviewed " + response.text)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            logger.error("HTTP error occurred while bulk reviewed: %s", http_err)
            raise RuntimeError(f"HTTP error: {http_err}") from http_err
        except requests.exceptions.RequestException as req_err:
            logger.error("Request error occurred while bulk reviewed: %s", req_err)
            raise RuntimeError(f"Request error: {req_err}") from req_err
        except Exception as e:
            logger.error("An unexpected error occurred while bulk reviewed: %s", e)
            raise RuntimeError(f"Unexpected error: {e}") from e
        try:
            bulk_reviewed_response = json.loads(response.text)
            return self.__populate_process_action_response_data(bulk_reviewed_response)
        except json.JSONDecodeError as json_err:
            logger.error("Failed to parse the response JSON: %s", json_err)
            raise RuntimeError(f"Failed to parse response JSON: {json_err}") from json_err

    def rerun(self, process_id : int, version: int) -> ProcessData:
        if process_id is None:
            raise ValueError("Process ID cannot be None")
        params = {
            "clientId": self.client_config.get_client_id(),
            "processId": process_id
        }
        url = self.__run_process_request_url + "rerun"
        if version is not None:
            params["version"]= version

        try:
            response = self.http_request_factory.create_post_request(url, params, None)
            if response.status_code != 200:
                raise RuntimeError("Failed to rerun request " + response.text)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            logger.error("HTTP error occurred rerunning process: %s", http_err)
            raise RuntimeError(f"HTTP error: {http_err}") from http_err
        except requests.exceptions.RequestException as req_err:
            logger.error("Request error occurred while rerunning process: %s", req_err)
            raise RuntimeError(f"Request error: {req_err}") from req_err
        except Exception as e:
            logger.error("An unexpected error occurred while rerunning process: %s", e)
            raise RuntimeError(f"Unexpected error: {e}") from e
        try:
            process_data = json.loads(response.text)
            return self.__populate_process_data(process_data)
        except json.JSONDecodeError as json_err:
            logger.error("Failed to parse the response JSON: %s", json_err)
            raise RuntimeError(f"Failed to parse response JSON: {json_err}") from json_err

    def search_process_executions(self, params: ProcessSearchRequest) -> list[ProcessData]:
        query_params = asdict(params)  # type: ignore
        # Convert list values to comma-separated strings
        query_params_filtered = {}
        for k, v in query_params.items():
            if v is not None:
                if isinstance(v, list):
                    query_params_filtered[k] = ",".join(str(x) for x in v)
                else:
                    query_params_filtered[k] = v

        url = "api/stats/process/search"

        try:
            response = self.http_request_factory.create_get_request(url, params=query_params_filtered)
            if response.status_code != 200:
                raise RuntimeError("Invalid fetch processes data " + response.text)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            logger.error("HTTP error occurred while fetching processes data: %s", http_err)
            raise RuntimeError(f"HTTP error: {http_err}") from http_err
        except requests.exceptions.RequestException as req_err:
            logger.error("Request error occurred fetching processes data: %s", req_err)
            raise RuntimeError(f"Request error: {req_err}") from req_err
        except Exception as e:
            logger.error("An unexpected error occurred fetching processes data: %s", e)
            raise RuntimeError(f"Unexpected error: {e}") from e

        try:
            processes_data_json = json.loads(response.text)
            return self.__populate_processes_data(processes_data_json)
        except json.JSONDecodeError as json_err:
            logger.error("Failed to parse the response JSON: %s", json_err)
            raise RuntimeError(f"Failed to parse response JSON: {json_err}") from json_err

    def invoke_api_mapping_get(self, endpoint: str, _id : str, correlation_id : str, api_call_type: ApiCallType) -> dict['str', 'Any']:
        query_params, url = self.validate_endpoint_and_get_url(api_call_type, correlation_id, endpoint, _id)
        try:
            response = self.http_request_factory.create_get_request(url, params=query_params)
            if response.status_code != 200:
                raise RuntimeError("Failed invoking webhook get request " + response.text)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            logger.error("HTTP error occurred while invoking webhook get request: %s", http_err)
            raise RuntimeError(f"HTTP error: {http_err}") from http_err
        except requests.exceptions.RequestException as req_err:
            logger.error("Request error occurred invoking webhook get request: %s", req_err)
            raise RuntimeError(f"Request error: {req_err}") from req_err
        except Exception as e:
            logger.error("An unexpected error occurred invoking webhook get request: %s", e)
            raise RuntimeError(f"Unexpected error: {e}") from e
        try:
            response = json.loads(response.text)
            return response

        except json.JSONDecodeError as json_err:
            logger.error("Failed to parse the response JSON: %s", json_err)
            raise RuntimeError(f"Failed to parse response JSON: {json_err}") from json_err

    @staticmethod
    def validate_endpoint_and_get_url(api_call_type, correlation_id, endpoint, _id):
        if endpoint is None:
            raise ValueError("Endpoint cannot be None")
        query_params = {
            "id": _id if _id else None,
            "correlationId": correlation_id if correlation_id else None,
            "apiCallType": api_call_type.name if api_call_type else ApiCallType.ASYNC.name
        }
        query_params = {k: v for k, v in query_params.items() if v is not None}
        url = "api/call/" + endpoint
        return query_params, url

    def invoke_api_mapping_post(self, endpoint: str, _input: dict['str', 'Any'], _id : str, correlation_id : str, api_call_type: ApiCallType) -> dict['str', 'Any']:
        query_params, url = self.validate_endpoint_and_get_url(api_call_type, correlation_id, endpoint, _id)
        try:
            response = self.http_request_factory.create_post_request(url, query_params, _input)
            if response.status_code != 200:
                raise RuntimeError("Failed invoking webhook post request " + response.text)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            logger.error("HTTP error occurred while invoking webhook post request: %s", http_err)
            raise RuntimeError(f"HTTP error: {http_err}") from http_err
        except requests.exceptions.RequestException as req_err:
            logger.error("Request error occurred invoking webhook post request: %s", req_err)
            raise RuntimeError(f"Request error: {req_err}") from req_err
        except Exception as e:
            logger.error("An unexpected error occurred invoking webhook post request: %s", e)
            raise RuntimeError(f"Unexpected error: {e}") from e
        try:
            response = json.loads(response.text)
            return response
        except json.JSONDecodeError as json_err:
            logger.error("Failed to parse the response JSON: %s", json_err)
            raise RuntimeError(f"Failed to parse response JSON: {json_err}") from json_err