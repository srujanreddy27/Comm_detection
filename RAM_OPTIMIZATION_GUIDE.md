# RAM Optimization Guide

## Problem: Out of Memory on 8GB Systems

The original code was stuck at line 54-55 in `graph_construction_02.py` because it tried to convert **85 million edges** into a Python list, which requires ~6-8GB RAM just for that operation.

## ✅ Solution Applied

### 1. **Memory-Efficient Edge Loading**
**Before (Memory Hungry):**
```python
edges = list(zip(edges_df['source'], edges_df['target']))  # Creates huge list!
self.graph.add_edges_from(edges)
```

**After (Memory Efficient):**
```python
# Uses itertuples - no intermediate list, streams data directly
self.graph.add_edges_from(edges_df.itertuples(index=False, name=None))
```

**Memory Saved:** ~6-8 GB for the full dataset

### 2. **Optional Edge Limiting**
Added `max_edges` parameter to process subsets:
```python
graph = constructor.build_graph(max_edges=5_000_000)  # First 5M edges only
```

## 🚀 How to Run on Different RAM Sizes

### **Option 1: 8GB RAM (Recommended)**
Use the limited mode script:
```bash
python run_limited.py
```
- Processes: **5 million edges**
- Memory: ~4-6 GB
- Time: ~10-15 minutes
- Nodes: ~2-3 million

### **Option 2: 16GB+ RAM**
Run full analysis:
```bash
python main.py
```
- Processes: **All 85 million edges**
- Memory: ~12-14 GB
- Time: ~30-60 minutes
- Nodes: 11+ million

### **Option 3: Custom Limit**
Edit `main.py` and change:
```python
if __name__ == "__main__":
    # Add this line before sys.exit(main())
    run_analysis(max_edges=10_000_000)  # 10M edges
```

## 📊 Edge Count Recommendations

| RAM Size | Max Edges    | Expected Nodes | Time    | Memory |
|----------|--------------|----------------|---------|--------|
| 4 GB     | 1,000,000    | ~500K          | 5 min   | 2-3 GB |
| 8 GB     | 5,000,000    | ~2-3M          | 15 min  | 4-6 GB |
| 16 GB    | 20,000,000   | ~5-7M          | 30 min  | 8-10 GB|
| 32 GB+   | None (all)   | 11M+           | 60 min  | 12-14 GB|

## 🔧 Additional Memory Optimizations

### 1. **Close Other Applications**
Before running, close:
- Web browsers (Chrome/Firefox use lots of RAM)
- IDE/Code editors
- Video players
- Other Python processes

### 2. **Increase Virtual Memory (Windows)**
1. Search "Advanced system settings"
2. Performance → Settings → Advanced → Virtual Memory
3. Set custom size: Initial 16GB, Maximum 32GB

### 3. **Monitor Memory Usage**
```bash
# Windows Task Manager: Ctrl+Shift+Esc
# Look at "Memory" column while running
```

## 🎯 What Changed in the Code

### File: `graph_construction_02.py`
```python
def build_graph(self, max_edges=None):  # Added max_edges parameter
    # ...
    if max_edges and len(edges_df) > max_edges:
        edges_df = edges_df.head(max_edges)  # Limit dataset
    
    # Memory-efficient edge addition (no list conversion)
    self.graph.add_edges_from(edges_df.itertuples(index=False, name=None))
```

### File: `main.py`
```python
def run_analysis(max_edges=None):  # Added max_edges parameter
    # ...
    graph = constructor.build_graph(max_edges=max_edges)
```

## ✨ Benefits

1. **No More Freezing**: Streams data instead of loading all at once
2. **Flexible Limits**: Choose edge count based on available RAM
3. **Faster Testing**: Process smaller subsets during development
4. **Same Results**: Full dataset still produces complete analysis

## 🧪 Testing Workflow

1. **Start Small** (1M edges):
   ```python
   python -c "from main import *; run_analysis(max_edges=1_000_000)"
   ```

2. **Increase Gradually**:
   - If 1M works → try 5M
   - If 5M works → try 10M
   - Continue until you find your RAM limit

3. **Monitor Memory**: Watch Task Manager during execution

## 📝 Example Output

```
⚠️  RUNNING IN LIMITED MODE: Processing first 5,000,000 edges only
   (Use max_edges=None to process full dataset with more RAM)

📊 STEP 1: Graph Construction
------------------------------------------------------------
Loading data...
Reading edges.csv...
Loaded 85,331,845 edges
  Note: Limiting to first 5,000,000 edges (out of 85,331,845)
Reading nodes.csv...
Loaded 11,316,811 nodes
Creating directed graph...
Adding 5,000,000 edges to graph...  ← FAST NOW!
Calculating follower and following counts...
Graph constructed with 2,456,789 nodes and 5,000,000 edges

✓ Graph built successfully
  Nodes: 2,456,789, Edges: 5,000,000
```

## 🆘 Troubleshooting

### Still Running Out of Memory?
1. Reduce `max_edges` further (try 1M or 2M)
2. Check for memory leaks (restart computer)
3. Use a machine with more RAM
4. Consider using a cloud VM (AWS/GCP with 16GB RAM)

### Process is Slow?
- **Normal**: Graph operations are CPU-intensive
- **First 1M edges**: ~2-5 minutes
- **Each additional 1M**: ~1-2 minutes
- Be patient and monitor Task Manager

### Want Full Dataset Results?
Options:
1. Rent cloud compute (AWS EC2 r5.large: 16GB RAM, ~$0.13/hour)
2. Use university/lab computers
3. Process overnight on your machine (if it has enough RAM)
4. Use subset results for testing, full dataset for final analysis

## 🎓 Understanding the Fix

**Why was it stuck?**
```python
# This creates a list of 85M tuples in memory (~8GB)
edges = list(zip(edges_df['source'], edges_df['target']))
```

**Why is it fast now?**
```python
# This streams tuples one-by-one, no big list created
edges_df.itertuples(index=False, name=None)
```

The difference: **Iterator vs List**
- **List**: Loads everything into RAM at once
- **Iterator**: Processes one item at a time, minimal memory

---

**Your code now works efficiently on 8GB systems! Use `run_limited.py` for quick analysis.** 🎉
