"""Regression fixtures are synthetic TIFFs, not released papyrus annotations."""
import importlib
import os

import numpy as np
import pytest
import tifffile
import zarr

validator = importlib.import_module(os.getenv('VALIDATOR_MODULE', 'patched_validate_segments'))


@pytest.mark.parametrize('value', [-0.5, 0.5, 1.5, 255.5, 2.0, np.nan, np.inf, -np.inf])
@pytest.mark.parametrize('dtype', [np.float32, np.float64])
def test_rejects_nonbinary_float_values(tmp_path, value, dtype):
    data = np.zeros((16, 16), dtype=dtype)
    data[7, 5] = value
    path = tmp_path / 'segment_inklabels.tif'
    tifffile.imwrite(path, data)
    issues = validator.validate_label_tiff(path, workers=1, raw_shape=data.shape)
    assert any('not binary' in issue for issue in issues), (value, issues)
    assert str(value) in ' '.join(issues)


@pytest.mark.parametrize('dtype', [np.uint8, np.uint16, np.int16, np.float32, np.float64, np.bool_])
def test_accepts_binary_values(tmp_path, dtype):
    values = [0, 1] if dtype is np.bool_ else [0, 1, 255]
    data = np.resize(np.array(values, dtype=dtype), (16, 16))
    path = tmp_path / 'segment_inklabels.tif'
    tifffile.imwrite(path, data)
    assert validator.validate_label_tiff(path, workers=1, raw_shape=data.shape) == ()


@pytest.mark.parametrize('dtype,value', [(np.uint8, 2), (np.uint16, 256), (np.int16, -1)])
def test_retains_integer_rejection(tmp_path, dtype, value):
    data = np.full((16, 16), value, dtype=dtype)
    path = tmp_path / 'segment_inklabels.tif'
    tifffile.imwrite(path, data)
    assert validator.validate_label_tiff(path, workers=1, raw_shape=data.shape)


@pytest.mark.parametrize('value,expected_exit', [(0.5, 1), (1.5, 1), (255.5, 1), (1.0, 0)])
def test_full_cli_exit_code(tmp_path, value, expected_exit, capsys):
    segment = tmp_path / 'scroll' / 'segment'
    segment.mkdir(parents=True)
    array = zarr.open(str(segment / 'segment.zarr'), mode='w', shape=(3,16,16), chunks=(3,16,16), dtype='uint8')
    for kind in ['inklabels', 'supervision_mask']:
        tifffile.imwrite(segment / f'segment_{kind}.tif', np.full((16,16), value, dtype=np.float32))
    assert validator.main([str(tmp_path), '--workers', '1', '--no-progress']) == expected_exit
