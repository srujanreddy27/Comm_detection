# Social Network Security Analysis

A comprehensive social network analysis tool for detecting threats, recommending connections, and analyzing community structures using X (Twitter) network data.

## Features

- **Graph Construction**: Build directed social graphs from edge and user data
- **Centrality Analysis**: Calculate degree, betweenness, closeness, and eigenvector centrality
- **Community Detection**: Identify clusters using Louvain and Label Propagation algorithms
- **Recommendation Engine**: Suggest connections based on graph structure and common neighbors
- **Threat Detection**: Identify echo chambers, influencer concentration, and spam clusters
- **Visualization**: Generate insightful network visualizations
- **Automated Reporting**: Comprehensive analysis reports

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

Note: Make sure scipy is installed. If not, run:
```bash
pip install scipy
```

## Usage

Run the complete analysis pipeline:
```bash
python main.py
```

This will:
1. Load your data from `data/edges.csv` and `data/users.csv`
2. Construct the social graph
3. Calculate all network metrics
4. Detect communities
5. Generate threat analysis
6. Create visualizations (saved to `output/visualizations/`)
7. Generate a comprehensive report (`output/network_analysis_report.txt`)

## Data Format

- **edges.csv**: `source,target,relationship`
- **users.csv**: `id,username,name,verified,created_at,followers_count,following_count,tweet_count,listed_count`

## Output

- Visualizations: `output/visualizations/`
- Analysis Report: `output/network_analysis_report.txt`
- Processed Graph: `output/network_graph.graphml`
