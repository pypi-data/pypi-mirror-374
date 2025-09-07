from typing import List, Type, Tuple
import logging

import requests
from ai_haley_kg_domain.model.KGInteraction import KGInteraction
from kgraphservice.kgraph_service_inf import KGraphServiceInterface, KGFP, KGN, G
from kgraphservice.ontology.ontology_query_manager import OntologyQueryManager
from typing_extensions import TypedDict
from vital_ai_vitalsigns.query.part_list import PartList
from vital_ai_vitalsigns.query.result_list import ResultList
from vital_ai_vitalsigns.service.vital_namespace import VitalNamespace
from vital_ai_vitalsigns.service.vital_service_status import VitalServiceStatus

from vital_agent_kg_utils.vital_agent_rest_resource_client.tool_service_interface import ToolServiceInterface
from vital_agent_kg_utils.vital_agent_rest_resource_client.tools.place_search.tool_handler import \
    PlaceSearchToolHandler
from vital_agent_kg_utils.vital_agent_rest_resource_client.tools.tool_parameters import ToolParameters
from vital_agent_kg_utils.vital_agent_rest_resource_client.tools.tool_request import ToolRequest
from vital_agent_kg_utils.vital_agent_rest_resource_client.tools.tool_response import ToolResponse
from vital_agent_kg_utils.vital_agent_rest_resource_client.tools.tool_results import ToolResults
from vital_agent_kg_utils.vital_agent_rest_resource_client.tools.weather.models import WeatherOutput, WeatherData
from vital_agent_kg_utils.vital_agent_rest_resource_client.tools.weather.tool_handler import WeatherToolHandler
from vital_agent_kg_utils.vital_agent_rest_resource_client.tools.web_search.tool_handler import WebSearchToolHandler


# client to the python webservice which provides access to tools
# and queries to kgraph service (graph and vector db)


