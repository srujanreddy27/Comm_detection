"""
Module 5: Recommendation Engine
Suggests connections based on graph structure, common neighbors, and community membership.
"""

import networkx as nx
from collections import defaultdict


class RecommendationEngine:
    """Generates connection recommendations for users."""
    
    def __init__(self, graph: nx.Graph, community_attr='community_louvain'):
        """
        Initialize RecommendationEngine.
        
        Args:
            graph: NetworkX graph with computed metrics and communities
            community_attr: Name of the community attribute in the graph
        """
        self.graph = graph
        self.community_attr = community_attr
    
    def get_common_neighbors(self, user_id):
        """
        Get common neighbors between user and all other users.
        
        Args:
            user_id: Target user ID
            
        Returns:
            Dictionary mapping user_id -> number of common neighbors
        """
        if user_id not in self.graph:
            raise ValueError(f"User {user_id} not in graph")
        
        # Get user's neighbors
        if self.graph.is_directed():
            # For directed graphs, consider out-neighbors (people user follows)
            user_neighbors = set(self.graph.successors(user_id))
        else:
            user_neighbors = set(self.graph.neighbors(user_id))
        
        # Calculate common neighbors with all other users
        common_neighbors = {}
        for node in self.graph.nodes():
            if node == user_id:
                continue
            
            if self.graph.is_directed():
                node_neighbors = set(self.graph.successors(node))
            else:
                node_neighbors = set(self.graph.neighbors(node))
            
            common = len(user_neighbors.intersection(node_neighbors))
            if common > 0:
                common_neighbors[node] = common
        
        return common_neighbors
    
    def recommend_by_common_neighbors(self, user_id, n=10):
        """
        Recommend users based on common neighbors.
        
        Args:
            user_id: Target user ID
            n: Number of recommendations to return
            
        Returns:
            List of tuples (recommended_user_id, common_neighbor_count, reason)
        """
        # Get users already connected to
        if self.graph.is_directed():
            already_following = set(self.graph.successors(user_id))
        else:
            already_following = set(self.graph.neighbors(user_id))
        
        # Get common neighbors
        common_neighbors = self.get_common_neighbors(user_id)
        
        # Filter out users already connected to
        candidates = {
            node: count for node, count in common_neighbors.items()
            if node not in already_following
        }
        
        # Sort by common neighbors count
        sorted_candidates = sorted(candidates.items(), key=lambda x: x[1], reverse=True)[:n]
        
        # Format recommendations
        recommendations = [
            (node, count, f"{count} common connections")
            for node, count in sorted_candidates
        ]
        
        return recommendations
    
    def recommend_by_community(self, user_id, n=10):
        """
        Recommend users from the same community.
        
        Args:
            user_id: Target user ID
            n: Number of recommendations to return
            
        Returns:
            List of tuples (recommended_user_id, score, reason)
        """
        if user_id not in self.graph:
            raise ValueError(f"User {user_id} not in graph")
        
        # Get user's community
        user_data = self.graph.nodes[user_id]
        if self.community_attr not in user_data:
            raise ValueError(f"Community attribute '{self.community_attr}' not found")
        
        user_community = user_data[self.community_attr]
        
        # Get users already connected to
        if self.graph.is_directed():
            already_following = set(self.graph.successors(user_id))
        else:
            already_following = set(self.graph.neighbors(user_id))
        
        # Find users in same community
        candidates = []
        for node in self.graph.nodes():
            if node == user_id or node in already_following:
                continue
            
            node_data = self.graph.nodes[node]
            if self.community_attr in node_data and node_data[self.community_attr] == user_community:
                # Use PageRank or in-degree as a quality score
                score = node_data.get('pagerank', node_data.get('in_degree', 0))
                candidates.append((node, score))
        
        # Sort by score
        sorted_candidates = sorted(candidates, key=lambda x: x[1], reverse=True)[:n]
        
        # Format recommendations
        recommendations = [
            (node, score, f"Same community (Community {user_community})")
            for node, score in sorted_candidates
        ]
        
        return recommendations
    
    def recommend_hybrid(self, user_id, n=10, weight_common=0.6, weight_community=0.4):
        """
        Hybrid recommendation combining common neighbors and community membership.
        
        Args:
            user_id: Target user ID
            n: Number of recommendations to return
            weight_common: Weight for common neighbors score
            weight_community: Weight for community score
            
        Returns:
            List of tuples (recommended_user_id, combined_score, reason)
        """
        if user_id not in self.graph:
            raise ValueError(f"User {user_id} not in graph")
        
        # Get users already connected to
        if self.graph.is_directed():
            already_following = set(self.graph.successors(user_id))
        else:
            already_following = set(self.graph.neighbors(user_id))
        
        # Get user's community
        user_data = self.graph.nodes[user_id]
        user_community = user_data.get(self.community_attr, None)
        
        # Calculate common neighbors
        common_neighbors = self.get_common_neighbors(user_id)
        max_common = max(common_neighbors.values()) if common_neighbors else 1
        
        # Score all candidates
        candidate_scores = defaultdict(lambda: {'common': 0, 'community': 0, 'reasons': []})
        
        # Score by common neighbors
        for node, count in common_neighbors.items():
            if node not in already_following:
                normalized_score = count / max_common
                candidate_scores[node]['common'] = normalized_score
                candidate_scores[node]['reasons'].append(f"{count} common connections")
        
        # Score by community membership and influence
        if user_community is not None:
            for node in self.graph.nodes():
                if node == user_id or node in already_following:
                    continue
                
                node_data = self.graph.nodes[node]
                if self.community_attr in node_data and node_data[self.community_attr] == user_community:
                    # Use PageRank as influence score
                    influence = node_data.get('pagerank', 0)
                    candidate_scores[node]['community'] = influence * 100  # Scale up
                    candidate_scores[node]['reasons'].append(f"Same community")
        
        # Combine scores
        final_scores = []
        for node, scores in candidate_scores.items():
            combined = (scores['common'] * weight_common + 
                       scores['community'] * weight_community)
            reason = ", ".join(scores['reasons'])
            final_scores.append((node, combined, reason))
        
        # Sort and return top N
        sorted_recommendations = sorted(final_scores, key=lambda x: x[1], reverse=True)[:n]
        
        return sorted_recommendations
    
    def recommend_influencers(self, user_id, n=10, metric='pagerank'):
        """
        Recommend influential users not yet connected to.
        
        Args:
            user_id: Target user ID
            n: Number of recommendations to return
            metric: Influence metric to use ('pagerank', 'betweenness_centrality', etc.)
            
        Returns:
            List of tuples (recommended_user_id, influence_score, reason)
        """
        if user_id not in self.graph:
            raise ValueError(f"User {user_id} not in graph")
        
        # Get users already connected to
        if self.graph.is_directed():
            already_following = set(self.graph.successors(user_id))
        else:
            already_following = set(self.graph.neighbors(user_id))
        
        # Find influential users
        candidates = []
        for node in self.graph.nodes():
            if node == user_id or node in already_following:
                continue
            
            node_data = self.graph.nodes[node]
            influence_score = node_data.get(metric, 0)
            candidates.append((node, influence_score))
        
        # Sort by influence
        sorted_candidates = sorted(candidates, key=lambda x: x[1], reverse=True)[:n]
        
        # Format recommendations
        recommendations = [
            (node, score, f"High {metric}: {score:.6f}")
            for node, score in sorted_candidates
        ]
        
        return recommendations


