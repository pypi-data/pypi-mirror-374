#
# # Copyright © 2025 Peak AI Limited. or its affiliates. All Rights Reserved.
# #
# # Licensed under the Apache License, Version 2.0 (the "License"). You
# # may not use this file except in compliance with the License. A copy of
# # the License is located at:
# #
# # https://github.com/PeakBI/peak-sdk/blob/main/LICENSE
# #
# # or in the "license" file accompanying this file. This file is
# # distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# # ANY KIND, either express or implied. See the License for the specific
# # language governing permissions and limitations under the License.
# #
# # This file is part of the peak-sdk.
# # see (https://github.com/PeakBI/peak-sdk)
# #
# # You should have received a copy of the APACHE LICENSE, VERSION 2.0
# # along with this program. If not, see <https://apache.org/licenses/LICENSE-2.0>
#
"""Peak blocks deployments commands."""

from __future__ import annotations

from typing import Dict, List, Optional

import typer
from peak.cli import args, helpers
from peak.cli.args import DRY_RUN, GENERATE_YAML, OUTPUT_TYPES, PAGING
from peak.constants import OutputTypes, OutputTypesNoTable
from peak.output import Writer
from peak.press.blocks import Block

app = typer.Typer()

_DEPLOYMENT_ID = typer.Argument(..., help="ID of the Block deployment to be used in this operation")

_DEPLOYMENT_ID_OPTION = typer.Option(None, help="ID of the Block deployment to be used in this operation")
_FALLBACK_PARAMS_FILE = typer.Option(
    None,
    help="File containing parameters to be used when deployment id is not present",
)
_FALLBACK_DETAILS_FILE = typer.Option(
    None,
    help="File containing details to be used when deployment id is not present",
)


