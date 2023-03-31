from typing import List
from sdk_py.auction_suffix.types import AuctionPoint, AuctionWhitelistItem
from sdk_py.utils import padStart
from sdk_py.constants import ZERO_ADDRESS, ZERO_NUMBER

def encodeAuctionParams(points: List[AuctionPoint]) -> str:
    result = []
    for point in points:
        result.append(padStart(hex(point.delay), 4, '0') + padStart(hex(point.coefficient), 6, '0'))
    return ''.join(result)

def encodeWhitelist(whitelist: List[AuctionWhitelistItem]) -> str:
    result = []
    for item in whitelist:
        result.append(padStart(hex(item.allowance), 8, '0') + item.address[2:])
    return ''.join(result)

def encodePublicResolvingDeadline(deadline: int) -> str:
    return padStart(hex(deadline), 8, '0')

def encodeTakingFeeData(takerFeeReceiver: str = ZERO_ADDRESS, takerFeeRatio: str = ZERO_NUMBER) -> str:
    if takerFeeReceiver == ZERO_ADDRESS or takerFeeRatio == ZERO_NUMBER:
        return ''
    return takerFeeReceiver[2:] + padStart(hex(int(takerFeeRatio)), 4, '0')

def encodeFlags(whitelist: List[AuctionWhitelistItem], points: List[AuctionPoint], takingFeeData: str) -> str:
    if len(points) > 8:
        raise Exception('max points count = 8')
    flags = (len(whitelist) << 3) | len(points)
    if takingFeeData:
         flags |= 128
    return padStart(hex(flags), 2, '0')