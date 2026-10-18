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
            self.assertFalse(helper.select_services(False, False, helper.retained_catalog())[0])
            self.assertTrue(helper.select_services(True, False, helper.retained_catalog())[0])
            path = Path(directory) / 'hub.json'
            path.write_text(json.dumps(helper.catalog(helper.HUB_ORIGIN)))
            self.assertFalse(helper.select_services(False, False, helper.retained_catalog())[0])
            self.assertTrue(helper.select_services(True, False, helper.retained_catalog())[0])
            path.write_text(json.dumps(helper.catalog(helper.HUB_ORIGIN, include_artifact=True)))
            self.assertTrue(helper.select_services(False, False, helper.retained_catalog())[0])

    def test_foreign_or_changed_native_placement_fails_before_regeneration(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(helper, 'STATE', Path(directory)):
            current = helper.catalog(helper.HUB_ORIGIN, include_artifact=True)
            current['nativeUpstreams']['bindings'][1]['sandbox'] = 'unapproved'
            path = Path(directory) / 'hub.json'
            encoded = json.dumps(current)
            path.write_text(encoded)
            with self.assertRaisesRegex(ValueError, 'review operator placement'):
                helper.select_services(True, False, helper.retained_catalog())[0]
            self.assertEqual(path.read_text(), encoded)


    def test_media_requires_artifact_and_retains_every_approved_selection(self):
        with self.assertRaisesRegex(ValueError, 'Media requires selected Artifact'):
            helper.catalog(helper.HUB_ORIGIN, include_media=True)
        selected = helper.catalog(helper.HUB_ORIGIN, include_artifact=True, include_media=True)
        self.assertEqual(selected['nativeUpstreams']['bindings'],
                         [helper.TIME_BINDING, helper.ARTIFACT_BINDING, helper.MEDIA_BINDING])
        self.assertEqual(helper.select_services(False, False, selected), (True, True))
        self.assertEqual(helper.catalog(helper.HUB_ORIGIN, retained=selected), selected)
        artifact = helper.catalog(helper.HUB_ORIGIN, include_artifact=True)
        self.assertEqual(helper.select_services(False, True, artifact), (True, True))

    def test_media_billed_role_is_narrow_and_member_admission_is_unchanged(self):
        baseline = helper.catalog(helper.HUB_ORIGIN, include_artifact=True)
        selected = helper.catalog(helper.HUB_ORIGIN, include_artifact=True, include_media=True)
        self.assertEqual(selected['authorization']['roles'][:-1], baseline['authorization']['roles'])
        self.assertEqual(selected['authorization']['roles'][-1],
                         {'name': 'billed', 'access': ['read', 'write'], 'risks': ['billed']})
        self.assertEqual(selected['authorization']['grants'][:-1], baseline['authorization']['grants'])
        self.assertEqual(selected['authorization']['grants'][-1],
                         {'role': 'billed', 'subject': {'principal': helper.ISSUER + '#vv-hub-billed'}})
        self.assertEqual(selected['oauthClients'][:-1], baseline['oauthClients'])
        billed = selected['oauthClients'][-1]
        self.assertEqual(billed['id'], 'vv-hub-billed')
        self.assertEqual(billed['authMethods'], ['client_secret_post'])
        self.assertNotIn('clientSecret', billed)
        self.assertEqual(selected['workContexts'][0]['memberships'][0]['oauthClients'],
                         ['vv-hub-member', 'vv-hub-admin', 'vv-hub-billed'])

    def test_media_preserves_context_owner_policy_and_does_not_mutate_retained_input(self):
        baseline = helper.catalog(helper.HUB_ORIGIN, include_artifact=True)
        baseline['workContexts'][0]['outputPolicy']['owner']['id'] = helper.ISSUER + '#retained-owner'
        baseline['workContexts'][0]['policyRevision'] = 'retained'
        baseline['policies'].append({'version': 'retained', 'rules': []})
        before = json.dumps(baseline)
        selected = helper.catalog(helper.HUB_ORIGIN, include_media=True, retained=baseline)
        self.assertEqual(json.dumps(baseline), before)
        self.assertEqual(selected['policies'], baseline['policies'])
        selected['workContexts'][0]['memberships'][0]['oauthClients'].remove('vv-hub-billed')
        self.assertEqual(selected['workContexts'], baseline['workContexts'])

    def test_media_refuses_ambiguous_membership_or_foreign_placement(self):
        retained = helper.catalog(helper.HUB_ORIGIN, include_artifact=True)
        retained['workContexts'][0]['memberships'].append(
            dict(retained['workContexts'][0]['memberships'][0]))
        with self.assertRaisesRegex(ValueError, 'review retained contributor membership'):
            helper.catalog(helper.HUB_ORIGIN, include_media=True, retained=retained)
        for bindings in [
            [helper.TIME_BINDING, helper.MEDIA_BINDING],
            [helper.TIME_BINDING, helper.ARTIFACT_BINDING, dict(helper.MEDIA_BINDING, port=9999)],
            [helper.TIME_BINDING, helper.ARTIFACT_BINDING, helper.MEDIA_BINDING, helper.MEDIA_BINDING],
        ]:
            retained['nativeUpstreams']['bindings'] = bindings
            with self.assertRaisesRegex(ValueError, 'review operator placement'):
                helper.select_services(False, True, retained)


if __name__ == '__main__':
    unittest.main()
