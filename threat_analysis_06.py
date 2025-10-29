"""
Module 6: Threat Analysis
Identifies potential threats: echo chambers, influencer concentration, and spam clusters.
"""

import networkx as nx
from collections import defaultdict, Counter
import numpy as np


class ThreatAnalyzer:
    """Analyzes network for potential security threats and anomalies."""
    
    def __init__(self, graph: nx.Graph, community_attr='community_louvain'):
        """
        Initialize ThreatAnalyzer.
        
        Args:
            graph: NetworkX graph with computed metrics and communities
            community_attr: Name of the community attribute
        """
        self.graph = graph
        self.community_attr = community_attr
        self.threats = {
            'echo_chambers': [],
            'influencer_concentration': [],
            'spam_clusters': [],
            'isolated_communities': []
        }
    
    def detect_echo_chambers(self, clustering_threshold=0.7, isolation_threshold=0.1):
        """
        Detect potential echo chambers: highly clustered communities with few external connections.
        
        Args:
            clustering_threshold: Minimum average clustering coefficient
            isolation_threshold: Maximum ratio of external to internal edges
            
        Returns:
            List of communities flagged as echo chambers
        """
        print("Detecting echo chambers...")
        
        # Group nodes by community
        communities = self._get_community_groups()
        
        echo_chambers = []
        
        for comm_id, members in communities.items():
            if len(members) < 3:  # Skip very small communities
                continue
            
            # Calculate average clustering coefficient
            clustering_values = []
            for node in members:
                node_data = self.graph.nodes[node]
                clustering = node_data.get('clustering_coefficient', 0)
                clustering_values.append(clustering)
            
            avg_clustering = np.mean(clustering_values) if clustering_values else 0
            
            # Count internal vs external edges
            internal_edges = 0
            external_edges = 0
            
            for node in members:
                if self.graph.is_directed():
                    neighbors = list(self.graph.successors(node))
                else:
                    neighbors = list(self.graph.neighbors(node))
                
                for neighbor in neighbors:
                    neighbor_comm = self.graph.nodes[neighbor].get(self.community_attr)
                    if neighbor_comm == comm_id:
                        internal_edges += 1
                    else:
                        external_edges += 1
            
            # Calculate isolation ratio
            total_edges = internal_edges + external_edges
            if total_edges > 0:
                external_ratio = external_edges / total_edges
            else:
                external_ratio = 0
            
            # Flag as echo chamber if highly clustered and isolated
            if avg_clustering >= clustering_threshold and external_ratio <= isolation_threshold:
                echo_chambers.append({
                    'community_id': comm_id,
                    'size': len(members),
                    'avg_clustering': avg_clustering,
                    'external_ratio': external_ratio,
                    'risk_level': 'HIGH' if external_ratio < 0.05 else 'MEDIUM'
                })
        
        self.threats['echo_chambers'] = echo_chambers
        print(f"✓ Found {len(echo_chambers)} potential echo chambers")
        
        return echo_chambers
    
    def detect_influencer_concentration(self, concentration_threshold=0.8):
        """
        Detect communities with extreme influencer concentration.
        
        Args:
            concentration_threshold: Minimum ratio of influence held by top node
            
        Returns:
            List of communities with concentrated influence
        """
        print("Detecting influencer concentration...")
        
        communities = self._get_community_groups()
        concentrated_communities = []
        
        for comm_id, members in communities.items():
            if len(members) < 5:  # Skip very small communities
                continue
            
            # Get betweenness centrality for all members
            betweenness_values = []
            pagerank_values = []
            
            for node in members:
                node_data = self.graph.nodes[node]
                betweenness_values.append(node_data.get('betweenness_centrality', 0))
                pagerank_values.append(node_data.get('pagerank', 0))
            
            # Check concentration
            if betweenness_values:
                total_betweenness = sum(betweenness_values)
                max_betweenness = max(betweenness_values)
                
                if total_betweenness > 0:
                    concentration_ratio = max_betweenness / total_betweenness
                    
                    if concentration_ratio >= concentration_threshold:
                        # Find the dominant influencer
                        max_node = members[betweenness_values.index(max_betweenness)]
                        
                        concentrated_communities.append({
                            'community_id': comm_id,
                            'size': len(members),
                            'dominant_user': max_node,
                            'concentration_ratio': concentration_ratio,
                            'risk_level': 'HIGH' if concentration_ratio > 0.9 else 'MEDIUM'
                        })
        
        self.threats['influencer_concentration'] = concentrated_communities
        print(f"✓ Found {len(concentrated_communities)} communities with influencer concentration")
        
        return concentrated_communities
    
    def detect_spam_clusters(self, min_following_ratio=5.0, min_cluster_size=3):
        """
        Detect potential spam clusters: groups with abnormally high following-to-follower ratios.
        
        Args:
            min_following_ratio: Minimum following/followers ratio
            min_cluster_size: Minimum size to be considered a cluster
            
        Returns:
            List of communities flagged as potential spam clusters
        """
        print("Detecting spam clusters...")
        
        communities = self._get_community_groups()
        spam_clusters = []
        
        for comm_id, members in communities.items():
            if len(members) < min_cluster_size:
                continue
            
            # Calculate following/follower ratios
            suspicious_count = 0
            total_ratio = 0
            
            for node in members:
                node_data = self.graph.nodes[node]
                
                # Get following and followers from user data
                following = node_data.get('following_count', 0)
                followers = node_data.get('followers_count', 0)
                
                if followers > 0:
                    ratio = following / followers
                else:
                    ratio = following  # If no followers, just use following count
                
                total_ratio += ratio
                
                if ratio >= min_following_ratio:
                    suspicious_count += 1
            
            # Flag if majority of community has suspicious ratios
            suspicious_percentage = suspicious_count / len(members)
            avg_ratio = total_ratio / len(members)
            
            if suspicious_percentage >= 0.6:  # 60% or more are suspicious
                spam_clusters.append({
                    'community_id': comm_id,
                    'size': len(members),
                    'suspicious_percentage': suspicious_percentage,
                    'avg_following_ratio': avg_ratio,
                    'risk_level': 'HIGH' if suspicious_percentage > 0.8 else 'MEDIUM'
                })
        
        self.threats['spam_clusters'] = spam_clusters
        print(f"✓ Found {len(spam_clusters)} potential spam clusters")
        
        return spam_clusters
    
    def detect_isolated_communities(self, max_external_connections=2):
        """
        Detect highly isolated communities.
        
        Args:
            max_external_connections: Maximum number of external connections
            
        Returns:
            List of isolated communities
        """
        print("Detecting isolated communities...")
        
        communities = self._get_community_groups()
        isolated_communities = []
        
        for comm_id, members in communities.items():
            if len(members) < 3:
                continue
            
            # Count external connections
            external_connections = set()
            
            for node in members:
                if self.graph.is_directed():
                    neighbors = list(self.graph.successors(node)) + list(self.graph.predecessors(node))
                else:
                    neighbors = list(self.graph.neighbors(node))
                
                for neighbor in neighbors:
                    neighbor_comm = self.graph.nodes[neighbor].get(self.community_attr)
                    if neighbor_comm != comm_id:
                        external_connections.add(neighbor)
            
            # Flag if very few external connections
            if len(external_connections) <= max_external_connections:
                isolated_communities.append({
                    'community_id': comm_id,
                    'size': len(members),
                    'external_connections': len(external_connections),
                    'risk_level': 'HIGH' if len(external_connections) == 0 else 'MEDIUM'
                })
        
        self.threats['isolated_communities'] = isolated_communities
        print(f"✓ Found {len(isolated_communities)} isolated communities")
        
        return isolated_communities
    
    def analyze_all_threats(self):
        """Run all threat detection algorithms."""
        print("\n=== Analyzing Network Threats ===")
        
        self.detect_echo_chambers()
        self.detect_influencer_concentration()
        self.detect_spam_clusters()
        self.detect_isolated_communities()
        
        print("\n✓ Threat analysis completed")
    
    def get_threat_summary(self):
        """
        Get a summary of all detected threats.
        
        Returns:
            Dictionary with threat counts and details
        """
        summary = {
            'total_threats': sum(len(threats) for threats in self.threats.values()),
            'echo_chambers_count': len(self.threats['echo_chambers']),
            'influencer_concentration_count': len(self.threats['influencer_concentration']),
            'spam_clusters_count': len(self.threats['spam_clusters']),
            'isolated_communities_count': len(self.threats['isolated_communities']),
            'details': self.threats
        }
        
        return summary
    
    def _get_community_groups(self):
        """Helper method to group nodes by community."""
        communities = defaultdict(list)
        
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            comm_id = node_data.get(self.community_attr)
            if comm_id is not None:
                communities[comm_id].append(node)
        
        return communities


