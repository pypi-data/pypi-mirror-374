"""Results parser agent with tool registry integration."""

from typing import Any

from loguru import logger

from ..config.settings import settings
from ..core.registry import ToolRegistry
from ..models.schema import StructuredResults


class ResultsParser:
    """Results parser agent with tool registry integration."""

    # Class variable for tool registry
    _tool_registry = None

    def __init__(self) -> None:
        self.config = settings

    @classmethod
    def _get_tool_registry(cls) -> ToolRegistry:
        """Get or create the tool registry instance for this class."""
        if cls._tool_registry is None:
            cls._tool_registry = ToolRegistry()
        return cls._tool_registry

    async def parse_results(
        self,
        input_path: str,
        workload_name: str | None = None,
    ) -> StructuredResults:
        """
        Parse results using workload-specific extraction tools.

        Args:
            input_path: Path to file or directory to parse
            workload_name: Name of the workload (for tool selection)

        Returns:
            StructuredResults with extracted data or empty results on failure
        """
        if not input_path:
            logger.error("❌ No input_path provided to parse_results.")
            return StructuredResults(iterations=[])

        if not workload_name:
            logger.error("❌ No workload_name provided. Cannot select extraction tool.")
            return StructuredResults(iterations=[])

        try:
            extracted_results = await self._try_workload_extraction(
                workload_name, input_path
            )
            if not extracted_results or not extracted_results.get("success"):
                logger.warning(
                    f"⚠️ Extraction failed or returned no results for workload '{workload_name}': {extracted_results.get('error') if extracted_results else 'No result'}"
                )
                return StructuredResults(iterations=[])

            # Attempt to parse the raw output into StructuredResults
            raw_output = extracted_results.get("raw_output")
            if not raw_output:
                logger.error("❌ No raw_output found in extraction results.")
                return StructuredResults(iterations=[])

            try:
                # If raw_output is already a dict, use it; else, try to parse as JSON
                import json

                if isinstance(raw_output, dict):
                    structured_data = raw_output
                else:
                    structured_data = json.loads(raw_output)

                # Validate/parse with StructuredResults
                results = StructuredResults.parse_obj(structured_data)
                logger.info("✅ Successfully parsed structured results.")
                return results
            except Exception as parse_exc:
                logger.error(f"❌ Failed to parse structured results: {parse_exc}")
                return StructuredResults(iterations=[])

        except Exception as e:
            logger.error(f"❌ Error in parse_results: {e}")
            logger.warning("🔄 Returning empty results due to error in results parsing")
            return StructuredResults(iterations=[])

    async def _try_workload_extraction(
        self, workload_name: str, input_path: str
    ) -> dict[str, Any]:
        """Try to extract data using workload-specific tool."""
        try:
            logger.info(f"🔧 Attempting data extraction for: {workload_name}")

            tool_registry = self._get_tool_registry()
            tool_info = tool_registry.get_workload_tool(workload_name)

            if not tool_info:
                logger.info(f"📝 No tool found for data extraction: {workload_name}")
                return {"success": False, "error": f"No tool found for {workload_name}"}

            logger.info(f"🛠️  Using existing tool: {tool_info['script']}")
            result = tool_registry.execute_extraction_tool(workload_name, input_path)

            if result.get("success"):
                logger.info(f"✅ Data extraction successful for {workload_name}")
                return result
            else:
                logger.warning(f"⚠️  Data extraction failed: {result.get('error')}")
                return {"success": False, "error": result.get("error")}

        except Exception as e:
            logger.error(f"❌ Error in data extraction: {e}")
            return {"success": False, "error": str(e)}

    def validate_extraction_completeness(
        self, results: StructuredResults, requested_metrics: list[str]
    ) -> bool:
        """Validate that data for all requested metrics was extracted."""
        if not results.iterations:
            logger.warning("⚠️  No iterations found in results")
            return False

        captured_metrics = set()
        for iteration in results.iterations:
            for instance in iteration.instances:
                for stat in instance.statistics:
                    captured_metrics.add(stat.metricName)

        missing_metrics = set(requested_metrics) - captured_metrics
        if missing_metrics:
            logger.warning(f"⚠️  Missing metrics: {missing_metrics}")
            return False

        logger.info(f"✅ All requested metrics captured: {list(captured_metrics)}")
        return True
