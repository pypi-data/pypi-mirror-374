from fmp4j import Fmp4jClient
import pytest
import time

@pytest.fixture(autouse=True)
def delay_between_tests():
    time.sleep(1)

# +-----------------+
# | CALENDAR CLIENT |
# +-----------------+

def test_dividends():
    # given
    symbol = "AAPL"
    client = Fmp4jClient()

    # when
    res = client.dividends(symbol)

    # then
    assert res is not None
    assert len(res) > 0

def test_dividends_calendar():
    # given
    client = Fmp4jClient()

    # when
    res = client.dividends_calendar()

    # then
    assert res is not None
    assert len(res) > 0

def test_earnings():
    # given
    symbol = "AAPL"
    client = Fmp4jClient()

    # when
    res = client.earnings(symbol)

    # then
    assert res is not None
    assert len(res) > 0

def test_earnings_calendar():
    # given
    client = Fmp4jClient()

    # when
    res = client.earnings_calendar()

    # then
    assert res is not None
    assert len(res) > 0

def test_ipos_calendar():
    # given
    from_date = "2025-02-28"
    to_date = "2025-02-28"
    client = Fmp4jClient()

    # when
    res = client.ipos_calendar(from_date, to_date)

    # then
    assert res is not None
    assert len(res) > 0

def test_ipos_disclosure():
    # given
    from_date = "2025-02-28"
    to_date = "2025-02-28"
    client = Fmp4jClient()

    # when
    res = client.ipos_disclosure(from_date, to_date)

    # then
    assert res is not None
    assert len(res) > 0

def test_ipos_prospectus():
    # given
    from_date = "2025-02-28"
    to_date = "2025-02-28"
    client = Fmp4jClient()

    # when
    res = client.ipos_prospectus(from_date, to_date)

    # then
    assert res is not None
    assert len(res) > 0

# +--------------+
# | CHART CLIENT |
# +--------------+

def test_historical_price_eod_light_chart():
    # given
    symbol = "AAPL"
    from_date = "2025-02-28"
    to_date = "2025-02-28"
    client = Fmp4jClient()

    # when
    res = client.historical_price_eod_light_chart(symbol, from_date, to_date)

    # then
    assert res is not None
    assert len(res) > 0

def test_historical_price_eod_full_chart():
    # given
    symbol = "AAPL"
    from_date = "2025-02-28"
    to_date = "2025-02-28"
    client = Fmp4jClient()

    # when
    res = client.historical_price_eod_full_chart(symbol, from_date, to_date)

    # then
    assert res is not None
    assert len(res) > 0

def test_historical_chart():
    # given
    symbol = "AAPL"
    interval = "1hour"
    from_date = "2025-02-28"
    to_date = "2025-02-28"
    client = Fmp4jClient()

    # when
    res = client.historical_chart(symbol, interval, from_date, to_date)

    # then
    assert res is not None
    assert len(res) > 0

# +----------------+
# | COMPANY CLIENT |
# +----------------+

def test_company():
    # given
    symbol = "AAPL"
    client = Fmp4jClient()

    # when
    res = client.company(symbol)

    # then
    assert res is not None
    assert res[0] is not None
    assert res[0].symbol().value() == symbol

# +------------------+
# | DIRECTORY CLIENT |
# +------------------+

def test_etfs():
    # given
    client = Fmp4jClient()

    # when
    # res = client.etfs()

    # then
    # assert res is not None
    # assert len(res) > 0

def test_stocks():
    # given
    client = Fmp4jClient()

    # when
    # res = client.etfs()

    # then
    # assert res is not None
    # assert len(res) > 0

# +------------------+
# | ECONOMICS CLIENT |
# +------------------+

def test_treasury_rates():
    # given
    client = Fmp4jClient()
    from_date = "2025-02-28"
    to_date = "2025-02-28"

    # when
    res = client.treasury_rates(from_date, to_date)

    # then
    assert res is not None
    assert len(res) > 0

# +------------+
# | ETF CLIENT |
# +------------+

def test_etf_asset_exposure():
    # given
    symbol = "VOO"
    client = Fmp4jClient()

    # when
    res = client.etf_asset_exposure(symbol)

    # then
    assert res is not None
    assert len(res) > 0

def test_etf_country_weightings():
    # given
    symbol = "VOO"
    client = Fmp4jClient()

    # when
    res = client.etf_country_weightings(symbol)

    # then
    assert res is not None
    assert len(res) > 0

def test_etf_holdings():
    # given
    symbol = "VOO"
    client = Fmp4jClient()

    # when
    res = client.etf_holdings(symbol)

    # then
    assert res is not None
    assert len(res) > 0

def test_etf_info():
    # given
    symbol = "VOO"
    client = Fmp4jClient()

    # when
    res = client.etf_info(symbol)

    # then
    assert res is not None
    assert len(res) > 0

def test_etf_sector_weightings():
    # given
    symbol = "VOO"
    client = Fmp4jClient()

    # when
    res = client.etf_sector_weightings(symbol)

    # then
    assert res is not None
    assert len(res) > 0

