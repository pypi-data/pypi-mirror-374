#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2025.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

import json
from pathlib import Path

import typer
from ibm_watsonx_ai import APIClient  # type:ignore[import-untyped]
from typing_extensions import Annotated

from ibm_watsonx_ai_cli.utils.chat import ChatAgent
from ibm_watsonx_ai_cli.utils.github import (
    download_and_extract_resource,
    get_available_resources,
)
from ibm_watsonx_ai_cli.utils.utils import (
    ensure_template_is_cli_compatible,
    get_directory,
    get_package_root,
    get_resource_name,
    install_agent_library,
    is_cli_compatible,
    load_question_payload,
    prepare_client,
    prepare_resources_prompt,
)

cli = typer.Typer(no_args_is_help=True)


@cli.command(help="List of available templates.")
def list() -> None:
    """
    List all available templates.

    Usage:
        watsonx-ai template list
    """
    agents = get_available_resources(resource_type="template")
    typer.echo(prepare_resources_prompt(agents, resource_type="template"))


@cli.command(help="Creates a selected template in a local environment.")
def new(
    name: Annotated[str | None, typer.Argument(help="Template name")] = None,
    target: Annotated[
        str | None, typer.Argument(help="The name of the folder to create")
    ] = None,
) -> None:
    """
    Create a template in a local environment.

    Args:
        name (str | None): The name of the template to use. If not provided, the user will be prompted to choose one.
        target (str | None): The target folder where the template will be downloaded. If not provided, the user will be prompted to enter one.

    Usage:
        watsonx-ai template new [TEMPLATE_NAME] [TARGET_FOLDER]
    """
    available_agents = get_available_resources(resource_type="template")
    selected_agent = get_resource_name(
        available_resources=available_agents,
        resource_name=name,
        resource_type="template",
    )
    target_directory = get_directory(
        selected_agent,
        target,
    )

    typer.echo(
        typer.style(
            f"---> Downloading template '{selected_agent}' into '{target_directory}'...",
            fg="bright_green",
            bold=True,
        )
    )
    target_directory = download_and_extract_resource(
        selected_agent, target_directory, resource_type="template"
    )
    typer.echo(
        typer.style(
            f"---> Template '{selected_agent}' downloaded successfully into '{target_directory}'.",
            fg="bright_green",
            bold=True,
        )
    )
    cli_compatible = is_cli_compatible(Path().cwd() / target_directory)

    if cli_compatible:
        typer.echo(
            typer.style(
                "\nNext steps\n",
                fg="bright_blue",
                bold=True,
            )
        )

        typer.echo(
            typer.style(
                "Configure your agent:\n\n"
                "Before running or deploying the agent, copy and update your configuration file:\n\n"
                f"  cd {target_directory}\n"
                "  cp config.toml.example config.toml\n"
                "  cp template.env .env\n\n"
                "Run the agent locally:\n\n"
                '  watsonx-ai template invoke "<your-question>"\n\n'
                "Deploy the agent as an AI service:\n\n"
                "  watsonx-ai service new\n",
            )
        )
    else:
        typer.echo(
            typer.style(
                "\nPlease refer to the README.md file for usage details.",
                fg="bright_blue",
                bold=True,
            )
        )


@cli.command(help="Executes the template code locally with demo data.")
def invoke(
    query: Annotated[str | None, typer.Argument(help="Content of User Message")] = None,
) -> None:
    """
    Execute the template code locally using demo data.

    Args:
        query (str | None): The query to send to the locally executed template.

    Usage:
        watsonx-ai template invoke "<question>"
    """
    ensure_template_is_cli_compatible(
        project_directory=Path().cwd(), cli_method="watsonx-ai template invoke"
    )

    project_directory = get_package_root()
    install_agent_library(project_directory=project_directory)

    chat_agent = ChatAgent(agent_root_directory=project_directory)

    if query is None:
        query = load_question_payload()

    chat_agent.chat_with_agent_locally(agent_payload=query)


