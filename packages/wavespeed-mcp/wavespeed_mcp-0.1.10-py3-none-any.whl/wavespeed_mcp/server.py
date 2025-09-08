"""
WaveSpeed MCP Server

This server connects to WaveSpeed AI API endpoints which may involve costs.
Any tool that makes an API call is clearly marked with a cost warning.

Note: Always ensure you have proper API credentials before using these tools.
"""

import os
import requests
import time
import json
import logging
from typing import Dict, List, Optional, Union
from pydantic import BaseModel
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from wavespeed_mcp.utils import (
    build_output_path,
    build_output_file,
    validate_loras,
    get_image_as_base64,
    process_image_input,
    is_english_text,
)
from wavespeed_mcp.const import (
    DEFAULT_IMAGE_SIZE,
    DEFAULT_NUM_INFERENCE_STEPS,
    DEFAULT_GUIDANCE_SCALE,
    DEFAULT_NUM_IMAGES,
    DEFAULT_SEED,
    DEFAULT_IMAGE_LORA,
    ENV_WAVESPEED_API_KEY,
    ENV_WAVESPEED_API_HOST,
    ENV_WAVESPEED_MCP_BASE_PATH,
    ENV_RESOURCE_MODE,
    RESOURCE_MODE_URL,
    RESOURCE_MODE_BASE64,
    DEFAULT_LOG_LEVEL,
    ENV_FASTMCP_LOG_LEVEL,
    API_VERSION,
    API_BASE_PATH,
    API_IMAGE_ENDPOINT,
    API_VIDEO_ENDPOINT,
    API_IMAGE_TO_IMAGE_ENDPOINT,
    ENV_API_TEXT_TO_IMAGE_ENDPOINT,
    ENV_API_IMAGE_TO_IMAGE_ENDPOINT,
    ENV_API_VIDEO_ENDPOINT,
)
from wavespeed_mcp.exceptions import (
    WavespeedRequestError,
    WavespeedAuthError,
    WavespeedTimeoutError,
)
from wavespeed_mcp.client import WavespeedAPIClient

# Load environment variables
load_dotenv()

# Configure logging

logging.basicConfig(
    level=os.getenv(ENV_FASTMCP_LOG_LEVEL, DEFAULT_LOG_LEVEL),
    format="%(asctime)s - wavespeed-mcp - %(levelname)s - %(message)s",
)
logger = logging.getLogger("wavespeed-mcp")

# Get configuration from environment variables
api_key = os.getenv(ENV_WAVESPEED_API_KEY)
api_host = os.getenv(ENV_WAVESPEED_API_HOST, "https://api.wavespeed.ai")
base_path = os.getenv(ENV_WAVESPEED_MCP_BASE_PATH) or "~/Desktop"
resource_mode = os.getenv(ENV_RESOURCE_MODE, RESOURCE_MODE_URL)

# Validate required environment variables
if not api_key:
    raise ValueError(f"{ENV_WAVESPEED_API_KEY} environment variable is required")

# Initialize MCP server and API client
mcp = FastMCP(
    "WaveSpeed", log_level=os.getenv(ENV_FASTMCP_LOG_LEVEL, DEFAULT_LOG_LEVEL)
)
api_client = WavespeedAPIClient(api_key, f"{api_host}{API_BASE_PATH}/{API_VERSION}")


class FileInfo(BaseModel):
    """Information about a local file."""

    path: str
    index: int


class Base64Info(BaseModel):
    """Information about a base64 encoded resource."""

    data: str
    mime_type: str
    index: int


class WaveSpeedResult(BaseModel):
    """Unified model for WaveSpeed generation results."""

    status: str = "success"
    urls: List[str] = []
    base64: List[Base64Info] = []
    local_files: List[FileInfo] = []
    error: Optional[str] = None
    processing_time: float = 0.0
    model: Optional[str] = None

    def to_json(self) -> str:
        """Convert the result to a JSON string."""
        return json.dumps(self.model_dump(), indent=2)


