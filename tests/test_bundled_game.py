# SPDX-License-Identifier: MPL-2.0
"""Fail closed before an untrusted downloaded archive becomes runnable code."""
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import bundled_game

class BundledGameTests(unittest.TestCase):
    def run_archive(self, members, *, archive_hash=None, asset_hash=None):
        buffer=io.BytesIO()
        with tarfile.open(fileobj=buffer,mode='w:gz') as archive:
            for name,value,kind in members:
                info=tarfile.TarInfo(name);info.size=len(value);info.type=kind
                if kind==tarfile.SYMTYPE:info.linkname='../escape'
                archive.addfile(info,io.BytesIO(value) if info.isfile() else None)
        data=buffer.getvalue();name='aion-0123456789abcdef.js';payload=b'good local engine'
        pin={'build':'0123456789abcdef','origin':'https://example.invalid/','files':{name:{'size':len(payload),'sha256':asset_hash or hashlib.sha256(payload).hexdigest()}},'bundle':{'url':'https://example.invalid/immutable.tar.gz','size':len(data),'sha256':archive_hash or hashlib.sha256(data).hexdigest()}}
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'source';source.mkdir();(root/'work').mkdir();cache=root/'cache'
            with patch.multiple(bundled_game,ROOT=root,SOURCE=source,CACHE=cache,PIN=pin),patch('bundled_game.urllib.request.urlopen',return_value=io.BytesIO(data)):
                result=bundled_game.files();self.assertEqual(result[name].read_bytes(),payload)
    def test_exact_archive_is_verified_and_usable(self):self.run_archive([('aion-0123456789abcdef.js',b'good local engine',tarfile.REGTYPE)])
    def test_archive_hash_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError,'archive hash mismatch'):self.run_archive([('aion-0123456789abcdef.js',b'good local engine',tarfile.REGTYPE)],archive_hash='0'*64)
    def test_traversal_and_extra_members_rejected(self):
        with self.assertRaisesRegex(ValueError,'Unexpected or duplicate'):self.run_archive([('../escape',b'good local engine',tarfile.REGTYPE)])
    def test_symlink_rejected(self):
        with self.assertRaisesRegex(ValueError,'Invalid game archive member'):self.run_archive([('aion-0123456789abcdef.js',b'good local engine',tarfile.SYMTYPE)])
    def test_duplicate_member_rejected(self):
        with self.assertRaisesRegex(ValueError,'Unexpected or duplicate'):self.run_archive([('aion-0123456789abcdef.js',b'good local engine',tarfile.REGTYPE)]*2)
    def test_wrong_runnable_bytes_rejected(self):
        with self.assertRaisesRegex(ValueError,'asset hash mismatch'):self.run_archive([('aion-0123456789abcdef.js',b'evil local engine',tarfile.REGTYPE)])
    def test_newtab_csp_changes_only_frame_directive(self):
        original="default-src 'none'; object-src 'none'; script-src resource: chrome:; connect-src https:;"
        updated=bundled_game.allow_game_frame(original)
        self.assertEqual(updated.replace(' frame-src moz-extension:;',''),original)
        self.assertEqual(bundled_game.allow_game_frame(updated),updated)
        with self.assertRaises(ValueError):bundled_game.allow_game_frame("default-src 'self';")
    def test_game_has_no_browser_data_permissions_or_remote_updater(self):
        manifest=json.loads((bundled_game.SOURCE/'manifest.json').read_text());html=(bundled_game.SOURCE/'play.html').read_text();bootstrap=(bundled_game.SOURCE/'bootstrap.js').read_text()
        self.assertEqual(manifest['permissions'],[]);self.assertNotIn('background',manifest);self.assertNotIn('content_scripts',manifest)
        self.assertIn("connect-src 'self';",manifest['content_security_policy'])
        self.assertNotIn('<script>',html);self.assertNotIn('serviceWorker.register',bootstrap);self.assertNotIn('fetch(',bootstrap)