def main():
    """Example usage of ThreatAnalyzer."""
    from importlib import import_module
    
    # Load and prepare graph
    graph_constructor = import_module('graph_construction_02')
    metric_calculator = import_module('metric_calculation_03')
    community_detector = import_module('community_detection_04')
    
    # Build graph
    constructor = graph_constructor.GraphConstructor("data/edges.csv", "data/nodes.csv")
    graph = constructor.build_graph()
    
    # Add metrics
    calculator = metric_calculator.MetricCalculator(graph)
    calculator.calculate_all_metrics()
    calculator.add_metrics_to_graph()
    
    # Add communities
    detector = community_detector.CommunityDetector(graph)
    detector.detect_all_communities()
    detector.add_communities_to_graph()
    
    # Analyze threats
    analyzer = ThreatAnalyzer(graph)
    analyzer.analyze_all_threats()
    
    # Print summary
    print("\n=== Threat Analysis Summary ===")
    summary = analyzer.get_threat_summary()
    
    print(f"\nTotal threats detected: {summary['total_threats']}")
    print(f"- Echo chambers: {summary['echo_chambers_count']}")
    print(f"- Influencer concentration: {summary['influencer_concentration_count']}")
    print(f"- Spam clusters: {summary['spam_clusters_count']}")
    print(f"- Isolated communities: {summary['isolated_communities_count']}")
    
    # Show details of high-risk threats
    if summary['echo_chambers_count'] > 0:
        print("\nHigh-Risk Echo Chambers:")
        for threat in analyzer.threats['echo_chambers'][:3]:
            if threat['risk_level'] == 'HIGH':
                print(f"  Community {threat['community_id']}: {threat['size']} members, "
                      f"Clustering: {threat['avg_clustering']:.2f}, "
                      f"External: {threat['external_ratio']:.2%}")


if __name__ == "__main__":
    main()
