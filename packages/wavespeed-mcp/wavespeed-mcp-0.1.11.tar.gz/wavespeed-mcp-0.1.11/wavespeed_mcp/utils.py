"""Utility functions for WavespeedMCP."""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Union
from wavespeed_mcp.exceptions import WavespeedMcpError


logger = logging.getLogger("wavespeed-utils")


def is_file_writeable(path: Path) -> bool:
    """Check if a file or directory is writeable.

    Args:
        path: Path to check

    Returns:
        True if the path is writeable, False otherwise
    """
    if path.exists():
        return os.access(path, os.W_OK)
    parent_dir = path.parent
    return os.access(parent_dir, os.W_OK)


def build_output_file(
    tool: str, description: str, output_path: Path, extension: str
) -> Path:
    """Build an output filename based on the tool and description.

    Args:
        tool: Name of the tool generating the file
        description: Brief description to include in the filename
        output_path: Directory to save the file in
        extension: File extension

    Returns:
        Path object for the output file
    """
    # Use a short version of the description for the filename
    short_desc = description[:20].replace(" ", "_")

    # Create a filename with timestamp
    output_file_name = (
        f"{tool}_{short_desc}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
    )
    # Return the full path (output_path / filename)
    return output_path / output_file_name


def build_output_path(
    output_directory: Optional[str] = None, base_path: Optional[str] = None
) -> Path:
    """Build the output path for saving files.

    Args:
        output_directory: User-specified output directory
        base_path: Base path to use if output_directory is not absolute

    Returns:
        Path object for the output directory

    Raises:
        WavespeedMcpError: If the directory is not writeable
    """
    # Set default base_path to desktop if not provided
    if base_path is None:
        base_path = str(Path.home() / "Desktop")

    # Ensure base_path is expanded properly
    expanded_base_path = os.path.expanduser(base_path)

    # Handle output path based on output_directory
    if output_directory is None:
        # If no output directory specified, use the expanded base path
        output_path = Path(expanded_base_path)
    elif not os.path.isabs(os.path.expanduser(output_directory)):
        # For relative paths, join with the expanded base path
        output_path = Path(expanded_base_path) / Path(output_directory)
    else:
        # For absolute paths, use the expanded output directory
        output_path = Path(os.path.expanduser(output_directory))

    # Safety checks and directory creation
    if not is_file_writeable(output_path):
        raise WavespeedMcpError(f"Directory ({output_path}) is not writeable")

    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def save_image_from_url(url: str, output_path: Path, filename: str) -> Path:
    """Download and save an image from a URL.

    Args:
        url: URL of the image to download
        output_path: Directory to save the image in
        filename: Filename to save the image as

    Returns:
        Path object for the saved image

    Raises:
        WavespeedMcpError: If the image cannot be downloaded or saved
    """
    import requests

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        full_path = output_path / filename
        with open(full_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return full_path

    except Exception as e:
        raise WavespeedMcpError(f"Failed to save image from URL: {str(e)}")


def save_base64_image(base64_data: str, output_path: Path, filename: str) -> Path:
    """Save a base64 encoded image to a file.

    Args:
        base64_data: Base64 encoded image data
        output_path: Directory to save the image in
        filename: Filename to save the image as

    Returns:
        Path object for the saved image

    Raises:
        WavespeedMcpError: If the image cannot be saved
    """
    import base64

    try:
        # Create the output directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)

        # Decode the base64 data
        image_data = base64.b64decode(base64_data)

        # Save the image
        full_path = output_path / filename
        with open(full_path, "wb") as f:
            f.write(image_data)

        return full_path

    except Exception as e:
        raise WavespeedMcpError(f"Failed to save base64 image: {str(e)}")


def get_image_as_base64(url: str, timeout: int = 30) -> tuple[str, str]:
    """Download an image from a URL and convert it to base64.

    Args:
        url: URL of the image to download
        timeout: Request timeout in seconds

    Returns:
        Tuple of (base64_string, mime_type)

    Raises:
        WavespeedMcpError: If the image cannot be downloaded or converted
    """
    import requests
    import base64

    try:
        response = requests.get(url, stream=True, timeout=timeout)
        response.raise_for_status()

        # Get content type
        content_type = response.headers.get("content-type", "image/jpeg")
        if not content_type.startswith("image/"):
            raise WavespeedMcpError(f"Invalid content type: {content_type}")

        # Get image data
        image_data = response.content

        # Convert to base64
        base64_data = base64.b64encode(image_data).decode("utf-8")

        return base64_data, content_type

    except requests.Timeout:
        raise WavespeedMcpError(
            f"Timeout downloading image from URL (after {timeout}s)"
        )
    except requests.RequestException as e:
        raise WavespeedMcpError(f"Failed to download image: {str(e)}")
    except Exception as e:
        raise WavespeedMcpError(f"Unexpected error processing image: {str(e)}")


def process_image_input(image_input: str) -> str:
    """Process different types of image input and return a format suitable for API calls.

    Args:
        image_input: Can be a URL, base64 string, or local file path

    Returns:
        Processed image string (URL or base64 with data URI prefix)

    Raises:
        WavespeedMcpError: If the image cannot be processed
    """
    import base64
    import re
    from pathlib import Path

    # Check if input is empty
    if not image_input:
        return ""

    # Check if input is already a URL
    if image_input.startswith(("http://", "https://", "ftp://")):
        return image_input

    # Check if input is already a base64 string with data URI prefix
    if image_input.startswith("data:image/"):
        return image_input

    # Check if input is a base64 string without prefix
    # Base64 strings are typically long and contain only certain characters
    if len(image_input) > 100 and re.match(r"^[A-Za-z0-9+/]+={0,2}$", image_input):
        # Add data URI prefix
        return f"data:image/jpeg;base64,{image_input}"

    # Check if input is a local file path
    path = Path(image_input)
    if path.exists() and path.is_file():
        try:
            # Read file and convert to base64
            with open(path, "rb") as f:
                file_data = f.read()

            # Determine MIME type based on file extension
            mime_type = "image/jpeg"  # Default
            if path.suffix.lower() in [".png"]:
                mime_type = "image/png"
            elif path.suffix.lower() in [".gif"]:
                mime_type = "image/gif"
            elif path.suffix.lower() in [".webp"]:
                mime_type = "image/webp"

            # Convert to base64 and add data URI prefix
            base64_data = base64.b64encode(file_data).decode("utf-8")
            return f"data:{mime_type};base64,{base64_data}"
        except Exception as e:
            raise WavespeedMcpError(f"Failed to process local image file: {str(e)}")

    # If we get here, the input format is unknown
    raise WavespeedMcpError(f"Unrecognized image input format: {image_input[:50]}...")


def is_english_text(text: str) -> bool:
    """
    Check if a text is primarily in English.

    Args:
        text: The text to check

    Returns:
        True if the text is primarily in English, False otherwise
    """
    # Simple heuristic: Check if most characters are ASCII
    # This is a basic check and can be improved with more sophisticated language detection
    if not text:
        return True

    # Count ASCII characters (English text is mostly ASCII)
    ascii_count = sum(1 for char in text if ord(char) < 128)
    # If more than 80% of characters are ASCII, consider it English
    return ascii_count / len(text) > 0.8


def validate_loras(
    loras: Optional[List[Dict[str, Union[str, float]]]]
) -> List[Dict[str, Union[str, float]]]:
    """Validate lora configuration.

    Args:
        loras: List of lora configurations

    Returns:
        Validated list of lora configurations

    Raises:
        WavespeedMcpError: If loras are invalid
    """
    if not loras:
        return []

    for lora in loras:
        if not isinstance(lora, dict):
            raise WavespeedMcpError(f"Invalid lora configuration: {lora}")

        if "path" not in lora:
            raise WavespeedMcpError(f"Missing 'path' in lora configuration: {lora}")

        if "scale" not in lora:
            lora["scale"] = 1.0

    return loras
