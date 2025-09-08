# Copyright (c) 2025, Ofer Hasson. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
from pathlib import Path
from typing import Any
from typing import Literal
from typing import Optional

import torch
import torch.nn.functional as F
from tqdm import tqdm

logger = logging.getLogger(__name__)


def _safe_save(data: object, path: Path) -> None:
    temp_path = path.with_suffix(".tmp")
    torch.save(data, temp_path)
    temp_path.rename(path)


def _save_config(config: dict[str, Any], cache_path: Path) -> None:
    config_file_path = cache_path.joinpath("config.json")
    with open(config_file_path, "w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)

    logger.debug(f"Saved configuration to {config_file_path}")


def compute_distance(
    x: torch.Tensor,
    centers: torch.Tensor,
    distance_metric: Literal["l2", "cosine"] = "l2",
    x_squared_norm: Optional[torch.Tensor] = None,
    x_pre_normalized: bool = False,
    chunk_size: Optional[int] = None,
) -> torch.Tensor:
    """
    Computes distances between data points and cluster centers.

    Parameters
    ----------
    x
        Input data of shape (n_samples, n_features). Can be on any device.
    centers
        Cluster centers of shape (n_clusters, n_features). Expected to be on the target device.
    distance_metric
        Distance metric to use.
    x_squared_norm
        Pre-computed squared L2 norm for x. If provided, it must correspond to the full x.
        If chunking is active, this will be chunked internally and moved to the target device.
        If None, squared norms are computed on-the-fly for relevant chunks on the target device.
    x_pre_normalized
        If True, assumes 'x' has already been L2-normalized to unit vectors.
    chunk_size
        Number of data points to process in a single batch during distance computations.

    Returns
    -------
    Distances of shape (n_samples, n_clusters), on the same device as centers.
    """

    n_samples = x.size(0)
    n_clusters = centers.size(0)
    device = centers.device

    if chunk_size is None or chunk_size >= n_samples:
        x = x.to(device)
        if distance_metric == "l2":
            if x_squared_norm is None:
                x_squared_norm = torch.sum(x**2, dim=1)
            else:
                x_squared_norm = x_squared_norm.to(device)

            centers_squared_norm = torch.sum(centers**2, dim=1)
            distances = x_squared_norm[:, None] - 2 * torch.mm(x, centers.t()) + centers_squared_norm[None, :]
            # distances = torch.clamp(distances, min=0.0)
            # distances = torch.cdist(x, centers, p=2).square()
        elif distance_metric == "cosine":
            if x_pre_normalized is True:
                x_norm = x
            else:
                x_norm = F.normalize(x, p=2, dim=1)

            centers_norm = F.normalize(centers, p=2, dim=1)
            similarities = torch.mm(x_norm, centers_norm.t())
            distances = 1 - similarities
        else:
            raise ValueError(f"Unknown distance_metric: {distance_metric}")

        return distances

    if distance_metric == "l2":
        centers_squared_norm = torch.sum(centers**2, dim=1)
    elif distance_metric == "cosine":
        centers_norm = F.normalize(centers, p=2, dim=1)

    distances = torch.empty((n_samples, n_clusters), dtype=x.dtype, device=device)
    n_iters = (n_samples + chunk_size - 1) // chunk_size
    for chunk_idx in range(n_iters):
        begin_idx = chunk_idx * chunk_size
        end_idx = min(n_samples, (chunk_idx + 1) * chunk_size)
        x_chunk = x[begin_idx:end_idx].to(device)
        x_squared_norm_chunk = x_squared_norm[begin_idx:end_idx].to(device) if x_squared_norm is not None else None
        if distance_metric == "l2":
            if x_squared_norm_chunk is None:
                x_squared_norm_chunk = torch.sum(x_chunk**2, dim=1)

            distances_chunk = (
                x_squared_norm_chunk[:, None] - 2 * torch.mm(x_chunk, centers.t()) + centers_squared_norm[None, :]
            )
            # distances_chunk = torch.clamp(distances_chunk, min=0.0)
        elif distance_metric == "cosine":
            if x_pre_normalized is True:
                x_norm_chunk = x_chunk
            else:
                x_norm_chunk = F.normalize(x_chunk, p=2, dim=1)

            similarities_chunk = torch.mm(x_norm_chunk, centers_norm.t())
            distances_chunk = 1 - similarities_chunk
        else:
            raise ValueError(f"Unknown distance_metric: {distance_metric}")

        distances[begin_idx:end_idx] = distances_chunk

    return distances


def _kmeans_plusplus_init(
    x: torch.Tensor,
    n_clusters: int,
    distance_metric: Literal["l2", "cosine"] = "l2",
    n_local_trials: Optional[int] = None,
    x_pre_normalized: bool = False,
    show_progress: bool = False,
    generator: Optional[torch.Generator] = None,
    chunk_size: Optional[int] = None,
    device: Optional[torch.device] = None,
) -> torch.Tensor:
    """
    Initialize cluster centers using K-Means++ algorithm

    K-Means++ selects initial cluster centers that are far apart from each other,
    leading to better convergence compared to random initialization.

    Parameters
    ----------
    x
        Input data of shape (n_samples, n_features).
    n_clusters
        Number of clusters to initialize.
    distance_metric
        Distance metric to use.
    n_local_trials
        Number of local trials to sample per iteration.
        If None, defaults to 2 + log(n_clusters).
        Use n_local_trials=1 to turn off.
    x_pre_normalized
        If True, assumes 'x' has already been L2-normalized to unit vectors.
    show_progress
        If True, display a progress bar during processing.
    generator
        Random number generator for reproducibility.
    chunk_size
        Number of data points to process in a single batch during distance computations.
    device
        The device (e.g., 'cuda', 'cpu') to perform computations on. If None, uses x.device.

    Returns
    -------
    Initial cluster centers of shape (n_clusters, n_features).

    References
    ----------
    .. [1] D. Arthur and S. Vassilvitskii, "k-means++: the advantages of careful seeding",
       Proceedings of the Eighteenth Annual ACM-SIAM Symposium on Discrete Algorithms, 2007.

    Examples
    --------
    >>> X = torch.randn(100, 2)  # 100 samples, 2 features
    >>> centers = _kmeans_plusplus_init(X, n_clusters=5)
    >>> centers.shape
    torch.Size([5, 2])
    """

    if device is None:
        device = x.device

    (n_samples, n_features) = x.shape
    centers = torch.empty((n_clusters, n_features), dtype=x.dtype, device=device)

    if n_local_trials is None:
        n_local_trials = 2 + int(torch.log(torch.tensor(n_clusters, dtype=torch.float32)).item())

    # Choose first center randomly
    first_idx = torch.randint(0, n_samples, (1,), device=device, generator=generator).to(x.device)
    centers[0] = x[first_idx].to(device)

    # Initialize min_distances with distances to the first center
    min_distances = compute_distance(
        x, centers[0:1], distance_metric, x_pre_normalized=x_pre_normalized, chunk_size=chunk_size
    ).squeeze(1)

    # Choose remaining centers
    for i in tqdm(
        range(1, n_clusters),
        total=n_clusters,
        initial=1,
        desc="K-Means++ initialization",
        leave=False,
        disable=not show_progress,
    ):
        probabilities = min_distances / (min_distances.sum() + 1e-12)
        cumulative_probs = torch.cumsum(probabilities, dim=0)

        # Sample using inverse transform sampling
        r = torch.rand(n_local_trials, device=device, generator=generator)
        candidates_idx = torch.searchsorted(cumulative_probs, r, right=True)
        candidates_idx = torch.clamp(candidates_idx, 0, n_samples - 1)
        distances = compute_distance(
            x,
            x[candidates_idx.to(x.device)].to(device),
            distance_metric,
            x_pre_normalized=x_pre_normalized,
            chunk_size=chunk_size,
        )
        candidate_potentials = torch.min(min_distances.unsqueeze(1), distances).sum(dim=0)
        best_idx = candidates_idx[torch.argmin(candidate_potentials)]
        centers[i] = x[best_idx].to(device)

        # Update min_distances only with the newly added center, if more centers are yet to be picked
        if i < n_clusters - 1:
            new_center_distances = distances[:, torch.argmin(candidate_potentials)]
            min_distances = torch.minimum(min_distances, new_center_distances)

    return centers


def initialize_centers(
    x: torch.Tensor,
    n_clusters: int,
    method: Literal["random", "kmeans++"] = "kmeans++",
    distance_metric: Literal["l2", "cosine"] = "l2",
    n_local_trials: Optional[int] = None,
    x_pre_normalized: bool = False,
    show_progress: bool = False,
    generator: Optional[torch.Generator] = None,
    chunk_size: Optional[int] = None,
    device: Optional[torch.device] = None,
    cache_path: Optional[Path] = None,
) -> torch.Tensor:
    """
    Initialize centers for K-Means clustering

    Parameters
    ----------
    x
        Input data of shape (n_samples, n_features).
    n_clusters
        Number of clusters to initialize.
    method
        Initialization method.
    distance_metric
        Distance metric to use.
    n_local_trials
        Number of local trials to sample per iteration for K-Means++ initialization.
        If None, defaults to 2 + log(n_clusters). Use n_local_trials=1 to turn off.
    x_pre_normalized
        If True, assumes 'x' has already been L2-normalized to unit vectors.
    show_progress
        If True, display a progress bar during processing.
    generator
        Random number generator for reproducibility.
    chunk_size
        Number of data points to process in a single batch during distance computations.
    device
        The device (e.g., 'cuda', 'cpu') to perform computations on. If None, uses x.device.
    cache_path
        Internal parameter for caching initial centers.

    Returns
    -------
    Initial cluster centers of shape (n_clusters, n_features).
    """

    if device is None:
        device = x.device

    # Try to load initial centers from cache first
    if cache_path is not None and cache_path.exists() is True:
        logger.info(f"Loading initial centers from cache: {cache_path}")
        return torch.load(cache_path, map_location=device)

    if method == "random":
        indices = torch.multinomial(
            torch.ones(x.size(0), dtype=torch.float32, device=device),
            n_clusters,
            replacement=False,
            generator=generator,
        ).to(x.device)
        centers = x[indices].to(device=device, dtype=x.dtype)
    elif method == "kmeans++":
        centers = _kmeans_plusplus_init(
            x,
            n_clusters,
            distance_metric,
            n_local_trials,
            x_pre_normalized,
            show_progress,
            generator,
            chunk_size,
            device,
        )
    else:
        raise ValueError(f"Unknown initialization method: {method}")

    if cache_path is not None:
        _safe_save(centers.cpu(), cache_path)
        logger.info(f"Saved initial centers to cache: {cache_path}")

    return centers


def _assign_clusters(
    x: torch.Tensor,
    centers: torch.Tensor,
    distance_metric: Literal["l2", "cosine"] = "l2",
    x_pre_normalized: bool = False,
    chunk_size: Optional[int] = None,
) -> torch.Tensor:
    """
    Assign each data point to the nearest cluster center

    Parameters
    ----------
    x
        Input data of shape (n_samples, n_features).
    centers
        Cluster centers of shape (n_clusters, n_features), expected to be on the target device.
    distance_metric
        Distance metric to use:
        - "l2": L2 distance
        - "cosine": Cosine distance (1 - cosine similarity)
    x_pre_normalized
        If True, assumes 'x' has already been L2-normalized to unit vectors.
    chunk_size
        Number of data points to process in a single batch during distance computations.

    Returns
    -------
    Cluster assignments of shape (n_samples,) with values in [0, n_clusters), on CPU.

    Examples
    --------
    >>> X = torch.randn(100, 2)
    >>> centers = torch.randn(5, 2)
    >>> cluster_ids = assign_clusters(X, centers, distance_metric="l2")
    >>> cluster_ids.shape
    torch.Size([100])
    """

    n_samples = x.size(0)
    if chunk_size is None or chunk_size >= n_samples:
        all_distances = compute_distance(x, centers, distance_metric, x_pre_normalized=x_pre_normalized)
        return torch.argmin(all_distances, dim=1).cpu()

    cluster_ids = torch.empty(n_samples, dtype=torch.long)
    n_iters = (n_samples + chunk_size - 1) // chunk_size
    for chunk_idx in range(n_iters):
        begin_idx = chunk_idx * chunk_size
        end_idx = min(n_samples, (chunk_idx + 1) * chunk_size)
        x_chunk = x[begin_idx:end_idx]

        distances_chunk = compute_distance(x_chunk, centers, distance_metric, x_pre_normalized=x_pre_normalized)
        cluster_ids[begin_idx:end_idx] = torch.argmin(distances_chunk, dim=1).cpu()

    return cluster_ids


def _update_centers(
    x: torch.Tensor,
    labels: torch.Tensor,
    n_clusters: int,
    device: torch.device,
    generator: Optional[torch.Generator] = None,
    chunk_size: Optional[int] = None,
) -> torch.Tensor:
    """
    Update centers as the mean of assigned points

    Parameters
    ----------
    x
        Input data of shape (n_samples, n_features).
    labels
        Cluster assignments of shape (n_samples,).
    n_clusters
        Number of clusters.
    device
        The device (e.g., 'cuda', 'cpu') to perform computations on.
    generator
        Random number generator for reproducibility.
    chunk_size
        Number of data points to process in a single batch during scatter computations.
        If None, all data is processed in one go.

    Returns
    -------
    Updated centers of shape (n_clusters, n_features).

    Notes
    -----
    - Empty clusters are detected (i.e., no samples assigned) and reinitialized to random points from the dataset.
    """

    (n_samples, n_features) = x.size()
    sums = torch.zeros(n_clusters, n_features, dtype=x.dtype, device=device)
    total_counts = torch.zeros(n_clusters, dtype=torch.long, device=device)
    if chunk_size is None or chunk_size >= n_samples:
        chunk_size = n_samples
        n_iters = 1
    else:
        n_iters = (n_samples + chunk_size - 1) // chunk_size

    for chunk_idx in range(n_iters):
        begin_idx = chunk_idx * chunk_size
        end_idx = min(n_samples, (chunk_idx + 1) * chunk_size)

        x_chunk = x[begin_idx:end_idx].to(device)
        labels_chunk = labels[begin_idx:end_idx].to(device)

        sums.scatter_add_(0, labels_chunk[:, None].expand(-1, n_features), x_chunk)

        ones_chunk = torch.ones_like(labels_chunk, dtype=torch.long, device=device)
        total_counts.scatter_add_(0, labels_chunk, ones_chunk)

    empty_clusters_mask = total_counts == 0
    safe_counts = total_counts.clamp(min=1).unsqueeze(1).to(dtype=x.dtype, device=device)
    new_centers = sums / safe_counts

    # Handle empty clusters
    if empty_clusters_mask.any():
        num_empty_clusters = empty_clusters_mask.sum().item()
        logger.warning(f"{num_empty_clusters} empty clusters detected, reinitializing randomly")

        rand_ids_on_x_device = torch.randint(
            0, x.size(0), (num_empty_clusters,), device=device, generator=generator
        ).to(x.device)
        random_points = x[rand_ids_on_x_device].to(device)
        new_centers[empty_clusters_mask] = random_points

    return new_centers


def kmeans(
    x: torch.Tensor,
    n_clusters: int,
    max_iters: int = 100,
    tol: float = 1e-4,
    distance_metric: Literal["l2", "cosine"] = "l2",
    init_method: Literal["random", "kmeans++"] = "kmeans++",
    n_local_trials: Optional[int] = None,
    chunk_size: Optional[int] = None,
    show_progress: bool = False,
    random_seed: Optional[int] = None,
    device: Optional[torch.device] = None,
    *,
    initial_centers: Optional[torch.Tensor] = None,
    x_pre_normalized: bool = False,
    cache_dir: Optional[str | Path] = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Perform K-Means clustering

    Parameters
    ----------
    x
        Input data of shape (n_samples, n_features).
    n_clusters
        Number of clusters.
    max_iters
        Maximum number of iterations.
    tol
        Tolerance for convergence (normalized change in centers).
    distance_metric
        Distance metric to use.
    init_method
        Centers initialization method.
    n_local_trials
        Number of local trials to sample per iteration for K-Means++ initialization.
        If None, defaults to 2 + log(n_clusters). Use n_local_trials=1 to turn off.
    chunk_size
        Number of data points to process in a single batch during distance computations.
    show_progress
        If True, display a progress bar during processing.
    random_seed
        Random seed for reproducibility. If None, uses default random state.
    device
        The device (e.g., 'cuda', 'cpu') to perform computations on. If None, uses x.device.
    initial_centers
        Optional tensor of initial cluster centers of shape (n_clusters, n_features).
        If provided, the 'init_method' is ignored and clustering starts from these centers.
    x_pre_normalized
        If True, assumes 'x' has already been L2-normalized to unit vectors.
    cache_dir
        Optional path to a directory for caching K-Means results.
        If provided, caches initial centers (after initialization) and final results
        (after convergence). On subsequent runs with the same cache_dir, will load
        from cache if available, skipping computation.

    Returns
    -------
    A tuple containing:
    - Final centers of shape (n_clusters, n_features), on CPU.
    - Final cluster assignments of shape (n_samples,), on CPU.
    """

    # Input validation
    if n_clusters <= 0:
        raise ValueError("n_clusters must be positive")
    if n_clusters > x.size(0):
        raise ValueError("n_clusters cannot exceed number of samples")
    if x.size(0) == 0:
        raise ValueError("Input data cannot be empty")
    if x.dim() != 2:
        raise ValueError("Input data must be 2-dimensional")

    # Takes too much memory to run those validations
    # if torch.isnan(x).any():
    #     raise ValueError("Input data contains NaN values")
    # if torch.isinf(x).any():
    #     raise ValueError("Input data contains infinite values")

    if device is None:
        device = x.device

    generator = None
    if random_seed is not None:
        generator = torch.Generator(device=device)
        generator.manual_seed(random_seed)

    logger.info(f"Starting K-Means: n_clusters={n_clusters}, n_samples={x.size(0)}, n_features={x.size(1)}")
    cache_initial_centers_path: Optional[Path] = None
    cache_final_results_path: Optional[Path] = None
    if cache_dir is not None:
        cache_path = Path(cache_dir)
        if cache_path.exists() is True and cache_path.is_dir() is False:
            raise ValueError("cache_dir must be a directory")

        cache_path.mkdir(parents=True, exist_ok=True)
        cache_initial_centers_path = cache_path.joinpath("initial_centers.pt")
        cache_final_results_path = cache_path.joinpath("final_results.pt")

        _save_config(
            {
                "n_clusters": n_clusters,
                "max_iters": max_iters,
                "tol": tol,
                "distance_metric": distance_metric,
                "init_method": init_method,
                "n_local_trials": n_local_trials,
                "random_seed": random_seed,
                "initial_centers_provided": initial_centers is not None,
                "x_pre_normalized": x_pre_normalized,
            },
            cache_path,
        )

        if cache_final_results_path.exists():
            logger.info(f"Loading cached K-Means results from: {cache_final_results_path}")
            cached_data = torch.load(cache_final_results_path, map_location="cpu")
            return (cached_data["centers"], cached_data["labels"])

    if initial_centers is not None:
        if initial_centers.shape != (n_clusters, x.shape[1]):
            raise ValueError(
                f"initial_centers must have shape ({n_clusters}, {x.shape[1]}), " f"but got {initial_centers.shape}"
            )

        # Ensure initial_centers are on the correct device and dtype
        centers = initial_centers.to(device=device, dtype=x.dtype)
    else:
        centers = initialize_centers(
            x,
            n_clusters,
            init_method,
            distance_metric,
            n_local_trials,
            x_pre_normalized,
            show_progress,
            generator,
            chunk_size,
            device,
            cache_initial_centers_path,
        )

    prev_centers = centers.clone()
    labels = _assign_clusters(x, centers, distance_metric, x_pre_normalized, chunk_size)
    for it in tqdm(range(max_iters), desc="K-Means iterations", leave=False, disable=not show_progress):
        centers = _update_centers(x, labels, n_clusters, device, generator, chunk_size)
        labels = _assign_clusters(x, centers, distance_metric, x_pre_normalized, chunk_size)

        # Check for convergence
        center_shift = torch.norm(centers - prev_centers) / torch.norm(prev_centers)
        if center_shift < tol:
            logger.debug(f"Converged after {it + 1} iterations (shift={center_shift:.6f} < tol={tol})")
            break

        prev_centers = centers.clone()

    centers = centers.cpu()
    if cache_final_results_path is not None:
        _safe_save({"centers": centers, "labels": labels}, cache_final_results_path)
        logger.info(f"Saved kmeans final results to cache: {cache_path}")

    return (centers, labels)


# pylint: disable=too-many-branches,too-many-locals
def hierarchical_kmeans(
    x: torch.Tensor,
    n_clusters: list[int],
    max_iters: int = 100,
    tol: float = 1e-4,
    distance_metric: Literal["l2", "cosine"] = "l2",
    init_method: Literal["random", "kmeans++"] = "kmeans++",
    n_local_trials: Optional[int] = None,
    chunk_size: Optional[int] = None,
    show_progress: bool = False,
    random_seed: Optional[int] = None,
    device: Optional[torch.device] = None,
    method: Literal["centers", "resampled"] = "centers",
    n_samples: Optional[list[int]] = None,
    n_resamples: int = 10,
    x_pre_normalized: bool = False,
    cache_dir: Optional[str | Path] = None,
) -> list[dict[str, torch.Tensor]]:
    """
    Run a bottom up hierarchical K-Means

    The hierarchical K-Means algorithm works by:
    1. Level 0: Apply K-Means to the original data
    2. Level 1: Apply K-Means to the centers from Level 0
    3. Level 2: Apply K-Means to the centers from Level 1
    4. Continue until n_levels is reached

    Parameters
    ----------
    x
        Data embeddings of shape (n_samples, n_features).
    n_clusters
        Number of clusters for each level of hierarchical K-Means. Must be in strictly descending order.
    max_iters
        Maximum number of iterations.
    tol
        Tolerance for convergence (normalized change in centers).
    distance_metric
        Distance metric to use.
    init_method
        Centers initialization method.
    n_local_trials
        Number of local trials to sample per iteration for K-Means++ initialization.
        If None, defaults to 2 + log(n_clusters). Use n_local_trials=1 to turn off.
    chunk_size
        Number of data points to process in a single batch during distance computations.
    show_progress
        If True, display a progress bar during processing.
    random_seed
        Random seed for reproducibility. If None, uses default random state.
    device
        The device (e.g., 'cuda', 'cpu') to perform computations on. If None, uses x.device.
    method
        Method for building hierarchy:
        - "centers": Cluster the centers from the previous level (traditional approach).
        - "resampled": Perform an initial K-Means at each level, then optionally refine
                       the centers using resampling.
    n_samples
        List of integers of length equal to 'len(n_clusters)', relevant when
        'method="resampled"'. For each level 'i', 'n_samples[i]' specifies how many
        points to resample per cluster:
        - If 'n_samples[i] > 0': resampling is applied at that level.
        - If 'n_samples[i] == 0': resampling is skipped at that level.
        For level 0, resampling is performed directly from the original dataset.
        For higher levels, resampling is performed from the previous level's centers.
    n_resamples
        Number of resampling steps to perform for each level when 'method="resampled"'.
    x_pre_normalized
        If True, assumes 'x' has already been L2-normalized to unit vectors.
    cache_dir
        Optional path to a directory for caching hierarchical K-Means results.
        If provided, each level gets its own subdirectory (level_0/, level_1/, etc.).
        For resampled method, each resample iteration gets its own subdirectory
        (resample_0/, resample_1/, etc.) within the level directory.
        Allows resuming from any point if interrupted.

    Returns
    -------
    A list of dictionaries where each dictionary contains:
    - centers: Centers of clusters of shape (n_clusters_level, n_features), on CPU.
    - assignment: Mapping from original data to cluster indices of shape (n_samples,), on CPU.

    References
    ----------
    .. [1] Huy V. Vo, Vasil Khalidov, Timothee Darcet, et al., "Automatic Data Curation
       for Self-Supervised Learning: A Clustering-Based Approach", arXiv preprint
       arXiv:2405.15613, 2024.

    Examples
    --------
    >>> data = torch.randn(1000, 50)  # 1000 samples, 50 features
    >>> results = hierarchical_kmeans(data, n_clusters=[100, 20, 5])
    >>> results[0]["centers"].shape  # Level 0: 100 clusters from 1000 points
    torch.Size([100, 50])
    >>> results[1]["centers"].shape  # Level 1: 20 clusters from 100 centers
    torch.Size([20, 50])
    >>> results[2]["centers"].shape  # Level 2: 5 clusters from 20 centers
    torch.Size([5, 50])
    """

    n_levels = len(n_clusters)

    # Input validation
    if x.size(0) == 0:
        raise ValueError("Input data cannot be empty")
    if any(nc <= 0 for nc in n_clusters):
        raise ValueError("All values in n_clusters must be positive")
    if len(n_clusters) > 1:
        for i in range(len(n_clusters) - 1):
            if n_clusters[i] <= n_clusters[i + 1]:
                raise ValueError(
                    f"n_clusters must be in strictly descending order. "
                    f"Found {n_clusters[i]} <= {n_clusters[i + 1]} at positions {i} and {i + 1}."
                )

    if method == "resampled":
        if n_samples is None:
            raise ValueError("n_samples must be provided when method is 'resampled'")
        if len(n_samples) != n_levels:
            raise ValueError(f"Length of n_samples ({len(n_samples)}) must match len(n_clusters) ({n_levels})")
        if any(ns < 0 for ns in n_samples):
            raise ValueError("All values in n_samples must be >= 0 when method is 'resampled'")
        if n_resamples <= 0:
            raise ValueError("n_resamples must be positive when method is 'resampled'")

    logger.info(f"Starting Hierarchical K-Means: levels={n_clusters}, method={method}")
    if cache_dir is not None:
        cache_path = Path(cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)

        _save_config(
            {
                "n_clusters_levels": n_clusters,
                "max_iters": max_iters,
                "tol": tol,
                "distance_metric": distance_metric,
                "init_method": init_method,
                "n_local_trials": n_local_trials,
                "random_seed": random_seed,
                "method": method,
                "n_samples": n_samples,
                "n_resamples": n_resamples,
                "x_pre_normalized": x_pre_normalized,
            },
            cache_path,
        )

    results: list[dict[str, torch.Tensor]] = []
    current_level_assignments = torch.empty(0)
    current_centers = torch.empty(0)
    for level in range(n_levels):
        level_cache_dir: Optional[Path] = None
        if cache_dir is not None:
            level_cache_dir = Path(cache_dir).joinpath(f"level_{level}")

        if level == 0:
            data = x  # First level: use original data
        else:
            data = current_centers  # Subsequent levels: use previous centers

        (centers, center_assignment) = kmeans(
            data,
            n_clusters=n_clusters[level],
            max_iters=max_iters,
            tol=tol,
            distance_metric=distance_metric,
            init_method=init_method,
            n_local_trials=n_local_trials,
            chunk_size=chunk_size,
            show_progress=show_progress,
            random_seed=random_seed,
            device=device,
            x_pre_normalized=x_pre_normalized if level == 0 else False,
            cache_dir=level_cache_dir,
        )

        current_centers = centers.to(x.device)
        if method == "resampled" and n_samples[level] > 0:  # type: ignore[index]
            sample_size = n_samples[level]  # type: ignore[index]
            logger.info(f"Level {level}: resampling {sample_size} points per cluster for {n_resamples} resamples")
            for resample_iter in range(n_resamples):
                logger.info(f"Level {level}, resample {resample_iter + 1}/{n_resamples}")
                # Collect sampled points from each cluster based on proximity to current center
                sampled_points_list = []
                for cluster_id in range(n_clusters[level]):
                    cluster_indices = torch.where(center_assignment == cluster_id)[0]
                    if cluster_indices.numel() == 0:
                        continue

                    cluster_points = data[cluster_indices]

                    # Pick closest points to the center
                    distances = compute_distance(
                        cluster_points,
                        centers[cluster_id : cluster_id + 1],
                        distance_metric,
                        x_pre_normalized=x_pre_normalized if level == 0 else False,
                    )
                    sorted_indices = torch.argsort(distances.squeeze(1))
                    chosen_indices = sorted_indices[: min(sample_size, len(sorted_indices))]

                    sampled_points_list.append(cluster_points[chosen_indices])

                if len(sampled_points_list) == 0:
                    logger.warning(
                        f"Level {level}, resample {resample_iter}: no points were sampled from any cluster, skipping..."
                    )
                    continue

                sampled_points = torch.concat(sampled_points_list, dim=0)

                resample_cache_dir = None
                if level_cache_dir is not None:
                    resample_cache_dir = level_cache_dir.joinpath(f"resample_{resample_iter}")

                # Re-run k-means on the sampled points to refine centers
                (centers, _) = kmeans(
                    sampled_points,
                    n_clusters=n_clusters[level],
                    max_iters=max_iters,
                    tol=tol,
                    distance_metric=distance_metric,
                    init_method=init_method,
                    n_local_trials=n_local_trials,
                    chunk_size=chunk_size,
                    show_progress=show_progress,
                    random_seed=random_seed,
                    device=device,
                    x_pre_normalized=x_pre_normalized if level == 0 else False,
                    cache_dir=resample_cache_dir,
                )

                # Re-assign all data points for this level to the newly refined centers
                logger.info(f"Level {level}, resample {resample_iter}: reassigning all data points")
                center_assignment = _assign_clusters(
                    data,
                    centers.to(device),
                    distance_metric,
                    x_pre_normalized=x_pre_normalized if level == 0 else False,
                    chunk_size=chunk_size,
                )
                current_centers = centers.to(x.device)

            logger.info(f"Level {level}: resampling completed after {n_resamples} iterations")

        if level == 0:
            original_assignment = center_assignment
        else:
            original_assignment = center_assignment[current_level_assignments]

        results.append(
            {
                "centers": centers.cpu(),
                "assignment": original_assignment,
            }
        )

        current_level_assignments = original_assignment

    return results


def split_cluster(
    x: torch.Tensor,
    labels: torch.Tensor,
    cluster_id: int,
    n_clusters: int,
    max_iters: int = 100,
    tol: float = 1e-4,
    distance_metric: Literal["l2", "cosine"] = "l2",
    init_method: Literal["random", "kmeans++"] = "kmeans++",
    n_local_trials: Optional[int] = None,
    chunk_size: Optional[int] = None,
    show_progress: bool = False,
    random_seed: Optional[int] = None,
    device: Optional[torch.device] = None,
    x_pre_normalized: bool = False,
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Split an existing cluster into multiple sub-clusters using K-Means

    This function extracts all data points belonging to a specific cluster
    and applies K-Means clustering to split them into n_clusters sub-clusters.

    Parameters
    ----------
    x
        Input data of shape (n_samples, n_features).
    labels
        Current cluster assignments of shape (n_samples,).
    cluster_id
        ID of the cluster to split.
    n_clusters
        Number of sub-clusters to create from the split.
    max_iters
        Maximum number of iterations.
    tol
        Tolerance for convergence (normalized change in centers).
    distance_metric
        Distance metric to use.
    init_method
        Centers initialization method.
    n_local_trials
        Number of local trials to sample per iteration for K-Means++ initialization.
        If None, defaults to 2 + log(n_clusters). Use n_local_trials=1 to turn off.
    chunk_size
        Number of data points to process in a single batch during distance computations.
    show_progress
        If True, display a progress bar during processing.
    random_seed
        Random seed for reproducibility. If None, uses default random state.
    device
        The device (e.g., 'cuda', 'cpu') to perform computations on. If None, runs on x.device.
    x_pre_normalized
        If True, assumes 'x' has already been L2-normalized to unit vectors.

    Returns
    -------
    A tuple containing:
    - New centers of the sub-clusters of shape (n_clusters, n_features), on CPU.
    - Updated labels of shape (n_samples,) where the original cluster_id is replaced with new cluster IDs, on CPU.
    """

    # Input validation
    if cluster_id not in labels:
        raise ValueError(f"Cluster ID {cluster_id} not found in labels")
    if n_clusters <= 1:
        raise ValueError("n_clusters must be greater than 1 for splitting")

    labels = labels.cpu()
    cluster_mask = labels == cluster_id
    cluster_data = x[cluster_mask]

    (sub_centers, sub_labels) = kmeans(
        cluster_data,
        n_clusters=n_clusters,
        max_iters=max_iters,
        tol=tol,
        distance_metric=distance_metric,
        init_method=init_method,
        n_local_trials=n_local_trials,
        chunk_size=chunk_size,
        show_progress=show_progress,
        random_seed=random_seed,
        device=device,
        x_pre_normalized=x_pre_normalized,
    )

    max_label = labels.max().item()
    new_labels = labels.clone()
    for sub_label_idx in range(n_clusters):
        sub_cluster_indices = torch.where(cluster_mask)[0][sub_labels == sub_label_idx]
        if sub_label_idx == 0:
            new_cluster_id = cluster_id
        else:
            new_cluster_id = max_label + sub_label_idx

        new_labels[sub_cluster_indices] = new_cluster_id

    return (sub_centers.cpu(), new_labels)


def predict(
    x: torch.Tensor,
    centers: torch.Tensor,
    distance_metric: Literal["l2", "cosine"] = "l2",
    chunk_size: Optional[int] = None,
    device: Optional[torch.device] = None,
    x_pre_normalized: bool = False,
) -> torch.Tensor:
    """
    Assigns new data points to the closest cluster centers.

    Parameters
    ----------
    x
        Input data of shape (n_samples, n_features).
    centers
        Cluster centers of shape (n_clusters, n_features) to which data will be assigned.
    distance_metric
        Distance metric to use:
        - "l2": L2 distance
        - "cosine": Cosine distance (1 - cosine similarity)
    chunk_size
        Number of data points to process in a single batch during distance computations.
    device
        The device (e.g., 'cuda', 'cpu') to perform computations on. If None, uses x.device.
    x_pre_normalized
        If True, assumes 'x' has already been L2-normalized to unit vectors.

    Returns
    -------
    Cluster assignments for 'x' of shape (n_samples,) with values in [0, n_clusters), on CPU.

    Examples
    --------
    >>> X_train = torch.randn(100, 2)
    >>> centers, _ = pt_kmeans.kmeans(X_train, n_clusters=5)
    >>> X_new = torch.randn(20, 2)
    >>> new_cluster_ids = pt_kmeans.predict(X_new, centers, distance_metric="l2")
    >>> new_cluster_ids.shape
    torch.Size([20])
    """

    if device is None:
        device = x.device

    return _assign_clusters(x, centers.to(device), distance_metric, x_pre_normalized, chunk_size)
