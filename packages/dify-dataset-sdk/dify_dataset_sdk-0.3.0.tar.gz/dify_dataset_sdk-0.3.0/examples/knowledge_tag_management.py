"""
Knowledge Tag Management Example

Demonstrates how to use the Dify Knowledge SDK to manage knowledge tags, including:
- Creating and managing knowledge tags
- Binding datasets to tags
- Batch operations on tags
- Building tag classification systems
"""

import time
from typing import Any, Dict, List

from dify_dataset_sdk import DifyDatasetClient
from dify_dataset_sdk.exceptions import DifyAPIError


class KnowledgeTagManager:
    """Knowledge Tag Manager"""

    def __init__(self, api_key: str, base_url: str = "https://api.dify.ai"):
        self.client = DifyDatasetClient(api_key=api_key, base_url=base_url)
        self.created_tags = []  # Track created tags
        self.created_datasets = []  # Track created datasets

    def create_tag_category_system(self) -> Dict[str, Any]:
        """Create a complete tag classification system"""
        print("🏷️  Creating tag classification system...")

        # Define tag categories
        tag_categories = {
            "Department": ["Engineering", "Sales", "Marketing", "HR"],
            "Project": ["Project A", "Project B", "Project C"],
            "Document Type": [
                "Technical Docs",
                "User Manual",
                "API Docs",
                "Design Docs",
            ],
            "Priority": ["High Priority", "Medium Priority", "Low Priority"],
            "Status": ["Draft", "Under Review", "Published", "Archived"],
        }

        created_tags = {}

        for category, tags in tag_categories.items():
            created_tags[category] = []
            for tag_name in tags:
                try:
                    tag = self.client.create_knowledge_tag(
                        name=f"{category}-{tag_name}"
                    )
                    created_tags[category].append(tag)
                    self.created_tags.append(tag)
                    print(f"  ✅ Created tag: {tag.name}")
                    time.sleep(0.5)  # Avoid too frequent requests
                except DifyAPIError as e:
                    print(f"  ❌ Failed to create tag {tag_name}: {e}")

        return created_tags

    def create_sample_datasets(self) -> List[Dict[str, Any]]:
        """Create sample datasets"""
        print("\n📚 Creating sample datasets...")

        datasets_config = [
            {
                "name": "Technical Documentation",
                "description": "Repository for all technical documents",
                "tags": [
                    "Department-Engineering",
                    "Document Type-Technical Docs",
                    "Priority-High Priority",
                ],
            },
            {
                "name": "User Manual Collection",
                "description": "User operation guides and manuals",
                "tags": [
                    "Document Type-User Manual",
                    "Priority-Medium Priority",
                    "Status-Published",
                ],
            },
            {
                "name": "Project A Documents",
                "description": "All documents related to Project A",
                "tags": ["Project-Project A", "Status-Under Review"],
            },
            {
                "name": "API Reference Documentation",
                "description": "API interface documentation and examples",
                "tags": [
                    "Department-Engineering",
                    "Document Type-API Docs",
                    "Priority-High Priority",
                ],
            },
        ]

        created_datasets = []

        for config in datasets_config:
            try:
                # Create dataset
                dataset = self.client.create_dataset(
                    name=f"{config['name']}_{int(time.time())}",
                    description=config["description"],
                    permission="only_me",
                )
                self.created_datasets.append(dataset)
                created_datasets.append({"dataset": dataset, "config": config})
                print(f"  ✅ Created dataset: {dataset.name}")
                time.sleep(0.5)

            except DifyAPIError as e:
                print(f"  ❌ Failed to create dataset {config['name']}: {e}")

        return created_datasets

    def bind_datasets_to_tags(
        self, datasets: List[Dict[str, Any]], tag_mapping: Dict[str, Any]
    ):
        """Bind datasets to corresponding tags"""
        print("\n🔗 Binding datasets to tags...")

        # Create mapping from tag names to IDs
        tag_name_to_id = {}
        for _category, tags in tag_mapping.items():
            for tag in tags:
                tag_name_to_id[tag.name] = tag.id

        for dataset_info in datasets:
            dataset = dataset_info["dataset"]
            config = dataset_info["config"]

            # Get tag IDs to bind
            tag_ids = []
            for tag_name in config["tags"]:
                if tag_name in tag_name_to_id:
                    tag_ids.append(tag_name_to_id[tag_name])

            if tag_ids:
                try:
                    self.client.bind_dataset_to_tag(dataset.id, tag_ids)
                    print(f"  ✅ Bound dataset {dataset.name} to {len(tag_ids)} tags")
                except DifyAPIError as e:
                    print(f"  ❌ Failed to bind {dataset.name}: {e}")

    def demonstrate_tag_queries(self):
        """Demonstrate tag query functionality"""
        print("\n🔍 Demonstrating tag query functionality...")

        try:
            # Get all tags
            all_tags = self.client.list_knowledge_tags()
            print(
                f"  📊 Total of {len(all_tags.data) if hasattr(all_tags, 'data') else len(all_tags)} tags"
            )

            # Display some tags
            tags_list = all_tags.data if hasattr(all_tags, "data") else all_tags
            for i, tag in enumerate(tags_list[:5]):
                print(f"    {i + 1}. {tag.name} (ID: {tag.id})")

            # Query tags for specific dataset
            if self.created_datasets:
                dataset = self.created_datasets[0]
                bound_tags = self.client.get_dataset_tags(dataset.id)
                print(f"  🏷️  Tags bound to dataset {dataset.name}:")
                for tag in bound_tags:
                    print(f"    - {tag.name}")

        except DifyAPIError as e:
            print(f"  ❌ Failed to query tags: {e}")

    def demonstrate_tag_filtering(self):
        """Demonstrate dataset filtering based on tags"""
        print("\n🎯 Demonstrating tag filtering functionality...")

        try:
            # Get Engineering department tag IDs
            all_tags = self.client.list_knowledge_tags()
            tags_list = all_tags.data if hasattr(all_tags, "data") else all_tags

            engineering_tag_ids = []
            for tag in tags_list:
                if "Engineering" in tag.name:
                    engineering_tag_ids.append(tag.id)

            if engineering_tag_ids:
                # Filter datasets by tags
                filtered_datasets = self.client.list_datasets(
                    tag_ids=engineering_tag_ids[
                        :1
                    ],  # Use only the first engineering tag
                    limit=10,
                )
                print(
                    f"  📋 Engineering department related datasets ({filtered_datasets.total} total):"
                )
                for dataset in filtered_datasets.data[:3]:
                    print(f"    - {dataset.get('name', 'Unknown')}")
            else:
                print("  ℹ️  No Engineering department related tags found")

        except DifyAPIError as e:
            print(f"  ❌ Tag filtering failed: {e}")

    def update_tag_names(self):
        """Demonstrate tag renaming"""
        print("\n✏️  Demonstrating tag renaming...")

        if self.created_tags:
            try:
                # Rename the first tag
                tag = self.created_tags[0]
                new_name = f"{tag.name}_Updated_{int(time.time())}"

                updated_tag = self.client.update_knowledge_tag(tag.id, new_name)
                print(f"  ✅ Tag renamed: {tag.name} -> {updated_tag.name}")

            except DifyAPIError as e:
                print(f"  ❌ Tag renaming failed: {e}")

    def manage_tag_bindings(self):
        """Demonstrate tag binding management"""
        print("\n🔄 Demonstrating tag binding management...")

        if self.created_datasets and self.created_tags:
            try:
                dataset = self.created_datasets[0]
                tag = self.created_tags[-1]  # Use the last created tag

                # Unbind tag
                self.client.unbind_dataset_from_tag(dataset.id, tag.id)
                print(f"  ✅ Unbound tag: {tag.name} from dataset {dataset.name}")

                # Re-bind
                self.client.bind_dataset_to_tag(dataset.id, [tag.id])
                print(f"  ✅ Re-bound tag: {tag.name} to dataset {dataset.name}")

            except DifyAPIError as e:
                print(f"  ❌ Tag binding management failed: {e}")

    def cleanup_resources(self):
        """Clean up created resources"""
        print("\n🧹 Cleaning up created resources...")

        # Delete datasets
        for dataset in self.created_datasets:
            try:
                self.client.delete_dataset(dataset.id)
                print(f"  🗑️  Deleted dataset: {dataset.name}")
            except DifyAPIError as e:
                print(f"  ❌ Failed to delete dataset {dataset.name}: {e}")

        # Delete tags
        for tag in self.created_tags:
            try:
                self.client.delete_knowledge_tag(tag.id)
                print(f"  🗑️  Deleted tag: {tag.name}")
            except DifyAPIError as e:
                print(f"  ❌ Failed to delete tag {tag.name}: {e}")

    def close(self):
        """Close client connection"""
        self.client.close()


