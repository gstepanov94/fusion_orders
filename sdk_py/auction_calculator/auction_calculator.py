from dataclasses import dataclass
from typing import List
from sdk_py.auction_calculator.constants import RATE_BUMP_DENOMINATOR, CONTRACT_TAKER_FEE_PRECISION
from sdk_py.auction_calculator.calc import linearInterpolation
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
            cumulativeTime += point.delay # add the delay of the point to the cumulative time
            coefficientBN = point.coefficient # coefficientBN is the coefficient of the point
            if cumulativeTime > currentTime:
                rate = linearInterpolation(prevCumulativeTime, cumulativeTime, prevCoefficient, coefficientBN, currentTime)
                return int(rate)
            prevCumulativeTime = cumulativeTime
            prevCoefficient = coefficientBN
        rate = linearInterpolation(prevCumulativeTime, lastTime, prevCoefficient, 0, currentTime)
        return int(rate)
        