@app.command(short_help="Create a Block deployment.")
def create(
    ctx: typer.Context,
    file: str = args.TEMPLATE_PATH,
    description_file: Optional[str] = args.TEMPLATE_DESCRIPTION_FILE,
    revision_notes_file: Optional[str] = args.REVISION_NOTES_FILE,
    params_file: Optional[str] = args.TEMPLATE_PARAMS_FILE,
    params: Optional[List[str]] = args.TEMPLATE_PARAMS,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Create*** a Block deployment This creates the resource described in the Block Spec.

    \b
    🧩 ***Input file schema (yaml):***<br/>
    ```yaml
      body (map):
        metadata (map):
            name (string | required: false): Name of the deployment. Must be unique within the tenant.
            title (string | required: false): Title of the deployment.
            summary (string | required: false): Summary of the deployment.
            description (string | required: false): Description of the deployment.
            descriptionContentType (string | required: false): Content type of the description. Should be one of "text/plain" or "text/markdown".
            imageUrl (string | required: false): URL of the image to be associated with the block deployment.
            tags (list(map) | required: false):
                - name (string): Name of the tag.
        parameters (map | required: false):
            build (map | required: false): Dictionary of parameters specific to the 'build' phase. Keys are parameter names, and values are the parameter values, which can be of type string, boolean, number, dictionary or list (string, number, dictionary).
            run (map | required: false): Dictionary of parameters specific to the 'run' phase. Keys are parameter names, and values are the parameter values, which can be of type string, boolean, number, dictionary or list (string, number, dictionary).
        revision (map | required: false):
            notes (string | required: false): Notes for the deployment revision.
        spec (map):
            id (string): ID of the block spec to be deployed.
            release (map | required: false):
                version (string): A valid semantic release version of the block spec.
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak blocks deployments create /path/to/body.yaml -v /path/to/params.yaml
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "id": "632a4e7c-ab86-4ecb-8f34-99b5da531ceb"
    }
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Block%20Deployments/post_v1_blocks_deployments)
    """
    blocks_client: Block = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    markdown_files = {}
    if description_file:
        markdown_files["body:metadata:description"] = description_file
    if revision_notes_file:
        markdown_files["body:revision:notes"] = revision_notes_file

    body = helpers.template_handler(file, params_file, params, markdown_files)
    body = helpers.remove_unknown_args(body, blocks_client.create_deployment)

    with writer.pager():
        response: Dict[str, str] = blocks_client.create_deployment(**body)
        writer.write(response)


@app.command("list", short_help="List Block deployments.")
def list_block_deployments(
    ctx: typer.Context,
    page_size: Optional[int] = args.PAGE_SIZE,
    page_number: Optional[int] = args.PAGE_NUMBER,
    status: Optional[List[str]] = args.STATUS_FILTER_DEPLOYMENTS,
    name: Optional[str] = args.NAME_FILTER,
    title: Optional[str] = args.TITLE_FILTER,
    sort: Optional[List[str]] = args.SORT_KEYS,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypes] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***List*** Block deployments that have been created for the given tenant.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak blocks deployments list --status=deployed,failed --page-size 10 --page-number 1
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "deploymentsCount": 1,
        "deployments": [...],
        "pageCount": 1,
        "pageNumber": 1,
        "pageSize": 25
    }
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Block%20Deployments/get_v1_blocks_deployments)
    """
    blocks_client: Block = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = blocks_client.list_deployments(
            status=status,
            name=name,
            sort=sort,
            title=title,
            page_size=page_size,
            page_number=page_number,
            return_iterator=False,
        )
        writer.write(response)


@app.command(short_help="Describe the Block deployment.")
def describe(
    ctx: typer.Context,
    deployment_id: str = _DEPLOYMENT_ID,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Describe*** the Block deployment with details of its latest revision.

    \b
    ***Note***: Parameters listed in the response are masked if "hideValue" was set to true
        when creating the block spec.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak blocks deployments describe <deployment_id>
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "id": "632a4e7c-ab86-4ecb-8f34-99b5da531ceb",
        "kind": "app",
        "latestRevision": {...},
        "metadata": {...},
        "spec": {...}
        "parameters": {...}
    }
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Block%20Deployments/get_v1_blocks_deployments__deploymentId_)
    """
    blocks_client: Block = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = blocks_client.describe_deployment(deployment_id)
        writer.write(response)


@app.command(short_help="Update the Block deployment metadata.")
def update_metadata(
    ctx: typer.Context,
    deployment_id: str = _DEPLOYMENT_ID,
    file: str = args.TEMPLATE_PATH,
    description_file: Optional[str] = args.TEMPLATE_DESCRIPTION_FILE,
    params_file: Optional[str] = args.TEMPLATE_PARAMS_FILE,
    params: Optional[List[str]] = args.TEMPLATE_PARAMS,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Update*** the Block deployment metadata.

    \b
    🧩 ***Input file schema (yaml):***<br/>
    ```yaml
      body (map):
        name (string | required: false): Name of the deployment. Must be unique within the tenant.
        title (string | required: false): Title of the deployment.
        summary (string | required: false): Summary of the deployment.
        description (string | required: false): Description of the deployment.
        descriptionContentType (string | required: false): Content type of the description. Should be one of "text/plain" or "text/markdown".
        imageUrl (string | required: false): URL of the image to be associated with the block deployment.
        tags (list(map) | required: false):
            - name (string): Name of the tag.
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak blocks deployments update-metadata <deployment_id> /path/to/body.yaml -v /path/to/params.yaml
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "id": "632a4e7c-ab86-4ecb-8f34-99b5da531ceb"
        "kind": "workflow",
        "latestRevision": {...},
        "metadata": {...},
        "spec": {...}
    }
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Block%20Deployments/patch_v1_blocks_deployments__deploymentId_)
    """
    blocks_client: Block = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    markdown_files = {}
    if description_file:
        markdown_files["body:description"] = description_file

    body = helpers.template_handler(file, params_file, params, markdown_files)
    body = helpers.remove_unknown_args(body, blocks_client.update_deployment_metadata)

    with writer.pager():
        response = blocks_client.update_deployment_metadata(deployment_id, **body)
        writer.write(response)


@app.command(short_help="Redeploy a Block deployment.")
def redeploy(
    ctx: typer.Context,
    deployment_id: str = _DEPLOYMENT_ID,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Redeploy*** latest revision of a Block deployment. This allows you to redeploy a Block deployment that is in `failed` or `warning` state.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak blocks deployments redeploy <deployment_id>
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "deploymentId": "632a4e7c-ab86-4ecb-8f34-99b5da531ceb",
        "revision": 2
        "revisionId": "7092bd84-c35d-43c1-90ca-7510a1204dcc"
    }
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Block%20Deployments/redeploy_v1_blocks_deployments__deploymentId_)
    """
    blocks_client: Block = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = blocks_client.redeploy(deployment_id)
        writer.write(response)


