"""ModelScope MCP Server Model tools.

Provides tools for model-related operations in the ModelScope MCP Server,
such as searching for models and retrieving model details.
"""

from typing import Annotated, Literal

from fastmcp import FastMCP
from fastmcp.utilities import logging
from pydantic import Field

from ..client import get_client
from ..settings import settings
from ..types import Model

logger = logging.get_logger(__name__)


def register_model_tools(mcp: FastMCP) -> None:
    """Register all model-related tools with the MCP server.

    Args:
        mcp (FastMCP): The MCP server instance

    """

    @mcp.tool(
        annotations={
            "title": "Search Models",
        }
    )
    async def search_models(
        query: Annotated[
            str,
            Field(
                description="Keyword to search for related models. "
                "Leave empty to get all models based on other filters."
            ),
        ] = "",
        task: Annotated[
            Literal["text-generation", "text-to-image", "image-to-image"] | None,
            Field(description="Task category to filter by"),
        ] = None,
        filters: Annotated[
            list[Literal["support_inference"]] | None,
            Field(description="Additional filter options for models"),
        ] = None,
        sort: Annotated[
            Literal["Default", "DownloadsCount", "StarsCount", "GmtModified"],
            Field(description="Sort order"),
        ] = "Default",
        limit: Annotated[int, Field(description="Maximum number of models to return", ge=1, le=30)] = 10,
    ) -> list[Model]:
        """Search for models on ModelScope."""
        url = f"{settings.main_domain}/api/v1/dolphin/models"

        # Build criterion for task filter
        criterion = []
        if task:
            # Map task to API values
            task_mapping = {
                "text-generation": "text-generation",
                "text-to-image": "text-to-image-synthesis",
                "image-to-image": "image-to-image",
            }
            api_task_value = task_mapping.get(task)
            if api_task_value:
                criterion.append(
                    {
                        "category": "tasks",
                        "predicate": "contains",
                        "values": [api_task_value],
                        "sub_values": [],
                    }
                )

        # Build single criterion based on filters parameter
        single_criterion = []
        if filters:
            for filter_type in filters:
                if filter_type == "support_inference":
                    single_criterion.append(
                        {
                            "category": "inference_type",
                            "DateType": "int",
                            "predicate": "equal",
                            "IntValue": 1,
                        }
                    )

        request_data = {
            "Name": query,
            "Criterion": criterion,
            "SingleCriterion": single_criterion,
            "SortBy": sort,
            "PageNumber": 1,
            "PageSize": limit,
        }

        client = get_client()
        response = await client.put(url, request_data)

        models_data = response.get("Data", {}).get("Model", {}).get("Models", [])

        models = []
        for model_data in models_data:
            path = model_data.get("Path", "")
            name = model_data.get("Name", "")
            modelscope_url = f"{settings.main_domain}/models/{path}/{name}"

            if not path or not name:
                logger.warning(f"Skipping model with invalid path or name: {model_data}")
                continue

            model = Model(
                id=f"{path}/{name}",
                path=path,
                name=name,
                chinese_name=model_data.get("ChineseName", ""),
                created_by=model_data.get("CreatedBy"),
                license=model_data.get("License", ""),
                modelscope_url=modelscope_url,
                # Non-empty value means True, else False
                support_inference=bool(model_data.get("SupportInference", "")),
                downloads_count=model_data.get("Downloads", 0),
                stars_count=model_data.get("Stars", 0),
                created_at=model_data.get("CreatedTime", 0),
                updated_at=model_data.get("LastUpdatedTime", 0),
            )
            models.append(model)

        return models
