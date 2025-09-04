from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Optional, Union

from kiota_abstractions.api_client_builder import (
    enable_backing_store_for_serialization_writer_factory,
    register_default_deserializer,
    register_default_serializer,
)
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.serialization import (
    ParseNodeFactoryRegistry,
    SerializationWriterFactoryRegistry,
)
from kiota_abstractions.store import BackingStoreFactory, BackingStoreFactorySingleton
from kiota_serialization_form.form_parse_node_factory import FormParseNodeFactory
from kiota_serialization_form.form_serialization_writer_factory import (
    FormSerializationWriterFactory,
)
from kiota_serialization_json.json_parse_node_factory import JsonParseNodeFactory
from kiota_serialization_json.json_serialization_writer_factory import (
    JsonSerializationWriterFactory,
)
from kiota_serialization_multipart.multipart_serialization_writer_factory import (
    MultipartSerializationWriterFactory,
)
from kiota_serialization_text.text_parse_node_factory import TextParseNodeFactory
from kiota_serialization_text.text_serialization_writer_factory import (
    TextSerializationWriterFactory,
)

if TYPE_CHECKING:
    from .copilot.copilot_request_builder import CopilotRequestBuilder

class BaseAgentsM365CopilotBetaServiceClient(BaseRequestBuilder):
    """
    The main entry point of the SDK, exposes the configuration and the fluent API.
    """
    def __init__(self,request_adapter: RequestAdapter, backing_store: Optional[BackingStoreFactory] = None) -> None:
        """
        Instantiates a new BaseAgentsM365CopilotBetaServiceClient and sets the default values.
        param backing_store: The backing store to use for the models.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        if request_adapter is None:
            raise TypeError("request_adapter cannot be null.")
        super().__init__(request_adapter, "{+baseurl}", None)
        register_default_serializer(JsonSerializationWriterFactory)
        register_default_serializer(TextSerializationWriterFactory)
        register_default_serializer(FormSerializationWriterFactory)
        register_default_serializer(MultipartSerializationWriterFactory)
        register_default_deserializer(JsonParseNodeFactory)
        register_default_deserializer(TextParseNodeFactory)
        register_default_deserializer(FormParseNodeFactory)
        if not self.request_adapter.base_url:
            self.request_adapter.base_url = "https://graph.microsoft.com/beta"
        self.path_parameters["base_url"] = self.request_adapter.base_url
        self.request_adapter.enable_backing_store(backing_store)
    
    @property
    def copilot(self) -> CopilotRequestBuilder:
        """
        The copilot property
        """
        from .copilot.copilot_request_builder import CopilotRequestBuilder

        return CopilotRequestBuilder(self.request_adapter, self.path_parameters)
    

