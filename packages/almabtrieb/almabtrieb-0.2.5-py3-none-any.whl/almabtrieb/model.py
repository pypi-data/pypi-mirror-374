"""
Data models used in communication with the Cattle Drive protocol

"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ActorInformation(BaseModel):
    """Information about an actor"""

    id: str = Field(
        examples=["http://host.example/actor/1"],
        description="The id of the actor",
    )

    name: str = Field(
        examples=["Alice"],
        description="The internal name of the actor",
    )


class InformationResponse(BaseModel):
    """Response for the information request"""

    actors: List[ActorInformation] = Field(
        examples=[
            [
                ActorInformation(id="http://host.example/actor/1", name="Alice"),
                ActorInformation(id="http://host.example/actor/2", name="Bob"),
            ]
        ],
        description="""Actors of the account on the server""",
    )

    base_urls: List[str] = Field(
        examples=[["http://host.example"]],
        alias="baseUrls",
        description="""The base urls of the server""",
    )

    method_information: List[Any] = Field(
        [],
        alias="methodInformation",
        description="""
    A list of methods to information about the methods implemented by the backend.
    """,
    )


class CreateActorRequest(BaseModel):
    """Request to create an actor"""

    base_url: str = Field(
        examples=["http://host.example"],
        serialization_alias="baseUrl",
        description="""Base url for the actor, the actor URI will be of the form `{base_url}/actor/{id}`""",
    )

    preferred_username: str | None = Field(
        None,
        examples=["alice", "bob"],
        description="""
    Add a preferred username. This name will be used in acct:username@domain and supplied to webfinger. Here domain is determine from baseUrl.
    """,
        serialization_alias="preferredUsername",
    )
    profile: Dict[str, Any] = Field(
        {},
        examples=[{"summary": "A new actor"}],
        description="""
    New profile object for the actor.
    """,
    )
    automatically_accept_followers: bool | None = Field(
        examples=[True],
        description="""
    Enables setting actors to automatically accept follow requests
    """,
        serialization_alias="automaticallyAcceptFollowers",
    )
    name: str | None = Field(
        None, examples=["Alice"], description="The name of the actor"
    )


class WithActor(BaseModel):
    """Used as base for messages requiring an actor"""

    actor: str = Field(
        examples=["http://host.example/actor/1"],
        description="""The actor performing the action""",
    )


class FetchMessage(WithActor):
    """Message to fetch an object from the Fediverse"""

    uri: str = Field(
        examples=["http://remote.example/object/1"],
        description="""The resource to fetch""",
    )


class FetchResponse(WithActor):
    """Result of a a fetch request"""

    uri: str = Field(
        examples=["http://remote.example/object/1"],
        description="""The resource that was requested""",
    )

    data: dict | None = Field(description="""The data returned for the object""")


class TriggerMessage(WithActor):
    """Message to trigger something on the ActivityExchange"""

    model_config = ConfigDict(
        extra="allow",
    )
