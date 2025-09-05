import numpy as np


class BaseIndicator:
    def _unify_axes_legend(self, *axes):

        lines = []
        labels = []
        for ax in axes:
            line, label = ax.get_legend_handles_labels()
            lines += line
            labels += label

        unique = dict(zip(labels, lines))
        axes[0].legend(unique.values(), unique.keys(), loc="upper left")

    def _add_region_to_ax(self, ax):
        regions = np.asarray(self._cpp_regions)

        ax.fill_between(
            self.market.dates,
            0,
            1,
            where=regions == 1,
            # step='mid',
            color="green",
            alpha=0.2,
            label="Market Range",
            transform=ax.get_xaxis_transform(),
        )

        ax.fill_between(
            self.market.dates,
            0,
            1,
            where=regions == -1,
            # step='mid',
            color="red",
            alpha=0.2,
            label="Market Range",
            transform=ax.get_xaxis_transform(),
        )
