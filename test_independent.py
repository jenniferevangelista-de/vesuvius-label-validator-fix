"""Independent real TIFF I/O tests; all labels are synthetic."""
import importlib
import tempfile
import unittest
from pathlib import Path
import numpy as np
import tifffile

old = importlib.import_module('upstream_validate_segments')
new = importlib.import_module('patched_validate_segments')

class Independent(unittest.TestCase):
    def check_fixture(self, values, tiled=False, dtype=np.float64):
        data = np.zeros((32, 32), dtype=dtype)
        data[-1, -len(values):] = values
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'segment_inklabels.tif'
            tifffile.imwrite(path, data, **({'tile': (16,16)} if tiled else {'rowsperstrip': 8}))
            return old.validate_label_tiff(path, workers=1, raw_shape=data.shape), new.validate_label_tiff(path, workers=1, raw_shape=data.shape)

    def test_subnormal_and_near_allowed_values_strips_and_tiles(self):
        for tiled in [False, True]:
            for val in [np.nextafter(0.,1.), np.nextafter(1.,2.), np.nextafter(255.,256.), -0.5]:
                with self.subTest(tiled=tiled, value=val):
                    before, after = self.check_fixture([val], tiled)
                    self.assertEqual(before, ())
                    self.assertTrue(after)
                    self.assertIn(str(val), ' '.join(after))

    def test_exact_valid_values_unchanged(self):
        for tiled in [False, True]:
            for dtype in [np.uint8,np.int16,np.float32,np.float64]:
                with self.subTest(tiled=tiled,dtype=dtype):
                    self.assertEqual(self.check_fixture([0,1,255],tiled,dtype), ((),()))

    def test_large_integer_error_value_not_rounded(self):
        # The correction must not lose integer precision by converting to float.
        value = 2**63 + 1
        before, after = self.check_fixture([value], dtype=np.uint64)
        self.assertEqual(before, after)
        self.assertIn(str(value), ' '.join(after))

if __name__ == '__main__': unittest.main(verbosity=2)
