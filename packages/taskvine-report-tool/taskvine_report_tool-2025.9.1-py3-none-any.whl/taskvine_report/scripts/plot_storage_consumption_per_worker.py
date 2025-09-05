#!/usr/bin/env python3
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
from pathlib import Path
from configs import PNG_DIR, CSV_DIR, get_repeat_dirs_by_ids, WORKFLOW
import numpy as np

try:
    from ..utils import downsample_points
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from utils import downsample_points

def read_storage_data(p):
    try:
        df = pd.read_csv(p)
        if df.empty:
            raise ValueError("Storage consumption CSV file is empty")
        
        # First column is time, rest are workers
        time_col = df.columns[0]
        worker_cols = df.columns[1:]
        
        if len(worker_cols) == 0:
            raise ValueError("No worker columns found in storage CSV")
        
        # Enforce numeric time and clamp negative
        time_values = pd.to_numeric(df[time_col], errors='coerce').values
        # Clamp to 0
        time_values = np.maximum(time_values, 0.0)
        worker_data = df[worker_cols]
        
        return time_values, worker_data
    except Exception as e:
        print(f"Error reading storage data from {p}: {e}")
        raise

def create_matrix_plot(all_data, templates, repeat_dirs, x_axis='time'):
    """
    Create a matrix-style grid of storage consumption plots.
    Args:
        all_data: Dict of repeat-template to worker series
        templates: Template names
        repeat_dirs: List of (repeat_name, path)
        x_axis: 'time' or 'percentage'
    """
    sns.set(style="whitegrid")
    
    # Grid shape
    n_templates = len(templates)
    n_repeats = len(repeat_dirs)
    
    # Create subplots
    fig, axes = plt.subplots(n_templates, n_repeats, figsize=(4*n_repeats, 4*n_templates))
    
    # Ensure 2D axes for edge cases
    if n_templates == 1 and n_repeats == 1:
        axes = np.array([[axes]])
    elif n_templates == 1:
        axes = axes.reshape(1, -1)
    elif n_repeats == 1:
        axes = axes.reshape(-1, 1)
    
    # Draw each repeat-template
    for i, template in enumerate(templates):
        for j, (repeat_name, _) in enumerate(repeat_dirs):
            ax = axes[i, j]
            
            # Get data for repeat-template
            key = f"{repeat_name}_{template}"
            if key in all_data:
                data = all_data[key]
                
                # Plot worker lines
                for worker, worker_data in data.items():
                    times = []
                    values = []
                    for point in worker_data:
                        time, value = point
                        # Skip nulls
                        if value is None or pd.isna(value) or value == '':
                            continue
                        times.append(time)
                        values.append(value)
                    
                    if times and values:
                        ax.plot(times, values, alpha=0.7, linewidth=1)
                
                # Title
                ax.set_title(f'{template}\n({repeat_name})', fontsize=10)
                
                # Labels
                if x_axis == 'percentage':
                    ax.set_xlabel('Task Completion (%)', fontsize=9)
                else:
                    ax.set_xlabel('Time (s)', fontsize=9)
                ax.set_ylabel('Storage (GB)', fontsize=9)
                
                # Grid
                ax.grid(True, alpha=0.3)
                
                # Legend for small worker counts
                if len(data) <= 10:
                    ax.legend(fontsize=6, frameon=True)
    
    # Layout
    plt.tight_layout()
    
    # Save
    out_png = PNG_DIR / 'storage_consumption_per_worker.png'
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    # Matrix plot saved to: {out_png}

def compress_consecutive_zeros(pts):
    """
    对连续0值段应用边界保留规则：
    - 若该段之前存在任意>0值，则保留该段首个0；
    - 若该段之后存在任意>0值，则保留该段最后一个0；
    - 若两侧都存在>0，则首尾都保留；否则相应端不保留。
    """
    if not pts:
        return pts
    
    result = []
    n = len(pts)
    i = 0
    while i < n:
        t, v = pts[i]
        if v != 0.0:
            result.append((t, v))
            i += 1
            continue
        # v == 0.0，找到零段 [i, j)
        j = i
        while j < n and pts[j][1] == 0.0:
            j += 1
        # 是否在该段之前存在任意>0
        prev_has_pos = any(val > 0.0 for _, val in pts[:i])
        # 是否在该段之后存在任意>0
        next_has_pos = any(val > 0.0 for _, val in pts[j:])
        # 保留首尾零（按需）
        if prev_has_pos:
            result.append(pts[i])  # 段首0
        if next_has_pos:
            if j - 1 != i or not prev_has_pos:
                result.append(pts[j - 1])  # 段末0，避免重复添加同一点
        # 跳过中间零
        i = j
    return result

