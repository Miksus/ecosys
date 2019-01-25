# Balck and Scholes
def european_call_price(S, K, T, r, sigma, q=0):
    """
    S: Underlying's spot
    K=Strike
    T=time to maturity
    r=riskless rate
    sigma=volatility of underlying
    q=dividend rate
    """
    d1 = calculate_d1(S, K, T, r, sigma)
    d2 = calculate_d2(S, K, T, r, sigma)
    if q == 0:
        return (S * stats.norm.cdf(d1) - K * np.exp(-r * T) * stats.norm.cdf(d2))
    else:
        return (S * np.exp(-q*T) * stats.norm.cdf(d1) - K * np.exp(-r * T) * stats.norm.cdf(d2))

def european_put_price(S, K, T, r, sigma, q=0):
    """
    S: Underlying's spot
    K=Strike
    T=time to maturity
    r=riskless rate
    sigma=volatility of underlying
    q=dividend rate
    """
    d1 = calculate_d1(S, K, T, r, sigma)
    d2 = calculate_d2(S, K, T, r, sigma)
    if q == 0:
        return K * np.exp(-r * T) * stats.norm.cdf(-d2) - S * stats.norm.cdf(-d1)
    else:
        return K * np.exp(-r * T) * stats.norm.cdf(-d2) - S * np.exp(-q*T) * stats.norm.cdf(-d1)

def d1(S, K, T, r, sigma):
    return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

def d2(S, K, T, r, sigma):
    return (np.log(S / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))


# Greeks
def delta_call(S, K, T, r, sigma, q=0):
    "NOTE: European"
    d1 = calculate_d1(S, K, T, r, sigma)
    if q == 0:
        return stats.norm.cdf(d1)
    else:
        return np.exp(-q*T) * stats.norm.cdf(d1)

def delta_put(S, K, T, r, sigma, q=0):
    "NOTE: European"
    d1 = calculate_d1(S, K, T, r, sigma)
    if q == 0:
        return stats.norm.cdf(d1) - 1
    else:
        return np.exp(-q*T) * stats.norm.cdf(d1) - 1

def gamma():
    raise NotImplementedError

def vega():
    raise NotImplementedError