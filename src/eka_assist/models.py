from typing import List, Optional

from pydantic import BaseModel, Field


class MedicationUnderstanding(BaseModel):
    drug_name: Optional[str] = Field(
        None, description="The segmented branded name of the medicine like Glim 1mg"
    )
    form: Optional[str] = Field(
        None, description="The form of the medicine like Tablet, Syrup"
    )
    generic_names: Optional[str] = Field(
        None, description="The generic name of the medicine like 'Glimeperide', 'Metformin'. "
                          "In case of compound generics, pass the name only with comma separated like Glimeperide,Metformin"
    )
    volumes: Optional[str] = Field(
        None, description="The volume of the drug name or generic composition like '650','1000','500'"
    )


class MedicationInteraction(BaseModel):
    drug_names: List[str] = Field(
        None, description="List of drug names to check for interactions. Eg: ['Bencid tablet', 'Fluvir 75Mg capsule']"
    )


class Protocol(BaseModel):
    query: str = Field(
        description="Concise and exact sentence to search. Do not use when, where, how, etc."
    )
    tag: str = Field(
        description="The tag/condition basis which the protocols database should be filtered"
    )
    publisher: str = Field(
        description="The name of the publisher. Cannot be assumed unless specified in the query by the user "
                    "or selected from output of get_protocol_publishers"
    )


class QueryProtocols(BaseModel):
    queries: List[Protocol] = Field(
        description="List of non overlapping distinct queries to search for protocols"
    )


class ProtocolPublisher(BaseModel):
    tag: str = Field(
        None, description="The tag/condition for which the publisher is being fetched"
    )
