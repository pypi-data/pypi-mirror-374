from pathlib import Path
import pandas as pd
import numpy as np
import subprocess
import cloudpickle

from ndcctools.taskvine.graph_executor import GraphExecutor


# Centralized output dirs
PNG_DIR = Path('pngs')
CSV_DIR = Path('csvs')

PNG_DIR.mkdir(exist_ok=True, parents=True)
CSV_DIR.mkdir(exist_ok=True, parents=True)

# Fixed configuration
LOGS_DIR = "/users/jzhou24/afs/taskvine-report-tool/logs/"
EXPERIMENT = "fault_tolerance"
REPEAT_IDS = [4]
WORKFLOWS = ["DV5", "RSTriPhoton", "BinaryForest"]

FP_TEMPLATES = ["baseline",
				"disk-load-balance",
				"priority-mode-random", "priority-mode-largest-input-first"]
FT_TEMPLATES = ["baseline",
				"prune-depth-2", "prune-depth-3", "prune-depth-4",
				"replica-count-2", "replica-count-3", "replica-count-4", "replica-count-5",
				"checkpoint-percentage-0.1", "checkpoint-percentage-0.2", "checkpoint-percentage-0.3",
				"checkpoint-percentage-0.4", "checkpoint-percentage-0.5", "checkpoint-percentage-0.6",
				"checkpoint-percentage-0.7", "checkpoint-percentage-0.8", "checkpoint-percentage-0.9",
				"checkpoint-percentage-1.0"]


def get_all_templates(experiment="fault_tolerance"):
	all_templates_absolute_paths = []
	for rid in REPEAT_IDS:
		for wf in WORKFLOWS:
			if experiment == "fault_tolerance":
				for template in FT_TEMPLATES:
					all_templates_absolute_paths.append(Path(LOGS_DIR) / experiment / f"repeat{rid}" / wf / template)
			elif experiment == "fault_prevention":
				for template in FP_TEMPLATES:
					all_templates_absolute_paths.append(Path(LOGS_DIR) / experiment / f"repeat{rid}" / wf / template)
			else:
				raise ValueError(f"Unknown experiment: {experiment}")
	return all_templates_absolute_paths


def compute_template_graph_makespan(template_path):
	df = pd.read_csv(
		template_path / 'csv-files' / 'task_execution_details.csv',
		usecols=['time_worker_start', 'time_worker_end'],
		dtype={'time_worker_start': 'float64', 'time_worker_end': 'float64'},
		low_memory=False
	)
	start_min = df['time_worker_start'].min()
	end_max = df['time_worker_end'].max()
	return float(round(end_max - start_min, 2))


def compute_template_recovery_task_count(template_path):
	df = pd.read_csv(
		template_path / 'csv-files' / 'task_execution_details.csv',
		usecols=['task_id', 'is_recovery_task'],
		dtype={'task_id': 'float64', 'is_recovery_task': 'boolean'},
		low_memory=False
	)
	df = df.dropna(subset=['is_recovery_task'])
	if df.empty:
		return 0
	return float(df[df['is_recovery_task'] == True]['task_id'].nunique())


def compute_template_recovery_task_execution_time(template_path):
	df = pd.read_csv(
		template_path / 'csv-files' / 'task_execution_details.csv',
		usecols=['task_id', 'is_recovery_task', 'time_worker_start', 'time_worker_end'],
		dtype={'task_id': 'float64', 'is_recovery_task': 'boolean', 'time_worker_start': 'float64', 'time_worker_end': 'float64'},
		low_memory=False
	)
	df = df.dropna(subset=['is_recovery_task'])

	mask = (
		(df['is_recovery_task']) &
		(df['time_worker_end'] > 0.0) &
		(df['time_worker_start'] > 0.0)
	)

	sum_recovery_task_execution_time = (df.loc[mask, 'time_worker_end'] - df.loc[mask, 'time_worker_start']).sum()
	return float(round(sum_recovery_task_execution_time, 2))


def compute_template_pruning_overhead(template_path):
	debug_log_path = template_path / 'vine-logs' / 'debug'
	cmd = f'grep "pruned " "{debug_log_path}" | awk \'{{sum+=$(NF-1)}} END {{print sum}}\''
	result = subprocess.check_output(cmd, shell=True, text=True)
	return float(round(float(result.strip()), 2))


def compute_template_storage_consumption_peak(template_path):
	df = pd.read_csv(
		template_path / 'csv-files' / 'worker_storage_consumption.csv',
		index_col=0,   # except the first column (time)
	).iloc[1:]   	   # except the first row (column names)

	return float(np.nanmax(df.to_numpy()))


def compute_template_peer_transferred_size_mb(template_path):
	cols = pd.read_csv(template_path / 'csv-files' / 'file_transferred_size.csv', nrows=0).columns
	if "cumulative_size_mb" in cols:
		df = pd.read_csv(
			template_path / 'csv-files' / 'file_transferred_size.csv',
			usecols=['cumulative_size_mb'],
			dtype={'cumulative_size_mb': 'float64'},
			low_memory=False
		)
		return float(round(df['cumulative_size_mb'].max(), 2))
	elif "delta_size_mb" in cols:
		return 0
	else:
		raise ValueError(f"Unknown column in file_transferred_size.csv: {cols}")


def save_results(results, output_path="results.csv"):
    records = []
    for k, v in results.items():
        p = Path(k)
        workflow = None
        repeat_id = None

        for part in p.parts:
            if part.startswith("repeat"):
                repeat_id = part
            if part in ["DV5", "RSTriPhoton", "BinaryForest"]:
                workflow = part

        template_name = p.parts[-1].split("-compute_template_")[0]
        metric_name = p.parts[-1].split("-compute_template_")[1].replace("_", "-")

        records.append((metric_name, workflow, template_name, repeat_id, v))

    df = pd.DataFrame(records, columns=["metric","workflow","template","repeat_id","value"])
    df = df.groupby(["metric","workflow","template"])["value"].agg(["mean","std"]).reset_index()
    df[["mean","std"]] = df[["mean","std"]].round(2)
    df.to_csv(output_path, index=False)


if __name__ == "__main__":
	executor = GraphExecutor(
		[9200, 9210],
		name="test-manager",
		run_info_path="/users/jzhou24/afs/taskvine-report-tool/logs",
		run_info_template="compute-templates-stats",
		libcores=12,
	)

	func_list = [compute_template_graph_makespan,
				 compute_template_recovery_task_count,
				 compute_template_recovery_task_execution_time,
				 compute_template_pruning_overhead,
				 compute_template_storage_consumption_peak,
				 compute_template_peer_transferred_size_mb]
	
	collection_dict = {}
	for t in get_all_templates():
		for func in func_list:
			k = f"{t}-{func.__name__}"
			collection_dict[k] = (func, t)

	results = executor.run(
		collection_dict,
		target_keys=list(collection_dict.keys()),
	)

	with open('results.pkl', 'wb') as f:
		cloudpickle.dump(results, f)

	save_results(results)