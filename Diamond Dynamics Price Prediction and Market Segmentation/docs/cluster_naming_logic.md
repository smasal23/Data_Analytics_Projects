# Cluster Naming Logic

## Purpose

This document explains how the project converts raw clustering output into human-readable market segments.

The logic is based on the actual implementation in:

- `src/modeling/evaluate_clustering.py`
  - `build_cluster_summary`
  - `build_cluster_name_mapping`
  - `apply_cluster_name_mapping`

---

## 1. Why Cluster Naming Is Needed

Clustering algorithms output arbitrary numeric labels such as:

- `0`
- `1`
- `2`
- `3`

These labels have no business meaning on their own.

Without a naming layer, a result like:

- “This diamond belongs to cluster 2”

is technically correct but not very useful.

The naming layer turns that into something more interpretable, such as:

- “This diamond belongs to the Premium Segment”

---

## 2. What the Project Uses to Interpret Clusters

The implemented function `build_cluster_summary` creates summary statistics for each cluster using the final cluster-assigned dataset.

### Numeric profile fields used
- `record_count`
- `avg_carat`
- `median_carat`
- `avg_price`
- `median_price`
- `avg_depth`
- `avg_table`

### Categorical profile fields used
- `dominant_cut`
- `dominant_color`
- `dominant_clarity`

### Distribution fields also included
- `cut_distribution`
- `color_distribution`
- `clarity_distribution`

This means cluster naming is not random; it is based on actual aggregated segment characteristics.

---

## 3. How the Naming Function Works

The function `build_cluster_name_mapping` sorts clusters by:

1. `avg_price`
2. `avg_carat`

That means clusters are interpreted from lower-value to higher-value / larger-size profiles.

Then the function assigns labels according to the number of clusters found.

### If there is 1 cluster
- `Core Segment`

### If there are 2 clusters
- `Value Segment`
- `Premium Segment`

### If there are 3 clusters
- `Small Value Segment`
- `Mid-Market Segment`
- `Large Premium Segment`

### If there are 4 or more clusters
The function uses a base sequence:
- `Entry Segment`
- `Value Segment`
- `Mid Segment`
- `Premium Segment`
- `Luxury Segment`
- `Elite Segment`

If there are more clusters than base labels, fallback names like `Segment 7`, `Segment 8`, and so on are added.

---

## 4. Cut-Based Suffix Logic

The naming function adds a suffix based on `dominant_cut` when available.

So instead of a plain label like:

- `Premium Segment`

the final label may become:

- `Premium Segment - Ideal`

This is a simple but effective way to make the segment description more informative.

---

## 5. Example of the Mapping Style

A produced mapping may look conceptually like:

```python
{
    0: "Entry Segment - Good",
    1: "Value Segment - Very Good",
    2: "Premium Segment - Premium",
    3: "Luxury Segment - Ideal"
}