import argparse
import json
import os
import sys
import pickle
from typing import Tuple, List

import numpy as np
import pandas as pd

try:
    import deepchem as dc
except Exception as exc:  # pragma: no cover
    print("Failed to import deepchem. Please ensure the environment matches your notebooks.", file=sys.stderr)
    raise

from sklearn.feature_selection import VarianceThreshold


def _project_root() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def _models_dir() -> str:
    return os.path.join(_project_root(), "models")


def _data_dir() -> str:
    return os.path.join(_project_root(), "data")


def featurize_with_training_mask(
    featname: str,
    training_df: pd.DataFrame,
    smiles: str,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Replicates the featurization from the notebook:
    - Fit VarianceThreshold on training features
    - Apply the learned mask to the input SMILES
    Returns (training_selected, input_selected)
    """
    if featname == "MACCS":
        featurizer = dc.feat.MACCSKeysFingerprint()
        train_features = featurizer.featurize(training_df["smiles"])
        input_features = featurizer.featurize([smiles])
    elif featname == "RDkit":
        featurizer = dc.feat.RDKitDescriptors()
        train_features = featurizer.featurize(training_df["smiles"])
        input_features = featurizer.featurize([smiles])
    else:
        raise ValueError("Unsupported feature type: {}".format(featname))

    vt = VarianceThreshold(threshold=(0.98 * (1 - 0.98)))
    training_selected = vt.fit_transform(train_features)
    mask_indices = vt.get_support(indices=True)
    input_selected = input_features[:, mask_indices]

    return training_selected, input_selected


def build_feature_selectors(training_df: pd.DataFrame):
    """
    Fit featurizers and variance threshold selectors on training data once
    and return callable that transforms a list of SMILES into selected features.
    """
    # MACCS
    maccs_featurizer = dc.feat.MACCSKeysFingerprint()
    maccs_train_features = maccs_featurizer.featurize(training_df["smiles"])
    vt_maccs = VarianceThreshold(threshold=(0.98 * (1 - 0.98)))
    vt_maccs.fit(maccs_train_features)
    maccs_indices = vt_maccs.get_support(indices=True)

    # RDKit descriptors
    rdkit_featurizer = dc.feat.RDKitDescriptors()
    rdkit_train_features = rdkit_featurizer.featurize(training_df["smiles"])
    vt_rdkit = VarianceThreshold(threshold=(0.98 * (1 - 0.98)))
    vt_rdkit.fit(rdkit_train_features)
    rdkit_indices = vt_rdkit.get_support(indices=True)

    def transform_input(smiles_list: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        maccs_input = maccs_featurizer.featurize(smiles_list)
        rdkit_input = rdkit_featurizer.featurize(smiles_list)
        maccs_selected = maccs_input[:, maccs_indices]
        rdkit_selected = rdkit_input[:, rdkit_indices]
        return maccs_selected, rdkit_selected

    return transform_input


def load_models(models_path: str):
    paths = {
        "rf_maccs": os.path.join(models_path, "rf_maccs_model.pkl"),
        "rf_rdkit": os.path.join(models_path, "rf_rdkit_model.pkl"),
        "svm_maccs": os.path.join(models_path, "svm_maccs_model.pkl"),
        "xgb_maccs": os.path.join(models_path, "xgb_maccs_model.pkl"),
        "stacking": os.path.join(models_path, "stacking_model.pkl"),
    }

    models = {}
    for key, path in paths.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        with open(path, "rb") as f:
            models[key] = pickle.load(f)
    return models


def predict_smiles(smiles: str) -> dict:
    # Load training data to reproduce the same feature selection masks
    data_csv = os.path.join(_data_dir(), "GABAA.csv")
    if not os.path.exists(data_csv):
        raise FileNotFoundError(f"Training data not found: {data_csv}")

    training_df = pd.read_csv(data_csv, encoding="gb18030")
    if "smiles" not in training_df.columns:
        # Fallback common capitalization
        if "SMILES" in training_df.columns:
            training_df = training_df.rename(columns={"SMILES": "smiles"})
        else:
            raise ValueError("Training CSV must contain a 'smiles' column")

    # Featurize using the exact approach from the notebook
    _, input_maccs = featurize_with_training_mask("MACCS", training_df, smiles)
    _, input_rdkit = featurize_with_training_mask("RDkit", training_df, smiles)

    # NaN guard (rare, but defensive)
    if np.isnan(input_rdkit).any() or np.isnan(input_maccs).any():
        raise ValueError("Generated features contain NaN. Please verify the input SMILES is valid.")

    models = load_models(_models_dir())

    # First-level predictions (probabilities)
    rf_maccs_pred = models["rf_maccs"].predict_proba(input_maccs)
    rf_rdkit_pred = models["rf_rdkit"].predict_proba(input_rdkit)
    svm_maccs_pred = models["svm_maccs"].predict_proba(input_maccs)
    xgb_maccs_pred = models["xgb_maccs"].predict_proba(input_maccs)

    stacking_input = np.concatenate(
        (rf_maccs_pred, rf_rdkit_pred, svm_maccs_pred, xgb_maccs_pred), axis=1
    )

    stacking_pred = models["stacking"].predict(stacking_input)
    stacking_proba = models["stacking"].predict_proba(stacking_input)

    # Probability of the positive class assumed to be at index 1 (as in the notebook)
    pos_proba = float(stacking_proba[0][1]) if stacking_proba.shape[1] > 1 else float(stacking_proba[0][0])
    label = int(stacking_pred[0])

    return {
        "smiles": smiles,
        "prediction": label,
        "probability": pos_proba,
        "details": {
            "rf_maccs_proba": rf_maccs_pred.tolist(),
            "rf_rdkit_proba": rf_rdkit_pred.tolist(),
            "svm_maccs_proba": svm_maccs_pred.tolist(),
            "xgb_maccs_proba": xgb_maccs_pred.tolist(),
        },
    }


def predict_csv(
    csv_path: str,
    output_path: str,
    smiles_column: str = "smiles",
    input_encoding: str = "utf-8",
) -> None:
    """
    Batch prediction for a CSV containing a SMILES column. Writes a result CSV.
    Output columns: smiles, prediction, probability, and base-model probabilities.
    """
    # Load input
    input_df = pd.read_csv(csv_path, encoding=input_encoding)
    if smiles_column not in input_df.columns:
        raise ValueError(f"Input CSV must contain column '{smiles_column}'")
    smiles_list = input_df[smiles_column].astype(str).tolist()

    # Load training data and models once
    data_csv = os.path.join(_data_dir(), "GABAA.csv")
    if not os.path.exists(data_csv):
        raise FileNotFoundError(f"Training data not found: {data_csv}")
    training_df = pd.read_csv(data_csv, encoding="gb18030")
    if "smiles" not in training_df.columns:
        if "SMILES" in training_df.columns:
            training_df = training_df.rename(columns={"SMILES": "smiles"})
        else:
            raise ValueError("Training CSV must contain a 'smiles' column")

    transform_input = build_feature_selectors(training_df)
    input_maccs, input_rdkit = transform_input(smiles_list)

    if np.isnan(input_rdkit).any() or np.isnan(input_maccs).any():
        raise ValueError("Generated features contain NaN. Please verify input SMILES values are valid.")

    models = load_models(_models_dir())

    # Base model probabilities (batch)
    rf_maccs_pred = models["rf_maccs"].predict_proba(input_maccs)
    rf_rdkit_pred = models["rf_rdkit"].predict_proba(input_rdkit)
    svm_maccs_pred = models["svm_maccs"].predict_proba(input_maccs)
    xgb_maccs_pred = models["xgb_maccs"].predict_proba(input_maccs)

    stacking_input = np.concatenate(
        (rf_maccs_pred, rf_rdkit_pred, svm_maccs_pred, xgb_maccs_pred), axis=1
    )
    stacking_pred = models["stacking"].predict(stacking_input)
    stacking_proba = models["stacking"].predict_proba(stacking_input)

    # Prepare output DataFrame
    # Assume positive class probability is column 1 when available
    pos_proba = (
        stacking_proba[:, 1] if stacking_proba.shape[1] > 1 else stacking_proba[:, 0]
    )

    result_df = pd.DataFrame(
        {
            "smiles": smiles_list,
            "probability": pos_proba.astype(float),
        }
    )

    # Preserve original columns alongside results
    merged = input_df.copy()
    merged = pd.concat([merged.reset_index(drop=True), result_df.reset_index(drop=True)], axis=1)
    merged.to_csv(output_path, index=False)


def main():
    parser = argparse.ArgumentParser(
        description="Predict activity for an input SMILES using the trained stacking model."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--smiles", help="Input SMILES string")
    group.add_argument("--csv", help="Path to a CSV file containing SMILES for batch prediction")
    parser.add_argument("--out", help="Output CSV path for batch prediction (required if --csv is used)")
    parser.add_argument("--smiles-column", default="smiles", help="SMILES column name in input CSV (default: smiles)")
    parser.add_argument("--input-encoding", default="utf-8", help="Encoding of input CSV (default: utf-8)")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print full JSON output (includes base model probabilities)",
    )
    args = parser.parse_args()

    try:
        if args.csv:
            if not args.out:
                raise ValueError("--out is required when using --csv for batch prediction")
            predict_csv(
                csv_path=args.csv,
                output_path=args.out,
                smiles_column=args.smiles_column,
                input_encoding=args.input_encoding,
            )
            print(f"Wrote predictions to: {args.out}")
            return
        # single SMILES mode
        result = predict_smiles(args.smiles)
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"SMILES: {result['smiles']}")
        print(f"Prediction (label): {result['prediction']}")
        print(f"Probability (positive class): {result['probability']:.6f}")


if __name__ == "__main__":
    main()


