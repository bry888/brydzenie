# Copyright 2015 Google Inc. All Rights Reserved.
"""instance-groups unmanaged set-named-ports command.

It's an alias for the instance-groups set-named-ports command.
"""
from googlecloudsdk.compute.lib import instance_groups_utils


class SetNamedPorts(instance_groups_utils.InstanceGroupSetNamedPorts):
  pass
