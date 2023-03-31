from dataclasses import dataclass
from typing import List
from sdk_py.auction_calculator.constants import RATE_BUMP_DENOMINATOR, CONTRACT_TAKER_FEE_PRECISION
from sdk_py.auction_calculator.calc import linearInterpolation
#import os
#import sys
#sys.path.append(os.path.split(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))[0])

from sdk_py.auction_suffix.auction_suffix import AuctionSuffix
from sdk_py.auction_salt.auction_salt import AuctionSalt


@dataclass
class AuctionPoint():
    delay: int
    coefficient: int

@dataclass
class AuctionCalculator():
    startTime: int
    duration: int
    initialRateBump: int
    points: List[AuctionPoint]
    takerFeeRatio: str

    @staticmethod
    def fromLimitOrderV3Struct(order):
        suffix = AuctionSuffix.decode(order['interactions'])
        salt = AuctionSalt.decode(order['salt'])
        return AuctionCalculator.fromAuctionData(suffix, salt)
    @staticmethod
    def fromAuctionData(suffix: AuctionSuffix, salt: AuctionSalt):
        return AuctionCalculator(
            salt.auctionStartTime,
            salt.duration,
            salt.initialRateBump,
            suffix.points,
            suffix.takerFeeRatio
        )

    def calcAuctionTakingAmount(self, takingAmount: int, rate: int) -> str:
        auctionTakingAmount = takingAmount * (rate+RATE_BUMP_DENOMINATOR) / RATE_BUMP_DENOMINATOR
        #print(rate, takingAmount, auctionTakingAmount )
        if int(self.takerFeeRatio) == 0:
            return auctionTakingAmount
        else:
            return auctionTakingAmount + (auctionTakingAmount*self.takerFeeRatio/CONTRACT_TAKER_FEE_PRECISION)
        
    def calcRateBump(self, time: int) -> int:
        cumulativeTime = self.startTime # cumulativeTime is the time when the auction starts
        lastTime = self.duration + cumulativeTime # lastTime is the time when the auction ends
        startBump = self.initialRateBump # startBump is the initial rate bump

        currentTime = time
        if currentTime < cumulativeTime: # if the current time is before the auction starts, return 0
            return 0
        elif currentTime > lastTime: # if the current time is after the auction ends, return 0
            return startBump
        
        prevCoefficient = startBump # prevCoefficient is the coefficient of the previous point
        prevCumulativeTime = cumulativeTime  # prevCumulativeTime is the cumulative time of the previous point
        for point in self.points: # for each point in the points list
            print('point:', point.__dict__)
            cumulativeTime += point.delay # add the delay of the point to the cumulative time
            coefficientBN = point.coefficient # coefficientBN is the coefficient of the point
            if cumulativeTime > currentTime:
                rate = linearInterpolation(prevCumulativeTime, cumulativeTime, prevCoefficient, coefficientBN, currentTime)
                return int(rate)
            prevCumulativeTime = cumulativeTime
            prevCoefficient = coefficientBN
        rate = linearInterpolation(prevCumulativeTime, lastTime, prevCoefficient, 0, currentTime)
        return int(rate)
        

# limitOrderStruct = {
#     'allowedSender': '0x0000000000000000000000000000000000000000',
#     'interactions':
#         '0x2cc2878d0000642663d2000000000000d87a8851aa1a641585703c8fd40fb78ffc471f448290dbccb15b5a516deee2805c58e56075d6605ed87a8851aa1a641585703c8fd40fb78ffc471f440000000084d99aa569d93a9ca187d83734c8c4a519c4e9b100000000c6c7565644ea1893ad29182f7b6961aab7edfed000000000d1742b3c4fbb096990c8950fa635aec75b30781a000000007636a5bfd763cefec2da9858c459f2a9b0fe8a6c00000000bd4dbe0cb9136ffb4955ede88ebd5e92222ad09a0000000069313aec23db7e4e8788b942850202bcb603873400000000cfa62f77920d6383be12c91c71bd403599e1116f00000000ee230dd7519bc5d0c9899e8704ffdc80560e8509000000009108813f22637385228a1c621c1904bbbc50dc256426638f48',
#     'maker': '0xd87a8851aa1a641585703c8fd40fb78ffc471f44',
#     'makerAsset': '0x5283d291dbcf85356a21ba090e6db59121208b44',
#     'makingAmount': '80700753813649000000',
#     'offsets': '2048955946929424286921227713067743020696385405755235979139736848564224',
#     'receiver': '0x8290dbccb15b5a516deee2805c58e56075d6605e',
#     'salt': '45299108939755612574122910909393027489470166614205160412366878165217005876205',
#     'takerAsset': '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
#     'takingAmount': '19654381581179911'
# }
# calculator = AuctionCalculator.fromLimitOrderV3Struct(limitOrderStruct)
# rate = calculator.calcRateBump(16802373341)
# print(rate)
# takingAmount = calculator.calcAuctionTakingAmount(limitOrderStruct['takingAmount'], rate)
# print(takingAmount)
