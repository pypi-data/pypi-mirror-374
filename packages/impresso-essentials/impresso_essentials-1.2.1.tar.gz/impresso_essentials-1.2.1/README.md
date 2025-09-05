# impresso-essentials
[![Documentation Status](https://readthedocs.org/projects/impresso-essentials/badge/?version=latest)](https://impresso-essentials.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/impresso-essentials.svg)](https://badge.fury.io/py/impresso-essentials)
![PyPI - License](https://img.shields.io/pypi/l/impresso-essentials)

Python module with bits of code (objects, functions) highly-reusable within the [impresso project](https://impresso-project.ch/).

Please refer to the [documentation](https://impresso-essentials.readthedocs.io/) for further information on this library.

The library supports configuration of s3 credentials via project-specific local .env files.

## Installation

With `pip`:

```bash
pip install impresso-essentials
```

or

```bash
pip install --upgrade impresso-essentials
```

### To Clone the repository:

The `--recursive` option needs to be used when cloning the repository so that the [impresso-schemas](https://github.com/impresso/impresso-schemas) submodule is also cloned at the same time.
```bash
# with SSH
git clone --recursive git@github.com:impresso/impresso-essentials.git 
```

## Data Versioning

### Motivation

The `versioning` package of `impresso-essentials` contains several modules and scripts that allow to version Impresso's data at various stages of the processing pipeline.
The main goal of this approach is to version the data and track information at every stage to:

1. **Ensure data consisteny and ease of debugging:** Data elements should be consistent across stages, and inconsistencies/differences should be justifiable through the identification of data leakage points.
2. **Allow partial updates:** It should be possible to (re)run all or part of the processes on subsets of the data, knowing which version of the data was used at each step. This can be necessary when new media collections arrive, or when an existing collection has been patched.
3. **Ensure transparency:** Citation of the various data stages and datasets should be straightforward; users should know when using the interface exactly what versions they are using, and should be able to consult the precise statistics related to them.

### Data Stages

Impresso's data processing pipeline is organised in three main data "meta-stages", mirroring the main processing steps. During each of those meta-stages, different formats of data are created as output of processes and in turn used as inputs to other downstream tasks.

1. **[Data Preparation]**: Conversion of the original media collections to unified base formats which will serve as input to the various data enrichment tasks and processes. Produces **prepared data**.
    - Includes the data stages: _canonical_, _rebuilt_, _evenized-rebuilt_ and _passim_ (rebuilt format adapted to the passim algorithm).
2. **[Data Enrichment]**: All processes and tasks performing **text and media mining** on the prepared data, through which media collections are enriched with various annotations at different levels, and turned into vector representations.
    - Includes the data stages: _entities_, _langident_, _text-reuse_, _topics_, _ocrqa_, _embeddings_, (and _lingproc_).
3. **[Data Indexation]**: All processes of **data ingestion** of the prepared and enriched data into the backend servers: Solr and MySQL.
    - Includes the data stages: _solr-ingestion-text_, _solr-ingestion-entities_, _solr-ingestion-emb_, _mysql-ingestion_.
4. **[Data Releases]**: Packages of **Impresso released data**, composed of the datasets of all previously mentioned data stages, along with their corresponding versioned manifests, to be cited on the interface.
    - They will be accessible on the [impresso-data-release](https://github.com/impresso/impresso-data-release) GitHub repository.

**TODO**: Update/finalize the exact list of stages once every stage has been included.

### Data Manifests

The versioning aiming to document the data at each step through versions and statistics is implemented through **manifest files**, in JSON format which follow a specific [schema](https://github.com/impresso/impresso-schemas/blob/master/json/versioning/manifest.schema.json). (TODO update JSON schema with yearly modif date.)

After each processing step, a manifest should be created documenting the changes made to the data resulting from that processing. It can also be created on the fly during a processing, and in-between processings to count and sanity-check the contents of a given S3 bucket.
Once created, the manifest file will automatically be uploaded to the S3 bucket corresponding to the data it was computed on, and optionally pushed to the [impresso-data-release](https://github.com/impresso/impresso-data-release) repository to keep track of all changes made throughout the versions.

There are multiple ways in which the manifest can be created/computed.

#### Computing a manifest automatically based on the S3 data - `compute_manifest.py` script

The script `impresso_essentials/versioning/compute_manifest.py`, allows one to compute a manifest on the data present within a specific S3 bucket.
This approach is meant to compute the manifest **after** the processing is over, and will automatically fetch the data (according to the configuration), and compute the needed statistics on it.
It can be used or run in three ways: the CLI from the cloned `impresso_essentials` repository, running the script as a module, or calling the function performing the main logic within one's code.

The **CLI** for this script is the following:

```bash
# when the working directory is impresso_essentials/versioning
python compute_manifest.py --config-file=<cf> --log-file=<lf> [--scheduler=<sch> --nworkers=<nw> --verbose]
```

Where the `config_file` should be a simple json file, with specific arguments, all described [here](https://github.com/impresso/impresso-essentials/blob/main/impresso_essentials/config/manifest.config.example.md).

- The script uses [dask](https://www.dask.org/) to parallelize its task. By default, it will start a local cluster, with 8 as the default number of workers (the parameter `nworkers` can be used to specify any desired value).
- Optinally, a [dask scheduler and workers](https://docs.dask.org/en/stable/deploying-cli.html) can be started in separate terminal windows, and their IP provided to the script via the `scheduler` parameter.

It can also be **run as a module** with the CLI, but from any other project or directory, as long as `impresso_essentials` is installed in the user's environment. The same arguments apply:

```bash
# the env where impresso_essentials is installed should be active
python -m impresso_essentials.versioning.compute_manifest --config-file=<cf> --log-file=<lf> [--scheduler=<sch> --nworkers=<nw> --verbose]
```

Finally, one can prefer to **directly incorporate this computation within their code**. That can be done by calling the `create_manifest` function, performing the main logic in the following way:
```python
from impresso_essentials.versioning.compute_manifest import create_manifest

# optionally, or config_dict can be directly defined
with open(config_file_path, "r", encoding="utf-8") as f_in:
    config_dict = json.load(f_in)

# also optional, can be None
dask_client = Client(n_workers=nworkers, threads_per_worker=1)

create_manifest(config_dict, dask_client)
```
- The `config_dict` is a dict with the same contents as the `config_file`, described [here](https://github.com/impresso/impresso-essentials/blob/main/impresso_essentials/config/manifest.config.example.md).
- Providing `dask_client` is optional, and the user can choose whether to include it or not.
- However, when generating the manifest in this way, the user should add `if __name__ == "__main__":` in the script calling `create_manifest`.

#### Computing a manifest on the fly during a process

It's also possible to compute a manfest on the fly during a process. In particular when the output from the process is not stored on S3, this method is more adapted; eg. for data indexation.
To do so, some simple modifications should be made to the process' code:

1. **Instantiation of a DataManifest object:** The `DataManifest` class holds all methods and attributes necessary to generate a manifest. It counts a relatively large number of input arguments (most of which are optional) which allow a precise specification and configuration, and ease all other interactions with the instantiated manifest object. All of them are also described in the [manifest configuration](https://github.com/impresso/impresso-essentials/blob/main/impresso_essentials/config/manifest.config.example.md):
    - Example instantiation:

    ```python
    from impresso_essentials.versioning.data_manifest import DataManifest
    
    manifest = DataManifest(
        data_stage="passim", # DataStage.PASSIM also accepted
        s3_output_bucket="32-passim-rebuilt-final/passim", # includes partition within bucket
        s3_input_bucket="22-rebuilt-final", # includes partition within bucket
        git_repo="/local/path/to/impresso-essentials",
        temp_dir="/local/path/to/git_temp_folder",
        is_patch=True,
        patched_fields=["series", "id"], # example of modified fields in the passim-rebuilt schema
        previous_mft_path=None, # a manifest already exists on S3 inside "32-passim-rebuilt-final/passim"
        only_counting=False,
        notes="Patching some information in the passim-rebuilt",
        push_to_git=True,
        relative_git_path="relative/path/to/use/in/git/repo", # if None will be set to the s3 partition by default (here "/passim")
        model_id = "model_id_vx.x.x", # according to Impresso naming conventions, if relevant
        run_id = "run_id_vx-x-x", # according to Impresso naming conventions
    )
    ```

    Note however that as opposed to the previous approach, simply instantiating the manifest **will not do anything**, as it is not filled in with S3 data automatically. Instead, the user should provide it with statistics that they computed on their data and wish to track, as it is described in the next steps.

2. **Addition of data and counts:** Once the manifest is instantiated the main interaction with the instantiated manifest object will be through the `add_by_title_year` or `add_by_ci_id` methods (two other with "replace" instead also exist, as well as `add_count_list_by_title_year`, all described in the [documentation](https://impresso-essentials.readthedocs.io/)), which take as input:
    - The _media title_ and _year_  to which the provided counts correspond
    - The _counts_ dict which maps string keys to integer values. Each data stage has its own set of keys to instantiate, which can be obtained through the `get_count_keys` method or the [NewspaperStatistics](https://github.com/impresso/impresso-essentials/blob/main/impresso_essentials/versioning/data_statistics.py#L176) class. The values corresponding to each key can be computed by the user "by hand" or by using/adapting functions like `counts_for_canonical_issue` (or `counts_for_rebuilt`) to the given situation. All such functions can be found in the helper submodule [aggregators.py](https://github.com/impresso/impresso-essentials/blob/main/impresso_essentials/versioning/aggregators.py).
        - Note that the count keys will always include at least `"content_items_out"` and `"issues"`.
    - Example:

    ```python
    # for all title-years pairs or content-items processed within the task

    counts = ... # compute counts for a given title and year of data or content-item 
    # eg. rebuilt counts could be: {"issues": 45, "content_items_out": 9110, "ft_tokens": 1545906} 

    # add the counts to the manifest
    manifest.add_by_title_year("title_x", "year_y", counts)
    # OR
    manifest.add_by_ci_id("content-item-id_z", counts)
    ```

    - Note that it can be useful to only add counts for items or title-year pairs for which it's certain that the processing was successful. For instance, if the resulting output is written in files and uplodaded to S3, it would be preferable to add the counts corresponding to each file only once the upload is over without any exceptions or issues. This ensures the manifest's counts actually reflect the result of the processing.

3. **Computation, validation and export of the manifest:** Finally, after all counts have been added to the manifest, its lazy computation can be triggered. This corresponds to a series of processing steps that:
    - compare the provided counts to the ones of previous versions,
    - compute title and corpus-level statistics,
    - serialize the generated manifest to JSON and
    - upload it to S3 (optionally Git if it's a final version).
    - This computation is triggered as follows:

    ```python
    [...] # instantiate the manifest, and add all counts for processed objects
    
    # To compute the manifest, upload to S3 AND push to GitHub
    manifest.compute(export_to_git_and_s3=True) 

    # OR

    # To compute the manifest, without exporting it directly
    manifest.compute(export_to_git_and_s3=False)
    # Then one can explore/verify the generated manifest with
    print(manifest.manifest_data)
    # To export it to S3, and optionally push it to Git if it's ALREADY BEEN GENERATED
    manifest.validate_and_export_manifest(push_to_git=[True or False])
    ```

#### Versions and version increments

The manifests use **semantic versioning**, where increments are automatically deduced based on the changes made to the data during a given processing or since the last manifest computation on a bucket.
There are two main "modes" in which the manifest computation can be configured:

- **Documenting an update (`only_counting=False`):**
  - By default, any data "shown"/added to the manifest (so to be taken into account in the statistics) is _considered to have been "modified"_ or re-generated.
  - If one desires to generate a manifest after a _partial update_ of the data of a given stage, without taking the whole corpus into consideration, the best approach is to _provide the exact list of media titles_ to include in the versioning.
- **Documenting the contents of a bucket independently of a processing (`only_counting=True`):**
  - However, the option has also been added to compute a manifest on a given bucket to _simply count and document its contents_ (after data was copied from one bucket ot he next for instance).
  - In such cases, _only modifications in the statistics_ for a given title-year pair will result in updates/modifications in the final manifest generated (in particular, the `"last_modification_date"` field of the manifest, associated to statistics would stay the same for any title for which no changes were identified).

When the computing of a manifest is launched, the following will take place to determine the version to give to the resulting manifest:

- _If a an existing version of the manifest for a given data stage exists in the `output_bucket` provided_, this manifest will be read and updated. Its version will be the basis to identify what the version increment should be based on the type of modifications.
- _If no such manifest exists and no manifest can be found in the `output_bucket` provided_, the there are two possibilities:
  - The argument `previous_mft_s3_path` is provided, with the path to a previously computed manifest which is present in _another_ bucket. This manifest is used as the previous one like described above to update the data and compute the next verison.
  - The argument `previous_mft_s3_path` is not provided, then this is the original manifest for a given data stage, and the version in this case is 0.0.1. This is the case for your first manifest.

Based on the information that was updated, the version increment varies:

- **Major** version increment if _new title-year pairs_ have been added that were not present in the previous manifest.
- **Minor** version increment if:
  - _No new title-year pairs_ have been provided as part of the new manifest's data, and the processing was _not a patch_.
  - This is in particular the version increment if we re-ingest or re-generate a portion of the corpus, where the underlying stats do not change. If a part of the corpus only was modified/reingested, the specific newspaper titles should be provided within the `newspapers` parameter to indicate which data (within the `media_list`) to consider and update.
- **Patch** version increment if:
  - The _`is_patch` or `patched_fields` parameters are set to True_. The processing or ingestion versioned in this case is a patch, and the patched_fields will be updated according to the values provided as parameters.
  - The _`only_counting` parameter is set to True_.
    - This parameter is exactly made for the case scenarios where one wants to recompute the manifest on an _entire bucket of existing data_ which has not necessarily been recomputed or changed (for instance if data was copied, or simply to recount etc).
    - The computation of the manifest in this context is meant more as a sanity-check of the bucket's contents.
    - The counts and statistics will be computed like in other cases, but the update information (modification date, updated years, git commit url etc) will not be updated unless a change in the statstics is identified (in which case the resulting manifest version is incremented accordingly).

---
---
## BBOX visualizer JSON extractor
### Motivation 
The impresso corpus is very large, and aggregates data from a wide variety of data providers, each in their own unique format, with varying quality.

This data is first converted to a unified data format - specific to impresso - the canonical format.
When converting the original OCR (sometimes including OLR) data into this canonical format, many errors and mistakes can arise, due to the low quality of the OCR/OLR, complexity of the logical structure or code bugs. 

It is not straightfoward to visualize the extracted structure of content-items and issues (and their bounding boxes) before the very end of the data processing pipeline, when it’s ingested into the interface.
As a result, many issues (like misplaced coordinates, faulty content-items or else) are only uncovered at the very end of the process, once the data is already public. 

The motivation for this tool is thus to:
  - visualize better the canonical and rebuilt data when it’s generated and at various steps of the pipeline
  - enable easier debugging, and identification/correction of potential issues and bugs in the code.
  - allow for quick checks of content-items against the facsimile at later stages of the pipeline, helping in all development phases.
---
### Usage
The functions built are found in `impresso_essentials/bbox_visualizer/`. We focus on extracting from element (issue, page, content item) id, the corresponding JSON formatted to be seen by a JSON visualizer. The schema for the format outputed can found in `impresso-schema/json/visualizer/bbox_visualizer_schema.json`.
You can either call `build_bbox_json()` in a notebook by importing it with
```python
from impresso_essentials.bbox_visualizer.json_builder import build_bbox_json
```
or call it as a **CLI** with 
```bash
python json_builder.py <element_ID> --level <level of bboxes> --output <output_path.json> --verbose --log-file <path/to/log_file>
```
#### Arguments
  - `element_id` **(positional)** : ID of the element you want to extract the JSON from
  - `level` : level of the bounding boxes you want to visualize, it can be from `{regions,paragraphs,lines,tokens}`
  - `output` : path where the correspondin JSON with the bounding boxes will be outputed. 
---
### Testing
You can make some tests in `notebooks/json_bbox_extractor.ipynb`.

### Visualizing BBoxes

Once you have extracted your JSON, you can visualize the bounding boxes from the given element by installing the [impresso/bbox-viewer](https://github.com/impresso/bbox-viewer) repository.

Once you have launched the web app, you can copy-paste your JSON file in the left text box and visualize on the right your elements with bounding boxes overlayed.
![](impresso_essentials/bbox_visualizer/images/viewer.png)
## About Impresso

### Impresso project

[Impresso - Media Monitoring of the Past](https://impresso-project.ch) is an interdisciplinary research project that aims to develop and consolidate tools for processing and exploring large collections of media archives across modalities, time, languages and national borders. The first project (2017-2021) was funded by the Swiss National Science Foundation under grant No. [CRSII5_173719](http://p3.snf.ch/project-173719) and the second project (2023-2027) by the SNSF under grant No. [CRSII5_213585](https://data.snf.ch/grants/grant/213585) and the Luxembourg National Research Fund under grant No. 17498891.

### Copyright

Copyright (C) 2024 The Impresso team.

### License

This program is provided as open source under the [GNU Affero General Public License](https://github.com/impresso/impresso-pyindexation/blob/master/LICENSE) v3 or later.

---

<p align="center">
  <img src="https://github.com/impresso/impresso.github.io/blob/master/assets/images/3x1--Yellow-Impresso-Black-on-White--transparent.png?raw=true" width="350" alt="Impresso Project Logo"/>
</p>
