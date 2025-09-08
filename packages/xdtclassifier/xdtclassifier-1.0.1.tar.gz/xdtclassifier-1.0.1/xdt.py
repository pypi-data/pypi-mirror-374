# version 1.0.1

import numpy as np
import pandas as pd
import time
import psutil
import os
import gc
from numba import njit, prange, types

# External dependencies used in benchmarking helpers
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

# Self-contained XDT utilities (internal helpers)

def compute_quantile_edges(X, n_bins=64, sample_cap=100000, random_state=42):
    """Compute quantile-based bin edges preserving distribution mass."""
    rng = np.random.default_rng(random_state)
    if X.shape[0] > sample_cap:
        idx = rng.choice(X.shape[0], sample_cap, replace=False)
        Xs = X[idx]
    else:
        Xs = X
    qs = np.linspace(0, 1, n_bins + 1)
    edges = np.empty((X.shape[1], n_bins + 1), dtype=np.float64)
    for f in range(X.shape[1]):
        feat_values = Xs[:, f]
        valid_mask = ~np.isnan(feat_values)
        if np.sum(valid_mask) == 0:
            edges[f] = np.zeros(n_bins + 1)
            continue
        valid_values = feat_values[valid_mask]
        unique_vals = np.unique(valid_values)
        if len(unique_vals) <= n_bins:
            e = np.zeros(n_bins + 1)
            e[:len(unique_vals)] = unique_vals
            for i in range(len(unique_vals), n_bins + 1):
                e[i] = unique_vals[-1] + (i - len(unique_vals) + 1) * 1e-8
        else:
            e = np.quantile(valid_values, qs)
            for i in range(1, len(e)):
                if e[i] <= e[i-1]:
                    e[i] = e[i-1] + 1e-12
        e[0] = valid_values.min() - 1e-12
        e[-1] = valid_values.max() + 1e-12
        edges[f] = e
    return edges

def bin_with_edges(X, edges):
    """Use quantile edges to bin data with np.digitize for speed."""
    n_samples, n_features = X.shape
    n_bins = edges.shape[1] - 1
    Xb = np.empty_like(X, dtype=np.uint16)
    actual_bins = np.full(n_features, n_bins, dtype=np.int32)
    for f in range(n_features):
        mask_nan = np.isnan(X[:, f])
        has_nans = np.any(mask_nan)
        Xb[:, f] = np.digitize(X[:, f], edges[f][1:-1], right=False)
        if has_nans:
            Xb[mask_nan, f] = n_bins
            actual_bins[f] = n_bins + 1
        else:
            actual_bins[f] = n_bins
    return Xb, edges, actual_bins

@njit(cache=True, fastmath=True)
def partition_inplace(indices, X_col, thr):
    """In-place two-pointer partition. Returns split point."""
    i = 0
    j = len(indices) - 1
    while i <= j:
        if X_col[indices[i]] <= thr:
            i += 1
        else:
            tmp = indices[i]
            indices[i] = indices[j]
            indices[j] = tmp
            j -= 1
    return i

@njit(cache=True, fastmath=True, parallel=True)
def compute_exact_variance_bounds_multiclass(X_binned, indices, parent_gini):
    """XDT: Exact variance bounds without sampling - multi-class compatible."""
    n_features = X_binned.shape[1]
    max_possible_gains = np.zeros(n_features)
    n_indices = len(indices)
    if n_indices <= 1:
        return max_possible_gains
    for f in prange(n_features):
        s = 0.0
        ss = 0.0
        for i in range(n_indices):
            v = float(X_binned[indices[i], f])
            s += v
            ss += v * v
        mean = s / n_indices
        variance = ss / n_indices - mean * mean
        max_possible_gains[f] = parent_gini * variance
    return max_possible_gains

@njit(parallel=True, cache=True, fastmath=True)
def build_histograms_column_major_multiclass(idx, Xb_cf, y, bins_cf, n_classes, out_hist):
    """XDT: Column-major histogram build for better cache locality - MULTI-CLASS."""
    nF = Xb_cf.shape[0]
    for j in prange(nF):
        nb = bins_cf[j]
        for b in range(nb):
            for c in range(n_classes):
                out_hist[j, b, c] = 0
        for t in range(len(idx)):
            s = idx[t]
            b = Xb_cf[j, s]
            class_idx = y[s]
            if b < nb and class_idx >= 0 and class_idx < n_classes:
                out_hist[j, b, class_idx] += 1

@njit(cache=True, fastmath=True)
def compute_multiclass_gini(class_counts, total_count):
    """Compute Gini impurity for multi-class case."""
    if total_count == 0:
        return 0.0
    gini = 1.0
    for c in range(len(class_counts)):
        p = class_counts[c] / total_count
        gini -= p * p
    return gini

@njit(cache=True, fastmath=True)
def _gini_from_counts(class_counts, total_count):
    """Numba-friendly Gini computation from class counts.

    Used by indexed exact-split helpers in this module.
    """
    if total_count <= 0:
        return 0.0
    g = 1.0
    for c in range(len(class_counts)):
        p = class_counts[c] / total_count
        g -= p * p
    return g

@njit(cache=True, fastmath=True)
def best_split_from_hist_optimized_multiclass(hist, total_count, class_totals, parent_gini, n_classes, min_samples_leaf=2):
    n_bins = hist.shape[0]
    if total_count <= 0 or n_bins <= 1:
        return -1, -1.0, 0

    total_left_count = 0
    left_counts = np.zeros(n_classes, dtype=np.int32)

    total_ss = 0.0
    for c in range(n_classes):
        v = class_totals[c]
        total_ss += v * v

    left_ss = 0.0
    left_dot_total = 0.0

    inv_tot = 1.0 / total_count
    best_gain = -1.0
    best_bin = -1
    best_lc = 0

    for b in range(n_bins - 1):
        bin_sum = 0
        for c in range(n_classes):
            add = hist[b, c]
            if add == 0:
                continue
            old = left_counts[c]
            new = old + add
            left_counts[c] = new
            left_ss += 2.0 * old * add + add * add
            left_dot_total += add * class_totals[c]
            bin_sum += add

        if bin_sum == 0:
            continue

        total_left_count += bin_sum
        total_right_count = total_count - total_left_count

        if (total_left_count < min_samples_leaf or total_right_count < min_samples_leaf):
            continue

        left_gini = 1.0 - left_ss / (total_left_count * total_left_count)
        right_ss = total_ss + left_ss - 2.0 * left_dot_total
        right_gini = 1.0 - right_ss / (total_right_count * total_right_count)

        weighted = (total_left_count * inv_tot) * left_gini + (total_right_count * inv_tot) * right_gini
        gain = parent_gini - weighted

        if gain > best_gain:
            best_gain = gain
            best_bin = b
            best_lc = total_left_count

    return best_bin, best_gain, best_lc


@njit(cache=True, fastmath=True)
def guaranteed_exact_split_optimized_multiclass(x_raw, y_idx, n_classes, min_leaf, max_unique_vals=10000):
    """Compute exact split for a single feature (multi-class) using O(n) buckets when feasible, otherwise sorting."""
    n_total = len(x_raw)
    valid_count = 0
    
    # Count valid (non-NaN) values and find range
    min_val = np.inf
    max_val = -np.inf
    for i in range(n_total):
        if not (x_raw[i] != x_raw[i]):  # NaN check in numba
            valid_count += 1
            if x_raw[i] < min_val:
                min_val = x_raw[i]
            if x_raw[i] > max_val:
                max_val = x_raw[i]
    
    if valid_count < 2 * min_leaf:
        return (np.nan, -1.0), False
    
    # Binary optimization: fast path for 2-class problems
    if n_classes == 2:
        result = _guaranteed_exact_binary_optimized(x_raw, y_idx, min_leaf, max_unique_vals)
        return result
    
    # Use bucket only for integer-like features with a reasonable number of buckets
    # Otherwise, fall back to sorting for exact splits on continuous features
    n_buckets = int(np.floor(max_val) - np.floor(min_val)) + 1 if (max_val > -np.inf and min_val < np.inf) else 0
    # Integer-like if all fractional parts are ~0 or ~1
    frac_ok = True
    if n_buckets > 1 and n_buckets <= max_unique_vals:
        for i in range(n_total):
            v = x_raw[i]
            if not (v != v):
                fv = v - np.floor(v)
                if fv > 1e-6 and (1.0 - fv) > 1e-6:
                    frac_ok = False
                    break
    else:
        frac_ok = False
    if frac_ok:
        result = _bucket_exact_split_multiclass(x_raw, y_idx, n_classes, min_leaf, min_val, max_val, valid_count)
        return result, True
    else:
        result = _sorting_exact_split_multiclass(x_raw, y_idx, n_classes, min_leaf, valid_count)
        return result, False

