#!/usr/bin/env python
# -*- coding: utf-8 -*-
from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.api.docs import addModel
from girder.api.rest import (
    Resource,
    filtermodel,
    RestException,
    setResponseHeader,
    setRawResponse
)
from girder.constants import AccessType, SortDir
from girder.models.setting import Setting
from girder.models.user import User

from ..constants import PluginSettings
from ..models.instance import Instance as InstanceModel
from ..models.tale import Tale


instanceSchema = {
    'id': 'instance',
    'type': 'object',
    'required': [
        '_accessLevel', '_id', '_modelType', 'containerId',
        'containerPath', 'created', 'digest',
        'frontendId', 'imageId',  'lastActivity', 'mountPoint',
        'status', 'userId', 'when'
    ],
    'example': {
        '_accessLevel': 2,
        '_id': '587506670791d3000121b68d',
        '_modelType': 'instance',
        'containerInfo': {
            'containerId': '397914f6bf9e4d153dd86',
            'containerPath': 'user/.../login?token=...',
            'host': '172.17.0.1',
            'mountPoint': '/var/lib/docker/volumes/58caa69f9fcbde0001/_data',
            'volumeName': '58ca9fcbde0001df4d26_foo',
            'digest': 'sha256:198246816212941281ab1243de09c9adbca92',
            'imageId': '58caa69f00f4d26cbd9fe01d'
        },
        'created': '2017-04-07T17:04:04.777000+00:00',
        'creatorId': '57c099af86ed1d0001733722',
        'iframe': True,
        'lastActivity': '2017-04-07T17:04:04.777000+00:00',
        'name': 'test',
        'status': 0,
        'taleId': '58caa69f9fcbde0001df4d26',
        'url': 'user/hkhHpMloA4Pp/login?token=babf41833c9641a4a92bece48a34e5b7'
    },
    'properties': {
        '_accessLevel': {'type': 'integer', 'format': 'int32'},
        '_id': {'type': 'string'},
        '_modelType': {'type': 'string'},
        'containerInfo': {
            '$ref': '#/definitions/containerInfo'
        },
        'created': {'type': 'string', 'format': 'date'},
        'creatorId': {'type': 'string'},
        'iframe': {
            'type': 'boolean',
            'description': 'If "true", instance can be embedded in an iframe'
        },
        'lastActivity': {'type': 'string', 'format': 'date'},
        'name': {'type': 'string'},
        'status': {'type': 'integer', 'format': 'int32',
                   'allowEmptyValue': False,
                   'maximum': 1, 'minimum': 0},
        'taleId': {'type': 'string'},
        'url': {'type': 'string'}
    }
}
addModel('instance', instanceSchema, resources='instance')
instanceCapErrMsg = (
    'You have reached a limit for running instances ({}). '
    'Please shutdown one of the running instances before '
    'continuing.'
)


