# Quick Start Guide

## Dataset Information

**Large-scale Twitter Dataset:**
- **nodes.csv**: 11,316,811 nodes (no header, single column of node IDs)
- **edges.csv**: 85,331,846 edges (no header, format: `follower,following`)
- **Relationship**: Line `1,2` means "User 1 follows User 2"
- **No metadata**: All user attributes calculated from graph structure
- **Expected runtime**: 30-60 minutes for full analysis

## Installation

1. **Run the setup script:**
   ```bash
   setup.bat
   ```
   This will:
   - Create a virtual environment
   - Install all required dependencies

2. **Or manually install:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Running the Analysis

1. **Activate the virtual environment:**
   ```bash
   venv\Scripts\activate
   ```

2. **Run the complete pipeline:**
   ```bash
   python main.py
   ```

3. **Check the outputs:**
   - Report: `output/network_analysis_report.txt`
   - Visualizations: `output/visualizations/`
   - Metrics: `output/network_metrics.csv`
   - Graph: `output/network_graph.graphml`

## Running Individual Modules

You can run each module independently for testing:

```bash
# Graph construction
python graph_construction_02.py

# Metrics calculation
python metric_calculation_03.py

# Community detection
python community_detection_04.py

# Recommendation engine
python recommendation_engine_05.py

# Threat analysis
python threat_analysis_06.py

# Visualization
python visualization_07.py

# Report generation
python generate_report_08.py
```

## Project Structure

```
Qoder/
├── data/
│   ├── edges.csv          # 85M+ edges (follower,following)
│   └── nodes.csv          # 11M+ node IDs
├── output/
│   ├── visualizations/    # Generated charts
│   ├── network_analysis_report.txt
│   ├── network_metrics.csv
│   └── network_graph.graphml
├── graph_construction_02.py
├── metric_calculation_03.py
├── community_detection_04.py
├── recommendation_engine_05.py
├── threat_analysis_06.py
├── visualization_07.py
├── generate_report_08.py
├── main.py                # Run this!
├── requirements.txt
└── README.md
```

## What Gets Analyzed

1. **Network Metrics:**
   - Degree centrality (in/out)
   - Betweenness centrality
   - Closeness centrality
   - Eigenvector centrality
   - PageRank
   - Clustering coefficients

2. **Communities:**
   - Louvain algorithm
   - Label propagation
   - Modularity scores

3. **Threats:**
   - Echo chambers
   - Influencer concentration
   - Spam clusters
   - Isolated communities

4. **Recommendations:**
   - Based on common neighbors
   - Based on community membership
   - Hybrid recommendations
   - Influencer suggestions

## Troubleshooting

### Installation Issues

**python-igraph fails to install:**
```bash
pip install --upgrade pip
pip install python-igraph
```

If that doesn't work, try:
```bash
pip install igraph
```

### Memory Issues

**For large graphs (11M+ nodes):**
- Ensure at least 16GB RAM available
- Close other applications during processing
- The code automatically uses approximation methods:
  - Betweenness: Samples ~1000 nodes instead of all
  - Closeness: Skipped for graphs >100K nodes
  - Eigenvector: Skipped for graphs >500K nodes
- Network visualization limited to top 1000 nodes
- **First run takes 30-60 minutes** - this is normal!

### Visualization Issues

If matplotlib shows errors, ensure you have proper GUI backend:
```bash
pip install --upgrade matplotlib
```

## Tips

- Start with the complete pipeline (`python main.py`)
- Review the generated report first
- Then explore visualizations
- Use individual modules for deeper analysis
- Metrics CSV can be imported into Excel/Pandas for custom analysis
