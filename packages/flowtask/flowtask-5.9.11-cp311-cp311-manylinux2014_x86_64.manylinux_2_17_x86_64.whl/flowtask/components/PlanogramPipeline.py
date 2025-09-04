from typing import Any, Dict, List, Union
from collections.abc import Callable
import asyncio
import json
import pandas as pd
from io import BytesIO
from pathlib import Path
from PIL import Image
from parrot.clients.gpt import OpenAIClient, OpenAIModel
from .flow import FlowComponent
from ..interfaces.pipelines.parrot import AIPipeline
from ..exceptions import ComponentError, ConfigError


DEFAULT_PLANOGRAM_CONFIG = {
    "brand": "Epson",
    "category": "Printers",
    "aisle": {
        "name": "Electronics > Printers & Printer Boxes and Supplies",
        "lighting_conditions": "bright"
    },
    "shelves": [
        {
            "level": "header",
            "products": [
                {
                    "name": "Epson EcoTank Advertisement",
                    "product_type": "promotional_graphic",
                    "mandatory": True
                }
            ],
            "allow_extra_products": True,
            "compliance_threshold": 0.95
        },
        {
            "level": "top",
            "products": [
                {
                    "name": "ET-2980",
                    "product_type": "printer",
                    "quantity_range": [1, 1],
                    "position_preference": "left"
                },
                {
                    "name": "ET-3950",
                    "product_type": "printer",
                    "quantity_range": [1, 1],
                    "position_preference": "center"
                },
                {
                    "name": "ET-4950",
                    "product_type": "printer",
                    "quantity_range": [1, 1],
                    "position_preference": "right"
                }
            ],
            "compliance_threshold": 0.9
        },
        {
            "level": "middle",
            "products": [
                {
                    "name": "ET-2980 box",
                    "product_type": "printer_box",
                    "quantity_range": [1, 2]
                },
                {
                    "name": "ET-3950 box",
                    "product_type": "printer_box",
                    "quantity_range": [1, 2]
                },
                {
                    "name": "ET-4950 box",
                    "product_type": "printer_box",
                    "quantity_range": [1, 2]
                }
            ],
            "compliance_threshold": 0.8
        }
    ],
    "advertisement_endcap": {
        "enabled": True,
        "promotional_type": "backlit_graphic",
        "position": "header",
        "text_requirements": [
            {
                "required_text": "Goodbye Cartridges",
                "match_type": "contains",
                "mandatory": True
            },
            {
                "required_text": "Hello Savings",
                "match_type": "contains",
                "mandatory": True
            }
        ]
    }
}