class Instance(Resource):

    def __init__(self):
        super(Instance, self).__init__()
        self.resourceName = 'instance'
        self._model = InstanceModel()

        self.route('GET', (), self.listInstances)
        self.route('POST', (), self.createInstance)
        self.route('GET', (':id',), self.getInstance)
        self.route('DELETE', (':id',), self.deleteInstance)
        self.route('PUT', (':id',), self.updateInstance)
        self.route('GET', (':id', 'log'), self.getInstanceLog)

    @access.user
    @filtermodel(model='instance', plugin='wholetale')
    @autoDescribeRoute(
        Description('Return all the running instances accessible by the user')
        .param('userId', "The ID of the instance's creator.", required=False)
        .param('taleId',  'List all the instanes using this tale.', required=False)
        .param('text', 'Perform a full text search for a tale with a matching '
               'name.', required=False)
        .responseClass('instance', array=True)
        .pagingParams(defaultSort='created', defaultSortDir=SortDir.DESCENDING)
    )
    def listInstances(self, userId, taleId, text, limit, offset, sort, params):
        # TODO: text search is ignored
        currentUser = self.getCurrentUser()
        if taleId:
            tale = Tale().load(
                taleId, user=currentUser, level=AccessType.READ)
        else:
            tale = None

        if userId:
            user = User().load(userId, force=True, exc=True)
        else:
            user = None

        # TODO allow to search for instances that belongs to specific user
        return list(InstanceModel().list(
            user=user, tale=tale, offset=offset, limit=limit,
            sort=sort, currentUser=currentUser))

    @access.user
    @filtermodel(model='instance', plugin='wholetale')
    @autoDescribeRoute(
        Description('Get an instance by ID.')
        .modelParam('id', model='instance', plugin='wholetale', level=AccessType.READ)
        .responseClass('instance')
        .errorResponse('ID was invalid.')
        .errorResponse('Read access was denied for the instance.', 403)
    )
    def getInstance(self, instance, params):
        return instance

    @access.user
    @filtermodel(model='instance', plugin='wholetale')
    @autoDescribeRoute(
        Description('Updates and restarts an existing instance.')
        .modelParam('id', model='instance', plugin='wholetale', level=AccessType.WRITE)
        .errorResponse('ID was invalid.')
        .errorResponse('Write access was denied for the instance.', 403)
    )
    def updateInstance(self, instance):
        currentUser = self.getCurrentUser()

        taleId = instance['taleId']
        tale = Tale().load(taleId, user=currentUser, level=AccessType.READ)

        # TODO: Only continue if digest has changed
        # if image['digest'] != instance['containerInfo']['digest']:

        # Digest ensures that container runs from newest image version
        self._model.updateAndRestartInstance(
            instance,
            currentUser,
            tale)
        return instance

    @access.user
    @autoDescribeRoute(
        Description('Delete an existing instance.')
        .modelParam('id', model='instance', plugin='wholetale', level=AccessType.WRITE)
        .errorResponse('ID was invalid.')
        .errorResponse('Write access was denied for the instance.', 403)
    )
    def deleteInstance(self, instance, params):
        InstanceModel().deleteInstance(
            instance, self.getCurrentUser())

    @access.user
    @filtermodel(model='instance', plugin='wholetale')
    @autoDescribeRoute(
        Description('Create a new instance')
        .notes('Instantiate a tale.')
        .param('taleId', 'The ID of a tale used to create an instance.',
               required=True)
        .param('name', 'A user-friendly, short name of the tale.',
               required=False)
        .param('spawn', 'If false, create only db object without a corresponding '
                        'container.',
               default=True, required=False, dataType='boolean')
        .responseClass('instance')
        .errorResponse(instanceCapErrMsg, 400)
        .errorResponse('Read access was denied for the tale.', 403)
    )
    def createInstance(self, taleId, name, spawn):
        user = self.getCurrentUser()

        tale = Tale().load(
            taleId, user=user, level=AccessType.READ)

        existing = InstanceModel().findOne({
            'taleId': tale['_id'],
            'creatorId': user['_id'],
        })
        if existing:
            return existing

        running_instances = list(
            self._model.list(user=user, currentUser=user)
        )
        instance_cap = Setting().get(PluginSettings.INSTANCE_CAP)
        if len(running_instances) + 1 > int(instance_cap):
            raise RestException(instanceCapErrMsg.format(instance_cap))

        return InstanceModel().createInstance(tale, user, name=name, save=True, spawn=spawn)

    @access.user
    @autoDescribeRoute(
        Description("Fetch Instance logs")
        .modelParam('id', model='instance', plugin='wholetale', level=AccessType.READ)
        .param("tail", "Number of lines to show from the end of the logs",
               default=100, required=False, dataType='int')
        .produces("text/plain")
        .errorResponse('ID was invalid.')
        .errorResponse('Read access was denied for the instance.', 403)
    )
    def getInstanceLog(self, instance, tail):
        if tail < 0:
            tail = "all"
        setResponseHeader('Content-Type', "text/plain")
        setRawResponse()
        return self._model.get_logs(instance, tail)
