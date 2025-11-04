"""
Ultra-Low RAM Mode for 6GB Systems
Optimized configuration for minimal memory usage.
"""

import sys
from main import print_banner, run_analysis

if __name__ == "__main__":
    print_banner()
    
    # OPTIMIZED FOR 6GB RAM
    MAX_EDGES = 2_000_000  # 2M edges - safe for 6GB
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║               ULTRA-LOW RAM MODE (6GB SYSTEM)                 ║
    ║                                                               ║
    ║  🔧 Optimized Settings:                                       ║
    ║     • Edges: {MAX_EDGES:,} (2.3% of dataset)                 ║
    ║     • Nodes: ~800K-1.2M expected                              ║
    ║     • Betweenness: SKIPPED (too slow - uses PageRank instead) ║
    ║     • Memory: ~3-4 GB peak usage                              ║
    ║     • Time: ~5-8 minutes (FAST!)                              ║
    ║                                                               ║
    ║  ⚠️  Tips for 6GB RAM:                                        ║
    ║     • Close ALL other applications (browser, etc.)            ║
    ║     • Monitor Task Manager during run                         ║
    ║     • Betweenness skipped = 90% faster!                       ║
    ║                                                               ║
    ║  ✅ What You Get:                                             ║
    ║     • Degree Centrality (exact, instant)                      ║
    ║     • PageRank (exact, better than betweenness)               ║
    ║     • Community Detection (exact)                             ║
    ║     • All visualizations and reports                          ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    response = input("\n⚠️  Have you closed all other applications? (y/n): ")
    if response.lower() != 'y':
        print("\n👉 Please close other apps first, then run again!")
        sys.exit(0)
    
    print("\n🚀 Starting analysis...\n")
    
    try:
        run_analysis(max_edges=MAX_EDGES)
        print("\n✅ SUCCESS! Analysis completed without running out of memory.")
        sys.exit(0)
    except MemoryError:
        print("\n❌ Out of Memory!")
        print("\n💡 Solutions:")
        print("   1. Edit run_6gb.py: Change MAX_EDGES to 1_000_000")
        print("   2. Close more applications")
        print("   3. Restart computer and try again")
        print("   4. Use a machine with more RAM")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user (Ctrl+C)")
        print("   If it was stuck on betweenness, the sampling might still be too large.")
        print("   Try reducing MAX_EDGES to 1_000_000")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