@njit(cache=True, fastmath=True)
def _guaranteed_exact_binary_optimized(x_raw, y_idx, min_leaf, max_unique_vals=10000):
    """Binary-specific exact split."""
    n_total = len(x_raw)
    valid_count = 0
    
    # Count valid values and find range
    min_val = np.inf
    max_val = -np.inf
    for i in range(n_total):
        if not (x_raw[i] != x_raw[i]):  # NaN check
            valid_count += 1
            if x_raw[i] < min_val:
                min_val = x_raw[i]
            if x_raw[i] > max_val:
                max_val = x_raw[i]
    
    if valid_count < 2 * min_leaf:
        return (np.nan, -1.0), False
    
    # Use bucket only when values are integer-like and bucket count is sensible
    n_buckets = int(np.floor(max_val) - np.floor(min_val)) + 1 if (max_val > -np.inf and min_val < np.inf) else 0
    frac_ok = True
    if n_buckets > 1 and n_buckets <= max_unique_vals:
        for i in range(n_total):
            v = x_raw[i]
            if not (v != v):
                fv = v - np.floor(v)
                if fv > 1e-6 and (1.0 - fv) > 1e-6:
                    frac_ok = False
                    break
    else:
        frac_ok = False
    if frac_ok:
        result = _bucket_exact_split_binary(x_raw, y_idx, min_leaf, min_val, max_val, valid_count)
        return result, True
    else:
        result = _sorting_exact_split_binary(x_raw, y_idx, min_leaf, valid_count)
        return result, False

@njit(cache=True, fastmath=True)
def _bucket_exact_split_binary(x_raw, y_idx, min_leaf, min_val, max_val, valid_count):
    """O(n) bucket-based exact split for dense binary features."""
    n_buckets = int(max_val - min_val) + 1
    
    # Create buckets for counts (binary optimized)
    bucket_total = np.zeros(n_buckets, dtype=np.int32)
    bucket_pos = np.zeros(n_buckets, dtype=np.int32)
    
    total_pos = 0
    for i in range(len(x_raw)):
        if not (x_raw[i] != x_raw[i]):  # Valid value
            bucket_idx = int(x_raw[i] - min_val)
            bucket_total[bucket_idx] += 1
            if y_idx[i] == 1:
                bucket_pos[bucket_idx] += 1
                total_pos += 1
    
    # Calculate parent gini (binary optimized)
    p = total_pos / valid_count
    parent_gini = 1.0 - (p*p + (1-p)*(1-p))
    
    # Scan for best split
    best_gain = -1.0
    best_thr = np.nan
    left_count = 0
    left_pos = 0
    
    for b in range(n_buckets - 1):
        if bucket_total[b] == 0:
            continue
            
        left_count += bucket_total[b]
        left_pos += bucket_pos[b]
        right_count = valid_count - left_count
        right_pos = total_pos - left_pos
        
        if left_count < min_leaf or right_count < min_leaf:
            continue
            
        # Binary Gini calculation (faster than multi-class)
        lp_ratio = left_pos / left_count
        rp_ratio = right_pos / right_count
        
        left_gini = 1.0 - (lp_ratio*lp_ratio + (1-lp_ratio)*(1-lp_ratio))
        right_gini = 1.0 - (rp_ratio*rp_ratio + (1-rp_ratio)*(1-rp_ratio))
        
        gain = parent_gini - (left_count/valid_count)*left_gini - (right_count/valid_count)*right_gini
        
        if gain > best_gain:
            best_gain = gain
            best_thr = min_val + b + 0.5
    
    return best_thr, best_gain

@njit(cache=True, fastmath=True)
def _sorting_exact_split_binary(x_raw, y_idx, min_leaf, valid_count):
    """O(n log n) sorting-based exact split for continuous binary features."""
    # Extract valid values
    x = np.empty(valid_count, dtype=np.float32)
    y = np.empty(valid_count, dtype=np.int32)
    idx = 0
    for i in range(len(x_raw)):
        if not (x_raw[i] != x_raw[i]):  # NaN check
            x[idx] = x_raw[i]
            y[idx] = y_idx[i]
            idx += 1
    
    # Sort by feature value
    order = np.argsort(x)
    xs = x[order]
    ys = y[order]
    n = len(xs)
    
    # Calculate parent gini (binary optimized)
    total_pos = np.sum(ys)
    p = total_pos / n
    parent_gini = 1.0 - (p*p + (1-p)*(1-p))
    
    best_gain = -1.0
    best_thr = np.nan
    left_pos = 0
    
    # Scan split positions
    for b in range(n - 1):
        left_pos += ys[b]
        
        if xs[b] == xs[b + 1]:  # Skip non-changing values
            continue
            
        left_count = b + 1
        right_count = n - left_count
        
        if left_count < min_leaf or right_count < min_leaf:
            continue
            
        right_pos = total_pos - left_pos
        
        # Binary Gini calculation (faster)
        lp_ratio = left_pos / left_count
        rp_ratio = right_pos / right_count
        
        left_gini = 1.0 - (lp_ratio*lp_ratio + (1-lp_ratio)*(1-lp_ratio))
        right_gini = 1.0 - (rp_ratio*rp_ratio + (1-rp_ratio)*(1-rp_ratio))
        
        gain = parent_gini - (left_count/n)*left_gini - (right_count/n)*right_gini
        
        if gain > best_gain:
            best_gain = gain
            best_thr = 0.5 * (xs[b] + xs[b+1])
    
    return best_thr, best_gain

@njit(cache=True, fastmath=True)
def _bucket_exact_split_multiclass(x_raw, y_idx, n_classes, min_leaf, min_val, max_val, valid_count):
    """O(n) bucket-based exact split for dense integer-like features (multi-class)."""
    n_buckets = int(max_val - min_val) + 1
    
    # Create buckets for counts
    bucket_total = np.zeros(n_buckets, dtype=np.int32)
    bucket_class_counts = np.zeros((n_buckets, n_classes), dtype=np.int32)
    
    total_class_counts = np.zeros(n_classes, dtype=np.int32)
    for i in range(len(x_raw)):
        if not (x_raw[i] != x_raw[i]):  # Valid value
            bucket_idx = int(x_raw[i] - min_val)
            bucket_total[bucket_idx] += 1
            class_idx = y_idx[i]
            if class_idx >= 0 and class_idx < n_classes:
                bucket_class_counts[bucket_idx, class_idx] += 1
                total_class_counts[class_idx] += 1
    
    # Calculate parent gini
    parent_gini = compute_multiclass_gini(total_class_counts, valid_count)
    
    # Scan for best split
    best_gain = -1.0
    best_thr = np.nan
    left_count = 0
    left_class_counts = np.zeros(n_classes, dtype=np.int32)
    
    for b in range(n_buckets - 1):
        if bucket_total[b] == 0:
            continue
            
        left_count += bucket_total[b]
        for c in range(n_classes):
            left_class_counts[c] += bucket_class_counts[b, c]
            
        right_count = valid_count - left_count
        right_class_counts = np.zeros(n_classes, dtype=np.int32)
        for c in range(n_classes):
            right_class_counts[c] = total_class_counts[c] - left_class_counts[c]
        
        if left_count < min_leaf or right_count < min_leaf:
            continue
            
        # Calculate gain
        left_gini = compute_multiclass_gini(left_class_counts, left_count)
        right_gini = compute_multiclass_gini(right_class_counts, right_count)
        
        gain = parent_gini - (left_count/valid_count)*left_gini - (right_count/valid_count)*right_gini
        
        if gain > best_gain:
            best_gain = gain
            best_thr = min_val + b + 0.5  # Split between bucket b and b+1
    
    return best_thr, best_gain

@njit(cache=True, fastmath=True)
def _sorting_exact_split_multiclass(x_raw, y_idx, n_classes, min_leaf, valid_count):
    """O(n log n) sorting-based exact split for continuous features (multi-class)."""
    # Extract valid values
    x = np.empty(valid_count, dtype=np.float32)
    y = np.empty(valid_count, dtype=np.int32)
    idx = 0
    for i in range(len(x_raw)):
        if not (x_raw[i] != x_raw[i]):  # NaN check
            x[idx] = x_raw[i]
            y[idx] = y_idx[i]
            idx += 1
    
    # Sort by feature value
    order = np.argsort(x)
    xs = x[order]
    ys = y[order]
    n = len(xs)
    
    # Calculate parent gini and total class counts
    total_class_counts = np.zeros(n_classes, dtype=np.int32)
    for i in range(n):
        class_idx = ys[i]
        if class_idx >= 0 and class_idx < n_classes:
            total_class_counts[class_idx] += 1
    
    parent_gini = compute_multiclass_gini(total_class_counts, n)
    
    best_gain = -1.0
    best_thr = np.nan
    left_class_counts = np.zeros(n_classes, dtype=np.int32)
    
    # Scan split positions
    for b in range(n - 1):
        class_idx = ys[b]
        if class_idx >= 0 and class_idx < n_classes:
            left_class_counts[class_idx] += 1
        
        if xs[b] == xs[b + 1]:  # Skip non-changing values
            continue
            
        left_count = b + 1
        right_count = n - left_count
        
        if left_count < min_leaf or right_count < min_leaf:
            continue
            
        right_class_counts = np.zeros(n_classes, dtype=np.int32)
        for c in range(n_classes):
            right_class_counts[c] = total_class_counts[c] - left_class_counts[c]
        
        left_gini = compute_multiclass_gini(left_class_counts, left_count)
        right_gini = compute_multiclass_gini(right_class_counts, right_count)
        
        gain = parent_gini - (left_count/n)*left_gini - (right_count/n)*right_gini
        
        if gain > best_gain:
            best_gain = gain
            best_thr = 0.5 * (xs[b] + xs[b+1])
    
    return best_thr, best_gain