@app.command(short_help="Delete a Block deployment.")
def delete(
    ctx: typer.Context,
    deployment_id: str = _DEPLOYMENT_ID,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Delete*** a Block deployment. This will delete the resource that was created as part of the deployment.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak blocks deployments delete <deployment_id>
    ```

    \b
    🆗 ***Response:***
    ```json
    {}
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Block%20Deployments/delete_v1_blocks_deployments__deploymentId_)
    """
    blocks_client: Block = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = blocks_client.delete_deployment(deployment_id)
        writer.write(response)


@app.command(short_help="Create a Block deployment revision.")
def create_revision(
    ctx: typer.Context,
    deployment_id: str = _DEPLOYMENT_ID,
    file: str = args.TEMPLATE_PATH,
    revision_notes_file: Optional[str] = args.REVISION_NOTES_FILE,
    params_file: Optional[str] = args.TEMPLATE_PARAMS_FILE,
    params: Optional[List[str]] = args.TEMPLATE_PARAMS,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Create*** a Block deployment revision. This updates the deployment with the specified spec release.

    \b
    🧩 ***Input file schema (yaml):***<br/>
    ```yaml
      body (map):
        parameters (map | required: false):
            build (map | required: false): Dictionary of parameters specific to the 'build' phase. Keys are parameter names, and values are the parameter values, which can be of type string, boolean, number, dictionary or list (string, number, dictionary).
            run (map | required: false): Dictionary of parameters specific to the 'run' phase. Keys are parameter names, and values are the parameter values, which can be of type string, boolean, number, dictionary or list (string, number, dictionary).
        release (map):
            version (string): A valid semantic release version of the block spec.
        revision (map | required: false):
            notes (string | required: false): Notes for the deployment revision.

    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak blocks deployments create-revision /path/to/body.yaml -v /path/to/params.yaml
    ```

    \b
    🆗 ***Response:***
    ```json
    {
        "id": "632a4e7c-ab86-4ecb-8f34-99b5da531ceb",
        "revision": 2
    }
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Block%20Deployments/post_v1_blocks_deployments__deploymentId__revisions)
    """
    blocks_client: Block = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    markdown_files = {}
    if revision_notes_file:
        markdown_files["body:revision:notes"] = revision_notes_file

    body = helpers.template_handler(file, params_file, params, markdown_files)
    body = helpers.remove_unknown_args(body, blocks_client.create_deployment_revision)

    with writer.pager():
        response: Dict[str, str] = blocks_client.create_deployment_revision(deployment_id, **body)
        writer.write(response)


@app.command(short_help="Describe a Block deployment revision.")
def describe_revision(
    ctx: typer.Context,
    deployment_id: str = args.DEPLOYMENT_ID,
    revision: str = args.REVISION,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Describe*** a Block deployment revision.

    \b
    ***Note***: Parameters listed in the response are masked if "hideValue" was set to true
        when creating the block spec release.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak blocks deployments describe-revision --deployment-id <deployment_id> --revision 2
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "createdAt": "2020-01-01T18:00:00.000Z",
        "createdBy": "jane.smith@peak.ai",
        "id": "7092bd84-c35d-43c1-90ca-7510a1204dcc",
        "latestRevision": {...},
        "notes": "This is a new revision"
        "resources": [...],
        "revision": 2,
        "status": "deploying",
        "spec": {...}
        "parameters": {...}
    }
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Block%20Deployments/get_v1_blocks_deployments__deploymentId__revisions__revision_)
    """
    blocks_client: Block = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = blocks_client.describe_deployment_revision(deployment_id, revision)
        writer.write(response)


@app.command(short_help="List revisions of a Block deployment.")
def list_revisions(
    ctx: typer.Context,
    deployment_id: str = _DEPLOYMENT_ID,
    sort: Optional[List[str]] = args.SORT_KEYS,
    status: Optional[List[str]] = args.STATUS_FILTER_DEPLOYMENT_REVISIONS,
    page_size: Optional[int] = args.PAGE_SIZE,
    page_number: Optional[int] = args.PAGE_NUMBER,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypes] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***List*** all revisions for a given Block deployment.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak blocks deployments list-revisions "632a4e7c-ab86-4ecb-8f34-99b5da531ceb" --sort createdBy:asc,createdAt --status deployed,deploying --page-size 10 --page-number 1
    ```

    \b
    🆗 ***Response:***
    ```
    {
        "pageCount": 1,
        "pageNumber": 1,
        "pageSize": 10,
        "revisionCount": 1,
        "revisions": [...]
    }
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Block%20Deployments/get_v1_blocks_deployments__deploymentId__revisions)
    """
    block_client: Block = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = block_client.list_deployment_revisions(
            deployment_id,
            sort=sort,
            status=status,
            page_size=page_size,
            page_number=page_number,
            return_iterator=False,
        )
        writer.write(response)


