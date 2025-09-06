"""
Ground Truth Computation Correctness Tests

Verify that batched computation and merging results are consistent with one-time computation results.
Test configuration: 10,000 training vectors, 100 query vectors, top_k=10
Batch settings: train_batch=1000, test_batch=10
"""

import tempfile

import numpy as np
import pandas as pd
import pytest
from pymilvus import CollectionSchema, DataType, FieldSchema
from usearch.index import MetricKind, search

from milvus_dataset import ConfigManager, StorageType, load_dataset


class TestGroundTruthCorrectness:
    """Test class for Ground Truth computation correctness"""

    def create_test_dataset(self, temp_dir, train_count=1000, test_count=50, dim=32):
        """Create test dataset"""
        # Initialize storage
        config_manager = ConfigManager()
        config_manager.init_storage(
            root_path=temp_dir,
            storage_type=StorageType.LOCAL,
        )

        # Define schema
        schema = CollectionSchema(
            fields=[
                FieldSchema("id", DataType.INT64, is_primary=True),
                FieldSchema("text", DataType.VARCHAR, max_length=1000),
                FieldSchema("embedding", DataType.FLOAT_VECTOR, dim=dim),
            ],
            description="GT correctness test dataset",
        )

        # Load dataset
        dataset = load_dataset("gt-test", schema=schema)

        # Generate data with fixed seed
        np.random.seed(42)

        # Generate training data
        train_data = pd.DataFrame(
            {
                "id": range(train_count),
                "text": [f"train_{i}" for i in range(train_count)],
                "embedding": [np.random.rand(dim).astype(np.float32) for _ in range(train_count)],
            }
        )

        # Generate test data
        test_data = pd.DataFrame(
            {
                "id": range(train_count, train_count + test_count),
                "text": [f"test_{i}" for i in range(test_count)],
                "embedding": [np.random.rand(dim).astype(np.float32) for _ in range(test_count)],
            }
        )

        # Write data
        with dataset["train"].get_writer(mode="append") as writer:
            writer.write(train_data)

        with dataset["test"].get_writer(mode="append") as writer:
            writer.write(test_data)

        return dataset, train_data, test_data

    def compute_reference_gt(self, train_data, test_data, top_k=10, metric="cosine"):
        """Compute reference ground truth (compute all at once)"""
        # Extract vectors
        train_vectors = np.vstack(train_data["embedding"].values).astype(np.float32)
        test_vectors = np.vstack(test_data["embedding"].values).astype(np.float32)
        train_ids = train_data["id"].values

        # Metric type mapping
        metric_mapping = {
            "cosine": MetricKind.Cos,
            "inner_product": MetricKind.IP,
            "euclidean": MetricKind.L2sq,
        }

        usearch_metric = metric_mapping[metric]

        # Compute using USearch
        matches = search(train_vectors, test_vectors, top_k, usearch_metric, exact=True)

        # Extract results
        reference_results = []
        for query_idx, query_matches in enumerate(matches):
            neighbor_indices = [match.key for match in query_matches]
            distances = [match.distance for match in query_matches]

            # Map to actual training IDs
            neighbor_ids = [train_ids[idx] for idx in neighbor_indices]

            # For inner_product, adjust distances
            if metric == "inner_product":
                distances = [d - 1 for d in distances]

            reference_results.append(
                {
                    "test_id": test_data.iloc[query_idx]["id"],
                    "neighbor_ids": neighbor_ids,
                    "distances": distances,
                }
            )

        return reference_results

    def get_batched_results(
        self, dataset, metric="cosine", train_batch_size=100, test_batch_size=10, top_k=10
    ):
        """Get batched computation results"""
        # Use dataset's compute_neighbors method
        dataset.compute_neighbors(
            vector_field_name="embedding",
            pk_field_name="id",
            top_k=top_k,
            metric_type=metric,
            max_rows_per_epoch=train_batch_size,
            test_batch_size=test_batch_size,
            device="cpu",
        )

        # Get neighbors dataset
        neighbors_dataset = dataset["neighbors"]

        # Read computation results
        neighbors_file = f"{neighbors_dataset.root_path}/{neighbors_dataset.name}/{neighbors_dataset.split}/neighbors-vector-embedding-pk-id-expr-None-metric-{metric}.parquet"

        assert neighbors_dataset.fs.exists(
            neighbors_file
        ), f"Result file does not exist: {neighbors_file}"

        # Read results
        with neighbors_dataset.fs.open(neighbors_file, "rb") as f:
            results_df = pd.read_parquet(f)

        return results_df

    def compare_results(self, reference_results, batched_results_df, tolerance=1e-6):
        """Compare reference results and batched computation results"""
        # Convert batched results to comparison format
        batched_results = []
        for _, row in batched_results_df.iterrows():
            batched_results.append(
                {
                    "test_id": row["id"],
                    "neighbor_ids": row["neighbors_id"],
                    "distances": row["neighbors_distance"],
                }
            )

        # Sort by test_id
        reference_results = sorted(reference_results, key=lambda x: x["test_id"])
        batched_results = sorted(batched_results, key=lambda x: x["test_id"])

        assert (
            len(reference_results) == len(batched_results)
        ), f"Result count mismatch: reference={len(reference_results)}, batched={len(batched_results)}"

        for i, (ref, batch) in enumerate(zip(reference_results, batched_results, strict=False)):
            # Verify test_id
            assert (
                ref["test_id"] == batch["test_id"]
            ), f"Query {i}: test_id mismatch {ref['test_id']} != {batch['test_id']}"

            # Compare neighbor IDs
            ref_ids = ref["neighbor_ids"]
            batch_ids = batch["neighbor_ids"]

            # Convert arrays to lists for comparison
            if isinstance(ref_ids, np.ndarray):
                ref_ids = ref_ids.tolist()
            if isinstance(batch_ids, np.ndarray):
                batch_ids = batch_ids.tolist()

            assert (
                ref_ids == batch_ids
            ), f"Query {i} (test_id={ref['test_id']}): neighbor ID mismatch\n  Reference: {ref_ids}\n  Batched: {batch_ids}"

            # Compare distances
            ref_dists = ref["distances"]
            batch_dists = batch["distances"]

            # Ensure distances are in list format
            if isinstance(ref_dists, np.ndarray):
                ref_dists = ref_dists.tolist()
            if isinstance(batch_dists, np.ndarray):
                batch_dists = batch_dists.tolist()

            max_dist_diff = max(abs(r - b) for r, b in zip(ref_dists, batch_dists, strict=False))
            assert max_dist_diff <= tolerance, (
                f"Query {i} (test_id={ref['test_id']}): distance difference too large {max_dist_diff:.8f}\n"
                f"  Reference distances: {ref_dists}\n  Batched distances: {batch_dists}"
            )

    @pytest.mark.parametrize("metric", ["cosine", "euclidean", "inner_product"])
    def test_ground_truth_correctness_small(self, metric):
        """Test ground truth computation correctness for small-scale data"""
        with tempfile.TemporaryDirectory(prefix="gt_test_small_") as temp_dir:
            # Create small-scale test data - suitable for CI environment
            dataset, train_data, test_data = self.create_test_dataset(
                temp_dir,
                train_count=500,  # 500 training vectors
                test_count=20,  # 20 test vectors
                dim=32,  # 32 dimensions
            )

            # Compute reference results
            reference_results = self.compute_reference_gt(
                train_data,
                test_data,
                top_k=5,  # top-5 to speed up computation
                metric=metric,
            )

            # Test batched computation
            batched_results_df = self.get_batched_results(
                dataset,
                metric=metric,
                train_batch_size=100,  # training batch size
                test_batch_size=5,  # test batch size
                top_k=5,
            )

            # Compare results
            self.compare_results(reference_results, batched_results_df)

    @pytest.mark.parametrize("metric", ["cosine", "euclidean"])
    def test_ground_truth_correctness_medium(self, metric):
        """Test ground truth computation correctness for medium-scale data"""
        with tempfile.TemporaryDirectory(prefix="gt_test_medium_") as temp_dir:
            # Create medium-scale test data
            dataset, train_data, test_data = self.create_test_dataset(
                temp_dir,
                train_count=2000,  # 2000 training vectors
                test_count=50,  # 50 test vectors
                dim=64,  # 64 dimensions
            )

            # Compute reference results
            reference_results = self.compute_reference_gt(
                train_data, test_data, top_k=10, metric=metric
            )

            # Test batched computation
            batched_results_df = self.get_batched_results(
                dataset,
                metric=metric,
                train_batch_size=200,  # training batch size
                test_batch_size=10,  # test batch size
                top_k=10,
            )

            # Compare results
            self.compare_results(reference_results, batched_results_df)

    def test_edge_case_topk_across_batches(self):
        """Test edge case where top_k requires spanning multiple training batches"""
        with tempfile.TemporaryDirectory(prefix="gt_test_edge_") as temp_dir:
            # Create small dataset for edge case testing
            dataset, train_data, test_data = self.create_test_dataset(
                temp_dir,
                train_count=100,  # 100 training vectors
                test_count=10,  # 10 test vectors
                dim=32,
            )

            # Compute reference results - top_k=15 needs to span multiple training batches
            reference_results = self.compute_reference_gt(
                train_data, test_data, top_k=15, metric="cosine"
            )

            # Test batched computation - train_batch_size=20, need to span 5 batches to get 15 neighbors
            batched_results_df = self.get_batched_results(
                dataset,
                metric="cosine",
                train_batch_size=20,  # training batch size is 20
                test_batch_size=3,  # test batch size is 3
                top_k=15,
            )

            # Compare results
            self.compare_results(reference_results, batched_results_df)

    def test_different_batch_sizes(self):
        """Test different batch size combinations"""
        with tempfile.TemporaryDirectory(prefix="gt_test_batch_sizes_") as temp_dir:
            dataset, train_data, test_data = self.create_test_dataset(
                temp_dir, train_count=300, test_count=15, dim=32
            )

            # Compute reference results
            reference_results = self.compute_reference_gt(
                train_data, test_data, top_k=8, metric="cosine"
            )

            # Test multiple batch size combinations
            batch_configs = [
                (50, 3),  # train_batch=50, test_batch=3
                (75, 5),  # train_batch=75, test_batch=5
                (100, 7),  # train_batch=100, test_batch=7
            ]

            for train_batch_size, test_batch_size in batch_configs:
                # Recompute (because previous results will be overwritten)
                batched_results_df = self.get_batched_results(
                    dataset,
                    metric="cosine",
                    train_batch_size=train_batch_size,
                    test_batch_size=test_batch_size,
                    top_k=8,
                )

                # Compare results
                self.compare_results(reference_results, batched_results_df)

    @pytest.mark.slow
    def test_ground_truth_correctness_large(self):
        """Test ground truth computation correctness for large-scale data - only run in slow tests"""
        with tempfile.TemporaryDirectory(prefix="gt_test_large_") as temp_dir:
            # Create larger-scale test data - closer to real-world scenarios
            dataset, train_data, test_data = self.create_test_dataset(
                temp_dir,
                train_count=10000,  # 10,000 training vectors
                test_count=100,  # 100 test vectors
                dim=64,  # 64 dimensions
            )

            # Only test cosine to save time
            reference_results = self.compute_reference_gt(
                train_data, test_data, top_k=10, metric="cosine"
            )

            # Test batched computation - using original required batch sizes
            batched_results_df = self.get_batched_results(
                dataset,
                metric="cosine",
                train_batch_size=1000,  # training batch size 1000
                test_batch_size=10,  # test batch size 10
                top_k=10,
            )

            # Compare results
            self.compare_results(reference_results, batched_results_df)

    def get_batched_results_gpu(
        self, dataset, metric="cosine", train_batch_size=100, test_batch_size=10, top_k=10
    ):
        """Get GPU batched computation results"""
        # Use dataset's compute_neighbors method, force GPU usage
        dataset.compute_neighbors(
            vector_field_name="embedding",
            pk_field_name="id",
            top_k=top_k,
            metric_type=metric,
            max_rows_per_epoch=train_batch_size,
            test_batch_size=test_batch_size,
            device="cuda",  # Force GPU usage
        )

        # Get neighbors dataset
        neighbors_dataset = dataset["neighbors"]

        # Read computation results
        neighbors_file = f"{neighbors_dataset.root_path}/{neighbors_dataset.name}/{neighbors_dataset.split}/neighbors-vector-embedding-pk-id-expr-None-metric-{metric}.parquet"

        assert neighbors_dataset.fs.exists(
            neighbors_file
        ), f"Result file does not exist: {neighbors_file}"

        # Read results
        with neighbors_dataset.fs.open(neighbors_file, "rb") as f:
            results_df = pd.read_parquet(f)

        return results_df

    @pytest.mark.gpu
    @pytest.mark.parametrize("metric", ["cosine", "euclidean"])
    def test_gpu_ground_truth_correctness_small(self, metric):
        """Test GPU ground truth computation correctness for small-scale data"""
        pytest.importorskip("cupy", reason="cupy not available")
        pytest.importorskip("cuvs", reason="cuvs not available")

        with tempfile.TemporaryDirectory(prefix="gt_test_gpu_small_") as temp_dir:
            # Create small-scale test data
            dataset, train_data, test_data = self.create_test_dataset(
                temp_dir,
                train_count=800,  # 800 training vectors
                test_count=20,  # 20 test vectors
                dim=64,  # 64 dimensions, suitable for GPU computation
            )

            # Compute reference results
            reference_results = self.compute_reference_gt(
                train_data,
                test_data,
                top_k=8,
                metric=metric,
            )

            # Test GPU batched computation
            batched_results_df = self.get_batched_results_gpu(
                dataset,
                metric=metric,
                train_batch_size=200,  # GPU training batch size
                test_batch_size=5,  # GPU test batch size
                top_k=8,
            )

            # Compare results
            self.compare_results(reference_results, batched_results_df)

    @pytest.mark.gpu
    @pytest.mark.parametrize("metric", ["cosine", "euclidean"])
    def test_gpu_ground_truth_correctness_medium(self, metric):
        """Test GPU ground truth computation correctness for medium-scale data"""
        pytest.importorskip("cupy", reason="cupy not available")
        pytest.importorskip("cuvs", reason="cuvs not available")

        with tempfile.TemporaryDirectory(prefix="gt_test_gpu_medium_") as temp_dir:
            # Create medium-scale test data
            dataset, train_data, test_data = self.create_test_dataset(
                temp_dir,
                train_count=3000,  # 3000 training vectors
                test_count=50,  # 50 test vectors
                dim=128,  # 128 dimensions
            )

            # Compute reference results
            reference_results = self.compute_reference_gt(
                train_data, test_data, top_k=10, metric=metric
            )

            # Test GPU batched computation
            batched_results_df = self.get_batched_results_gpu(
                dataset,
                metric=metric,
                train_batch_size=500,  # GPU training batch size
                test_batch_size=10,  # GPU test batch size
                top_k=10,
            )

            # Compare results
            self.compare_results(reference_results, batched_results_df)

    @pytest.mark.gpu
    def test_gpu_edge_case_topk_across_batches(self):
        """Test GPU edge case where top_k requires spanning multiple training batches"""
        pytest.importorskip("cupy", reason="cupy not available")
        pytest.importorskip("cuvs", reason="cuvs not available")

        with tempfile.TemporaryDirectory(prefix="gt_test_gpu_edge_") as temp_dir:
            # Create small dataset for edge case testing
            dataset, train_data, test_data = self.create_test_dataset(
                temp_dir,
                train_count=150,  # 150 training vectors
                test_count=10,  # 10 test vectors
                dim=64,
            )

            # Compute reference results - top_k=20 needs to span multiple training batches
            reference_results = self.compute_reference_gt(
                train_data, test_data, top_k=20, metric="cosine"
            )

            # Test GPU batched computation
            batched_results_df = self.get_batched_results_gpu(
                dataset,
                metric="cosine",
                train_batch_size=30,  # GPU training batch size is 30, need to span 5 batches to get 20 neighbors
                test_batch_size=3,  # GPU test batch size is 3
                top_k=20,
            )

            # Compare results
            self.compare_results(reference_results, batched_results_df)

    @pytest.mark.gpu
    def test_gpu_vs_cpu_consistency(self):
        """Test consistency between GPU and CPU computation results"""
        pytest.importorskip("cupy", reason="cupy not available")
        pytest.importorskip("cuvs", reason="cuvs not available")

        with tempfile.TemporaryDirectory(prefix="gt_test_gpu_vs_cpu_") as temp_dir:
            # Create test data
            dataset, train_data, test_data = self.create_test_dataset(
                temp_dir,
                train_count=1000,  # 1000 training vectors
                test_count=25,  # 25 test vectors
                dim=128,  # 128 dimensions
            )

            # First compute with CPU
            cpu_results_df = self.get_batched_results(
                dataset,
                metric="cosine",
                train_batch_size=200,
                test_batch_size=5,
                top_k=10,
            )

            # Then compute with GPU (need to recreate dataset because results will be overwritten)
            dataset2, _, _ = self.create_test_dataset(
                temp_dir + "_gpu",
                train_count=1000,
                test_count=25,
                dim=128,
            )

            gpu_results_df = self.get_batched_results_gpu(
                dataset2,
                metric="cosine",
                train_batch_size=200,
                test_batch_size=5,
                top_k=10,
            )

            # Convert CPU results to comparison format
            cpu_results = []
            for _, row in cpu_results_df.iterrows():
                cpu_results.append(
                    {
                        "test_id": row["id"],
                        "neighbor_ids": row["neighbors_id"],
                        "distances": row["neighbors_distance"],
                    }
                )

            # Convert GPU results to comparison format
            gpu_results = []
            for _, row in gpu_results_df.iterrows():
                gpu_results.append(
                    {
                        "test_id": row["id"],
                        "neighbor_ids": row["neighbors_id"],
                        "distances": row["neighbors_distance"],
                    }
                )

            # Sort by test_id
            cpu_results = sorted(cpu_results, key=lambda x: x["test_id"])
            gpu_results = sorted(gpu_results, key=lambda x: x["test_id"])

            # Compare CPU and GPU results
            assert len(cpu_results) == len(gpu_results), "CPU and GPU result count mismatch"

            for i, (cpu_result, gpu_result) in enumerate(
                zip(cpu_results, gpu_results, strict=False)
            ):
                assert (
                    cpu_result["test_id"] == gpu_result["test_id"]
                ), f"test_id mismatch: {cpu_result['test_id']} != {gpu_result['test_id']}"

                # Compare neighbor IDs
                cpu_ids = cpu_result["neighbor_ids"]
                gpu_ids = gpu_result["neighbor_ids"]

                if isinstance(cpu_ids, np.ndarray):
                    cpu_ids = cpu_ids.tolist()
                if isinstance(gpu_ids, np.ndarray):
                    gpu_ids = gpu_ids.tolist()

                assert (
                    cpu_ids == gpu_ids
                ), f"Query {i}: CPU and GPU neighbor ID mismatch\n  CPU: {cpu_ids}\n  GPU: {gpu_ids}"

                # Compare distances (allow larger tolerance due to potential numerical precision differences between GPU and CPU)
                cpu_dists = cpu_result["distances"]
                gpu_dists = gpu_result["distances"]

                if isinstance(cpu_dists, np.ndarray):
                    cpu_dists = cpu_dists.tolist()
                if isinstance(gpu_dists, np.ndarray):
                    gpu_dists = gpu_dists.tolist()

                max_dist_diff = max(abs(c - g) for c, g in zip(cpu_dists, gpu_dists, strict=False))
                assert (
                    max_dist_diff <= 1e-5
                ), f"Query {i}: CPU and GPU distance difference too large {max_dist_diff:.8f}\n  CPU: {cpu_dists}\n  GPU: {gpu_dists}"

    @pytest.mark.gpu
    @pytest.mark.slow
    def test_gpu_ground_truth_correctness_large(self):
        """Test GPU ground truth computation correctness for large-scale data - requires GPU and slow test markers"""
        pytest.importorskip("cupy", reason="cupy not available")
        pytest.importorskip("cuvs", reason="cuvs not available")

        with tempfile.TemporaryDirectory(prefix="gt_test_gpu_large_") as temp_dir:
            # Create large-scale test data
            dataset, train_data, test_data = self.create_test_dataset(
                temp_dir,
                train_count=10000,  # 10,000 training vectors
                test_count=100,  # 100 test vectors
                dim=256,  # Higher dimensions to fully utilize GPU
            )

            # Only test cosine to save time
            reference_results = self.compute_reference_gt(
                train_data, test_data, top_k=10, metric="cosine"
            )

            # Test GPU batched computation - using original required batch sizes
            batched_results_df = self.get_batched_results_gpu(
                dataset,
                metric="cosine",
                train_batch_size=1000,  # GPU training batch size 1000
                test_batch_size=10,  # GPU test batch size 10
                top_k=10,
            )

            # Compare results
            self.compare_results(reference_results, batched_results_df)

    @pytest.mark.gpu
    def test_gpu_memory_management(self):
        """Test GPU memory management and adaptive batching"""
        pytest.importorskip("cupy", reason="cupy not available")
        pytest.importorskip("cuvs", reason="cuvs not available")

        with tempfile.TemporaryDirectory(prefix="gt_test_gpu_memory_") as temp_dir:
            # Create data that may cause memory pressure
            dataset, train_data, test_data = self.create_test_dataset(
                temp_dir,
                train_count=2000,  # 2000 training vectors
                test_count=40,  # 40 test vectors
                dim=512,  # High dimensions to increase memory pressure
            )

            # Compute reference results
            reference_results = self.compute_reference_gt(
                train_data, test_data, top_k=15, metric="cosine"
            )

            # Test GPU batched computation, using large batches that may trigger memory management
            batched_results_df = self.get_batched_results_gpu(
                dataset,
                metric="cosine",
                train_batch_size=800,  # Large batch may trigger GPU memory insufficiency
                test_batch_size=20,  # Large test batch
                top_k=15,
            )

            # Compare results - results should still be correct even with memory pressure
            self.compare_results(reference_results, batched_results_df)
