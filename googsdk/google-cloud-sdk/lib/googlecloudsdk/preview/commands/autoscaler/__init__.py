# Copyright 2014 Google Inc. All Rights Reserved.

"""The command group for the Autoscaler CLI."""

import argparse

from googlecloudsdk.core import log
from googlecloudsdk.core import properties

from googlecloudsdk.third_party.apis.autoscaler import v1beta2 as autoscaler_v1beta2
from googlecloudsdk.third_party.apis.autoscaler.v1beta2 import autoscaler_v1beta2_messages as messages_v2
from googlecloudsdk.calliope import actions
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import resolvers
from googlecloudsdk.core import resources
from googlecloudsdk.core.credentials import store


class Autoscaler(base.Group):
  """Manage autoscalers of cloud resources."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--zone', required=True, help='Autoscaler Zone name',
        action=actions.StoreProperty(properties.VALUES.compute.zone))

  @exceptions.RaiseToolExceptionInsteadOf(store.Error)
  def Filter(self, context, args):
    log.warn('This preview command will be removed soon.')
    log.warn('These managed infrastructure preview commands have been migrated '
             'to "gcloud compute instance-groups managed" command group.')
    log.warn('See https://cloud.google.com/sdk/gcloud/reference/ for more '
             'details.')

    client = autoscaler_v1beta2.AutoscalerV1beta2(
        get_credentials=False, http=self.Http())
    context['autoscaler_messages_module'] = messages_v2


    context['autoscaler-client'] = client
    resources.SetParamDefault(
        api='compute',
        collection=None,
        param='project',
        resolver=resolvers.FromProperty(properties.VALUES.core.project))
    resources.SetParamDefault(
        api='autoscaler',
        collection=None,
        param='project',
        resolver=resolvers.FromProperty(properties.VALUES.core.project))
    resources.SetParamDefault(
        api='autoscaler',
        collection=None,
        param='zone',
        resolver=resolvers.FromProperty(properties.VALUES.compute.zone))
    resources.SetParamDefault(
        api='replicapool',
        collection=None,
        param='project',
        resolver=resolvers.FromProperty(properties.VALUES.core.project))
    resources.SetParamDefault(
        api='replicapool',
        collection=None,
        param='zone',
        resolver=resolvers.FromProperty(properties.VALUES.compute.zone))

    context['autoscaler_resources'] = resources
    return context