def main():
    """Example usage of RecommendationEngine."""
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
    
    # Create recommendation engine
    engine = RecommendationEngine(graph)
    
    # Pick a user (use a user with some connections)
    test_user = 3026368  # This user has many followers
    
    print(f"\n=== Recommendations for User {test_user} ===")
    
    # Common neighbors recommendations
    print("\n1. Based on Common Neighbors:")
    recommendations = engine.recommend_by_common_neighbors(test_user, n=5)
    for rank, (user, score, reason) in enumerate(recommendations, 1):
        print(f"  {rank}. User {user}: {reason}")
    
    # Community-based recommendations
    print("\n2. Based on Community Membership:")
    recommendations = engine.recommend_by_community(test_user, n=5)
    for rank, (user, score, reason) in enumerate(recommendations, 1):
        print(f"  {rank}. User {user}: {reason} (score: {score:.6f})")
    
    # Hybrid recommendations
    print("\n3. Hybrid Recommendations:")
    recommendations = engine.recommend_hybrid(test_user, n=5)
    for rank, (user, score, reason) in enumerate(recommendations, 1):
        print(f"  {rank}. User {user}: {reason} (score: {score:.4f})")
    
    # Influencer recommendations
    print("\n4. Influential Users to Follow:")
    recommendations = engine.recommend_influencers(test_user, n=5)
    for rank, (user, score, reason) in enumerate(recommendations, 1):
        print(f"  {rank}. User {user}: {reason}")


if __name__ == "__main__":
    main()