def _process_wavespeed_request(
    api_endpoint: str,
    payload: dict,
    output_directory: Optional[str],
    prompt: str,
    resource_type: str = "image",  # "image" or "video"
    operation_name: str = "Generation",
) -> TextContent:
    """Process a WaveSpeed API request and handle the response.

    This is a common function to handle API requests, polling for results,
    and processing the output based on the resource mode.

    Args:
        api_endpoint: The API endpoint to call
        payload: The request payload
        output_directory: Directory to save generated files
        prompt: The prompt used for generation
        resource_type: Type of resource being generated ("image" or "video")
        operation_name: Name of the operation for logging

    Returns:
        TextContent with the result JSON
    """

    begin_time = time.time()
    try:
        # Make API request
        response_data = api_client.post(api_endpoint, json=payload)
        request_id = response_data.get("data", {}).get("id")

        if not request_id:
            return TextContent(
                type="text",
                text="Failed to get request ID from response. Please try again.",
            )

        logger.info(f"{operation_name} request submitted with ID: {request_id}")

        # Poll for results
        result = api_client.poll_result(request_id)
        outputs = result.get("outputs", [])

        if not outputs:
            return TextContent(
                type="text",
                text=f"No {resource_type} outputs received. Please try again.",
            )

        end = time.time()
        processing_time = end - begin_time
        
        model = result.get("model", "")

        logger.info(f"{operation_name} completed in {processing_time:.2f} seconds")

        # Prepare result
        result = WaveSpeedResult(urls=outputs, processing_time=processing_time, model=model)

        # Handle different resource modes
        if resource_mode == RESOURCE_MODE_URL:
            # Only return URLs
            pass
        elif resource_mode == RESOURCE_MODE_BASE64:
            # Get base64 encoding
            if resource_type == "video":
                # For video, usually just one is returned
                video_url = outputs[0]
                try:
                    response = requests.get(video_url)
                    response.raise_for_status()

                    # Convert to base64
                    import base64

                    base64_data = base64.b64encode(response.content).decode("utf-8")

                    result.base64.append(
                        Base64Info(data=base64_data, mime_type="video/mp4", index=0)
                    )

                    logger.info(f"Successfully encoded {resource_type} to base64")
                except Exception as e:
                    logger.error(f"Failed to encode {resource_type}: {str(e)}")
            else:
                # For images, handle multiple outputs
                for i, url in enumerate(outputs):
                    try:
                        # Get base64 encoding and MIME type
                        base64_data, mime_type = get_image_as_base64(url)
                        result.base64.append(
                            Base64Info(data=base64_data, mime_type=mime_type, index=i)
                        )
                        logger.info(
                            f"Successfully encoded {resource_type} {i+1}/{len(outputs)} to base64"
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to encode {resource_type} {i+1}: {str(e)}"
                        )
        else:
            # Save to local file
            output_path = build_output_path(output_directory, base_path)
            output_path.mkdir(parents=True, exist_ok=True)

            if resource_type == "video":
                # For video, usually just one is returned
                video_url = outputs[0]
                try:
                    filename = build_output_file(
                        resource_type, prompt, output_path, "mp4"
                    )

                    response = requests.get(video_url, stream=True)
                    response.raise_for_status()

                    with open(filename, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    result.local_files.append(FileInfo(path=str(filename), index=0))
                    logger.info(f"Successfully saved {resource_type} to {filename}")
                except Exception as e:
                    logger.error(f"Failed to save {resource_type}: {str(e)}")
            else:
                # For images, handle multiple outputs
                for i, url in enumerate(outputs):
                    try:
                        output_file_name = build_output_file(
                            resource_type, f"{i}_{prompt}", output_path, "jpeg"
                        )

                        response = requests.get(url)
                        response.raise_for_status()

                        with open(output_file_name, "wb") as f:
                            f.write(response.content)

                        result.local_files.append(
                            FileInfo(path=str(output_file_name), index=i)
                        )
                        logger.info(
                            f"Successfully saved {resource_type} {i+1}/{len(outputs)} to {output_file_name}"
                        )
                    except Exception as e:
                        logger.error(f"Failed to save {resource_type} {i+1}: {str(e)}")

        # Return unified JSON structure
        return TextContent(type="text", text=result.to_json())

    except (WavespeedAuthError, WavespeedRequestError, WavespeedTimeoutError) as e:
        logger.error(f"{operation_name} failed: {str(e)}")
        error_result = WaveSpeedResult(
            status="error", error=f"Failed to generate {resource_type}: {str(e)}"
        )
        return TextContent(type="text", text=error_result.to_json())
    except Exception as e:
        logger.exception(f"Unexpected error during {operation_name.lower()}: {str(e)}")
        error_result = WaveSpeedResult(
            status="error", error=f"An unexpected error occurred: {str(e)}"
        )
        return TextContent(type="text", text=error_result.to_json())


def get_models(model):
    if model == "":
        model = os.getenv(ENV_API_TEXT_TO_IMAGE_ENDPOINT, API_IMAGE_ENDPOINT)

    if not model.startswith("/"):
        model = "/" + model

    return model


def get_image_models(model):
    if model == "":
        model = os.getenv(ENV_API_IMAGE_TO_IMAGE_ENDPOINT, API_IMAGE_TO_IMAGE_ENDPOINT)

    if not model.startswith("/"):
        model = "/" + model

    return model


def get_video_models(model):
    if model == "":
        model = os.getenv(ENV_API_VIDEO_ENDPOINT, API_VIDEO_ENDPOINT)

    if not model.startswith("/"):
        model = "/" + model

    return model


@mcp.tool(
    description="""Generate an image from text prompt using WaveSpeed AI.

    Args:
        prompt (str): Required. Text description of the image to generate. MUST BE IN ENGLISH. Non-English prompts will be rejected or result in poor quality outputs.
        model (str, optional): Model to use for image generation.
        loras (list, optional): List of LoRA models to use, each with a path and scale. Format: [{"path": "model_path", "scale": weight_value}]. Default model used if not provided.
        size (str, optional): Size of the output image in format "width*height", e.g., "512*512". Default: 1024*1024.
        num_inference_steps (int, optional): Number of denoising steps. Higher values improve quality but increase generation time. Default: 30.
        guidance_scale (float, optional): Guidance scale for text adherence. Controls how closely the image matches the text description. Default: 7.5.
        num_images (int, optional): Number of images to generate. Default: 1.
        seed (int, optional): Random seed for reproducible results. Set to -1 for random. Default: -1.
        enable_safety_checker (bool, optional): Whether to enable safety filtering. Default: True.
        output_directory (str, optional): Directory to save the generated images. Uses a temporary directory if not provided.

    Returns:
        WaveSpeedResult object with the result of the image generation, containing:
        - status: "success" or "error"
        - urls: List of image URLs if successful
        - base64: List of base64 encoded images if resource_mode is set to base64
        - local_files: List of local file paths if resource_mode is set to local
        - error: Error message if status is "error"
        - processing_time: Time taken to generate the image(s)
        
    Examples:
        Basic usage: text_to_image(prompt="A golden retriever running on grass")
        Advanced usage: text_to_image(
            prompt="A golden retriever running on grass", 
            size="1024*1024", 
            num_inference_steps=50,
            seed=42
        )
        
    Note: 
        For optimal results, always provide prompts in English, regardless of your interface language.
        Non-English prompts may result in lower quality or unexpected images.
    """
)
def text_to_image(
    prompt: str,
    model: Optional[str] = None,
    loras: Optional[List[Dict[str, Union[str, float]]]] = None,
    size: str = DEFAULT_IMAGE_SIZE,
    num_inference_steps: int = DEFAULT_NUM_INFERENCE_STEPS,
    guidance_scale: float = DEFAULT_GUIDANCE_SCALE,
    num_images: int = DEFAULT_NUM_IMAGES,
    seed: int = DEFAULT_SEED,
    enable_safety_checker: bool = True,
    output_directory: str = None,
):
    """Generate an image from text prompt using WaveSpeed AI."""

    if not prompt:
        return TextContent(
            type="text",
            text="Prompt is required for image generation. Please provide an English prompt for optimal results.",
        )

    # Check if prompt is in English
    if not is_english_text(prompt):
        return TextContent(
            type="text",
            text="Prompt must be in English. Please provide an English prompt for optimal results.",
        )

    # Validate and set default loras if not provided
    if not loras:
        loras = [DEFAULT_IMAGE_LORA]
    else:
        loras = validate_loras(loras)

    # Prepare API payload
    payload = {
        "prompt": prompt,
        "loras": loras,
        "size": size,
        "num_inference_steps": num_inference_steps,
        "guidance_scale": guidance_scale,
        # "num_images": num_images,
        "seed": seed,
        "enable_base64_output": False,  # 使用URL，后续自己转换为base64
        "enable_safety_checker": enable_safety_checker,
    }

    return _process_wavespeed_request(
        api_endpoint=get_models(model),
        payload=payload,
        output_directory=output_directory,
        prompt=prompt,
        resource_type="image",
        operation_name="Image generation",
    )


@mcp.tool(
    description="""Generate an image from an existing image using WaveSpeed AI.

    Args:
        image (str): Required. URL, base64 string, or local file path of the input image to modify.
        prompt (str): Required. Text description of the desired modifications. MUST BE IN ENGLISH. Non-English prompts will be rejected or result in poor quality outputs.
        model (str, optional): Model to use for image generation.
        guidance_scale (float, optional): Guidance scale for text adherence. Controls how closely the output follows the prompt. Range: [1.0-10.0]. Default: 3.5.
        enable_safety_checker (bool, optional): Whether to enable safety filtering. Default: True.
        output_directory (str, optional): Directory to save the generated images. Uses a temporary directory if not provided.

    Returns:
        WaveSpeedResult object with the result of the image generation, containing:
        - status: "success" or "error"
        - urls: List of image URLs if successful
        - base64: List of base64 encoded images if resource_mode is set to base64
        - local_files: List of local file paths if resource_mode is set to local
        - error: Error message if status is "error"
        - processing_time: Time taken to generate the image(s)
        
    Examples:
        Basic usage: image_to_image(image="https://example.com/image.jpg", prompt="Make it look like winter")
        Local file: image_to_image(image="/path/to/local/image.jpg", prompt="Convert to oil painting style")
        
    Note: 
        For optimal results, always provide prompts in English, regardless of your interface language.
        Non-English prompts may result in lower quality or unexpected images.
    """
)
def image_to_image(
    image: str,
    prompt: str,
    model: Optional[str] = None,
    guidance_scale: float = 3.5,
    enable_safety_checker: bool = True,
    output_directory: str = None,
):
    """Generate an image from an existing image using WaveSpeed AI."""

    if not image:
        return TextContent(
            type="text", text="Input image is required for image-to-image generation"
        )

    if not prompt:
        return TextContent(
            type="text",
            text="Prompt is required for image-to-image generation. Please provide an English prompt for optimal results.",
        )

    # Check if prompt is in English
    if not is_english_text(prompt):
        return TextContent(
            type="text",
            text="Prompt must be in English. Please provide an English prompt for optimal results.",
        )

    # handle image input
    try:
        processed_image = process_image_input(image)
        logger.info("Successfully processed input image")
    except Exception as e:
        logger.error(f"Failed to process input image: {str(e)}")
        return TextContent(type="text", text=f"Failed to process input image: {str(e)}")

    # Prepare API payload
    payload = {
        "image": processed_image,
        "prompt": prompt,
        "guidance_scale": guidance_scale,
        "enable_safety_checker": enable_safety_checker,
    }

    return _process_wavespeed_request(
        api_endpoint=get_image_models(model),
        payload=payload,
        output_directory=output_directory,
        prompt=prompt,
        resource_type="image",
        operation_name="Image-to-image generation",
    )


@mcp.tool(
    description="""Generate a video using WaveSpeed AI.

    Args:
        image (str): Required. URL, base64 string, or local file path of the input image to animate.
        prompt (str): Required. Text description of the video to generate. MUST BE IN ENGLISH. Non-English prompts will be rejected or result in poor quality outputs.
        model (str, optional): Model to use for video generation.
        negative_prompt (str, optional): Text description of what to avoid in the video. Default: "".
        loras (list, optional): List of LoRA models to use, each with a path and scale. Format: [{"path": "model_path", "scale": weight_value}]. Default: [].
        size (str, optional): Size of the output video in format "width*height". Default: "832*480".
        num_inference_steps (int, optional): Number of denoising steps. Higher values improve quality but increase generation time. Default: 30.
        duration (int, optional): Duration of the video in seconds. Must be either 5 or 10. Default: 5.
        guidance_scale (float, optional): Guidance scale for text adherence. Controls how closely the video matches the text description. Default: 5.
        flow_shift (int, optional): Shift of the flow in the video. Affects motion intensity. Default: 3.
        seed (int, optional): Random seed for reproducible results. Set to -1 for random. Default: -1.
        enable_safety_checker (bool, optional): Whether to enable safety filtering. Default: True.
        output_directory (str, optional): Directory to save the generated video. Uses a temporary directory if not provided.

    Returns:
        WaveSpeedResult object with the result of the video generation, containing:
        - status: "success" or "error"
        - urls: List of video URLs if successful
        - base64: List of base64 encoded videos if resource_mode is set to base64
        - local_files: List of local file paths if resource_mode is set to local
        - error: Error message if status is "error"
        - processing_time: Time taken to generate the video(s)
        
    Examples:
        Basic usage: generate_video(image="https://example.com/image.jpg", prompt="The dog running through a forest")
        Advanced usage: generate_video(
            image="/path/to/local/image.jpg", 
            prompt="The dog running through a forest", 
            duration=10,
            negative_prompt="blurry, low quality"
        )
        
    Note: 
        IMPORTANT: Prompts MUST be in English. The system only processes English prompts properly.
        Non-English prompts will be rejected or produce low-quality results. If user input is not in English,
        you MUST translate it to English before passing to this tool.
    """
)
def generate_video(
    image: str,
    prompt: str,
    model: Optional[str] = None,
    negative_prompt: str = "",
    loras: Optional[List[Dict[str, Union[str, float]]]] = None,
    size: str = "832*480",
    num_inference_steps: int = 30,
    duration: int = 5,
    guidance_scale: float = 5,
    flow_shift: int = 3,
    seed: int = -1,
    enable_safety_checker: bool = True,
    output_directory: str = None,
):
    """Generate a video using WaveSpeed AI."""

    if not image:
        # raise WavespeedRequestError("Input image is required for video generation")
        return TextContent(
            type="text",
            text="Input image is required for video generation. Can use generate_image tool to generate an image first.",
        )

    if not prompt:
        # raise WavespeedRequestError("Prompt is required for video generation")
        return TextContent(
            type="text",
            text="Prompt is required for video generation. Please provide an English prompt for optimal results.",
        )

    # Check if prompt is in English
    if not is_english_text(prompt):
        return TextContent(
            type="text",
            text="Prompt must be in English. Please provide an English prompt for optimal results.",
        )

    # Validate and set default loras if not provided
    if not loras:
        loras = []
    else:
        loras = validate_loras(loras)

    if duration not in [5, 10]:
        return TextContent(
            type="text",
            text="Duration must be 5 or 10 seconds. Please set it to 5 or 10.",
        )

    # handle image input
    try:
        processed_image = process_image_input(image)
        logger.info("Successfully processed input image")
    except Exception as e:
        logger.error(f"Failed to process input image: {str(e)}")
        return TextContent(type="text", text=f"Failed to process input image: {str(e)}")

    # Prepare API payload
    payload = {
        "image": processed_image,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "loras": loras,
        "size": size,
        "num_inference_steps": num_inference_steps,
        "duration": duration,
        "guidance_scale": guidance_scale,
        "flow_shift": flow_shift,
        "seed": seed,
        "enable_safety_checker": enable_safety_checker,
    }

    return _process_wavespeed_request(
        api_endpoint=get_video_models(model),
        payload=payload,
        output_directory=output_directory,
        prompt=prompt,
        resource_type="video",
        operation_name="Video generation",
    )


def main():
    print("Starting WaveSpeed MCP server")
    """Run the WaveSpeed MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()
