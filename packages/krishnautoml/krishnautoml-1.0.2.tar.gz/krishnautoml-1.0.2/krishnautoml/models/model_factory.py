from __future__ import annotations
from typing import Dict, Optional, List

from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from ..utils.helpers import safe_import_lightgbm, safe_import_xgboost


class ModelFactory:
    def __init__(
        self, problem_type: str, random_state: int = 42, max_rf_samples: int = 50000
    ) -> None:
        if problem_type not in {"classification", "regression"}:
            raise ValueError("problem_type must be 'classification' or 'regression'")
        self.problem_type = problem_type
        self.random_state = random_state
        self.max_rf_samples = max_rf_samples  # max dataset size to allow RF

    def get_models(
        self, X=None, include: Optional[List[str]] = None
    ) -> Dict[str, object]:
        """
        X: pd.DataFrame or None — used to check dataset size
        """
        include = set(m.lower() for m in include) if include else None

        models: Dict[str, object] = {}

        # Check dataset size (number of rows)
        n_samples = len(X) if X is not None else None

        def allow_rf():
            # Only allow RandomForest if dataset is small enough
            if n_samples is None:
                return True
            return n_samples <= self.max_rf_samples

        if self.problem_type == "classification":
            if include is None or "logreg" in include:
                models["logreg"] = LogisticRegression

            if (
                include is None or "rf" in include or "randomforest" in include
            ) and allow_rf():
                models["random_forest"] = RandomForestClassifier

            xgb_cls = safe_import_xgboost(task="cls", random_state=self.random_state)
            if xgb_cls and (
                include is None or "xgb" in include or "xgboost" in include
            ):
                models["xgboost"] = xgb_cls

            lgbm_cls = safe_import_lightgbm(task="cls", random_state=self.random_state)
            if lgbm_cls and (
                include is None or "lgbm" in include or "lightgbm" in include
            ):
                models["lightgbm"] = lgbm_cls

        else:  # regression
            if include is None or "linreg" in include or "linear" in include:
                models["linear"] = LinearRegression

            if (
                include is None or "rf" in include or "randomforest" in include
            ) and allow_rf():
                models["random_forest"] = RandomForestRegressor

            xgb_reg = safe_import_xgboost(task="reg", random_state=self.random_state)
            if xgb_reg and (
                include is None or "xgb" in include or "xgboost" in include
            ):
                models["xgboost"] = xgb_reg

            lgbm_reg = safe_import_lightgbm(task="reg", random_state=self.random_state)
            if lgbm_reg and (
                include is None or "lgbm" in include or "lightgbm" in include
            ):
                models["lightgbm"] = lgbm_reg

        if not models:
            raise RuntimeError(
                "No models available. Check your 'include' filter or install optional libs."
            )
        return models
