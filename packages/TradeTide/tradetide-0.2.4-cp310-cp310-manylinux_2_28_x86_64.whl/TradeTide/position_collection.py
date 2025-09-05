from typing import Union
import numpy as np
import matplotlib.pyplot as plt
from MPSPlots import helper

from TradeTide.binary.interface_position_collection import POSITIONCOLLECTION
from TradeTide import position
import TradeTide


Long = position.Long
Short = position.Short


class PositionCollection(POSITIONCOLLECTION):

    def __init__(self, market, trade_signal: np.ndarray, debug_mode: bool = False):
        """
        Initialize the PositionCollection with a market and trade signal.

        Parameters
        ----------
        market : Market
            The market data to use for positions.
        trade_signal : np.ndarray
            The trade signal to use for opening positions.
        """
        self.market = market
        super().__init__(
            market=market,
            trade_signal=trade_signal,
            debug_mode=TradeTide.debug_mode if TradeTide.debug_mode else debug_mode,
        )

    @helper.pre_plot(nrows=2, ncols=1)
    def plot(self, axes: plt.Axes, max_positions: Union[int, float] = np.inf):
        """
        Plot market bid/ask prices and shade closed positions, using the mps style,
        consistent naming of 'position', and a clear legend with distinct colors.

        Parameters
        ----------
        max_positions : int or float, default=np.inf
            Maximum number of positions to draw (in chronological order).
        axes : matplotlib.axes.Axes, optional
            Axes to draw on. If None, a new figure+axes are created.
        """
        axes[0].sharex(axes[1])
        axes[0].sharey(axes[1])

        self.market.plot_ask(axes=axes[0], show=False)

        self.market.plot_bid(axes=axes[1], show=False)

        axes[0].set_xlabel("Date")
        axes[1].set_ylabel(f"Bid Price")
        axes[0].set_ylabel(f"Ask Price")

        for idx in range(min(len(self), max_positions)):

            position = self[idx]

            ax = axes[0] if position.is_long else axes[1]

            start, end = position.start_date, position.close_date
            fill_color = "C0" if position.is_long else "C1"

            # shade the region
            ax.axvspan(start, end, facecolor=fill_color, edgecolor="black", alpha=0.2)

            # SL and TP lines
            axes[0].plot(
                position.exit_strategy.dates,
                position.exit_strategy.stop_loss_prices,
                linestyle="--",
                color="red",
                linewidth=1,
            )

            axes[1].plot(
                position.exit_strategy.dates,
                position.exit_strategy.take_profit_prices,
                linestyle="--",
                color="green",
                linewidth=1,
            )

            axes[0].get_figure().autofmt_xdate()
