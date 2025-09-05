"""This module contains the definition of a manifest class.

A manifest object should be instantiated for each processing step of the data
preprocessing and augmentation of the Impresso project.
"""

import copy
import json
import logging
import os
from typing import Any, Union, Optional
from git import Repo
from impresso_essentials.io.s3 import get_storage_options, upload_to_s3
from impresso_essentials.utils import (
    validate_against_schema,
    get_provider_for_alias,
    get_src_info_for_alias,
    PARTNER_TO_MEDIA,
    timestamp,
    DataStage,
    validate_stage
)
from impresso_essentials.versioning.data_statistics import MediaStatistics
from impresso_essentials.versioning.helpers import (
    read_manifest_from_s3,
    increment_version,
    validate_version,
    init_media_info,
    media_list_from_mft_json,
    read_manifest_from_s3_path,
    add_media_source_metadata,
    sort_media_list_years_and_titles,
)
from impresso_essentials.versioning.git_utils import (
    clone_git_repo,
    write_and_push_to_git,
    write_dump_to_fs,
    get_head_commit_url,
)

logger = logging.getLogger(__name__)

GIT_REPO_SSH_URL = "git@github.com:impresso/impresso-data-release.git"
REPO_BRANCH_URL = "https://github.com/impresso/impresso-data-release/tree/{branch}"
IMPRESSO_STORAGEOPT = get_storage_options()


