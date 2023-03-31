from typing import List, Optional
from dataclasses import dataclass

@dataclass
class AuctionPoint():
    coefficient: int
    delay: int

@dataclass
class AuctionWhitelistItem():
    address: str
    allowance: int  # seconds

@dataclass
class SettlementSuffixData():
    points: List[AuctionPoint]
    whitelist: List[AuctionWhitelistItem]
    publicResolvingDeadline: Optional[int] = None  # seconds
    takerFeeReceiver: Optional[str] = None
    takerFeeRatio: Optional[str] = None

@dataclass
class InteractionFlags():
    takingFeeEnabled: bool
    resolversCount: bool
    pointsCount: bool

@dataclass
class TakerFeeData():
    takerFeeRatio: int
    takerFeeReceiver: str
    interactions: str

@dataclass
class PrivateAuctionDeadline():
    deadline: int

@dataclass
class ResolversWhitelist(): #, total=False, NamedTuple
    whitelist: List[AuctionWhitelistItem]
@dataclass
class ParsedAuctionParams():
    points: List[AuctionPoint]