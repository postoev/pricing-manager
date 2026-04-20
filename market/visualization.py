"""Visualization for Market simulation results."""
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List, Tuple

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MaxNLocator
import numpy as np

if TYPE_CHECKING:
    from .simulation import Market
    from .seller import Seller
    from .goods import Good

# Type alias
EventMarkers = Dict[str, List[Tuple[int, str]]]


def plot_simulation(market: 'Market',
                    save_path: str = 'market_simulation.png') -> None:
    n_days     = market.day
    days       = list(range(1, n_days + 1))
    good_names = list(market.goods.keys())
    n_goods    = len(good_names)

    seller_color = _seller_palette(market)
    event_markers = _build_event_markers(market, good_names)

    fig = plt.figure(figsize=(14, 4 * n_goods + 4))
    fig.patch.set_facecolor('#F7F9FC')

    outer    = gridspec.GridSpec(2, 1, figure=fig,
                                 height_ratios=[n_goods, 1], hspace=0.45)
    top_grid = gridspec.GridSpecFromSubplotSpec(
        n_goods, 2, subplot_spec=outer[0], hspace=0.55, wspace=0.35)
    bot_grid = gridspec.GridSpecFromSubplotSpec(
        1, 2, subplot_spec=outer[1], wspace=0.35)

    for row, gname in enumerate(good_names):
        carriers = [s for s in market.sellers if gname in s.goods]
        _plot_prices(
            fig.add_subplot(top_grid[row, 0]),
            market.goods[gname], gname, carriers, n_days, seller_color,
            event_markers[gname],
        )
        _plot_shares(
            fig.add_subplot(top_grid[row, 1]),
            gname, carriers, days, n_days, seller_color,
            event_markers[gname],
        )

    _plot_cumulative_profit(
        fig.add_subplot(bot_grid[0, 0]),
        market.sellers, days, n_days, seller_color,
    )
    _plot_daily_profit(
        fig.add_subplot(bot_grid[0, 1]),
        market.sellers, days, n_days, seller_color,
    )

    fig.suptitle('Market Simulator', fontsize=14, fontweight='bold', y=1.01)
    plt.savefig(save_path, dpi=120, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    print(f"\nPlot saved → {save_path}")


# ---------------------------------------------------------------------------
# Per-panel helpers
# ---------------------------------------------------------------------------

def _plot_prices(
    ax,
    good:          'Good',
    gname:         str,
    carriers:      List['Seller'],
    n_days:        int,
    seller_color:  Dict[str, tuple],
    event_markers: List[Tuple[int, str]],
) -> None:
    ax.set_facecolor('#FAFAFA')
    for s in carriers:
        prices = s.hist_price[gname]
        if not prices:
            continue
        s_days = list(range(s.start_day, s.start_day + len(prices)))
        color  = seller_color[s.name]
        ax.plot(s_days, prices, color=color, linewidth=1.4, alpha=0.4)
        sd_sm, sm = _smooth(prices, s_days)
        ax.plot(sd_sm, sm, color=color, linewidth=2.2, label=s.name)

    ax.axhline(good.cost, color='#E74C3C', linestyle='--', linewidth=1.2,
               label=f'cost={good.cost:.0f}')
    ax.axhline(good.monopoly_optimal_price(), color='#27AE60', linestyle=':',
               linewidth=1.5, label=f'opt≈{good.monopoly_optimal_price():.0f}')

    _add_event_vlines(ax, event_markers)
    _style_ax(ax, f'{gname}  —  цены продавцов', 'Цена')


def _plot_shares(
    ax,
    gname:         str,
    carriers:      List['Seller'],
    days:          List[int],
    n_days:        int,
    seller_color:  Dict[str, tuple],
    event_markers: List[Tuple[int, str]],
) -> None:
    ax.set_facecolor('#FAFAFA')

    sales_matrix = np.array([s.sales_series(gname, n_days) for s in carriers])
    totals       = sales_matrix.sum(axis=0)
    shares       = sales_matrix / np.where(totals == 0, 1, totals) * 100

    bottom = np.zeros(n_days)
    for idx, s in enumerate(carriers):
        ax.fill_between(days, bottom, bottom + shares[idx],
                        color=seller_color[s.name], alpha=0.75, label=s.name)
        bottom += shares[idx]

    _add_event_vlines(ax, event_markers)
    ax.set_ylim(0, 100)
    _style_ax(ax, f'{gname}  —  доля рынка', 'Доля рынка, %')


def _plot_cumulative_profit(
    ax,
    sellers:      List['Seller'],
    days:         List[int],
    n_days:       int,
    seller_color: Dict[str, tuple],
) -> None:
    ax.set_facecolor('#FAFAFA')
    for s in sellers:
        ax.plot(days, np.cumsum(s.profit_series(n_days)),
                color=seller_color[s.name], linewidth=2.5, label=s.name)
    _style_ax(ax, 'Накопленная прибыль', 'Прибыль')


def _plot_daily_profit(
    ax,
    sellers:      List['Seller'],
    days:         List[int],
    n_days:       int,
    seller_color: Dict[str, tuple],
) -> None:
    ax.set_facecolor('#FAFAFA')
    for s in sellers:
        daily = s.profit_series(n_days)
        ax.plot(days, daily, color=seller_color[s.name], alpha=0.25, linewidth=1)
        d_sm, sm_d = _smooth(daily, days, w=7)
        ax.plot(d_sm, sm_d, color=seller_color[s.name], linewidth=2.2, label=s.name)
    _style_ax(ax, 'Дневная прибыль (сглаженная)', 'Прибыль / день')


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------

def _style_ax(ax, title: str, ylabel: str) -> None:
    ax.set_title(title, fontsize=10, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=8)
    ax.set_xlabel('День', fontsize=8)
    ax.legend(fontsize=7, loc='upper right')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=8))
    ax.grid(axis='y', alpha=0.3)


def _add_event_vlines(ax, markers: List[Tuple[int, str]]) -> None:
    for day, label in markers:
        ax.axvline(day, color='#888', linestyle=':', linewidth=1.2)
        ax.text(day + 0.3, 0.95, label,
                transform=ax.get_xaxis_transform(),
                fontsize=6, color='#555', va='top')


def _smooth(arr, x, w: int = 5):
    """Return (x_aligned, smoothed) using valid convolution — no edge artifacts."""
    arr = np.asarray(arr, dtype=float)
    x   = np.asarray(x)
    if len(arr) < w:
        return x, arr
    sm     = np.convolve(arr, np.ones(w) / w, mode='valid')
    offset = (w - 1) // 2
    return x[offset: offset + len(sm)], sm


def _seller_palette(market: 'Market') -> Dict[str, tuple]:
    names = list(dict.fromkeys(
        [s.name for s in market.sellers] +
        [e.seller for e in market.events if e.kind == 'new_seller']
    ))
    palette = plt.cm.tab10.colors
    return {name: palette[i % 10] for i, name in enumerate(names)}


def _build_event_markers(market: 'Market',
                          good_names: List[str]) -> EventMarkers:
    markers: EventMarkers = {g: [] for g in good_names}
    for ev in market.events:
        label = f"+{ev.seller}" if ev.kind == 'new_seller' else f"{ev.seller}+{','.join(ev.goods)}"
        for g in ev.goods:
            if g in markers:
                markers[g].append((ev.day, label))
    return markers
