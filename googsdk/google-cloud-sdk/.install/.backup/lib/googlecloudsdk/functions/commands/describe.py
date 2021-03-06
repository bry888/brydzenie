# Copyright 2015 Google Inc. All Rights Reserved.

"""'functions describe' command."""

from googlecloudsdk.core import properties

from apitools.base import py as apitools_base
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as base_exceptions
from googlecloudsdk.functions.lib import util


class Describe(base.Command):
  """Show description of a function."""

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    parser.add_argument(
        'name', help='The name of the function to describe.',
        type=util.ParseFunctionName)

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      The specified function with its description and configured filter.
    """
    client = self.context['functions_client']
    messages = self.context['functions_messages']
    project = properties.VALUES.core.project.Get(required=True)
    name = 'projects/{0}/regions/{1}/functions/{2}'.format(
        project, args.region, args.name)

    try:
      # TODO(user): Use resources.py here after b/21908671 is fixed.
      return client.projects_regions_functions.Get(
          messages.CloudfunctionsProjectsRegionsFunctionsGetRequest(name=name))
    except apitools_base.HttpError as error:
      raise base_exceptions.HttpException(util.GetError(error))

  def Display(self, unused_args, result):
    """This method is called to print the result of the Run() method.

    Args:
      unused_args: The arguments that command was run with.
      result: The value returned from the Run() method.
    """
    self.format(result)
