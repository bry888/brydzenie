# Copyright 2015 Google Inc. All Rights Reserved.
"""gcloud datastore emulator start command."""

from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.emulators.lib import datastore_util
from googlecloudsdk.emulators.lib import util


class Start(base.Command):
  """Start a local datastore emulator.

  This command starts a local datastore emulator.
  """

  detailed_help = {
      'DESCRIPTION': '{description}',
      'EXAMPLES': """\
          To start a local datastore emulator, run:

            $ {command} DATA-DIR
          """,
  }

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--host-port',
        required=False,
        type=arg_parsers.HostPort.Parse,
        help='The host:port to which the emulator should be bound.')
    parser.add_argument(
        '--store-on-disk',
        required=False,
        type=bool,
        default=True,
        help='Whether data should be persisted to disk.')

  def Run(self, args):
    if not args.host_port:
      args.host_port = arg_parsers.HostPort.Parse(datastore_util.GetHostPort())
    args.host_port.host = args.host_port.host or 'localhost'

    datastore_util.PrepareGCDDataDir(args.data_dir)
    datastore_process = datastore_util.StartGCDEmulator(args)
    datastore_util.WriteGCDEnvYaml(args)
    util.PrefixOutput(datastore_process, 'datastore')
