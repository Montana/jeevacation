import networkx as nx
import plotly.graph_objects as go
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class NetworkGraphGenerator:
    
    def generate_interactive_graph(self, results: List[Dict[str, Any]]) -> str:
        G = nx.Graph()
        
        documents = {}
        
        for result in results:
            person_name = result['name']
            
            G.add_node(
                person_name,
                node_type='person',
                mentions=result['total_mentions'],
                company=result.get('company', ''),
                position=result.get('position', '')
            )
            
            for doc_result in result['results']:
                doc_path = doc_result['document_path']
                
                if doc_path not in documents:
                    documents[doc_path] = []
                    G.add_node(doc_path, node_type='document')
                
                documents[doc_path].append(person_name)
                G.add_edge(person_name, doc_path)
        
        for doc_path, people in documents.items():
            if len(people) > 1:
                for i, person1 in enumerate(people):
                    for person2 in people[i+1:]:
                        if G.has_edge(person1, person2):
                            G[person1][person2]['weight'] += 1
                        else:
                            G.add_edge(person1, person2, weight=1)
        
        pos = nx.spring_layout(G, k=0.5, iterations=50)
        
        edge_traces = []
        node_traces = []
        
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            weight = edge[2].get('weight', 1) if edge[2] else 1
            
            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=weight * 0.5, color='rgba(125,125,125,0.3)'),
                hoverinfo='none',
                showlegend=False
            )
            edge_traces.append(edge_trace)
        
        person_nodes_x = []
        person_nodes_y = []
        person_node_text = []
        person_node_size = []
        
        for node, data in G.nodes(data=True):
            if data.get('node_type') == 'person':
                x, y = pos[node]
                person_nodes_x.append(x)
                person_nodes_y.append(y)
                
                mentions = data.get('mentions', 0)
                company = data.get('company', 'N/A')
                position = data.get('position', 'N/A')
                
                person_node_text.append(
                    f"{node}<br>"
                    f"Company: {company}<br>"
                    f"Position: {position}<br>"
                    f"Mentions: {mentions}"
                )
                person_node_size.append(10 + mentions * 2)
        
        person_trace = go.Scatter(
            x=person_nodes_x,
            y=person_nodes_y,
            mode='markers+text',
            text=[name.split()[0] for name, _ in [(n, d) for n, d in G.nodes(data=True) if d.get('node_type') == 'person']],
            textposition='top center',
            hovertext=person_node_text,
            hoverinfo='text',
            marker=dict(
                size=person_node_size,
                color='
                line=dict(width=2, color='white')
            ),
            name='People',
            showlegend=True
        )
        
        doc_nodes_x = []
        doc_nodes_y = []
        doc_node_text = []
        
        for node, data in G.nodes(data=True):
            if data.get('node_type') == 'document':
                x, y = pos[node]
                doc_nodes_x.append(x)
                doc_nodes_y.append(y)
                
                people_count = len(documents.get(node, []))
                doc_node_text.append(f"Document: {node}<br>People mentioned: {people_count}")
        
        doc_trace = go.Scatter(
            x=doc_nodes_x,
            y=doc_nodes_y,
            mode='markers',
            hovertext=doc_node_text,
            hoverinfo='text',
            marker=dict(
                size=8,
                color='
                symbol='square',
                line=dict(width=1, color='white')
            ),
            name='Documents',
            showlegend=True
        )
        
        fig = go.Figure(
            data=edge_traces + [person_trace, doc_trace],
            layout=go.Layout(
                title='LinkedIn Contacts Network in Epstein Documents',
                titlefont=dict(size=20),
                showlegend=True,
                hovermode='closest',
                margin=dict(b=0, l=0, r=0, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='rgba(240,240,240,0.9)',
                height=800
            )
        )
        
        return fig.to_html(include_plotlyjs='cdn')
    
    def find_clusters(self, results: List[Dict[str, Any]]) -> List[List[str]]:
        G = nx.Graph()
        documents = {}
        
        for result in results:
            person_name = result['name']
            G.add_node(person_name)
            
            for doc_result in result['results']:
                doc_path = doc_result['document_path']
                if doc_path not in documents:
                    documents[doc_path] = []
                documents[doc_path].append(person_name)
        
        for people in documents.values():
            if len(people) > 1:
                for i, person1 in enumerate(people):
                    for person2 in people[i+1:]:
                        if G.has_edge(person1, person2):
                            G[person1][person2]['weight'] += 1
                        else:
                            G.add_edge(person1, person2, weight=1)
        
        try:
            import networkx.algorithms.community as nx_comm
            communities = nx_comm.greedy_modularity_communities(G, weight='weight')
            return [list(community) for community in communities]
        except Exception as e:
            logger.error(f"Error finding clusters: {e}")
            return []