@njit(cache=True, fastmath=True)
def exact_refine_in_bin_multiclass(x_raw, y, Xb_col, best_bin, total_count, class_totals, parent_gini, n_classes, min_leaf):
    """Original global variant (kept for compatibility)."""
    n_total = len(x_raw)
    
    # Count samples in adjacent bins
    boundary_count = 0
    for i in range(n_total):
        if Xb_col[i] == best_bin or Xb_col[i] == best_bin + 1:
            boundary_count += 1
    
    if boundary_count < 2 * min_leaf:
        return np.nan, -1.0
    
    # Extract boundary samples
    x_boundary = np.empty(boundary_count, dtype=np.float32)
    y_boundary = np.empty(boundary_count, dtype=np.int32)
    idx = 0
    for i in range(n_total):
        if Xb_col[i] == best_bin or Xb_col[i] == best_bin + 1:
            if not (x_raw[i] != x_raw[i]):  # Skip NaNs
                x_boundary[idx] = x_raw[i]
                y_boundary[idx] = y[i]
                idx += 1
    
    if idx < 2 * min_leaf:
        return np.nan, -1.0
    
    # Trim arrays to actual size
    x_boundary = x_boundary[:idx]
    y_boundary = y_boundary[:idx]
    
    # Sort boundary samples
    order = np.argsort(x_boundary)
    xs = x_boundary[order]
    ys = y_boundary[order]
    m = len(xs)
    
    # Count fixed samples in other bins for offset calculation
    fixed_left_count = 0
    fixed_left_class_counts = np.zeros(n_classes, dtype=np.int32)
    for i in range(n_total):
        if Xb_col[i] < best_bin:
            fixed_left_count += 1
            class_idx = y[i]
            if class_idx >= 0 and class_idx < n_classes:  # Bounds check
                fixed_left_class_counts[class_idx] += 1
    
    # Cumulative class counts within boundary region
    boundary_class_counts = np.zeros((m, n_classes), dtype=np.int32)
    
    # Initialize first position
    class_idx = ys[0]
    if class_idx >= 0 and class_idx < n_classes:
        boundary_class_counts[0, class_idx] = 1
    
    # Build cumulative counts
    for i in range(1, m):
        # Copy previous counts
        for c in range(n_classes):
            boundary_class_counts[i, c] = boundary_class_counts[i-1, c]
        # Add current sample
        class_idx = ys[i]
        if class_idx >= 0 and class_idx < n_classes:
            boundary_class_counts[i, class_idx] += 1
    
    best_gain = -1.0
    best_thr = np.nan
    
    for b in range(m - 1):
        if xs[b] == xs[b + 1]:
            continue
        boundary_left_count = b + 1
        # Total left class counts = fixed_left + boundary_left
        total_left_class_counts = np.zeros(n_classes, dtype=np.int32)
        for c in range(n_classes):
            total_left_class_counts[c] = fixed_left_class_counts[c] + boundary_class_counts[b, c]
        total_left_count = fixed_left_count + boundary_left_count
        total_right_count = total_count - total_left_count
        if total_left_count < min_leaf or total_right_count < min_leaf:
            continue
        total_right_class_counts = np.zeros(n_classes, dtype=np.int32)
        for c in range(n_classes):
            total_right_class_counts[c] = class_totals[c] - total_left_class_counts[c]
        left_gini = compute_multiclass_gini(total_left_class_counts, total_left_count)
        right_gini = compute_multiclass_gini(total_right_class_counts, total_right_count)
        gain = parent_gini - (total_left_count/total_count)*left_gini - (total_right_count/total_count)*right_gini
        if gain > best_gain:
            best_gain = gain
            best_thr = 0.5 * (xs[b] + xs[b+1])
    return best_thr, best_gain

@njit(cache=True, fastmath=True)
def exact_refine_in_bin_multiclass_idx(x_raw, y_all, Xb_col, idx, best_bin, total_count, class_totals, parent_gini, n_classes, min_leaf):
    """Indexed variant: exact refinement only using samples at histogram boundary bins.

    - Operates on the node's sample indices `idx`.
    - Routes NaNs to the right by construction (they are not in boundary set and not in fixed-left).
    """
    n_idx = len(idx)
    # Count boundary samples among idx
    boundary_count = 0
    for k in range(n_idx):
        i = idx[k]
        b = Xb_col[i]
        if b == best_bin or b == best_bin + 1:
            v = x_raw[i]
            if not (v != v):
                boundary_count += 1
    # If boundary is too large, skip in-bin to avoid O(m log m) with large m
    if boundary_count > max(4096, int(0.3 * total_count)):
        return np.nan, -1.0
    if boundary_count < 2 * min_leaf:
        return np.nan, -1.0
    # Extract boundary samples
    x_boundary = np.empty(boundary_count, dtype=np.float32)
    y_boundary = np.empty(boundary_count, dtype=np.int32)
    p = 0
    for k in range(n_idx):
        i = idx[k]
        b = Xb_col[i]
        if b == best_bin or b == best_bin + 1:
            v = x_raw[i]
            if not (v != v):
                x_boundary[p] = v
                y_boundary[p] = y_all[i]
                p += 1
    if p < 2 * min_leaf:
        return np.nan, -1.0
    # Sort boundary
    order = np.argsort(x_boundary[:p])
    xs = x_boundary[order]
    ys = y_boundary[order]
    m = len(xs)
    # Fixed-left from bins strictly less than best_bin
    fixed_left_count = 0
    fixed_left_class_counts = np.zeros(n_classes, dtype=np.int32)
    for k in range(n_idx):
        i = idx[k]
        if Xb_col[i] < best_bin:
            fixed_left_count += 1
            ci = y_all[i]
            if 0 <= ci < n_classes:
                fixed_left_class_counts[ci] += 1
    # Cumulative boundary class counts
    boundary_class_counts = np.zeros((m, n_classes), dtype=np.int32)
    ci0 = ys[0]
    if 0 <= ci0 < n_classes:
        boundary_class_counts[0, ci0] = 1
    for t in range(1, m):
        for c in range(n_classes):
            boundary_class_counts[t, c] = boundary_class_counts[t-1, c]
        ci = ys[t]
        if 0 <= ci < n_classes:
            boundary_class_counts[t, ci] += 1
    best_gain = -1.0
    best_thr = np.nan
    for t in range(m - 1):
        if xs[t] == xs[t + 1]:
            continue
        boundary_left = t + 1
        total_left_count = fixed_left_count + boundary_left
        total_right_count = total_count - total_left_count
        if total_left_count < min_leaf or total_right_count < min_leaf:
            continue
        total_left_class_counts = np.zeros(n_classes, dtype=np.int32)
        for c in range(n_classes):
            total_left_class_counts[c] = fixed_left_class_counts[c] + boundary_class_counts[t, c]
        total_right_class_counts = np.zeros(n_classes, dtype=np.int32)
        for c in range(n_classes):
            total_right_class_counts[c] = class_totals[c] - total_left_class_counts[c]
        left_gini = compute_multiclass_gini(total_left_class_counts, total_left_count)
        right_gini = compute_multiclass_gini(total_right_class_counts, total_right_count)
        gain = parent_gini - (total_left_count/total_count)*left_gini - (total_right_count/total_count)*right_gini
        if gain > best_gain:
            best_gain = gain
            best_thr = 0.5 * (xs[t] + xs[t+1])
    return best_thr, best_gain

@njit(cache=True, fastmath=True, parallel=True)
def _predict_numba_parallel_multiclass(X, is_leaf, features, thresholds, left_children, right_children, values):
    """JIT-compiled parallel tree traversal for maximum prediction speed."""
    n = X.shape[0]
    out = np.empty(n, dtype=np.int32)
    for i in prange(n):  # PARALLEL EXECUTION WITH PRANGE
        node = 0
        while True:
            if is_leaf[node]:
                out[i] = values[node]
                break
            if X[i, features[node]] <= thresholds[node]:
                node = left_children[node]
            else:
                node = right_children[node]
            if node == -1:  # Safety check
                out[i] = 0
                break
    return out

@njit(cache=True, fastmath=True)
def _predict_numba_multiclass(X, is_leaf, features, thresholds, left_children, right_children, values):
    """JIT-compiled tree traversal for maximum prediction speed."""
    n = X.shape[0]
    out = np.empty(n, dtype=np.int32)
    for i in range(n):
        node = 0
        while True:
            if is_leaf[node]:
                out[i] = values[node]
                break
            if X[i, features[node]] <= thresholds[node]:
                node = left_children[node]
            else:
                node = right_children[node]
            if node == -1:  # Safety check
                out[i] = 0
                break
    return out

