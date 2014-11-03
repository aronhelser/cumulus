import cherrypy
import json
from girder.api.rest import Resource
from girder.api import access
from girder.api.describe import Description
from girder.api.docs import addModel
from girder.constants import AccessType


class Job(Resource):
    def __init__(self):
        self.resourceName = 'jobs'
        self.route('POST', (), self.create)
        self.route('PATCH', (':id',), self.update)
        self.route('GET', (':id', 'status'), self.status)
        self.route('PUT', (':id', 'terminate'), self.terminate)
        self.route('POST', (':id', 'log'), self.add_log_record)
        self.route('GET', (':id', 'log'), self.log)

        self._model = self.model('job', 'cumulus')

    @access.user
    def create(self, params):
        user = self.getCurrentUser()

        body = json.loads(cherrypy.request.body.read())
        commands = body['commands']
        name = body['name']
        output_collection_id = body['outputCollectionId']

        job = self._model.create(user, name, commands, output_collection_id)

        cherrypy.response.status = 201
        cherrypy.response.headers['Location'] = '/jobs/%s' % job['_id']

        # Don't return the access object
        del job['access']

        return job

    addModel('JobParameters', {
        "id":"JobParameters",
        "properties":{
            "commands": {"type": "string", "description": "The commands to run."},
            "name":  {"type": "string", "description": "The human readable job name."},
            "outputCollectionId": {"type": "string", "description": "The id of the collection to upload the output to."}
        }})

    create.description = (Description(
            'Create a new job'
        )
        .param(
            'body',
            'The job parameters in JSON format.', dataType='JobParameters', paramType='body', required=True))

    @access.user
    def terminate(self, id, params):
        pass

    terminate.description = (Description(
            'Terminate a job'
        )
        .param(
            'id',
            'The job id', paramType='path'))

    @access.user
    def update(self, id, params):
        user = self.getCurrentUser()
        body = json.loads(cherrypy.request.body.read())
        status = None
        sge_id = None

        if 'status' in body:
            status = body['status']

        if 'sgeId' in body:
            sge_id = body['sgeId']

        job = self._model.update_job(user, id, status, sge_id)

        # Don't return the access object
        del job['access']
        # Don't return the log
        del job['log']

        return job

    addModel("JobUpdateParameters", {
        "id":"JobUpdateParameters",
        "properties":{
            "status": {"type": "string", "description": "The new status. (optional)"},
            "sgeId": {"type": "integer", "description": "The SGE job id. (optional)"}
        }
    })


    update.description = (Description(
            'Update the job'
        )
        .param('id',
              'The id of the job to update', paramType='path')
        .param(
            'body',
            'The properties to update.', dataType='JobUpdateParameters' , paramType='body'))

    @access.user
    def status(self, id, params):
        user = self.getCurrentUser()

        return {'status': self._model.status(user, id)}

    status.description = (Description(
            'Get the status of a job'
        )
        .param(
            'id',
            'The job id.', paramType='path'))


    @access.user
    def add_log_record(self, id, params):
        user = self.getCurrentUser()
        return self._model.add_log_record(user, id, json.load(cherrypy.request.body))

    add_log_record.description = None

    @access.user
    def log(self, id, params):
        user = self.getCurrentUser()
        offset = 0
        if 'offset' in params:
            offset = int(params['offset'])

        log_records = self._model.log_records(user, id, offset)

        return {'log': log_records}

    log.description = (Description(
            'Get log entries for cluster'
        )
        .param(
            'id',
            'The job to get log entries for.', paramType='path')
        .param(
            'offset',
            'The offset to start getting entiries at.', required=False, paramType='query'))
