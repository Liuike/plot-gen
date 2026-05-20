from __future__ import annotations

import argparse
from pathlib import Path
import textwrap
from typing import Iterable

import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, MaxNLocator
import pandas as pd


STYLE_PRESETS = {
    "cs-research": {
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "legend.fontsize": 9,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "figure.dpi": 140,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.04,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.28,
        "grid.linewidth": 0.6,
        "lines.linewidth": 1.8,
        "lines.markersize": 4.5,
        "patch.linewidth": 0.6,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    }
}

PALETTE = [
    "#1f77b4",
    "#d62728",
    "#2ca02c",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]


def require_columns(df: pd.DataFrame, columns: Iterable[str]) -> None:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        available = ", ".join(df.columns)
        raise SystemExit(f"Missing column(s): {', '.join(missing)}. Available columns: {available}")


def ensure_numeric(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    df = df.copy()
    for col in columns:
        df[col] = pd.to_numeric(df[col], errors="raise")
    return df


def apply_style(name: str) -> None:
    if name not in STYLE_PRESETS:
        choices = ", ".join(STYLE_PRESETS)
        raise SystemExit(f"Unknown style '{name}'. Available styles: {choices}")
    plt.rcParams.update(STYLE_PRESETS[name])


def finish_plot(ax: plt.Axes, args: argparse.Namespace) -> None:
    if args.title:
        ax.set_title(args.title, pad=8)
    if args.xlabel:
        ax.set_xlabel(args.xlabel)
    if args.ylabel:
        ax.set_ylabel(args.ylabel)
    if args.ylim:
        ax.set_ylim(args.ylim)
    if args.yticks:
        ax.set_yticks(args.yticks)
    else:
        ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
    if args.x_rotate:
        ax.tick_params(axis="x", labelrotation=args.x_rotate)
    ax.margins(x=0.02)
    ax.legend(frameon=False)


def apply_line_grid(ax: plt.Axes, minor_grid: bool) -> None:
    ax.minorticks_on()
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.grid(True, which="major", axis="both", alpha=0.28, linewidth=0.6)
    if minor_grid:
        ax.grid(True, which="minor", axis="both", alpha=0.14, linewidth=0.4)
    else:
        ax.grid(False, which="minor", axis="both")


def highlight_minimum(ax: plt.Axes, x_values: pd.Series, y_values: pd.Series, color: str) -> None:
    min_index = y_values.idxmin()
    ax.scatter(
        x_values.loc[min_index],
        y_values.loc[min_index],
        s=42,
        marker="o",
        facecolors="white",
        edgecolors=color,
        linewidths=1.4,
        zorder=4,
        label="_nolegend_",
    )


def hide_legend(ax: plt.Axes) -> None:
    legend = ax.get_legend()
    if legend:
        legend.remove()


def wrap_label(label: object, width: int) -> str:
    label = str(label)
    if width <= 0:
        return label
    return "\n".join(
        textwrap.wrap(
            label,
            width=width,
            break_long_words=False,
            break_on_hyphens=False,
        )
    )


def apply_bar_x_labels(ax: plt.Axes, labels: Iterable[object], args: argparse.Namespace) -> None:
    labels = [str(label) for label in labels]
    longest_label = max((len(label) for label in labels), default=0)
    should_wrap = args.bar_label_wrap > 0 and not args.x_rotate and longest_label > args.bar_label_wrap
    display_labels = [wrap_label(label, args.bar_label_wrap) for label in labels] if should_wrap else labels

    ax.set_xticks(range(len(display_labels)))
    ax.set_xticklabels(display_labels)

    if should_wrap:
        ax.tick_params(axis="x", pad=4)


def plot_line(df: pd.DataFrame, args: argparse.Namespace) -> None:
    require_columns(df, [args.x, *args.y])
    if args.group:
        require_columns(df, [args.group])
    df = ensure_numeric(df, args.y)

    fig, ax = plt.subplots(figsize=(args.width, args.height))

    if args.group:
        for color_index, (group_name, group_df) in enumerate(df.groupby(args.group, sort=False)):
            for y_col in args.y:
                color = PALETTE[color_index % len(PALETTE)]
                label = f"{group_name}: {y_col}" if len(args.y) > 1 else str(group_name)
                ax.plot(
                    group_df[args.x],
                    group_df[y_col],
                    marker=args.marker,
                    color=color,
                    label=label,
                )
                if args.highlight_minima:
                    highlight_minimum(ax, group_df[args.x], group_df[y_col], color)
    else:
        for color_index, y_col in enumerate(args.y):
            color = PALETTE[color_index % len(PALETTE)]
            ax.plot(
                df[args.x],
                df[y_col],
                marker=args.marker,
                color=color,
                label=y_col,
            )
            if args.highlight_minima:
                highlight_minimum(ax, df[args.x], df[y_col], color)

    if args.xticks_from_data:
        ax.set_xticks(df[args.x].drop_duplicates())
    apply_line_grid(ax, args.minor_grid)
    finish_plot(ax, args)
    save_figure(fig, args.output)


def plot_bar(df: pd.DataFrame, args: argparse.Namespace) -> None:
    require_columns(df, [args.x, *args.y])
    if args.group:
        require_columns(df, [args.group])
    df = ensure_numeric(df, args.y)
    single_measure = not args.group and len(args.y) == 1

    fig, ax = plt.subplots(figsize=(args.width, args.height))

    if args.group:
        if len(args.y) != 1:
            raise SystemExit("Grouped bar charts require exactly one --y column.")
        pivot = df.pivot(index=args.x, columns=args.group, values=args.y[0])
        pivot.plot(kind="bar", ax=ax, color=PALETTE[: len(pivot.columns)], width=0.78)
        apply_bar_x_labels(ax, pivot.index, args)
    else:
        x_labels = df[args.x].astype(str)
        if len(args.y) == 1:
            positions = range(len(df))
            ax.bar(positions, df[args.y[0]], color=PALETTE[0], label=args.y[0], width=0.72)
            apply_bar_x_labels(ax, x_labels, args)
        else:
            positions = range(len(df))
            total_width = 0.78
            bar_width = total_width / len(args.y)
            offsets = [i * bar_width - total_width / 2 + bar_width / 2 for i in range(len(args.y))]
            for color_index, (offset, y_col) in enumerate(zip(offsets, args.y)):
                ax.bar(
                    [pos + offset for pos in positions],
                    df[y_col],
                    width=bar_width,
                    color=PALETTE[color_index % len(PALETTE)],
                    label=y_col,
                )
            apply_bar_x_labels(ax, x_labels, args)

    finish_plot(ax, args)
    if single_measure:
        hide_legend(ax)
    ax.grid(axis="y")
    ax.grid(axis="x", visible=False)
    fig.subplots_adjust(bottom=args.bar_bottom)
    save_figure(fig, args.output)


def save_figure(fig: plt.Figure, output: str) -> None:
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    print(f"Wrote {output_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate academic-style plots from CSV files.")
    subparsers = parser.add_subparsers(dest="chart_type", required=True)

    for chart_type in ("line", "bar"):
        sub = subparsers.add_parser(chart_type, help=f"Create a {chart_type} chart")
        sub.add_argument("csv", help="Input CSV file")
        sub.add_argument("--x", required=True, help="Column to use for the x axis")
        sub.add_argument("--y", required=True, nargs="+", help="One or more numeric y-axis columns")
        sub.add_argument("--group", help="Optional grouping column")
        sub.add_argument("--title", default="", help="Plot title")
        sub.add_argument("--xlabel", default="", help="X-axis label")
        sub.add_argument("--ylabel", default="", help="Y-axis label")
        sub.add_argument("--ylim", type=float, nargs=2, metavar=("MIN", "MAX"), help="Y-axis limits")
        sub.add_argument("--yticks", type=float, nargs="+", help="Explicit y-axis tick values")
        sub.add_argument("--output", required=True, help="Output image path, e.g. artifacts/plot.pdf")
        sub.add_argument("--style", default="cs-research", choices=sorted(STYLE_PRESETS), help="Plot style preset")
        sub.add_argument("--width", type=float, default=5.4, help="Figure width in inches")
        sub.add_argument("--height", type=float, default=3.2, help="Figure height in inches")
        sub.add_argument("--x-rotate", type=float, default=0, help="Rotate x-axis labels by this many degrees")

    subparsers.choices["line"].add_argument("--marker", default="", help="Line marker style")
    subparsers.choices["line"].add_argument(
        "--highlight-minima",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Mark the minimum value of each line series.",
    )
    subparsers.choices["line"].add_argument(
        "--minor-grid",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Show minor gridlines on line charts.",
    )
    subparsers.choices["line"].add_argument(
        "--xticks-from-data",
        action="store_true",
        help="Use only the x values present in the input CSV as x-axis ticks.",
    )
    subparsers.choices["bar"].add_argument(
        "--bar-label-wrap",
        type=int,
        default=14,
        help="Wrap bar x-axis labels after this many characters. Use 0 to disable.",
    )
    subparsers.choices["bar"].add_argument(
        "--bar-bottom",
        type=float,
        default=0.24,
        help="Bottom figure margin for bar labels, as a fraction of figure height.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    apply_style(args.style)
    df = pd.read_csv(args.csv)

    if args.chart_type == "line":
        plot_line(df, args)
    elif args.chart_type == "bar":
        plot_bar(df, args)


if __name__ == "__main__":
    main()
