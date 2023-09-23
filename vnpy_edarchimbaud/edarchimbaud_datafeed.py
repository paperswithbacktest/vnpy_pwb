from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Callable

from datasets import load_dataset
from numpy import datetime64, ndarray
from pandas import DataFrame, to_datetime

from vnpy.trader.setting import SETTINGS
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData, TickData, HistoryRequest
from vnpy.trader.utility import round_to, ZoneInfo
from vnpy.trader.datafeed import BaseDatafeed


INTERVAL_VT2EA: Dict[Interval, str] = {
    Interval.MINUTE: "1m",
    Interval.DAILY: "1d",
}

INTERVAL_ADJUSTMENT_MAP: Dict[Interval, timedelta] = {
    Interval.MINUTE: timedelta(minutes=1),
    Interval.DAILY: timedelta(),  # no need to adjust for daily bar
}

EXCHANGES: Set[Exchange] = {
    Exchange.NASDAQ,
}

NYC_TZ = ZoneInfo("America/New_York")


class EdarchimbaudDatafeed(BaseDatafeed):
    """EdArchimbaud data service interface"""

    def __init__(self):
        """"""
        self.username: str = SETTINGS["datafeed.username"]
        self.password: str = SETTINGS["datafeed.password"]

        self.inited: bool = False
        self.symbols: ndarray = None

    def init(self, output: Callable = print) -> bool:
        """Initialisation"""
        if self.inited:
            return True

        try:
            dataset = load_dataset("edarchimbaud/perimeter-stocks")
            df: DataFrame = dataset["train"].to_pandas()
            self.symbols = df["symbol"].values
        except Exception as ex:
            output(f"An unknown exception occurred: {ex}")
            return False

        self.inited = True
        return True

    def query_bar_history(
        self, req: HistoryRequest, output: Callable = print
    ) -> Optional[List[BarData]]:
        """Query bar data"""
        if not self.inited:
            n: bool = self.init(output)
            if not n:
                return []

        symbol: str = req.symbol
        exchange: Exchange = req.exchange
        interval: Interval = req.interval
        start: datetime = req.start
        end: datetime = req.end

        ea_symbol: str = symbol
        if symbol not in self.symbols:
            output(
                f"EdArchimbaud failed to query bar data: unsupported contract code {req.vt_symbol}"
            )
            return []

        ea_interval: str = INTERVAL_VT2EA.get(interval)
        if not ea_interval:
            output(
                f"EdArchimbaud failed to query bar data: unsupported time period {req.interval.value}"
            )
            return []

        # In order to convert the basket timestamp (the point at which the bar ends)
        # to the VeighNa timestamp (the point at which the bar begins)
        adjustment: timedelta = INTERVAL_ADJUSTMENT_MAP[interval]

        # In order to check the nightly data
        end += timedelta(1)

        dataset = load_dataset(f"edarchimbaud/timeseries-{ea_interval}-stocks")
        df: DataFrame = dataset["train"].to_pandas()
        df["date"] = to_datetime(df["date"])
        index: ndarray = (
            (df.symbol == ea_symbol)
            & (df.date >= datetime64(start))
            & (df.date <= datetime64(end))
        )
        df = df.loc[index, :]

        data: List[BarData] = []

        if df is not None:
            # Fill NaN to 0
            df.fillna(0, inplace=True)

            for row in df.itertuples():
                dt: datetime = row.date.to_pydatetime() - adjustment
                dt: datetime = dt.replace(tzinfo=NYC_TZ)
                adj_factor: float = row.adj_close / row.close

                bar: BarData = BarData(
                    symbol=symbol,
                    exchange=exchange,
                    interval=interval,
                    datetime=dt,
                    open_price=round_to(row.open * adj_factor, 0.000001),
                    high_price=round_to(row.high * adj_factor, 0.000001),
                    low_price=round_to(row.low * adj_factor, 0.000001),
                    close_price=round_to(row.adj_close, 0.000001),
                    volume=row.volume,
                    turnover=row.volume * row.adj_close,
                    open_interest=0,
                    gateway_name="EA",
                )

                data.append(bar)

        return data
