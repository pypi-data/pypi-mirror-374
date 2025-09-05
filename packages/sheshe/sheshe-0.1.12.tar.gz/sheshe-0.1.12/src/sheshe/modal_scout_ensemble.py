from __future__ import annotations
from typing import List, Tuple, Dict, Any, Optional, Sequence, Callable, Self
import logging
import sys
import math, time
import numpy as np
import numpy.typing as npt
import pandas as pd
from pathlib import Path
import joblib

from sklearn.base import BaseEstimator, clone
from sklearn.model_selection import StratifiedKFold, KFold, train_test_split
from sklearn.metrics import accuracy_score, balanced_accuracy_score, r2_score
from sklearn.utils.multiclass import type_of_target

# Importaciones pedidas
from sheshe.subspace_scout import SubspaceScout
from sheshe import ModalBoundaryClustering


# ------------------------
# Utilidades ligeras
# ------------------------

def jaccard_overlap(a: Sequence[int], b: Sequence[int]) -> float:
  A, B = set(a), set(b)
  u = len(A | B)
  return (len(A & B) / u) if u else 0.0

def minmax01(values: Sequence[float], eps: float = 1e-12) -> np.ndarray:
  v = np.asarray(values, dtype=float)
  vmin, vmax = float(np.min(v)), float(np.max(v))
  if math.isclose(vmin, vmax):
    return np.ones_like(v)
  return (v - vmin) / (vmax - vmin + eps)

def infer_task(y) -> str:
  t = type_of_target(y)
  return "classification" if t in ("binary", "multiclass") else "regression"

def ray_count(dim: int, base_2d: int = 8, cap: int = 48) -> int:
  """2D->8 (preferencia de JC). >=3D: ceil(8 * sqrt(d/2)), con tope."""
  if dim <= 2:
    return base_2d
  return int(min(cap, math.ceil(base_2d * math.sqrt(dim / 2.0))))


def pick_slices(
  subspaces: List[Dict[str, Any]],
  *,
  top_k: int = 8,
  min_score: Optional[float] = None,
  max_order: Optional[int] = None,
  metric: Optional[str] = "mi_synergy",
  jaccard_threshold: float = 0.55,
) -> List[Dict[str, Any]]:
  """Filtra por métrica/orden/score y desduplica por Jaccard."""
  cand = [s for s in subspaces if (metric is None or s.get("metric") == metric)]
  if max_order is not None:
    cand = [s for s in cand if s.get("order", len(s["features"])) <= max_order]
  if min_score is not None:
    cand = [s for s in cand if s.get("score", -np.inf) >= min_score]
  cand.sort(key=lambda d: d.get("score", -np.inf), reverse=True)

  chosen: List[Dict[str, Any]] = []
  for s in cand:
    feats = s["features"]
    if not any(jaccard_overlap(feats, c["features"]) >= jaccard_threshold for c in chosen):
      chosen.append(s)
      if top_k is not None and len(chosen) >= top_k:
        break
  return chosen


def extract_global_importances(
  estimator: BaseEstimator,
  X: np.ndarray,
  y: np.ndarray,
  *,
  sample_size: Optional[int] = 4096,
  random_state: Optional[int] = 0,
) -> Optional[np.ndarray]:
  """
  Ajusta un clon del estimator (posible submuestreo) y devuelve
  importancias por feature si existen (feature_importances_ o coef_).
  """
  n = X.shape[0]
  Xs, ys = X, y
  if sample_size is not None and n > sample_size:
    rng = np.random.default_rng(random_state)
    idx = rng.choice(n, size=sample_size, replace=False)
    Xs, ys = X[idx], y[idx]

  est = clone(estimator)
  try:
    est.fit(Xs, ys)
  except Exception:
    return None

  if hasattr(est, "feature_importances_"):
    imp = np.asarray(est.feature_importances_, dtype=float)
  elif hasattr(est, "coef_"):
    coef = np.asarray(est.coef_, dtype=float)
    if coef.ndim == 1:
      imp = np.abs(coef)
    else:
      # multi-clase: suma de magnitudes por feature
      imp = np.sum(np.abs(coef), axis=0)
  else:
    return None

  if imp.ndim != 1:
    return None
  return imp


# ------------------------
# Ensamble principal
# ------------------------

