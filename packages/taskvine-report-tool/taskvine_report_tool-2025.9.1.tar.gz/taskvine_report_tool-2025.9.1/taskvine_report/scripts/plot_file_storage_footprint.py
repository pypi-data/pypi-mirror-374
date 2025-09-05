#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from configs import PNG_DIR, CSV_DIR, get_repeat_dirs_by_ids, WORKFLOW


def read_activation_values(csv_path: Path) -> np.ndarray:
    """Read activation durations from CSV and return as a sorted ascending 1D numpy array."""
    df = pd.read_csv(csv_path)
    if df.empty:
        return np.array([], dtype=float)
    if 'time_activation' in df.columns:
        vals = pd.to_numeric(df['time_activation'], errors='coerce').values
    else:
        vals = pd.to_numeric(df.iloc[:, -1], errors='coerce').values
    vals = vals[~np.isnan(vals)]
    if vals.size == 0:
        return np.array([], dtype=float)
    vals = np.sort(vals.astype(float))
    return vals


def compute_cdf_wide(repeat_dirs: list, templates: list) -> pd.DataFrame:
    """Compute CDF curves (x: time seconds, y: percentage 0..100) for each template.

    Strategy:
    - Pool activation durations across repeats per template
    - Compute t_of_p for p=0..100 (percentile times)
    - Build a unified time grid as the sorted union of all templates' t_of_p
    - For each template, interpolate percentage p at each time in the grid
    Output columns: ['time', <template1>, <template2>, ...] where values are percentages (0..100)
    """
    # Collect per-repeat activations per template
    per_repeat = {t: [] for t in templates}
    warnings_list = []
    for repeat_name, repeat_workflow_dir in repeat_dirs:
        print(f"Processing {repeat_name}...")
        for tmpl in templates:
            csv_path = repeat_workflow_dir / tmpl / 'csv-files' / 'file_replica_activation_intervals.csv'
            if not csv_path.exists():
                warnings_list.append(f"Missing CSV: {csv_path}")
                continue
            try:
                sorted_vals = read_activation_values(csv_path)
                if sorted_vals.size > 0:
                    per_repeat[tmpl].append(sorted_vals)
                else:
                    warnings_list.append(f"Empty or invalid CSV: {csv_path}")
            except Exception as e:
                warnings_list.append(f"Failed to process {csv_path}: {e}")
                continue

    # Build global time grid using integer seconds from 0 to ceil(max_time)
    all_times = []
    max_time = 0.0
    for arrays in per_repeat.values():
        for arr in arrays:
            if arr.size == 0:
                continue
            all_times.append(arr.astype(float))
            mt = float(np.max(arr))
            if mt > max_time:
                max_time = mt

    if not all_times:
        if warnings_list:
            print("Warnings during processing:")
            for msg in warnings_list:
                print(f"  - {msg}")
        raise ValueError("No valid activation data found")

    max_time_int = int(np.ceil(max_time))
    time_grid = np.arange(0, max_time_int + 1, 1, dtype=float)

    # For each template, compute per-repeat empirical CDF at each time, then mean/std across repeats
    df_wide = pd.DataFrame({'time': time_grid})
    for tmpl in templates:
        arrays = per_repeat.get(tmpl, [])
        if not arrays:
            df_wide[tmpl] = np.nan
            df_wide[f'{tmpl}_max'] = np.nan
            df_wide[f'{tmpl}_min'] = np.nan
            continue
        per_rep_p = []
        for arr in arrays:
            data = np.sort(arr.astype(float))
            n = data.size
            if n == 0:
                continue
            # count of values <= t for each t in time_grid
            counts = np.searchsorted(data, time_grid, side='right')
            p_at_time = counts / n * 100.0
            per_rep_p.append(p_at_time)
        mat = np.vstack(per_rep_p) if per_rep_p else np.empty((0, time_grid.size))
        mean_p = np.nanmean(mat, axis=0) if mat.size > 0 else np.full(time_grid.size, np.nan)
        min_p = np.nanmin(mat, axis=0) if mat.size > 0 else np.full(time_grid.size, np.nan)
        max_p = np.nanmax(mat, axis=0) if mat.size > 0 else np.full(time_grid.size, np.nan)
        mean_p = np.clip(np.round(mean_p, 6), 0.0, 100.0)
        min_p = np.clip(np.round(min_p, 6), 0.0, 100.0)
        max_p = np.clip(np.round(max_p, 6), 0.0, 100.0)
        df_wide[tmpl] = mean_p
        df_wide[f'{tmpl}_max'] = max_p
        df_wide[f'{tmpl}_min'] = min_p
    if warnings_list:
        print("Warnings during processing:")
        for msg in warnings_list:
            print(f"  - {msg}")
    return df_wide


