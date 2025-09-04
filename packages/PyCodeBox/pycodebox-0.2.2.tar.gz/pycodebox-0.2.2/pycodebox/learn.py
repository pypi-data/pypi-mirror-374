#!/bin/env python
# -*- coding: utf-8 -*-


# ----------------------------------------------------------------#
# Machine Learning Utilities                                      #
# ----------------------------------------------------------------#
# These functions consist of machine learning-based utilities     #
# for building and evaluating machine learning models and         #
# performing clustering analyses.                                 #
# ----------------------------------------------------------------#


def random_forest_classifier(
  x,
  y,
  random_state=1234,
  test_size=0.2,
  n_estimators=100,
  criterion="gini",
  class_weight="balanced_subsample",
  max_depth=None,
  min_samples_split=2,
  min_samples_leaf=1,
  max_features="sqrt",
  max_leaf_nodes=None,
  bootstrap=True,
  max_samples=None,
  cv=5,
  n_jobs=-1,
  roc_curve_col="black",
  out_file_prefix=None,
):
  """
  Trains and evaluates a random forest classifier using the provided feature matrix `x`
  and target vector `y`.

  Parameters
  ----------
  x : pandas.DataFrame
      Feature matrix for training and testing.
  y : array-like or pandas.Series
      Target values (class labels) as integers or strings.
  random_state : int, RandomState instance or None, optional
      Controls the randomness of the estimator (default: 1234).
  test_size : float, optional
      Proportion of the dataset to include in the test split (default: 0.2).
  n_estimators : int, optional
      Number of trees in the forest (default: 100).
  criterion : {"gini", "entropy", "log_loss"}, optional
      Function to measure the quality of a split (default: "gini").
  class_weight : dict, list of dict, "balanced", "balanced_subsample" or None, optional
      Weights associated with classes (default: "balanced_subsample").
  max_depth : int or None, optional
      Maximum depth of the tree (default: None).
  min_samples_split : int or float, optional
      Minimum number of samples required to split an internal node (default: 2).
  min_samples_leaf : int or float, optional
      Minimum number of samples required to be at a leaf node (default: 1).
  max_features : {"sqrt", "log2", None}, int or float, optional
      Number of features to consider when looking for the best split (default: "sqrt").
  max_leaf_nodes : int or None, optional
      Grow trees with `max_leaf_nodes` in best-first fashion (default: None).
  bootstrap : bool, optional
      Whether bootstrap samples are used when building trees (default: True).
  max_samples : int, float or None, optional
      If bootstrap is True, number of samples to draw from X to train each base
      estimator (default: None).
  cv : int, cross-validation generator or iterable, optional
      Determines the cross-validation splitting strategy (default: 5).
  n_jobs : int, optional
      Number of jobs to run in parallel (default: -1, use all available cores).
  roc_curve_col : str, optional
      Color for the ROC curve plot (default: "black").
  out_file_prefix : str or None, optional
      Prefix for output files. If None, no prefix is given to output files and they are
      saved to the current directory (default: None).

  Returns
  -------
  dict
      A dictionary containing the following values:
      - 'selected_features': Selected features from feature selection.
      - 'rfecv': The RFECV (Recursive Feature Elimination with Cross-Validation) object.
      - 'param_search': The RandomizedSearchCV object after hyperparameter tuning.
      - 'optimal_pred_threshold': The optimal probability threshold for classification.
      - 'confusion_matrix': The confusion matrix of the final model.
      - 'performance_report': The classification report as a DataFrame.
      - 'model': The trained RandomForestClassifier model.
  """
  import numpy as np
  import pandas as pd
  import matplotlib.pyplot as plt
  import seaborn as sns
  from sklearn.ensemble import RandomForestClassifier
  from sklearn.model_selection import (
    train_test_split,
    RandomizedSearchCV,
    StratifiedKFold,
  )
  from sklearn.feature_selection import RFECV
  from sklearn.metrics import (
    f1_score,
    precision_score,
    recall_score,
    classification_report,
    RocCurveDisplay,
  )

  # Split data into training and testing datasets (with stratification)
  x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=test_size, random_state=random_state
  )

  # Set random forest parameters
  rf = RandomForestClassifier(
    n_estimators=n_estimators,
    criterion=criterion,
    class_weight=class_weight,
    max_depth=max_depth,
    min_samples_split=min_samples_split,
    min_samples_leaf=min_samples_leaf,
    max_features=max_features,
    max_leaf_nodes=max_leaf_nodes,
    bootstrap=bootstrap,
    max_samples=max_samples,
    random_state=random_state,
    n_jobs=n_jobs,
  )

  # Feature selection using recursive feature elimination with cross validation
  rfecv = RFECV(
    estimator=rf,
    step=1,
    min_features_to_select=1,
    cv=StratifiedKFold(cv),
    scoring="balanced_accuracy",
    n_jobs=n_jobs,
  )
  rfecv.fit(x_train, y_train)
  selected_features = x_train.columns[rfecv.support_]

  # Hyperparameter tuning with randomized search and cross validation on selected features
  param_dist = {
    "n_estimators": [100, 200, 500, 1000],
    "max_depth": [None, 10, 20, 30],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4, 5],
    "max_features": ["sqrt", "log2", 0.2, 0.5, 1.0],
  }
  search = RandomizedSearchCV(
    estimator=rf,
    param_distributions=param_dist,
    n_iter=20,
    scoring="roc_auc",
    cv=StratifiedKFold(cv),
    random_state=random_state,
    n_jobs=n_jobs,
  )
  search.fit(x_train[selected_features], y_train)
  trained_mod = search.best_estimator_

  # Calculate probabilities with trained model
  y_prob = trained_mod.predict_proba(x_test[selected_features])[:, 1]

  # Sweep a range of probability thresholds to find best threshold for making predictions
  thresholds = np.linspace(0, 1, 101)
  f1s, precisions, recalls, accuracies = [], [], [], []

  for t in thresholds:
    preds = np.where(y_prob >= t, trained_mod.classes_[1], trained_mod.classes_[0])
    f1s.append(f1_score(y_test, preds, pos_label=y.cat.categories[1]))
    precisions.append(precision_score(y_test, preds, pos_label=y.cat.categories[1]))
    recalls.append(recall_score(y_test, preds, pos_label=y.cat.categories[1]))
    accuracies.append(np.mean(preds == y_test))

  # Get the threshold with the highest average across metrics
  optimal_pred_thresh = (
    pd.DataFrame(
      {
        "Threshold": thresholds,
        "F1": f1s,
        "Precision": precisions,
        "Recall": recalls,
        "Accuracy": accuracies,
      }
    )
    .set_index("Threshold")
    .mean(axis=1)
    .idxmax()
  )

  # Plot feature importances
  plt.figure(figsize=(6, len(selected_features) * 0.25))
  feature_importances = pd.DataFrame(
    {
      "Feature": selected_features.str.replace("_rank", ""),
      "Importance": trained_mod.feature_importances_,
    }
  ).sort_values("Importance", ascending=False)
  sns.barplot(
    data=feature_importances,
    x="Importance",
    y="Feature",
    hue="Feature",
    palette="viridis",
    legend=False,
  )
  plt.xlabel("Feature importance score", fontsize=10)
  plt.title(
    "Selected features and their importance scores\nfrom RFECV and RandomizedSearchCV",
    fontsize=10,
  )
  plt.grid(visible=True, alpha=0.3)
  plt.tight_layout()
  plt.savefig(f"{out_file_prefix}feature_importance.jpg", dpi=600)
  plt.close()

  # Plot classification metrics vs thresholds
  plt.figure(figsize=(8, 5))
  plt.plot(thresholds, f1s, label=f"F1 ({y.cat.categories[1]})")
  plt.plot(thresholds, precisions, label=f"Precision ({y.cat.categories[1]})")
  plt.plot(thresholds, recalls, label=f"Recall ({y.cat.categories[1]})")
  plt.plot(thresholds, accuracies, label="Accuracy")
  plt.axvline(
    x=optimal_pred_thresh,
    color="grey",
    linestyle="--",
    label=f"Max pan-metric average ({optimal_pred_thresh:.2f})",
  )
  plt.xlabel("Probability thresholds")
  plt.ylabel("Metric value")
  plt.title("Probability thresholds vs classification performance metrics")
  plt.legend(framealpha=1)
  plt.grid(alpha=0.3)
  plt.tight_layout()
  plt.savefig(f"{out_file_prefix}prob_vs_metrics.jpg", dpi=600)
  plt.close()

  # Generate predictions based on optimal probability threshold
  y_pred = np.where(
    y_prob >= optimal_pred_thresh,
    trained_mod.classes_[1],
    trained_mod.classes_[0],
  )

  # Generate confusion matrix
  confusion_mat = pd.crosstab(
    y_test, y_pred, rownames=["Actual"], colnames=["Predicted"]
  )

  # Generate classification performance report
  report_df = pd.DataFrame(classification_report(y_test, y_pred, output_dict=True)).T

  # Plot ROC curve
  RocCurveDisplay.from_estimator(
    trained_mod,
    x_test[selected_features],
    y_test,
    color=roc_curve_col,
    linewidth=5,
  )
  plt.plot([0, 1], [0, 1], color="grey", linestyle="--")
  plt.xlim([-0.01, 1.0])
  plt.ylim([0.0, 1.05])
  plt.xlabel("False positive rate")
  plt.ylabel("True positive rate")
  plt.grid(visible=True, alpha=0.3)
  plt.legend(loc="lower right")
  plt.tight_layout()
  plt.savefig(f"{out_file_prefix}ROC_AUC.jpg", dpi=600)
  plt.close()

  # Return training and testing components/reports and final trained model
  return {
    "selected_features": selected_features,
    "rfecv": rfecv,
    "param_search": search,
    "confusion_matrix": confusion_mat,
    "performance_report": report_df,
    "optimal_pred_threshold": optimal_pred_thresh,
    "model": trained_mod,
  }


