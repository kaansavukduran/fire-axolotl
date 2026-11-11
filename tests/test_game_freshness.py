# SPDX-License-Identifier: MPL-2.0
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from check_game_link import unchanged_gameplay, unchanged_engine_assets, PIN


class FreshnessTests(unittest.TestCase):
    def test_only_web_host_and_documents_can_change_without_a_new_game(self):
        self.assertTrue(unchanged_gameplay({'status':'ahead','ahead_by':1,'files':[{'filename':name} for name in ['packaging/web_boot.js','packaging/web_worker.js','docs/result.png','tests/browser_loader.py']]}))

    def test_every_game_resource_or_unknown_path_requires_a_new_snapshot(self):
        for name in ['scripts/game.gd','assets/wolf.png','project.godot','export_presets.cfg','scenes/main.tscn','shaders/world.gdshader','packaging/unknown.py','browser.js','tests/shadow.gd','docs/level.tscn']:
            self.assertFalse(unchanged_gameplay({'status':'ahead','ahead_by':1,'files':[{'filename':name}]}),name)

    def test_truncated_or_diverged_comparisons_are_not_proof(self):
        self.assertFalse(unchanged_gameplay({'status':'ahead','ahead_by':1}))
        self.assertFalse(unchanged_gameplay({'status':'diverged','files':[]}))
        self.assertFalse(unchanged_gameplay({'status':'ahead','ahead_by':251,'files':[]}))
        self.assertFalse(unchanged_gameplay({'status':'ahead','files':[{'filename':'docs/a.md'}]*300}))

    def test_moving_an_asset_into_docs_is_still_a_game_change(self):
        self.assertFalse(unchanged_gameplay({'status':'ahead','files':[{'filename':'docs/wolf.png','previous_filename':'assets/wolf.png'}]}))

    def test_engine_changes_or_missing_hashes_require_a_fresh_snapshot(self):
        build={'build':'f'*16,'assets':{name.replace(PIN['build'],'f'*16):{'bytes':record['size'],'sha256':record['sha256']} for name,record in PIN['files'].items()}}
        self.assertTrue(unchanged_engine_assets(build))
        wasm=next(name for name in build['assets'] if name.endswith('.wasm'))
        build['assets'][wasm]['sha256']='0'*64
        self.assertFalse(unchanged_engine_assets(build))
        self.assertFalse(unchanged_engine_assets({'build':'f'*16}))
