#!/usr/bin/env python
# -*- coding: utf-8 -*-
from operator import itemgetter

from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.api.docs import addModel
from girder.api.rest import Resource, RestException
from girder.models.setting import Setting

from ..constants import PluginSettings
from ..lib.data_map import dataMapDoc
from ..lib.file_map import fileMapDoc
from ..lib import pids_to_entities


addModel('dataMap', dataMapDoc)
addModel('fileMap', fileMapDoc)


class Repository(Resource):
    def __init__(self):
        super(Repository, self).__init__()
        self.resourceName = 'repository'

        self.route('GET', (), self.getPublishRepositories)
        self.route('GET', ('lookup',), self.lookupData)
        self.route('GET', ('listFiles',), self.listFiles)

    @access.public
    @autoDescribeRoute(
        Description('Create data mapping to an external repository.')
        .notes(
            'Given a list of external data identifiers, returns mapping to specific repository '
            'along with a basic metadata, such as size, name.'
        )
        .jsonParam(
            'dataId',
            paramType='query',
            required=True,
            description='List of external datasets identificators.',
        )
        .responseClass('dataMap', array=True)
    )
    def lookupData(self, dataId):
        try:
            results = pids_to_entities(
                dataId, user=self.getCurrentUser(), lookup=True
            )
        except RuntimeError as exc:
            raise RestException(exc.args[0])
        return sorted([x.toDict() for x in results], key=lambda k: k['name'])

    @access.public
    @autoDescribeRoute(
        Description(
            'Retrieve a list of files and nested packages in a repository'
        )
        .notes(
            'Given a list of external data identifiers, returns a list of files inside '
            'along with their sizes'
        )
        .jsonParam(
            'dataId',
            paramType='query',
            required=True,
            description='List of external datasets identificators.',
        )
        .responseClass('fileMap', array=True)
    )
    def listFiles(self, dataId):
        try:
            results = pids_to_entities(
                dataId, user=self.getCurrentUser(), lookup=False
            )
        except RuntimeError as exc:
            raise RestException(exc.args[0])
        return sorted([x.toDict() for x in results], key=lambda k: list(k))

    @access.public
    @autoDescribeRoute(
        Description(
            "Retrieve a list of repositories where user can deposit their Tale"
        )
    )
    def getPublishRepositories(self):
        user = self.getCurrentUser()
        if not user:
            return []

        targets = []
        for entry in Setting().get(PluginSettings.PUBLISHER_REPOS):
            repository = entry["repository"]
            key = "resource_server"
            value = repository

            token = next(
                (_ for _ in user.get("otherTokens", []) if _.get(key) == value), None
            )
            if token:
                targets.append({"repository": repository, "name": entry["name"]})

        return sorted(targets, key=itemgetter("name"))
