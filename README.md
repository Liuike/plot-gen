# Academic Plot Generator

Small matplotlib-based CLI for generating publication-ready line charts and bar graphs from CSV files.

## Setup

Create and use the local virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

All dependencies stay inside `.venv`.

## Usage

Line chart:

```powershell
.\.venv\Scripts\python plotgen.py line examples\line_example.csv --x epoch --y accuracy loss --title "Training Curves" --xlabel "Epoch" --ylabel "Score" --output artifacts\line_example.png
```

Line charts use continuous lines by default, show minor gridlines on both axes, and mark the minimum value of each series with a hollow marker.

Bar graph:

```powershell
.\.venv\Scripts\python plotgen.py bar examples\bar_example.csv --x method --y score --title "Method Comparison" --xlabel "Method" --ylabel "Accuracy" --output artifacts\bar_example.png
```

Useful options:

- `--y`: one or more numeric columns to plot.
- `--group`: optional grouping column. For line charts this creates one line per group. For bar charts this creates grouped bars.
- `--output`: output path. Supported formats depend on matplotlib, including `.png`, `.pdf`, and `.svg`.
- `--style`: currently `cs-research`.
- `--ylim MIN MAX`: set the y-axis range, for example `--ylim 0 2`.
- `--yticks`: set explicit y-axis ticks, for example `--yticks 0 1 2`.
- `--no-highlight-minima`: for line charts, do not mark the minimum point of each series.
- `--no-minor-grid`: for line charts, show only major gridlines.
- `--bar-label-wrap`: bar charts automatically wrap long x-axis labels after 14 characters. Set this to another width, or use `0` to disable wrapping.
- `--x-rotate`: manually rotate x-axis labels. For bar charts, manual rotation takes priority over automatic wrapping.

## CSV Format

For a line chart, use one x-axis column and one or more numeric y-axis columns:

```csv
epoch,accuracy,loss
1,0.62,1.08
2,0.71,0.84
```

For a bar chart, use a category column and one or more numeric y-axis columns:

```csv
method,score
Baseline,0.78
Ours,0.86
```
