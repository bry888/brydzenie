# Copyright 2013 Google Inc. All Rights Reserved.

"""Provide commands for working with Cloud SQL instance operations."""

from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import remote_completion


@base.ReleaseTracks(base.ReleaseTrack.GA)
class Operations(base.Group):
  """Provide commands for working with Cloud SQL instance operations.

  Provide commands for working with Cloud SQL instance operations, including
  listing and getting information about instance operations of a Cloud SQL
  instance.
  """

  @staticmethod
  def Args(parser):
    instance = parser.add_argument(
        '--instance',
        '-i',
        help='Cloud SQL instance ID.')
    cli = Operations.GetCLIGenerator()
    instance.completer = (remote_completion.RemoteCompletion.
                          GetCompleterForResource('sql.instances', cli))

  def Filter(self, tool_context, args):
    if not args.instance:
      raise exceptions.ToolException('argument --instance/-i is required')