@njit(cache=True, fastmath=True)
def guaranteed_exact_split_optimized_multiclass_idx(x_col, y_all, idx, n_classes, min_leaf, max_unique_vals=10000):
    n_idx = len(idx)
    valid = 0
    min_val = np.inf
    max_val = -np.inf
    for k in range(n_idx):
        i = idx[k]
        v = x_col[i]
        if not (v != v):
            valid += 1
            if v < min_val:
                min_val = v
            if v > max_val:
                max_val = v
    if valid < 2 * min_leaf:
        return (np.nan, -1.0), False

    if n_classes == 2:
        thr, gain, used_bucket = _guaranteed_exact_binary_optimized_idx(x_col, y_all, idx, min_leaf, max_unique_vals)
        return (thr, gain), used_bucket

    # Use buckets only for integer-like features with reasonable bucket count
    n_buckets = int(np.floor(max_val) - np.floor(min_val)) + 1 if (max_val > -np.inf and min_val < np.inf) else 0
    frac_ok = True
    if n_buckets > 1 and n_buckets <= max_unique_vals:
        for k in range(n_idx):
            i = idx[k]
            v = x_col[i]
            if not (v != v):
                fv = v - np.floor(v)
                if fv > 1e-6 and (1.0 - fv) > 1e-6:
                    frac_ok = False
                    break
    else:
        frac_ok = False
    if frac_ok:
        thr, gain = _bucket_exact_split_multiclass_idx(x_col, y_all, idx, n_classes, min_leaf, min_val, max_val, valid)
        return (thr, gain), True
    else:
        thr, gain = _sorting_exact_split_multiclass_idx(x_col, y_all, idx, n_classes, min_leaf, valid)
        return (thr, gain), False

@njit(cache=True, fastmath=True)
def _guaranteed_exact_binary_optimized_idx(x_col, y_all, idx, min_leaf, max_unique_vals=10000):
    n_idx = len(idx)
    valid = 0
    min_val = np.inf
    max_val = -np.inf
    for k in range(n_idx):
        i = idx[k]
        v = x_col[i]
        if not (v != v):
            valid += 1
            if v < min_val:
                min_val = v
            if v > max_val:
                max_val = v
    if valid < 2 * min_leaf:
        return np.nan, -1.0, False

    # Buckets only for integer-like with sensible bucket count
    n_buckets = int(np.floor(max_val) - np.floor(min_val)) + 1 if (max_val > -np.inf and min_val < np.inf) else 0
    frac_ok = True
    if n_buckets > 1 and n_buckets <= max_unique_vals:
        for k in range(n_idx):
            i = idx[k]
            v = x_col[i]
            if not (v != v):
                fv = v - np.floor(v)
                if fv > 1e-6 and (1.0 - fv) > 1e-6:
                    frac_ok = False
                    break
    else:
        frac_ok = False
    if frac_ok:
        thr, gain = _bucket_exact_split_binary_idx(x_col, y_all, idx, min_leaf, min_val, max_val, valid)
        return thr, gain, True
    else:
        thr, gain = _sorting_exact_split_binary_idx(x_col, y_all, idx, min_leaf, valid)
        return thr, gain, False

@njit(cache=True, fastmath=True)
def _bucket_exact_split_binary_idx(x_col, y_all, idx, min_leaf, min_val, max_val, valid_count):
    n_buckets = int(max_val - min_val) + 1
    bucket_total = np.zeros(n_buckets, dtype=np.int32)
    bucket_pos = np.zeros(n_buckets, dtype=np.int32)

    # Count totals including NaNs (which we deterministically route to the right child)
    total_count = len(idx)
    total_pos_all = 0

    for k in range(len(idx)):
        i = idx[k]
        yi = y_all[i]
        v = x_col[i]
        if yi == 1:
            total_pos_all += 1
        if not (v != v):  # valid
            b = int(v - min_val)
            bucket_total[b] += 1
            if yi == 1:
                bucket_pos[b] += 1

    # Parent gini over ALL samples in the node (valid + NaN)
    p = total_pos_all / total_count
    parent_gini = 1.0 - (p * p + (1 - p) * (1 - p))

    best_gain = -1.0
    best_thr = np.nan
    left_n_valid = 0
    left_pos = 0

    for b in range(n_buckets - 1):
        bt = bucket_total[b]
        if bt == 0:
            continue
        left_n_valid += bt
        left_pos += bucket_pos[b]
        # Right side includes remaining valid samples and all NaNs
        left_n = left_n_valid
        right_n = total_count - left_n
        if left_n < min_leaf or right_n < min_leaf:
            continue
        lp = left_pos / left_n
        rp = (total_pos_all - left_pos) / right_n
        lg = 1.0 - (lp * lp + (1 - lp) * (1 - lp))
        rg = 1.0 - (rp * rp + (1 - rp) * (1 - rp))
        gain = parent_gini - (left_n / total_count) * lg - (right_n / total_count) * rg
        if gain > best_gain:
            best_gain = gain
            best_thr = min_val + b + 0.5

    return best_thr, best_gain

@njit(cache=True, fastmath=True)
def _sorting_exact_split_binary_idx(x_col, y_all, idx, min_leaf, valid_count):
    x = np.empty(valid_count, dtype=np.float32)
    y = np.empty(valid_count, dtype=np.int32)
    p = 0
    total_count = len(idx)
    total_pos_all = 0
    for k in range(len(idx)):
        i = idx[k]
        v = x_col[i]
        yi = y_all[i]
        if yi == 1:
            total_pos_all += 1
        if not (v != v):
            x[p] = v
            y[p] = yi
            p += 1

    order = np.argsort(x)
    xs = x[order]
    ys = y[order]

    # Parent gini over all samples (valid + NaN)
    parent_gini = 1.0 - ((total_pos_all / total_count) ** 2 + (1 - total_pos_all / total_count) ** 2)

    best_thr = np.nan
    best_gain = -1.0
    left_pos = 0

    for t in range(p - 1):
        left_pos += ys[t]
        if xs[t] == xs[t + 1]:
            continue
        left_n = t + 1  # valid moved left
        right_n = total_count - left_n  # includes NaNs on right
        if left_n < min_leaf or right_n < min_leaf:
            continue
        lp = left_pos / left_n
        rp = (total_pos_all - left_pos) / right_n
        lg = 1.0 - (lp * lp + (1 - lp) * (1 - lp))
        rg = 1.0 - (rp * rp + (1 - rp) * (1 - rp))
        gain = parent_gini - (left_n / total_count) * lg - (right_n / total_count) * rg
        if gain > best_gain:
            best_gain = gain
            best_thr = 0.5 * (xs[t] + xs[t + 1])

    return best_thr, best_gain

@njit(cache=True, fastmath=True)
def _bucket_exact_split_multiclass_idx(x_col, y_all, idx, n_classes, min_leaf, min_val, max_val, valid_count):
    n_buckets = int(max_val - min_val) + 1
    bucket_total = np.zeros(n_buckets, dtype=np.int32)
    bucket_class = np.zeros((n_buckets, n_classes), dtype=np.int32)

    # Totals over ALL samples (valid + NaN) for consistent gains
    total_count = len(idx)
    total_class_all = np.zeros(n_classes, dtype=np.int32)

    for k in range(len(idx)):
        i = idx[k]
        v = x_col[i]
        yc = y_all[i]
        if 0 <= yc < n_classes:
            total_class_all[yc] += 1
        if not (v != v):
            b = int(v - min_val)
            bucket_total[b] += 1
            if 0 <= yc < n_classes:
                bucket_class[b, yc] += 1

    parent_gini = _gini_from_counts(total_class_all, total_count)

    best_thr = np.nan
    best_gain = -1.0
    left_n_valid = 0
    left_counts = np.zeros(n_classes, dtype=np.int32)
    total_ss = 0.0
    for c in range(n_classes):
        v = total_class_all[c]
        total_ss += v * v
    left_ss = 0.0
    left_dot_total = 0.0

    for b in range(n_buckets - 1):
        bt = bucket_total[b]
        if bt == 0:
            continue
        left_n_valid += bt
        for c in range(n_classes):
            add = bucket_class[b, c]
            if add == 0:
                continue
            old = left_counts[c]
            new = old + add
            left_counts[c] = new
            left_ss += 2.0 * old * add + add * add
            left_dot_total += add * total_class_all[c]

        left_n = left_n_valid
        right_n = total_count - left_n
        if left_n < min_leaf or right_n < min_leaf:
            continue
        lg = 1.0 - left_ss / (left_n * left_n)
        rg = 1.0 - (total_ss + left_ss - 2.0 * left_dot_total) / (right_n * right_n)
        gain = parent_gini - (left_n / total_count) * lg - (right_n / total_count) * rg
        if gain > best_gain:
            best_gain = gain
            best_thr = min_val + b + 0.5

    return best_thr, best_gain

