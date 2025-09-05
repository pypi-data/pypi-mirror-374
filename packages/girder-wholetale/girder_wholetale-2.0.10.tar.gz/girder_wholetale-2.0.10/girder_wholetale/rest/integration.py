#!/usr/bin/env python
# -*- coding: utf-8 -*-
from girder.api.rest import Resource
from ..lib.dataverse.integration import dataverseExternalTools
from ..lib.zenodo.integration import zenodoDataImport


class Integration(Resource):

    def __init__(self):
        super(Integration, self).__init__()
        self.resourceName = 'integration'

        self.route('GET', ('dataverse',), dataverseExternalTools)
        self.route('GET', ('zenodo',), zenodoDataImport)
