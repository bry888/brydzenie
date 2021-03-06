# Copyright 2013 Google Inc. All Rights Reserved.

"""Lists customizable MySQL flags for Google Cloud SQL instances."""

from googlecloudsdk.calliope import base
from googlecloudsdk.core.util import list_printer
from googlecloudsdk.sql import util


class List(base.Command):
  """Lists customizable MySQL flags for Google Cloud SQL instances."""

  @util.ReraiseHttpException
  def Run(self, unused_args):
    """Lists customizable MySQL flags for Google Cloud SQL instances.

    Args:
      unused_args: argparse.Namespace, The arguments that this command was
          invoked with.

    Returns:
      A dict object that has the list of flag resources if the command ran
      successfully.
    Raises:
      HttpException: A http error response was received while executing api
          request.
      ToolException: An error other than http error occured while executing the
          command.
    """
    sql_client = self.context['sql_client']
    sql_messages = self.context['sql_messages']

    result = sql_client.flags.List(sql_messages.SqlFlagsListRequest())
    return iter(result.items)

  def Display(self, unused_args, result):
    list_printer.PrintResourceList('sql.flags', result)