def mask_consecutive_zeros_keep_edges(arr: np.ndarray) -> np.ndarray:
    """
    针对等间隔横轴（如百分比0..100），对连续为0的段应用边界保留规则：
    - 段前存在任意>0时保留段首0；
    - 段后存在任意>0时保留段末0；
    其余置为NaN，便于CSV写空并在绘图时跳过。
    """
    if arr is None:
        return arr
    values = np.array(arr, dtype=float)
    if values.size == 0:
        return values
    is_zero = values == 0.0
    if not np.any(is_zero):
        return values
    masked = values.copy()
    n = len(masked)
    i = 0
    while i < n:
        if not is_zero[i]:
            i += 1
            continue
        j = i
        while j < n and is_zero[j]:
            j += 1
        prev_has_pos = np.any(values[:i] > 0.0)
        next_has_pos = np.any(values[j:] > 0.0)
        # 全部置NaN
        masked[i:j] = np.nan
        # 恢复首尾零（按需）
        if prev_has_pos:
            masked[i] = 0.0
        if next_has_pos:
            masked[j - 1] = 0.0
        i = j
    return masked

def process_worker_data(xs, wide_df, worker_name):
    """处理单个worker的数据，返回时间-值对"""
    try:
        worker_data = wide_df[worker_name].values
        pts = []
        for t, v in zip(xs, worker_data):
            if pd.notna(v):
                try:
                    t_val = float(t)
                    v_val = float(v)
                    t_val = max(0.0, t_val)
                    t_val = 0.0 if t_val < 0 else t_val
                    pts.append((t_val, v_val))
                except (ValueError, TypeError):
                    continue
        
        # 压缩连续的零值
        pts = compress_consecutive_zeros(pts)
        return pts
    except Exception as e:
        print(f"Error processing worker {worker_name}: {e}")
        return []

def downsample_worker_data(pts, points):
    """对单个worker的数据进行下采样"""
    # 暂时禁用下采样功能以避免错误
    return pts
    # if points and points > 0 and len(pts) > points:
    #     return downsample_points(pts, target_point_count=points, y_index=1)
    # return pts

def read_task_percentiles(percentiles_path):
    """Read task completion percentiles mapping."""
    df = pd.read_csv(percentiles_path)
    
    if df.empty:
        raise ValueError("Task completion percentiles CSV is empty")
    if len(df.columns) < 2:
        raise ValueError("Task completion percentiles CSV should have at least 2 columns")
    
    # Column name fallback
    if {'Percentile', 'Completion Time'}.issubset(df.columns):
        percentiles = df['Percentile'].values
        completion_times = df['Completion Time'].values
    else:
        percentiles = df.iloc[:, 0].values
        completion_times = df.iloc[:, 1].values
    
    # Cleanup and type casting
    mask = ~pd.isna(percentiles) & ~pd.isna(completion_times)
    percentiles = pd.Series(percentiles[mask]).astype(float)
    completion_times = pd.Series(completion_times[mask]).astype(float)
    
    # Sort and deduplicate by percentile
    pt_df = pd.DataFrame({'p': percentiles, 't': completion_times}).sort_values('p').drop_duplicates(subset=['p'], keep='last')
    
    # Ensure 0% exists
    if 0.0 not in pt_df['p'].values:
        pt_df = pd.concat([pd.DataFrame({'p': [0.0], 't': [0.0]}), pt_df], ignore_index=True)
        pt_df = pt_df.sort_values('p')
    
    # Return numpy arrays
    p_values = pt_df['p'].values.astype(float)
    t_values = pt_df['t'].values.astype(float)
    
    # Validate
    if len(p_values) == 0 or len(t_values) == 0:
        raise ValueError("No valid percentile data found")
    
    return p_values, t_values

