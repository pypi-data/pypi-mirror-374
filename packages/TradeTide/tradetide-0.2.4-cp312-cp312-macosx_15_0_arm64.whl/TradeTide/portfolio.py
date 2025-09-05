from typing import Union
import numpy as np
import matplotlib.pyplot as plt
from MPSPlots.styles import mps
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from MPSPlots import helper

from TradeTide.binary import position
from TradeTide.binary.interface_portfolio import PORTFOLIO
import TradeTide


Long = position.Long
Short = position.Short


class Portfolio(PORTFOLIO):
    def __init__(self, position_collection, debug_mode: bool = False):
        """
        Initialize the Portfolio with a position collection and optional debug mode.

        Parameters
        ----------
        position_collection : PositionCollection
            The collection of positions to manage.
        """
        super().__init__(
            position_collection=position_collection,
            debug_mode=TradeTide.debug_mode if TradeTide.debug_mode else debug_mode,
        )
        self.position_collection = position_collection

    @helper.pre_plot(nrows=2, ncols=1)
    def plot_positions(
        self,
        axes: plt.Axes,
        max_positions: Union[int, float] = np.inf,
    ) -> plt.Figure:
        """
        Plot market bid/ask prices and shade closed positions, using the mps style,
        consistent naming of 'position', and a clear legend with distinct colors.

        Parameters
        ----------
        axes : matplotlib.axes.Axes, optional
            Axes to draw on. If None, a new figure+axes are created.
        max_positions : int or float, default=np.inf
            Maximum number of positions to draw (in chronological order).
        """
        long_list = []
        short_list = []

        position_list = self.get_positions(max_positions)

        for idx, p in enumerate(position_list):
            if p.is_long:
                long_list.append(p)
            else:
                short_list.append(p)

            if idx > 10:
                break

            axes[0].sharex(axes[1])

            self._plot_long_positions(axes=axes[0], position_list=long_list, show=False)

            self._plot_short_positions(
                axes=axes[1], position_list=short_list, show=False
            )

    @helper.pre_plot(nrows=1, ncols=1)
    def _plot_long_positions(
        self, position_list: list[position.Long], axes: plt.Axes
    ) -> None:
        """
        Plot the long positions in the portfolio.

        Parameters
        ----------
        axes : matplotlib.axes.Axes, optional
            Axes to draw on. If None, a new figure+axes are created.
        """
        color_fill = "lightblue"
        sl_color = "#d62728"
        tp_color = "#2ca02c"

        axes.set_ylabel(f"Bid Price")

        self.position_collection.market.plot_bid(axes=axes, show=False)

        for position in position_list:
            start, end = position.start_date, position.close_date
            axes.axvspan(start, end, facecolor=color_fill, edgecolor="black", alpha=0.2)
            axes.plot(
                position.dates(),
                position.stop_loss_prices(),
                linestyle="--",
                color=sl_color,
                linewidth=1,
            )
            axes.plot(
                position.dates(),
                position.take_profit_prices(),
                linestyle="--",
                color=tp_color,
                linewidth=1,
            )

        # Custom legend
        legend_handles = [
            Line2D([0], [0], color=sl_color, linestyle="--", label="Stop Loss"),
            Line2D([0], [0], color=tp_color, linestyle="--", label="Take Profit"),
            Patch(facecolor=color_fill, edgecolor="none", label="Long Position"),
        ]

        axes.legend(handles=legend_handles, loc="upper left", framealpha=0.9)

    @helper.pre_plot(nrows=1, ncols=1)
    def _plot_short_positions(
        self, position_list: list[position.Long], axes: plt.Axes
    ) -> None:
        """
        Plot the short positions in the portfolio.

        Parameters
        ----------
        axes : matplotlib.axes.Axes, optional
            Axes to draw on. If None, a new figure+axes are created.
        """
        color_fill = (0.8, 0.2, 0.2, 0.3)
        sl_color = "#d62728"
        tp_color = "#2ca02c"

        axes.set_ylabel(f"Bid Price")

        self.position_collection.market.plot_bid(axes=axes, show=False)

        for position in position_list:
            start, end = position.start_date, position.close_date
            axes.axvspan(start, end, facecolor=color_fill, edgecolor="black", alpha=0.2)
            axes.plot(
                position.dates(),
                position.stop_loss_prices(),
                linestyle="--",
                color=sl_color,
                linewidth=1,
            )
            axes.plot(
                position.dates(),
                position.take_profit_prices(),
                linestyle="--",
                color=tp_color,
                linewidth=1,
            )

        # Custom legend
        legend_handles = [
            Line2D([0], [0], color=sl_color, linestyle="--", label="Stop Loss"),
            Line2D([0], [0], color=tp_color, linestyle="--", label="Take Profit"),
            Patch(facecolor=color_fill, edgecolor="none", label="Short Position"),
        ]

        axes.legend(handles=legend_handles, loc="upper left", framealpha=0.9)

    @helper.pre_plot(nrows=1, ncols=1)
    def plot_equity(self, axes: plt.Axes) -> None:
        """
        Plot the portfolio's equity over time.

        Parameters
        ----------
        axes : matplotlib.axes.Axes, optional
            Axes to draw on. If None, a new figure+axes are created.
        """
        axes.plot(self.record.time, self.record.equity, color="black")
        axes.axhline(
            self.record.initial_capital,
            color="red",
            linestyle="--",
            linewidth=1,
            label="Initial Capital",
        )
        axes.set_ylabel("Equity")
        axes.legend()

    @helper.pre_plot(nrows=1, ncols=1)
    def plot_capital_at_risk(self, axes: plt.Axes) -> None:
        """
        Plot the capital at risk over time.

        Parameters
        ----------
        axes : matplotlib.axes.Axes, optional
            Axes to draw on. If None, a new figure+axes are created.
        """
        axes.step(
            self.record.time, self.record.capital_at_risk, color="black", where="mid"
        )
        axes.set_ylabel("Capital at Risk")

    @helper.pre_plot(nrows=1, ncols=1)
    def plot_capital(self, axes: plt.Axes) -> None:
        """
        Plot the capital over time.

        Parameters
        ----------
        axes : matplotlib.axes.Axes, optional
            Axes to draw on. If None, a new figure+axes are created.
        """
        axes.step(self.record.time, self.record.capital, color="black", where="mid")
        axes.set_ylabel("Capital")

    @helper.pre_plot(nrows=1, ncols=1)
    def plot_number_of_positions(self, axes: plt.Axes) -> None:
        """
        Plot the number of open positions over time.

        Parameters
        ----------
        axes : matplotlib.axes.Axes, optional
            Axes to draw on. If None, a new figure+axes are created.
        """
        axes.step(
            self.record.time,
            self.record.number_of_concurent_positions,
            color="black",
            where="mid",
        )
        axes.set_ylabel("Number of open positions")

    @helper.pre_plot(nrows=1, ncols=1)
    def plot_prices(self, axes: plt.Axes) -> None:
        """
        Plot the market bid and ask prices over time.

        Parameters
        ----------
        axes : matplotlib.axes.Axes, optional
            Axes to draw on. If None, a new figure+axes are created.

        """
        axes.plot(self.dates, self.market.ask.open, label="Ask-Open", color="C0")
        axes.plot(self.dates, self.market.bid.open, label="Bid-Open", color="C1")
        axes.ticklabel_format(style="plain", axis="y")  # Prevent y-axis offset
        # Legend (bottom plot only)
        axes.legend(loc="upper left")
        axes.set_ylabel("Prices")

    def plot(self, *plot_type) -> plt.Figure:
        """
        Plot the portfolio's performance, including equity, capital at risk, capital,
        number of open positions, and market prices.

        Returns
        -------
        None
        """
        if len(plot_type) == 0:
            plot_type = (
                "equity",
                "capital_at_risk",
                "capital",
                "number_of_positions",
                "prices",
            )
        else:
            plot_type = plot_type[0] if isinstance(plot_type[0], tuple) else plot_type

        if not isinstance(plot_type, tuple):
            plot_type = (plot_type,)

        n_plots = len(plot_type)

        with plt.style.context(mps):
            _, axs = plt.subplots(
                nrows=n_plots, ncols=1, figsize=(12, 2 * n_plots), sharex=True
            )

            plot_methods = {
                "equity": self.plot_equity,
                "capital_at_risk": self.plot_capital_at_risk,
                "capital": self.plot_capital,
                "number_of_positions": self.plot_number_of_positions,
                "prices": self.plot_prices,
            }

            for ax, plot in zip(axs, plot_type):
                plot_methods[plot](ax=ax, show=False)

            plt.tight_layout()
            plt.show()
