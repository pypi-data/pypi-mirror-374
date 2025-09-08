import os
import urllib.request
from pathlib import Path
import jpype
import jpype.imports
from jpype.types import *
from .version import __version__

def get_jar_path():
    # Check environment variable first
    # env_jar_path = os.environ.get('FMP_JAR_PATH')
    # if env_jar_path:
    #     return env_jar_path

    # Determine cache directory
    home = Path.home()
    cache_dir = home / '.fmp4j' / 'jar'
    cache_dir.mkdir(parents=True, exist_ok=True)

    jar_name = f'fmp4j-{__version__}-all.jar'
    jar_path = cache_dir / jar_name

    # Download if not exists
    if not jar_path.exists():
        maven_url = f"https://repo1.maven.org/maven2/dev/sorn/fmp4j/{__version__}/{jar_name}"
        try:
            print(f"Downloading {jar_name} from Maven Central...")
            urllib.request.urlretrieve(maven_url, jar_path)
            print("Download completed.")
        except Exception as e:
            raise RuntimeError(f"Failed to download JAR from {maven_url}: {e}")

    return str(jar_path)

# Start JVM with downloaded JAR
jar_path = get_jar_path()

if not jpype.isJVMStarted():
    jpype.startJVM(
        "-Djava.awt.headless=true",
        classpath=[jar_path],
        convertStrings=True
    )
    print(f"✅ JVM started with classpath: {jar_path}")

# Alphabetical order
import datetime
from java.time import LocalDate
from java.util import HashSet
from java.util import Optional
from dev.sorn.fmp4j import FmpClient
from dev.sorn.fmp4j.cfg import FmpConfig
from dev.sorn.fmp4j.types import FmpSymbol
from dev.sorn.fmp4j.types.FmpCik import cik as to_cik
from dev.sorn.fmp4j.types.FmpCurrency import currency as to_currency
from dev.sorn.fmp4j.types.FmpCusip import cusip as to_cusip
from dev.sorn.fmp4j.types.FmpInterval import interval as to_interval
from dev.sorn.fmp4j.types.FmpIsin import isin as to_isin
from dev.sorn.fmp4j.types.FmpLimit import limit as to_limit
from dev.sorn.fmp4j.types.FmpPeriod import period as to_period
from dev.sorn.fmp4j.types.FmpSymbol import symbol as to_symbol

def to_local_date(value):
    if value is None:
        return None
    if isinstance(value, str):
        return LocalDate.parse(value)
    elif isinstance(value, datetime.date):
        return LocalDate.of(value.year, value.month, value.day)
    else:
        raise TypeError(f"Invalid type for date: {type(value)}")

def to_optional(value):
    return Optional.of(value) if value is not None else Optional.empty()

