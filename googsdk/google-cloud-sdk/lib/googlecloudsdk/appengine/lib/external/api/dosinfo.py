# Copyright 2015 Google Inc. All Rights Reserved.
#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""DOS configuration tools.

Library for parsing dos.yaml files and working with these in memory.
"""



# WARNING: This file is externally viewable by our users.  All comments from
# this file will be stripped.  The docstrings will NOT.  Do not put sensitive
# information in docstrings.  If you must communicate internal information in
# this source file, please place them in comments only.

import re
import ipaddr

from googlecloudsdk.appengine.lib.external.api import appinfo
from googlecloudsdk.appengine.lib.external.api import validation
from googlecloudsdk.appengine.lib.external.api import yaml_builder
from googlecloudsdk.appengine.lib.external.api import yaml_listener
from googlecloudsdk.appengine.lib.external.api import yaml_object

_DESCRIPTION_REGEX = r'^.{0,499}$'

BLACKLIST = 'blacklist'
DESCRIPTION = 'description'
SUBNET = 'subnet'


class SubnetValidator(validation.Validator):
  """Checks that a subnet can be parsed and is a valid IPv4 or IPv6 subnet."""

  def Validate(self, value, unused_key=None):
    """Validates a subnet."""
    if value is None:
      raise validation.MissingAttribute('subnet must be specified')
    if not isinstance(value, basestring):
      raise validation.ValidationError('subnet must be a string, not \'%r\'' %
                                       type(value))
    try:
      ipaddr.IPNetwork(value)
    except ValueError:
      raise validation.ValidationError('%s is not a valid IPv4 or IPv6 subnet' %
                                       value)

    # Extra validation check since ipaddr accepts quad-dotted subnet masks.
    parts = value.split('/')
    if len(parts) == 2 and not re.match('^[0-9]+$', parts[1]):
      raise validation.ValidationError('Prefix length of subnet %s must be an '
                                       'integer (quad-dotted masks are not '
                                       'supported)' % value)

    return value


class MalformedDosConfiguration(Exception):
  """Configuration file for DOS API is malformed."""


class BlacklistEntry(validation.Validated):
  """A blacklist entry describes a blocked IP address or subnet."""
  ATTRIBUTES = {
      DESCRIPTION: validation.Optional(_DESCRIPTION_REGEX),
      SUBNET: SubnetValidator(),
  }


class DosInfoExternal(validation.Validated):
  """Describes the format of a dos.yaml file."""
  ATTRIBUTES = {
      appinfo.APPLICATION: validation.Optional(appinfo.APPLICATION_RE_STRING),
      BLACKLIST: validation.Optional(validation.Repeated(BlacklistEntry)),
  }


def LoadSingleDos(dos_info, open_fn=None):
  """Load a dos.yaml file or string and return a DosInfoExternal object.

  Args:
    dos_info: The contents of a dos.yaml file as a string, or an open file
      object.
    open_fn: Function for opening files. Unused.

  Returns:
    A DosInfoExternal instance which represents the contents of the parsed yaml
    file.

  Raises:
    MalformedDosConfiguration: The yaml file contains multiple blacklist
      sections.
    yaml_errors.EventError: An error occured while parsing the yaml file.
  """
  builder = yaml_object.ObjectBuilder(DosInfoExternal)
  handler = yaml_builder.BuilderHandler(builder)
  listener = yaml_listener.EventListener(handler)
  listener.Parse(dos_info)

  parsed_yaml = handler.GetResults()
  if not parsed_yaml:
    return DosInfoExternal()
  if len(parsed_yaml) > 1:
    raise MalformedDosConfiguration('Multiple blacklist: sections '
                                    'in configuration.')
  return parsed_yaml[0]
