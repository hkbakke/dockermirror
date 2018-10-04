#!/usr/bin/env python3

import argparse
import logging
from pathlib import Path
import os
import time
import hashlib
import base64
import json

import dockermirror


LOGGER = logging.getLogger()


def get_archives(path):
    for entry in os.scandir(path):
        if entry.name.endswith('.tar') and entry.is_file():
            yield dockermirror.DockerArchive(Path(entry.path))

def get_archive_filename(data):
    """
    Produce a length limited deterministic file system friendly name from
    variable input
    """
    h = hashlib.sha256()
    h.update(data)
    sha256 = h.digest()
    b64 = base64.urlsafe_b64encode(sha256)

    # Remove base64 padding (trailing '=' characters) as there is no need to
    # reverse the base64 operation later
    return '%s.tar' % b64.decode('utf-8').rstrip('=')

def main():
    # global arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--log-level',
        choices=[
            'critical',
            'error',
            'warning',
            'info',
            'debug'
        ],
        default='info',
        help='Set log level for console output'
    )
    subparsers = parser.add_subparsers(title='subcommands', dest='subcommand')

    # save subcommand
    save_parser = subparsers.add_parser('save', help='save docker image to file')
    save_parser.add_argument('--output-dir', metavar='DIRECTORY', default='.',
                             help='directory to put archive file in')
    save_parser.add_argument('--remove', action='store_true', default=False,
                             help='remove docker images after save')
    save_parser.add_argument('images', metavar='IMAGE', nargs='+',
                             help='docker images to save')

    # load subcommands
    load_parser = subparsers.add_parser('load', help='load docker image from file')
    load_parser.add_argument('--registry', metavar='REGISTRY', default=None,
                             help='push archive images to registry')
    load_parser.add_argument('--remove', action='store_true', default=False,
                             help='remove archive after load')
    load_parser.add_argument('archive', metavar='NAME',
                             help='archive filename')

    # remove subcommands
    remove_parser = subparsers.add_parser('remove', help='remove saved docker images')
    remove_parser.add_argument('archive', metavar='ARCHIVE',
                               help='archive filename')

    # monitor subcommands
    monitor_parser = subparsers.add_parser(
       'monitor', help='monitor folder for new archives and auto-load')
    monitor_parser.add_argument('--registry', metavar='REGISTRY', default=None,
                                help='push archive images to registry')
    monitor_parser.add_argument('--interval', metavar='SECONDS', default=60, type=int,
                                help='monitor directory scan interval')
    monitor_parser.add_argument('directory', metavar='DIRECTORY',
                                help='directory to monitor')

    # show subcommands
    show_parser = subparsers.add_parser('show', help='show archive information')
    show_parser.add_argument('archive', metavar='ARCHIVE',
                             help='archive filename')

    args = parser.parse_args()

    # Set up logging
    LOGGER.setLevel(args.log_level.upper())
    console = logging.StreamHandler()
    LOGGER.addHandler(console)

    if args.subcommand == 'save':
        images = [dockermirror.DockerImage(i) for i in args.images]
        filename = get_archive_filename(''.join(sorted(args.images)).encode('utf-8'))
        archive_path = Path(args.output_dir).joinpath(filename)
        archive = dockermirror.DockerArchive(archive_path)
        archive.save(images, args.remove)
    elif args.subcommand == 'load':
        archive = dockermirror.DockerArchive(Path(args.archive))
        archive.load(args.registry, args.remove)
    elif args.subcommand == 'remove':
        archive = dockermirror.DockerArchive(Path(args.archive))

        for image in archive.images:
            image.remove()

        archive.remove()
    elif args.subcommand == 'monitor':
        while True:
            start_time = time.time()

            LOGGER.debug('Scanning %s for new docker archives', args.directory)
            for archive in get_archives(args.directory):
                LOGGER.info('Loading %s', archive.filepath)
                archive.load(args.registry, remove=True)

            run_time = time.time() - start_time

            if run_time < args.interval:
                sleep_time = args.interval - run_time
                LOGGER.debug('Sleeping %s seconds', sleep_time)
                time.sleep(args.interval - run_time)
    elif args.subcommand == 'show':
        archive = dockermirror.DockerArchive(Path(args.archive))
        print(json.dumps(archive.manifest, sort_keys=True, indent=4))


if __name__ == '__main__':
    main()