def main():
    """Main function - Demonstrates the complete knowledge tag management workflow"""
    # Configure API information
    api_key = "YOUR_API_KEY_HERE"  # Replace with your actual API key
    base_url = "https://api.dify.ai"  # Dify API address

    manager = KnowledgeTagManager(api_key=api_key, base_url=base_url)

    try:
        print("🚀 Dify Knowledge SDK - Knowledge Tag Management Example")
        print("=" * 60)

        # 1. Create tag classification system
        tag_mapping = manager.create_tag_category_system()

        # 2. Create sample datasets
        datasets = manager.create_sample_datasets()

        # 3. Bind datasets to tags
        manager.bind_datasets_to_tags(datasets, tag_mapping)

        # 4. Demonstrate tag queries
        manager.demonstrate_tag_queries()

        # 5. Demonstrate tag filtering
        manager.demonstrate_tag_filtering()

        # 6. Demonstrate tag renaming
        manager.update_tag_names()

        # 7. Demonstrate tag binding management
        manager.manage_tag_bindings()

        print("\n✅ Knowledge tag management example completed!")
        print(
            "💡 Tip: When using in production, pay attention to tag naming conventions and permission management"
        )

    except Exception as e:
        print(f"\n❌ Error occurred during example execution: {e}")

    finally:
        # Clean up resources (optional - comment this line if you want to keep the created tags and datasets)
        # manager.cleanup_resources()

        # Close client
        manager.close()


if __name__ == "__main__":
    main()
