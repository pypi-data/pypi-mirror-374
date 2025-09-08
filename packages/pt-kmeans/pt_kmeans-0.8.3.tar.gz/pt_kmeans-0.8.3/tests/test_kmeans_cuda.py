# pylint: disable=protected-access

import logging
import unittest
from typing import Literal

import torch

import pt_kmeans
import pt_kmeans.pt_kmeans

logging.disable(logging.CRITICAL)


class TestKMeansCUDA(unittest.TestCase):
    @unittest.skipUnless(torch.cuda.is_available(), "CUDA not available")
    def setUp(self) -> None:
        torch.manual_seed(0)
        self.device = torch.device("cuda")

        # Create test data on GPU
        cluster1 = torch.randn(30, 2, device=self.device) + torch.tensor([0.0, 0.0], device=self.device)
        cluster2 = torch.randn(30, 2, device=self.device) + torch.tensor([10.0, 10.0], device=self.device)
        cluster3 = torch.randn(30, 2, device=self.device) + torch.tensor([-10.0, 10.0], device=self.device)
        self.x_cuda = torch.concat([cluster1, cluster2, cluster3], dim=0)
        self.n_clusters = 3

    @unittest.skipUnless(torch.cuda.is_available(), "CUDA not available")
    def test_kmeans_cuda_device_consistency(self) -> None:
        (centers, labels) = pt_kmeans.kmeans(self.x_cuda, self.n_clusters, device=self.device)

        self.assertEqual(centers.device, torch.device("cpu"))
        self.assertEqual(labels.device, torch.device("cpu"))
        self.assertEqual(centers.shape, (self.n_clusters, self.x_cuda.shape[1]))
        self.assertEqual(labels.shape, (self.x_cuda.shape[0],))

        # Data on CPU, compute on CUDA
        (centers, labels) = pt_kmeans.kmeans(self.x_cuda.to(torch.device("cpu")), self.n_clusters, device=self.device)

        self.assertEqual(centers.device, torch.device("cpu"))
        self.assertEqual(labels.device, torch.device("cpu"))

    @unittest.skipUnless(torch.cuda.is_available(), "CUDA not available")
    def test_kmeans_chunked_cuda_device_consistency(self) -> None:
        (centers, labels) = pt_kmeans.kmeans(self.x_cuda, self.n_clusters, chunk_size=10, device=self.device)

        self.assertEqual(centers.device, torch.device("cpu"))
        self.assertEqual(labels.device, torch.device("cpu"))
        self.assertEqual(centers.shape, (self.n_clusters, self.x_cuda.shape[1]))
        self.assertEqual(labels.shape, (self.x_cuda.shape[0],))

        # Data on CPU, compute on CUDA
        (centers, labels) = pt_kmeans.kmeans(self.x_cuda.to(torch.device("cpu")), self.n_clusters, device=self.device)

        self.assertEqual(centers.device, torch.device("cpu"))
        self.assertEqual(labels.device, torch.device("cpu"))

    @unittest.skipUnless(torch.cuda.is_available(), "CUDA not available")
    def test_kmeans_random_cuda_device_consistency(self) -> None:
        (centers, labels) = pt_kmeans.kmeans(self.x_cuda, self.n_clusters, init_method="random", device=self.device)

        self.assertEqual(centers.device, torch.device("cpu"))
        self.assertEqual(labels.device, torch.device("cpu"))
        self.assertEqual(centers.shape, (self.n_clusters, self.x_cuda.shape[1]))
        self.assertEqual(labels.shape, (self.x_cuda.shape[0],))

        # Data on CPU, compute on CUDA
        (centers, labels) = pt_kmeans.kmeans(
            self.x_cuda.to(torch.device("cpu")), self.n_clusters, init_method="random", device=self.device
        )

        self.assertEqual(centers.device, torch.device("cpu"))
        self.assertEqual(labels.device, torch.device("cpu"))

    @unittest.skipUnless(torch.cuda.is_available(), "CUDA not available")
    def test_hierarchical_kmeans_cuda_device_consistency(self) -> None:
        x_large = torch.randn(200, 5, device=self.device)
        n_clusters = [50, 10, 3]
        results = pt_kmeans.hierarchical_kmeans(x_large, n_clusters, max_iters=20, device=self.device)

        for result in results:
            self.assertEqual(result["centers"].device, torch.device("cpu"))
            self.assertEqual(result["assignment"].device, torch.device("cpu"))

        # Data on CPU, compute on CUDA
        x_large = torch.randn(200, 5)
        n_clusters = [50, 10, 3]
        results = pt_kmeans.hierarchical_kmeans(x_large, n_clusters, max_iters=20, device=self.device)

        for result in results:
            self.assertEqual(result["centers"].device, torch.device("cpu"))
            self.assertEqual(result["assignment"].device, torch.device("cpu"))

        # Data on CPU, compute on CUDA with resampling
        x_large = torch.randn(200, 5)
        n_clusters = [50, 10, 3]
        results = pt_kmeans.hierarchical_kmeans(
            x_large, n_clusters, max_iters=20, device=self.device, method="resampled", n_samples=[10, 5, 1]
        )

        for result in results:
            self.assertEqual(result["centers"].device, torch.device("cpu"))
            self.assertEqual(result["assignment"].device, torch.device("cpu"))

    @unittest.skipUnless(torch.cuda.is_available(), "CUDA not available")
    def test_split_cluster_cuda_device_consistency(self) -> None:
        x_cuda = torch.tensor(
            [
                [1.0, 1.0],
                [1.1, 1.1],
                [1.2, 1.2],
                [1.3, 1.3],
                [5.0, 5.0],
                [5.1, 5.1],
                [5.2, 5.2],
                [5.3, 5.3],
                [10.0, 10.0],
                [10.1, 10.1],
                [10.2, 10.2],
                [10.3, 10.3],
            ],
            device=self.device,
        )
        labels = torch.tensor([0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2])

        (new_centers, new_labels) = pt_kmeans.split_cluster(
            x_cuda, labels, cluster_id=1, n_clusters=2, device=self.device
        )
        self.assertEqual(new_centers.device, torch.device("cpu"))
        self.assertEqual(new_labels.device, torch.device("cpu"))

        (new_centers, new_labels) = pt_kmeans.split_cluster(
            x_cuda.to(torch.device("cpu")), labels, cluster_id=1, n_clusters=2, device=self.device
        )
        self.assertEqual(new_centers.device, torch.device("cpu"))
        self.assertEqual(new_labels.device, torch.device("cpu"))

    @unittest.skipUnless(torch.cuda.is_available(), "CUDA not available")
    def test_predict_cuda_device_consistency(self) -> None:
        (centers, _) = pt_kmeans.kmeans(self.x_cuda, self.n_clusters, device=self.device)

        new_data_cuda = torch.randn(20, 2, device=self.device)
        predicted_labels = pt_kmeans.predict(new_data_cuda, centers.to(self.device), device=self.device)

        self.assertEqual(predicted_labels.device, torch.device("cpu"))
        self.assertEqual(predicted_labels.shape, (new_data_cuda.shape[0],))

        # Data on CPU, centers on CUDA, computation on CUDA
        new_data_cpu = torch.randn(20, 2)
        predicted_labels = pt_kmeans.predict(new_data_cpu, centers.to(self.device), device=self.device)
        self.assertEqual(predicted_labels.device, torch.device("cpu"))
        self.assertEqual(predicted_labels.shape, (new_data_cuda.shape[0],))

        # Data on CPU, centers on CUDA, computation on CUDA (cosine)
        new_data_cpu = torch.randn(20, 2)
        predicted_labels = pt_kmeans.predict(
            new_data_cpu, centers.to(self.device), distance_metric="cosine", device=self.device
        )
        self.assertEqual(predicted_labels.device, torch.device("cpu"))
        self.assertEqual(predicted_labels.shape, (new_data_cuda.shape[0],))

        # Data on CPU, centers on CPU, computation on CUDA
        new_data_cpu = torch.randn(20, 2)
        predicted_labels = pt_kmeans.predict(new_data_cpu, centers, device=self.device)
        self.assertEqual(predicted_labels.device, torch.device("cpu"))
        self.assertEqual(predicted_labels.shape, (new_data_cuda.shape[0],))

    @unittest.skipUnless(torch.cuda.is_available(), "CUDA not available")
    def test_distance_computation_cuda_chunked(self) -> None:
        large_x = torch.randn(500, 10, device=self.device)
        large_centers = torch.randn(5, 10, device=self.device)

        distance_metrics: list[Literal["l2", "cosine"]] = ["l2", "cosine"]
        for distance_metric in distance_metrics:
            distances_full = pt_kmeans.compute_distance(
                large_x, large_centers, distance_metric=distance_metric, chunk_size=None
            )
            distances_chunked = pt_kmeans.compute_distance(
                large_x, large_centers, distance_metric=distance_metric, chunk_size=50
            )

            # Results should be identical
            torch.testing.assert_close(distances_full, distances_chunked)

    @unittest.skipUnless(torch.cuda.is_available(), "CUDA not available")
    def test_update_centers_empty_cluster_x_cpu_centers_cuda(self) -> None:
        x_cpu = torch.tensor(
            [[1.0, 1.0], [2.0, 2.0], [10.0, 10.0], [11.0, 11.0]], dtype=torch.float32, device=torch.device("cpu")
        )

        labels_with_empty_cpu = torch.tensor([0, 0, 0, 0], dtype=torch.long, device=torch.device("cpu"))
        target_device = torch.device("cuda")
        empty_cluster_id = 1

        generator = torch.Generator(device=target_device).manual_seed(0)

        new_centers = pt_kmeans.pt_kmeans._update_centers(
            x_cpu, labels_with_empty_cpu, self.n_clusters, target_device, generator
        )

        # Verify shape and device of new_centers
        self.assertEqual(new_centers.shape, (self.n_clusters, x_cpu.shape[1]))
        self.assertEqual(new_centers.device.type, target_device.type)

        # Verify non-empty cluster (cluster 0) is correctly updated on CUDA
        expected_center_0_cpu = torch.mean(x_cpu, dim=0)
        torch.testing.assert_close(new_centers[0].cpu(), expected_center_0_cpu)

        # Verify empty cluster (cluster 1) is reinitialized with a point from x
        # The point should be on CUDA after reinitialization
        reinitialized_center = new_centers[empty_cluster_id]
        is_reinitialized_from_x = torch.any(torch.all(reinitialized_center == x_cpu.to(target_device), dim=1))
        self.assertTrue(
            is_reinitialized_from_x, "Empty cluster center was not reinitialized from input data (x_cpu, centers_cuda)."
        )
        self.assertFalse(
            torch.all(reinitialized_center == 0.0), "Empty cluster center is still zero (x_cpu, centers_cuda)."
        )
        self.assertEqual(reinitialized_center.device.type, target_device.type)
