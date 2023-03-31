from sdk_py.auction_suffix.parser.constants import *
from sdk_py.auction_suffix.parser.types import InteractionFlags, TakerFeeData, PrivateAuctionDeadline, AuctionPoint, AuctionWhitelistItem, ParsedAuctionParams
from sdk_py.errors import BadOrderSuffixError
from sdk_py.utils import add0x

from decimal import Decimal as D
from typing import Dict

def parseFlags(interactions: str) -> InteractionFlags:
    flags_hex = interactions[-FLAGS_LENGTH:]
    
    if len(flags_hex) < FLAGS_LENGTH:
        raise ('Invalid flags length')
    
    flags = int(flags_hex, 16)
    
    if not flags:
        raise BadOrderSuffixError('cannot parse flags')
    
    resolvers_count = (flags & RESOLVERS_LENGTH_MASK) >> RESOLVERS_LENGTH_OFFSET
    
    if resolvers_count == 0:
        raise BadOrderSuffixError('cannot have 0 resolvers')
    
    taking_fee_enabled = (flags & HAS_TAKING_FEE_FLAG) != 0
    
    points_count = flags & POINTS_LENGTH_MASK
    
    
    return InteractionFlags(takingFeeEnabled=taking_fee_enabled, resolversCount=bool(resolvers_count), pointsCount=bool(points_count))

def minInteractionsLength(flags: InteractionFlags) -> int:
    auction_points_len = flags.pointsCount * (AUCTION_DELAY_LENGTH + AUCTION_BUMP_LENGTH)
    whitelist_len = flags.resolversCount * (ALLOWED_TIMESTAMP_LENGTH + ADDRESS_LENGTH)

    required_length = auction_points_len + whitelist_len + PRIVATE_AUCTION_DEADLINE_LENGTH + FLAGS_LENGTH

    if flags.takingFeeEnabled:
        return required_length + TAKER_FEE_RECEIVER_LENGTH + TAKER_FEE_RATIO_LENGTH

    return required_length

def parseTakingFeeAndReturnRemainingInteractions(flags: InteractionFlags, interactions: str) -> TakerFeeData:
    if not flags.takingFeeEnabled:
        return TakerFeeData(interactions=interactions, takerFeeReceiver=ZERO_ADDRESS, takerFeeRatio='0')

    takerFeeDataLen = TAKER_FEE_RECEIVER_LENGTH + TAKER_FEE_RATIO_LENGTH

    takerFeeData = interactions[-takerFeeDataLen:]

    takerFeeReceiverHex = takerFeeData[TAKER_FEE_RATIO_LENGTH:]
    takerFeeReceiver = add0x(takerFeeReceiverHex)

    if takerFeeReceiver == ZERO_ADDRESS:
        raise BadOrderSuffixError('takerFeeReceiver cannot be zero address')

    takerFeeRateHex = takerFeeData[0:TAKER_FEE_RATIO_LENGTH]
    takerFeeRatio = D(add0x(takerFeeRateHex))

    if takerFeeRatio > CONTRACT_TAKER_FEE_PRECISION:
        raise BadOrderSuffixError('takerFeeRatio cannot be > 1e9')

    return {
        'interactions': interactions[:-takerFeeDataLen],
        'takerFeeReceiver': takerFeeReceiver,
        'takerFeeRatio': str(takerFeeRatio)
    }

def parsePrivateAuctionDeadline(interactions: str) -> PrivateAuctionDeadline:
    deadlineHex = interactions[-PRIVATE_AUCTION_DEADLINE_LENGTH:]
    deadline = int('0x'+deadlineHex, 16)

    if not deadline:
        raise BadOrderSuffixError('cannot parse deadline')

    return {
        'interactions': interactions[:-PRIVATE_AUCTION_DEADLINE_LENGTH],
        'deadline': deadline
    }

