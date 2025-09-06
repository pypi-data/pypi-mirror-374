from dataclasses import dataclass

from latch_config.config import read_config


@dataclass(frozen=True)
class FuseConfig:
    gql_endpoint: str = "https://vacuole.latch.bio/graphql"
    nucleus_endpoint: str = "https://nucleus.latch.bio"


config = read_config(FuseConfig)
