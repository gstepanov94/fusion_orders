from typing import List, Optional
from dataclasses import dataclass

@dataclass
class AuctionPoint():
    coefficient: int
    delay: int

@dataclass
class AuctionWhitelistItem():
    address: str= ''
    allowance: int = 0 # seconds

@dataclass
class SettlementSuffixData():
    points: List[AuctionPoint]
    whitelist: List[AuctionWhitelistItem]
    publicResolvingDeadline: Optional[int] = None  # seconds
    takerFeeReceiver: Optional[str] = None
    takerFeeRatio: Optional[str] = None

@dataclass
class RemainingInteractions():
    remainingInteractions: int

@dataclass
class InteractionAdditionalInfo():
    auction_start_time: int
    duration: int
    initial_rate_bump: int
    points: List[AuctionPoint]
    whitelist: List[AuctionWhitelistItem]
    public_resolving_deadline: Optional[int] = None
    taker_fee_receiver: Optional[str] = None
    taker_fee_ratio: Optional[str] = None

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
class ResolversWhitelist(): 
    whitelist: List[AuctionWhitelistItem]
@dataclass
class ParsedAuctionParams():
    points: List[AuctionPoint]
    


