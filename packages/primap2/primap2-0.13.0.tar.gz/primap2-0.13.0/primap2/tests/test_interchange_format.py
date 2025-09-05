"""Tests for the interchange format."""

import csv
import importlib
import importlib.resources

import pandas as pd
import pytest
import xarray as xr

import primap2
from primap2 import pm2io

from . import utils


def test_round_trip(any_ds: xr.Dataset, tmp_path):
    path = tmp_path / "if"
    pm2io.write_interchange_format(path, any_ds.pr.to_interchange_format())
    with path.with_suffix(".yaml").open() as fd:
        print(fd.read())
    actual = pm2io.from_interchange_format(pm2io.read_interchange_format(path))
    # we expect that Processing information is lost here
    expected = any_ds
    to_remove = []
    for var in expected:
        if (
            isinstance(var, str)
            and var.startswith("Processing of ")
            and "described_variable" in expected[var].attrs
        ):
            to_remove.append(var)
    for var in to_remove:
        del expected[var]
    utils.assert_ds_aligned_equal(any_ds, actual)


def test_missing_file(minimal_ds, tmp_path):
    path = tmp_path / "if"
    pm2io.write_interchange_format(path, minimal_ds.pr.to_interchange_format())
    with path.with_suffix(".yaml").open() as fd:
        content = fd.readlines()
    with path.with_suffix(".yaml").open("w") as fd:
        for line in content:
            if "data_file" in line:
                continue
            fd.write(line)

    # first test automatic discovery
    actual = pm2io.from_interchange_format(pm2io.read_interchange_format(path))
    utils.assert_ds_aligned_equal(minimal_ds, actual)

    # now test without csv file
    path.with_suffix(".csv").unlink()
    with pytest.raises(FileNotFoundError, match="Data file not found at"):
        pm2io.read_interchange_format(path)


def test_inharmonic_units(minimal_ds, tmp_path):
    path = tmp_path / "if"
    pm2io.write_interchange_format(path, minimal_ds.pr.to_interchange_format())
    df = pd.read_csv(path.with_suffix(".csv"))
    df.loc[3, "unit"] = "m"
    df.to_csv(path.with_suffix(".csv"), index=False, quoting=csv.QUOTE_NONNUMERIC)

    with pytest.raises(ValueError, match="More than one unit"):
        pm2io.from_interchange_format(pm2io.read_interchange_format(path))


def test_stable_sorting(empty_ds, tmp_path):
    path = tmp_path / "test_empty_ds_if"
    ds = empty_ds.copy()
    # add some unsorted metadata
    ds.pr.contact = "Someone"
    ds.pr.comment = "This needs to be sorted alphabetically."
    ds.pr.title = "Test Dataset"
    # mess up the sorting of the data
    ds_if = ds.pr.to_interchange_format()
    ds_if = ds_if.sort_values("entity")
    pm2io.write_interchange_format(path, ds_if)
    result_csv = path.with_suffix(".csv").read_bytes()
    result_yaml = path.with_suffix(".yaml").read_bytes()
    test_data_dir = importlib.resources.files(primap2).joinpath("tests").joinpath("data")
    expected_csv = test_data_dir.joinpath("test_empty_ds_if.csv").read_bytes()
    expected_yaml = test_data_dir.joinpath("test_empty_ds_if.yaml").read_bytes()

    assert result_csv == expected_csv
    assert result_yaml == expected_yaml
