import numpy as np
from datetime import timedelta
import matplotlib.pyplot as plt
from MPSPlots import helper

from TradeTide.market import Market
from TradeTide.binary.interface_indicators import MOVINGAVERAGECROSSING
from TradeTide.indicators.base import BaseIndicator
from TradeTide.simulation_settings import SimulationSettings


class MovingAverageCrossing(MOVINGAVERAGECROSSING, BaseIndicator):
    """
    Implements a Moving Average Crossing (MAC) indicator as an extension of the BaseIndicator class.

    This indicator involves two moving averages of a series: a "short" and a "long" moving average. A typical trading signal
    is generated when the short moving average crosses above (bullish signal) or below (bearish signal) the long moving average.
    The indicator is commonly used to identify the momentum and direction of a trend.

    Attributes:
        short_window (int | str): The window size of the short moving average.
        long_window (int | str): The window size of the long moving average.

    Methods:
        plot: Plots the short and long moving averages on a given Matplotlib axis.
    """

    def __init__(self, short_window: timedelta, long_window: timedelta):
        self.short_window = short_window
        self.long_window = long_window

        int_short_window = int(
            short_window.total_seconds()
            / SimulationSettings().get_time_unit().total_seconds()
        )
        int_long_window = int(
            long_window.total_seconds()
            / SimulationSettings().get_time_unit().total_seconds()
        )

        super().__init__(short_window=int_short_window, long_window=int_long_window)

    def run(self, market: Market) -> None:
        """
        Runs the Moving Average Crossing indicator on the provided market data.
        This method initializes the indicator with the market's dates and calculates the short and long moving averages
        based on the specified window sizes.

        Parameters
        ----------
        market (Market):
            The market data to run the indicator on. It should contain the dates and price data.

        Raises
        -------
        ValueError: If the market does not contain enough data points to calculate the moving averages.
        """
        self.market = market

        self._cpp_run_with_market(market)

    @helper.pre_plot(nrows=1, ncols=1)
    def plot(self, axes: plt.Axes) -> None:
        """
        Plots the raw price, both SMAs, the SMA-difference and the crossover signals
        on the provided axis.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axis to draw onto.
        """
        dates = np.asarray(self.market.dates)

        # get the two moving‐averages
        short_ma = np.asarray(self._cpp_short_moving_average)
        long_ma = np.asarray(self._cpp_long_moving_average)
        diff_ma = short_ma - long_ma

        # plot price and MAs
        axes.plot(
            dates,
            short_ma,
            label=f"Short MA ({self.short_window})",
            linestyle="--",
            linewidth=2,
        )
        axes.plot(
            dates,
            long_ma,
            label=f"Long MA ({self.long_window})",
            linestyle="-",
            linewidth=2,
        )

        # optional: show the difference on a secondary axis
        ax2 = axes.twinx()
        ax2.plot(
            dates, diff_ma, label="MA Diff (Short-Long)", linestyle=":", linewidth=1
        )
        ax2.set_ylabel("MA Difference")
        axes.set_xlabel("Date")
        axes.set_ylabel("Price / SMA")

        self._unify_axes_legend(axes, ax2)

        self._add_region_to_ax(ax=axes)

        self.market.plot_ask(axes=axes, show=False)

        ax2.grid(False)
        ax2.set_zorder(-1)