def parseResolversWhitelist(flags, interactions):
    whitelist = []

    allowed_ts_and_resolver_len = ADDRESS_LENGTH + ALLOWED_TIMESTAMP_LENGTH # 48

    addresses_packed = interactions[(-1 * flags.resolversCount * allowed_ts_and_resolver_len):]
    

    if len(addresses_packed) % allowed_ts_and_resolver_len:
        raise BadOrderSuffixError("Invalid whitelist addresses in interactions")

    for i in range(0, len(addresses_packed), allowed_ts_and_resolver_len):
        ts_and_address = addresses_packed[i:(i + allowed_ts_and_resolver_len)]
        timestamp_hex = ts_and_address[:ALLOWED_TIMESTAMP_LENGTH]
        address = ts_and_address[ALLOWED_TIMESTAMP_LENGTH:] #-8

        timestamp = int('0x'+timestamp_hex, 16)

        if timestamp != 0 and not timestamp:
            raise BadOrderSuffixError("Invalid resolver allowance timestamp")
        awl = AuctionWhitelistItem(address= add0x(address).lower(), allowance= int(timestamp))
        whitelist.append(awl)

    return {
        "whitelist": whitelist,
        "interactions": interactions[:(-1 * flags.resolversCount * allowed_ts_and_resolver_len)],
    }

def parseAuctionParams(flags: InteractionFlags, interactions: str) -> ParsedAuctionParams:
    if flags.pointsCount == 0:
        return {
            "interactions": interactions,
            "points": []
        }

    points = []

    auction_params_length = AUCTION_DELAY_LENGTH + AUCTION_BUMP_LENGTH

    params_packed = interactions[-1 * flags.pointsCount * auction_params_length:]

    if len(params_packed) % auction_params_length:
        raise BadOrderSuffixError("Invalid auction params in interactions")

    for i in range(0, len(params_packed), auction_params_length):
        duration_and_bump = params_packed[i:i+auction_params_length]
        duration_hex = duration_and_bump[:AUCTION_DELAY_LENGTH]
        bump_hex = duration_and_bump[AUCTION_DELAY_LENGTH:]

        duration = int(duration_hex, 16)

        if not duration:
            raise BadOrderSuffixError("Invalid auction point duration")

        bump = int(bump_hex, 16)

        if not bump:
            raise BadOrderSuffixError("Invalid auction point bump")

        points.append(AuctionPoint(delay=duration, coefficient=bump))

    return {
        "points": points,
        "interactions": interactions[:flags.pointsCount * auction_params_length]
    }

def parseInteractionsSuffix(interactions: str) -> Dict[str, any]:
    flags = parseFlags(interactions)

    if len(interactions) < minInteractionsLength(flags):
        raise BadOrderSuffixError('wrong interactions length')

    interactionsWithoutFlags = interactions[:-FLAGS_LENGTH]

    parsedTakingFee = parseTakingFeeAndReturnRemainingInteractions(
        flags,
        interactionsWithoutFlags
    )
    if type(parsedTakingFee) is not dict:
        parsedTakingFee = parsedTakingFee.__dict__

    takerFeeReceiver = parsedTakingFee['takerFeeReceiver']
    takerFeeRatio = int(parsedTakingFee['takerFeeRatio'])
    interactionsNoTakingFee = parsedTakingFee['interactions']

    parsedDeadline = parsePrivateAuctionDeadline(interactionsNoTakingFee)
    deadline = parsedDeadline['deadline']
    interactionsNoDeadline = parsedDeadline['interactions']

    parsedWhitelist = parseResolversWhitelist(flags, interactionsNoDeadline)
    whitelist = parsedWhitelist['whitelist']
    interactionsWithoutWhitelist = parsedWhitelist['interactions']

    parsedAuctionParams = parseAuctionParams(flags, interactionsWithoutWhitelist)
    points = parsedAuctionParams['points']

    return {
        'whitelist': whitelist,
        'publicResolvingDeadline': deadline,
        'takerFeeReceiver': takerFeeReceiver,
        'takerFeeRatio': takerFeeRatio,
        'points': points
    }

#print(minInteractionsLength(parseFlags('000c004e200000000000000000219ab540356cbb839cbe05303d7705fa63c0566a09')))

# interactionsWithoutFlags = '000c004e200000000000000000219ab540356cbb839cbe05303d7705fa63c0566a09'[:-2]
# #print(parseTakingFeeAndReturnRemainingInteractions(parseFlags('000c004e200000000000000000219ab540356cbb839cbe05303d7705fa63c0566a09'), interactionsWithoutFlags))
# print(parsePrivateAuctionDeadline(interactionsWithoutFlags))

# print(parseInteractionsSuffix('000c004e200000000000000000219ab540356cbb839cbe05303d7705fa63c0566a09'))

