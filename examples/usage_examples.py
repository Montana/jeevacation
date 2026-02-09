import asyncio
import os
from pathlib import Path

from epstein_enhanced.core.search_client import EpsteinSearchClient
from epstein_enhanced.core.linkedin_parser import LinkedInParser
from epstein_enhanced.ai.analyzer import AIAnalyzer
from epstein_enhanced.utils.report_generator import ReportGenerator
from epstein_enhanced.utils.network_graph import NetworkGraphGenerator
from epstein_enhanced.database.models import Database


async def example_basic_search():
    print("=" * 60)
    print("Example 1: Basic Search")
    print("=" * 60)
    
    contacts = LinkedInParser.parse_csv('path/to/Connections.csv')
    print(f"Loaded {len(contacts)} contacts")
    
    contacts = LinkedInParser.filter_common_names(contacts)
    print(f"After filtering: {len(contacts)} contacts")
    
    async with EpsteinSearchClient() as client:
        names = [c.full_name for c in contacts]
        results = await client.batch_search(names, batch_size=10)
        
        matches = []
        for contact in contacts:
            contact_results = results.get(contact.full_name, [])
            if contact_results:
                matches.append({
                    'name': contact.full_name,
                    'company': contact.company,
                    'position': contact.position,
                    'mentions': len(contact_results)
                })
        
        print(f"\nFound {len(matches)} contacts with matches:")
        for match in matches[:5]:
            print(f"  - {match['name']}: {match['mentions']} mentions")


async def example_with_ai_analysis():
    print("\n" + "=" * 60)
    print("Example 2: Search with AI Analysis")
    print("=" * 60)
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set. Skipping AI example.")
        return
    
    analyzer = AIAnalyzer(api_key=api_key)
    
    contacts = LinkedInParser.parse_csv('path/to/Connections.csv')[:5]
    
    async with EpsteinSearchClient() as client:
        for contact in contacts:
            results = await client.search_name(contact.full_name)
            
            if results:
                excerpts = [r.get('excerpt', '') for r in results]
                
                analysis = analyzer.analyze_mentions(
                    contact.full_name,
                    excerpts,
                    contact.position,
                    contact.company
                )
                
                if analysis:
                    print(f"\n{contact.full_name}:")
                    print(f"  Category: {analysis.category}")
                    print(f"  Sentiment: {analysis.sentiment}")
                    print(f"  Summary: {analysis.summary}")
                    print(f"  Confidence: {analysis.confidence:.2f}")


async def example_network_graph():
    print("\n" + "=" * 60)
    print("Example 3: Network Graph Visualization")
    print("=" * 60)
    
    contacts = LinkedInParser.parse_csv('path/to/Connections.csv')
    
    results = []
    async with EpsteinSearchClient() as client:
        names = [c.full_name for c in contacts]
        search_results = await client.batch_search(names)
        
        for contact in contacts:
            contact_results = search_results.get(contact.full_name, [])
            if contact_results:
                results.append({
                    'name': contact.full_name,
                    'company': contact.company,
                    'position': contact.position,
                    'total_mentions': len(contact_results),
                    'results': [
                        {'document_path': r.get('file_path', '')}
                        for r in contact_results
                    ]
                })
    
    generator = NetworkGraphGenerator()
    html = generator.generate_interactive_graph(results)
    
    output_path = 'network_graph.html'
    with open(output_path, 'w') as f:
        f.write(html)
    
    print(f"✅ Network graph saved to {output_path}")
    
    clusters = generator.find_clusters(results)
    print(f"\nFound {len(clusters)} clusters:")
    for i, cluster in enumerate(clusters[:3], 1):
        print(f"  Cluster {i}: {', '.join(cluster[:5])}")


async def example_false_positive_detection():
    print("\n" + "=" * 60)
    print("Example 4: False Positive Detection")
    print("=" * 60)
    
    analyzer = AIAnalyzer()
    
    test_cases = [
        {
            'name': 'John Smith',
            'excerpts': ['John Smith was mentioned.'],
            'position': None,
            'company': None
        },
        {
            'name': 'Dr. Jane Williams',
            'excerpts': [
                'Dr. Jane Williams testified as an expert witness.',
                'Dr. Williams provided medical records.',
                'Williams stated that...'
            ],
            'position': 'Chief Medical Officer',
            'company': 'Memorial Hospital'
        }
    ]
    
    for test in test_cases:
        score = analyzer.calculate_false_positive_score(
            test['name'],
            test['excerpts'],
            test['position'],
            test['company']
        )
        
        print(f"\n{test['name']}:")
        print(f"  False Positive Score: {score:.2f}")
        print(f"  Assessment: {'⚠️ High risk' if score > 0.6 else '✅ Low risk'}")


def example_report_generation():
    print("\n" + "=" * 60)
    print("Example 5: Report Generation")
    print("=" * 60)
    
    results = [
        {
            'name': 'John Doe',
            'company': 'Acme Inc',
            'position': 'CEO',
            'total_mentions': 5,
            'results': [
                {
                    'document_path': '/dataset1/doc001.pdf',
                    'excerpt': 'John Doe testified regarding...',
                    'pdf_url': 'https://example.com/doc001.pdf'
                }
            ]
        }
    ]
    
    generator = ReportGenerator()
    
    html_path = generator.generate_html_report(results, 'example_report.html')
    print(f"✅ HTML report: {html_path}")
    
    json_path = generator.generate_json_report(results, 'example_report.json')
    print(f"✅ JSON export: {json_path}")
    
    csv_path = generator.generate_csv_report(results, 'example_report.csv')
    print(f"✅ CSV export: {csv_path}")


def example_database_operations():
    print("\n" + "=" * 60)
    print("Example 6: Database Operations")
    print("=" * 60)
    
    db = Database('sqlite:///example.db')
    db.create_tables()
    print("✅ Database initialized")
    
    from epstein_enhanced.database.models import Contact, Match
    
    session = db.get_session()
    
    contact = Contact(
        first_name='John',
        last_name='Doe',
        full_name='John Doe',
        email='john@example.com',
        company='Acme Inc',
        position='CEO'
    )
    session.add(contact)
    session.commit()
    
    all_contacts = session.query(Contact).all()
    print(f"📊 Total contacts: {len(all_contacts)}")
    
    session.close()


async def main():
    print("\n🚀 Epstein Enhanced - Example Usage\n")
    
    print("⚠️  Update 'path/to/Connections.csv' in the examples before running!\n")
    
    
    print("\n" + "=" * 60)
    print("✅ Examples completed!")
    print("=" * 60)


if __name__ == '__main__':
    asyncio.run(main())