@cli.command(
    help="Evaluates the agent locally using the provided metrics and input data."
)
def eval(
    tests_files: str = typer.Option(
        ..., "--tests", help="List of input data files for evaluation"
    ),
    metrics: str = typer.Option(
        "answer_similarity,answer_relevance,text_reading_ease,unsuccessful_request_metric,text_grade_level",
        "--metrics",
        help="List of evaluation metrics. "
        "Possible metrics: answer_similarity, answer_relevance, text_reading_ease, unsuccessful_request_metric, text_grade_level. "
        "If not specified all metrics are calculated. "
        "For metrics answer_similarity and answer_relevance, the llm as judge evaluator can be used.",
    ),
    evaluator: str = typer.Option(
        None,
        "--evaluator",
        help="Specify a model name for evaluation, or use 'llm_as_judge' for a predefined choice (`meta-llama/llama-3-3-70b-instruct`, or `mistralai/mistral-small-3-1-24b-instruct-2503` if former is not available)",
    ),
) -> None:
    from ibm_watsonx_gov.clients.api_client import (  # type:ignore[import-untyped]
        APIClient as GovAPIClient,
    )
    from ibm_watsonx_gov.clients.api_client import (  # type:ignore[import-untyped]
        Credentials as GovCredentials,
    )
    from ibm_watsonx_gov.config.gen_ai_configuration import (  # type:ignore[import-untyped]
        GenAIConfiguration,
    )
    from ibm_watsonx_gov.entities.enums import (  # type:ignore[import-untyped]
        TaskType,
    )
    from ibm_watsonx_gov.evaluators import (  # type:ignore[import-untyped] # noqa: E402
        MetricsEvaluator,
    )

    from ibm_watsonx_ai_cli.utils.evaluate import (
        generate_metrics,
        initialize_ai_service,
        run_agent,
    )

    ensure_template_is_cli_compatible(
        project_directory=Path().cwd(), cli_method="watsonx-ai template eval"
    )

    client: APIClient = prepare_client()
    if client.CLOUD_PLATFORM_SPACES:
        if client.credentials.api_key is not None:
            gov_client = GovAPIClient(
                credentials=GovCredentials(api_key=client.credentials.api_key)
            )
        else:
            typer.echo(
                typer.style(
                    "Incorrect credentials provided for evaluations. API key is required",
                    fg="bright_red",
                    bold=True,
                )
            )
            raise typer.Exit(code=1)
    else:
        if (
            client.credentials.username is not None
            and client.credentials.password is not None
        ):
            gov_client = GovAPIClient(
                credentials=GovCredentials(
                    username=client.credentials.username,
                    password=client.credentials.password,
                    url=client.credentials.url,
                    version=client.credentials.version,
                    disable_ssl=True,
                )
            )
        elif (
            client.credentials.username is not None
            and client.credentials.api_key is not None
        ):
            gov_client = GovAPIClient(
                credentials=GovCredentials(
                    username=client.credentials.username,
                    api_key=client.credentials.api_key,
                    url=client.credentials.url,
                    version=client.credentials.version,
                    disable_ssl=True,
                )
            )
        else:
            typer.echo(
                typer.style(
                    "Incorrect credentials provided for evaluations. Username and Password or Username and API key are required",
                    fg="bright_red",
                    bold=True,
                )
            )
            raise typer.Exit(code=1)

    project_directory = get_package_root()
    install_agent_library(project_directory=project_directory)

    config = GenAIConfiguration(
        input_fields=["input"],
        output_fields=["output"],
        reference_fields=["ground_truth"],
        task_type=TaskType.QA,
    )
    available_models = [
        model_spec["model_id"]
        for model_spec in client.foundation_models.get_model_specs().get(
            "resources", []
        )
    ]
    default_models = (
        "meta-llama/llama-3-3-70b-instruct",
        "mistralai/mistral-small-3-1-24b-instruct-2503",
    )
    eval_model_used = None
    if evaluator is None:
        metrics_classes = generate_metrics(metrics=metrics)
    elif evaluator == "llm_as_judge":
        for model in default_models:
            if model in available_models:
                eval_model_used = model
                metrics_classes = generate_metrics(
                    metrics=metrics, evaluator=model, client=client
                )
                break
        else:
            typer.echo(
                typer.style(
                    "Incorrect evaluation model. Available models are: {}".format(
                        available_models
                    ),
                    fg="bright_red",
                    bold=True,
                )
            )
            raise typer.Exit(code=1)

    else:
        if evaluator in available_models:
            eval_model_used = evaluator
            metrics_classes = generate_metrics(
                metrics=metrics, evaluator=evaluator, client=client
            )
        else:
            typer.echo(
                typer.style(
                    "Incorrect evaluation model. Available models are: {}".format(
                        available_models
                    ),
                    fg="bright_red",
                    bold=True,
                )
            )
            raise typer.Exit(code=1)

    metrics_evaluator = MetricsEvaluator(configuration=config, api_client=gov_client)

    inference_service_generate = initialize_ai_service(project_directory, client)
    for file in tests_files.split(","):
        with open(file, "r") as evaluation_file:
            data = [json.loads(line) for line in evaluation_file]

        for d in data:
            response = run_agent(inference_service_generate, d["input"], client)
            d["output"] = response

        typer.echo(
            typer.style(
                f'\nEvaluation result for file "{file}":',
                fg=typer.colors.GREEN,
                bold=True,
            )
        )
        if eval_model_used:
            typer.echo(
                typer.style(
                    f'\nllm_as_judge = "{eval_model_used}"',
                    fg=typer.colors.GREEN,
                    bold=True,
                )
            )

        result = metrics_evaluator.evaluate(data=data, metrics=metrics_classes)

        for r in result.metrics_result:
            print(r.model_dump_json(indent=2))
            print(3 * "\n")


if __name__ == "__main__":
    cli()
