# Compute effective fixed rate rho for portfolio
# See performance.txt

import numpy as np
import scipy.optimize as sopt

def logsumexp(x):
    mx = np.max(x)
    return np.log(np.sum(np.exp(x - mx))) + mx

def critfunc(x, data, port_value):
    arg = np.array([1.0, x]).reshape((2, 1))
    return logsumexp(np.dot(data, arg)) - np.log(port_value)

# NOTE:
# Since different ETFs are always bought at exactly the same ratio,
# can also compute rho for any one of them:
# - Set port_value to single ETF current value
# - Set frac to ratio (where 1.0 is the sum of all ETFs)

# 9.4.17
#days_start = 145
#port_value = 450987.09
#frac = 1.0
# ==> rho = 0.167733

# 25.11.17
#days_start = 375
#port_value = 593139.91
#frac = 1.0
# ==> rho = 0.055667
# Example for single ETF:
#days_start = 375
#port_value = 46167.31
#frac = 0.5/7.

# 30.4.2018
days_start = 531
port_value = 645820.71
frac = 1.0
# ==> rho = 0.034389


data = np.array(
    [[np.log(56604.0), float(days_start-0)/365],
     [np.log(40833.0), float(days_start-16)/365],
     [np.log(43833.0), float(days_start-30)/365],
     [np.log(40833.0), float(days_start-47)/365],
     [np.log(43833.0), float(days_start-61)/365],
     [np.log(40833.0), float(days_start-78)/365],
     [np.log(43833.0), float(days_start-92)/365],
     [np.log(40833.0), float(days_start-106)/365],
     [np.log(43833.0), float(days_start-120)/365],
     [np.log(40833.0), float(days_start-137)/365],
     [np.log(43833.0), float(days_start-151)/365],
     [np.log(40833.0), float(days_start-167)/365],
     [np.log(3000.0),  float(days_start-181)/365],
     [np.log(27120.0), float(days_start-198)/365],
     [np.log(3000.0),  float(days_start-212)/365],
     [np.log(3000.0),  float(days_start-242)/365],
     [np.log(3000.0),  float(days_start-273)/365],
     [np.log(3000.0),  float(days_start-304)/365],
     [np.log(3000.0),  float(days_start-334)/365],
     [np.log(3000.0),  float(days_start-365)/365],
     [np.log(37790.0), float(days_start-381)/365],
     [np.log(3000.0),  float(days_start-395)/365],
     [np.log(3000.0),  float(days_start-426)/365],
     [np.log(3000.0),  float(days_start-457)/365],
     [np.log(3000.0),  float(days_start-485)/365],
     [np.log(3000.0),  float(days_start-516)/365]])

data[:, 0] += np.log(frac)
a = np.log1p(0.0001)  # More than 0.01%
b = np.log1p(0.3)  # Less than 30%
log1prho = sopt.brentq(
    f=lambda x: critfunc(x, data, port_value),
    a=a, b=b)

print 'Effective rate: rho = %f\n' % (np.expm1(log1prho),)
