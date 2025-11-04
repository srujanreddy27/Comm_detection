"""
Quick Test Script for Limited RAM Systems (8GB)
Processes a subset of edges for faster testing and lower memory usage.
"""

import sys
from main import print_banner, run_analysis

# Recommended configurations for different RAM sizes:
# 4GB RAM:  max_edges = 500_000     (500K edges)
# 6GB RAM:  max_edges = 2_000_000   (2M edges)  ← YOUR SYSTEM
# 8GB RAM:  max_edges = 5_000_000   (5M edges)
# 16GB RAM: max_edges = 20_000_000  (20M edges)
# 32GB RAM: max_edges = None        (all 85M edges)

if __name__ == "__main__":
    print_banner()
    
    # FOR 6GB RAM SYSTEMS - Use 2 million edges
    MAX_EDGES = 2_000_000
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                   LIMITED RAM MODE (6GB)                      ║
    ║                                                               ║
    ║  Processing: {MAX_EDGES:,} edges (instead of 85M)            ║
    ║  Expected time: ~5-8 minutes                                  ║
    ║  Memory usage: ~3-4 GB                                        ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    input("Press Enter to start analysis...")
    
    try:
        run_analysis(max_edges=MAX_EDGES)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
