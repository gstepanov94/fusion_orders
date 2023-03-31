def linearInterpolation(t1, t2, v1, v2, t):
    timePassedFromNow = t-t1 
    timeLeft = t2-t
    partialCoefficient = v2*timePassedFromNow
    partialPrevCoefficient = v1*timeLeft
    coefficient = partialCoefficient + partialPrevCoefficient
    pointsTimeDiff = t2-t1
    return coefficient/pointsTimeDiff


#(v2*(t-t1) + v1(t2-t)) /(t2-t1)