# Copyright 2015 Google Inc. All Rights Reserved.

"""Implementation of gcloud bigquery datasets list.
"""

from googlecloudsdk.core import properties

from apitools.base.py import list_pager
from googlecloudsdk.bigquery import commands
from googlecloudsdk.bigquery.lib import bigquery
from googlecloudsdk.calliope import base
from googlecloudsdk.core.util import list_printer


class DatasetsList(base.Command):
  """List datasets in the current project.
  """

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    parser.add_argument('--all', help='List even hidden datasets.')
    parser.add_argument(
        '--limit',
        type=int,
        default=bigquery.DEFAULT_RESULTS_LIMIT,
        help='The maximum number of datasets to list')

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace, All the arguments that were provided to this
        command invocation.

    Returns:
      A list of bigquery_messages.DatasetsValueListEntry objects. Each such
      object has the following form:
          {'kind': 'bigquery#dataset',
           'datasetReference': {'projectId': '$PROJ', 'datasetId': '$DS'},
           'id': '$PROJ:$DS'}
    """
    apitools_client = self.context[commands.APITOOLS_CLIENT_KEY]
    bigquery_messages = self.context[commands.BIGQUERY_MESSAGES_MODULE_KEY]
    project_id = properties.VALUES.core.project.Get(required=True)
    return list_pager.YieldFromList(
        apitools_client.datasets,
        bigquery_messages.BigqueryDatasetsListRequest(projectId=project_id),
        args.limit,
        batch_size=None,  # Use server default.
        field='datasets')

  def Display(self, args, result):
    """This method is called to print the result of the Run() method.

    Args:
      args: The arguments that command was run with.
      result: The value returned from the Run() method.
    """
    list_printer.PrintResourceList('bigquery.datasets', result)
