"""Secret-free local catalog placement regression tests; no identity/runtime calls."""
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).with_name('configure-hub')
loader = importlib.machinery.SourceFileLoader('configure_hub', str(SOURCE))
spec = importlib.util.spec_from_loader(loader.name, loader)
helper = importlib.util.module_from_spec(spec)
loader.exec_module(helper)


class NativePlacementTests(unittest.TestCase):
    def test_artifact_is_explicit_and_preserves_time_and_admission(self):
        baseline = helper.catalog(helper.HUB_ORIGIN)
        selected = helper.catalog(helper.HUB_ORIGIN, include_artifact=True)
        self.assertEqual(baseline['nativeUpstreams']['bindings'], [helper.TIME_BINDING])
        self.assertEqual(selected['nativeUpstreams']['bindings'],
                         [helper.TIME_BINDING, helper.ARTIFACT_BINDING])
        selected['nativeUpstreams']['bindings'].pop()
        self.assertEqual(selected, baseline)

    def test_rerun_keeps_previously_selected_artifact(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(helper, 'STATE', Path(directory)):
            self.assertFalse(helper.retain_artifact_binding(False))
            self.assertTrue(helper.retain_artifact_binding(True))
            path = Path(directory) / 'hub.json'
            path.write_text(json.dumps(helper.catalog(helper.HUB_ORIGIN)))
            self.assertFalse(helper.retain_artifact_binding(False))
            self.assertTrue(helper.retain_artifact_binding(True))
            path.write_text(json.dumps(helper.catalog(helper.HUB_ORIGIN, include_artifact=True)))
            self.assertTrue(helper.retain_artifact_binding(False))

    def test_foreign_or_changed_native_placement_fails_before_regeneration(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(helper, 'STATE', Path(directory)):
            current = helper.catalog(helper.HUB_ORIGIN, include_artifact=True)
            current['nativeUpstreams']['bindings'][1]['sandbox'] = 'unapproved'
            path = Path(directory) / 'hub.json'
            encoded = json.dumps(current)
            path.write_text(encoded)
            with self.assertRaisesRegex(ValueError, 'review operator placement'):
                helper.retain_artifact_binding(True)
            self.assertEqual(path.read_text(), encoded)


if __name__ == '__main__':
    unittest.main()
