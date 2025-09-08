# -*- coding: utf-8 -*-

"""
Base classes implementing the command pattern for GitHub operations.

This module provides foundational classes that follow the command pattern design,
where complex operations are encapsulated within objects that contain all the 
information needed to execute the operation. Each class acts as a self-contained
command that can be configured with parameters, executed independently, and 
provides clear interfaces for logging and error handling.

The command pattern is particularly well-suited for GitHub API operations because:

- It encapsulates API credentials, repository information, and operation parameters
- It provides consistent logging and error handling across different operations
- It enables easy testing by allowing dependency injection (like custom printers)
- It supports caching of expensive resources (like API clients) through properties
- It makes complex workflows readable by breaking them into discrete, reusable commands

Classes in this module serve as building blocks for more specialized GitHub 
operations like release management, tag creation, and repository synchronization.
"""

import typing as T
import dataclasses
from functools import cached_property

from func_args.api import BaseFrozenModel, REQ
from github import Github

from .typehint import T_PRINTER

if T.TYPE_CHECKING:  # pragma: no cover
    from github.GitRef import GitRef
    from github.GitTag import GitTag
    from github.GitRelease import GitRelease


@dataclasses.dataclass(frozen=True)
class BaseLogger(BaseFrozenModel):
    """
    Base logging functionality with configurable output control.

    Provides simple message logging with optional verbosity control and
    customizable output destination following the command pattern.

    :param verbose: Enable or disable message output
    :param printer: Function to handle message output (defaults to print)
    """

    verbose: bool = dataclasses.field(default=True)
    printer: T_PRINTER = dataclasses.field(default=print)

    def info(self, msg: str):
        """
        Log an informational message if verbose mode is enabled.

        This method provides controlled logging output that can be disabled via the verbose flag.
        It follows specific guidelines for when and how to log messages in workflow methods.

        **When to Add Logging:**

        - **Simple API wrappers**: Do NOT add logging to methods that are just wrappers around
          single API calls (e.g., get_git_tag_and_ref, delete_tag, create_tag_on_commit)
        - **Complex workflows**: DO add logging to methods that involve multi-step decision-making
          and perform different actions based on conditions (e.g., put_tag_on_commit, put_release)
        - **First log pattern**: For complex workflow methods, the first log message should
          typically follow the pattern: "--- ${description of what this function does}"

        **Examples:**
            Complex workflow logging::

                self.info("--- Put tag on commit abcd123 ...")
                self.info("Check if tag exists ...")
                self.info("Tag exists.")
                self.info("Check if tag points to the desired commit ...")

        :param msg: Message to log to the configured printer function

        .. note::
            This approach keeps logs focused on meaningful workflow steps while avoiding
            noise from simple operations.
        """
        if self.verbose:
            self.printer(msg)

    def shorten_sha(self, sha: str) -> str:
        """
        Shorten a Git SHA to its first 7 characters for display.

        :param sha: Full Git SHA string

        :returns: Shortened SHA (first 7 characters)
        """
        return sha[:7]


@dataclasses.dataclass(frozen=True)
class BaseGitHubApiRunner(BaseLogger):
    """
    Base class for GitHub API operations with authentication and logging.

    Combines logging capabilities with GitHub API client management.
    Stores GitHub API configuration as attributes and provides a cached
    GitHub client instance following the command pattern.

    :param github_kwargs: Configuration parameters for GitHub API client
    :param data: Additional data storage for derived classes
    """

    github_kwargs: dict[str, T.Any] = dataclasses.field(default=REQ)
    data: dict[str, T.Any] = dataclasses.field(default_factory=dict)

    @cached_property
    def gh(self) -> "Github":
        """
        GitHub API client instance.

        :returns: Configured GitHub API client using stored credentials
        """
        return Github(**self.github_kwargs)


@dataclasses.dataclass(frozen=True)
class TagAndRef:
    """
    A container for holding a Git tag and its corresponding reference.

    :param tag: The Git tag object (or None if it doesn't exist)
    :param ref: The Git reference object (or None if it doesn't exist)
    """

    tag: T.Optional["GitTag"] = dataclasses.field(default=None)
    ref: T.Optional["GitRef"] = dataclasses.field(default=None)

    def exists(self) -> bool:
        """
        Check if the Git tag exists.

        :returns: True if tag is not None, False otherwise
        """
        return self.tag is not None


@dataclasses.dataclass(frozen=True)
class ReleaseAndTagAndRef:
    """
    A container for holding a GitHub release, its corresponding tag, and reference.

    :param release: The GitHub release object (or None if it doesn't exist)
    :param tag_and_ref: The TagAndRef object containing the tag and reference
    """

    release: T.Optional["GitRelease"] = dataclasses.field(default=None)
    tag_and_ref: "TagAndRef" = dataclasses.field(default=REQ)

    def exists(self) -> bool:
        """
        Check if the GitHub release exists.
        """
        return self.release is not None
