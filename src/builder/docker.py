from __future__ import (absolute_import, division, print_function)

import sh
import json

from builder.log import Logger

logger = Logger(__name__)


class DockerCLI(object):
    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def images_list(self):
        '''
        :return: the list of existing images 
        '''
        try:
            for details in sh.docker.images(format='{{json .}}').split('\n'):
                if not details:
                    continue
                try:
                    img = json.loads(details)
                except ValueError as err:
                    logger.error(**{u'msg': u'{}'.format(err), u'image.details': u'{}'.format(details)})
                    continue
                yield {
                    u'id': img.get(u'ID', u''),
                    u'repository': img.get(u'Repository', u''),
                    u'tag': img.get(u'Tag', u''),
                    u'size': img.get(u'Size', 0),
                    u'createdAt': img.get(u'CreatedAt', '')
                }
        except sh.ErrorReturnCode as err:
            logger.error(**{u'msg': err.stderr})
            raise StopIteration()

    def containers_list(self):
        '''
        return the list of containers
        :return: the list of containers
        '''
        try:
            for details in sh.docker.ps('-a', format='{{json .}}').split('\n'):
                if not details:
                    continue
                try:
                    cont = json.loads(details)
                except ValueError as err:
                    logger.error(**{u'msg': u'{}'.format(err), u'image.details': u'{}'.format(details)})
                    continue
                yield {
                    u'id': cont.get(u'ID', u''),
                    u'names': cont.get(u'Names', u''),
                    u'image': cont.get(u'Image', u''),
                    u'labels': cont.get(u'Labels', []),
                    u'command': cont.get(u'Command', u''),
                    u'createdAt': cont.get(u'CreatedAt', u''),
                    u'localVolumes': cont.get(u'LocalVolumes', u''),
                    u'mounts': cont.get(u'Mounts', u''),
                    u'networks': cont.get(u'Networks', u''),
                    u'ports': cont.get(u'Ports', []),
                    u'status': cont.get(u'Status', u''),
                    u'runningFor': cont.get(u'RunningFor', u''),
                    u'size': cont.get(u'Size', 0),
                }
        except sh.ErrorReturnCode as err:
            logger.error(**{u'msg': err.stderr})
            raise StopIteration()

    def run(self, *args):
        '''
        Run image
        :param args: docker run command line arguments
        :return the ID of container
        '''
        try:
            return sh.docker.run(*args).strip()
        except sh.ErrorReturnCode as err:
            logger.error(**{u'msg': err.stderr})
            return None

    def run_base_container(self, image_name, container_name, rerun=False):
        ''' 
        Run base container as daemon
        :param image_name: Image name
        :param container_name: Container name
        :return the ID of container
        '''
        logger.info(**{
            u'msg': 'Starting base container',
            u'image.name': image_name,
            u'container.name': container_name,
            u'rerun': rerun,
        })
        container_exists = ([c for c in self.containers_list() if container_name == c[u'names']])
        if container_exists:
            logger.warning(**{u'msg': u'Container exists', u'container.details': container_exists})
            if not rerun:
                logger.info(**{u'msg': u'Base container was not created'})
                return None
            else:
                container_ids = [c[u'id'] for c in container_exists]
                self.stop_containers(container_ids)
                self.remove_containers(container_ids)
        _id = self.run('-d', '--name=%s' % container_name, image_name, '/bin/sh', '-c', 'tail -f /dev/null').strip()
        logger.info(**{u'msg': 'Base container was created', u'container.id': _id})
        return _id

    def stop_containers(self, *ids):
        '''
        Stop container(-s)
        :param container_id: container id 
        :return: the result of stopping (True or False)
        '''
        logger.info(**{u'msg': u'Stopping containers', u'container.ids': ids})

        if not ids:
            logger.info(**{u'msg': u'No containers for stopping'})
            return []

        try:
            return sh.docker.stop(*ids).strip()
        except sh.ErrorReturnCode as err:
            logger.error(**{u'msg': err.stderr})
            return []

    def remove_containers(self, *ids):
        '''
        Remove container(-s)
        :param container_id: container id 
        :return: the result of removing (True or False)
        '''
        logger.info(**{u'msg': u'Removing containers', u'container.ids': ids})

        if not ids:
            logger.info(**{u'msg': u'No containers for stopping'})
            return []

        try:
            return sh.docker.rm(*ids).strip()
        except sh.ErrorReturnCode as err:
            logger.error(**{u'msg': err.stderr})
            return []

    def execute(self, containter_name, *args):
        '''
        Execute command(-s) in the container
        :param containter_name: container name
        :param args: the list of command line arguments
        :return: exit code of command execution
        '''
        logger.info(**{u'msg': u'Execute command in the container',
                       u'container.name': containter_name,
                       u'command.args': args})
        try:
            return sh.docker('exec', containter_name, *args)
        except sh.ErrorReturnCode as err:
            if err.stdout:
                print(err.stdout)
            if err.stderr:
                print(err.stderr)
            return []

    def commit(self, containter_name, image_name):
        '''
        Commit container to image
        
        :param containter_name: container name 
        :param image_name: image name
        :return: image id 
        '''
        logger.info(**{u'msg': u'Committing container into image',
                       u'container.name': containter_name,
                       u'image.name': image_name})

        if not containter_name or not image_name:
            logger.info(**{u'msg': u'No container or image names for commit',
                           u'container.name': containter_name,
                           u'image.name': image_name})
            return []

        try:
            _id = sh.docker.commit(containter_name, image_name).strip()
            logger.info(**{u'msg': 'Container committed to the image',
                           u'container.name': containter_name,
                           u'image.name': image_name,
                           u'image.id': _id})
            return _id
        except sh.ErrorReturnCode as err:
            logger.error(**{u'msg': err.stderr})
            return []
