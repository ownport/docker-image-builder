from __future__ import (absolute_import, division, print_function)

import imp
import sys
import logging
import argparse

from builder import BUILDER_VERSION
from builder.log import Logger
from builder.docker import DockerCLI
from builder.container import ContainerContext

BUILDER_USAGE = '''docker-image-builer <command> [<args>]

The list of commands:
   run              run Docker image           
   build            build Docker image
   halt             stop and remove container(-s)
'''

# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logger = Logger(__name__)


class CLI(object):
    def __init__(self):
        parser = argparse.ArgumentParser(usage=BUILDER_USAGE)
        parser.add_argument('-v', '--version', action='version',
                            version='docker-image-builder-v{}'.format(BUILDER_VERSION))
        parser.add_argument('-l', '--log_level', default='INFO',
                            help='Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL')
        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])

        if not hasattr(self, args.command):
            print('Unrecognized command: %s' % args.command)
            sys.exit(1)

        logging.basicConfig(level=args.log_level,
                            handler=NullHandler(),
                            format="%(asctime)s (%(name)s) [%(levelname)s] %(message)s")

        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    @staticmethod
    def run():
        parser = argparse.ArgumentParser(description='run base image')
        parser.add_argument('-i', '--image_name', dest='image_name', required=True,
                            help="the image name")
        parser.add_argument('-c', '--container_name', dest='container_name', required=True,
                            help="the container name")
        parser.add_argument('--re-run', dest='rerun', action='store_true',
                            help="re-run container if exists, default: False")
        args = parser.parse_args(sys.argv[2:])

        docker_cli = DockerCLI()

        images_list = ["%s:%s" % (i[u'repository'], i[u'tag']) for i in docker_cli.images_list()]
        if args.image_name not in images_list:
            logger.error(**{u'msg': u'Image does not exist', u'image.name': args.image_name})
            logger.info(**{u'msg': u'Available images', u'images': images_list})
            sys.exit(1)

        docker_cli.run_base_container(args.image_name, args.container_name, rerun=args.rerun)

    @staticmethod
    def build():
        parser = argparse.ArgumentParser(description='build Docker image')
        parser.add_argument('-s', '--source_image_name', dest='source_image_name', required=True,
                            help="source (base) image name")
        parser.add_argument('-c', '--container_name', dest='container_name', required=True,
                            help="container name (staging)")
        parser.add_argument('-t', '--target_image_name', dest='target_image_name', required=True,
                            help="target image name")
        parser.add_argument('-b', '--build-script', dest='build_script', required=True,
                            help="build script")
        parser.add_argument('--re-run', dest='rerun', action='store_true',
                            help="re-run container if exists, default: False")
        parser.add_argument('--remove-staging', dest='remove_staging', action='store_true',
                            help="remove staging container after commit")
        parser.add_argument('--enable-sh-logging', action='store_true',
                            help='Enable sh module logging, default: disabled')
        args = parser.parse_args(sys.argv[2:])

        if args.enable_sh_logging:
            logging.getLogger('sh').setLevel('INFO')
        else:
            logging.getLogger('sh').setLevel(logging.WARNING)

        docker_cli = DockerCLI()

        images_list = ["%s:%s" % (i[u'repository'], i[u'tag']) for i in docker_cli.images_list()]
        if args.source_image_name not in images_list:
            logger.error(**{u'msg': u'Source image does not exist', u'image.name': args.source_image_name})
            logger.info(**{u'msg': u'Available images', u'images': images_list})
            sys.exit(1)

        docker_cli.run_base_container(args.source_image_name, args.container_name, rerun=args.rerun)

        build_script = imp.load_source('build.script', args.build_script)
        try:
            build_script.run(ContainerContext(args.container_name))
            docker_cli.commit(args.container_name, args.target_image_name)
        except AttributeError as err:
            logger.error(**{u'msg': u'Cannot execute run() from the build script',
                            u'build.script': args.build_script})

        if args.remove_staging:
            staging_container_id = [c[u'id'] for c in docker_cli.containers_list()
                                    if args.container_name == c[u'names']]
            docker_cli.stop_containers(*staging_container_id)
            docker_cli.remove_containers(*staging_container_id)

    @staticmethod
    def halt():
        parser = argparse.ArgumentParser(description='stop and remove containers')
        parser.add_argument('-c', '--container_id', dest='container_id', action='append',
                            help="the container id(-s)")
        parser.add_argument('--all', dest='all', action='store_true',
                            help="stop and remove all containers")

        args = parser.parse_args(sys.argv[2:])

        if not args.container_id and not args.all:
            parser.print_help()
            sys.exit(1)

        docker_cli = DockerCLI()

        if args.container_id:
            logger.info(**{u'msg': u'Halting container', u'container.id': args.container_id})
            docker_cli.stop_containers(args.container_id)
            docker_cli.remove_containers(args.container_id)

        if args.all:
            ids = [c[u'id'] for c in docker_cli.containers_list()]
            logger.info(**{u'msg': u'Halting all container(-s)', u'container.ids': ids})
            docker_cli.stop_containers(*ids)
            docker_cli.remove_containers(*ids)
        logger.info(**{u'msg': u'Available containers',
                       u'container.ids': [c[u'id'] for c in docker_cli.containers_list()]})
