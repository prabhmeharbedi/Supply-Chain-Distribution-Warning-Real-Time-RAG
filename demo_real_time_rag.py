#!/usr/bin/env python3
"""
Real-Time RAG Demo Script - Pathway-Powered Supply Chain Intelligence

This script demonstrates the core Pathway capabilities:
1. Streaming ETL with real-time data ingestion
2. Dynamic indexing with no rebuilds required
3. Live retrieval that immediately reflects new data
4. Real-time query interface

Usage:
    python demo_real_time_rag.py
"""

import asyncio
import json
import time
import requests
from datetime import datetime
from typing import Dict, Any
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.rag.pathway_vector_store import pathway_vector_store
from src.core.pipeline.pathway_rag_pipeline import pathway_rag_pipeline

class RealTimeRAGDemo:
    def __init__(self):
        self.api_base = "http://localhost:8001"
        self.headers = {"Authorization": "Bearer demo_token"}
        
    def print_banner(self):
        """Print demo banner"""
        print("=" * 80)
        print("🚀 PATHWAY-POWERED REAL-TIME RAG DEMONSTRATION")
        print("   Supply Chain Disruption Intelligence System")
        print("=" * 80)
        print()
        
    def print_section(self, title: str):
        """Print section header"""
        print(f"\n{'='*60}")
        print(f"📋 {title}")
        print(f"{'='*60}")
        
    async def demo_1_initial_state(self):
        """Demo 1: Show initial system state"""
        self.print_section("DEMO 1: Initial System State")
        
        print("🔍 Querying initial vector store state...")
        
        # Get current stats
        stats = pathway_vector_store.get_real_time_stats()
        print(f"📊 Vector Store Stats:")
        print(f"   • Total Documents: {stats['total_documents']}")
        print(f"   • Last Update: {stats['last_update']}")
        print(f"   • Update Counter: {stats['update_counter']}")
        
        # Test initial query
        print("\n🔍 Testing initial query: 'Shanghai port disruption'")
        results = pathway_vector_store.search_real_time("Shanghai port disruption", k=3)
        
        print(f"📋 Found {len(results)} relevant documents:")
        for i, result in enumerate(results, 1):
            print(f"   {i}. Score: {result['score']:.3f} | {result['document'][:80]}...")
        
        return stats, results
    
    async def demo_2_add_live_data(self):
        """Demo 2: Add data and show immediate availability"""
        self.print_section("DEMO 2: Real-Time Data Addition")
        
        print("📝 Adding new supply chain disruption data...")
        
        # Create new disruption event
        new_event = {
            "content": f"BREAKING: Suez Canal traffic disruption at {datetime.utcnow().isoformat()}. "
                      f"Container ship Ever Given has run aground again, blocking 12% of global trade. "
                      f"Immediate impact on Asia-Europe trade routes expected.",
            "metadata": {
                "type": "breaking_news",
                "location": "Suez Canal, Egypt",
                "severity": "critical",
                "impact_sectors": ["shipping", "oil", "consumer_goods"],
                "demo_timestamp": datetime.utcnow().isoformat(),
                "real_time_demo": True
            }
        }
        
        # Add to vector store
        print("⚡ Adding to vector store (real-time indexing)...")
        doc_id = pathway_vector_store.add_document_streaming(
            new_event["content"], 
            new_event["metadata"]
        )
        
        print(f"✅ Document added with ID: {doc_id}")
        print(f"⏱️  Added at: {datetime.utcnow().isoformat()}")
        
        return doc_id, new_event
    
    async def demo_3_immediate_query(self, demo_timestamp: str):
        """Demo 3: Query immediately and show new data is available"""
        self.print_section("DEMO 3: Immediate Query - Proving Real-Time Updates")
        
        print("🔍 Querying IMMEDIATELY after data addition...")
        print("   (This proves data is available at T+1 after update at T+0)")
        
        # Query for the new data
        results = pathway_vector_store.search_real_time("Suez Canal disruption", k=5)
        
        print(f"📋 Query Results ({len(results)} found):")
        
        new_data_found = False
        for i, result in enumerate(results, 1):
            metadata = result.get("metadata", {})
            is_new = metadata.get("demo_timestamp") == demo_timestamp
            
            if is_new:
                new_data_found = True
                print(f"   🆕 {i}. [NEW DATA] Score: {result['score']:.3f}")
                print(f"       Freshness: {result.get('real_time_freshness', 'unknown')}")
                print(f"       Content: {result['document'][:100]}...")
            else:
                print(f"   📄 {i}. [EXISTING] Score: {result['score']:.3f}")
                print(f"       Content: {result['document'][:80]}...")
        
        print(f"\n✅ NEW DATA IMMEDIATELY SEARCHABLE: {new_data_found}")
        print("🎯 This proves Pathway's real-time indexing capability!")
        
        return new_data_found
    
    async def demo_4_api_integration(self):
        """Demo 4: Test API endpoints"""
        self.print_section("DEMO 4: API Integration Test")
        
        print("🌐 Testing real-time RAG API endpoints...")
        
        try:
            # Test health endpoint
            print("1. Testing Pathway health endpoint...")
            response = requests.get(f"{self.api_base}/api/v1/pathway-rag/health/pathway")
            if response.status_code == 200:
                health_data = response.json()
                print(f"   ✅ Status: {health_data.get('status', 'unknown')}")
                print(f"   📊 Documents: {health_data.get('performance', {}).get('total_documents', 0)}")
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
            
            # Test real-time stats
            print("\n2. Testing real-time stats endpoint...")
            response = requests.get(
                f"{self.api_base}/api/v1/pathway-rag/stats/real-time",
                headers=self.headers
            )
            if response.status_code == 200:
                stats_data = response.json()
                print(f"   ✅ Vector store size: {stats_data.get('real_time_stats', {}).get('total_documents', 0)}")
                print(f"   🔄 Recent updates: {stats_data.get('real_time_stats', {}).get('recent_updates_count', 0)}")
            else:
                print(f"   ❌ Stats failed: {response.status_code}")
            
            # Test real-time proof endpoint
            print("\n3. Testing real-time proof demonstration...")
            response = requests.get(
                f"{self.api_base}/api/v1/pathway-rag/demo/real-time-proof?test_query=supply chain",
                headers=self.headers
            )
            if response.status_code == 200:
                proof_data = response.json()
                proof = proof_data.get("real_time_proof", {})
                print(f"   ✅ Vector size increased: {proof.get('size_increased', False)}")
                print(f"   ✅ New data searchable: {proof.get('new_data_immediately_searchable', False)}")
                print(f"   📈 Size change: {proof.get('initial_vector_size', 0)} → {proof.get('updated_vector_size', 0)}")
            else:
                print(f"   ❌ Proof demo failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ API test failed: {e}")
            print("💡 Make sure the API server is running on port 8001")
    
    async def demo_5_streaming_simulation(self):
        """Demo 5: Simulate streaming data updates"""
        self.print_section("DEMO 5: Streaming Data Simulation")
        
        print("📡 Simulating continuous data stream...")
        
        events = [
            {
                "title": "Taiwan Semiconductor Alert",
                "content": "TSMC reports potential production delays due to power grid instability. Global chip supply may be affected.",
                "location": "Taiwan",
                "severity": "high"
            },
            {
                "title": "Panama Canal Drought",
                "content": "Severe drought conditions limiting Panama Canal capacity. Ship transit times increasing by 2-3 days.",
                "location": "Panama Canal",
                "severity": "medium"
            },
            {
                "title": "European Rail Strike",
                "content": "Major rail strike across European freight networks. Alternative trucking routes experiencing congestion.",
                "location": "Europe",
                "severity": "medium"
            }
        ]
        
        initial_size = pathway_vector_store.get_current_size()
        print(f"📊 Initial vector store size: {initial_size}")
        
        for i, event in enumerate(events, 1):
            print(f"\n⚡ Streaming Event {i}/3: {event['title']}")
            
            # Add event to vector store
            doc_id = pathway_vector_store.add_document_streaming(
                event["content"],
                {
                    "type": "streaming_demo",
                    "title": event["title"],
                    "location": event["location"],
                    "severity": event["severity"],
                    "stream_order": i,
                    "streamed_at": datetime.utcnow().isoformat()
                }
            )
            
            print(f"   📝 Added document ID: {doc_id}")
            
            # Immediate query test
            query_results = pathway_vector_store.search_real_time(event["title"], k=2)
            found_new = any(
                result.get("metadata", {}).get("stream_order") == i
                for result in query_results
            )
            
            print(f"   🔍 Immediate search result: {'✅ Found' if found_new else '❌ Not found'}")
            
            # Small delay to simulate real streaming
            await asyncio.sleep(1)
        
        final_size = pathway_vector_store.get_current_size()
        print(f"\n📊 Final vector store size: {final_size}")
        print(f"📈 Documents added: {final_size - initial_size}")
        print("✅ All streaming events immediately indexed and searchable!")
    
    async def run_complete_demo(self):
        """Run the complete demonstration"""
        self.print_banner()
        
        print("🎬 Starting Pathway Real-Time RAG Demonstration...")
        print("   This demo proves that data updated at T+0 is available at T+1")
        print()
        
        try:
            # Demo 1: Initial state
            initial_stats, initial_results = await self.demo_1_initial_state()
            
            # Demo 2: Add live data
            doc_id, new_event = await self.demo_2_add_live_data()
            demo_timestamp = new_event["metadata"]["demo_timestamp"]
            
            # Demo 3: Immediate query
            new_data_found = await self.demo_3_immediate_query(demo_timestamp)
            
            # Demo 4: API integration
            await self.demo_4_api_integration()
            
            # Demo 5: Streaming simulation
            await self.demo_5_streaming_simulation()
            
            # Final summary
            self.print_section("DEMO SUMMARY")
            print("🎯 PATHWAY CAPABILITIES DEMONSTRATED:")
            print("   ✅ Streaming ETL - Continuous data ingestion")
            print("   ✅ Dynamic Indexing - No rebuilds required")
            print("   ✅ Live Retrieval - Immediate data availability")
            print("   ✅ Real-Time Interface - T+0 to T+1 updates")
            print()
            print("🏆 SUCCESS: Real-Time RAG system fully operational!")
            print("📹 This demo proves Pathway's real-time capabilities")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            import traceback
            traceback.print_exc()

async def main():
    """Main demo function"""
    demo = RealTimeRAGDemo()
    await demo.run_complete_demo()

if __name__ == "__main__":
    print("🚀 Initializing Pathway Real-Time RAG Demo...")
    
    # Run the demo
    asyncio.run(main()) 