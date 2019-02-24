


def sharpe(r_portfolio, r_riskfree, std_portfolio):
    """Calculate Sharpe
    
    Arguments:
        r_portfolio {[type]} -- Average return of portfolio
        r_riskfree {[type]} -- Risk-free rate of return
        std_portfolio {[type]} -- Standard deviation of portfolio returns (r_portfolio)
    
    """

    return (r_portfolio - r_riskfree) / std_portfolio