def pca_kmeans_clustering(
  data,
  group_var=None,
  k_range=range(2, 20),
  random_state=0,
  standardize=True,
  group_fill_color=None,
):
  """
  Perform PCA and k-means clustering, plotting the first two PCs colored by clusters.
  Optionally, if a grouping variable is provided, plot two subplots: coloring by group
  and by k-means clusters, and return a contingency table.

  Parameters
  ----------
  data : pandas.DataFrame
      Input dataframe. Must be all numeric except possibly the grouping variable.
  group_var : str or None, optional
      Name of the column with known groupings. If provided, k will be set to the
      number of unique groups.
  k_range : range, optional
      Range of k values to try if group_var is not given.
  random_state : int, optional
      Random state for reproducibility.
  standardize : bool, optional
      Whether to standardize features before PCA (default: True).
  group_fill_color : list, optional
      List of color hex codes to use for filling the groups in the plot. If provided,
      it will override the default color mapping.

  Returns
  -------
  fig : matplotlib.figure.Figure
      A matplotlib figure object containing a PCA plot colored by k-means cluster
      membership and, if `group_var` provided, the known groupings.
  ax : matplotlib.axes.Axes
      A matplotlib axes object containing specifications of the PCA plot(s).
  cluster_labels : numpy.ndarray
      Array of cluster labels assigned by k-means.
  contingency_table : pandas.DataFrame
      A contingency table showing the relationship between the grouping variable and
      the k-means cluster membership. Only returned if `group_var` is provided.
  """
  import pandas as pd
  import numpy as np
  import matplotlib.pyplot as plt
  from sklearn.decomposition import PCA
  from sklearn.cluster import KMeans
  from sklearn.metrics import silhouette_score
  from sklearn.preprocessing import StandardScaler

  # Separate features and group_var
  if group_var is not None:
    # Make `group_var` categorical if not already
    if not (data[group_var].dtype.name == "category"):
      data[group_var] = pd.Categorical(data[group_var])

    # Grab `group_var` and expected k
    x = data.drop(columns=[group_var])
    k = len(data[group_var].cat.categories)
  else:
    x = data.copy()
    k = None

  # Only keep numeric features
  x = x.select_dtypes(include=[np.number])

  # Standardize to mean of ~0 and variance of 1
  if standardize:
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x)
  else:
    x_scaled = x.values

  # Perform PCA and extract first two components
  pca = PCA(n_components=2, random_state=random_state).fit_transform(x_scaled)
  pc_data = pd.DataFrame(pca, columns=["PC1", "PC2"])

  # Determine optimal k
  if k is None:
    sil_scores = []
    for i in k_range:
      labels = KMeans(
        n_clusters=i,
        n_init=10,
        random_state=random_state,
      ).fit_predict(x_scaled)
      sil_scores.append(silhouette_score(x_scaled, labels))
    k = k_range[np.argmax(sil_scores)]

  # Fit KMeans
  cluster_labels = KMeans(
    n_clusters=k,
    n_init=10,
    random_state=random_state,
  ).fit_predict(x_scaled)
  pc_data["cluster"] = cluster_labels

  ### Begin figure generation ###

  plt.ioff()
  if group_var is None:
    # Initiate a single plot
    fig, ax = plt.subplots(figsize=(6, 5))

    # Plot coloring by estimated cluster
    scatter = ax.scatter(
      pc_data["PC1"],
      pc_data["PC2"],
      c=pc_data["cluster"],
      cmap="tab10",
      s=50,
      alpha=0.8,
      edgecolor="k",
    )

    # Set plot title and formatting
    ax.set_title(f"PCA - Colored by estimated clusters (k={k})", fontsize=12)
    ax.set_xlabel("PC1", fontsize=12)
    ax.set_ylabel("PC2", fontsize=12)
    ax.grid(visible=True, alpha=0.3)

    # Set legend
    handles, labels = scatter.legend_elements(prop="colors")
    ax.legend(handles=handles, labels=labels, title="Cluster")

    return fig, ax, cluster_labels
  else:
    # Initiate a two-panel plot
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(12, 5))

    # Plot coloring by known group
    group_map = {g: i for i, g in enumerate(data[group_var].cat.categories)}
    group_colors = [group_map[grp] for grp in data[group_var].values]
    if group_fill_color is not None:
      color_list = [group_fill_color[group_map[grp]] for grp in data[group_var].values]
      g1 = ax[0].scatter(
        pc_data["PC1"],
        pc_data["PC2"],
        c=color_list,
        s=50,
        alpha=0.8,
        edgecolor="k",
      )
    else:
      g1 = ax[0].scatter(
        pc_data["PC1"],
        pc_data["PC2"],
        c=group_colors,
        cmap="tab10",
        s=50,
        alpha=0.8,
        edgecolor="k",
      )

    # Set plot title and formatting of first subplot
    group_var_format = group_var[0].upper() + group_var[1:].replace("_", " ")
    ax[0].set_title(f"PCA - Colored by {group_var_format}", fontsize=12)
    ax[0].set_xlabel("PC1", fontsize=12)
    ax[0].set_ylabel("PC2", fontsize=12)
    ax[0].grid(visible=True, alpha=0.3)

    # Set legend for known groups
    if group_fill_color is not None:
      # If group_fill_color is provided, use it to create legend handles
      handles = [
        plt.Line2D(
          [0],
          [0],
          marker="o",
          color="w",
          label=grp,
          markerfacecolor=group_fill_color[group_map[grp]],
        )
        for grp in data[group_var].cat.categories
      ]
      labels = list(data[group_var].cat.categories)
    else:
      # Otherwise, use the default legend elements
      handles, labels = g1.legend_elements(prop="colors")

    ax[0].legend(handles=handles, labels=labels, title=group_var_format)

    # Plot coloring by estimated cluster
    g2 = ax[1].scatter(
      pc_data["PC1"],
      pc_data["PC2"],
      c=pc_data["cluster"],
      cmap="tab10",
      s=50,
      alpha=0.8,
      edgecolor="k",
    )

    # Set plot title and formatting of second subplot
    ax[1].set_title(f"PCA - Colored by estimated clusters (k={k})", fontsize=12)
    ax[1].set_xlabel("PC1", fontsize=12)
    ax[1].set_ylabel("PC2", fontsize=12)
    ax[1].grid(visible=True, alpha=0.3)

    # Set legend for estimated clusters
    handles, labels = g2.legend_elements(prop="colors")
    ax[1].legend(handles=handles, labels=labels, title="Cluster")

    # Create contingency table of known groups vs estimated clusters
    contingency = pd.crosstab(
      pd.Series(data[group_var].values, name=group_var),
      pd.Series(cluster_labels, name="KMeansCluster"),
    )
    return fig, ax, cluster_labels, contingency
