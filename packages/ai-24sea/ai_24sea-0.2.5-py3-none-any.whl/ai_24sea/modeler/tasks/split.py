# -*- coding: utf-8 -*-
"""
Utilities for splitting data into training and test sets.

This module defines how to split data into training and test sets. The main
function to be used for the data splitting is ``split``. It works in
combination with configuration files. Specifically for the split step, the main
configuration of interest is the "split" config in which parameters such as the
``test_size`` can be defined.

If a different splitting method is needed, custom code can be passed through the
``split_func`` argument.
"""
from __future__ import annotations

from typing import Any, Callable, Union

import pandas as pd
from prefect import task
from sklearn.model_selection import train_test_split as sklearn_train_test_split

from .. import constants as C
from ..config import validate_config


def split(
    df: pd.DataFrame,
    config: dict[str, Any],
    split_func: Union[Callable, None] = None,
) -> tuple[pd.DataFrame, Union[pd.DataFrame, None]]:
    """
    Split the data into training and test sets.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to be split.
    config : dict[str, Any]
        The full configuration dictionary containing the split configuration
        under the ``"split"`` key.
    split_func : Callable or None, default None
        Optional custom splitting function with the signature
        ``(df: pd.DataFrame, test_size: float, split_config: dict | None)
        -> tuple[pd.DataFrame, pd.DataFrame]``. If ``None``, uses the default
        ``train_test_split`` defined in this module.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame | None]
        A tuple containing the training DataFrame and the test DataFrame.
        If no test set is needed, the second element can be None.
    """
    s_c = config.get("split", {})
    validate_config(s_c, C.SPLIT_CONFIG_KEYS)
    test_size = s_c["test_size"]
    if split_func is None:
        split_func = train_test_split
    train_df, test_df = split_func(df, test_size, s_c)
    return train_df, test_df


@task
def train_test_split(
    df: pd.DataFrame, test_size: float, split_config: dict | None = None
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Define how the data is split into train and test sets.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    test_size : float
        Fraction of the data to allocate to the test set. Must be in ``(0, 1)``.
    split_config : dict or None, default None
        Optional configuration. Supported keys:

        - ``random_state`` (int): Random seed. Default is ``42``.

    Returns
    -------
    train_df : pd.DataFrame
        Training DataFrame.
    test_df : pd.DataFrame
        Test DataFrame.

    Raises
    ------
    TypeError
        If ``df`` is not a pandas DataFrame.
    ValueError
        If ``test_size`` is not between 0 and 1.
    """
    if split_config is None:
        split_config = {}
    random_state = split_config.get("random_state", 42)
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input data must be a pandas DataFrame.")
    if not 0 < test_size < 1:
        raise ValueError("test_size must be between 0 and 1.")

    train_df, test_df = sklearn_train_test_split(
        df, test_size=test_size, random_state=random_state
    )
    return train_df, test_df