class ModalScoutEnsemble(BaseEstimator):
  """
  Ensamble de ModalBoundaryClustering aplicado SOLO en subespacios valiosos
  hallados por SubspaceScout (ejecutado internamente).  Alternativamente,
  puede delegar en :class:`ShuShu` cuando ``ensemble_method='shushu'``.

  Ponderación por subespacio s (normalizado en [0,1]):
    weight_s ∝ (scout_score_s)^alpha × (cv_score_s)^beta × (feat_importance_s)^gamma

  Donde:
    • scout_score_s = score del SubspaceScout para el subespacio s
    • cv_score_s    = desempeño local del MBC en s (CV u holdout)
    • feat_importance_s = suma (o media) de importancias globales de las features en s

  Parametrización de SubspaceScout:
    Usa 'scout_kwargs' con la firma:
      SubspaceScout(
        model_method=None, max_order=3, n_bins=8, top_m=20, branch_per_parent=5,
        density_occup_min=0.03, min_support=30, sample_size=4096, task='classification',
        random_state=0, base_pairs_limit=12, beam_width=12, extend_candidate_pool=16,
        marginal_gain_min=0.001, max_eval_per_order=1000, time_budget_s=None,
        objective='mi_joint', min_per_order=1
      )

  Parámetros relevantes:
    • ``ensemble_method``: ``'modal_scout'`` (predeterminado) usa la lógica de
      este ensamble basada en ``SubspaceScout``. ``'shushu'`` delega el ajuste
      y la predicción al optimizador :class:`ShuShu`.
    • ``shushu_kwargs``: diccionario de parámetros para ``ShuShu`` cuando se
      utiliza ``ensemble_method='shushu'``.
  """

  __artifact_version__ = "1.0"

  def __init__(
    self,
    *,
    base_estimator,
    task: Optional[str] = None,
    ensemble_method: str = "modal_scout",

    # Selección de subespacios
    top_k: int = 8,
    min_score: Optional[float] = None,
    max_order: Optional[int] = None,
    metric: Optional[str] = "mi_synergy",
    jaccard_threshold: float = 0.55,

    # Ponderación (exponentes)
    alpha: float = 0.5,  # scout
    beta: float = 0.5,   # cv
    gamma: float = 0.5,  # feature_importances (si disponibles)

    # Evaluación local (rápida)
    cv: int | None = 3,                 # 0/None => holdout 80/20
    cv_metric_cls: Callable = balanced_accuracy_score,
    cv_metric_reg: Callable = r2_score,
    cv_floor: Optional[float] = None,   # salta subespacios con CV < floor

    # Rendimiento
    n_jobs: int = 1,
    random_state: Optional[int] = 0,
    base_2d_rays: int = 8,
    ray_cap: int = 48,
    time_budget_s: Optional[float] = None,

    # Importancias globales del base_estimator
    use_importances: bool = True,
    importance_sample_size: Optional[int] = 4096,  # para entrenar imp más rápido

    # Config de SubspaceScout
    scout_kwargs: Optional[Dict[str, Any]] = None,

    # Config de ShuShu
    shushu_kwargs: Optional[Dict[str, Any]] = None,

    # Passthrough a MBC
    mbc_kwargs: Optional[Dict[str, Any]] = None,
    verbose: int = 0,
    prediction_within_region: bool = False,
  ):
    self.base_estimator = base_estimator
    self.task = task
    self.ensemble_method = ensemble_method

    self.top_k = top_k
    self.min_score = min_score
    self.max_order = max_order
    self.metric = metric
    self.jaccard_threshold = jaccard_threshold

    self.alpha = alpha
    self.beta = beta
    self.gamma = gamma

    self.cv = cv
    self.cv_metric_cls = cv_metric_cls
    self.cv_metric_reg = cv_metric_reg
    self.cv_floor = cv_floor

    self.n_jobs = n_jobs
    self.random_state = random_state
    self.base_2d_rays = base_2d_rays
    self.ray_cap = ray_cap
    self.time_budget_s = time_budget_s

    self.use_importances = use_importances
    self.importance_sample_size = importance_sample_size

    self.scout_kwargs = scout_kwargs or {}
    self.shushu_kwargs = shushu_kwargs or {}
    self.mbc_kwargs = mbc_kwargs or {}
    self.verbose = verbose
    self.logger = logging.getLogger(self.__class__.__name__)
    if not self.logger.handlers:
      # Redirigimos a ``stdout`` para compatibilidad con entornos como Colab
      # donde ``stderr`` puede mostrarse por separado o no capturarse.
      self.logger.addHandler(logging.StreamHandler(stream=sys.stdout))
    if verbose >= 2:
      self.logger.setLevel(logging.DEBUG)
    elif verbose == 1:
      self.logger.setLevel(logging.INFO)
    else:
      self.logger.setLevel(logging.WARNING)
    self.prediction_within_region = prediction_within_region

    # Atributos post-fit
    self.selected_: List[Dict[str, Any]] = []
    self.models_: List[ModalBoundaryClustering] = []
    self.features_: List[Tuple[int, ...]] = []
    self.weights_: Optional[np.ndarray] = None
    self.cv_scores_: List[float] = []
    self.scout_scores_: List[float] = []
    self.imp_scores_: List[float] = []
    self.classes_: Optional[np.ndarray] = None
    self.fitted_task_: Optional[str] = None
    self.model_ = None
    self.score_fn_ = None
    self._cache: Dict[str, Any] = {}

  # ---------- internos ----------

  def _mk_mbc_ctor(self, dim: int):
    rays = ray_count(dim, base_2d=self.base_2d_rays, cap=self.ray_cap)
    def ctor():
      return ModalBoundaryClustering(
        base_estimator=clone(self.base_estimator),
        task=self.fitted_task_,
        base_2d_rays=rays,
        random_state=self.random_state,
        **self.mbc_kwargs
      )
    return ctor

  def _precompute_splits(self, y: np.ndarray, task: str):
    """Splits compartidos para ahorrar overhead en CV."""
    if not self.cv or self.cv <= 0:
      return None
    if task == "classification":
      cv = StratifiedKFold(n_splits=self.cv, shuffle=True, random_state=self.random_state)
      return list(cv.split(np.zeros((len(y), 1)), y))
    else:
      cv = KFold(n_splits=self.cv, shuffle=True, random_state=self.random_state)
      return list(cv.split(np.zeros((len(y), 1)), y))

  def _cv_or_holdout_score(self, make_model, Xs: np.ndarray, y: np.ndarray, task: str, splits):
    if splits is None:
      # Holdout 80/20
      if task == "classification":
        X_tr, X_te, y_tr, y_te = train_test_split(
          Xs, y, test_size=0.2, random_state=self.random_state, stratify=y
        )
        m = make_model()
        m.fit(X_tr, y_tr)
        return float(self.cv_metric_cls(y_te, m.predict(X_te)))
      else:
        X_tr, X_te, y_tr, y_te = train_test_split(
          Xs, y, test_size=0.2, random_state=self.random_state
        )
        m = make_model()
        m.fit(X_tr, y_tr)
        return float(self.cv_metric_reg(y_te, m.predict(X_te)))

    # CV k-fold con splits precomputados
    scores = []
    if self.fitted_task_ == "classification":
      scorer = self.cv_metric_cls
    else:
      scorer = self.cv_metric_reg

    for tr, te in splits:
      m = make_model()
      m.fit(Xs[tr], y[tr])
      scores.append(float(scorer(y[te], m.predict(Xs[te]))))
    return float(np.mean(scores)) if scores else 0.0

  # ---------- API sklearn ----------

  def fit(
      self,
      X: npt.NDArray[np.float_] | pd.DataFrame,
      y: npt.NDArray,
      *,
      score_fn: Optional[Callable[[npt.NDArray[np.float_]], npt.NDArray[np.float_]]] = None,
      score_model=None,
  ) -> Self:
    self.score_fn_ = score_fn
    self.model_ = score_model
    if self.ensemble_method.lower() == "shushu":
      from .shushu import ShuShu
      sh_args = dict(random_state=self.random_state)
      sh_args.update(self.shushu_kwargs or {})
      self.shushu_model_ = ShuShu(**sh_args)
      self.shushu_model_.fit(np.asarray(X, dtype=float), y, score_fn=score_fn, score_model=score_model)
      self.fitted_task_ = self.task or infer_task(y)
      if hasattr(self.shushu_model_, "classes_"):
        self.classes_ = np.asarray(self.shushu_model_.classes_)
      if self.prediction_within_region:
        df = self.shushu_model_.predict_regions(X)
        self.labels_ = df["label"].to_numpy()
        self.label2id_ = df["region_id"].to_numpy()
      else:
        self.labels_ = self.shushu_model_.predict(X)
      return self

    t0 = time.time()
    self.fitted_task_ = self.task or infer_task(y)
    if self.fitted_task_ not in ("classification", "regression"):
      raise ValueError(f"Tarea no soportada: {self.fitted_task_}")

    # 1) (Opcional) Importancias globales del base_estimator
    Xs = np.asarray(X, dtype=float)
    global_imp = None
    if self.use_importances:
      global_imp = extract_global_importances(
        self.base_estimator, Xs, y,
        sample_size=self.importance_sample_size,
        random_state=self.random_state,
      )
      if global_imp is not None and len(global_imp) != X.shape[1]:
        # seguridad
        global_imp = None

    # 2) Ejecuta SubspaceScout INTERNAMENTE
    scout_args = dict(
      task=self.fitted_task_,
      random_state=self.random_state,
    )
    # Defaults prácticos: mantener lo pedido, pero deja override por scout_kwargs
    # Si no especificas 'objective', usamos 'mi_synergy' para alinear tu métrica
    scout_args.setdefault("objective", "mi_synergy")
    scout_args.update(self.scout_kwargs or {})

    scout = SubspaceScout(**scout_args)
    subspaces = scout.fit(Xs, y)  # lista de dicts con keys: features, score, metric, order, ...

    # 3) Selección + desduplicación
    self.selected_ = pick_slices(
      subspaces,
      top_k=self.top_k,
      min_score=self.min_score,
      max_order=self.max_order,
      metric=self.metric,
      jaccard_threshold=self.jaccard_threshold,
    )
    if not self.selected_:
      raise ValueError("SubspaceScout no produjo subespacios útiles tras el filtrado.")

    self.models_.clear()
    self.features_.clear()
    self.cv_scores_.clear()
    self.scout_scores_ = [float(s.get("score", 0.0)) for s in self.selected_]
    self.imp_scores_.clear()

    # 4) Precompute CV splits
    splits = self._precompute_splits(y, self.fitted_task_)

    # 5) Entrenamiento por subespacio (paralelizable)
    use_joblib = (self.n_jobs is not None and self.n_jobs != 1)
    if use_joblib:
      try:
        from joblib import Parallel, delayed
      except Exception:
        use_joblib = False

    def _train_one(s: Dict[str, Any]):
      feats = tuple(s["features"])
      Xs_local = Xs[:, feats]  # vista sin copia
      ctor = self._mk_mbc_ctor(dim=len(feats))

      # CV / Holdout local
      cv_s = self._cv_or_holdout_score(ctor, Xs_local, y, self.fitted_task_, splits)

      # early-skip por piso
      if self.cv_floor is not None and cv_s < self.cv_floor:
        return feats, None, cv_s, 0.0

      # Importancia del subespacio (si existe)
      imp_s = 0.0
      if global_imp is not None:
        # suma de importancias de las features del subespacio
        imp_s = float(np.sum(np.abs(global_imp[list(feats)])))

      # Ajuste final
      model = ctor()
      model.fit(Xs_local, y, score_fn=score_fn, score_model=score_model)
      return feats, model, cv_s, imp_s

    if use_joblib:
      from joblib import Parallel, delayed
      results = Parallel(n_jobs=self.n_jobs, prefer="processes")(
        delayed(_train_one)(s) for s in self.selected_
      )
    else:
      results = []
      for s in self.selected_:
        if self.time_budget_s is not None and (time.time() - t0) >= self.time_budget_s:
          self.logger.info("Budget de tiempo alcanzado; se detiene.")
          break
        results.append(_train_one(s))

    # 6) Consolidación
    kept_scout_scores, kept_cv_scores, kept_imp_scores = [], [], []
    for (feats, model, cv_s, imp_s), sc_score in zip(results, self.scout_scores_):
      self.features_.append(feats)
      self.cv_scores_.append(float(cv_s))
      self.imp_scores_.append(float(imp_s))
      if model is not None:
        self.models_.append(model)
        kept_scout_scores.append(sc_score)
        kept_cv_scores.append(float(cv_s))
        kept_imp_scores.append(float(imp_s))

    if not self.models_:
      raise RuntimeError("No se entrenó ningún MBC (p. ej., por cv_floor o budget).")

    # 7) Pesos
    scout_norm = minmax01(kept_scout_scores) if len(kept_scout_scores) else np.ones(len(self.models_))
    cv_norm    = minmax01(kept_cv_scores)    if len(kept_cv_scores)    else np.ones(len(self.models_))

    if np.all(np.asarray(kept_imp_scores) == 0.0) or not self.use_importances:
      imp_norm = np.ones(len(self.models_))
      g = 0.0  # no aportan
    else:
      imp_norm = minmax01(kept_imp_scores)
      g = float(self.gamma)

    a = float(self.alpha)
    b = float(self.beta)
    raw = (scout_norm ** a) * (cv_norm ** b) * (imp_norm ** g)
    denom = float(np.sum(raw)) or 1.0
    self.weights_ = (raw / denom).astype(float)

    # 8) Clases (si clasificación)
    if self.fitted_task_ == "classification":
      c = None
      for m in self.models_:
        if hasattr(m, "classes_"):
          c = np.asarray(m.classes_)
          break
      if c is None:
        c = np.unique(y)
      self.classes_ = c

    # 9) Assign global cluster IDs across all submodels
    self.regions_ = []
    cid = 0
    for mbc in self.models_:
      if hasattr(mbc, "regions_"):
        for reg in mbc.regions_:
          reg.cluster_id = cid
          self.regions_.append(reg)
          cid += 1

    if self.prediction_within_region:
      df = self.predict_regions(X)
      self.labels_ = df["label"].to_numpy()
      self.label2id_ = df["region_id"].to_numpy()
    else:
      self.labels_ = self.predict(X)

    self.logger.info("Submodelos=%d | Pesos≈%s", len(self.models_), np.round(self.weights_, 3))
    return self

  def fit_predict(
      self,
      X: npt.NDArray[np.float_] | pd.DataFrame,
      y: npt.NDArray,
      **fit_kwargs,
  ) -> npt.NDArray[np.int_]:
    """Ajusta el ensamble y devuelve las predicciones para ``X``.

    Equivalente a ejecutar ``fit(X, y)`` seguido de ``predict(X)``.

    Parameters
    ----------
    X : ndarray of shape (n_samples, n_features)
        Datos de entrenamiento.
    y : ndarray of shape (n_samples,)
        Valores objetivo.

    Returns
    -------
    ndarray
        Predicciones del modelo para cada muestra de ``X``.
    """
    self.fit(X, y, **fit_kwargs)
    return self.predict(X)

  def predict_proba(self, X: npt.NDArray[np.float_] | pd.DataFrame) -> npt.NDArray[np.float_]:
    if isinstance(X, pd.DataFrame):
      X = X.to_numpy(dtype=float)
    else:
      X = np.asarray(X, dtype=float)
    if self.ensemble_method.lower() == "shushu":
      if self.fitted_task_ != "classification":
        raise AttributeError("predict_proba solo para clasificación.")
      if not hasattr(self, "shushu_model_"):
        raise RuntimeError("Modelo no ajustado.")
      return self.shushu_model_.predict_proba(X)
    if self.fitted_task_ != "classification":
      raise AttributeError("predict_proba solo para clasificación.")
    if self.classes_ is None:
      raise RuntimeError("Modelo no ajustado.")

    n, k = X.shape[0], len(self.classes_)
    agg = np.zeros((n, k), dtype=float)

    for w, feats, mbc in zip(self.weights_, self.features_, self.models_):
      Xs = X[:, feats]
      if hasattr(mbc, "predict_proba"):
        P = mbc.predict_proba(Xs)
        if P.shape[1] != k:
          subc = getattr(mbc, "classes_", self.classes_)
          P2 = np.zeros((n, k), dtype=float)
          for j, c in enumerate(subc):
            idx = int(np.where(self.classes_ == c)[0][0])
            P2[:, idx] = P[:, j]
          P = P2
      else:
        yhat = mbc.predict(Xs)
        P = np.zeros((n, k), dtype=float)
        for j, c in enumerate(self.classes_):
          P[:, j] = (yhat == c).astype(float)
      agg += w * P

    row_sums = agg.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0.0] = 1.0
    return agg / row_sums

  def predict(self, X: npt.NDArray[np.float_] | pd.DataFrame) -> npt.NDArray[np.int_]:
    if isinstance(X, pd.DataFrame):
      X = X.to_numpy(dtype=float)
    else:
      X = np.asarray(X, dtype=float)
    if self.ensemble_method.lower() == "shushu":
      if not hasattr(self, "shushu_model_"):
        raise RuntimeError("Modelo no ajustado.")
      return self.shushu_model_.predict(X)
    if self.fitted_task_ == "classification":
      P = self.predict_proba(X)
      return self.classes_[np.argmax(P, axis=1)]
    # Regresión: promedio ponderado
    out = None
    for w, feats, mbc in zip(self.weights_, self.features_, self.models_):
      Xs = X[:, feats]
      yhat = mbc.predict(Xs)
      out = (w * yhat) if out is None else (out + w * yhat)
    return out

  def decision_function(
      self, X: npt.NDArray[np.float_] | pd.DataFrame
  ) -> npt.NDArray[np.float_]:
    """Return raw decision scores for ``X``.

    In classification the scores from each submodel are aggregated using the
    corresponding weights. If a submodel lacks ``decision_function`` the method
    falls back to ``predict_proba`` or one-hot predictions. For regression the
    weighted sum of each submodel's decision function (or prediction) is
    returned.
    """

    if self.ensemble_method.lower() == "shushu":
      if not hasattr(self, "shushu_model_"):
        raise RuntimeError("Modelo no ajustado.")
      return self.shushu_model_.decision_function(X)

    if self.weights_ is None:
      raise RuntimeError("Modelo no ajustado.")
    if isinstance(X, pd.DataFrame):
      X = X.to_numpy(dtype=float)
    else:
      X = np.asarray(X, dtype=float)

    if self.fitted_task_ == "classification":
      k = len(self.classes_) if self.classes_ is not None else 0
      agg = None
      for w, feats, mbc in zip(self.weights_, self.features_, self.models_):
        Xs = X[:, feats]
        if hasattr(mbc, "decision_function"):
          S = mbc.decision_function(Xs)
          if S.ndim == 1:
            S = S[:, None]
        elif hasattr(mbc, "predict_proba"):
          S = mbc.predict_proba(Xs)
        else:
          yhat = mbc.predict(Xs)
          S = np.zeros((Xs.shape[0], k), dtype=float)
          for j, c in enumerate(self.classes_):
            S[:, j] = (yhat == c).astype(float)
        if S.shape[1] != k:
          subc = getattr(mbc, "classes_", self.classes_)
          S2 = np.zeros((Xs.shape[0], k), dtype=float)
          for j, c in enumerate(subc):
            idx = int(np.where(self.classes_ == c)[0][0])
            S2[:, idx] = S[:, j]
          S = S2
        agg = w * S if agg is None else agg + w * S
      return agg if agg is not None else np.zeros((X.shape[0], k))

    # Regression
    out = None
    for w, feats, mbc in zip(self.weights_, self.features_, self.models_):
      Xs = X[:, feats]
      if hasattr(mbc, "decision_function"):
        S = mbc.decision_function(Xs)
      else:
        S = mbc.predict(Xs)
      out = w * S if out is None else out + w * S
    return out

  def predict_regions(self, X: npt.NDArray[np.float_] | pd.DataFrame) -> pd.DataFrame:
    """Predicción usando solo modelos cuya región cubre cada muestra."""

    if self.ensemble_method.lower() == "shushu":
      if not hasattr(self, "shushu_model_"):
        raise RuntimeError("Modelo no ajustado.")
      df = self.shushu_model_.predict_regions(X)
      return df

    if self.weights_ is None:
      raise RuntimeError("Modelo no ajustado.")

    if isinstance(X, pd.DataFrame):
      index = X.index
      X = X.to_numpy(dtype=float)
    else:
      index = None
      X = np.asarray(X, dtype=float)
    n = X.shape[0]

    if self.fitted_task_ == "classification":
      labels = np.empty(n, dtype=object)
    else:
      labels = np.full(n, -1.0, dtype=float)
    cluster_ids = np.full(n, -1, dtype=int)

    for i in range(n):
      agg = None
      used_weights = []
      used_ids = []
      for w, feats, mbc in zip(self.weights_, self.features_, self.models_):
        Xi = X[i : i + 1, feats]
        cid_df = mbc.predict_regions(Xi)
        cid_val = int(cid_df["region_id"].iloc[0])
        if cid_val == -1:
          continue
        if self.fitted_task_ == "classification":
          if hasattr(mbc, "predict_proba"):
            P = mbc.predict_proba(Xi)
            if P.shape[1] != len(self.classes_):
              subc = getattr(mbc, "classes_", self.classes_)
              P2 = np.zeros((1, len(self.classes_)), dtype=float)
              for j, c in enumerate(subc):
                idx = int(np.where(self.classes_ == c)[0][0])
                P2[0, idx] = P[0, j]
              P = P2
          else:
            yhat = mbc.predict(Xi)
            P = np.zeros((1, len(self.classes_)), dtype=float)
            for j, c in enumerate(self.classes_):
              P[0, j] = float(yhat[0] == c)
          agg = w * P if agg is None else agg + w * P
        else:
          yhat = mbc.predict(Xi)
          agg = w * yhat if agg is None else agg + w * yhat
        used_weights.append(w)
        used_ids.append(cid_val)

      if used_weights:
        wsum = sum(used_weights)
        if wsum > 0:
          if self.fitted_task_ == "classification":
            probs = agg / wsum
            labels[i] = self.classes_[int(np.argmax(probs))]
          else:
            labels[i] = float(agg / wsum)
          cluster_ids[i] = used_ids[int(np.argmax(used_weights))]
        else:
          labels[i] = -1
          cluster_ids[i] = -1
      else:
        labels[i] = -1
        cluster_ids[i] = -1

    if self.fitted_task_ == "classification":
      labels = labels.astype(int)
    return pd.DataFrame({"label": labels, "region_id": cluster_ids}, index=index)

  def transform(self, X: npt.NDArray[np.float_] | pd.DataFrame) -> npt.NDArray[np.float_]:
    """Feature transformation is not implemented for ModalScoutEnsemble."""
    raise NotImplementedError("ModalScoutEnsemble does not implement transform")

  def fit_transform(
      self,
      X: npt.NDArray[np.float_] | pd.DataFrame,
      y: Optional[npt.NDArray] = None,
      **fit_kwargs: Any,
  ) -> npt.NDArray[np.float_]:
    """Fit the model and transform ``X``.

    Notes
    -----
    This estimator does not implement a transform operation.
    """
    raise NotImplementedError("ModalScoutEnsemble does not implement fit_transform")

  def score(
      self,
      X: npt.NDArray[np.float_] | pd.DataFrame,
      y: npt.NDArray,
      *,
      metric: str | Callable[[npt.NDArray, npt.NDArray], float] = "auto",
      **metric_kwargs: Any,
  ) -> float:
    """Evaluate predictions of ``X`` against ``y``."""
    if metric == "auto":
      metric_fn = accuracy_score if self.fitted_task_ == "classification" else r2_score
      y_pred = self.predict(X)
      return float(metric_fn(y, y_pred, **metric_kwargs))
    if isinstance(metric, str):
      from sklearn.metrics import get_scorer

      scorer = get_scorer(metric)
      return float(scorer(self, X, y))
    y_pred = self.predict(X)
    return float(metric(y, y_pred, **metric_kwargs))

  def save(self, filepath: str | Path) -> None:
    """Persist the ensemble using joblib including version metadata."""
    payload = {"__artifact_version__": self.__artifact_version__, "model": self}
    joblib.dump(payload, filepath)

  @classmethod
  def load(cls, filepath: str | Path) -> "ModalScoutEnsemble":
    """Load a previously saved ensemble."""
    payload = joblib.load(filepath)
    ver = payload.get("__artifact_version__")
    if ver != cls.__artifact_version__:
      raise ValueError(
          f"Artifact version mismatch: expected {cls.__artifact_version__}, got {ver}"
      )
    model = payload.get("model")
    if not isinstance(model, cls):
      raise TypeError("Loaded object is not a ModalScoutEnsemble instance")
    return model

  def summary_tables(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Resumen simple por submodelo y por región."""

    if not self.models_:
      return pd.DataFrame(), pd.DataFrame()
    rows_m: List[Dict[str, Any]] = []
    rows_r: List[Dict[str, Any]] = []
    for idx, (w, mbc) in enumerate(zip(self.weights_, self.models_)):
      regs = getattr(mbc, "regions_", []) or []
      rows_m.append({"model_idx": idx, "n_regions": len(regs), "weight": float(w)})
      for reg in regs:
        rows_r.append({"model_idx": idx, "cluster_id": reg.cluster_id, "label": reg.label})
    return pd.DataFrame(rows_m), pd.DataFrame(rows_r)

  def report(self) -> List[Dict[str, Any]]:
    """Resumen por subespacio (ordenado por peso)."""
    if self.ensemble_method.lower() == "shushu":
      if not hasattr(self, "shushu_model_"):
        raise RuntimeError("Modelo no ajustado.")
      info: List[Dict[str, Any]] = []
      if hasattr(self.shushu_model_, "per_class_") and self.shushu_model_.per_class_:
        for pc in self.shushu_model_.per_class_.values():
          clus = pc.get("clusterer")
          if clus is not None and hasattr(clus, "clusters_"):
            info.extend(clus.clusters_)
      elif hasattr(self.shushu_model_, "clusters_"):
        info = list(self.shushu_model_.clusters_)
      return info
    info = []
    # Solo reportamos para los modelos realmente entrenados
    for idx, (w, feats, mbc) in enumerate(zip(self.weights_, self.features_, self.models_)):
      s = self.selected_[idx] if idx < len(self.selected_) else {}
      row = {
        "features": feats,
        "order": s.get("order", len(feats)),
        "metric": s.get("metric"),
        "scout_score": float(s.get("score", 0.0)),
        "cv_score": float(self.cv_scores_[idx]) if idx < len(self.cv_scores_) else None,
        "feat_importance": float(self.imp_scores_[idx]) if idx < len(self.imp_scores_) else None,
        "weight": float(w),
        "cluster_ids": [reg.cluster_id for reg in getattr(mbc, "regions_", [])],
      }
      for attr in ("regions_", "rules_", "segments_", "boundaries_", "feature_importances_"):
        if hasattr(mbc, attr):
          row[attr] = getattr(mbc, attr)
      info.append(row)
    info.sort(key=lambda d: d["weight"], reverse=True)
    return info

  # ---------- Visualización ----------

  def _get_submodel(self, model_idx: int = 0) -> Tuple[ModalBoundaryClustering, Tuple[int, ...]]:
    """Retorna el submodelo y las features asociadas.

    Parameters
    ----------
    model_idx : int, default=0
        Índice del submodelo dentro del ensamble.
    """
    if not self.models_:
      raise RuntimeError("Modelo no ajustado.")
    if not (0 <= model_idx < len(self.models_)):
      raise IndexError("model_idx fuera de rango.")
    return self.models_[model_idx], self.features_[model_idx]

  def get_frontier(self, model_idx: int, cluster_id: int, dims: Sequence[int]) -> np.ndarray:
    """Recupera la frontera de un submodelo para un par de features globales."""

    mbc, feats = self._get_submodel(model_idx)
    feat_map = {f: i for i, f in enumerate(feats)}
    dims_local = [feat_map[d] for d in dims]
    return mbc.get_frontier(cluster_id, dims_local)

  def plot_pairs(
    self,
    X: np.ndarray,
    y: Optional[np.ndarray] = None,
    *,
    model_idx: int = 0,
    max_pairs: Optional[int] = None,
    feature_names: Optional[Sequence[str]] = None,
    block_size: Optional[int] = None,
    max_classes: Optional[int] = None,
    show_histograms: bool = False,
  ) -> None:
    """Visualiza superficies 2D para un submodelo específico.

    Esta función delega en :meth:`ModalBoundaryClustering.plot_pairs`, por lo
    que acepta los mismos parámetros, añadiendo ``model_idx`` para seleccionar
    el submodelo dentro del ensamble.
    ``feature_names`` permite especificar nombres globales de las features,
    que se ajustarán al subespacio del modelo elegido.
    ``show_histograms`` permite dibujar histogramas marginales en cada gráfico.
    """
    mbc, feats = self._get_submodel(model_idx)
    feats_list = list(feats)
    if hasattr(X, "iloc"):
      Xs = X.iloc[:, feats_list]
    else:
      Xs = np.asarray(X)[:, feats_list]
    sub_names: Optional[Sequence[str]]
    if feature_names is not None:
      sub_names = [feature_names[f] for f in feats_list]
    else:
      sub_names = None
    mbc.plot_pairs(
      Xs,
      y,
      max_pairs=max_pairs,
      feature_names=sub_names,
      block_size=block_size,
      max_classes=max_classes,
      show_histograms=show_histograms,
    )

  def plot_classes(self, X: np.ndarray, y: np.ndarray, **kwargs):
    """Atajo que delega en :meth:`plot_pairs` para compatibilidad."""

    return self.plot_pairs(X, y=y, **kwargs)

  def plot_pair_3d(
    self,
    X: np.ndarray,
    pair: Tuple[int, int],
    *,
    model_idx: int = 0,
    feature_names: Optional[Sequence[str]] = None,
    **kwargs: Any,
  ):
    """Superficie 3D de probabilidad/valor predicho para un submodelo.

    Parameters
    ----------
    X : ndarray of shape (n_samples, n_features)
        Datos usados para definir el rango de los ejes.
    pair : tuple of int
        Índices globales ``(i, j)`` de las features a visualizar.
    model_idx : int, default=0
        Submodelo dentro del ensamble a utilizar.
    feature_names : sequence of str, optional
        Nombres globales de las features. Se extraerán los correspondientes al
        submodelo antes de delegar en :meth:`ModalBoundaryClustering.plot_pair_3d`.
    **kwargs : dict
        Parámetros adicionales pasados a
        :meth:`ModalBoundaryClustering.plot_pair_3d`.
    """
    mbc, feats = self._get_submodel(model_idx)
    feats_list = list(feats)
    if pair[0] not in feats_list or pair[1] not in feats_list:
      raise ValueError("pair debe pertenecer a las features del submodelo")
    local_pair = (feats_list.index(pair[0]), feats_list.index(pair[1]))
    if hasattr(X, "iloc"):
      Xs = X.iloc[:, feats_list]
    else:
      Xs = np.asarray(X)[:, feats_list]
    sub_names: Optional[Sequence[str]]
    if feature_names is not None:
      sub_names = [feature_names[f] for f in feats_list]
    else:
      sub_names = None
    return mbc.plot_pair_3d(Xs, local_pair, feature_names=sub_names, **kwargs)

  # ---------- Interpretabilidad ----------

  def interpretability_summary(
    self,
    X: npt.NDArray[np.float_] | pd.DataFrame,
    y: Optional[npt.NDArray] = None,
    *,
    per_model: bool = False,
    top_k: int = 10,
  ) -> pd.DataFrame:
    """Provide a lightweight interpretability summary.

    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        Dataset used to evaluate regional dominance/purity.
    y : array-like of shape (n_samples,), optional
        Ground truth labels.  When provided, per-model purity is computed.
    per_model : bool, default=False
        When ``True`` returns one row per submodel (limited by ``top_k``) plus
        an aggregate weighted row.  Otherwise only the aggregate row is
        returned.
    top_k : int, default=10
        Maximum number of submodels to include in the summary.

    Returns
    -------
    DataFrame
        Table with columns ``['model_id', 'feature_importances',
        'region_dominance', 'support', 'purity', 'weight']``.  The last row
        corresponds to the weighted aggregate of the shown submodels.
    """

    if self.ensemble_method.lower() == "shushu":
      if not hasattr(self, "shushu_model_"):
        raise RuntimeError("Modelo no ajustado.")
      # Delegamos a ShuShu; compatibilidad básica.
      return self.shushu_model_.interpretability_summary()

    if isinstance(X, pd.DataFrame):
      X_arr = X.to_numpy(dtype=float)
    else:
      X_arr = np.asarray(X, dtype=float)
    y_arr = None if y is None else np.asarray(y)

    rows: List[Dict[str, Any]] = []
    n_models = len(self.models_)
    # Recogemos métricas por submodelo
    for idx, (w, feats, mbc) in enumerate(zip(self.weights_, self.features_, self.models_)):
      feats_list = list(feats)
      Xs = X_arr[:, feats_list]
      try:
        df = mbc.predict_regions(Xs)
        rids = df["region_id"].to_numpy()
        labels = df["label"].to_numpy()
      except Exception:
        # Fallback: uso de predict si predict_regions no está disponible
        rids = np.full(X_arr.shape[0], -1, dtype=int)
        labels = mbc.predict(Xs)
      mask = rids != -1
      support = float(mask.mean())
      if np.any(mask):
        unique, counts = np.unique(rids[mask], return_counts=True)
        region_dom = float(np.max(counts)) / rids.size
      else:
        region_dom = 0.0
      if y_arr is not None and np.any(mask):
        if self.fitted_task_ == "classification":
          purity = float(accuracy_score(y_arr[mask], labels[mask]))
        else:
          purity = float(r2_score(y_arr[mask], labels[mask]))
      else:
        purity = float("nan")
      imp = float(self.imp_scores_[idx]) if idx < len(self.imp_scores_) else float("nan")
      rows.append(
        {
          "model_id": idx,
          "feature_importances": imp,
          "region_dominance": region_dom,
          "support": support,
          "purity": purity,
          "weight": float(w),
        }
      )

    rows.sort(key=lambda r: r["weight"], reverse=True)
    if top_k is not None:
      rows = rows[:top_k]

    # Agregado ponderado por pesos
    if rows:
      total_w = float(np.sum([r["weight"] for r in rows])) or 1.0

      def wavg(key: str) -> float:
        vals = np.array([r[key] for r in rows], dtype=float)
        wts = np.array([r["weight"] for r in rows], dtype=float)
        mask = np.isfinite(vals)
        if not np.any(mask):
          return float("nan")
        return float(np.sum(vals[mask] * wts[mask]) / np.sum(wts[mask]))

      agg_row = {
        "model_id": "aggregate",
        "feature_importances": wavg("feature_importances"),
        "region_dominance": wavg("region_dominance"),
        "support": wavg("support"),
        "purity": wavg("purity"),
        "weight": total_w,
      }
      rows.append(agg_row)

    df_out = pd.DataFrame(rows)
    if per_model:
      return df_out
    return df_out[df_out["model_id"] == "aggregate"].reset_index(drop=True)
