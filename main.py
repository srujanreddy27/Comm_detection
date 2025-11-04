"""
Main Orchestration Script
Runs the complete social network analysis pipeline.
"""

import sys
from pathlib import Path

# Import all modules
from importlib import import_module


def print_banner():
    """Print welcome banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║        SOCIAL NETWORK SECURITY ANALYSIS SYSTEM                ║
    ║                                                               ║
    ║     Comprehensive Network Analysis & Threat Detection         ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def run_analysis(max_edges=None):
    """Run the complete analysis pipeline.
    
    Args:
        max_edges: Maximum number of edges to load (None = all)
                  For 8GB RAM, try max_edges=5_000_000 (5M edges)
                  For 16GB RAM, can use full dataset
    """
    
    # Configuration
    edges_path = "data/edges.csv"
    users_path = "data/nodes.csv"  # Updated to nodes.csv
    output_dir = "output"
    
    if max_edges:
        print(f"\n⚠️  RUNNING IN LIMITED MODE: Processing first {max_edges:,} edges only")
        print("   (Use max_edges=None to process full dataset with more RAM)\n")
    
    print("\n🚀 Starting Social Network Analysis Pipeline...\n")
    
    # ===== STEP 1: Graph Construction =====
    print("📊 STEP 1: Graph Construction")
    print("-" * 60)
    
    graph_constructor_module = import_module('graph_construction_02')
    constructor = graph_constructor_module.GraphConstructor(edges_path, users_path)
    graph = constructor.build_graph(max_edges=max_edges)
    
    stats = constructor.get_graph_statistics()
    print("\n✓ Graph built successfully")
    print(f"  Nodes: {stats['nodes']:,}, Edges: {stats['edges']:,}")
    
    # ===== STEP 2: Metric Calculation =====
    print("\n\n📈 STEP 2: Network Metrics Calculation")
    print("-" * 60)
    
    metric_calculator_module = import_module('metric_calculation_03')
    calculator = metric_calculator_module.MetricCalculator(graph)
    
    # Use approximation for large graphs (this is a VERY large graph)
    use_approximation = True  # Always use approximation for 11M+ nodes
    print(f"\n  Note: Using approximation methods for large-scale graph ({graph.number_of_nodes():,} nodes)")
    calculator.calculate_all_metrics(use_approximation=use_approximation)
    calculator.add_metrics_to_graph()
    calculator.export_metrics(f"{output_dir}/network_metrics.csv")
    
    # Show top influencers
    print("\n  Top 5 Influencers (by PageRank):")
    top_influencers = calculator.get_top_nodes('pagerank', n=5)
    for rank, (node, value) in enumerate(top_influencers, 1):
        print(f"    {rank}. User {node}: {value:.6f}")
    
    # ===== STEP 3: Community Detection =====
    print("\n\n🔍 STEP 3: Community Detection")
    print("-" * 60)
    
    community_detector_module = import_module('community_detection_04')
    detector = community_detector_module.CommunityDetector(graph)
    detector.detect_all_communities()
    detector.add_communities_to_graph(algorithm='louvain')
    
    stats = detector.get_community_statistics('louvain')
    modularity = detector.calculate_modularity('louvain')
    print(f"\n  Communities detected: {stats['num_communities']}")
    print(f"  Modularity: {modularity:.4f}")
    print(f"  Largest community: {stats['largest_community_size']} members")
    
    # ===== STEP 4: Recommendation Engine =====
    print("\n\n💡 STEP 4: Recommendation Engine")
    print("-" * 60)
    
    recommendation_engine_module = import_module('recommendation_engine_05')
    engine = recommendation_engine_module.RecommendationEngine(graph)
    
    # Demo for a high-degree user (sample from top nodes)
    if graph.number_of_nodes() > 0:
        # Find a user with good connectivity from top PageRank nodes
        top_users = calculator.get_top_nodes('pagerank', n=10)
        if top_users:
            demo_user = top_users[0][0]  # Use top PageRank user
            
            print(f"\n  Sample recommendations for User {demo_user}:")
            try:
                recommendations = engine.recommend_hybrid(demo_user, n=3)
                for rank, (user, score, reason) in enumerate(recommendations, 1):
                    print(f"    {rank}. User {user}: {reason}")
            except Exception as e:
                print(f"    (Demo skipped: {e})")
    
    # ===== STEP 5: Threat Analysis =====
    print("\n\n⚠️  STEP 5: Threat Analysis")
    print("-" * 60)
    
    threat_analyzer_module = import_module('threat_analysis_06')
    analyzer = threat_analyzer_module.ThreatAnalyzer(graph)
    analyzer.analyze_all_threats()
    
    summary = analyzer.get_threat_summary()
    print(f"\n  Total threats detected: {summary['total_threats']:,}")
    print(f"    • Echo chambers: {summary['echo_chambers_count']:,}")
    print(f"    • Influencer concentration: {summary['influencer_concentration_count']:,}")
    print(f"    • Spam clusters: {summary['spam_clusters_count']:,}")
    print(f"    • Isolated communities: {summary['isolated_communities_count']:,}")
    
    # ===== STEP 6: Visualization =====
    print("\n\n🎨 STEP 6: Creating Visualizations")
    print("-" * 60)
    
    visualization_module = import_module('visualization_07')
    visualizer = visualization_module.NetworkVisualizer(graph, output_dir=f"{output_dir}/visualizations")
    visualizer.visualize_all()
    
    # ===== STEP 7: Report Generation =====
    print("\n\n📄 STEP 7: Generating Comprehensive Report")
    print("-" * 60)
    
    report_generator_module = import_module('generate_report_08')
    report_generator = report_generator_module.ReportGenerator(
        graph, calculator, detector, analyzer,
        output_path=f"{output_dir}/network_analysis_report.txt"
    )
    report_path = report_generator.generate_report()
    
    # ===== STEP 8: Save Graph =====
    print("\n\n💾 STEP 8: Saving Processed Graph")
    print("-" * 60)
    constructor.save_graph(f"{output_dir}/network_graph.graphml")
    
    # ===== COMPLETION =====
    print("\n\n" + "=" * 60)
    print("✅ ANALYSIS COMPLETE!")
    print("=" * 60)
    print(f"\n📁 Output Location: {Path(output_dir).absolute()}")
    print(f"\n📊 Generated Files:")
    print(f"  • Network graph: {output_dir}/network_graph.graphml")
    print(f"  • Metrics: {output_dir}/network_metrics.csv")
    print(f"  • Report: {output_dir}/network_analysis_report.txt")
    print(f"  • Visualizations: {output_dir}/visualizations/")
    print("\n💡 Next Steps:")
    print("  1. Review the analysis report")
    print("  2. Examine visualizations for insights")
    print("  3. Investigate flagged threats")
    print("  4. Use metrics for further research\n")


def main():
    """Main entry point."""
    try:
        print_banner()
        run_analysis()
        return 0
    except FileNotFoundError as e:
        print(f"\n❌ Error: Required file not found - {e}")
        print("   Please ensure data/edges.csv and data/nodes.csv exist.")
        return 1
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
