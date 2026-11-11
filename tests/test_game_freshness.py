# SPDX-License-Identifier: MPL-2.0
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from check_game_link import unchanged_gameplay


class FreshnessTests(unittest.TestCase):
    def test_only_web_host_and_documents_can_change_without_a_new_game(self):
        self.assertTrue(unchanged_gameplay({'status':'ahead','ahead_by':1,'files':[{'filename':name} for name in ['packaging/web_boot.js','packaging/web_worker.js','docs/result.png','tests/browser_loader.py']]}))

    def test_every_game_resource_or_unknown_path_requires_a_new_snapshot(self):
        for name in ['scripts/game.gd','assets/wolf.png','project.godot','export_presets.cfg','scenes/main.tscn','shaders/world.gdshader','packaging/unknown.py','browser.js']:
            self.assertFalse(unchanged_gameplay({'status':'ahead','ahead_by':1,'files':[{'filename':name}]}),name)

    def test_truncated_or_diverged_comparisons_are_not_proof(self):
        self.assertFalse(unchanged_gameplay({'status':'ahead','ahead_by':1}))
        self.assertFalse(unchanged_gameplay({'status':'diverged','files':[]}))
        self.assertFalse(unchanged_gameplay({'status':'ahead','ahead_by':251,'files':[]}))
        self.assertFalse(unchanged_gameplay({'status':'ahead','files':[{'filename':'docs/a.md'}]*300}))

    def test_moving_an_asset_into_docs_is_still_a_game_change(self):
        self.assertFalse(unchanged_gameplay({'status':'ahead','files':[{'filename':'docs/wolf.png','previous_filename':'assets/wolf.png'}]}))
