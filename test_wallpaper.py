import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HELPER = Path(__file__).resolve().parent / 'wallpaper.py'
spec = importlib.util.spec_from_file_location('wallpaper', HELPER)
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)
URL = 'https://www.pexels.com/photo/skyscraper-with-spire-in-city-downtown-7078504/'
ARGS = ['apply', URL, '--city', 'New York', '--mood', 'blue hour', '--photographer', 'Laura Tancredi', '--reviewed']


class WallpaperTest(unittest.TestCase):
    def test_source_boundary(self):
        self.assertEqual(w.photo_id(URL), '7078504')
        self.assertEqual(w.photo_id('https://www.pexels.com/photo/7078504/'), '7078504')
        for bad in ['http://www.pexels.com/photo/7078504/', 'https://www.pexels.com.evil.test/photo/7078504/',
                    'https://www.pexels.com@evil.test/photo/7078504/', 'https://www.pexels.com/video/7078504/', URL+'?url=other']:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                w.photo_id(bad)

    def test_no_review_no_network_or_settings(self):
        with patch.object(w, 'run') as run, self.assertRaises(ValueError):
            w.main(ARGS[:-1])
        run.assert_not_called()

    def test_download_only_has_no_apply_or_history(self):
        with tempfile.TemporaryDirectory() as root, patch.object(w, 'screen', return_value={'width': 2560, 'height': 1664}), \
             patch.object(w, 'run'), patch.object(w, 'dimensions', return_value=(2560, 1664)), patch.object(w, 'apply_file') as apply:
            result = w.main(['--data-dir', root] + ARGS + ['--download-only'])
            self.assertFalse(result['applied'])
            self.assertTrue(Path(result['path']).exists())
            self.assertFalse((Path(root) / 'history.json').exists())
            apply.assert_not_called()

    def test_success_saved_and_repeat_refused(self):
        with tempfile.TemporaryDirectory() as root, patch.object(w, 'screen', return_value={'width': 2560, 'height': 1664}), \
             patch.object(w, 'run'), patch.object(w, 'dimensions', return_value=(2560, 1664)), patch.object(w, 'apply_file') as apply:
            result = w.main(['--data-dir', root] + ARGS)
            self.assertTrue(result['applied'])
            self.assertEqual(len(w.read_history(Path(root))), 1)
            with self.assertRaises(ValueError):
                w.main(['--data-dir', root] + ARGS)
            self.assertEqual(apply.call_count, 1)

    def test_failed_application_not_saved(self):
        with tempfile.TemporaryDirectory() as root, patch.object(w, 'screen', return_value={'width': 2560, 'height': 1664}), \
             patch.object(w, 'run'), patch.object(w, 'dimensions', return_value=(2560, 1664)), \
             patch.object(w, 'apply_file', side_effect=ValueError('permission denied')):
            with self.assertRaises(ValueError):
                w.main(['--data-dir', root] + ARGS)
            self.assertEqual(w.read_history(Path(root)), [])

    def test_delayed_system_readback(self):
        with patch.object(w, 'run', side_effect=['', '/old.jpg', '/new.jpg']), patch.object(w.time, 'sleep'):
            w.apply_file(Path('/new.jpg'))

    def test_wrong_size_not_applied(self):
        with tempfile.TemporaryDirectory() as root, patch.object(w, 'screen', return_value={'width': 2560, 'height': 1664}), \
             patch.object(w, 'run'), patch.object(w, 'dimensions', return_value=(1600, 900)), patch.object(w, 'apply_file') as apply:
            with self.assertRaises(ValueError):
                w.main(['--data-dir', root] + ARGS)
            apply.assert_not_called()
            self.assertEqual(list(Path(root).iterdir()), [])

    def test_skill_install_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as root:
            result = w.install_skill(root)
            self.assertTrue((Path(result['installed']) / 'SKILL.md').exists())
            with self.assertRaises(ValueError):
                w.install_skill(root)


if __name__ == '__main__':
    unittest.main()
