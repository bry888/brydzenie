# Copyright 2015 Google Inc. All Rights Reserved.
"""Convenience functions for dealing with gaia accounts."""

from googlecloudsdk.core import exceptions as core_exceptions

from apitools.base.py import credentials_lib
from googlecloudsdk.core.credentials import store as c_store

# API restriction: account names cannot be greater than 32 characters.
_MAX_ACCOUNT_NAME_LENGTH = 32


class GaiaException(core_exceptions.Error):
  """GaiaException is for non-code-bug errors in gaia_utils."""


def MapGaiaEmailToDefaultAccountName(email):
  """Returns the default account name given a GAIA email."""
  # Maps according to following rules:
  # 1) Remove all characters following and including '@'.
  # 2) Lowercase all alpha characters.
  # 3) Replace all non-alphanum characters with '_'.
  # 4) Prepend with 'g' if the username does not start with an alpha character.
  # 5) Truncate the username to 32 characters.
  account_name = email.partition('@')[0].lower()
  if not account_name:
    raise GaiaException('Invalid email address [{email}].'
                        .format(email=email))
  account_name = ''.join(
      [char if char.isalnum() else '_' for char in account_name])
  if not account_name[0].isalpha():
    account_name = 'g' + account_name
  return account_name[:_MAX_ACCOUNT_NAME_LENGTH]


def GetDefaultAccountName(http):
  return MapGaiaEmailToDefaultAccountName(GetAuthenticatedGaiaEmail(http))


def GetAuthenticatedGaiaEmail(http):
  """Get the email associated with the active credentails."""
  # If there are no credentials in the c_store c_store.Load() will throw an
  # error with a nice message on how to get credentials.
  email = credentials_lib.GetUserinfo(c_store.Load(), http).get('email')
  # GetUserinfo depends on the token having either the userinfo.email or
  # userinfo.profile scope for the given token. Otherwise it will return empty
  # JSON and email will be None.
  if not email:
    raise c_store.AuthenticationException(
        'An error occured while obtaining your email from your active'
        ' credentials.')
  return email
