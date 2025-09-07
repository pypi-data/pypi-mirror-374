def clean_symbol(symbol: str) -> str:
    """
    將 MT5 商品代碼轉為商品名稱
    例如: 'EURUSD.sml' -> 'EURUSD'
          'BATS_CFD.UK' -> 'BATS_CFD.UK'
    """
    # 如果最後一段是 sml，就去掉
    if symbol.lower().endswith('.sml'):
        return symbol.rsplit('.', 1)[0]
    return symbol