def interpolate_to_percentages(time_values, storage_values, percentiles_times):
    """Interpolate storage values to given percentile times."""
    # 确保输入是numpy数组
    time_values = np.array(time_values, dtype=float)
    storage_values = np.array(storage_values, dtype=float)
    percentiles_times = np.array(percentiles_times, dtype=float)
    
    # Filter invalid
    valid_mask = ~(np.isnan(time_values) | np.isnan(storage_values))
    if not np.any(valid_mask):
        # No valid data
        return np.zeros_like(percentiles_times)
    
    time_values = time_values[valid_mask]
    storage_values = storage_values[valid_mask]
    
    # Ensure increasing time order
    order = np.argsort(time_values)
    t_sorted = time_values[order]
    storage_sorted = storage_values[order]
    
    # Empty after filtering
    if len(t_sorted) == 0:
        return np.zeros_like(percentiles_times)
    
    # Interpolate to target times
    try:
        interpolated_values = np.interp(
            percentiles_times, 
            t_sorted, 
            storage_sorted,
            left=storage_sorted[0] if len(storage_sorted) > 0 else 0.0, 
            right=storage_sorted[-1] if len(storage_sorted) > 0 else 0.0
        )
        return interpolated_values
    except Exception as e:
        print(f"Interpolation error: {e}")
        print(f"percentiles_times shape: {percentiles_times.shape}, dtype: {percentiles_times.dtype}")
        print(f"t_sorted shape: {t_sorted.shape}, dtype: {t_sorted.dtype}")
        print(f"storage_sorted shape: {storage_sorted.shape}, dtype: {storage_sorted.dtype}")
        # Fallback
        return np.zeros_like(percentiles_times)