class VitalAgentRestResourceClient(KGraphServiceInterface, ToolServiceInterface):

    def __init__(self, config:dict):
        self.config = config
        self.logger = logging.getLogger(__name__)

    # Tools

    def handle_tool_request(self, tool_name: str, tool_parameters: ToolParameters) -> ToolResponse:

        # TODO
        # check tool_name to determine validation and handler

        tool_request = ToolRequest(
            tool=tool_name,
            tool_input=tool_parameters
        )

        tool_endpoint = self.config.get("tool_endpoint")

        # url = "http://localhost:8008/tool"
        # url = "http://internal-vital-agent-resource-rest-lb-1305845817.us-east-1.elb.amazonaws.com:8008/tool"
        # url = "http://vital-agent-resource-rest-lb.apichatai.com:8008/tool"

        url = f"{tool_endpoint}/tool"
       
        tool_request_dict = tool_request.to_dict()

        response = requests.post(url, json=tool_request_dict)

        self.logger.info(f"Tool request to {url} - Status Code: {response.status_code}")
        
        response_json = response.json()
        self.logger.debug(f"Response JSON: {response_json}")

        if tool_name == "weather_tool":
            handler = WeatherToolHandler()
            weather_results = handler.handle_response(tool_parameters, response_json)
            tool_response = ToolResponse.create_success(
                tool_output=weather_results,
                duration_ms=0  # Could extract from response_json if available
            )
            return tool_response

        if tool_name == "place_search_tool":
            handler = PlaceSearchToolHandler()
            place_search_results = handler.handle_response(tool_parameters, response_json)
            tool_response = ToolResponse.create_success(
                tool_output=place_search_results,
                duration_ms=0  # Could extract from response_json if available
            )
            return tool_response

        if tool_name == "google_address_validation_tool":
            from vital_agent_kg_utils.vital_agent_rest_resource_client.tools.google_address_validation.tool_handler import AddressValidationToolHandler
            handler = AddressValidationToolHandler()
            address_validation_results = handler.handle_response(tool_parameters, response_json)
            tool_response = ToolResponse.create_success(
                tool_output=address_validation_results,
                duration_ms=0  # Could extract from response_json if available
            )
            return tool_response

        if tool_name == "google_web_search_tool":
            handler = WebSearchToolHandler()
            web_search_results = handler.handle_response(tool_parameters, response_json)
            tool_response = ToolResponse.create_success(
                tool_output=web_search_results,
                duration_ms=0  # Could extract from response_json if available
            )
            return tool_response

        # unknown tool
        tool_results = ToolResults()

        tool_response = ToolResponse(
            tool_name=tool_name,
            tool_parameters=tool_parameters,
            tool_results=tool_results
        )

        return tool_response

    # KGService calls

    def get_ontology_query_manager(self) -> OntologyQueryManager:
        pass

    def get_graph(self, graph_uri: str) -> VitalNamespace:
        pass

    def list_graphs(self) -> List[VitalNamespace]:
        pass

    def check_create_graph(self, graph_uri: str) -> bool:
        pass

    def create_graph(self, graph_uri: str) -> bool:
        pass

    def delete_graph(self, graph_uri: str) -> bool:
        pass

    def purge_graph(self, graph_uri: str) -> bool:
        pass

    def get_graph_all_objects(self, graph_uri: str, limit=100, offset=0) -> ResultList:
        pass

    def insert_object(self, graph_uri: str, graph_object: G) -> VitalServiceStatus:
        pass

    def insert_object_list(self, graph_uri: str, graph_object_list: List[G]) -> VitalServiceStatus:
        pass

    def update_object(self, graph_object: G, graph_uri: str, *, upsert: bool = False) -> VitalServiceStatus:
        pass

    def update_object_list(self, graph_object_list: List[G], graph_uri: str, *,
                           upsert: bool = False) -> VitalServiceStatus:
        pass

    def get_object(self, object_uri: str, graph_uri: str | None = None) -> G:
        pass

    def get_object_list(self, object_uri_list: List[str], graph_uri: str | None = None) -> ResultList:
        pass

    def delete_object(self, object_uri: str, graph_uri: str | None = None) -> VitalServiceStatus:
        pass

    def delete_object_list(self, object_uri_list: List[str], graph_uri: str | None = None) -> VitalServiceStatus:
        pass

    def filter_query(self, graph_uri: str, sparql_query: str) -> ResultList:
        pass

    def query(self, graph_uri: str, sparql_query: str) -> ResultList:
        pass

    def query_construct(self, graph_uri: str, sparql_query: str, binding_list: List[Tuple[str, str]]) -> ResultList:
        pass

    def get_interaction_list(self, graph_uri: str, limit=100, offset=0) -> ResultList:
        pass

    def get_interaction_graph(self, graph_uri: str, interaction: KGInteraction, limit=100, offset=0) -> ResultList:
        pass

    def get_interaction_frames(self, graph_uri: str, interaction: KGInteraction, limit=100, offset=0) -> PartList:
        pass

    def get_interaction_nodes(self, graph_uri: str, interaction: KGInteraction, kgnode_type: Type[KGN], limit=100,
                              offset=0) -> ResultList:
        pass

    def get_frame(self, graph_uri: str, frame_uri: str, limit=100, offset=0) -> KGFP:
        pass

    def get_frames(self, graph_uri: str, frame_uri_list: List[str], limit=100, offset=0) -> PartList:
        pass

    def get_frame_id(self, graph_uri: str, frame_id: str, limit=100, offset=0) -> KGFP:
        pass

    def get_frames_id(self, graph_uri: str, frame_id_list: List[str], limit=100, offset=0) -> PartList:
        pass

    def get_frames_root(self, graph_uri: str, root_uri: str, limit=100, offset=0) -> PartList:
        pass

    def get_graph_objects_type(self, graph_uri: str, class_uri: str, include_subclasses=True, limit=100,
                               offset=0) -> ResultList:
        pass

    def get_graph_objects_tag(self, graph_uri: str, kg_graph_uri: str, limit=100, offset=0) -> ResultList:
        pass

    def delete_frame(self, graph_uri: str, frame_uri: str) -> VitalServiceStatus:
        pass

    def delete_frames(self, graph_uri: str, frame_uri_list: List[str]) -> VitalServiceStatus:
        pass

    def delete_frame_id(self, graph_uri: str, frame_id: str) -> VitalServiceStatus:
        pass

    def delete_frames_id(self, graph_uri: str, frame_id_list: List[str]) -> VitalServiceStatus:
        pass

    def delete_graph_objects_tag(self, graph_uri: str, kg_graph_uri: str) -> VitalServiceStatus:
        pass
