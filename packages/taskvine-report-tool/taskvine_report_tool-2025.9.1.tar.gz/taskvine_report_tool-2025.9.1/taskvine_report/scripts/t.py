from generate_ft_data import save_results
import cloudpickle

with open('results.pkl', 'rb') as f:
    results = cloudpickle.load(f)

save_results(results)