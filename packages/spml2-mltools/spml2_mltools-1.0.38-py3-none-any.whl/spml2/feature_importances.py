from abc import ABC, abstractmethod
from typing import Any
import numpy as np
import pandas as pd

from .utils import local_print, local_print_df
from .options import Options


class FeatureImportancesAbstract(ABC):
    def __init__(self, output_area=None):
        self.output_area = output_area

    @abstractmethod
    def get(self, model, X_test, y_test, features):
        pass

    def display_df(self, importances: pd.DataFrame):
        if self.output_area is not None:
            if isinstance(importances, pd.DataFrame):
                local_print(
                    f"Feature importances found with {self.__class__.__name__} method.",
                    output_area=self.output_area,
                )
                local_print_df(importances, output_area=self.output_area)
            elif isinstance(importances, (tuple, list)):
                local_print(
                    f"Feature importances found with {self.__class__.__name__} method.",
                    output_area=self.output_area,
                )
                local_print_df(pd.DataFrame(importances), output_area=self.output_area)
            else:
                ...


class FeatureImportancesBasic(FeatureImportancesAbstract):
    def get(self, best_model, X_test, y_test, features):
        importances = getattr(
            best_model.named_steps["model"], "feature_importances_", None
        )
        self.display_df(importances)
        return importances


class FeatureImportancesSKLEARN(FeatureImportancesAbstract):
    def get(self, model, X_test, y_test, features):
        from sklearn.inspection import permutation_importance

        result = permutation_importance(
            model, X_test, y_test, n_repeats=10, random_state=42
        )
        importances = result.importances_mean
        feature_importances = pd.DataFrame(
            {"features": features, "importances": importances}
        )
        self.display_df(feature_importances)
        return feature_importances


def get_feature_importances(model, X_test, y_test, features):
    from sklearn.inspection import permutation_importance

    result = permutation_importance(
        model, X_test, y_test, n_repeats=10, random_state=42
    )
    importances = result.importances_mean
    feature_importances = pd.DataFrame(
        {"features": features, "importances": importances}
    )
    return feature_importances


def save_feature_importances_basic(
    best_model: Any,
    options: Options,
    result_name: str,
    features: list,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    output_area=None,
):
    importances = FeatureImportancesBasic(output_area).get(best_model, None, None, None)
    result_name = f"feature_importances_basic_{result_name}"

    if isinstance(importances, np.ndarray):
        if importances.shape[0] != len(features):
            print(f"Warning: importances shape {importances.shape} does not match number of features {len(features)}")
            return   
        feature_importances = pd.DataFrame({"features": features, "importances": importances})
        return save_feature_df(feature_importances, result_name, options)

    
    if isinstance(importances, pd.DataFrame):
       return save_feature_df(importances, result_name, options)

    if importances is not None:
        feature_importances = pd.DataFrame(
            {"features": features, "importances": importances}
        )

        return save_feature_df(feature_importances, result_name, options)
    else:
        print(f"Model {result_name} does not have feature_importances_ attribute.")


def save_feature_importances_SKLEARN(
    best_model: Any,
    options: Options,
    result_name: str,
    features: list,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    output_area=None,
):
    importances = FeatureImportancesSKLEARN(output_area).get(
        best_model, X_test, y_test, features
    )
    result_name = f"feature_importances_SKLEARN_{result_name}"
    if isinstance(importances, pd.DataFrame):
        return save_feature_df(importances, result_name, options)
    if isinstance(importances, (tuple, list)):
        feature_importances = pd.DataFrame(
            {"features": features, "importances": importances}
        )
        return save_feature_df(feature_importances, result_name, options)
    print(" Feature importances was not found with SKLEARN")


def save_feature_df(feat_df, result_name, options):
    if "importances" in feat_df.columns: 
        feat_df = feat_df.sort_values(by="importances", ascending=False)
    print(f"Saving feature importances for {result_name}...")
    local_print_df(feat_df)
    feat_df.to_excel(
        options.output_folder / f"{result_name}.xlsx",
        index=False,
    )


def save_feature_importances(
    best_model:Any, options:Options, result_name:str, features:list, X_test:pd.DataFrame, y_test:pd.Series, output_area=None
):
    fncs = [save_feature_importances_SKLEARN  ] # save_feature_importances_basic
    if options._dev : 
        fncs = [save_feature_importances_SKLEARN ,save_feature_importances_basic ] # 
    
    for fnc in fncs:
        try:
            fnc(
                best_model,
                options,
                result_name,
                features,
                X_test,
                y_test,
                output_area=output_area,
            )
        except Exception as e:
            if options.raise_error and options.debug and options._dev :
                
               raise e
            
