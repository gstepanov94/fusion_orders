
from dataclasses import dataclass
from typing import List

from sdk_py.auction_suffix.types import AuctionPoint, AuctionWhitelistItem
from sdk_py.auction_suffix.constants import NoPublicResolvingDeadline
from sdk_py.constants import ZERO_ADDRESS
from sdk_py.auction_suffix.encoder import encodeAuctionParams, encodeWhitelist, encodePublicResolvingDeadline, encodeTakingFeeData, encodeFlags
from sdk_py.auction_suffix.parser.parser import parseInteractionsSuffix

@dataclass
class AuctionSuffix():
    points: List[AuctionPoint]
    whitelist: List[AuctionWhitelistItem] 
    publicResolvingDeadline: int = NoPublicResolvingDeadline
    takerFeeReceiver: str = ZERO_ADDRESS
    takerFeeRatio: str = '0'

    @staticmethod
    def decode(interactions: str):
        suffix = parseInteractionsSuffix(interactions)
        
        return AuctionSuffix(publicResolvingDeadline= suffix['publicResolvingDeadline'],
             points= suffix['points'],
             takerFeeReceiver= suffix['takerFeeReceiver'],
             takerFeeRatio= suffix['takerFeeRatio'],
             whitelist= suffix['whitelist']
        )

    def build(self):
        auctionParams = encodeAuctionParams(self.points)
        whitelist = encodeWhitelist(self.whitelist)
        publicResolvingDeadline = encodePublicResolvingDeadline(self.publicResolvingDeadline)
        takingFeeData = encodeTakingFeeData(self.takerFeeReceiver, self.takerFeeRatio)
        flags = encodeFlags(self.whitelist, self.points, takingFeeData)
        return auctionParams + whitelist + publicResolvingDeadline + takingFeeData + flags



