import logging
import shutil
import tempfile
import unittest
from pathlib import Path

import torch

import pt_kmeans

logging.disable(logging.CRITICAL)


class TestKMeansCaching(unittest.TestCase):
    def setUp(self) -> None:
        torch.manual_seed(0)
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = Path(self.temp_dir).joinpath("kmeans_cache")

        # Create test data
        cluster1 = torch.randn(30, 2) + torch.tensor([0.0, 0.0])
        cluster2 = torch.randn(30, 2) + torch.tensor([5.0, 5.0])
        self.x = torch.concat([cluster1, cluster2], dim=0)
        self.n_clusters = 2

    def tearDown(self) -> None:
        if Path(self.temp_dir).exists() is True:
            shutil.rmtree(self.temp_dir)

    def test_kmeans_cache_basic(self) -> None:
        (centers1, labels1) = pt_kmeans.kmeans(self.x, self.n_clusters, random_seed=0, cache_dir=self.cache_dir)

        # Verify cache files were created
        self.assertTrue(self.cache_dir.joinpath("initial_centers.pt").exists())
        self.assertTrue(self.cache_dir.joinpath("final_results.pt").exists())

        # Second run - should load from cache
        (centers2, labels2) = pt_kmeans.kmeans(
            self.x,
            self.n_clusters,
            random_seed=456,  # Different seed should be ignored when loading from cache
            cache_dir=self.cache_dir,
        )

        # Results should be identical
        torch.testing.assert_close(centers1, centers2)
        torch.testing.assert_close(labels1, labels2)

    def test_kmeans_cache_initial_centers_only(self) -> None:
        # Create initial centers cache manually
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        initial_centers = pt_kmeans.initialize_centers(self.x, self.n_clusters, method="kmeans++")
        torch.save(initial_centers.cpu(), self.cache_dir.joinpath("initial_centers.pt"))

        # Run kmeans - should use cached initial centers
        (centers, labels) = pt_kmeans.kmeans(self.x, self.n_clusters, cache_dir=self.cache_dir)

        # Verify it completed and created final results
        self.assertEqual(centers.shape, (self.n_clusters, self.x.shape[1]))
        self.assertEqual(labels.shape, (self.x.shape[0],))
        self.assertTrue(self.cache_dir.joinpath("final_results.pt").exists())

    def test_hierarchical_kmeans_cache_structure(self) -> None:
        n_clusters = [10, 5, 2]
        x_large = torch.randn(50, 3)

        results1 = pt_kmeans.hierarchical_kmeans(x_large, n_clusters=n_clusters, max_iters=3, cache_dir=self.cache_dir)

        # Check cache structure
        for i in range(len(n_clusters)):
            level_dir = self.cache_dir / f"level_{i}"
            self.assertTrue(level_dir.exists())
            self.assertTrue(level_dir.joinpath("initial_centers.pt").exists())
            self.assertTrue(level_dir.joinpath("final_results.pt").exists())

        # Run again - should load from cache
        results2 = pt_kmeans.hierarchical_kmeans(x_large, n_clusters=n_clusters, max_iters=3, cache_dir=self.cache_dir)

        # Results should be identical
        for r1, r2 in zip(results1, results2):
            torch.testing.assert_close(r1["centers"], r2["centers"])
            torch.testing.assert_close(r1["assignment"], r2["assignment"])

    def test_hierarchical_kmeans_resampled_cache(self) -> None:
        n_clusters = [10, 5]
        n_samples = [3, 2]
        n_resamples = 2
        x_large = torch.randn(50, 3)

        results1 = pt_kmeans.hierarchical_kmeans(
            x_large,
            n_clusters=n_clusters,
            method="resampled",
            n_samples=n_samples,
            n_resamples=n_resamples,
            max_iters=3,
            cache_dir=self.cache_dir,
        )

        # Check that resample directories were created
        for level_idx in range(len(n_clusters)):
            if n_samples[level_idx] > 0:
                level_dir = self.cache_dir.joinpath(f"level_{level_idx}")
                for resample_idx in range(n_resamples):
                    resample_dir = level_dir.joinpath(f"resample_{resample_idx}")
                    self.assertTrue(resample_dir.exists())
                    self.assertTrue(resample_dir.joinpath("final_results.pt").exists())

        # Run again - should load from cache
        results2 = pt_kmeans.hierarchical_kmeans(
            x_large,
            n_clusters=n_clusters,
            method="resampled",
            n_samples=n_samples,
            n_resamples=n_resamples,
            max_iters=3,
            cache_dir=self.cache_dir,
        )

        # Results should be identical
        for r1, r2 in zip(results1, results2):
            torch.testing.assert_close(r1["centers"], r2["centers"])
            torch.testing.assert_close(r1["assignment"], r2["assignment"])
