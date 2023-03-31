import random
from dataclasses import dataclass
from sdk_py.utils import padStart
from sdk_py.auction_salt.parser import *


@dataclass
class AuctionSalt():
    auctionStartTime: int = 0
    duration: int=0
    initialRateBump: int=0
    bankFee: int=0
    salt: int = random.randint(0,10000)

    
    def build(self):
        result = padStart(hex(self.auctionStartTime), 8,  '0') + \
            padStart(hex(self.duration), 6,  '0') + \
            padStart(hex(self.initialRateBump), 6,  '0') + \
            padStart(hex(self.bankFee), 8,  '0') + \
            padStart(hex(self.salt), 36,  '0')
        return int('0x' + result, 16)
    
    @classmethod
    def decode(self, salt):
        return AuctionSalt(**{
            'auctionStartTime': getStartTime(salt),
            'duration': getDuration(salt),
            'initialRateBump': getInitialRateBump(salt),
            'bankFee': getFee(salt),
            'salt': getSalt(salt)
        })
    