class Fmp4jClient:
    def __init__(self):
        self.client = FmpClient()

    # +-----------------+
    # | CALENDAR CLIENT |
    # +-----------------+

    def dividends(self, symbol):
        symbol = to_symbol(symbol)
        return self.client.calendar().dividends(symbol)

    def dividends_calendar(self):
        return self.client.calendar().dividends()

    def earnings(self, symbol):
        symbol = to_symbol(symbol)
        return self.client.calendar().earnings(symbol)

    def earnings_calendar(self):
        return self.client.calendar().earnings()

    def ipos_calendar(self, from_date, to_date):
        from_date = to_optional(to_local_date(from_date))
        to_date = to_optional(to_local_date(to_date))
        return self.client.calendar().ipos(from_date, to_date)

    def ipos_disclosure(self, from_date, to_date):
        from_date = to_optional(to_local_date(from_date))
        to_date = to_optional(to_local_date(to_date))
        return self.client.calendar().disclosures(from_date, to_date)

    def ipos_prospectus(self, from_date, to_date):
        from_date = to_optional(to_local_date(from_date))
        to_date = to_optional(to_local_date(to_date))
        return self.client.calendar().prospectus(from_date, to_date)

    # +--------------+
    # | CHART CLIENT |
    # +--------------+

    def historical_price_eod_light_chart(self, symbol, from_date, to_date):
        from_date = to_optional(to_local_date(from_date))
        to_date = to_optional(to_local_date(to_date))
        symbol = to_symbol(symbol)
        return self.client.chart().historicalPriceEodLight(symbol, from_date, to_date)

    def historical_price_eod_full_chart(self, symbol, from_date, to_date):
        from_date = to_optional(to_local_date(from_date))
        to_date = to_optional(to_local_date(to_date))
        symbol = to_symbol(symbol)
        return self.client.chart().historicalPriceEodFull(symbol, from_date, to_date)

    def historical_chart(self, symbol, interval, from_date, to_date):
        symbol = to_symbol(symbol)
        interval = to_interval(interval)
        from_date = to_optional(to_local_date(from_date))
        to_date = to_optional(to_local_date(to_date))
        return self.client.chart().historical(symbol, interval, from_date, to_date)

    # +----------------+
    # | COMPANY CLIENT |
    # +----------------+

    def company(self, symbol):
        symbol = to_symbol(symbol)
        return self.client.company().bySymbol(symbol)

    # +------------------+
    # | DIRECTORY CLIENT |
    # +------------------+

    def etfs(self):
        return self.client.directory().etfs()

    def stocks(self):
        return self.client.directory().stocks()

    # +------------------+
    # | ECONOMICS CLIENT |
    # +------------------+

    def treasury_rates(self, from_date, to_date):
        from_date = to_local_date(from_date)
        to_date = to_local_date(to_date)
        return self.client.economics().treasuryRates(from_date, to_date)

    # +------------+
    # | ETF CLIENT |
    # +------------+

    def etf_asset_exposure(self, symbol):
        symbol = to_symbol(symbol)
        return self.client.etf().assetExposure(symbol)

    def etf_country_weightings(self, symbol):
        symbol = to_symbol(symbol)
        return self.client.etf().countryWeightings(symbol)

    def etf_holdings(self, symbol):
        symbol = to_symbol(symbol)
        return self.client.etf().holdings(symbol)

    def etf_info(self, symbol):
        symbol = to_symbol(symbol)
        return self.client.etf().info(symbol)

    def etf_sector_weightings(self, symbol):
        symbol = to_symbol(symbol)
        return self.client.etf().sectorWeightings(symbol)

    # +-------------+
    # | NEWS CLIENT |
    # +-------------+

    def crypto_news(self, symbols):
        symbol_set = HashSet()
        for symbol in symbols:
            symbol_set.add(to_symbol(symbol))
        return self.client.news().crypto(symbol_set)

    def forex_news(self, symbols):
        symbol_set = HashSet()
        for symbol in symbols:
            symbol_set.add(to_symbol(symbol))
        return self.client.news().forex(symbol_set)

    def stock_news(self, symbols):
        symbol_set = HashSet()
        for symbol in symbols:
            symbol_set.add(to_symbol(symbol))
        return self.client.news().stock(symbol_set)

    # +---------------+
    # | QUOTES CLIENT |
    # +---------------+

    def full_quote(self, symbol):
        symbol = to_symbol(symbol)
        return self.client.quote().full(symbol)

    def partial_quote(self, symbol):
        symbol = to_symbol(symbol)
        return self.client.quote().partial(symbol)

    def price_change(self, symbol):
        symbol = to_symbol(symbol)
        return self.client.quote().priceChange(symbol)

    # +---------------+
    # | SEARCH CLIENT |
    # +---------------+

    def search_by_cik(self, cik):
        cik = to_cik(cik)
        return self.client.search().byCik(cik)

    def search_by_cusip(self, cusip):
        cusip = to_cusip(cusip)
        return self.client.search().byCusip(cusip)

    def search_by_isin(self, isin):
        isin = to_isin(isin)
        return self.client.search().byIsin(isin)

    def search_by_name(self, name):
        return self.client.search().byName(name)

    def search_by_symbol(self, symbol):
        symbol = to_symbol(symbol)
        return self.client.search().bySymbol(symbol)

    # +---------------------------+
    # | SEC FILINGS SEARCH CLIENT |
    # +---------------------------+

    def sec_filings_search(self, symbol, from_date, to_date, page, limit):
        symbol = to_symbol(symbol)
        from_date = to_local_date(from_date)
        to_date = to_local_date(to_date)
        page = to_optional(page)
        limit = to_optional(to_limit(limit))
        return self.client.secFilingsSearch().bySymbol(symbol, from_date, to_date, page, limit)

    # +-------------------+
    # | STATEMENTS CLIENT |
    # +-------------------+

    def income_statement(self, symbol, period, limit):
        symbol = to_symbol(symbol)
        period = to_optional(to_period(period))
        limit = to_optional(to_limit(limit))
        return self.client.statement().income(symbol, period, limit)

    def income_statement_as_reported(self, symbol, period, limit):
        symbol = to_symbol(symbol)
        period = to_optional(to_period(period))
        limit = to_optional(to_limit(limit))
        return self.client.statement().incomeAsReported(symbol, period, limit)

    def income_statement_growth(self, symbol, period, limit):
        symbol = to_symbol(symbol)
        period = to_optional(to_period(period))
        limit = to_optional(to_limit(limit))
        return self.client.statement().incomeGrowth(symbol, period, limit)

    def income_statement_ttm(self, symbol, limit):
        symbol = to_symbol(symbol)
        limit = to_optional(to_limit(limit))
        return self.client.statement().incomeTtm(symbol, limit)

    def balance_sheet_statement(self, symbol, period, limit):
        symbol = to_symbol(symbol)
        period = to_optional(to_period(period))
        limit = to_optional(to_limit(limit))
        return self.client.statement().balanceSheet(symbol, period, limit)

    def balance_sheet_statement_as_reported(self, symbol, period, limit):
        symbol = to_symbol(symbol)
        period = to_optional(to_period(period))
        limit = to_optional(to_limit(limit))
        return self.client.statement().balanceSheetAsReported(symbol, period, limit)

    def balance_sheet_statement_growth(self, symbol, period, limit):
        symbol = to_symbol(symbol)
        period = to_optional(to_period(period))
        limit = to_optional(to_limit(limit))
        return self.client.statement().balanceSheetGrowth(symbol, period, limit)

    def balance_sheet_statement_ttm(self, symbol, limit):
        symbol = to_symbol(symbol)
        limit = to_optional(to_limit(limit))
        return self.client.statement().balanceSheetTtm(symbol, limit)

    def cash_flow_sheet_statement(self, symbol, period, limit):
        symbol = to_symbol(symbol)
        period = to_optional(to_period(period))
        limit = to_optional(to_limit(limit))
        return self.client.statement().cashFlow(symbol, period, limit)

    def cash_flow_sheet_statement_as_reported(self, symbol, period, limit):
        symbol = to_symbol(symbol)
        period = to_optional(to_period(period))
        limit = to_optional(to_limit(limit))
        return self.client.statement().cashFlowAsReported(symbol, period, limit)

    def cash_flow_sheet_statement_growth(self, symbol, period, limit):
        symbol = to_symbol(symbol)
        period = to_optional(to_period(period))
        limit = to_optional(to_limit(limit))
        return self.client.statement().cashFlowGrowth(symbol, period, limit)

    def cash_flow_sheet_statement_ttm(self, symbol, limit):
        symbol = to_symbol(symbol)
        limit = to_optional(to_limit(limit))
        return self.client.statement().cashFlowTtm(symbol, limit)

    def financial_growth(self, symbol, period, limit):
        symbol = to_symbol(symbol)
        period = to_optional(to_period(period))
        limit = to_optional(to_limit(limit))
        return self.client.statement().financialGrowth(symbol, period, limit)

    def key_metrics(self, symbol, period, limit):
        symbol = to_symbol(symbol)
        period = to_optional(to_period(period))
        limit = to_optional(to_limit(limit))
        return self.client.statement().keyMetrics(symbol, period, limit)

    def key_metrics_ttm(self, symbol):
        symbol = to_symbol(symbol)
        return self.client.statement().keyMetricsTtm(symbol)

    def ratios(self, symbol, period, limit):
        symbol = to_symbol(symbol)
        period = to_optional(to_period(period))
        limit = to_optional(to_limit(limit))
        return self.client.statement().ratios(symbol, period, limit)

    def ratios_ttm(self, symbol):
        symbol = to_symbol(symbol)
        return self.client.statement().ratiosTtm(symbol)

    def enterprise_values(self, symbol, period, limit):
        symbol = to_symbol(symbol)
        period = to_optional(to_period(period))
        limit = to_optional(to_limit(limit))
        return self.client.statement().enterpriseValues(symbol, period, limit)

    def revenue_geographic_segmentations(self, symbol, period, limit):
        symbol = to_symbol(symbol)
        period = to_optional(to_period(period))
        limit = to_optional(to_limit(limit))
        return self.client.statement().revenueGeographicSegmentations(symbol, period, limit)

    def revenue_product_segmentations(self, symbol, period, limit):
        symbol = to_symbol(symbol)
        period = to_optional(to_period(period))
        limit = to_optional(to_limit(limit))
        return self.client.statement().revenueProductSegmentations(symbol, period, limit)
