#!/usr/bin/env python3
"""
Script to plot the maximum worker storage consumption across all workers mapped to task completion percentiles.

Usage:
    python plot_storage_consumption_peaks.py --repeats 1 2 3 --templates template1 template2

This script reads worker_storage_consumption.csv and task_completion_percentiles.csv files and creates a plot showing:
- X-axis: Task Completion Percentile (%)
- Y-axis: Storage Consumption (GB)
- Curve: Maximum storage consumption among all workers at each percentile
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import argparse
from pathlib import Path
from configs import PNG_DIR, CSV_DIR, get_experiment_path, get_all_repeat_dirs, get_repeat_dirs_by_ids, aggregate_template_csvs, save_aggregated_csv, WORKFLOW

# Import downsample_points from utils module
try:
    from ..utils import downsample_points
except ImportError:
    # Fallback for standalone execution
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from utils import downsample_points


def read_task_percentiles(percentiles_path):
    df = pd.read_csv(percentiles_path)
    
    if df.empty:
        raise ValueError("Task completion percentiles CSV is empty")
    if len(df.columns) < 2:
        raise ValueError("Task completion percentiles CSV should have at least 2 columns")
    
    percentiles = df.iloc[:, 0].values
    completion_times = df.iloc[:, 1].values
    
    print(f"Found {len(percentiles)} percentile data points")
    print(f"Completion time range: {completion_times.min():.2f} - {completion_times.max():.2f} seconds")
    
    return percentiles, completion_times


def compute_peak_series(storage_csv_path: str, percentiles_csv_path: str):
    """Compute max storage consumption (GB) at percentiles 0..100 inclusive.
    Returns: (percentiles ndarray[int 0..100], values ndarray[float])
    """
    storage_df = pd.read_csv(storage_csv_path)
    if storage_df.empty:
        raise ValueError("Storage consumption CSV file is empty")
    time_col = storage_df.columns[0]
    worker_cols = storage_df.columns[1:]
    if len(worker_cols) == 0:
        raise ValueError("No worker columns found in storage CSV")
    
    # Prepare series of max across workers (MB)
    worker_data = storage_df[worker_cols].copy()
    worker_data = worker_data.ffill().fillna(0)
    max_mb = worker_data.max(axis=1).values.astype(float)
    time_points = storage_df[time_col].values.astype(float)
    
    # Load task percentiles to map 0..100 -> time
    dfp = pd.read_csv(percentiles_csv_path)
    if dfp.empty or len(dfp.columns) < 2:
        raise ValueError("Task completion percentiles CSV should have at least 2 columns")
    
    if {'Percentile', 'Completion Time'}.issubset(dfp.columns):
        p = dfp['Percentile'].values
        t = dfp['Completion Time'].values
    else:
        p = dfp.iloc[:, 0].values
        t = dfp.iloc[:, 1].values
    
    mask = ~pd.isna(p) & ~pd.isna(t)
    p = pd.Series(p[mask]).astype(float)
    t = pd.Series(t[mask]).astype(float)
    pt = pd.DataFrame({'p': p, 't': t}).sort_values('p').drop_duplicates(subset=['p'], keep='last')
    
    if 0.0 not in pt['p'].values:
        pt = pd.concat([pd.DataFrame({'p': [0.0], 't': [0.0]}), pt], ignore_index=True)
        pt = pt.sort_values('p')
    
    target_p = np.arange(0, 101, 1, dtype=float)
    times_for_p = np.interp(target_p, pt['p'].values, pt['t'].values,
                             left=pt['t'].values[0], right=pt['t'].values[-1])
    
    # Interpolate max consumption to those times
    order = np.argsort(time_points)
    t_sorted = time_points[order]
    max_mb_sorted = max_mb[order]
    max_gb_sorted = (max_mb_sorted / 1024.0).astype(float)
    y = np.interp(times_for_p, t_sorted, max_gb_sorted,
                  left=max_gb_sorted[0], right=max_gb_sorted[-1])
    y = np.round(y, 6)
    y[0] = 0.0
    return target_p.astype(int), y


def create_plot_single(x_values, max_consumption_gb, template_name=None):
    """Create plot for single template/repeat"""
    sns.set(style="whitegrid")
    plt.figure(figsize=(12, 8))
    
    label = f"Max Storage Consumption"
    if template_name:
        label += f" ({template_name})"
    
    plt.plot(x_values, max_consumption_gb, color='tab:blue', linewidth=1.2, label=label)
    
    plt.xlabel('Task Completion Percentile (%)', fontsize=12)
    plt.title('Maximum Worker Storage Consumption vs Task Completion Percentiles', fontsize=14, pad=20)
    plt.xlim(0, 100)
    plt.ylabel('Storage Consumption (GB)', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    ax = plt.gca()
    max_idx = np.argmax(max_consumption_gb)
    max_x = x_values[max_idx]
    max_y = max_consumption_gb[max_idx]
    stats_text = f'Peak: ({max_x:.1f}%, {max_y:.6f} GB)'
    plt.text(0.02, 0.98, stats_text, transform=ax.transAxes, verticalalignment='top', 
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8), fontsize=10)
    
    if template_name:
        plt.legend()
    
    plt.tight_layout()
    out_png = PNG_DIR / 'storage_consumption_peaks.png'
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {out_png}")


def create_plot_multi_workflows(df_wide: pd.DataFrame):
    """Create plot for multiple workflows aggregated, with separate lines for each template"""
    sns.set(style="whitegrid")
    plt.figure(figsize=(12, 8))
    
    # Get unique templates (columns that are not 'percentile')
    templates = [col for col in df_wide.columns if col != 'percentile']
    colors = plt.cm.Set3(np.linspace(0, 1, len(templates)))
    
    # Plot each template as a separate line
    for i, template in enumerate(templates):
        plt.plot(df_wide['percentile'].values, df_wide[template].values, 
                linewidth=1.2, label=template, color=colors[i])
    
    plt.xlabel('Task Completion Percentile (%)', fontsize=12)
    plt.title('Maximum Worker Storage Consumption vs Task Completion Percentiles (Workflow-Template Comparison)', fontsize=14, pad=20)
    plt.xlim(0, 100)
    plt.ylabel('Storage Consumption (GB)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(loc='best', fontsize=9, frameon=True)
    plt.tight_layout()
    
    out_png = PNG_DIR / 'storage_consumption_peaks.png'
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {out_png}")


def create_plot_with_error_bars(df_aggregated: pd.DataFrame):
    """Create plot with error bars for multiple repeats, with separate lines for each template"""
    sns.set(style="whitegrid")
    plt.figure(figsize=(12, 8))
    
    # Get unique templates
    templates = df_aggregated['template'].unique()
    colors = plt.cm.Set3(np.linspace(0, 1, len(templates)))
    
    # Group by percentile and template, then compute statistics
    percentiles = np.arange(0, 101, 1)
    
    for i, template in enumerate(templates):
        template_data = df_aggregated[df_aggregated['template'] == template]
        means = []
        stds = []
        
        for p in percentiles:
            p_data = template_data[template_data['percentile'] == p]['max_storage_consumption_gb']
            if len(p_data) > 0:
                means.append(p_data.mean())
                stds.append(p_data.std())
            else:
                means.append(0)
                stds.append(0)
        
        means = np.array(means)
        stds = np.array(stds)
        
        # Plot mean line with error bars for this template
        line, = plt.plot(percentiles, means, color=colors[i], linewidth=1.5, label=template)
        plt.fill_between(percentiles, means - stds, means + stds, alpha=0.3, color=colors[i])
    
    plt.xlabel('Task Completion Percentile (%)', fontsize=12)
    plt.title('Maximum Worker Storage Consumption vs Task Completion Percentiles (by Template)', fontsize=14, pad=20)
    plt.xlim(0, 100)
    plt.ylabel('Storage Consumption (GB)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(loc='best', fontsize=9, frameon=True)
    plt.tight_layout()
    
    out_png = PNG_DIR / 'storage_consumption_peaks.png'
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {out_png}")


def main():
    parser = argparse.ArgumentParser(
        description="Plot maximum worker storage consumption vs task completion percentiles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script creates a plot showing the maximum storage consumption
among all workers mapped to task completion percentiles.
        """
    )
    
    parser.add_argument('--repeats', nargs='+', type=int, required=True, help='Repeat ids to analyze, e.g., 1 or 1 2 3')
    parser.add_argument('--workflow', default=WORKFLOW, help=f'Workflow name (default: {WORKFLOW})')
    parser.add_argument('--templates', nargs='+', required=True, help='One or more log entry names (templates) to aggregate')
    parser.add_argument('--points', type=int, default=None, help='Number of points to retain after downsampling (default: no downsampling)')
    parser.add_argument('--workflows', nargs='+', help='One or more workflow names to compare (alternative to --repeats)')
    parser.add_argument('--experiment', help='Experiment name (default from configs)')
    
    args = parser.parse_args()
    
    try:
        # Handle different modes based on arguments
        if args.workflows and len(args.workflows) > 0:
            # Multi-workflow comparison mode
            print("Multi-workflow comparison mode")
            wide = pd.DataFrame({'percentile': np.arange(0, 101, 1, dtype=int)})
            
            for workflow in args.workflows:
                workflow_dir = get_experiment_path(repeat_id=3, workflow=workflow)  # Use default repeat
                
                for template in args.templates:
                    storage_csv_path = workflow_dir / template / 'csv-files' / 'worker_storage_consumption.csv'
                    percentiles_csv_path = workflow_dir / template / 'csv-files' / 'task_completion_percentiles.csv'
                    
                    if not storage_csv_path.exists():
                        print(f"Warning: File '{storage_csv_path}' does not exist, skipping workflow {workflow}, template {template}")
                        continue
                    if not percentiles_csv_path.exists():
                        print(f"Warning: File '{percentiles_csv_path}' does not exist, skipping workflow {workflow}, template {template}")
                        continue
                    
                    pcts, series = compute_peak_series(str(storage_csv_path), str(percentiles_csv_path))
                    series = np.round(series, 6)
                    series[0] = 0.0
                    wide[f"{workflow}_{template}"] = series
            
            # Save aggregated data
            out_csv = save_aggregated_csv(wide, 'storage_consumption_peaks_workflows.csv')
            print(f"Data saved to: {out_csv}")
            
            # Create plot
            create_plot_multi_workflows(wide)
            
        else:
            # Multi-repeat mode with error bars (default mode)
            print(f"Analyzing repeats: {args.repeats} for workflow: {args.workflow}")
            repeat_dirs = get_repeat_dirs_by_ids(args.repeats, args.workflow)
            if not repeat_dirs:
                print("Error: No repeat experiments found for provided ids")
                sys.exit(1)
            print(f"Found {len(repeat_dirs)} repeat experiments: {[r[0] for r in repeat_dirs]}")
            
            all_data = []
            
            for repeat_name, repeat_workflow_dir in repeat_dirs:
                print(f"Processing {repeat_name}...")
                
                for template in args.templates:
                    storage_csv_path = repeat_workflow_dir / template / 'csv-files' / 'worker_storage_consumption.csv'
                    percentiles_csv_path = repeat_workflow_dir / template / 'csv-files' / 'task_completion_percentiles.csv'
                    
                    if not storage_csv_path.exists():
                        print(f"Warning: File '{storage_csv_path}' does not exist, skipping template {template}")
                        continue
                    if not percentiles_csv_path.exists():
                        print(f"Warning: File '{percentiles_csv_path}' does not exist, skipping template {template}")
                        continue
                    
                    pcts, series = compute_peak_series(str(storage_csv_path), str(percentiles_csv_path))
                    series = np.round(series, 6)
                    series[0] = 0.0
                    
                    for pct, val in zip(pcts, series):
                        all_data.append({
                            'repeat_id': int(repeat_name[6:]),  # Extract number from "repeatX"
                            'template': template,
                            'percentile': pct,
                            'max_storage_consumption_gb': val
                        })
            
            if not all_data:
                print("Error: No valid data found for any repeat/template combination")
                sys.exit(1)
            
            df_aggregated = pd.DataFrame(all_data)
            out_csv = save_aggregated_csv(df_aggregated, 'storage_consumption_peaks_repeats.csv')
            print(f"Data saved to: {out_csv}")
            
            # Create plot with error bars
            create_plot_with_error_bars(df_aggregated)
        
        print("Done!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()