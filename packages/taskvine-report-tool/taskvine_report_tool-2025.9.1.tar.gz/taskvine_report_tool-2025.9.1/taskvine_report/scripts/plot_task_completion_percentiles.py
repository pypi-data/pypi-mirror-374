#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from configs import PNG_DIR, CSV_DIR, aggregate_template_csvs, save_aggregated_csv, get_repeat_dirs_by_ids, WORKFLOW

def read_percentiles_csv(p: Path):
    df = pd.read_csv(p)
    if df.empty:
        raise ValueError('task_completion_percentiles.csv is empty')
    if len(df.columns) < 2:
        raise ValueError('Expected at least two columns: percentile and time')
    # Prefer known column names; fallback to first two columns
    if {'Percentile', 'Completion Time'}.issubset(df.columns):
        x = df['Percentile'].values
        y = df['Completion Time'].values
    else:
        x = df.iloc[:, 0].values
        y = df.iloc[:, 1].values
    return x, y

def aggregate_repeat_data(workflow: str, templates: list, repeat_dirs: list):
    """Aggregate per-template CSVs across provided repeats for a workflow."""
    all_data = []
    
    for repeat_name, repeat_workflow_dir in repeat_dirs:
        print(f"Processing {repeat_name}...")
        
        # Aggregate templates for each repeat
        try:
            agg = aggregate_template_csvs(
                base_dir=repeat_workflow_dir,
                templates=templates,
                relative_csv='task_completion_percentiles.csv',
                rename_map={'Percentile': 'percentile', 'Completion Time': 'time'},
                required_cols=['percentile', 'time'],
                add_template_col=True,
            )
            
            # Add repeat label
            agg['repeat'] = repeat_name
            all_data.append(agg)
            
        except Exception as e:
            print(f"Warning: Failed to process {repeat_name}: {e}")
            continue
    
    if not all_data:
        raise ValueError("No valid repeat data found")
    
    # Concatenate across repeats
    combined_data = pd.concat(all_data, ignore_index=True)
    return combined_data

def calculate_statistics_with_error(df: pd.DataFrame, templates: list):
    """Compute per-template mean/std/min/max for each percentile 0..100."""
    target_percentiles = np.arange(0, 101, 1, dtype=int)
    stats_data = {}
    
    for tmpl in templates:
        template_data = df[df['template'] == tmpl].copy()
        if template_data.empty:
            stats_data[tmpl] = {
                'mean': np.full_like(target_percentiles, np.nan, dtype=float),
                'std': np.full_like(target_percentiles, np.nan, dtype=float),
                'min': np.full_like(target_percentiles, np.nan, dtype=float),
                'max': np.full_like(target_percentiles, np.nan, dtype=float)
            }
            continue
        
        # Compute stats for each percentile
        means = []
        stds = []
        mins = []
        maxs = []
        
        for p in target_percentiles:
            p_data = template_data[template_data['percentile'] == p]['time'].values
            if len(p_data) > 0:
                means.append(np.mean(p_data))
                stds.append(np.std(p_data))
                mins.append(np.min(p_data))
                maxs.append(np.max(p_data))
            else:
                means.append(np.nan)
                stds.append(np.nan)
                mins.append(np.nan)
                maxs.append(np.nan)
        
        # Interpolate missing percentiles
        means = np.array(means)
        stds = np.array(stds)
        mins = np.array(mins)
        maxs = np.array(maxs)
        
        # Interpolate missing values along 0..100
        valid_mask = ~np.isnan(means)
        if np.sum(valid_mask) > 1:
            means = np.interp(target_percentiles, target_percentiles[valid_mask], means[valid_mask])
            stds = np.interp(target_percentiles, target_percentiles[valid_mask], stds[valid_mask])
            mins = np.interp(target_percentiles, target_percentiles[valid_mask], mins[valid_mask])
            maxs = np.interp(target_percentiles, target_percentiles[valid_mask], maxs[valid_mask])
        elif np.sum(valid_mask) == 1:
            # Only one valid point, broadcast
            valid_idx = np.where(valid_mask)[0][0]
            means = np.full_like(target_percentiles, means[valid_idx], dtype=float)
            stds = np.full_like(target_percentiles, stds[valid_idx], dtype=float)
            mins = np.full_like(target_percentiles, mins[valid_idx], dtype=float)
            maxs = np.full_like(target_percentiles, maxs[valid_idx], dtype=float)
        
        # Enforce time==0 at percentile 0
        means[0] = 0.0
        stds[0] = 0.0
        mins[0] = 0.0
        maxs[0] = 0.0
        
        stats_data[tmpl] = {
            'mean': means,
            'std': stds,
            'min': mins,
            'max': maxs
        }
    
    return stats_data