class DataManifest:

    def __init__(
        self,
        data_stage: Union[DataStage, str],
        s3_output_bucket: str,  # including partition
        # str path to the local repo corresponding to the code used for processing
        git_repo: str | Repo,
        temp_dir: str,
        # S3 bucket of the previous stage, None if stage='canonical'
        s3_input_bucket: Optional[str] = None,
        # to directly provide the next version
        new_version: Optional[str] = None,
        # to indicate if patch in later stages
        is_patch: Optional[bool] = False,
        # to indiate patch in canonical/rebuilt
        patched_fields: Union[dict[str, list[str]], list[str], None] = None,
        # directly provide the s3 path of the manifest to use as base
        previous_mft_path: Optional[str] = None,
        only_counting: Optional[bool] = False,
        notes: Optional[str] = None,
        push_to_git: Optional[bool] = None,
        relative_git_path: Optional[str] = None,
        model_id: Optional[str] = "",
        run_id: Optional[str] = "",
    ) -> None:

        self.stage = validate_stage(data_stage)
        self.input_bucket_name = s3_input_bucket
        self.only_counting = only_counting
        self.modified_info = False
        self.push_to_git = push_to_git
        self.model_id = model_id
        self.run_id = run_id

        # s3_output_bucket is the path to actual data partition
        s3_output_bucket = s3_output_bucket.replace("s3://", "")
        if "/" in s3_output_bucket:
            self.output_bucket_name = s3_output_bucket.split("/")[0]
            self.output_s3_partition = "/".join(s3_output_bucket.split("/")[1:])
        else:
            # for data preparation, the manifest is at the top level of the bucket
            self.output_bucket_name, self.output_s3_partition = s3_output_bucket, None

        # define the relative path within the git repository
        if relative_git_path:
            self.output_git_partition = relative_git_path
        else:
            self.output_git_partition = self.output_s3_partition
        self._print_git_path_warning()

        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)
        self.notes = notes

        # get code version used for processing.
        self.commit_url = get_head_commit_url(git_repo)

        # init attributes of previous manifest
        self._prev_mft_s3_path = previous_mft_path
        self.prev_version = None

        # init attribute of input_manifest
        self.input_manifest_s3_path = None

        # if user already knows the target version
        self.version = None if new_version is None else validate_version(new_version)

        # if update is a patch, patched fields should be provided
        # either as list of fields or dict mapping each media to its patched fields
        self.patched_fields = patched_fields
        self.is_patch = is_patch or (patched_fields is not None)

        # dict mapping from title to year to np_stat,
        # where the statistics will be aggregated during the processing
        self._processing_stats = {}
        self.manifest_data = {}
        self._generation_date = None

        logger.info("DataManifest for %s stage successfully initialized.", self.stage)

    @property
    def _input_stage(self) -> DataStage:
        """Get the DataStage associated to the input data of this manifest.

        Returns:
            DataStage: The input DataStage.
        """
        if self.stage in [
            DataStage.REBUILT,
            DataStage.CANONICAL,
            DataStage.PASSIM,
            DataStage.MYSQL_CIS,
            DataStage.EMB_IMAGES,
        ]:
            # datastages that directly follow or use canonical data
            return DataStage.CANONICAL
        if self.stage in [DataStage.TEXT_REUSE]:
            # text reuse uses passim rebuilt text
            return DataStage.PASSIM
        # all other stages use the rebuilt as input
        return DataStage.REBUILT

    @property
    def _manifest_filename(self) -> str:
        """Get the manifest filename based on convention stage-value_vM-m-p.json.

        Returns:
            str: The manifest filename.
        """
        if self.version is None:
            logger.warning("The manifest name is only available once the version is.")
            return ""

        return f"{self.stage.value}_{self.version.replace('.', '-')}.json"

    @property
    def output_mft_s3_path(self) -> str:
        """Get this manifest's output S3 path based on its output bucket.

        The manifest will be uploaded to the S3 bucket and partition corresponding
        to the value provided for its input argument `s3_output_bucket`.
        If the versison attribute for this manifest is not defined, the S3 output
        path cannot be provided and the empty string will be returned.

        Returns:
            str: Full S3 path of this manifest if the version is already defined,
                the empty string otherwise.
        """
        if self.version is None:
            logger.warning("The manifest s3 path is only available once the version is.")
            return ""

        if self.output_s3_partition is not None:
            s3_path = os.path.join(self.output_s3_partition, self._manifest_filename)
        else:
            s3_path = self._manifest_filename

        full_s3_path = os.path.join("s3://", self.output_bucket_name, s3_path)

        # sanity check
        if (
            self._prev_mft_s3_path is not None
            and self.output_bucket_name in self._prev_mft_s3_path
        ):
            assert (
                self._prev_mft_s3_path.split(f"/{self.stage.value}_v")[0]
                == full_s3_path.split(f"/{self.stage.value}_v")[0]
            ), "Mismatch between s3 path of previous & current version of manifest."

        return full_s3_path

    def _print_git_path_warning(self) -> None:
        if self.push_to_git and self.output_git_partition is not None:
            out_git_path = self._get_out_path_within_repo()
            info_msg = (
                "Note that once generated, this manifest will be pushed to "
                f"the following path {out_git_path} within the git repository."
            )
            logger.info(info_msg)
            print(info_msg)

    def _get_prev_version_manifest(self) -> Union[dict[str, Any], None]:
        """Find and return the previous version manifest of this DataStage and bucket.

        Will try to find the previous manifest in the provided S3 output bucket
        partition, unless `self._prev_mft_s3_path` is defined, in which case it reads
        it from S3 and returns it.

        Returns:
            Union[dict[str, Any], None]: The previous version of the manifest,
                if available, otherwise None.
        """
        # previous version manifest is in the output bucket, except when:
        # _prev_mft_s3_path is defined upon instantiation, then use it directly
        logger.debug("Reading the previous version of the manifest from S3.")
        if self._prev_mft_s3_path is None:
            (self._prev_mft_s3_path, prev_v_mft) = read_manifest_from_s3(
                self.output_bucket_name, self.stage, self.output_s3_partition
            )
        else:
            prev_v_mft = read_manifest_from_s3_path(self._prev_mft_s3_path)

        if self._prev_mft_s3_path is None or prev_v_mft is None:
            logger.info(
                "No existing previous version of this manifest. Version will be v0.0.1"
            )
            return None

        self.prev_version = prev_v_mft["mft_version"]

        return prev_v_mft

    def _get_current_version(self, addition: bool = False) -> str:
        """Get the current version of manifest for the data stage.

        Versions are of format vM.m.p (=Major.minor.patch), where:
            - M changes in the case of additions to the collection (new “title-year” keys).
            - m when modifications are made to existing data (keeping the same ‘title-year’
                keys,by re-ingestion (not field-specific modifications).
            - p when a patch or small fix is made, modifying one or more fields for several
                titles, leaving the rest of the data unchanged.
                When `self.is_patch` is True or `self.patched_fields` is defined.
                Also when `self.only_counting` is set to True and no counts changed since
                the previous manifest version.

        If no previous version exists, the version returned will be v0.0.1.

        Args:
            addition (bool, optional): Whether new data was added during the processing.
                Defaults to False.

        Returns:
            str: The current version string.
        """
        if self.prev_version is None:
            # First manifest for this data stage.
            return "v0.0.1"

        logger.debug(
            "Addition: %s, self.is_patch: %s, self.only_counting: %s, self.modified_info: %s",
            addition,
            self.is_patch,
            self.only_counting,
            self.modified_info,
        )

        if addition:
            # any new title-year pair was added during processing
            logger.info("Addition is True, major version increase.")
            print("Addition is True, major version increase.")
            return increment_version(self.prev_version, "major")

        if self.is_patch or self.patched_fields is not None:
            # processing is a patch
            logger.info("Computation is patch, patch version increase.")
            print("Computation is patch, patch version increase.")
            return increment_version(self.prev_version, "patch")

        if self.only_counting is not None and self.only_counting and not self.modified_info:
            # manifest computed to count contents of a bucket
            # (eg. after a copy from one bucket to another)
            logger.info("Only counting, and no modified info, patch version increase.")
            print("Only counting, and no modified info, patch version increase.")
            return increment_version(self.prev_version, "patch")

        # modifications were made by re-ingesting/re-generating the data, not patching
        logger.info("No additional keys or patch, but modified info, minor version increase.")
        print("No additional keys or patch, but modified info, minor version increase.")
        return increment_version(self.prev_version, "minor")

    def _get_input_data_overall_stats(self) -> list[dict[str, Any]]:
        """Return the `"overall_statistics"` of the input manifest or an empty list.

        The input manifest is the manifest versioning the data used as input to the
        processing used to generate data of this manifest's `DataStage`.
        If `s3_input_bucket` is defined, find and read this manifest on S3, and extract
        its `"overall_statistics"`.
        When `self.stage=DataStage.CANONICAL`, no previous stage exists, so the empty
        list will be returned.
        For other stages, the `"overall_statistics"` for all upstream stages will be
        contained in the returned list.

        Returns:
            list[dict[str, Any]]: Input manifest's `"overall_statistics"` or empty list.
        """
        # reading the input manifest only if the input s3 bucket is defined
        if self.input_bucket_name is not None:
            logger.debug("Reading the input data's manifest from S3.")

            # only the rebuilt uses the canonical as input
            # text-reuse's input stage, passim rebuilt has various partitions
            split_path = self.input_bucket_name.replace("s3://", "").split("/")
            (self.input_manifest_s3_path, input_v_mft) = read_manifest_from_s3(
                split_path[0], self._input_stage, "/".join(split_path[1:])
            )

            if input_v_mft is not None:
                # assert self.input_manifest_s3_path == input_v_mft["mft_s3_path"]
                # fetch the overall statistics from the input data (it's a list!)
                if self.stage != DataStage.CANONICAL:
                    return input_v_mft["overall_statistics"]
        return []

    def _get_out_path_within_repo(
        self,
        folder_prefix: str = "data-processing-versioning",
        stage: Optional[DataStage] = None,
    ) -> str:
        """Get the output path within the "impresso-data-release" repository.

        Args:
            folder_prefix (str, optional): Folder prefix to use within the repository.
                Defaults to "data-processing-versioning".
            stage (Optional[DataStage], optional): DataStage to consider if not
                `self.stage`. Defaults to None.

        Returns:
            str: The output path within the repository based on `self.stage`.
        """
        stage = stage if stage is not None else self.stage
        # if stage in ["canonical", "rebuilt", "passim", "evenized-rebuilt"]: --> TODO remove evenized
        if stage in ["canonical", "rebuilt", "passim"]:
            sub_folder = "data-preparation"
        elif "solr" in stage or "mysql" in stage:
            sub_folder = "data-ingestion"
        else:
            sub_folder = os.path.join("data-processing", self.output_git_partition)

        return os.path.join(folder_prefix, sub_folder)

    def validate_and_export_manifest(
        self,
        push_to_git: bool = False,
        commit_msg: Optional[str] = None,
    ) -> bool:
        """Validate the current manifest against a schema and export it (s3 and Git).

        This function will always upload the generated manifest to S3, using a path
        constructed based on `self.output_bucket_name` and the DataStage.

        If `push_to_git` is True, by default the commit message used will be
        "Add generated manifest file {filename}." It can be overriden.

        Note:
            If a problem occurs when pushing to Git, a critical message will be logged,
            but it won't modify or alter the upload of the manifest to S3.

        Args:
            push_to_git (bool, optional): Whether to also push the generated manifest to
                GitHub (impresso/impresso-data-release). Defaults to False.
            commit_msg (Optional[str], optional): Commit message to override the
                default message. Defaults to None.

        Returns:
            bool: Whether the upload to s3 was successful.
        """
        msg = "Validating and exporting manifest to s3"
        validate_against_schema(self.manifest_data)

        if push_to_git:
            # clone the data release repository locally if not for debug - always staging branch
            out_repo = clone_git_repo(self.temp_dir, branch="staging")
            logger.info("%s and GitHub!", msg)
        else:
            out_repo = None
            logger.info("%s!", msg)

        manifest_dump = json.dumps(self.manifest_data, indent=4)

        mft_filename = self._manifest_filename

        # if out_repo is None, in debug mode
        if push_to_git:
            msg = f"Push manifest to git manually file at: \ns3://{self.output_bucket_name}"
            try:
                # write file and push to git
                local_path_in_repo = self._get_out_path_within_repo()
                pushed, out_file_path = write_and_push_to_git(
                    manifest_dump,
                    out_repo,
                    local_path_in_repo,
                    mft_filename,
                    commit_msg=commit_msg,
                )

                if not pushed:
                    new_msg = f"{msg}/{out_file_path}."
                    logger.critical(new_msg)
                    print(new_msg)
            except Exception as e:
                new_msg = f"{msg}/{out_file_path}. Exception: {e}"
                logger.error(new_msg)
                print(new_msg)
                # if there was a problem cloning the repository of pushing to git,
                # write the manifest somewhere in the fs
                out_file_path = write_dump_to_fs(manifest_dump, self.temp_dir, mft_filename)
        else:
            # for debug purposes, write in temp dir and not in git repo
            out_file_path = write_dump_to_fs(manifest_dump, self.temp_dir, mft_filename)

        if self.output_s3_partition is not None:
            # add the path within the bucket (partition) to the manifest file
            mft_filename = os.path.join(self.output_s3_partition, mft_filename)

        return upload_to_s3(out_file_path, mft_filename, self.output_bucket_name)

    def get_count_keys(self) -> list[str]:
        """Get the list of count keys for this manifest's media dict.

        Returns:
            list[str]: Count keys corresponding to this manifest's DataStage.
        """
        return MediaStatistics(self.stage, "year").count_keys

    def _log_failed_action(self, title: str, year: str, action: str) -> None:
        """Log and add to the notes that an action on the counts/statistics failed.

        Args:
            title (str): Media title on/with which this failure took place.
            year (str): Year on/with which this failure took place.
            action (str): Specific action during which failure took plave.
        """
        failed_note = f"{title}-{year}: {action} provided counts failed (invalid)."

        logger.warning(" ".join([failed_note, "Adding information to notes."]))
        self.append_to_notes(failed_note, to_start=False)

    def _init_yearly_stats(
        self,
        title: str,
        year: str,
        counts: dict[str, int],
        src_medium: str | None = None,
        provider: str | None = None,
    ) -> tuple[MediaStatistics, bool]:
        """Initialize the stats fro a given title and year given precomputed counts.

        Args:
            title (str): Media title to add the stats to.
            year (str): Year to which the stats correspond.
            counts (dict[str, int]): Precomputed counts used directly to initialize.

        Returns:
            tuple[MediaStatistics, bool]: The initiailized stats and whether this
                initialization was successful.
        """
        logger.debug("Initializing counts for %s-%s", title, year)
        elem = f"{title}-{year}"

        # if the source medium is not defined, fetch the information from utils
        if not src_medium:
            # already defining the provider prevents some overhead
            src_medium = get_src_info_for_alias(title, provider=provider)

        np_stats = MediaStatistics(self.stage, "year", elem, src_medium, counts=counts)
        success = True
        # if the created stats don't have the initialized values
        if np_stats.counts != counts:
            success = False
            self._log_failed_action(title, year, "initializing with")

        return np_stats, success

    def has_title_year_key(self, title: str, year: str) -> bool:
        """Verify whether the provided title and year have been processed.

        Args:
            title (str): Media title to check.
            year (str): Year to check.

        Returns:
            bool: True if the title-year pair has instantiated counts, false otherwise.
        """
        if title in self._processing_stats:
            return year in self._processing_stats[title]

        return False

    def _modify_processing_stats(
        self,
        title: str,
        year: str,
        counts: dict[str, int],
        adding: bool = True,
        src_medium: str | None = None,
        provider: str | None = None,
    ) -> bool:
        """Update or replace the processing stats for a given title-year pair.

        If the provided title-year key was not associated with any value in
        `processing_stats`, addition and replacement are the same: initialization.

        Args:
            title (str): Media title which should be updated with the new counts.
            year (str): Year which should be updated with the new counts.
            counts (dict[str, int]): Counts to use to add or replace current stats.
            adding (bool, optional): Whether this update should be an addition or
                replacement of any existing counts. Defaults to True.

        Returns:
            bool: True if the modification was a success, False otherwise.
        """
        # check if title/year pair is already in processing stats
        if self.has_title_year_key(title, year):
            # if title in self._processing_stats:
            #    if year in self._processing_stats[title]:
            success = self._processing_stats[title][year].add_counts(
                counts, replace=(not adding)
            )
            if not success:
                action = "adding" if adding else "replacing with"
                self._log_failed_action(title, year, action)

            # notify user of outcome
            return success

        if title not in self._processing_stats:
            logger.debug("Adding first stats for %s", title)
            self._processing_stats[title] = {}
        # initialize new statistics for this title-year pair:
        self._processing_stats[title][year], success = self._init_yearly_stats(
            title, year, counts, src_medium=src_medium, provider=provider
        )

        return success

    def add_by_ci_id(
        self,
        ci_id: str,
        counts: dict[str, int],
        src_medium: str | None = None,
        provider: str | None = None,
    ) -> bool:
        """Add new counts corresponding to a specific content-item ID.

        Args:
            ci_id (str): Content-item canonical ID to which the counts correspond.
            counts (dict[str, int]): Counts corresponding to that ID.

        Returns:
            bool: True if the processing stats' update was successful, False otherwise.
        """
        title, year = ci_id.split("-")[0:2]
        return self._modify_processing_stats(
            title, year, counts, src_medium=src_medium, provider=provider
        )

    def add_by_title_year(
        self,
        title: str,
        year: str,
        counts: dict[str, int],
        src_medium: str | None = None,
        provider: str | None = None,
    ) -> bool:
        """Add new counts corresponding to a specific media title and year.

        Args:
            title (str): Media title to which the counts correspond.
            year (str): Year to which the counts correspond.
            counts (dict[str, int]): Counts corresponding to that title and year.

        Returns:
            bool: True if the processing stats' update was successful, False otherwise.
        """
        if any(isinstance(v, str) for v in counts.values()):
            # if any of the count values are not ints of dicts, convert to int
            counts = {k: int(v) if isinstance(v, str) else v for k, v in counts.items()}
            logger.debug(
                "Some string values have been found in counts, converting to int: %s.",
                counts,
            )

        return self._modify_processing_stats(
            title, str(year), counts, src_medium=src_medium, provider=provider
        )

    def add_count_list_by_title_year(
        self,
        title: str,
        year: str,
        all_counts: list[dict[str, int]],
        src_medium: str | None = None,
        provider: str | None = None,
    ) -> bool:
        """Add a list of new counts corresponding to a specific media title and year.

        Args:
            title (str): Media title to which the counts correspond.
            year (str): Year to which the counts correspond.
            all_counts (list[dict[str, int]]): Lsit of counts for that title and year.

        Returns:
            bool: True if all the updates were successful, False otherwise.
        """
        return all(
            self._modify_processing_stats(
                title, str(year), c, src_medium=src_medium, provider=provider
            )
            for c in all_counts
        )

    def replace_by_ci_id(
        self,
        ci_id: str,
        counts: dict[str, int],
        src_medium: str | None = None,
        provider: str | None = None,
    ) -> bool:
        """Replace the current counts for a CI id's title-year pair with new ones.

        Warning:
            This operation will overwrite any current counts corresponding to the
            media title and year of the provided content-item ID. If the goal isn't
            to overwrite these counts, `add_by_ci_id` is better suited.

        Args:
            ci_id (str): Content-item canonical ID to which the counts correspond.
            counts (dict[str, int]): Counts for that ID to overwrite current counts with.

        Returns:
            bool: True if the stats' modification was successful, False otherwise.
        """
        title, year = ci_id.split("-")[0:2]
        msg = f"The counts for {title}-{year} will be replaced by {counts} (corresponding to id: {ci_id})"
        logger.warning(msg)
        return self._modify_processing_stats(
            title, year, counts, adding=False, src_medium=src_medium, provider=provider
        )

    def replace_by_title_year(
        self,
        title: str,
        year: str,
        counts: dict[str, int],
        src_medium: str | None = None,
        provider: str | None = None,
    ) -> bool:
        """Replace the current counts for a given title-year pair with new ones.

        Warning:
            This operation will overwrite any current counts corresponding to the
            media title and year of the provided content-item ID. If the goal isn't
            to overwrite these counts, `add_by_title_year` is better suited.

        Args:
            title (str): Media title to which the counts correspond.
            year (str): Year to which the counts correspond.
            counts (dict[str, int]): Counts for that ID to overwrite current counts with.

        Returns:
            bool: True if the stats' modification was successful, False otherwise.
        """
        logger.warning("The counts for %s-%s will be replaced by %s", title, year, counts)
        return self._modify_processing_stats(
            title, str(year), counts, adding=False, src_medium=src_medium, provider=provider
        )

    def append_to_notes(self, contents: str, to_start: bool = True) -> None:
        """Append a string content to the manifest notes, initialize them if needed.

        Args:
            contents (str): Text to add to the manifest notes.
            to_start (bool, optional): Whether the contents should be added to the
                start of the notes instead of the end. Defaults to True.
        """
        if self.notes is None:
            self.notes = contents
        else:
            new_notes = [contents, self.notes] if to_start else [self.notes, contents]
            print(f"Updates the notes - new_notes: {new_notes}")
            # there is no way of going to a new line, so separate with a hyphen
            self.notes = " — ".join(new_notes)

    def new_media(self, title: str, provider: str | None = None) -> dict[str, Any]:
        """Add a new media dict to the media list, given its title.

        By default, this means the update information will be the following:
            - "update_type": "addition"
            - "update_level": "title"
            - "updated_years": [] # all represented years will be new
            - "updated_fields": [] # all fields will be new

        Args:
            title (str): Media title for which to add a new media.

        Returns:
            dict[str, Any]: The new media dict to add to the media list.
        """
        # adding a new media means by default addition update type and title update level.
        logger.info("Creating new media dict for %s.", title)
        # don't fetch the provider from the title if it's already provided
        if not provider or provider not in PARTNER_TO_MEDIA:
            provider = get_provider_for_alias(title)
        media = {
            "media_title": title,
            "data_provider": provider,
            "source_type": get_src_info_for_alias(title, provider, False),
            "source_medium": get_src_info_for_alias(title, provider),
            "last_modification_date": self._generation_date,
        }
        media.update(init_media_info(fields=self.patched_fields))
        media.update(
            {
                "code_git_commit": self.commit_url,
                "media_statistics": [],
                "stats_as_dict": {},
            }
        )

        return media

    def define_update_info_for_title(
        self, processed_years: set[str], prev_version_years: set[str]
    ) -> dict[str, Union[str, list]]:
        """Define a title's update info from the previous and newly updated years.

        The update information for a given title corresponds to four keys, for which
        the values provide information about what modifications took place during the
        processing this manifest is documenting.

        They are defined based on various values:
            - `self.patched_fields`: fields updated during the processing (eg. for a patch).
            - `processed_years` and `prev_version_years`

        Four cases exist:
            - All newly processed years were in the previous version
                -> full title update, only modification.
            - Part of the previous years were updated, and no newly added years:
                -> year-specific update, where all modified years will be listed.
            - All previous years were updated, and new years were added:
                -> full title update with addition.
            - Part of the previous years were updated, and new years were added:
                -> year-specific update, with addition.

        Args:
            processed_years (set[str]): Years for which statistics were computed for
                this manifest.
            prev_version_years (set[str]): Years for which statistics has already been
                computed for the previous version of this manifest.

        Returns:
            dict[str, Union[str, list]]: New update info dict for the given title.
        """
        new_info = {"last_modification_date": self._generation_date}

        if processed_years == prev_version_years:
            # exactly all previous years were updated, none added: modification, full title
            new_info.update(init_media_info(add=False, fields=self.patched_fields))

        elif processed_years & prev_version_years == processed_years:
            # part of the previous years were updated, no new years added: modification, yearly
            new_info.update(
                init_media_info(
                    add=False,
                    full_title=False,
                    years=list(map(str, processed_years)),
                    fields=self.patched_fields,
                )
            )
        elif processed_years & prev_version_years == prev_version_years:
            # all previous years were updated, and new years added: addition, full title
            new_info.update(init_media_info(fields=self.patched_fields))
        else:
            # intersection is equal to none of the two original sets.
            # part of the previous years were updated, and new years added: addition, yearly
            new_info.update(
                init_media_info(
                    full_title=False,
                    years=list(map(str, processed_years)),
                    fields=self.patched_fields,
                )
            )
        new_info["code_git_commit"] = self.commit_url

        return new_info

    def update_media_stats(
        self, title: str, yearly_stats: dict[str, dict], old_media_list: dict[str, dict]
    ) -> Union[dict, list[str]]:
        """Update a title's media statistics given the its newly computed yearly stats.

        Note that it's actually the `old_media_list`'s contents which are updated when
        necessary.

        In addition, the value of `self.only_counting` will change the behavior:
            - When False, the computation of the manifest should follow a processing, and
              all data within the `_processing_stats` (here `yearly_stats` for 1 title) will
              be considered to have been modified (or re-generated).
            - When True, the manifest is computed to verify the contents of the data, and
              the media's information will be update only if differences in statisitics are
              found between the previous and current version.

        Args:
            title (str): Media title for which to update the media list.
            yearly_stats (dict[str, dict]): New yearly statistics for the title.
            old_media_list (dict[str, dict]): Previous version manifest' media list.

        Returns:
            Union[dict, list[str]]: Previous manifest's media list potentially updated to match
                new counts, and the list of years which have been modified
        """
        modified_years = []
        msg = f"---- INSIDE update_media_stats for {title} ----"
        logger.debug(msg)
        for year, stats in yearly_stats.items():

            # newly added title
            if year not in old_media_list[title]["stats_as_dict"]:
                logger.info("update_media_stats - Adding new key %s-%s.", year, title)
                print(f"update_media_stats - Adding new key {year}-{title}.")
                modified_years.append(year)
                logger.debug("Setting stats for %s-%s", title, year)
                old_media_list[title]["stats_as_dict"][year] = stats

            # if self.only_counting is True, only update media info if stats changed
            elif not self.only_counting or not stats.same_counts(
                old_media_list[title]["stats_as_dict"][year]
            ):
                modified_years.append(year)
                if not self.only_counting:
                    msg = f"update_media_stats - modified stats -> Setting stats for {title}-{year}"
                    logger.debug(msg)
                old_media_list[title]["stats_as_dict"][year] = stats

        msg = f"---- FINISHED update_media_stats for {title} – had modifications: {len(modified_years) != 0} ----"
        logger.info(msg)
        print(msg)

        return old_media_list, modified_years

    def generate_media_dict(self, old_media_list: dict[str, dict]) -> tuple[dict, bool]:
        """Given the previous manifest's and current statistics, generate new media dict.

        The previous version media list is updated with current processing media list:
            - Setting new modification date & git url for each modified title.
            - Compute update level & targets if not the processing is not a patch.

        From this update, also conclude on whether new data was added, informing the
        how the version should be increased: if new title-year keys exist, the "addition"
        flag will conduct to a major verison increase.

        Args:
            old_media_list (dict[str, dict]): _description_

        Returns:
            tuple[dict, bool]: _description_
        """
        addition = False
        for title, yearly_stats in self._processing_stats.items():

            provider = list(yearly_stats.values())[0].provider
            # if title not yet present in media list, initialize new media dict
            if title not in old_media_list:
                # new title added to the list: addition, full title
                old_media_list[title] = self.new_media(title, provider)
                addition = True

                # set the statistics
                old_media_list, _ = self.update_media_stats(
                    title, yearly_stats, old_media_list
                )
            else:
                # add provider, source type and medium if not already present
                old_media_list[title] = add_media_source_metadata(
                    title, old_media_list[title], provider
                )

                prev_version_years = set(old_media_list[title]["stats_as_dict"].keys())

                # update the statistics and identify if the media info needs to change
                old_media_list, modified_years = self.update_media_stats(
                    title, yearly_stats, old_media_list
                )

                if len(modified_years) != 0:
                    # if only counting, only consider the years which were actually modified/added
                    processed_years = (
                        set(modified_years) if self.only_counting else set(yearly_stats.keys())
                    )

                    media_update_info = self.define_update_info_for_title(
                        processed_years,
                        prev_version_years,
                    )
                    msg = (
                        f"define_update_info_for_title for {title}, new update info: {media_update_info}",
                    )
                    logger.debug(msg)

                    old_media_list[title].update(media_update_info)
                    print(f"Updated media information for {title}")
                    logger.info("Updated media information for %s", title)
                    # keep track that media info was updated for version increase
                    self.modified_info = True

                    # if title was already present, update the information with current processing
                    if not addition and media_update_info["update_type"] == "addition":
                        # only one addition is enough
                        addition = True

        # ensure the ordering of the elements in the media list stays constant
        sorted_media_list = sort_media_list_years_and_titles(old_media_list)

        return sorted_media_list, addition

    def aggregate_stats_for_title(
        self, title: str, media_dict: dict[str, Any]
    ) -> tuple[dict[str, Any], MediaStatistics]:
        """Aggregate all stats of given title and export them to a "pretty print" dict.

        The `DataStatistics` objects don't display in the dict format by default,
        but need to be converted to dicts to show as desired on the final manifest.

        Args:
            title (str): Media title for which to aggregate the yearly stats.
            media_dict (dict[str, Any]): Title's media dict with formatted statistics.

        Returns:
            tuple[dict[str, Any], MediaStatistics]: Updated media dict and
                corresponding title-level DataStatistics object.
        """
        logger.debug("Aggregating title-level stats for %s.", title)

        title_cumm_stats = MediaStatistics(
            self.stage, "title", title, get_src_info_for_alias(title)
        )
        pretty_counts = []

        for _, np_year_stat in media_dict["stats_as_dict"].items():
            if isinstance(np_year_stat, MediaStatistics):
                # newly added titles will be MediaStatistics objects -> needs pretty print
                title_cumm_stats.add_counts(np_year_stat.counts)
                # include the modification date at the year level
                pretty_counts.append(
                    np_year_stat.pretty_print(modif_date=self._generation_date)
                )
            else:
                # non-modified stats will be in pretty-print dict format -> can be added directly
                if "media_stats" in np_year_stat:
                    title_cumm_stats.add_counts(np_year_stat["media_stats"])
                else:
                    # TODO remove once all manifests only have "media stats"
                    title_cumm_stats.add_counts(np_year_stat["nps_stats"])
                    # replace existing "nps_stats" by "media_stats"
                    np_year_stat["media_stats"] = np_year_stat["nps_stats"]
                    del np_year_stat["nps_stats"]
                pretty_counts.append(np_year_stat)

        # insert the title-level statistics at the "top" of the statistics
        pretty_counts.insert(0, title_cumm_stats.pretty_print())
        media_dict["media_statistics"] = pretty_counts

        return media_dict, title_cumm_stats

    def title_level_stats(
        self, media_list: dict[str, dict]
    ) -> tuple[list[MediaStatistics], dict[str, dict]]:
        """Compute the title-level statistics from the new media list.

        Also removes the `stats_as_dict` field from the media list, and returns
        the media list with each MediaStatistics object "pretty printed".

        Args:
            media_list (dict[str, dict]): Updated media list for this manifest.

        Returns:
            tuple[list[MediaStatistics], dict[str, dict]]: New title-level stats and
                media list.
        """
        full_title_stats = []
        for title, media_as_dict in media_list.items():
            # update the canonical_media_list with the new media_dict
            media_as_dict, title_cumm_stats = self.aggregate_stats_for_title(
                title, media_as_dict
            )
            # remove the stats in dict format
            del media_as_dict["stats_as_dict"]
            # save the title level statistics for the overall statistics
            full_title_stats.append(title_cumm_stats)

        return full_title_stats, media_list

    def overall_stats(self, title_stats: list[MediaStatistics]) -> list[dict]:
        """Generate the overall stats and append the ones from the input manifest.

        Args:
            title_stats (list[MediaStatistics]): List of all title-level statistics
                used to compute the overall stats.

        Returns:
            list[dict]: This manifest's overall stats with the ones of previous stages.
        """
        corpus_stats = MediaStatistics(self.stage, "corpus", "")
        for np_stats in title_stats:
            corpus_stats.add_counts(np_stats.counts)
        # add the number of titles present in corpus
        corpus_stats.add_counts({"titles": len(title_stats)})

        # add these overall counts to the ones of previous stages
        overall_stats = self._get_input_data_overall_stats()
        overall_stats.append(corpus_stats.pretty_print())

        return overall_stats

    def compute(
        self, export_to_git_and_s3: bool = True, commit_msg: Optional[str] = None
    ) -> None:
        """Perform all necessary logic to compute and construct the resulting manifest.

        This lazy behavior ensures all necessary information is ready and accessible
        when generating the manifest (in particular the `_processing_stats`).

        The steps of this computation are the following:
            - Ensure `_processing_stats` is not empty so the manifest can be computed and
              crystallize the time this function is called as the `_generation_date`.
            - Fetch the previous version of this manifest from S3, extract its media list.
            - Generate the new media list given the previous one and `_processing_stats`.
            - Compute the new title and corpus level statistics using the new media list.
            - Compute the new version based on the performed updates.
            - Define the `manifest_data` attribute corresponding to the final manifest.
            - Optionally, dump it to JSON, export it to S3 and Git.

        Args:
            export_to_git_and_s3 (bool, optional): Whether to export the final
                `manifest_data` as JSON to S3 and GitHub. Defaults to True. If False,
                `validate_and_export_manifest` can be called separately to do it.
            commit_msg (Optional[str], optional): Commit message to use instead of
                the default from `validate_and_export_manifest`. Defaults to None.
        """
        if not self._processing_stats:
            # `self._processing_stats` is empty the manifest can't be computed, directly stop.
            msg = "The manifest can't be computed without having provided statistics!"
            logger.warning(msg)
        else:
            logger.info("Starting to compute the manifest...")

            self._generation_date = timestamp()

            #### IMPLEMENT LOGIC AND FILL MANIFEST DATA

            logger.info("Loading the previous version of this manifest if it exists.")
            # load previous version of this manifest
            prev_version_mft = self._get_prev_version_manifest()

            if prev_version_mft is not None:
                logger.info("Found previous version manifest, loading its contents.")
                # ensure a non-modified version remains
                old_mft = copy.deepcopy(prev_version_mft)
                old_media_list = media_list_from_mft_json(old_mft)

            else:
                logger.info("No previous version found, reinitializaing the media list.")
                # if no previous version media list, generate media list from scratch
                old_media_list = {}

                if self.only_counting:
                    logger.info(
                        "When no previous version exists, the option to only "
                        "count (only_counting=True) is not available."
                    )
                    self.only_counting = False

            logger.info("Updating the media statistics with the new information...")
            # compare current stats to previous version stats
            updated_media, addition = self.generate_media_dict(old_media_list)

            logger.info("Computing the title-level statistics...")
            full_title_stats, updated_media = self.title_level_stats(updated_media)

            logger.info("Computing the overall statistics...")
            overall_stats = self.overall_stats(full_title_stats)

            self.version = self._get_current_version(addition)

            # the canonical has no input stage
            if self.stage != DataStage.CANONICAL and self.input_manifest_s3_path is not None:
                input_mft_git_path = os.path.join(
                    self._get_out_path_within_repo(stage=self._input_stage),
                    self.input_manifest_s3_path.split("/")[-1],
                )
            else:
                input_mft_git_path = None

            if self.notes is None:
                self.notes = ""

            # populate the dict with all gathered information
            self.manifest_data = {
                "mft_version": self.version,
                "mft_generation_date": self._generation_date,
                "mft_s3_path": self.output_mft_s3_path,
                "input_mft_s3_path": self.input_manifest_s3_path,
                "input_mft_git_path": input_mft_git_path,
                "previous_mft_s3_path": self._prev_mft_s3_path,
                "code_git_commit": self.commit_url,
                "model_id": self.model_id,
                "run_id": self.run_id,
                "media_list": list(updated_media.values()),
                "overall_statistics": overall_stats,
                "notes": self.notes,
            }

            msg = f"{'-' * 15} Manifest successfully generated! {'-' * 15}"
            logger.info(msg)
            print(msg)
            if export_to_git_and_s3:

                # if push_to_git is not defined and exporting directly,
                # will both upload to s3 and push to git.
                push = self.push_to_git if self.push_to_git is not None else True
                if not push:
                    msg = (
                        "Argument export_to_git_and_s3 was set to True but push_to_git"
                        " was set to False. Exporting to S3 but not pushing to git."
                    )
                    logger.info(msg)
                    print(msg)
                success = self.validate_and_export_manifest(push, commit_msg)

                if success:
                    msg = f"{'-' * 15} Manifest successfully uploaded to S3 and GitHub! {'-' * 15}"
                    logger.info(msg)
                    print(msg)
