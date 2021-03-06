# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for listing autoscalers."""

from googlecloudsdk.core import log
from googlecloudsdk.core import properties

from apitools.base import py as apitools_base
from apitools.base.py import exceptions
from googlecloudsdk.calliope import exceptions as calliope_exceptions
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.core.util import list_printer
from googlecloudsdk.preview.lib.autoscaler import util


class ListAutoscalers(base_classes.BaseCommand):
  """List Autoscaler instances."""

  # TODO(user): Add --limit flag.
  def Run(self, args):
    log.warn('Please use instead [gcloud compute instance-groups '
             'managed list].')
    client = self.context['autoscaler-client']
    messages = self.context['autoscaler_messages_module']
    resources = self.context['autoscaler_resources']
    try:
      request = messages.AutoscalerAutoscalersListRequest()
      request.project = properties.VALUES.core.project.Get(required=True)
      request.zone = resources.Parse(
          args.zone, collection='compute.zones').zone
      return apitools_base.YieldFromList(client.autoscalers, request)

    except exceptions.HttpError as error:
      raise calliope_exceptions.HttpException(util.GetErrorMessage(error))
    except ValueError as error:
      raise calliope_exceptions.HttpException(error)

  def Display(self, unused_args, result):
    list_printer.PrintResourceList('autoscaler.instances', result)
