"""
Module 8: Report Generation
Generates a comprehensive analysis report summarizing all findings.
"""

import networkx as nx
from pathlib import Path
from datetime import datetime


class ReportGenerator:
    """Generates comprehensive network analysis reports."""
    
    def __init__(self, graph: nx.Graph, metric_calculator, community_detector, 
                 threat_analyzer, output_path='output/network_analysis_report.txt'):
        """
        Initialize ReportGenerator.
        
        Args:
            graph: NetworkX graph with all computations
            metric_calculator: MetricCalculator instance
            community_detector: CommunityDetector instance
            threat_analyzer: ThreatAnalyzer instance
            output_path: Path to save the report
        """
        self.graph = graph
        self.metric_calculator = metric_calculator
        self.community_detector = community_detector
        self.threat_analyzer = threat_analyzer
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.report_lines = []
    
    def add_header(self):
        """Add report header."""
        self.report_lines.append("=" * 80)
        self.report_lines.append("SOCIAL NETWORK SECURITY ANALYSIS REPORT")
        self.report_lines.append("=" * 80)
        self.report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.report_lines.append("=" * 80)
        self.report_lines.append("")
    
    def add_network_overview(self):
        """Add network statistics overview."""
        self.report_lines.append("1. NETWORK OVERVIEW")
        self.report_lines.append("-" * 80)
        
        stats = {
            'Total Users': self.graph.number_of_nodes(),
            'Total Connections': self.graph.number_of_edges(),
            'Network Density': f"{nx.density(self.graph):.6f}",
            'Is Directed': "Yes" if self.graph.is_directed() else "No"
        }
        
        if self.graph.is_directed():
            stats['Weakly Connected Components'] = nx.number_weakly_connected_components(self.graph)
            stats['Strongly Connected Components'] = nx.number_strongly_connected_components(self.graph)
        
        for key, value in stats.items():
            self.report_lines.append(f"  {key}: {value}")
        
        self.report_lines.append("")
    
    def add_top_influencers(self, n=10):
        """Add top influencers section."""
        self.report_lines.append("2. TOP INFLUENCERS")
        self.report_lines.append("-" * 80)
        
        metrics_to_report = [
            ('pagerank', 'PageRank'),
            ('betweenness_centrality', 'Betweenness Centrality'),
            ('in_degree', 'In-Degree (Followers)')
        ]
        
        for metric_key, metric_name in metrics_to_report:
            if metric_key in self.metric_calculator.metrics:
                self.report_lines.append(f"\n  Top {n} by {metric_name}:")
                top_nodes = self.metric_calculator.get_top_nodes(metric_key, n=n)
                
                for rank, (node, value) in enumerate(top_nodes, 1):
                    # Get user info
                    node_data = self.graph.nodes[node]
                    username = node_data.get('username', f'user_{node}')
                    verified = " [VERIFIED]" if node_data.get('verified') else ""
                    
                    self.report_lines.append(f"    {rank:2d}. {username}{verified}: {value:.6f}")
        
        self.report_lines.append("")
    
    def add_community_analysis(self):
        """Add community analysis section."""
        self.report_lines.append("3. COMMUNITY ANALYSIS")
        self.report_lines.append("-" * 80)
        
        # Louvain stats
        stats = self.community_detector.get_community_statistics('louvain')
        modularity = self.community_detector.calculate_modularity('louvain')
        
        self.report_lines.append(f"\n  Algorithm: Louvain")
        self.report_lines.append(f"  Number of Communities: {stats['num_communities']}")
        self.report_lines.append(f"  Modularity Score: {modularity:.4f}")
        self.report_lines.append(f"  Largest Community: {stats['largest_community_size']} members")
        self.report_lines.append(f"  Smallest Community: {stats['smallest_community_size']} members")
        self.report_lines.append(f"  Average Community Size: {stats['average_community_size']:.2f} members")
        
        # Top 10 largest communities
        self.report_lines.append(f"\n  Top 10 Largest Communities:")
        sorted_communities = sorted(stats['community_sizes'].items(), 
                                   key=lambda x: x[1], reverse=True)[:10]
        
        for rank, (comm_id, size) in enumerate(sorted_communities, 1):
            percentage = (size / self.graph.number_of_nodes()) * 100
            self.report_lines.append(f"    {rank:2d}. Community {comm_id}: {size} members ({percentage:.1f}%)")
        
        self.report_lines.append("")
    
    def add_threat_analysis(self):
        """Add threat analysis section."""
        self.report_lines.append("4. THREAT ANALYSIS")
        self.report_lines.append("-" * 80)
        
        summary = self.threat_analyzer.get_threat_summary()
        
        self.report_lines.append(f"\n  Total Threats Detected: {summary['total_threats']}")
        self.report_lines.append(f"  - Echo Chambers: {summary['echo_chambers_count']}")
        self.report_lines.append(f"  - Influencer Concentration: {summary['influencer_concentration_count']}")
        self.report_lines.append(f"  - Spam Clusters: {summary['spam_clusters_count']}")
        self.report_lines.append(f"  - Isolated Communities: {summary['isolated_communities_count']}")
        
        # Echo Chambers details
        if summary['echo_chambers_count'] > 0:
            self.report_lines.append(f"\n  Echo Chambers Details:")
            for threat in self.threat_analyzer.threats['echo_chambers'][:5]:
                self.report_lines.append(
                    f"    - Community {threat['community_id']}: "
                    f"{threat['size']} members, "
                    f"Risk: {threat['risk_level']}, "
                    f"Clustering: {threat['avg_clustering']:.2f}, "
                    f"External Ratio: {threat['external_ratio']:.2%}"
                )
        
        # Influencer Concentration details
        if summary['influencer_concentration_count'] > 0:
            self.report_lines.append(f"\n  Influencer Concentration Details:")
            for threat in self.threat_analyzer.threats['influencer_concentration'][:5]:
                self.report_lines.append(
                    f"    - Community {threat['community_id']}: "
                    f"{threat['size']} members, "
                    f"Risk: {threat['risk_level']}, "
                    f"Dominant User: {threat['dominant_user']}, "
                    f"Concentration: {threat['concentration_ratio']:.2%}"
                )
        
        # Spam Clusters details
        if summary['spam_clusters_count'] > 0:
            self.report_lines.append(f"\n  Spam Clusters Details:")
            for threat in self.threat_analyzer.threats['spam_clusters'][:5]:
                self.report_lines.append(
                    f"    - Community {threat['community_id']}: "
                    f"{threat['size']} members, "
                    f"Risk: {threat['risk_level']}, "
                    f"Suspicious: {threat['suspicious_percentage']:.1%}"
                )
        
        # Isolated Communities details
        if summary['isolated_communities_count'] > 0:
            self.report_lines.append(f"\n  Isolated Communities Details:")
            for threat in self.threat_analyzer.threats['isolated_communities'][:5]:
                self.report_lines.append(
                    f"    - Community {threat['community_id']}: "
                    f"{threat['size']} members, "
                    f"Risk: {threat['risk_level']}, "
                    f"External Connections: {threat['external_connections']}"
                )
        
        self.report_lines.append("")
    
    def add_recommendations(self):
        """Add recommendations section."""
        self.report_lines.append("5. RECOMMENDATIONS")
        self.report_lines.append("-" * 80)
        
        summary = self.threat_analyzer.get_threat_summary()
        
        self.report_lines.append("\n  Based on the analysis, we recommend:")
        
        if summary['echo_chambers_count'] > 0:
            self.report_lines.append(
                f"\n  • Monitor Echo Chambers: {summary['echo_chambers_count']} communities "
                "show signs of echo chamber behavior. Consider promoting diverse content "
                "and cross-community interactions."
            )
        
        if summary['influencer_concentration_count'] > 0:
            self.report_lines.append(
                f"\n  • Address Influencer Concentration: {summary['influencer_concentration_count']} "
                "communities have extreme influence concentration. Monitor for manipulation "
                "or single points of failure."
            )
        
        if summary['spam_clusters_count'] > 0:
            self.report_lines.append(
                f"\n  • Investigate Spam Clusters: {summary['spam_clusters_count']} communities "
                "show suspicious behavior patterns. Review for bot activity or spam."
            )
        
        if summary['isolated_communities_count'] > 0:
            self.report_lines.append(
                f"\n  • Engage Isolated Communities: {summary['isolated_communities_count']} "
                "communities are highly isolated. Consider outreach to prevent radicalization."
            )
        
        if summary['total_threats'] == 0:
            self.report_lines.append("\n  • Network appears healthy with no major threats detected.")
        
        self.report_lines.append("")
    
    def add_footer(self):
        """Add report footer."""
        self.report_lines.append("=" * 80)
        self.report_lines.append("END OF REPORT")
        self.report_lines.append("=" * 80)
    
    def generate_report(self):
        """Generate the complete report."""
        print("\n=== Generating Report ===")
        
        self.add_header()
        self.add_network_overview()
        self.add_top_influencers()
        self.add_community_analysis()
        self.add_threat_analysis()
        self.add_recommendations()
        self.add_footer()
        
        # Write to file
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.report_lines))
        
        print(f"✓ Report saved to {self.output_path}")
        
        return self.output_path


def main():
    """Example usage of ReportGenerator."""
    from importlib import import_module
    
    # Load and prepare graph
    graph_constructor = import_module('graph_construction_02')
    metric_calculator_module = import_module('metric_calculation_03')
    community_detector_module = import_module('community_detection_04')
    threat_analyzer_module = import_module('threat_analysis_06')
    
    # Build graph
    constructor = graph_constructor.GraphConstructor("data/edges.csv", "data/nodes.csv")
    graph = constructor.build_graph()
    
    # Calculate metrics
    calculator = metric_calculator_module.MetricCalculator(graph)
    calculator.calculate_all_metrics()
    calculator.add_metrics_to_graph()
    
    # Detect communities
    detector = community_detector_module.CommunityDetector(graph)
    detector.detect_all_communities()
    detector.add_communities_to_graph()
    
    # Analyze threats
    analyzer = threat_analyzer_module.ThreatAnalyzer(graph)
    analyzer.analyze_all_threats()
    
    # Generate report
    report_generator = ReportGenerator(graph, calculator, detector, analyzer)
    report_path = report_generator.generate_report()
    
    print(f"\nReport generated successfully at: {report_path}")


if __name__ == "__main__":
    main()
