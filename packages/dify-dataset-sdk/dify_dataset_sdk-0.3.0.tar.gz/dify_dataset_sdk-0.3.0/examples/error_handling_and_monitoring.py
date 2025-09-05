"""
Error Handling and Monitoring Example

Demonstrates how to use the Dify Knowledge SDK for error handling and system monitoring, including:
- Best practices for exception handling
- Implementation of a retry mechanism
- Performance monitoring and logging
- Health checks and failure recovery
"""

import functools
import json
import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict

from dify_dataset_sdk import DifyDatasetClient
from dify_dataset_sdk.exceptions import (
    DifyAPIError,
    DifyAuthenticationError,
    DifyConnectionError,
    DifyNotFoundError,
    DifyTimeoutError,
    DifyValidationError,
)


class DifyMonitor:
    """Dify SDK Monitor"""

    def __init__(self, api_key: str, base_url: str = "https://api.dify.ai"):
        self.client = DifyDatasetClient(api_key=api_key, base_url=base_url)
        self.setup_logging()
        self.metrics = {
            "requests": 0,
            "successes": 0,
            "failures": 0,
            "retries": 0,
            "avg_response_time": 0.0,
        }
        self.error_history = []

    def setup_logging(self):
        """Configure the logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("dify_sdk.log"), logging.StreamHandler()],
        )
        self.logger = logging.getLogger("DifyMonitor")

    def retry_on_failure(self, max_retries: int = 3, delay: float = 1.0):
        """Retry decorator"""

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None

                for attempt in range(max_retries + 1):
                    try:
                        start_time = time.time()
                        result = func(*args, **kwargs)
                        end_time = time.time()

                        # Update monitoring metrics
                        self.metrics["requests"] += 1
                        self.metrics["successes"] += 1
                        response_time = end_time - start_time
                        self._update_avg_response_time(response_time)

                        if attempt > 0:
                            self.metrics["retries"] += attempt
                            self.logger.info(
                                f"Operation successful after {attempt} retries"
                            )

                        return result

                    except (DifyTimeoutError, DifyConnectionError) as e:
                        last_exception = e
                        self.metrics["requests"] += 1
                        self.metrics["failures"] += 1

                        if attempt < max_retries:
                            wait_time = delay * (2**attempt)  # Exponential backoff
                            self.logger.warning(
                                f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}"
                            )
                            time.sleep(wait_time)
                        else:
                            self.logger.error(f"All retries failed: {e}")
                            self._record_error(str(e), func.__name__)
                            raise

                    except (DifyAuthenticationError, DifyValidationError) as e:
                        # Authentication and validation errors are not retried
                        self.metrics["requests"] += 1
                        self.metrics["failures"] += 1
                        self.logger.error(f"Non-retriable error: {e}")
                        self._record_error(str(e), func.__name__)
                        raise

                    except DifyAPIError as e:
                        last_exception = e
                        self.metrics["requests"] += 1
                        self.metrics["failures"] += 1

                        if attempt < max_retries:
                            wait_time = delay * (2**attempt)
                            self.logger.warning(
                                f"API error, attempt {attempt + 1}, retrying in {wait_time}s: {e}"
                            )
                            time.sleep(wait_time)
                        else:
                            self.logger.error(f"API call ultimately failed: {e}")
                            self._record_error(str(e), func.__name__)
                            raise

                # If all retries have failed
                self._record_error(str(last_exception), func.__name__)
                raise last_exception

            return wrapper

        return decorator

    def _update_avg_response_time(self, response_time: float):
        """Update average response time"""
        if self.metrics["successes"] == 1:
            self.metrics["avg_response_time"] = response_time
        else:
            # Using a weighted average
            self.metrics["avg_response_time"] = (
                self.metrics["avg_response_time"] * (self.metrics["successes"] - 1)
                + response_time
            ) / self.metrics["successes"]

    def _record_error(self, error: str, operation: str):
        """Record error history"""
        self.error_history.append(
            {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "operation": operation,
                "error": error,
            }
        )

        # Keep only the last 50 errors
        if len(self.error_history) > 50:
            self.error_history = self.error_history[-50:]

    @retry_on_failure(max_retries=3, delay=1.0)
    def safe_create_dataset(self, name: str, **kwargs) -> Any:
        """Safely create a dataset"""
        self.logger.info(f"Creating dataset: {name}")
        return self.client.create_dataset(name=name, **kwargs)

    @retry_on_failure(max_retries=2, delay=0.5)
    def safe_list_datasets(self, **kwargs) -> Any:
        """Safely list datasets"""
        self.logger.info("Listing datasets")
        return self.client.list_datasets(**kwargs)

    @retry_on_failure(max_retries=3, delay=1.0)
    def safe_create_document(
        self, dataset_id: str, name: str, text: str, **kwargs
    ) -> Any:
        """Safely create a document"""
        self.logger.info(f"Creating document: {name}")
        return self.client.create_document_by_text(
            dataset_id=dataset_id, name=name, text=text, **kwargs
        )

    @retry_on_failure(max_retries=2, delay=0.5)
    def safe_retrieve(self, dataset_id: str, query: str, **kwargs) -> Any:
        """Safely retrieve"""
        self.logger.info(f"Retrieving query: {query}")
        return self.client.retrieve(dataset_id=dataset_id, query=query, **kwargs)

    def health_check(self) -> Dict[str, Any]:
        """Health Check"""
        print("🏥 Performing health check...")

        health_status = {
            "overall": "healthy",
            "checks": {},
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Check API connectivity
        try:
            self.client.list_datasets(limit=1)
            health_status["checks"]["api_connection"] = {
                "status": "healthy",
                "message": "API connection is normal",
            }
        except DifyAuthenticationError:
            health_status["checks"]["api_connection"] = {
                "status": "unhealthy",
                "message": "Authentication failed, please check the API key",
            }
            health_status["overall"] = "unhealthy"
        except Exception as e:
            health_status["checks"]["api_connection"] = {
                "status": "unhealthy",
                "message": f"API connection failed: {e}",
            }
            health_status["overall"] = "unhealthy"

        # Check performance metrics
        success_rate = (
            self.metrics["successes"] / self.metrics["requests"] * 100
            if self.metrics["requests"] > 0
            else 0
        )

        if success_rate >= 90:
            performance_status = "healthy"
        elif success_rate >= 70:
            performance_status = "warning"
        else:
            performance_status = "unhealthy"
            health_status["overall"] = "unhealthy"

        health_status["checks"]["performance"] = {
            "status": performance_status,
            "success_rate": f"{success_rate:.1f}%",
            "avg_response_time": f"{self.metrics['avg_response_time']:.3f}s",
        }

        # Check error rate
        error_rate = (
            self.metrics["failures"] / self.metrics["requests"] * 100
            if self.metrics["requests"] > 0
            else 0
        )

        if error_rate <= 5:
            error_status = "healthy"
        elif error_rate <= 15:
            error_status = "warning"
        else:
            error_status = "unhealthy"
            health_status["overall"] = "unhealthy"

        health_status["checks"]["error_rate"] = {
            "status": error_status,
            "error_rate": f"{error_rate:.1f}%",
            "recent_errors": len(self.error_history),
        }

        # Print health status
        status_emoji = {"healthy": "✅", "warning": "⚠️", "unhealthy": "❌"}
        print(
            f"  Overall status: {status_emoji.get(health_status['overall'], '❓')} {health_status['overall']}"
        )

        for check_name, check_result in health_status["checks"].items():
            emoji = status_emoji.get(check_result["status"], "❓")
            print(f"  {check_name}: {emoji} {check_result['status']}")
            if "message" in check_result:
                print(f"    {check_result['message']}")

        return health_status

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get monitoring metrics summary"""
        print("📊 Monitoring Metrics Summary:")

        summary = {
            "total_requests": self.metrics["requests"],
            "successful_requests": self.metrics["successes"],
            "failed_requests": self.metrics["failures"],
            "retry_count": self.metrics["retries"],
            "success_rate": (
                self.metrics["successes"] / self.metrics["requests"] * 100
                if self.metrics["requests"] > 0
                else 0
            ),
            "avg_response_time": self.metrics["avg_response_time"],
            "recent_errors": len(self.error_history),
        }

        print(f"  Total requests: {summary['total_requests']}")
        print(f"  Successful requests: {summary['successful_requests']}")
        print(f"  Failed requests: {summary['failed_requests']}")
        print(f"  Retry count: {summary['retry_count']}")
        print(f"  Success rate: {summary['success_rate']:.1f}%")
        print(f"  Average response time: {summary['avg_response_time']:.3f}s")
        print(f"  Recent errors: {summary['recent_errors']}")

        return summary

    def export_monitoring_data(self) -> str:
        """Export monitoring data"""
        print("📤 Exporting monitoring data...")

        monitoring_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "metrics": self.metrics,
            "error_history": self.error_history,
            "health_status": self.health_check(),
        }

        export_file = Path(f"dify_monitoring_{int(time.time())}.json")
        export_file.write_text(
            json.dumps(monitoring_data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        print(f"  ✅ Monitoring data has been exported to: {export_file}")
        return str(export_file)

    def demonstrate_error_scenarios(self):
        """Demonstrate various error scenarios"""
        print("\n🧪 Demonstrating error handling scenarios...")

        # Scenario 1: Creating a dataset with a duplicate name
        print("  Scenario 1: Creating a dataset with a duplicate name")
        try:
            self.safe_create_dataset("Duplicate Test Dataset", permission="only_me")
            self.safe_create_dataset(
                "Duplicate Test Dataset", permission="only_me"
            )  # This will fail
        except DifyAPIError as e:
            print(f"    Expected error caught: {e}")

        # Scenario 2: Accessing a non-existent resource
        print("  Scenario 2: Accessing a non-existent resource")
        try:
            self.client.get_dataset("non-existent-dataset-id")
        except DifyNotFoundError as e:
            print(f"    Expected error caught: {e}")
            self._record_error(str(e), "get_dataset")

        # Scenario 3: Passing invalid parameters
        print("  Scenario 3: Passing invalid parameters")
        try:
            self.client.list_datasets(limit=1000)  # Exceeds limit
        except DifyValidationError as e:
            print(f"    Expected error caught: {e}")
            self._record_error(str(e), "list_datasets")

        print("  ✅ Error scenario demonstration complete")

    def close(self):
        """Close the client connection"""
        self.client.close()


def main():
    """Main function - Demonstrates the complete flow of error handling and monitoring"""
    # Configure API information
    api_key = "YOUR_API_KEY_HERE"  # Replace with your actual API key
    base_url = "https://api.dify.ai"  # Dify API address

    monitor = DifyMonitor(api_key=api_key, base_url=base_url)

    try:
        print("🚀 Dify Knowledge SDK - Error Handling and Monitoring Example")
        print("=" * 60)

        # 1. Perform some normal operations
        print("📝 Performing normal operations...")
        dataset = monitor.safe_create_dataset(
            f"Monitoring Test Dataset_{int(time.time())}",
            description="For monitoring and error handling demonstration",
            permission="only_me",
        )

        if dataset:
            dataset_id = dataset.id

            # Create document
            monitor.safe_create_document(
                dataset_id=dataset_id,
                name="Test Document",
                text="This is the content of a document used for testing the monitoring functionality.",
                indexing_technique="high_quality",
            )

            # Wait for indexing to complete
            time.sleep(3)

            # Perform retrieval
            monitor.safe_retrieve(
                dataset_id=dataset_id,
                query="test content",
                retrieval_model={"search_method": "semantic_search", "top_k": 5},
            )

        # 2. Demonstrate error scenarios
        monitor.demonstrate_error_scenarios()

        # 3. Perform a health check
        health_status = monitor.health_check()

        # 4. Get monitoring metrics
        metrics = monitor.get_metrics_summary()

        # 5. Export monitoring data
        export_file = monitor.export_monitoring_data()

        print("\n✅ Error handling and monitoring example finished!")
        print("📊 Summary:")
        print(f"  - Total Requests: {metrics['total_requests']}")
        print(f"  - Success Rate: {metrics['success_rate']:.1f}%")
        print(f"  - System Status: {health_status['overall']}")
        print(f"  - Monitoring Data: {export_file}")

        print("\n💡 Monitoring Suggestions:")
        print("  - Periodically perform health checks")
        print("  - Monitor success rate and response times")
        print("  - Set an appropriate retry policy")
        print("  - Log and analyze error patterns")

    except Exception as e:
        print(f"\n❌ An error occurred during the monitoring demonstration: {e}")
        monitor.logger.error(f"Demonstration failed: {e}")

    finally:
        # Close the client
        monitor.close()


if __name__ == "__main__":
    main()
