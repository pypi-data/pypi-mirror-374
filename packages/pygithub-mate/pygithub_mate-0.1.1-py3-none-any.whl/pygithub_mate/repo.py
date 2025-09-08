# -*- coding: utf-8 -*-

import typing as T
import os
import dataclasses
from pathlib import Path
from functools import cached_property

from func_args.api import REQ
from github import GithubException

from .emoji import Emoji
from .utils import calculate_sha256
from .base import (
    BaseGitHubApiRunner,
    TagAndRef,
    ReleaseAndTagAndRef,
)

if T.TYPE_CHECKING:
    from github.Repository import Repository
    from github.GitRef import GitRef
    from github.GitTag import GitTag
    from github.GitRelease import GitRelease
    from github.GitReleaseAsset import GitReleaseAsset


@dataclasses.dataclass(frozen=True)
class IsTagLatestOnDefaultBranchResult:
    """
    A container for the result of checking if a tag is the latest on the main branch.

    :param is_latest: True if the tag points to the latest commit on the default branch
    :param latest_commit_sha: SHA of the latest commit on the default branch
    :param tag_and_ref: The Git tag and reference objects for the tag
    """

    is_latest: bool = dataclasses.field()
    latest_commit_sha: str = dataclasses.field()
    tag_and_ref: "TagAndRef" = dataclasses.field()