@njit(cache=True, fastmath=True)
def _sorting_exact_split_multiclass_idx(x_col, y_all, idx, n_classes, min_leaf, valid_count):
    x = np.empty(valid_count, dtype=np.float32)
    y = np.empty(valid_count, dtype=np.int32)
    p = 0
    total_count = len(idx)
    total_class_all = np.zeros(n_classes, dtype=np.int32)
    for k in range(len(idx)):
        i = idx[k]
        v = x_col[i]
        ci = y_all[i]
        if 0 <= ci < n_classes:
            total_class_all[ci] += 1
        if not (v != v):
            x[p] = v
            y[p] = ci
            p += 1

    order = np.argsort(x)
    xs = x[order]
    ys = y[order]

    parent_gini = _gini_from_counts(total_class_all, total_count)

    best_thr = np.nan
    best_gain = -1.0

    left_counts = np.zeros(n_classes, dtype=np.int32)
    left_ss = 0.0
    total_ss = 0.0
    for c in range(n_classes):
        v = total_class_all[c]
        total_ss += v * v
    left_dot_total = 0.0

    for t in range(p - 1):
        ci = ys[t]
        if 0 <= ci < n_classes:
            old = left_counts[ci]
            new = old + 1
            left_counts[ci] = new
            left_ss += 2.0 * old + 1.0
            left_dot_total += total_class_all[ci]

        if xs[t] == xs[t + 1]:
            continue
        left_n = t + 1  # valid moved left
        right_n = total_count - left_n  # includes NaNs on right
        if left_n < min_leaf or right_n < min_leaf:
            continue
        lg = 1.0 - left_ss / (left_n * left_n)
        rg = 1.0 - (total_ss + left_ss - 2.0 * left_dot_total) / (right_n * right_n)
        gain = parent_gini - (left_n / total_count) * lg - (right_n / total_count) * rg
        if gain > best_gain:
            best_gain = gain
            best_thr = 0.5 * (xs[t] + xs[t + 1])

    return best_thr, best_gain


@njit(cache=True, fastmath=True)
def _predict_proba_numba_multiclass(X, is_leaf, features, thresholds, left_children, right_children, leaf_proba):
    n = X.shape[0]
    n_classes = leaf_proba.shape[1]
    out = np.zeros((n, n_classes), dtype=np.float32)
    for i in range(n):
        node = 0
        while True:
            if is_leaf[node]:
                for c in range(n_classes):
                    out[i, c] = leaf_proba[node, c]
                break
            if X[i, features[node]] <= thresholds[node]:
                node = left_children[node]
            else:
                node = right_children[node]
            if node == -1:
                # Fallback uniform distribution if something goes wrong
                for c in range(n_classes):
                    out[i, c] = 1.0 / n_classes
                break
    return out

