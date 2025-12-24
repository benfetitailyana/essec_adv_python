from trading import Order, Trader, TradeBlotter


def test_blotter_utilities() -> None:
    trader = Trader(trader_id="1", name="Adam", desk="EQ")
    blotter = TradeBlotter()
    blotter.add_order(Order(trader=trader, underlier="NKY", strike=100, maturity=0.25, notional=100))
    blotter.add_order(Order(trader=trader, underlier="NKY", strike=101, maturity=0.25, notional=50))
    assert blotter.sum_notional() == 150
    assert blotter.filter_by_strike(101)[0].strike == 101
    assert "NKY" in blotter.unique_underlier()
