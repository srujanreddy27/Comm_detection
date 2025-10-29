# Large-Scale Twitter Dataset Updates

## Dataset Information

### New Dataset Structure
- **nodes.csv**: 11,316,811 nodes (single column of node IDs, no headers)
- **edges.csv**: 85,331,846 edges (2 columns: follower, following, no headers)
- **Format**: `1,2` means "User 1 follows User 2"
- **No user metadata**: All user attributes must be derived from graph structure

## Key Changes Made

### 1. Graph Construction (`graph_construction_02.py`)
- **CSV Loading**: Updated to read files without headers
  - `edges.csv`: Read as two columns named 'source' and 'target'
  - `nodes.csv`: Read as single column named 'id'
- **Attribute Derivation**: Calculate follower/following counts from graph structure
  - `followers_count` = in-degree (number of incoming edges)
  - `following_count` = out-degree (number of outgoing edges)
- **Removed**: User metadata dictionary lookup (not available in new dataset)

### 2. Main Pipeline (`main.py`)
- **File path**: Updated from `users.csv` to `nodes.csv`
- **Formatting**: Added thousand separators for large numbers (11M+ nodes)
- **Approximation**: Always use approximation for this large-scale dataset
- **Demo selection**: Use top PageRank nodes instead of max degree for recommendations

### 3. Metric Calculation (`metric_calculation_03.py`)
- **Adaptive Sampling**: Scale-based approximation strategy
  - >1M nodes: Sample ~0.1% (1000 nodes) for betweenness
  - >500 nodes: Sample ~1% (5000 nodes) for betweenness
- **Skip expensive metrics** for very large graphs:
  - Closeness centrality: Skipped if >100k nodes
  - Eigenvector centrality: Skipped if >500k nodes
- **Always calculate**: Degree centrality, PageRank, clustering coefficient

### 4. Community Detection (`community_detection_04.py`)
- **Algorithm selection**: For graphs >1M nodes, only use Louvain (most efficient)
- **Label Propagation**: Skipped for very large graphs to save time
- **igraph Louvain**: Attempted but optional

### 5. Visualization (`visualization_07.py`)
- **Network plot**: 
  - Default max_nodes set to 1000 (always sample for large graphs)
  - Skip network visualization entirely if >100k nodes
- **Sampling strategy**: Show highest-degree nodes for representative view
- **Conditional plots**: Only plot betweenness if it was calculated

### 6. Threat Analysis (`threat_analysis_06.py`)
- **Follower/Following ratios**: Now derived from graph structure
  - `followers_count` = in-degree
  - `following_count` = out-degree
- **No changes needed**: Algorithm logic remains the same

## Performance Optimizations

### Memory Efficiency
1. **Sampling**: Use node sampling for expensive computations
2. **Approximation**: Use k-sampling for centrality metrics
3. **Selective calculation**: Skip metrics that don't scale well

### Computation Time
- **Louvain only**: Primary community detection for large graphs
- **Limited betweenness**: Sample 0.1% of nodes instead of full calculation
- **No closeness**: Skip for graphs >100k nodes (too expensive)

## Expected Runtime

For 11M+ nodes and 85M+ edges:
- **Graph construction**: 2-5 minutes
- **Degree centrality**: < 1 minute
- **PageRank**: 5-10 minutes
- **Betweenness (sampled)**: 5-15 minutes
- **Community detection**: 10-20 minutes
- **Visualizations**: 2-5 minutes
- **Total**: ~30-60 minutes

## Usage

No changes to usage commands:
```bash
# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run analysis
python main.py
```

## Output

All outputs remain the same:
- `output/network_graph.graphml`
- `output/network_metrics.csv`
- `output/network_analysis_report.txt`
- `output/visualizations/` (multiple PNG files)

## Notes

1. **Type warnings**: You may see type-checking warnings in the IDE - these are safe to ignore
2. **Memory**: Ensure at least 16GB RAM for this dataset
3. **Time**: First run will take 30-60 minutes due to graph size
4. **Metrics**: Some metrics are approximations for scalability
5. **Sampling**: Visualizations show representative samples, not all nodes
