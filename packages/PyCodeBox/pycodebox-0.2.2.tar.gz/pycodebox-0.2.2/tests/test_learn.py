import numpy as np
import pandas as pd
import matplotlib.figure as Figure
import matplotlib.axes as Axes
from pycodebox.learn import (
  random_forest_classifier,
  pca_kmeans_clustering,
)


def sample_data():
  # Create a small synthetic dataset
  np.random.seed(42)
  x = pd.DataFrame(
    {
      "feat1": np.random.randn(100),
      "feat2": np.random.rand(100),
      "feat3_rank": np.random.randint(0, 10, 100),
    }
  )
  # Binary target, as categorical
  y = pd.Series(np.random.choice(["A", "B"], size=100), dtype="category")
  return x, y


def test_random_forest_classifier_defaults():
  x, y = sample_data()
  result = random_forest_classifier(x, y, out_file_prefix="test_")
  # Basic checks
  assert isinstance(result, dict)
  assert "selected_features" in result
  assert "rfecv" in result
  assert "param_search" in result
  assert "confusion_matrix" in result
  assert "performance_report" in result
  assert "optimal_pred_threshold" in result
  assert "model" in result
  # Check that selected_features is non-empty
  assert len(result["selected_features"]) > 0


def test_random_forest_classifier_full_params():
  x, y = sample_data()
  result = random_forest_classifier(
    x,
    y,
    random_state=42,
    test_size=0.3,
    n_estimators=200,
    criterion="entropy",
    class_weight=None,
    max_depth=5,
    min_samples_split=5,
    min_samples_leaf=2,
    max_features=0.5,
    max_leaf_nodes=10,
    bootstrap=False,
    max_samples=None,
    cv=3,
    n_jobs=1,
    roc_curve_col="red",
    out_file_prefix="test_full_",
  )
  assert isinstance(result, dict)
  assert result["model"].n_estimators == 200 or result["model"].n_estimators in [
    100,
    200,
    500,
    1000,
  ]
  assert result["model"].max_depth == 5 or result["model"].max_depth in [
    None,
    10,
    20,
    30,
  ]
  assert result["model"].bootstrap is False
  assert isinstance(result["confusion_matrix"], pd.DataFrame)
  assert isinstance(result["performance_report"], pd.DataFrame)


def make_simple_df(n=40, nfeat=3, ngroups=3, seed=1):
  np.random.seed(seed)
  groups = np.arange(n) % ngroups
  data = np.random.randn(n, nfeat) + groups[:, None] * 3
  df = pd.DataFrame(data, columns=[f"feat{i}" for i in range(nfeat)])
  df["group"] = groups
  df["group"] = pd.Categorical(df["group"])
  return df


def test_pca_kmeans_clustering_required_params():
  df = make_simple_df()
  fig, ax, cluster_labels = pca_kmeans_clustering(df)
  assert isinstance(fig, Figure.Figure)
  assert isinstance(ax, Axes.Axes)
  assert isinstance(cluster_labels, np.ndarray)
  assert len(cluster_labels) == len(df)
  # Check that the number of unique clusters is at least 2
  assert len(np.unique(cluster_labels)) >= 2


def test_pca_kmeans_clustering_full_params():
  df = make_simple_df(n=60, nfeat=4, ngroups=4, seed=42)
  group_fill_color = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3"]
  fig, ax, cluster_labels, contingency = pca_kmeans_clustering(
    df,
    group_var="group",
    random_state=7,
    standardize=False,
    group_fill_color=group_fill_color,
  )
  assert isinstance(fig, Figure.Figure)
  assert isinstance(ax, np.ndarray)
  assert ax.shape == (2,)
  assert isinstance(cluster_labels, np.ndarray)
  assert len(cluster_labels) == len(df)
  assert isinstance(contingency, pd.DataFrame)
  # The number of rows in contingency must match unique groups
  assert contingency.shape[0] == df["group"].nunique()
  # The number of unique cluster labels matches the number of groups (k)
  assert len(np.unique(cluster_labels)) == df["group"].nunique()