def main():
    parser = argparse.ArgumentParser(description="Plot worker storage consumption over time")
    parser.add_argument('--repeats', nargs='+', type=int, required=True, help='Repeat ids to analyze, e.g., 1 or 1 2 3')
    parser.add_argument('--workflow', default=WORKFLOW, help=f'Workflow name (default: {WORKFLOW})')
    parser.add_argument('--templates', nargs='+', required=True, help='One or more log entry names (templates) to aggregate')
    parser.add_argument('--points', type=int, default=None, help='Down-sample each worker to this number of points (default: no downsampling)')
    parser.add_argument('--x-axis', choices=['time', 'percentage'], default='percentage', 
                       help='Choose x-axis: time (seconds) or percentage (task completion)')
    args = parser.parse_args()

    try:
        print(f"Analyzing repeats: {args.repeats} for workflow: {args.workflow}")
        repeat_dirs = get_repeat_dirs_by_ids(args.repeats, args.workflow)
        if not repeat_dirs:
            print("Error: No matching repeat experiments found")
            sys.exit(1)
        print(f"Found {len(repeat_dirs)} repeat experiments: {[r[0] for r in repeat_dirs]}")

        # 收集所有repeat-template的数据
        all_data = {}
        
        for repeat_name, repeat_workflow_dir in repeat_dirs:
            print(f"Processing {repeat_name}...")
            
            for template in args.templates:
                csv_path = repeat_workflow_dir / template / 'csv-files' / 'worker_storage_consumption.csv'
                
                if not csv_path.exists():
                    print(f"Warning: File '{csv_path}' does not exist, skipping...")
                    continue
                
                try:
                    xs, wide = read_storage_data(str(csv_path))
                    worker_cols = wide.columns
                    
                    # 处理每个worker的数据
                    template_data = {}
                    
                    for worker in worker_cols:
                        # 处理原始数据
                        pts = process_worker_data(xs, wide, worker)
                        # 下采样
                        pts = downsample_worker_data(pts, args.points)
                        
                        # 转换为GB并存储
                        template_data[worker] = [(t, round(max(0.0, v / 1024.0), 6)) for t, v in pts]
                    
                    # 保存单个CSV文件
                    if args.x_axis == 'percentage':
                        # 读取百分比映射关系
                        percentiles_path = repeat_workflow_dir / template / 'csv-files' / 'task_completion_percentiles.csv'
                        if percentiles_path.exists():
                            percentiles, completion_times = read_task_percentiles(str(percentiles_path))
                            
                            # 生成0-100的百分比点
                            target_percentages = np.arange(0, 101, 1, dtype=float)
                            
                            # 确保percentiles和completion_times是有效的numpy数组
                            percentiles = np.array(percentiles, dtype=float)
                            completion_times = np.array(completion_times, dtype=float)
                            
                            # 验证数据有效性
                            if len(percentiles) == 0 or len(completion_times) == 0:
                                print(f"Warning: Invalid percentile data for {template}, skipping percentage conversion")
                                continue
                            
                            try:
                                times_for_percentages = np.interp(
                                    target_percentages, 
                                    percentiles, 
                                    completion_times,
                                    left=completion_times[0], 
                                    right=completion_times[-1]
                                )
                            except Exception as e:
                                print(f"Error in percentage interpolation for {template}: {e}")
                                print(f"percentiles: {percentiles}")
                                print(f"completion_times: {completion_times}")
                                continue
                            
                            # 为每个worker插值数据并转换为百分比格式
                            result_data = {'percentage': target_percentages}
                            percentage_template_data = {}
                            
                            for worker, worker_data in template_data.items():
                                times = [point[0] for point in worker_data]
                                storage = [point[1] for point in worker_data]
                                
                                # 确保数据是有效的数值
                                times = [float(t) for t in times if not pd.isna(t)]
                                storage = [float(s) for s in storage if not pd.isna(s)]
                                
                                if len(times) == 0 or len(storage) == 0:
                                    # No valid data for this worker; skip silently
                                    continue
                                
                                try:
                                    interpolated_storage = interpolate_to_percentages(
                                        times, storage, times_for_percentages
                                    )
                                    interpolated_storage = np.maximum(interpolated_storage, 0.0)
                                    # 先四舍五入再掩蔽，确保“等于0”的判断稳定
                                    rounded_storage = np.round(interpolated_storage, 6)
                                    masked_storage = mask_consecutive_zeros_keep_edges(rounded_storage)
                                    
                                    result_data[worker] = masked_storage
                                    
                                    # 为绘图准备百分比数据（含NaN以便跳过）
                                    percentage_template_data[worker] = [(p, s) for p, s in zip(target_percentages, masked_storage)]
                                except Exception as e:
                                    # Skip worker on error silently
                                    continue
                            
                            result_df = pd.DataFrame(result_data)
                            
                            # 存储百分比数据到总数据字典
                            key = f"{repeat_name}_{template}"
                            all_data[key] = percentage_template_data
                        else:
                            # 如果没有百分比文件，使用原始时间数据
                            all_times = set()
                            for worker_data in template_data.values():
                                all_times.update([point[0] for point in worker_data])
                            
                            sorted_times = sorted(all_times)
                            result_data = {'time': sorted_times}
                            
                            for worker, worker_data in template_data.items():
                                worker_dict = dict(worker_data)
                                # 只包含worker实际有的时间点，避免填充0值
                                worker_values = []
                                for t in sorted_times:
                                    if t in worker_dict:
                                        worker_values.append(worker_dict[t])
                                    else:
                                        # 如果这个时间点worker没有数据，设为空值
                                        worker_values.append('')
                                result_data[worker] = worker_values
                            
                            result_df = pd.DataFrame(result_data)
                            
                            # 存储时间数据到总数据字典
                            key = f"{repeat_name}_{template}"
                            all_data[key] = template_data
                    else:
                        # 使用原始时间数据
                        all_times = set()
                        for worker_data in template_data.values():
                            all_times.update([point[0] for point in worker_data])
                        
                        sorted_times = sorted(all_times)
                        result_data = {'time': sorted_times}
                        
                        for worker, worker_data in template_data.items():
                            worker_dict = dict(worker_data)
                            # 只包含worker实际有的时间点，避免填充0值
                            worker_values = []
                            for t in sorted_times:
                                if t in worker_dict:
                                    worker_values.append(worker_dict[t])
                                else:
                                    # 如果这个时间点worker没有数据，设为空值
                                    worker_values.append('')
                            result_data[worker] = worker_values
                        
                        result_df = pd.DataFrame(result_data)
                        
                        # 存储时间数据到总数据字典
                        key = f"{repeat_name}_{template}"
                        all_data[key] = template_data
                    
                    # 保存CSV文件，使用repeat-template作为后缀
                    csv_filename = f'storage_consumption_per_worker_{repeat_name}_{template}.csv'
                    out_csv = CSV_DIR / csv_filename
                    
                    # 创建包含units的CSV文件
                    with open(out_csv, 'w', newline='') as f:
                        # 写入header行
                        f.write(','.join(result_df.columns) + '\n')
                        # 写入units行
                        if 'percentage' in result_df.columns:
                            units = ['%'] + ['GB'] * (len(result_df.columns) - 1)
                        else:
                            units = ['s'] + ['GB'] * (len(result_df.columns) - 1)
                        f.write(','.join(units) + '\n')
                        
                        # 写入数据行
                        for _, row in result_df.iterrows():
                            row_values = []
                            for value in row:
                                if pd.isna(value) or value is None:
                                    row_values.append('')
                                else:
                                    row_values.append(str(value))
                            f.write(','.join(row_values) + '\n')
                    
                    # CSV saved to: {out_csv}
                    
                except Exception as e:
                    print(f"Warning: Failed to process {repeat_name}/{template}: {e}")
                    continue
        
        if not all_data:
            print("Error: No valid data found")
            sys.exit(1)
        
        # 创建矩阵图
        create_matrix_plot(all_data, args.templates, repeat_dirs, args.x_axis)
        # Done!
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

