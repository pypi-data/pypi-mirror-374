from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional, Union

from kiota_abstractions.serialization import (
    AdditionalDataHolder,
    Parsable,
    ParseNode,
    SerializationWriter,
)
from kiota_abstractions.store import BackedModel, BackingStore, BackingStoreFactorySingleton

if TYPE_CHECKING:
    from .retrieval_entity_type import RetrievalEntityType
    from .retrieval_extract import RetrievalExtract
    from .search_resource_metadata_dictionary import SearchResourceMetadataDictionary
    from .search_sensitivity_label_info import SearchSensitivityLabelInfo

@dataclass
class RetrievalHit(AdditionalDataHolder, BackedModel, Parsable):
    # Stores model information.
    backing_store: BackingStore = field(default_factory=BackingStoreFactorySingleton(backing_store_factory=None).backing_store_factory.create_backing_store, repr=False)

    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)
    # The extracts property
    extracts: Optional[list[RetrievalExtract]] = None
    # The OdataType property
    odata_type: Optional[str] = None
    # The resourceMetadata property
    resource_metadata: Optional[SearchResourceMetadataDictionary] = None
    # The resourceType property
    resource_type: Optional[RetrievalEntityType] = None
    # The sensitivityLabel property
    sensitivity_label: Optional[SearchSensitivityLabelInfo] = None
    # The webUrl property
    web_url: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> RetrievalHit:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: RetrievalHit
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return RetrievalHit()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .retrieval_entity_type import RetrievalEntityType
        from .retrieval_extract import RetrievalExtract
        from .search_resource_metadata_dictionary import SearchResourceMetadataDictionary
        from .search_sensitivity_label_info import SearchSensitivityLabelInfo

        fields: dict[str, Callable[[Any], None]] = {
            "extracts": lambda n : setattr(self, 'extracts', n.get_collection_of_object_values(RetrievalExtract)),
            "@odata.type": lambda n : setattr(self, 'odata_type', n.get_str_value()),
            "resourceMetadata": lambda n : setattr(self, 'resource_metadata', n.get_object_value(SearchResourceMetadataDictionary)),
            "resourceType": lambda n : setattr(self, 'resource_type', n.get_enum_value(RetrievalEntityType)),
            "sensitivityLabel": lambda n : setattr(self, 'sensitivity_label', n.get_object_value(SearchSensitivityLabelInfo)),
            "webUrl": lambda n : setattr(self, 'web_url', n.get_str_value()),
        }
        return fields
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        writer.write_collection_of_object_values("extracts", self.extracts)
        writer.write_str_value("@odata.type", self.odata_type)
        writer.write_object_value("resourceMetadata", self.resource_metadata)
        writer.write_enum_value("resourceType", self.resource_type)
        writer.write_object_value("sensitivityLabel", self.sensitivity_label)
        writer.write_str_value("webUrl", self.web_url)
        writer.write_additional_data_value(self.additional_data)
    

