#!/usr/bin/env python3
"""Pexels-only macOS wallpaper helper. Standard library + macOS built-ins."""
import argparse
import datetime
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlsplit, urlencode


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=60).stdout.strip()


def screen():
    if platform.system() != 'Darwin':
        raise ValueError('Wallpaper application currently supports macOS only.')
    data = json.loads(run('system_profiler', 'SPDisplaysDataType', '-json'))
    displays = [d for gpu in data.get('SPDisplaysDataType', []) for d in gpu.get('spdisplays_ndrvs', [])]
    if not displays:
        raise ValueError('No screen detected.')
    main = next((d for d in displays if d.get('spdisplays_main') == 'spdisplays_yes'), displays[0])
    resolution = main.get('_spdisplays_pixels', main.get('_spdisplays_resolution', ''))
    match = re.search(r'(\d+)\s*x\s*(\d+)', resolution)
    if not match:
        raise ValueError('Could not determine screen dimensions: ' + resolution)
    width, height = map(int, match.groups())
    return {'width': width, 'height': height, 'display_count': len(displays)}


def photo_id(url):
    parsed = urlsplit(url)
    match = re.fullmatch(r'/photo/(?:[a-zA-Z0-9-]+-)?(\d+)/?', parsed.path)
    if parsed.scheme != 'https' or parsed.netloc not in ('www.pexels.com', 'pexels.com') or not match or parsed.query or parsed.fragment:
        raise ValueError('Use a canonical https://www.pexels.com/photo/name-ID/ photo page.')
    return match.group(1)


def dimensions(path):
    output = run('sips', '-g', 'pixelWidth', '-g', 'pixelHeight', str(path))
    width = re.search(r'pixelWidth:\s*(\d+)', output)
    height = re.search(r'pixelHeight:\s*(\d+)', output)
    if not width or not height:
        raise ValueError('Downloaded file is not a readable image.')
    return int(width[1]), int(height[1])


def read_history(root):
    path = root / 'history.json'
    return json.loads(path.read_text()) if path.exists() else []


def atomic_json(path, data):
    fd, name = tempfile.mkstemp(dir=str(path.parent), suffix='.tmp')
    try:
        with os.fdopen(fd, 'w') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def apple_literal(value):
    return '"' + str(value).replace('\\', '\\\\').replace('"', '\\"') + '"'


def apply_file(path):
    # System Events exposes the current desktop per display; inactive Spaces may differ.
    script = ('tell application "System Events"\nrepeat with d in every desktop\n'
              'set picture of d to ' + apple_literal(path) + '\nend repeat\nend tell')
    run('osascript', '-e', script)
    for _ in range(10):
        time.sleep(0.5)
        result = run('osascript', '-e', 'tell application "System Events" to get picture of every desktop')
        paths = [item.strip() for item in result.split(', ')]
        if paths and all(item == str(path) for item in paths):
            return
    raise ValueError('macOS did not confirm the wallpaper change. Check Automation permission; no success was recorded.')


def install_skill(destination):
    source = Path(__file__).resolve().parent
    target = Path(destination).expanduser().resolve() / 'city-night-wallpaper'
    if target.exists():
        raise ValueError('Skill already exists: ' + str(target) + '. Remove or rename it before installing an update.')
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git', 'node_modules', '*.tgz'))
    return {'installed': str(target), 'invoke': '$city-night-wallpaper'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', default=str(Path.home() / 'Library/Application Support/city-night-wallpaper'))
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('screen', help='Print main-screen dimensions without changing settings')
    commands.add_parser('history', help='Print successful wallpaper history')
    install = commands.add_parser('install-skill', help='Install the bundled Codex skill')
    install.add_argument('--destination', default=str(Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'skills'))
    apply = commands.add_parser('apply', help='Download a visually reviewed Pexels photograph and apply it')
    apply.add_argument('url')
    apply.add_argument('--city', required=True)
    apply.add_argument('--mood', required=True, help='Weather/time atmosphere for rotation history')
    apply.add_argument('--photographer', required=True)
    apply.add_argument('--reviewed', action='store_true', help='Confirm a human or agent inspected photo provenance and image quality')
    apply.add_argument('--download-only', action='store_true', help='Download and validate without changing wallpaper or rotation history')
    apply.add_argument('--allow-repeat', action='store_true')
    args = parser.parse_args(argv)
    root = Path(args.data_dir).expanduser().resolve()
    if args.command == 'install-skill':
        return install_skill(args.destination)
    if args.command == 'screen':
        return screen()
    if args.command == 'history':
        return read_history(root)
    ident = photo_id(args.url)
    if not args.reviewed:
        raise ValueError('Inspect the source page and image for real photography, quality, logos and distortion first; then pass --reviewed.')
    display = screen()
    history = read_history(root)
    if any(item['photo_id'] == ident for item in history) and not args.allow_repeat:
        raise ValueError('Photo already used. Choose another photo or pass --allow-repeat.')
    root.mkdir(parents=True, exist_ok=True)
    query = urlencode({'auto': 'compress', 'cs': 'tinysrgb', 'w': display['width'], 'h': display['height'], 'fit': 'crop'})
    image_url = 'https://images.pexels.com/photos/' + ident + '/pexels-photo-' + ident + '.jpeg?' + query
    fd, temporary = tempfile.mkstemp(dir=str(root), suffix='.jpg')
    os.close(fd)
    temporary = Path(temporary)
    try:
        run('curl', '--fail', '--silent', '--show-error', '--max-time', '45', '--max-filesize', '52428800', image_url, '-o', str(temporary))
        actual = dimensions(temporary)
        if actual != (display['width'], display['height']):
            raise ValueError('Downloaded dimensions differ from target: ' + str(actual))
        name = 'pexels-' + ident + '-' + str(display['width']) + 'x' + str(display['height']) + '.jpg'
        target = root / name
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
    record = {'photo_id': ident, 'city': args.city, 'mood': args.mood, 'photographer': args.photographer,
              'page': args.url, 'path': str(target), 'screen': display,
              'time': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'applied': False}
    if not args.download_only:
        apply_file(target)
        record['applied'] = True
        history.append(record)
        atomic_json(root / 'history.json', history)
    return record


if __name__ == '__main__':
    try:
        print(json.dumps(main(), ensure_ascii=False, indent=2))
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print('Error: ' + str(error), file=sys.stderr)
        sys.exit(1)
