import pandas as pd, networkx as nx
from collections import Counter, defaultdict

def parse_files(x):
    if pd.isnull(x): return []
    r=[]; s=str(x).strip()
    if not s: return r
    for t in s.split('|'):
        t=t.strip()
        if not t: continue
        r.append(t.rsplit(':',1)[0].strip())
    return r

def analyze_dag(df, pick=None):
    df=df[['task_id','input_files','output_files']].copy()
    df['in_list']=df['input_files'].apply(parse_files)
    df['out_list']=df['output_files'].apply(parse_files)

    sig_to_canon={}
    for r in df.itertuples(index=False):
        sig=(tuple(sorted(set(r.in_list))), tuple(sorted(set(r.out_list))))
        if sig not in sig_to_canon or r.task_id<sig_to_canon[sig]:
            sig_to_canon[sig]=int(r.task_id)

    tid_to_canon={}
    for r in df.itertuples(index=False):
        sig=(tuple(sorted(set(r.in_list))), tuple(sorted(set(r.out_list))))
        tid_to_canon[int(r.task_id)]=sig_to_canon[sig]

    files_prod=defaultdict(set); files_cons=defaultdict(set)
    canon_tasks=set(tid_to_canon.values())

    for r in df.itertuples(index=False):
        ctid=tid_to_canon[int(r.task_id)]
        for f in r.out_list: files_prod[f].add(ctid)
        for f in r.in_list:  files_cons[f].add(ctid)

    for f in files_cons:
        if f not in files_prod or not files_prod[f]:
            raise ValueError(f'missing producer for {f}')

    G=nx.DiGraph(); G.add_nodes_from(canon_tasks)
    for f, cs in files_cons.items():
        for p in files_prod[f]:
            for c in cs:
                if p!=c: G.add_edge(p,c)

    if not nx.is_directed_acyclic_graph(G):
        raise ValueError('graph contains a cycle')

    nodes=G.number_of_nodes()
    edges=G.number_of_edges()
    depth=0 if edges==0 else nx.dag_longest_path_length(G)

    levels={}
    for n in nx.topological_sort(G):
        levels[n]=0 if G.in_degree(n)==0 else max(levels[p]+1 for p in G.predecessors(n))
    width=max(Counter(levels.values()).values()) if levels else 0

    indeg=[d for _,d in G.in_degree()]
    outdeg=[d for _,d in G.out_degree()]
    max_in=max(indeg) if indeg else 0
    max_out=max(outdeg) if outdeg else 0
    sources=sum(1 for d in indeg if d==0)
    sinks=sum(1 for d in outdeg if d==0)
    components=nx.number_weakly_connected_components(G)

    return {
        "Nodes": nodes,
        "Edges": edges,
        "Depth": depth,
        "Width": width,
        "Max Indegree": max_in,
        "Max Outdegree": max_out,
        "Sources": sources,
        "Sinks": sinks,
        "Components": components
    }

def run_many(paths, pick=None):
    rows=[]
    for name, p in paths.items():
        df=pd.read_csv(p, usecols=['task_id','input_files','output_files'],
                       dtype={'task_id':'int64','input_files':'str','output_files':'str'},
                       low_memory=False)
        m=analyze_dag(df, pick=pick)
        m['Workflow']=name
        rows.append(m)
    cols=["Workflow","Nodes","Edges","Depth","Width","Max Indegree","Max Outdegree","Sources","Sinks","Components"]
    return pd.DataFrame(rows)[cols].set_index("Workflow")


if __name__ == "__main__":
    PATHS={
        "DV5": "/users/jzhou24/afs/taskvine-report-tool/logs/fault_tolerance/repeat1/DV5/baseline/csv-files/task_subgraphs.csv",
        "RSTriPhoton": "/users/jzhou24/afs/taskvine-report-tool/logs/fault_tolerance/repeat1/RSTriPhoton/baseline/csv-files/task_subgraphs.csv",
        "BinaryForest": "/users/jzhou24/afs/taskvine-report-tool/logs/fault_tolerance/repeat1/BinaryForest/baseline/csv-files/task_subgraphs.csv",
    }
    print(run_many(PATHS, pick='min'))
