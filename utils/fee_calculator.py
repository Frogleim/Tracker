def calculate_futures_fees(position_btc, entry_price, fee_rate, funding_rate=None, mark_price=None):
    # Trading fee
    position_usdt = position_btc * entry_price
    trading_fee = position_usdt * fee_rate * 2  # Open + Close

    # Funding fee (optional)
    funding_fee = None
    if funding_rate is not None and mark_price is not None:
        funding_fee = position_usdt * funding_rate

    return {
        "position_usdt": position_usdt,
        "trading_fee": trading_fee,
        "funding_fee": funding_fee
    }

# Example usage:
fees = calculate_futures_fees(
    position_btc=3,
    entry_price=32000,
    fee_rate=0.0005,           # 0.05% taker fee
    funding_rate=0.0001,       # 0.01% funding rate
    mark_price=32000
)

print(fees)