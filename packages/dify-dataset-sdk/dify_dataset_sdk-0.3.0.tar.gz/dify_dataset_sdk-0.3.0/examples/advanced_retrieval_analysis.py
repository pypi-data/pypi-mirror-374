"""
Advanced Retrieval and Analysis Example

Demonstrates how to use the Dify Knowledge SDK for advanced retrieval and data analysis.
"""

import json
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List

from dify_dataset_sdk import DifyDatasetClient


class AdvancedRetrievalAnalyzer:
    """Advanced Retrieval Analyzer"""

    def __init__(self, api_key: str, base_url: str = "https://api.dify.ai"):
        self.client = DifyDatasetClient(api_key=api_key, base_url=base_url)

    def setup_test_environment(self) -> str:
        """Sets up the test environment."""
        print("🔧 Setting up retrieval test environment...")

        timestamp = int(time.time())
        dataset = self.client.create_dataset(
            name=f"Retrieval_Analysis_Test_{timestamp}",
            description="Test dataset for advanced retrieval analysis",
            permission="only_me",
        )

        # Create test documents
        test_docs = [
            {
                "name": "Python Programming Guide",
                "content": "Python is a high-level programming language with a simple syntax. It supports object-oriented programming and has a rich library ecosystem.",
            },
            {
                "name": "Database Design",
                "content": "Relational database design needs to consider normalization. The SQL language is used for querying and manipulating data.",
            },
            {
                "name": "Introduction to Machine Learning",
                "content": "Machine learning includes supervised and unsupervised learning. Common algorithms include linear regression, decision trees, etc.",
            },
            {
                "name": "Frontend Development",
                "content": "Frontend development uses HTML, CSS, and JavaScript. Modern frameworks include React, Vue, etc.",
            },
            {
                "name": "System Architecture",
                "content": "System architecture design must consider scalability. Microservices architecture is suitable for large applications.",
            },
        ]

        for doc in test_docs:
            self.client.create_document_by_text(
                dataset_id=dataset.id,
                name=doc["name"],
                text=doc["content"],
                indexing_technique="high_quality",
            )
            time.sleep(1)

        print("  ⏳ Waiting for document indexing to complete...")
        time.sleep(5)
        return dataset.id

    def compare_retrieval_methods(
        self, dataset_id: str, queries: List[str]
    ) -> Dict[str, Any]:
        """Compares different retrieval methods."""
        print("\n🔍 Comparing retrieval methods...")

        methods = [
            {
                "name": "semantic",
                "config": {"search_method": "semantic_search", "top_k": 5},
            },
            {
                "name": "full_text",
                "config": {"search_method": "full_text_search", "top_k": 5},
            },
            {
                "name": "hybrid",
                "config": {"search_method": "hybrid_search", "top_k": 5},
            },
        ]

        results = {}

        for method in methods:
            print(f"  Testing method: {method['name']}")
            method_results = []

            for query in queries:
                try:
                    start_time = time.time()
                    response = self.client.retrieve(dataset_id, query, method["config"])
                    end_time = time.time()

                    result_count = (
                        len(response.records) if hasattr(response, "records") else 0
                    )
                    method_results.append(
                        {
                            "query": query,
                            "response_time": end_time - start_time,
                            "result_count": result_count,
                        }
                    )
                    print(f"    '{query}' - {result_count} results")

                except Exception as e:
                    print(f"    Query failed: {e}")
                    method_results.append(
                        {"query": query, "response_time": 0, "result_count": 0}
                    )

                time.sleep(0.5)

            results[method["name"]] = method_results

        return results

    def analyze_performance(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes retrieval performance."""
        print("\n📊 Analyzing retrieval performance...")

        analysis = {}

        for method, metrics in results.items():
            response_times = [
                m["response_time"] for m in metrics if m["response_time"] > 0
            ]
            result_counts = [m["result_count"] for m in metrics]

            analysis[method] = {
                "avg_response_time": statistics.mean(response_times)
                if response_times
                else 0,
                "avg_result_count": statistics.mean(result_counts),
                "success_rate": len([m for m in metrics if m["result_count"] > 0])
                / len(metrics)
                * 100,
            }

            print(
                f"  {method}: Success rate {analysis[method]['success_rate']:.1f}%, Average response time {analysis[method]['avg_response_time']:.3f}s"
            )

        return analysis

    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """Generates an analysis report."""
        print("\n📋 Generating retrieval analysis report...")

        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "analysis": analysis,
            "recommendations": [],
        }

        if analysis:
            best_method = max(
                analysis.keys(), key=lambda m: analysis[m]["success_rate"]
            )
            report["recommendations"].append(
                f"Recommended to use the {best_method} method"
            )

        report_file = Path(f"retrieval_report_{int(time.time())}.json")
        report_file.write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        print(f"  ✅ Report saved: {report_file}")
        return str(report_file)

    def close(self):
        """Closes the client connection."""
        self.client.close()


def main():
    """Main function"""
    api_key = "YOUR_API_KEY_HERE"  # Replace with your actual API key

    analyzer = AdvancedRetrievalAnalyzer(api_key=api_key)

    try:
        print("🚀 Dify Knowledge SDK - Advanced Retrieval Analysis Example")
        print("=" * 60)

        # Set up the test environment
        dataset_id = analyzer.setup_test_environment()

        # Test queries
        test_queries = [
            "Python programming",
            "Database design",
            "Machine learning",
            "Frontend development",
            "System architecture",
        ]

        # Compare retrieval methods
        results = analyzer.compare_retrieval_methods(dataset_id, test_queries)

        # Analyze performance
        analysis = analyzer.analyze_performance(results)

        # Generate report
        report_file = analyzer.generate_report(analysis)

        print("\n✅ Retrieval analysis complete!")
        print(f"📝 Report file: {report_file}")

    except Exception as e:
        print(f"\n❌ An error occurred during the analysis: {e}")

    finally:
        analyzer.close()


if __name__ == "__main__":
    main()
