from enum import Enum, IntEnum


class Action(IntEnum):
    """Telemetry actions, mirrored from the TS client."""
    FeedVersion = 0
    BestBlock = 1      # Not needed: chain-wide block info, we track per-node state
    BestFinalized = 2  # Not needed: chain-wide finalized info, we track per-node state
    AddedNode = 3
    RemovedNode = 4
    LocatedNode = 5
    ImportedBlock = 6
    FinalizedBlock = 7
    NodeStatsUpdate = 8
    Hardware = 9
    TimeSync = 10

    # TODO: multi-chain support
    AddedChain = 11
    RemovedChain = 12
    SubscribedTo = 13
    UnsubscribedFrom = 14

    Pong = 15
    StaleNode = 20
    NodeIOUpdate = 21
    ChainStatsUpdate = 22

FEED_VERSION = "32"
DEFAULT_WS_URL = "wss://feed.telemetry.polkadot.io/feed/"

class ChainGenesis(str, Enum):
    KUSAMA = '0xb0a8d493285c2df73290dfb7e61f870f17b41801197a149ca93654499ea3dafe'
    POLKADOT = '0x91b171bb158e2d3848fa23a9f1c25182fb8e20313b2c1eb49219da7a70ce90c3'
