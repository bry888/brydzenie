# Copyright 2013 Google Inc. All Rights Reserved.
"""Restarts a Cloud SQL instance."""

from googlecloudsdk.core import log

from googlecloudsdk.calliope import base
from googlecloudsdk.core import remote_completion
from googlecloudsdk.sql import util


@base.ReleaseTracks(base.ReleaseTrack.GA)
class Restart(base.Command):
  """Restarts a Cloud SQL instance."""

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    instance = parser.add_argument(
        'instance',
        help='Cloud SQL instance ID.')
    cli = Restart.GetCLIGenerator()
    instance.completer = (remote_completion.RemoteCompletion.
                          GetCompleterForResource('sql.instances', cli))
    parser.add_argument(
        '--async',
        action='store_true',
        help='Do not wait for the operation to complete.')

  @util.ReraiseHttpException
  def Run(self, args):
    """Restarts a Cloud SQL instance.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      A dict object representing the operations resource describing the restart
      operation if the restart was successful.
    Raises:
      HttpException: A http error response was received while executing api
          request.
      ToolException: An error other than http error occured while executing the
          command.
    """
    sql_client = self.context['sql_client']
    sql_messages = self.context['sql_messages']
    resources = self.context['registry']

    util.ValidateInstanceName(args.instance)
    instance_ref = resources.Parse(args.instance, collection='sql.instances')

    result = sql_client.instances.Restart(
        sql_messages.SqlInstancesRestartRequest(
            project=instance_ref.project,
            instance=instance_ref.instance))

    operation_ref = resources.Create(
        'sql.operations',
        operation=result.operation,
        project=instance_ref.project,
        instance=instance_ref.instance,
    )

    if args.async:
      return sql_client.operations.Get(operation_ref.Request())

    util.WaitForOperation(
        sql_client, operation_ref, 'Restarting Cloud SQL instance')

    log.status.write(
        'Restarted [{resource}].\n'.format(resource=instance_ref))

  # pylint: disable=unused-argument
  def Display(self, args, result):
    """Display prints information about what just happened to stdout.

    Args:
      args: The same as the args in Run.
      result: A dict object representing the operations resource describing the
          restart operation if the restart was successful.
    """
    self.format(result)