# ----------------------
# XDT Multi-Class Classifier
# ----------------------
class XDTClassifier:
    """
    Default param (binary): max_depth=10, min_samples_split=20, min_samples_leaf=1,
                 n_bins=192, min_gain_threshold=1e-8, random_state=42,
                 use_parallel_prediction=True, parallel_threshold=256,
                 max_exact_refinements_binary=96
    Default param (multi): max_depth=14, min_samples_split=10, min_samples_leaf=1,
                 n_bins=256, min_gain_threshold=1e-9, random_state=42,
                 use_parallel_prediction=True, parallel_threshold=1000
    """
    def __init__(self, max_depth=10, min_samples_split=20, n_bins=192, 
                 min_gain_threshold=1e-8, min_samples_leaf=1, random_state=42,
                 use_parallel_prediction=True, map_labels=True, parallel_threshold=256,
                 max_exact_refinements=16, max_exact_refinements_binary=96):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.n_bins = n_bins
        self.min_gain_threshold = min_gain_threshold
        self.min_samples_leaf = min_samples_leaf
        self.random_state = random_state
        self.use_parallel_prediction = use_parallel_prediction
        # Whether to map internal int32 class IDs back to original labels in predict
        self.map_labels = map_labels
        # Threshold for enabling parallel prediction
        self.parallel_threshold = parallel_threshold
        # Cap the number of expensive exact refinements per node (training speed)
        self.max_exact_refinements = max_exact_refinements
        # Binary-only: allow a higher cap to maintain exactness without hurting speed
        self.max_exact_refinements_binary = max_exact_refinements_binary
        # In-bin refinement is now optional and disabled by default for speed parity
        self.use_in_bin_refinement = False
        self.nodes = []
        self.bin_edges_ = None
        self.actual_bins_ = None
        self.n_features_ = None
        self.n_classes_ = None
        self.classes_ = None
        
        # Enhanced buffer reuse - will be resized for multi-class
        self._hist_buf = np.zeros((512, 256, 10), dtype=np.int32)  # Start with support for 10 classes
        self._indices_buf = np.zeros(100000, dtype=np.int32)
        
        # XDT: Global feature-major binned matrix for reuse
        self.Xb_T = None
        
        # Algorithm tracking (XDT + exact refinement)
        self.algorithm_stats = {
            'histogram_splits_used': 0,
            'exact_refinement_used': 0,
            'guaranteed_exact_used': 0,        # exact split computations performed
            'bucket_optimization_used': 0,     # O(n) bucket sort for integer-like features  
            'sorting_used': 0,                 # O(n log n) for continuous features
            'total_splits': 0,
            'avg_candidates_per_split': 0.0,
            'algorithm_purity': 'XDT'
        }
    
    def _compute_multiclass_gini(self, y):
        """Compute multi-class Gini impurity."""
        if len(y) == 0:
            return 0.0
        counts = np.bincount(y, minlength=self.n_classes_)
        n = len(y)
        if n == 0:
            return 0.0
        probs = counts / n
        return 1.0 - np.sum(probs * probs)
    
    def _find_best_split(self, X_binned, y, indices, X_raw=None, depth=0):
        """Find best split using histograms, with optional exact refinement on top candidates"""
        total_count = len(indices)
        
        # Calculate class distribution
        y_subset = y[indices]
        class_counts = np.bincount(y_subset, minlength=self.n_classes_)
        parent_gini = self._compute_multiclass_gini(y_subset)
        
        if parent_gini < 1e-8:
            return None, None, 0.0
        
        # Compute variance bounds per feature to short-list candidates
        max_possible_gains = compute_exact_variance_bounds_multiclass(X_binned, indices, parent_gini)
        # For binary problems, use a fixed threshold to avoid prematurely pruning potentially useful features.
        if self.n_classes_ == 2:
            adaptive_bound_threshold = self.min_gain_threshold
        else:
            adaptive_bound_threshold = max(self.min_gain_threshold, parent_gini * 0.001)
        if max_possible_gains.max() <= adaptive_bound_threshold:
            return None, None, 0.0
        
        # Choose a feature subset to evaluate in detail
        n_features = X_binned.shape[1]
        # Binary: use a higher candidate floor to preserve accuracy
        min_floor = max(32 if self.n_classes_ == 2 else 16, int(np.sqrt(n_features)))
        cap = n_features
        
        # Binary vs multi-class tuning of candidate ratios
        if self.n_classes_ == 2:
            if parent_gini > 0.3:
                feature_ratio = 1.0
            elif parent_gini > 0.1:
                feature_ratio = 0.8
            else:
                feature_ratio = 0.5
            # Reduce candidates at deeper levels
            if depth >= 6:
                feature_ratio *= 0.5
            if depth >= 8:
                feature_ratio *= 0.75
        else:
            # Multi-class: conservative scheme
            if parent_gini > 0.4:
                feature_ratio = 1.0
            elif parent_gini > 0.2:
                feature_ratio = 0.9
            elif parent_gini > 0.1:
                feature_ratio = 0.7
            else:
                feature_ratio = 0.4
            if depth >= 5:
                feature_ratio *= 0.8
            if depth >= 8:
                feature_ratio *= 0.8
            
        k = min(cap, max(min_floor, int(n_features * feature_ratio)))
        
        # Feature selection
        if k >= n_features:
            topk_indices = np.argsort(max_possible_gains)[::-1]
        else:
            topk_indices = np.argpartition(-max_possible_gains, k-1)[:k]
            topk_indices = topk_indices[np.argsort(-max_possible_gains[topk_indices])]
        
        # Gentle filtering
        if len(topk_indices) > min_floor and max_possible_gains[topk_indices[0]] > 0:
            thr = max_possible_gains[topk_indices[0]] * 0.001
            filtered_indices = topk_indices[max_possible_gains[topk_indices] >= thr]
            
            if len(filtered_indices) < min_floor:
                candidate_features = topk_indices[:min_floor]
            else:
                candidate_features = filtered_indices
        else:
            candidate_features = topk_indices
                
        candidate_features = np.array(candidate_features, dtype=np.int32)
        
        # Build histograms using a reusable feature-major binned matrix
        max_features_this_node = len(candidate_features)
        max_bins_needed = self.actual_bins_.max()
        
        # Ensure histogram buffer can handle the number of classes
        if (max_features_this_node > self._hist_buf.shape[0] or
            max_bins_needed > self._hist_buf.shape[1] or
            self.n_classes_ > self._hist_buf.shape[2]):
            
            new_size_f = max(self._hist_buf.shape[0], max_features_this_node)
            new_size_b = max(self._hist_buf.shape[1], max_bins_needed)
            new_size_c = max(self._hist_buf.shape[2], self.n_classes_)
            
            # Auto-dtype for histogram counts based on node size
            if total_count <= 65535:
                hist_dtype = np.uint16
            else:
                hist_dtype = np.int32
                
            self._hist_buf = np.zeros((new_size_f, new_size_b, new_size_c), dtype=hist_dtype)
        
        hist_counts = self._hist_buf[:max_features_this_node, :max_bins_needed, :self.n_classes_]
        
        # XDT: Use global feature-major matrix (no per-node transpose)
        Xb_cf = self.Xb_T[candidate_features]
        bins_cf = self.actual_bins_[candidate_features]
        
        # Build histograms with column-major access
        build_histograms_column_major_multiclass(indices, Xb_cf, y, bins_cf, self.n_classes_, hist_counts)
        
        # Two-phase selection
        # Phase 1: Histogram evaluation for all candidates
        candidate_results = {}  # feature -> (threshold, gain, method_info)
        hist_gains = np.full(len(candidate_features), -1.0, dtype=np.float64)
        for j in range(len(candidate_features)):
            feature = candidate_features[j]
            hist_for_feature = hist_counts[j, :bins_cf[j], :]
            best_bin, hist_gain, _left_count = best_split_from_hist_optimized_multiclass(
                hist_for_feature, total_count, class_counts, parent_gini, self.n_classes_, self.min_samples_leaf
            )
            if best_bin >= 0 and hist_gain > 0:
                final_threshold = self.bin_edges_[feature, best_bin + 1]
                candidate_results[int(feature)] = (final_threshold, float(hist_gain), {'type': 'histogram', 'best_bin': int(best_bin), 'hist_gain': float(hist_gain)})
                hist_gains[j] = float(hist_gain)
            else:
                # No useful histogram split; keep as negative gain
                hist_gains[j] = -1.0

        # If raw data available, Phase 2: exact-refine a small set of candidates
        # Priority: top by histogram gain; if insufficient/zero, supplement with top by bounds.
        candidate_exact_results = []  # list of (feature, threshold, gain, method_info)

        if X_raw is not None:
            # Build refinement order: bounds-descending for early stopping
            bounds_cf = max_possible_gains[candidate_features]
            order_bounds = np.argsort(-bounds_cf)
            if self.n_classes_ == 2:
                kb = min(self.max_exact_refinements_binary, len(order_bounds))
                refine_list = [int(j) for j in order_bounds[:kb]]
            else:
                k = min(self.max_exact_refinements, len(order_bounds))
                # Build refine list: first positive histogram-gain candidates
                refine_list = []
                for j in order_bounds:
                    if len(refine_list) >= k:
                        break
                    ji = int(j)
                    if ji < 0 or ji >= len(candidate_features):
                        continue
                    if bounds_cf[ji] > 0:
                        refine_list.append(ji)
                # If we still have budget (or no positive hist gains), backfill by variance bounds
                if len(refine_list) < k:
                    for pos in order_bounds:
                        if len(refine_list) >= k:
                            break
                        ji = int(pos)
                        if ji in refine_list:
                            continue
                        refine_list.append(ji)

            # Run exact refinement for selected indices
            # Refine in bound-descending order; early stop when best exact >= next bound
            best_exact = -1.0
            for pos, ji in enumerate(refine_list):
                feature = int(candidate_features[ji])
                x_col = X_raw[:, feature]
                (exact_thr, exact_gain), bucket_used = guaranteed_exact_split_optimized_multiclass_idx(
                    x_col, y, indices, self.n_classes_, self.min_samples_leaf
                )
                # Track that we performed an exact refinement computation
                self.algorithm_stats['exact_refinement_used'] += 1
                if not np.isnan(exact_thr) and exact_gain > 0:
                    prev = candidate_results.get(feature, (np.nan, -1.0, {'type': 'histogram'}))
                    if exact_gain > prev[1]:
                        candidate_results[feature] = (float(exact_thr), float(exact_gain), {'type': 'exact', 'bucket_used': bool(bucket_used)})
                    if exact_gain > best_exact:
                        best_exact = exact_gain
                # Early stop: if best exact >= next candidate's upper bound, remaining can't win
                if pos + 1 < len(order_bounds):
                    next_bound = float(bounds_cf[int(order_bounds[pos + 1])])
                    if best_exact >= next_bound - 1e-15:
                        break

        # Materialize candidate list
        for feature, (thr, gain, info) in candidate_results.items():
            candidate_exact_results.append((int(feature), float(thr), float(gain), info))

        
        if not candidate_exact_results:
            return None, None, 0.0
        
        # Sort by gain (descending) and select the best
        candidate_exact_results.sort(key=lambda x: x[2], reverse=True)
        best_feature, best_threshold, best_gain, best_method_info = candidate_exact_results[0]

        if best_feature is None:
            return None, None, 0.0

        # Ensure the final decision is based on an exact evaluation when needed:
        # 1) If the leader is histogram-based, refine it.
        # 2) If a histogram runner-up would win after refining the leader, refine that runner-up too.
        # Keeps overhead small (<=2 refinements) while avoiding histogram-only choices.
        if best_method_info.get('type') == 'histogram' and X_raw is not None:
            # Default: skip in-bin for speed; use full exact once for final decision
            best_bin = int(best_method_info.get('best_bin', -1))
            x_col = X_raw[:, best_feature]
            if self.use_in_bin_refinement and best_bin >= 0:
                Xb_col = self.Xb_T[best_feature]
                thr_inbin, gain_inbin = exact_refine_in_bin_multiclass_idx(
                    x_col, y, Xb_col, indices, best_bin,
                    total_count, class_counts, parent_gini,
                    self.n_classes_, self.min_samples_leaf
                )
                self.algorithm_stats['exact_refinement_used'] += 1
                hist_gain_cur = float(best_method_info.get('hist_gain', best_gain))
                if not np.isnan(thr_inbin) and gain_inbin > 0 and float(gain_inbin) + 1e-9 >= hist_gain_cur:
                    best_threshold = float(thr_inbin)
                    best_gain = float(gain_inbin)
                    best_method_info = {'type': 'exact_inbin'}
                else:
                    (thr_exact, gain_exact), bucket_used = guaranteed_exact_split_optimized_multiclass_idx(
                        x_col, y, indices, self.n_classes_, self.min_samples_leaf
                    )
                    self.algorithm_stats['exact_refinement_used'] += 1
                    if not np.isnan(thr_exact) and gain_exact > 0:
                        best_threshold = float(thr_exact)
                        best_gain = float(gain_exact)
                        best_method_info = {'type': 'exact', 'bucket_used': bool(bucket_used)}
            else:
                (thr_exact, gain_exact), bucket_used = guaranteed_exact_split_optimized_multiclass_idx(
                    x_col, y, indices, self.n_classes_, self.min_samples_leaf
                )
                self.algorithm_stats['exact_refinement_used'] += 1
                if not np.isnan(thr_exact) and gain_exact > 0:
                    best_threshold = float(thr_exact)
                    best_gain = float(gain_exact)
                    best_method_info = {'type': 'exact', 'bucket_used': bool(bucket_used)}

        # If the best is still histogram-based (e.g., original best was exact but next is histogram with higher gain),
        # refine that histogram candidate before finalizing selection.
        if best_method_info.get('type') == 'histogram' and X_raw is not None:
            # Identify its index in the sorted list
            # candidate_exact_results is list of (feature, thr, gain, info) sorted desc by gain
            # Find the entry matching best_feature and best_threshold/gain if possible (fallback by feature)
            idx_best = None
            for i, (f, thr, g, info) in enumerate(candidate_exact_results):
                if f == best_feature and abs(g - best_gain) < 1e-15:
                    idx_best = i
                    break
            if idx_best is None:
                idx_best = 0
            # Refine that candidate
            x_col = X_raw[:, best_feature]
            best_bin = int(best_method_info.get('best_bin', -1))
            if self.use_in_bin_refinement and best_bin >= 0:
                Xb_col = self.Xb_T[best_feature]
                thr_inbin, gain_inbin = exact_refine_in_bin_multiclass_idx(
                    x_col, y, Xb_col, indices, best_bin,
                    total_count, class_counts, parent_gini,
                    self.n_classes_, self.min_samples_leaf
                )
                self.algorithm_stats['exact_refinement_used'] += 1
                hist_gain_cur = float(best_method_info.get('hist_gain', best_gain))
                if not np.isnan(thr_inbin) and gain_inbin > 0 and float(gain_inbin) + 1e-9 >= hist_gain_cur:
                    best_threshold = float(thr_inbin)
                    best_gain = float(gain_inbin)
                    best_method_info = {'type': 'exact_inbin'}
                else:
                    (thr_exact, gain_exact), bucket_used = guaranteed_exact_split_optimized_multiclass_idx(
                        x_col, y, indices, self.n_classes_, self.min_samples_leaf
                    )
                    self.algorithm_stats['exact_refinement_used'] += 1
                    if not np.isnan(thr_exact) and gain_exact > 0:
                        best_threshold = float(thr_exact)
                        best_gain = float(gain_exact)
                        best_method_info = {'type': 'exact', 'bucket_used': bool(bucket_used)}
            else:
                (thr_exact, gain_exact), bucket_used = guaranteed_exact_split_optimized_multiclass_idx(
                    x_col, y, indices, self.n_classes_, self.min_samples_leaf
                )
                self.algorithm_stats['exact_refinement_used'] += 1
                if not np.isnan(thr_exact) and gain_exact > 0:
                    best_threshold = float(thr_exact)
                    best_gain = float(gain_exact)
                    best_method_info = {'type': 'exact', 'bucket_used': bool(bucket_used)}

        # Optionally compare against the second-best: if the second-best has higher gain but is histogram-based,
        # refine it and choose the higher of the two exact gains.
        if len(candidate_exact_results) > 1 and X_raw is not None:
            bf2, bt2, bg2, info2 = candidate_exact_results[1]
            if info2.get('type') == 'histogram':
                x_col2 = X_raw[:, bf2]
                # Only refine runner-up if its bound suggests it could beat current best
                if max_possible_gains[bf2] + 1e-12 > best_gain:
                    (thr2_exact, gain2_exact), bucket2_used = guaranteed_exact_split_optimized_multiclass_idx(
                        x_col2, y, indices, self.n_classes_, self.min_samples_leaf
                    )
                    self.algorithm_stats['exact_refinement_used'] += 1
                    if not np.isnan(thr2_exact) and gain2_exact > 0:
                        if float(gain2_exact) > best_gain:
                            best_feature = int(bf2)
                            best_threshold = float(thr2_exact)
                            best_gain = float(gain2_exact)
                            best_method_info = {'type': 'exact', 'bucket_used': bool(bucket2_used)}
                    (thr2_exact, gain2_exact), bucket2_used = guaranteed_exact_split_optimized_multiclass_idx(
                        x_col2, y, indices, self.n_classes_, self.min_samples_leaf
                    )
                    self.algorithm_stats['exact_refinement_used'] += 1
                    if not np.isnan(thr2_exact) and gain2_exact > 0:
                        if float(gain2_exact) > best_gain:
                            best_feature = int(bf2)
                            best_threshold = float(thr2_exact)
                            best_gain = float(gain2_exact)
                            best_method_info = {'type': 'exact', 'bucket_used': bool(bucket2_used)}

        # Track the method used for the CHOSEN split only (after potential refinement)
        if best_method_info.get('type') == 'exact':
            self.algorithm_stats['guaranteed_exact_used'] += 1
            if best_method_info.get('bucket_used'):
                self.algorithm_stats['bucket_optimization_used'] += 1
            else:
                self.algorithm_stats['sorting_used'] += 1
        else:
            # Histogram method
            self.algorithm_stats['histogram_splits_used'] += 1
        
        # XDT: Track algorithm purity
        self.algorithm_stats['total_splits'] += 1
        
        # Update average candidates per split
        total = self.algorithm_stats['total_splits']
        old_avg = self.algorithm_stats['avg_candidates_per_split']
        self.algorithm_stats['avg_candidates_per_split'] = old_avg + (len(candidate_features) - old_avg) / total
        
        return best_feature, best_threshold, best_gain

    
    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.n_features_ = n_features
        
        # Convert to appropriate types with contiguous arrays
        X = np.ascontiguousarray(X, dtype=np.float32)
        # y = np.ascontiguousarray(y, dtype=np.int32)
        y = np.asarray(y) # Update 1.0.1

        # Invalidate compiled prediction caches (tree will change after fit)
        if hasattr(self, '_compiled_arrays'):
            self._compiled_arrays = None
        if hasattr(self, '_leaf_proba_bfs'):
            self._leaf_proba_bfs = None
        
        # Determine classes and number of classes
        self.classes_ = np.unique(y)
        self.n_classes_ = len(self.classes_)
        
        # Remap labels to 0, 1, 2, ... for internal processing
        label_map = {label: idx for idx, label in enumerate(self.classes_)}
        # y_mapped = np.array([label_map[label] for label in y], dtype=np.int32)
        y_mapped = np.ascontiguousarray([label_map[label] for label in y], dtype=np.int32) # Update 1.0.1
        
        # Set random seed for reproducibility
        np.random.seed(self.random_state if hasattr(self, 'random_state') else 42)
        
        # XDT: Quantile-based binning
        edges = compute_quantile_edges(X, n_bins=self.n_bins, random_state=self.random_state)
        X_binned, self.bin_edges_, self.actual_bins_ = bin_with_edges(X, edges)
        
        # XDT: Create global feature-major binned matrix (reused across all nodes)
        self.Xb_T = np.ascontiguousarray(X_binned.T)
        
        # Pre-allocate node list
        self.nodes = []
        
        # Use iterative approach with explicit stack
        indices_pool = np.arange(n_samples, dtype=np.int32)
        stack = [(indices_pool, 0, -1, None)]
        
        while stack:
            idx, depth, parent_id, is_left = stack.pop()
            
            # Stopping conditions
            adaptive_min_split = max(self.min_samples_split, 10)
            
            if (depth >= self.max_depth or 
                len(idx) < adaptive_min_split or
                len(idx) < 2 * self.min_samples_leaf):
                
                # Create leaf node with majority class
                y_subset = y_mapped[idx]
                class_counts = np.bincount(y_subset, minlength=self.n_classes_)
                leaf_value = np.argmax(class_counts)
                total = class_counts.sum()
                proba = (class_counts / total).astype(np.float32) if total > 0 else np.full(self.n_classes_, 1.0 / self.n_classes_, dtype=np.float32)
                
                node_id = len(self.nodes)
                self.nodes.append({
                    "type": "leaf",
                    "value": leaf_value,
                    "samples": len(idx),
                    "proba": proba
                })
                
                if parent_id >= 0:
                    if is_left:
                        self.nodes[parent_id]["left"] = node_id
                    else:
                        self.nodes[parent_id]["right"] = node_id
                continue
            
            # Check for pure node
            y_subset = y_mapped[idx]
            unique_classes = np.unique(y_subset)
            if len(unique_classes) == 1:  # Pure node
                leaf_value = unique_classes[0]
                class_counts = np.bincount(y_subset, minlength=self.n_classes_)
                total = class_counts.sum()
                proba = (class_counts / total).astype(np.float32) if total > 0 else np.full(self.n_classes_, 1.0 / self.n_classes_, dtype=np.float32)
                node_id = len(self.nodes)
                self.nodes.append({
                    "type": "leaf", 
                    "value": leaf_value,
                    "samples": len(idx),
                    "proba": proba
                })
                if parent_id >= 0:
                    if is_left:
                        self.nodes[parent_id]["left"] = node_id
                    else:
                        self.nodes[parent_id]["right"] = node_id
                continue
            
            parent_gini = self._compute_multiclass_gini(y_subset)
            
            # Use fixed threshold for binary; keep adaptive for multi-class
            if self.n_classes_ == 2:
                adjusted_threshold = self.min_gain_threshold
            else:
                adjusted_threshold = max(self.min_gain_threshold, parent_gini * 0.001)
            if parent_gini < adjusted_threshold:
                class_counts = np.bincount(y_subset, minlength=self.n_classes_)
                leaf_value = np.argmax(class_counts)
                total = class_counts.sum()
                proba = (class_counts / total).astype(np.float32) if total > 0 else np.full(self.n_classes_, 1.0 / self.n_classes_, dtype=np.float32)
                node_id = len(self.nodes)
                self.nodes.append({
                    "type": "leaf",
                    "value": leaf_value,
                    "samples": len(idx),
                    "proba": proba
                })
                if parent_id >= 0:
                    if is_left:
                        self.nodes[parent_id]["left"] = node_id
                    else:
                        self.nodes[parent_id]["right"] = node_id
                continue
            
            # TRUE XDT: Multi-class histogram-based split finding
            split_result = self._find_best_split(X_binned, y_mapped, idx, X, depth)
            
            if split_result is None or len(split_result) != 3:
                best_feature, best_threshold, best_gain = None, None, 0.0
            else:
                best_feature, best_threshold, best_gain = split_result
            
            # Use the same adaptive threshold for split acceptance
            if best_feature is None or best_gain <= adjusted_threshold:
                class_counts = np.bincount(y_subset, minlength=self.n_classes_)
                leaf_value = np.argmax(class_counts)
                total = class_counts.sum()
                proba = (class_counts / total).astype(np.float32) if total > 0 else np.full(self.n_classes_, 1.0 / self.n_classes_, dtype=np.float32)
                node_id = len(self.nodes)
                self.nodes.append({
                    "type": "leaf",
                    "value": leaf_value,
                    "samples": len(idx),
                    "proba": proba
                })
                if parent_id >= 0:
                    if is_left:
                        self.nodes[parent_id]["left"] = node_id
                    else:
                        self.nodes[parent_id]["right"] = node_id
                continue
            
            # Create decision node
            node_id = len(self.nodes)
            self.nodes.append({
                "type": "node",
                "feature": best_feature,
                "threshold": best_threshold,
                "gain": best_gain,
                "samples": len(idx),
                "left": None,
                "right": None
            })
            
            if parent_id >= 0:
                if is_left:
                    self.nodes[parent_id]["left"] = node_id
                else:
                    self.nodes[parent_id]["right"] = node_id
            
            # Data splitting using raw partitioning
            raw_feature_col = X[:, best_feature]
            split_point = partition_inplace(idx, raw_feature_col, np.float32(best_threshold))
            left_idx = idx[:split_point]
            right_idx = idx[split_point:]
            
            # Add to stack (right first for DFS order)
            if len(right_idx) > 0:
                stack.append((right_idx, depth + 1, node_id, False))
            if len(left_idx) > 0:
                stack.append((left_idx, depth + 1, node_id, True))
        
        return self
    
    def _compile_tree_to_arrays_bfs(self):
        """BFS layout for better memory locality"""
        from collections import deque
        
        queue = deque([0])
        bfs_order = []
        
        while queue:
            node_id = queue.popleft()
            if node_id < len(self.nodes):
                bfs_order.append(node_id)
                node = self.nodes[node_id]
                
                if node["type"] != "leaf":
                    if node.get("left") is not None:
                        queue.append(node["left"])
                    if node.get("right") is not None:
                        queue.append(node["right"])
        
        # Create mapping from old index to new BFS index
        old_to_new = {old_idx: new_idx for new_idx, old_idx in enumerate(bfs_order)}
        
        # Optimized memory layout with smaller data types
        n_nodes = len(bfs_order)
        is_leaf = np.zeros(n_nodes, dtype=bool)
        features = np.zeros(n_nodes, dtype=np.int32)
        thresholds = np.zeros(n_nodes, dtype=np.float32)
        left_children = np.full(n_nodes, -1, dtype=np.int32)
        right_children = np.full(n_nodes, -1, dtype=np.int32)
        values = np.zeros(n_nodes, dtype=np.int32)
        leaf_proba = np.zeros((n_nodes, self.n_classes_), dtype=np.float32)
        
        for new_idx, old_idx in enumerate(bfs_order):
            node = self.nodes[old_idx]
            if node["type"] == "leaf":
                is_leaf[new_idx] = True
                values[new_idx] = node["value"]
                # Store per-leaf class probability distribution
                if "proba" in node:
                    p = node["proba"].astype(np.float32)
                    # Ensure correct length and normalization
                    if p.shape[0] == self.n_classes_:
                        s = p.sum()
                        if s > 0:
                            leaf_proba[new_idx, :] = p / s
                        else:
                            leaf_proba[new_idx, :] = 1.0 / self.n_classes_
                    else:
                        leaf_proba[new_idx, :] = 1.0 / self.n_classes_
            else:
                features[new_idx] = node["feature"]
                thresholds[new_idx] = node["threshold"]
                if node.get("left") is not None:
                    left_children[new_idx] = old_to_new[node["left"]]
                if node.get("right") is not None:
                    right_children[new_idx] = old_to_new[node["right"]]

        # Make arrays contiguous for better cache performance
        # Save leaf probability matrix for predict_proba
        self._leaf_proba_bfs = np.ascontiguousarray(leaf_proba)

        return (np.ascontiguousarray(is_leaf),
                np.ascontiguousarray(features),
                np.ascontiguousarray(thresholds),
                np.ascontiguousarray(left_children),
                np.ascontiguousarray(right_children),
                np.ascontiguousarray(values))

    def predict_internal_prechecked(self, X_contig_f32):
        """Fast path: returns internal int32 class IDs (no label mapping)."""
        # if not hasattr(self, '_compiled_arrays'):
        if getattr(self, '_compiled_arrays', None) is None: # update 1.0.1
            self._compiled_arrays = self._compile_tree_to_arrays_bfs()

        batch_size = X_contig_f32.shape[0]
        use_parallel = self.use_parallel_prediction and batch_size >= self.parallel_threshold

        if use_parallel:
            return _predict_numba_parallel_multiclass(X_contig_f32, *self._compiled_arrays)
        else:
            return _predict_numba_multiclass(X_contig_f32, *self._compiled_arrays)

    def predict_prechecked(self, X_contig_f32, map_labels=None):
        """Fast path prediction with optional label mapping.

        - If map_labels is True (default), returns labels in `self.classes_`.
        - If False, returns internal int32 class IDs for maximum speed.
        """
        ids = self.predict_internal_prechecked(X_contig_f32)
        do_map = self.map_labels if map_labels is None else map_labels
        if do_map:
            # Vectorized mapping; preserves original sklearn-like semantics
            return np.take(self.classes_, ids)
        return ids
    
    def predict_internal(self, X):
        """Returns internal int32 class IDs (no label mapping)."""
        X = np.ascontiguousarray(X, dtype=np.float32)
        return self.predict_internal_prechecked(X)

    def predict(self, X, map_labels=None):
        """Optimized prediction with optional label mapping.

        - By default (None), uses instance setting `self.map_labels` (default True).
        - Set map_labels=False to skip mapping for maximum throughput.
        """
        X = np.ascontiguousarray(X, dtype=np.float32)
        return self.predict_prechecked(X, map_labels=map_labels)

    def predict_proba_prechecked(self, X_contig_f32):
        # if not hasattr(self, '_compiled_arrays'):
        if getattr(self, '_compiled_arrays', None) is None: # update 1.0.1
            self._compiled_arrays = self._compile_tree_to_arrays_bfs()
        # if not hasattr(self, '_leaf_proba_bfs') or self._leaf_proba_bfs is None:
        if getattr(self, '_leaf_proba_bfs', None) is None: # update 1.0.1
            # Ensure compiled proba matrix exists
            self._compile_tree_to_arrays_bfs()
        is_leaf, features, thresholds, left_children, right_children, _values = self._compiled_arrays
        proba_internal = _predict_proba_numba_multiclass(
            X_contig_f32,
            is_leaf,
            features,
            thresholds,
            left_children,
            right_children,
            self._leaf_proba_bfs,
        )
        return proba_internal  # already in internal class order

    def predict_proba(self, X):
        X = np.ascontiguousarray(X, dtype=np.float32)
        proba_internal = self.predict_proba_prechecked(X)
        # proba already aligned to self.classes_ order
        return proba_internal
    
    def print_algorithm_stats(self):
        """Print detailed algorithm purity statistics for XDT"""
        stats = self.algorithm_stats
        total = stats['total_splits']
        
        if total == 0:
            print("No splits performed yet.")
            return
            
        print(f"🚀 XDT MULTI-CLASS STATISTICS (Total Splits: {total})")
        print(f"   Classes: {self.n_classes_} ({list(self.classes_)})")
        print("=" * 80)
        
        # Algorithm breakdown stats
        hist_splits = stats['histogram_splits_used']
        exact_splits = stats['exact_refinement_used'] 
        guaranteed_splits = stats['guaranteed_exact_used']
        
        print(f"✅ Histogram-Based Splits: {hist_splits} ({hist_splits/total*100:.1f}%)")
        print(f"✅ Exact refinements evaluated: {exact_splits} ({exact_splits/total*100:.1f}%)")
        print(f"🚀 Exact Splits: {guaranteed_splits} ({guaranteed_splits/total*100:.1f}%)")
        print(f"✅ Avg Candidates/Split: {stats['avg_candidates_per_split']:.1f}")
        
        # Optimization method breakdown
        bucket_used = stats['bucket_optimization_used']
        sorting_used = stats['sorting_used']
        total_exact = guaranteed_splits
        
        if total_exact > 0:
            print(f"\n🚀 OPTIMIZATION METHOD BREAKDOWN:")
            print(f"  - O(n) Bucket Sort: {bucket_used} ({bucket_used/total_exact*100:.1f}%) - Integer-like features")
            print(f"  - O(n log n) Sorting: {sorting_used} ({sorting_used/total_exact*100:.1f}%) - Continuous features")
        
        # Algorithm components assessment
        print(f"\n🏆 ALGORITHM COMPONENTS:")
        print(f"  ✅ Quantile-based binning (XDT core)")
        print(f"  ✅ Histogram-based candidate selection (XDT core)")
        print(f"  🚀 Exact split computation") 
        print(f"  ✅ Multi-class variance bounds")
        print(f"  ✅ {stats['algorithm_purity']}")
        
        # Performance insights
        if total_exact > 0:
            bucket_ratio = bucket_used / total_exact * 100
            if bucket_ratio > 70:
                print(f"\n⚡ PERFORMANCE: {bucket_ratio:.1f}% O(n) optimization - Excellent for integer-like data")
            elif bucket_ratio > 30:
                print(f"\n📊 PERFORMANCE: {bucket_ratio:.1f}% O(n) optimization - Good mixed feature types")
            else:
                print(f"\n🔄 PERFORMANCE: {bucket_ratio:.1f}% O(n) optimization - Mostly continuous features")
