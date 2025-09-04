from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional, Union

from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter

if TYPE_CHECKING:
    from ....models.ai_interaction import AiInteraction
    from ....models.base_collection_pagination_count_response import BaseCollectionPaginationCountResponse

from ....models.base_collection_pagination_count_response import (
    BaseCollectionPaginationCountResponse,
)


@dataclass
class GetAllEnterpriseInteractionsGetResponse(BaseCollectionPaginationCountResponse, Parsable):
    # The value property
    value: Optional[list[AiInteraction]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> GetAllEnterpriseInteractionsGetResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: GetAllEnterpriseInteractionsGetResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return GetAllEnterpriseInteractionsGetResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from ....models.ai_interaction import AiInteraction
        from ....models.base_collection_pagination_count_response import (
            BaseCollectionPaginationCountResponse,
        )

        fields: dict[str, Callable[[Any], None]] = {
            "value": lambda n : setattr(self, 'value', n.get_collection_of_object_values(AiInteraction)),
        }
        super_fields = super().get_field_deserializers()
        fields.update(super_fields)
        return fields
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        super().serialize(writer)
        writer.write_collection_of_object_values("value", self.value)
    