def plot_from_wide(df_wide: pd.DataFrame, templates: list):
    sns.set(style='whitegrid')
    plt.figure(figsize=(12, 6))
    colors = plt.cm.Set3(np.linspace(0, 1, len(templates)))
    x = df_wide['time'].values
    for i, tmpl in enumerate(templates):
        if tmpl not in df_wide.columns:
            continue
        y = df_wide[tmpl].values
        plt.plot(x, y, color=colors[i], linewidth=2, label=tmpl, alpha=0.85)
        max_col = f'{tmpl}_max'
        min_col = f'{tmpl}_min'
        if max_col in df_wide.columns and min_col in df_wide.columns:
            upper = df_wide[max_col].values
            lower = df_wide[min_col].values
            if np.any(~np.isnan(upper)) or np.any(~np.isnan(lower)):
                upper = np.minimum(100.0, np.where(np.isnan(upper), y, upper))
                lower = np.maximum(0.0, np.where(np.isnan(lower), y, lower))
                plt.fill_between(x, lower, upper, color=colors[i], alpha=0.18)
    plt.xlabel('Activation Duration (s)', fontsize=12)
    plt.ylabel('Replicas (%)', fontsize=12)
    plt.title('File Storage Footprint CDF: Percentage vs Activation Time', fontsize=14, pad=16)
    plt.ylim(0, 100)
    plt.grid(True, alpha=0.3)
    plt.legend(loc='best', fontsize=9, frameon=True)
    plt.tight_layout()
    out_png = PNG_DIR / 'file_storage_footprint.png'
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    print(f'Plot saved to: {out_png}')


def plot_from_stats(origin_df: pd.DataFrame, templates: list):
    sns.set(style='whitegrid')
    plt.figure(figsize=(12, 6))
    colors = plt.cm.Set3(np.linspace(0, 1, len(templates)))
    x = origin_df['Percentile'].values
    for i, tmpl in enumerate(templates):
        mean_col = f'{tmpl}_mean'
        std_col = f'{tmpl}_std'
        if mean_col not in origin_df.columns:
            continue
        y = origin_df[mean_col].values
        plt.plot(x, y, color=colors[i], linewidth=2, label=tmpl, alpha=0.85)
        if std_col in origin_df.columns:
            s = origin_df[std_col].values
            if np.any(~np.isnan(s)):
                plt.fill_between(x, y - s, y + s, color=colors[i], alpha=0.2)

    plt.xlabel('Percentile (%)', fontsize=12)
    plt.ylabel('Replica Activation Duration (s)', fontsize=12)
    plt.title('File Storage Footprint: Replica Activation Duration Percentiles', fontsize=14, pad=16)
    plt.xlim(0, 100)
    plt.grid(True, axis='y', alpha=0.3)
    plt.legend(loc='best', fontsize=9, frameon=True)
    plt.tight_layout()
    out_png = PNG_DIR / 'file_storage_footprint.png'
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    print(f'Plot saved to: {out_png}')


def main():
    parser = argparse.ArgumentParser(
        description='Plot replica activation duration percentiles from file_replica_activation_intervals.csv'
    )
    parser.add_argument('--repeats', nargs='+', type=int, required=True, help='Repeat ids to analyze, e.g., 1 or 1 2 3')
    parser.add_argument('--workflow', default=WORKFLOW, help=f'Workflow name (default: {WORKFLOW})')
    parser.add_argument('--templates', nargs='+', required=True, help='One or more log entry names (templates) to aggregate')
    args = parser.parse_args()

    try:
        print(f"Analyzing repeats: {args.repeats} for workflow: {args.workflow}")
        repeat_dirs = get_repeat_dirs_by_ids(args.repeats, args.workflow)
        if not repeat_dirs:
            print("Error: No repeat experiments found for provided ids")
            sys.exit(1)
        print(f"Found {len(repeat_dirs)} repeat experiments: {[r[0] for r in repeat_dirs]}")

        df_wide = compute_cdf_wide(repeat_dirs, args.templates)
        # Reorder columns: time, and for each template: mean, max, min
        ordered_cols = ['time']
        for tmpl in args.templates:
            if tmpl in df_wide.columns:
                ordered_cols.extend([tmpl, f'{tmpl}_max', f'{tmpl}_min'])
        df_wide = df_wide.reindex(columns=ordered_cols)
        out_csv = CSV_DIR / 'file_storage_footprint.csv'
        df_wide.to_csv(out_csv, index=False)
        print(f'CSV saved to: {out_csv}')

        plot_from_wide(df_wide, args.templates)
        print('Done!')
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()