def plot_from_csv_data(df: pd.DataFrame, templates: list):
    """Plot one figure with all template mean curves and std shading."""
    sns.set(style='whitegrid')
    plt.figure(figsize=(12, 6))
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(templates)))
    percentiles = df['Percentile'].values
    
    for i, tmpl in enumerate(templates):
        # 检查不同的列名模式
        mean_col = f'{tmpl}_mean'
        time_col = f'{tmpl}_time'
        completion_col = 'Completion_Time'
        
        if mean_col in df.columns:
            # 多repeat模式：有均值数据
            mean_times = df[mean_col].values
            std_col = f'{tmpl}_std'
            
            # 绘制均值线
            plt.plot(percentiles, mean_times, 
                    color=colors[i], linewidth=2, label=tmpl, alpha=0.8)
            
            # 如果有标准差数据，绘制误差范围
            if std_col in df.columns:
                std_times = df[std_col].values
                plt.fill_between(percentiles, 
                                mean_times - std_times, 
                                mean_times + std_times,
                                color=colors[i], alpha=0.2)
        elif time_col in df.columns:
            # Single-repeat wide format
            times = df[time_col].values
            plt.plot(percentiles, times, 
                    color=colors[i], linewidth=2, label=tmpl, alpha=0.8)
        elif completion_col in df.columns:
            # Single-repeat single-template format
            times = df[completion_col].values
            plt.plot(percentiles, times, 
                    color=colors[i], linewidth=2, label='template', alpha=0.8)
    
    plt.xlabel('Percentile (%)', fontsize=12)
    plt.ylabel('Completion Time (s)', fontsize=12)
    plt.title('Task Completion Percentiles', fontsize=14, pad=16)
    plt.xlim(0, 100)
    plt.grid(True, axis='y', alpha=0.3)
    plt.legend(loc='best', fontsize=9, frameon=True)
    plt.tight_layout()
    out_png = PNG_DIR / 'task_completion_percentiles.png'
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    print(f'Plot saved to: {out_png}')

def main():
    parser = argparse.ArgumentParser(description='Plot task completion percentiles (x: 0-100%, y: time)')
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

        combined_data = aggregate_repeat_data(args.workflow, args.templates, repeat_dirs)
        stats_data = calculate_statistics_with_error(combined_data, args.templates)

        target_percentiles = np.arange(0, 101, 1, dtype=int)
        origin_data = {'Percentile': target_percentiles}
        for tmpl in args.templates:
            if tmpl in stats_data:
                stats = stats_data[tmpl]
                origin_data[f'{tmpl}_mean'] = stats['mean']
                origin_data[f'{tmpl}_std'] = stats['std']
                origin_data[f'{tmpl}_min'] = stats['min']
                origin_data[f'{tmpl}_max'] = stats['max']

        origin_df = pd.DataFrame(origin_data)
        out_csv = CSV_DIR / 'task_completion_percentiles.csv'
        origin_df.to_csv(out_csv, index=False)
        print(f'CSV saved to: {out_csv}')

        plot_from_csv_data(origin_df, args.templates)
        print('Done!')
                
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