class PlanogramPipeline(AIPipeline, FlowComponent):
    """
    PlanogramPipeline

    Overview:
        FlowTask component for executing planogram compliance analysis using AI pipelines.
        This component extends FlowComponent and AIPipeline to process retail shelf images
        and verify compliance with planogram specifications.

    Properties:
        planogram_config (dict): Configuration defining the planogram specifications including
            brand, category, aisle info, shelf requirements, and compliance thresholds.
        reference_images_path (str|List[str]): Path(s) to reference product images for identification.
        image_column (str): Name of the DataFrame column containing BytesIO image data.
        llm_config (dict): Configuration for the LLM to use in the pipeline.
        detection_model (str): YOLO model to use for object detection.
        confidence_threshold (float): Confidence threshold for object detection.
        overlay_output_path (str): Base path for saving overlay images.

    Returns:
        DataFrame: Enhanced with new columns:
            - overall_compliance_score: Float compliance score (0-1)
            - overall_compliant: Boolean compliance status
            - compliance_analysis_markdown: Detailed markdown report
            - compliance_analysis_json: JSON structured results
            - overlay_image: PIL.Image of the analyzed image with overlays
    """

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop = None,
        job: Callable = None,
        stat: Callable = None,
        **kwargs,
    ):
        # Planogram-specific configuration
        self.planogram_config: Dict[str, Any] = kwargs.pop(
            'planogram_config', DEFAULT_PLANOGRAM_CONFIG
        )
        self.reference_images: Union[str, List[str]] = kwargs.get(
            'reference_images', []
        )
        self.image_column: str = kwargs.get(
            'image_column', 'image_data'
        )

        # Pipeline configuration
        self.llm_config: Dict[str, Any] = kwargs.get('llm_config', {})
        self.detection_model: str = kwargs.get(
            'detection_model', 'yolo11m.pt'
        )
        self.confidence_threshold: float = kwargs.get(
            'confidence_threshold',
            0.9
        )
        self.overlay_output: str = kwargs.get('overlay_output_path', 'identified')

        # Set pipeline name for AIPipeline
        kwargs['pipeline'] = 'planogram_compliance'

        # Validate required configurations
        if not self.planogram_config:
            raise ConfigError(
                "planogram_config is required"
            )

        if not self.reference_images:
            raise ConfigError(
                "reference_images is required"
            )

        # Initialize parent classes
        super().__init__(loop=loop, job=job, stat=stat, **kwargs)

    async def start(self, **kwargs):
        """Initialize the component."""
        if self.previous:
            self.data = self.input

        # Storage Directory:
        self.directory = self._taskstore.get_path().joinpath(self._program)
        # The Store Directory is used for saving overlays and other outputs
        self.store_directory = self._filestore.get_directory('').joinpath('compliance')
        self.store_directory.mkdir(parents=True, exist_ok=True)
        self.overlay_output_path = self.store_directory.joinpath(self.overlay_output)
        # create directory if it doesn't exist
        self.overlay_output_path.mkdir(parents=True, exist_ok=True)

        # Validate DataFrame has required image column
        if self.image_column not in self.data.columns:
            raise ComponentError(
                f"Image column '{self.image_column}' not found in DataFrame"
            )
        # Prepare reference images list
        self._reference_images = self._prepare_reference_images()

        # Initialize LLM for pipeline
        self._llm = self._initialize_llm()

        self._logger.info(
            f"PlanogramPipeline started with {len(self.data)} rows to process"
        )
        return True

    def _prepare_reference_images(self) -> List[Path]:
        """Convert reference image paths to Path objects."""
        reference_images = []
        for image in self.reference_images:
            image = self.mask_replacement(image)
            image_path = self.directory.joinpath('images', image)
            if not image_path.exists():
                raise ComponentError(
                    f"Reference image not found: {image_path}"
                )
            elif image_path.is_dir():
                # Get all image files from directory
                extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff']
                for ext in extensions:
                    reference_images.extend(image_path.glob(ext))
            else:
                reference_images.append(image_path)
        return reference_images

    def _initialize_llm(self):
        """Initialize the LLM client based on configuration."""
        # Default LLM configuration
        default_config = {
            'model': OpenAIModel.GPT_4_1_MINI
        }
        # Merge with user configuration
        final_config = {**default_config, **self.llm_config}
        return OpenAIClient(**final_config)

    def _convert_bytes_to_pil(self, image_data: BytesIO) -> Image.Image:
        """Convert BytesIO image data to PIL Image."""
        try:
            if isinstance(image_data, BytesIO):
                image_data.seek(0)
                return Image.open(image_data)
            elif isinstance(image_data, bytes):
                return Image.open(BytesIO(image_data))
            else:
                raise ComponentError(
                    f"Unsupported image data type: {type(image_data)}"
                )
        except Exception as e:
            raise ComponentError(
                f"Failed to convert image data to PIL Image: {e}"
            )

    def _create_markdown_report(self, result: Dict[str, Any]) -> str:
        """Generate a markdown report from pipeline results."""
        md = []
        md.append("# Planogram Compliance Analysis")
        md.append("")

        # Overall compliance
        compliance_emoji = "✅" if result.get('overall_compliant', False) else "❌"
        md.append(f"## Overall Compliance: {compliance_emoji}")
        md.append(f"**Score:** {result.get('overall_compliance_score', 0):.1%}")
        md.append("")

        # Shelf-by-shelf results
        md.append("## Shelf Analysis")
        shelf_results = result.get('step3_compliance_results', [])

        for shelf_result in shelf_results:
            level = shelf_result.shelf_level.upper()
            status = "✅" if shelf_result.compliance_status == "COMPLIANT" else "❌"

            md.append(f"### {level} Shelf: {status}")
            md.append(f"- **Product Score:** {shelf_result.compliance_score:.1%}")
            md.append(f"- **Expected Products:** {', '.join(shelf_result.expected_products)}")
            md.append(f"- **Found Products:** {', '.join(shelf_result.found_products)}")

            if hasattr(shelf_result, 'text_compliance_score'):
                md.append(f"- **Text Score:** {shelf_result.text_compliance_score:.1%}")

            if hasattr(shelf_result, 'text_compliance_results') and shelf_result.text_compliance_results:
                md.append("- **Text Requirements:**")
                for text_result in shelf_result.text_compliance_results:
                    status_emoji = "✅" if text_result.found else "❌"
                    md.append(
                        f"  - {status_emoji} '{text_result.required_text}' (confidence: {text_result.confidence:.2f})"
                    )
                    if text_result.matched_features:
                        md.append(f"    - Matched: {text_result.matched_features}")
            md.append("")

        return "\n".join(md)

    async def _process_dataframe_rows(
        self,
        df: pd.DataFrame,
        pipeline_method: str = 'run'
    ) -> List[Dict[str, Any]]:
        """
        Override the generic processing to use our specific pipeline execution logic.

        Args:
            df: DataFrame to process
            pipeline_method: Ignored for this implementation

        Returns:
            List of results from pipeline execution
        """
        results = []

        for idx, row in df.iterrows():
            result = await self._execute_pipeline_on_row(row, idx)
            results.append(result)

        return results

    async def _execute_pipeline_on_row(self, row: pd.Series, row_index: int) -> Dict[str, Any]:
        """
        Execute the pipeline on a single DataFrame row.

        Args:
            row: pandas Series representing a row
            row_index: Index of the row being processed

        Returns:
            Dictionary containing pipeline results
        """
        try:
            # Convert BytesIO to PIL Image
            image_data = row[self.image_column]
            pil_image = self._convert_bytes_to_pil(image_data)

            # Create planogram description from config
            planogram_description = self._pipeline.create_planogram_description(
                config=self.planogram_config
            )

            # Prepare overlay save path
            overlay_path = f"{self.overlay_output_path}/planogram_overlay_{row_index}.jpg"
            # and the original image path
            original_image_path = f"{self.overlay_output_path}/original_{row_index}.jpg"
            pil_image.save(original_image_path)

            # Execute pipeline
            result = await self._pipeline.run(
                image=pil_image,
                reference_images=self._reference_images,
                planogram_description=planogram_description,
                confidence_threshold=self.confidence_threshold,
                return_overlay="identified",
                overlay_save_path=overlay_path,
            )

            # Load overlay image as PIL Image
            overlay_image = None
            if result.get('overlay_path') and Path(result['overlay_path']).exists():
                overlay_image = Image.open(result['overlay_path'])

            # Create markdown and JSON reports
            markdown_report = self._create_markdown_report(result)
            json_report = json.dumps(result, default=str, indent=2)

            return {
                'row_index': row_index,
                'overall_compliance_score': result.get('overall_compliance_score', 0.0),
                'overall_compliant': result.get('overall_compliant', False),
                'compliance_analysis_markdown': markdown_report,
                'compliance_analysis_json': json_report,
                'overlay_image': overlay_image,
                'full_result': result,
                'status': 'success'
            }

        except Exception as e:
            self._loggererror(f"Error processing row {row_index}: {e}")
            return {
                'row_index': row_index,
                'overall_compliance_score': 0.0,
                'overall_compliant': False,
                'compliance_analysis_markdown': f"# Error\nFailed to process: {str(e)}",
                'compliance_analysis_json': json.dumps({"error": str(e)}),
                'overlay_image': None,
                'full_result': {},
                'status': 'error',
                'error': str(e)
            }

    def _post_process_results(self, results: List[Dict[str, Any]], df: pd.DataFrame) -> pd.DataFrame:
        """
        Integrate pipeline results back into the DataFrame.

        Args:
            results: List of pipeline execution results
            df: Original DataFrame

        Returns:
            DataFrame with new columns added
        """
        # Create a copy of the original DataFrame
        enhanced_df = df.copy()

        # Initialize new columns
        enhanced_df['overall_compliance_score'] = 0.0
        enhanced_df['overall_compliant'] = False
        enhanced_df['compliance_analysis_markdown'] = ""
        enhanced_df['compliance_analysis_json'] = ""
        enhanced_df['overlay_image'] = None

        # Populate results
        for result in results:
            idx = result['row_index']
            enhanced_df.at[idx, 'overall_compliance_score'] = result['overall_compliance_score']
            enhanced_df.at[idx, 'overall_compliant'] = result['overall_compliant']
            enhanced_df.at[idx, 'compliance_analysis_markdown'] = result['compliance_analysis_markdown']
            enhanced_df.at[idx, 'compliance_analysis_json'] = result['compliance_analysis_json']
            enhanced_df.at[idx, 'overlay_image'] = result['overlay_image']

        return enhanced_df

    async def run(self):
        """
        Execute the planogram compliance pipeline on all DataFrame rows.

        Returns:
            Enhanced DataFrame with compliance analysis results
        """
        if self.data is None or self.data.empty:
            raise ComponentError(
                "No data available for processing"
            )

        # Initialize pipeline with configuration
        pipeline_kwargs = {
            'llm': self._llm,
            'detection_model': self.detection_model
        }

        # Execute pipeline on DataFrame
        self._result = await self.execute_pipeline(
            self.data,
            **pipeline_kwargs
        )

        # Log summary statistics
        total_rows = len(self._result)
        compliant_rows = self._result['overall_compliant'].sum()
        avg_score = self._result['overall_compliance_score'].mean()

        self._logger.info(f"Processed {total_rows} images")
        self._logger.info(f"Compliant images: {compliant_rows}/{total_rows} ({compliant_rows/total_rows:.1%})")
        self._logger.info(f"Average compliance score: {avg_score:.1%}")

        # print the dataframe execution:
        self._print_data_(self._result, 'Compliance Results')
        return self._result

    async def close(self):
        """Clean up resources."""
        self._pipeline = None
        return True