@app.command(short_help="Get the parameters for a deployment at run time.")
def get_parameters(
    ctx: typer.Context,
    deployment_id: Optional[str] = _DEPLOYMENT_ID_OPTION,
    fallback_params_file: Optional[str] = _FALLBACK_PARAMS_FILE,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Get*** all the parameters for a deployment at run time.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak blocks deployments get-parameters --deployment-id=<deployment-id> --fallback-params-file=<path/to/fallback/params/file>
    ```

    \b
    🆗 ***Response:***
    ```
    {...}
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Deployment%20Parameters/get_v1_deployments__deploymentId__parameters_run)
    """
    blocks_client: Block = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = blocks_client.get_parameters(
            deployment_id=deployment_id,
            fallback_params_file=fallback_params_file,
        )
        writer.write(response)


@app.command(short_help="Update the parameters for a deployment at run time.")
def patch_parameters(
    ctx: typer.Context,
    deployment_id: str = _DEPLOYMENT_ID,
    file: str = args.TEMPLATE_PATH,
    params_file: Optional[str] = args.TEMPLATE_PARAMS_FILE,
    params: Optional[List[str]] = args.TEMPLATE_PARAMS,
    dry_run: Optional[bool] = DRY_RUN,  # noqa: ARG001
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
    generate: Optional[bool] = GENERATE_YAML,  # noqa: ARG001
) -> None:
    """***Update*** the parameters for a deployment at run time.

    \b
    🧩 ***Input file schema (yaml):***<br/>
    ```yaml
    body (map): Dictionary of parameters specific to the 'run' phase. Keys are parameter names, and values are the parameter values, which can be of type string, boolean, number, dictionary or list (string, number, dictionary).
    ```

    \b
    📝 ***Example usage:***
    ```bash
    peak blocks deployments patch-parameters <deployment-id> /path/to/body.yaml -v /path/to/params.yaml
    ```

    \b
    🆗 ***Response:***
    ```
    {...}
    ```

    🔗 [**API Documentation**](https://press.peak.ai/api-docs/index.htm#/Deployment%20Parameters/patch_v1_deployments__deploymentId__parameters_run)
    """
    body = helpers.template_handler(file, params_file, params)
    blocks_client: Block = ctx.obj["client"]
    body = helpers.remove_unknown_args(body, blocks_client.patch_parameters)
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = blocks_client.patch_parameters(deployment_id, **body)
        writer.write(response)


@app.command(short_help="Get the info for related blocks within an app.")
def get_related_block_details(
    ctx: typer.Context,
    deployment_id: Optional[str] = _DEPLOYMENT_ID_OPTION,
    fallback_details_file: Optional[str] = _FALLBACK_DETAILS_FILE,
    paging: Optional[bool] = PAGING,  # noqa: ARG001
    output_type: Optional[OutputTypesNoTable] = OUTPUT_TYPES,  # noqa: ARG001
) -> None:
    """***Get*** the info for related blocks within an app.

    \b
    📝 ***Example usage:***<br/>
    ```bash
    peak blocks deployments get_related_block_details --deployment-id=<deployment-id> --fallback-details-file=<path/to/fallback/details/file>
    ```

    \b
    🆗 ***Response:***
    ```
    {...}
    ```
    """
    blocks_client: Block = ctx.obj["client"]
    writer: Writer = ctx.obj["writer"]

    with writer.pager():
        response = blocks_client.get_related_block_details(
            deployment_id=deployment_id,
            fallback_details_file=fallback_details_file,
        )
        writer.write(response)
