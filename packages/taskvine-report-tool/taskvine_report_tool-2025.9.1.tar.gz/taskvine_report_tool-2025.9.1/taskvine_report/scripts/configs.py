import cloudpickle
from generate_ft_data import save_results

with open('results.pkl', 'rb') as f:
	results = cloudpickle.load(f)

save_results(results)