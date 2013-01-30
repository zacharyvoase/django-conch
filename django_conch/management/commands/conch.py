from optparse import make_option
import json
import os

from django.core.management.base import BaseCommand
from django.db.models.loading import get_models, get_apps
from twisted.application import internet, service
from twisted.conch.insults import insults
from twisted.conch.manhole import ColoredManhole
from twisted.conch.manhole_ssh import ConchFactory, TerminalRealm
from twisted.cred import portal

from django_conch.checker import DjangoSuperuserCredChecker


def make_namespace():
    ns = {}
    for app in get_apps():
        for model in get_models(app):
            ns[model.__name__] = model
            ns[model._meta.app_label + '_' + model._meta.object_name] = model
    return ns


def make_service(args):
    checker = DjangoSuperuserCredChecker()

    def chainProtocolFactory():
        return insults.ServerProtocol(
            args['protocol_factory'],
            *args.get('protocol_args', ()),
            **args.get('protocol_kwargs', {}))

    realm = TerminalRealm()
    realm.chainedProtocolFactory = chainProtocolFactory
    ptl = portal.Portal(realm, [checker])
    f = ConchFactory(ptl)
    return internet.TCPServer(args['ssh_port'], f)


application = service.Application("Django Secure Shell")

if '_DJANGO_CONCH_CONFIG' in os.environ:
    config = json.loads(os.environ['_DJANGO_CONCH_CONFIG'])
    namespace = make_namespace()
    make_service({'protocol_factory': ColoredManhole,
                  'protocol_kwargs': {'namespace': namespace},
                  'ssh_port': config['ssh_port']}).setServiceParent(application)


class Command(BaseCommand):

    help = 'Run a Django secure shell server on <port>'
    option_list = BaseCommand.option_list + (
        make_option('-p', '--port', type='int',
                    help='The port number on which to listen for SSH connections'),
    )

    def handle(self, *args, **kwargs):
        cmd = ['twistd', '-noy', __file__]
        os.environ['_DJANGO_CONCH_CONFIG'] = json.dumps({
            'ssh_port': kwargs['port']})
        os.execvp('twistd', cmd)
