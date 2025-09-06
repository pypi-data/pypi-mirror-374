"""
Copyright (C) 2024, Pelican Project, Morgridge Institute for Research

Licensed under the Apache License, Version 2.0 (the "License"); you
may not use this file except in compliance with the License.  You may
obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


class PelicanException(RuntimeError):
    """
    Base class for all Pelican-related failures
    """


class BadDirectorResponse(PelicanException):
    """
    The director response did not include the proper headers
    """


class NoAvailableSource(PelicanException):
    """
    No source endpoint is currently available for the requested object
    """


class InvalidMetadata(PelicanException):
    """
    No Pelican metadata was found for the federation
    """


class NoCollectionsUrl(PelicanException):
    """
    No collections URL was found in the director response
    """


class InvalidDestinationURL(PelicanException):
    """
    The destination URL is invalid or has an empty path
    """


class TokenIteratorException(PelicanException):
    """
    Failed to fetch tokens due to iterator error
    """


class NoCredentialsException(PelicanException):
    """
    Credential is required but was not discovered
    """
