import optuna
import numpy as np
import inspect
import logging
from sklearn.model_selection import (
    cross_val_score,
    KFold,
    StratifiedKFold,
    train_test_split,
)
import warnings

warnings.filterwarnings("ignore", category=UserWarning)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


class Tuner:
    def __init__(self, n_trials=20, cv=5, use_optuna=True, random_state=42):
        self.n_trials = n_trials
        self.cv = cv
        self.use_optuna = use_optuna
        self.random_state = random_state

    def run(self, candidates, X, y, problem_type="auto"):
        results = {}
        best_score = -np.inf
        best_model = None

        cv_strategy = (
            StratifiedKFold(
                n_splits=self.cv, shuffle=True, random_state=self.random_state
            )
            if problem_type == "classification"
            else KFold(n_splits=self.cv, shuffle=True, random_state=self.random_state)
        )

        for name, model_cls in candidates.items():
            logger.info(f"Tuning {name}...")

            if self.use_optuna:
                direction = (
                    "maximize" if problem_type == "classification" else "minimize"
                )
                study = optuna.create_study(direction=direction)
                study.optimize(
                    lambda trial: self._objective(
                        trial, model_cls, X, y, cv_strategy, problem_type
                    ),
                    n_trials=self.n_trials,
                )

                best_params = study.best_params
                model_init_params = inspect.signature(model_cls.__init__).parameters

                if "random_state" in model_init_params:
                    model = model_cls(**best_params, random_state=self.random_state)
                else:
                    model = model_cls(**best_params)
            else:
                if "random_state" in inspect.signature(model_cls).parameters:
                    model = model_cls(random_state=self.random_state)
                else:
                    model = model_cls()

            scoring = "accuracy" if problem_type == "classification" else "r2"
            scores = cross_val_score(model, X, y, cv=cv_strategy, scoring=scoring)
            mean_score = np.mean(scores)
            results[name] = {"score": mean_score}

            if mean_score > best_score:
                best_score = mean_score
                best_model = model.fit(X, y)

        logger.info(f"Best model: {type(best_model).__name__} (CV={best_score:.4f})")
        return results, best_model

    def _objective(self, trial, model_cls, X, y, cv, problem_type):
        model_name = model_cls.__name__.lower()
        logger.info(f"Starting Trial {trial.number} for {model_name}")
        params = {}

        if model_name == "linearregression":
            model = model_cls()
            score = np.mean(cross_val_score(model, X, y, cv=cv, scoring="r2", n_jobs=1))

            return score

        if "randomforest" in model_name:
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 50, 150),
                "max_depth": trial.suggest_int("max_depth", 5, 15),
                "n_jobs": 1,
            }

            if "random_state" in inspect.signature(model_cls.__init__).parameters:
                params["random_state"] = self.random_state

            model = model_cls(**params)
            scoring = "accuracy" if problem_type == "classification" else "r2"

            try:
                scores = cross_val_score(model, X, y, cv=cv, scoring=scoring, n_jobs=1)
                result = np.mean(scores)
                return result
            except Exception as e:
                logger.error(f"[Trial {trial.number}] Error during trial: {e}")
                return -9999

        elif "xgb" in model_name or "xgboost" in model_name:
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 50, 300),
                "max_depth": trial.suggest_int("max_depth", 3, 15),
                "learning_rate": trial.suggest_float(
                    "learning_rate", 0.01, 0.3, log=True
                ),
                "subsample": trial.suggest_float("subsample", 0.5, 1.0),
                'use_gpu': False,
                
                "verbosity": 0,
            }

            model = model_cls(**params)

            X_train, X_val, y_train, y_val = train_test_split(
                X,
                y,
                test_size=0.2,
                random_state=self.random_state,
                stratify=y if problem_type == "classification" else None,
            )

            model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

            if hasattr(model, "best_score_") and model.best_score_ is not None:
                return model.best_score_
            else:
                from sklearn.metrics import roc_auc_score, r2_score

                y_pred = model.predict(X_val)
                if problem_type == "classification":
                    return roc_auc_score(y_val, y_pred)
                else:
                    return r2_score(y_val, y_pred)

        elif "lgbm" in model_name or "lightgbm" in model_name:
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 50, 300),
                "max_depth": trial.suggest_int("max_depth", -1, 20),
                "learning_rate": trial.suggest_float(
                    "learning_rate", 0.01, 0.3, log=True
                ),
                "subsample": trial.suggest_float("subsample", 0.5, 1.0),
                "min_gain_to_split": trial.suggest_float("min_gain_to_split", 0, 1.0),
                "verbose": -1,
                "device": "cpu",
            }

            if problem_type == "classification":
                pruning_metric = "auc"
                eval_metric = ["auc", "binary_logloss"]
            else:
                pruning_metric = "l2"
                eval_metric = ["l2"]

            X_train, X_val, y_train, y_val = train_test_split(
                X,
                y,
                test_size=0.2,
                random_state=self.random_state,
                stratify=y if problem_type == "classification" else None,
            )

            model = model_cls(**params)

            model.fit(
                X_train,
                y_train,
                eval_set=[(X_val, y_val)],
                eval_metric=eval_metric,
                callbacks=[
                    optuna.integration.LightGBMPruningCallback(trial, pruning_metric)
                ],
            )

            booster = model.booster_
            eval_results = booster.best_score

            return eval_results["valid_0"][pruning_metric]

        model_init_params = inspect.signature(model_cls.__init__).parameters
        if "random_state" in model_init_params:
            params["random_state"] = self.random_state

        model = model_cls(**params)
        scoring = "accuracy" if problem_type == "classification" else "r2"
        scores = cross_val_score(model, X, y, cv=cv, scoring=scoring)
        return np.mean(scores)