# +-------------+
# | NEWS CLIENT |
# +-------------+

def test_crypto_news():
    # given
    symbol = "BTCUSD"
    client = Fmp4jClient()

    # when
    # res = client.crypto_news(symbol)

    # then
    # assert res is not None
    # assert len(res) > 0

def test_forex_news():
    # given
    symbol = "EURUSD"
    client = Fmp4jClient()

    # when
    # res = client.forex_news(symbol)

    # then
    # assert res is not None
    # assert len(res) > 0

def test_stock_news():
    # given
    symbol = "AAPL"
    client = Fmp4jClient()

    # when
    # res = client.stock_news(symbol)

    # then
    # assert res is not None
    # assert len(res) > 0

# +---------------+
# | QUOTES CLIENT |
# +---------------+

def test_full_quote():
    # given
    symbol = "AAPL"
    client = Fmp4jClient()

    # when
    res = client.full_quote(symbol)

    # then
    assert res is not None
    assert res[0] is not None
    assert res[0].symbol().value() == symbol
    assert res[0].price() is not None

def test_partial_quote():
    # given
    symbol = "AAPL"
    client = Fmp4jClient()

    # when
    res = client.partial_quote(symbol)

    # then
    assert res is not None
    assert res[0] is not None
    assert res[0].symbol().value() == symbol
    assert res[0].price() is not None

def test_price_change():
    # given
    symbol = "AAPL"
    client = Fmp4jClient()

    # when
    res = client.price_change(symbol)

    # then
    assert res is not None
    assert len(res) > 0

# +---------------+
# | SEARCH CLIENT |
# +---------------+

def test_search_by_cik():
    # given
    cik = "0000320193"
    client = Fmp4jClient()

    # when
    res = client.search_by_cik(cik)

    # then
    assert res is not None
    assert res[0] is not None
    assert res[0].cik().value() == cik

def test_search_by_cusip():
    # given
    cusip = "037833100"
    client = Fmp4jClient()

    # when
    res = client.search_by_cusip(cusip)

    # then
    assert res is not None
    assert res[0] is not None
    assert res[0].cusip().value() == cusip

def test_search_by_isin():
    # given
    isin = "US0378331005"
    client = Fmp4jClient()

    # when
    res = client.search_by_isin(isin)

    # then
    assert res is not None
    assert res[0] is not None
    assert res[0].isin().value() == isin

def test_search_by_name():
    # given
    name = "Apple"
    client = Fmp4jClient()

    # when
    res = client.search_by_name(name)

    # then
    assert res is not None
    assert res[0] is not None
    assert res[0].name() == name + " Inc."

def test_search_by_symbol():
    # given
    symbol = "AAPL"
    client = Fmp4jClient()

    # when
    res = client.search_by_symbol(symbol)

    # then
    assert res is not None
    assert res[0] is not None
    assert res[0].symbol().value() == symbol

# +---------------------------+
# | SEC FILINGS SEARCH CLIENT |
# +---------------------------+

def test_filings_search_by_symbol():
    # given
    symbol = "AAPL"
    from_date = "2024-02-28"
    to_date = "2025-02-28"
    page = 0
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.sec_filings_search(symbol, from_date, to_date, page, limit)

    # then
    assert res is not None
    assert len(res) > 0

# +-------------------+
# | STATEMENTS CLIENT |
# +-------------------+

def test_income_statement():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.income_statement(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_income_statement_as_reported():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.income_statement_as_reported(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_income_statement_growth():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.income_statement_growth(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_income_statement_ttm():
    # given
    symbol = "AAPL"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.income_statement_ttm(symbol, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_balance_sheet_statement():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.balance_sheet_statement(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_balance_sheet_statement_as_reported():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.balance_sheet_statement_as_reported(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_balance_sheet_statement_growth():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.balance_sheet_statement_growth(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_balance_sheet_statement_ttm():
    # given
    symbol = "AAPL"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.balance_sheet_statement_ttm(symbol, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_cash_flow_sheet_statement():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.cash_flow_sheet_statement(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_cash_flow_sheet_statement_as_reported():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.cash_flow_sheet_statement_as_reported(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_bcash_flow_sheet_statement_growth():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.cash_flow_sheet_statement_growth(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_cash_flow_sheet_statement_ttm():
    # given
    symbol = "AAPL"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.cash_flow_sheet_statement_ttm(symbol, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_financial_growth():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.financial_growth(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_key_metrics():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.key_metrics(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_key_metrics_ttm():
    # given
    symbol = "AAPL"
    client = Fmp4jClient()

    # when
    res = client.key_metrics_ttm(symbol)

    # then
    assert res is not None
    assert len(res) > 0

def test_ratios():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.ratios(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_ratios_ttm():
    # given
    symbol = "AAPL"
    client = Fmp4jClient()

    # when
    res = client.ratios_ttm(symbol)

    # then
    assert res is not None
    assert len(res) > 0

def test_enterprise_values():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.enterprise_values(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_revenue_geographic_segmentations():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.revenue_geographic_segmentations(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_revenue_product_segmentations():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.revenue_product_segmentations(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0
