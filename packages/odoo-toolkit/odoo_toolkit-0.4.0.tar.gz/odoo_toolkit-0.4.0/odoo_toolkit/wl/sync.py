from enum import Enum
from typing import Annotated

from typer import Argument, Exit, Option, Typer

from odoo_toolkit.common import (
    EMPTY_LIST,
    Status,
    TransientProgress,
    normalize_list_option,
    print_command_title,
    print_error,
    print_success,
    print_warning,
)

from .common import (
    WEBLATE_AUTOTRANSLATE_ENDPOINT,
    WEBLATE_PROJECT_COMPONENTS_ENDPOINT,
    WeblateApi,
    WeblateApiError,
    WeblateComponentResponse,
    WeblatePagedResponse,
    get_weblate_lang,
)


class FilterType(str, Enum):
    """Filter types available for the autotranslate endpoint."""

    ALL = "all"
    NOTTRANSLATED = "nottranslated"
    TODO = "todo"
    FUZZY = "fuzzy"

app = Typer()


@app.command()
def sync(
    src_project: Annotated[str, Argument(help="The Weblate project to copy the translations from.")],
    dest_project: Annotated[str, Argument(help="The Weblate project to copy the translations to.")],
    languages: Annotated[list[str], Option("--language", "-l", help="The language codes to copy.")],
    components: Annotated[
        list[str],
        Option(
            "--component",
            "-c",
            help="The Weblate components to copy. Copies all components if none are specified.",
        ),
    ] = EMPTY_LIST,
    filter_type: Annotated[
        FilterType,
        Option(
            "--filter",
            "-f",
            help="Specify which strings need to be changed. Either all strings (`all`), untranslated strings "
            "(`nottranslated`), unfinished strings (`todo`), or strings marked for edit (`fuzzy`).",
        ),
    ] = FilterType.NOTTRANSLATED,
) -> None:
    """Sync translations from one Weblate project to another.

    This command allows you to copy existing translations of components in one Weblate project to the same components in
    another Weblate project. You need to specify for which language(s) you want the translations copied.

    You can provide specific components or none at all. In that case, all common components will be used.

    Finally you can specify which type of strings you want to have translated in the destination project.
    """
    print_command_title(":memo: Odoo Weblate Sync Translations")

    # Support comma-separated values as well.
    languages = normalize_list_option(languages)
    components = normalize_list_option(components)

    try:
        weblate_api = WeblateApi()
    except NameError as e:
        print_error(str(e))
        raise Exit from e

    try:
        total_dest_components = weblate_api.get(
            WeblatePagedResponse, WEBLATE_PROJECT_COMPONENTS_ENDPOINT.format(project=dest_project),
        ).get("count", 0)
    except WeblateApiError as e:
        print_error("Weblate API Error", str(e))
        raise Exit from e

    success_count, partial_count, failure_count = _process_components(
        weblate_api, src_project, dest_project, components, languages, total_dest_components, filter_type,
    )

    total_processed = success_count + partial_count + failure_count

    if total_processed == 0:
        print_warning("No components were found or selected to copy.")
        return

    if partial_count == 0 and failure_count == 0:
        print_success(f"Successfully copied translations for all {success_count} component(s)!")
    else:
        summary = [
            "Operation finished with errors:",
            f"  - [b]{success_count}[/b] component(s) [b]succeeded[/b] completely.",
            f"  - [b]{partial_count}[/b] component(s) succeeded for [b]some languages[/b] but failed for others.",
            f"  - [b]{failure_count}[/b] component(s) [b]failed[/b] completely.",
        ]
        print_error("\n".join(summary))


def _get_project_components(api: WeblateApi, project: str) -> set[str]:
    """Fetch and return a set of component slugs for a given project."""
    try:
        component_generator = api.get_generator(
            WeblateComponentResponse, WEBLATE_PROJECT_COMPONENTS_ENDPOINT.format(project=project),
        )
        return {c.get("slug") for c in component_generator}
    except WeblateApiError as e:
        print_error(f"Weblate API Error: Failed to fetch components for project '{project}'.", str(e))
        raise Exit from e


def _copy_language_translations(
    api: WeblateApi, src_project: str, dest_project: str, component: str, languages: list[str], filter_type: FilterType,
) -> Status:
    """Copy translations for a specific component across multiple languages."""
    if not languages:
        return Status.SUCCESS

    success_count = 0
    failure_count = 0
    for language in languages:
        try:
            api.post(
                str,
                WEBLATE_AUTOTRANSLATE_ENDPOINT.format(
                    project=dest_project, component=component, language=get_weblate_lang(language),
                ),
                json={
                    "mode": "translate",
                    "filter_type": filter_type.value,
                    "auto_source": "others",
                    "component": f"{src_project}/{component}",
                    "threshold": 100,  # Not used, but required.
                },
            )
            success_count += 1
        except WeblateApiError as e:  # noqa: PERF203
            failure_count += 1
            print_error(f"An API call failed. Copying for '{component}' and '{language}' failed.", str(e))

    if failure_count == 0:
        return Status.SUCCESS
    if success_count > 0:
        return Status.PARTIAL
    return Status.FAILURE


def _process_components(
    api: WeblateApi,
    src_project: str,
    dest_project: str,
    components: list[str],
    languages: list[str],
    total_dest_components: int,
    filter_type: FilterType,
) -> tuple[int, int, int]:
    """Iterate through destination components, filter them, and call the translation copy function.

    Returns a tuple of (success_count, failure_count).
    """
    counts = {Status.SUCCESS: 0, Status.PARTIAL: 0, Status.FAILURE: 0}
    src_components = _get_project_components(api, src_project)

    with TransientProgress() as progress:
        progress_task = progress.add_task(
            f"Copying translations from {src_project} to {dest_project}", total=total_dest_components,
        )
        try:
            for dest_component in api.get_generator(
                WeblateComponentResponse, WEBLATE_PROJECT_COMPONENTS_ENDPOINT.format(project=dest_project),
            ):
                progress.advance(progress_task)
                component = dest_component.get("slug")

                if components and component not in components:
                    continue
                if component not in src_components:
                    print_warning(f"Component '{component}' not found in source project '{src_project}'. Skipping.")
                    continue

                status = _copy_language_translations(api, src_project, dest_project, component, languages, filter_type)
                counts[status] += 1
        except WeblateApiError as e:
            print_error("Fetching components failed.", str(e))
            counts[Status.FAILURE] += 1

    return counts[Status.SUCCESS], counts[Status.PARTIAL], counts[Status.FAILURE]