@dataclasses.dataclass(frozen=True)
class BaseGitHubRepo(BaseGitHubApiRunner):
    """
    GitHub repository operations.

    Provides comprehensive repository management functionality including
    tag creation, deletion, branch operations, and commit tracking.
    Follows the command pattern with repository details stored as
    attributes and dynamic operations as method parameters.

    :param owner_name: GitHub repository owner/organization name
    :param repo_name: Repository name
    """

    owner_name: str = dataclasses.field(default=REQ)
    repo_name: str = dataclasses.field(default=REQ)

    @cached_property
    def repo_full_name(self) -> str:
        """
        Full name of the repository in the format "owner/repo".
        """
        return f"{self.owner_name}/{self.repo_name}"

    @cached_property
    def repo(self) -> "Repository":
        """
        GitHub repository object.
        """
        return self.gh.get_repo(self.repo_full_name)

    @cached_property
    def repo_default_branch_name(self) -> str:
        """
        Default branch name of the repository.
        """
        return self.repo.default_branch

    def get_latest_commit_sha_on_branch(
        self,
        branch_name: str,
    ) -> str:
        """
        Get the SHA of the latest commit on a specific branch.

        :param branch_name: Name of the branch to query

        :returns: SHA hash of the latest commit on the branch
        """
        return self.repo.get_branch(branch_name).commit.sha

    def get_latest_commit_sha_on_default_branch(self) -> str:
        """
        Get the SHA of the latest commit on the repository's default branch.

        :returns: SHA hash of the latest commit on the default branch
        """
        return self.get_latest_commit_sha_on_branch(
            branch_name=self.repo_default_branch_name,
        )

    @cached_property
    def latest_commit_sha_on_default_branch(self) -> str:
        """
        SHA of the latest commit on the repository's default branch.
        """
        return self.get_latest_commit_sha_on_default_branch()

    def get_git_tag_and_ref(
        self,
        tag_name: str,
    ) -> "TagAndRef":
        """
        Retrieve the Git tag and reference objects for the specified tag.

        Attempts to fetch both the Git tag object and the Git reference for the
        specified tag name. Handles cases where the tag or reference doesn't exist.

        :param tag_name: Name of the tag to retrieve

        :returns: TagAndRef object containing:
            - tag=None, ref=None if the tag reference doesn't exist
            - tag=None, ref=GitRef if the reference exists but the tag object doesn't
            - tag=GitTag, ref=GitRef if both exist

        :raises GithubException: For API errors other than 404 (not found)
        """
        # Try to get the tag reference first
        try:
            ref = self.repo.get_git_ref(f"tags/{tag_name}")
        except GithubException as e:
            if e.status == 404:
                return TagAndRef()  # Tag reference doesn't exist
            else:  # pragma: no cover
                raise e
        except Exception:
            raise

        # Get the SHA that the tag reference points to
        tag_sha = ref.object.sha

        # Try to get the actual tag object
        try:
            tag = self.repo.get_git_tag(tag_sha)
        except GithubException as e:
            if e.status == 404:
                # Reference exists but tag object doesn't
                return TagAndRef(tag=None, ref=ref)
            else:  # pragma: no cover
                raise
        except Exception:
            raise

        return TagAndRef(tag=tag, ref=ref)

    def is_tag_latest_on_default_branch(
        self,
        tag_name: str,
    ) -> "IsTagLatestOnDefaultBranchResult":
        """
        Check if the specified tag points to the latest commit on the default branch.

        Compares the commit SHA that the tag points to with the SHA of the latest
        commit on the default branch to determine if the tag is up-to-date.

        :param tag_name: Name of the tag to check

        :returns: IsTagLatestOnDefaultBranchResult object containing:
            - is_latest: True if tag is latest, False otherwise (or if tag doesn't exist)
            - latest_commit_sha: SHA of the latest commit on the default branch
            - tag_and_ref: TagAndRef object containing the Git tag and reference

        Note:
            If the tag doesn't exist, is_latest will be False.
        """
        latest_commit_sha = self.get_latest_commit_sha_on_default_branch()
        tag_and_ref = self.get_git_tag_and_ref(tag_name)
        if tag_and_ref.tag is None:
            # Tag doesn't exist, so it can't be latest
            flag = False
        else:
            # Compare tag's commit SHA with latest commit SHA
            flag = tag_and_ref.tag.object.sha == latest_commit_sha
        return IsTagLatestOnDefaultBranchResult(
            is_latest=flag,
            latest_commit_sha=latest_commit_sha,
            tag_and_ref=tag_and_ref,
        )

    def delete_tag(
        self,
        tag_name: str,
    ) -> bool:
        """
        Delete the existing Git tag reference if it exists.

        Attempts to find and delete the Git tag reference for the specified tag name.
        This removes the tag from the repository, making it available for recreation.

        :param tag_name: Name of the tag to delete

        :returns: True if a tag was found and deleted, False if no tag existed

        :raises GithubException: If the deletion fails due to API errors other than 404
        """
        self.info(f"{Emoji.DELETE}Delete tag '{tag_name}' if it exists ...")
        try:
            # Get the tag reference
            ref = self.repo.get_git_ref(f"tags/{tag_name}")
            ref.delete()  # Delete the tag reference
            self.info("✅Done")
            return True
        except GithubException as e:
            if e.status == 404:
                self.info("✅Tag does not exist, nothing to delete.")
                return False  # Tag doesn't exist, nothing to delete
            else:  # pragma: no cover
                raise e

    def create_tag_on_commit(
        self,
        commit_sha: str,
        tag_name: str,
        tag_message: str | None = None,
        create_git_tag_kwargs: dict[str, T.Any] | None = None,
    ) -> "TagAndRef":
        """
        Create a new Git tag and reference pointing to a specific commit.

        Creates both a Git tag object and a Git reference for the specified tag name.

        :param commit_sha: SHA of the commit to tag
        :param tag_name: Name for the new Git tag
        :param tag_message: Optional message for the tag (defaults to "Tag {tag_name}")
        :param create_git_tag_kwargs: Additional keyword arguments for tag creation

        :returns: TagAndRef object containing the created Git tag and reference
        """
        self.info(
            f"{Emoji.CREATE}Create tag '{tag_name}' on commit {self.shorten_sha(commit_sha)} ..."
        )
        if tag_message is None:
            tag_message = f"Tag {tag_name}"
        if create_git_tag_kwargs is None:
            create_git_tag_kwargs = {}

        # Create the Git tag object
        tag = self.repo.create_git_tag(
            tag=tag_name,
            message=tag_message,
            object=commit_sha,
            type="commit",
            **create_git_tag_kwargs,
        )

        # Create the Git reference pointing to the tag
        ref = self.repo.create_git_ref(
            ref=f"refs/tags/{tag_name}",
            sha=tag.sha,
        )
        self.info("✅Done")
        return TagAndRef(tag=tag, ref=ref)

    def create_tag_on_latest_commit_on_default_branch(
        self,
        tag_name: str,
        tag_message: str | None = None,
        create_git_tag_kwargs: dict[str, T.Any] | None = None,
    ) -> "TagAndRef":
        """
        Create a new Git tag and reference pointing to the latest commit on default branch.

        Creates both a Git tag object and a Git reference for the specified tag name.
        Always uses the latest commit from the default branch.

        :param tag_name: Name for the new Git tag
        :param tag_message: Optional message for the tag (defaults to "Tag {tag_name}")
        :param create_git_tag_kwargs: Additional keyword arguments for tag creation

        :returns: TagAndRef object containing the created Git tag and reference

        :raises GithubException: If tag creation fails (e.g., tag already exists)
        """
        # Use latest commit if none specified
        latest_commit_sha = self.latest_commit_sha_on_default_branch
        return self.create_tag_on_commit(
            commit_sha=latest_commit_sha,
            tag_name=tag_name,
            tag_message=tag_message,
            create_git_tag_kwargs=create_git_tag_kwargs,
        )

    def get_git_release(self, release_name: str) -> T.Optional["GitRelease"]:
        """
        Retrieve the GitHub release object for the specified release.

        Attempts to fetch the GitHub release associated with the release name.
        Returns None if the release doesn't exist.

        :param release_name: Name/tag of the release to retrieve

        :returns: The GitHub release object if it exists, None otherwise

        :raises GithubException: For API errors other than 404 (not found)
        :raises Exception: For other unexpected errors
        """
        try:
            return self.repo.get_release(release_name)
        except GithubException as e:
            if e.status == 404:
                return None  # Release doesn't exist
            else:  # pragma: no cover
                raise e
        except Exception as e:  # pragma: no cover
            raise e

    def put_tag_on_commit(
        self,
        commit_sha: str,
        tag_name: str,
        tag_message: str | None = None,
        create_git_tag_kwargs: dict[str, T.Any] | None = None,
    ) -> "TagAndRef":
        """
        Ensure a Git tag points to a specific commit, updating or recreating the tag as needed.

        If the tag exists and already points to the desired commit, no action is taken.
        If the tag exists but points to a different commit, it is deleted and recreated.
        If the tag does not exist, it is created.

        :param commit_sha: SHA of the commit to tag
        :param tag_name: Name for the new Git tag
        :param tag_message: Optional message for the tag (defaults to "Tag {tag_name}")
        :param create_git_tag_kwargs: Additional keyword arguments for tag creation

        :returns: TagAndRef object containing the Git tag and reference
        """

        def create_tag_on_commit():
            result = self.create_tag_on_commit(
                commit_sha=commit_sha,
                tag_name=tag_name,
                tag_message=tag_message,
                create_git_tag_kwargs=create_git_tag_kwargs,
            )
            return result

        self.info(f"--- Put tag on commit {self.shorten_sha(commit_sha)} ...")
        self.info("Check if tag exists ...")
        tag_and_ref = self.get_git_tag_and_ref(tag_name)
        if tag_and_ref.exists():
            self.info("Tag exists.")
            self.info("Check if tag points to the desired commit ...")
            if tag_and_ref.tag.object.sha == commit_sha:
                msg = "🛑Tag already points to the desired commit, no action needed."
                self.info(msg)
                return tag_and_ref
            else:
                self.info("Tag points to a different commit, deleting existing tag ...")
                self.delete_tag(tag_name)
                return create_tag_on_commit()
        else:
            return create_tag_on_commit()

    def put_tag_on_latest_commit_on_branch(
        self,
        branch_name: str,
        tag_name: str,
        tag_message: str | None = None,
        create_git_tag_kwargs: dict[str, T.Any] | None = None,
    ) -> "TagAndRef":
        """
        Ensure a Git tag points to the latest commit on the specified branch.

        :param branch_name: Name of the branch to get the latest commit from
        :param tag_name: Name for the Git tag
        :param tag_message: Optional message for the tag (defaults to "Tag {tag_name}")
        :param create_git_tag_kwargs: Additional keyword arguments for tag creation

        :returns: TagAndRef object containing the Git tag and reference
        """
        return self.put_tag_on_commit(
            commit_sha=self.get_latest_commit_sha_on_branch(branch_name),
            tag_name=tag_name,
            tag_message=tag_message,
            create_git_tag_kwargs=create_git_tag_kwargs,
        )

    def put_tag_on_latest_commit_on_default_branch(
        self,
        tag_name: str,
        tag_message: str | None = None,
        create_git_tag_kwargs: dict[str, T.Any] | None = None,
    ) -> "TagAndRef":
        """
        Ensure a Git tag points to the latest commit on the default branch.

        :param tag_name: Name for the Git tag
        :param tag_message: Optional message for the tag (defaults to "Tag {tag_name}")
        :param create_git_tag_kwargs: Additional keyword arguments for tag creation

        :returns: TagAndRef object containing the Git tag and reference
        """
        return self.put_tag_on_commit(
            commit_sha=self.get_latest_commit_sha_on_default_branch(),
            tag_name=tag_name,
            tag_message=tag_message,
            create_git_tag_kwargs=create_git_tag_kwargs,
        )

    def delete_release(
        self,
        release_name: str,
    ) -> bool:
        """
        Delete the existing GitHub release if it exists.

        Attempts to find and delete the GitHub release associated with the specified
        release name. This is typically called before creating a new release to
        ensure clean state.

        :param release_name: Name/tag of the release to delete

        :returns: True if a release was found and deleted, False if no release existed

        :raises GithubException: If the deletion fails due to API errors
        """
        self.info(f"{Emoji.DELETE}Delete release {release_name} ...")
        release = self.get_git_release(release_name)
        if release is not None:
            release.delete_release()  # Delete the existing release
            self.info("✅Done")
            return True
        else:
            self.info("✅Release does not exist, nothing to delete.")
            return False  # No release to delete

    def create_release(
        self,
        tag_name: str,
        release_name: str,
        release_message: str | None = None,
        create_git_release_kwargs: dict[str, T.Any] | None = None,
    ) -> "GitRelease":
        """
        Create a new GitHub release for the specified tag and name.

        Creates a GitHub release associated with the specified tag. The release will use
        the provided tag name, release name, and release message (with a default if not provided).

        :param tag_name: Name of the Git tag to associate with the release
        :param release_name: Name for the GitHub release
        :param release_message: Optional message for the release (defaults to "Release {release_name}")
        :param create_git_release_kwargs: Additional keyword arguments for release creation

        :returns: The created GitHub release object

        :raises GithubException: If release creation fails (e.g., release already exists)

        .. note::
            The associated tag must exist before creating a release.
        """
        self.info(
            f"{Emoji.CREATE}Create release '{release_name}' using tag '{tag_name}' ..."
        )
        if release_message is None:
            release_message = f"Release {release_name}"
        if create_git_release_kwargs is None:
            create_git_release_kwargs = {}
        release = self.repo.create_git_release(
            tag=tag_name,
            name=release_name,
            message=release_message,
            **create_git_release_kwargs,
        )
        self.info("✅Done")
        return release

    def put_release(
        self,
        commit_sha: str,
        tag_name: str,
        release_name: str,
        tag_message: str | None = None,
        release_message: str | None = None,
        create_git_tag_kwargs: dict[str, T.Any] | None = None,
        create_git_release_kwargs: dict[str, T.Any] | None = None,
    ):
        """
        Ensure a GitHub release and its associated tag point to a specific commit.

        This method performs comprehensive release management by coordinating both
        tag and release operations. It validates consistency between existing releases
        and tags, and recreates them as needed to ensure they point to the desired commit.

        The workflow handles multiple scenarios:
        - If no release exists: Creates tag and release
        - If release exists with matching tag: Validates tag points to desired commit
        - If release exists with different tag: Raises error to prevent conflicts
        - If tag exists but points elsewhere: Deletes both release and tag, then recreates

        :param commit_sha: SHA of the commit to associate with the release
        :param tag_name: Name of the Git tag to create or update
        :param release_name: Name of the GitHub release to create or update
        :param tag_message: Optional message for the tag (defaults to "Tag {tag_name}")
        :param release_message: Optional message for the release (defaults to "Release {release_name}")
        :param create_git_tag_kwargs: Additional keyword arguments for tag creation
        :param create_git_release_kwargs: Additional keyword arguments for release creation

        :returns: ReleaseAndTagAndRef object containing the release and tag objects

        :raises ValueError: If existing release has a different tag name than expected
        :raises GithubException: If any GitHub API operation fails
        :raises NotImplementedError: If release exists but its associated tag doesn't exist (unexpected state)
        """

        def create_tag_on_commit():
            return self.create_tag_on_commit(
                commit_sha=commit_sha,
                tag_name=tag_name,
                tag_message=tag_message,
                create_git_tag_kwargs=create_git_tag_kwargs,
            )

        def put_tag_on_commit():
            return self.put_tag_on_commit(
                commit_sha=commit_sha,
                tag_name=tag_name,
                tag_message=tag_message,
                create_git_tag_kwargs=create_git_tag_kwargs,
            )

        def create_release():
            self.info("Create new release ...")
            self.create_release(
                tag_name=tag_name,
                release_name=release_name,
                release_message=release_message,
                create_git_release_kwargs=create_git_release_kwargs,
            )

        self.info(f"--- Put release on commit {self.shorten_sha(commit_sha)} ...")
        self.info("Check if release exists ...")
        release = self.get_git_release(release_name)
        if release is None:
            self.info("Release does not exist.")
            put_tag_on_commit()
            create_release()
        else:
            self.info("Release already exists.")
            if release.tag_name != tag_name:
                raise ValueError(
                    f"Existing release '{release_name}' has tag '{release.tag_name}', "
                    f"expected '{tag_name}'. Please resolve the conflict manually.",
                )
            else:
                self.info("Check if tag exists ...")
                tag_and_ref = self.get_git_tag_and_ref(tag_name)
                if tag_and_ref.exists():
                    self.info("Tag already exists.")
                    self.info("Check if tag points to the desired commit ...")
                    if tag_and_ref.tag.object.sha == commit_sha:
                        msg = "🛑Tag already points to the desired commit, no action needed."
                        self.info(msg)
                        return ReleaseAndTagAndRef(
                            release=release,
                            tag_and_ref=tag_and_ref,
                        )
                    else:
                        sha = self.shorten_sha(tag_and_ref.tag.object.sha)
                        self.info(f"Tag points to a different commit {sha}.")
                        # Has to delete the release first before deleting tag
                        self.delete_release(release_name)
                        self.delete_tag(tag_name)
                        tag_and_ref = create_tag_on_commit()
                        release = create_release()
                        return ReleaseAndTagAndRef(
                            release=release,
                            tag_and_ref=tag_and_ref,
                        )
                else:
                    raise NotImplementedError(
                        "How could release exists, but tag does not exist?"
                    )

    def put_release_on_latest_commit_on_branch(
        self,
        branch_name: str,
        tag_name: str,
        release_name: str,
        tag_message: str | None = None,
        release_message: str | None = None,
        create_git_tag_kwargs: dict[str, T.Any] | None = None,
        create_git_release_kwargs: dict[str, T.Any] | None = None,
    ) -> "ReleaseAndTagAndRef":
        """
        Ensure a GitHub release and its associated tag point to the latest commit on the specified branch.

        :param tag_name: Name of the Git tag to create or update
        :param release_name: Name of the GitHub release to create or update
        :param branch_name: Name of the branch to get the latest commit from
        :param tag_message: Optional message for the tag (defaults to "Tag {tag_name}")
        :param release_message: Optional message for the release (defaults to "Release {release_name}")
        :param create_git_tag_kwargs: Additional keyword arguments for tag creation
        :param create_git_release_kwargs: Additional keyword arguments for release creation

        :returns: ReleaseAndTagAndRef object containing the release and tag objects
        """
        return self.put_release(
            commit_sha=self.get_latest_commit_sha_on_branch(branch_name),
            tag_name=tag_name,
            release_name=release_name,
            tag_message=tag_message,
            release_message=release_message,
            create_git_tag_kwargs=create_git_tag_kwargs,
            create_git_release_kwargs=create_git_release_kwargs,
        )

    def put_release_on_latest_commit_on_default_branch(
        self,
        tag_name: str,
        release_name: str,
        tag_message: str | None = None,
        release_message: str | None = None,
        create_git_tag_kwargs: dict[str, T.Any] | None = None,
        create_git_release_kwargs: dict[str, T.Any] | None = None,
    ) -> "ReleaseAndTagAndRef":
        """
        Ensure a GitHub release and its associated tag point to the latest commit on the default branch.

        :param tag_name: Name of the Git tag to create or update
        :param release_name: Name of the GitHub release to create or update
        :param tag_message: Optional message for the tag (defaults to "Tag {tag_name}")
        :param release_message: Optional message for the release (defaults to "Release {release_name}")
        :param create_git_tag_kwargs: Additional keyword arguments for tag creation
        :param create_git_release_kwargs: Additional keyword arguments for release creation

        :returns: ReleaseAndTagAndRef object containing the release and tag objects
        """
        return self.put_release(
            commit_sha=self.get_latest_commit_sha_on_default_branch(),
            tag_name=tag_name,
            release_name=release_name,
            tag_message=tag_message,
            release_message=release_message,
            create_git_tag_kwargs=create_git_tag_kwargs,
            create_git_release_kwargs=create_git_release_kwargs,
        )

    def put_assets_to_release(
        self,
        release: "GitRelease",
        path_to_name_mapping: dict["os.PathLike", str],
    ):
        """
        Upload assets to a release, replacing any existing assets with the same names only if their SHA-256 digest differs.

        For each asset name, if an asset already exists in the release:

        - The existing asset is deleted and replaced only if the SHA-256 digest of the new file is different.
        - If the digest matches, the asset is not re-uploaded.

        If the asset does not exist, it is uploaded.

        :param release: The GitHub release object to upload assets to
        :param path_to_name_mapping: A mapping of file paths to asset names for upload
        """
        existing_assets: dict[str, GitReleaseAsset] = {
            asset.name: asset for asset in release.get_assets()
        }
        for path, name in path_to_name_mapping.items():
            if name in existing_assets:
                asset = existing_assets[name]
                sha = f"sha256:{calculate_sha256(Path(path))}"
                if asset.digest != sha:
                    existing_assets[name].delete_asset()
                    release.upload_asset(path=str(Path(path)), label=name)
                else:
                    pass
            else:
                release.upload_asset(path=str(Path(path)), label=name)
