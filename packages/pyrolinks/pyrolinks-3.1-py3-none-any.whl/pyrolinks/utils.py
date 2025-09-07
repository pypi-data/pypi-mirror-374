import logging
from typing import Optional, Tuple
from urllib.parse import quote
from .errors import InvalidParameterError, UtilsError

logger = logging.getLogger(__name__)

def content_disposition(filename: str) -> str:
    """
    Generate a RFC 5987 / RFC 6266 compatible Content-Disposition header
    for Unicode filenames. Ensures proper encoding for browser downloads.

    Parameters:
        filename (str): Name of the file to be used in Content-Disposition.

    Returns:
        str: Formatted Content-Disposition header.

    Raises:
        InvalidParameterError: If filename is empty or None.
    """
    if not filename:
        logger.error("Empty filename provided for Content-Disposition")
        raise InvalidParameterError("Empty filename for Content-Disposition")

    encoded_filename = quote(filename)
    header_value = f"attachment; filename*=UTF-8''{encoded_filename}"
    logger.debug("Generated Content-Disposition header: %s", header_value)
    return header_value


def parse_range(range_header: Optional[str], total_size: int) -> Optional[Tuple[int, int]]:
    """
    Parse an HTTP Range header to determine the requested byte range.
    Returns a tuple (start, end) inclusive, or None if no valid range is provided.

    Supports only a single range per request.

    Examples of supported headers:
        Range: bytes=0-499      -> returns (0, 499)
        Range: bytes=500-       -> returns (500, total_size-1)
        Range: bytes=-500       -> returns (total_size-500, total_size-1)

    Parameters:
        range_header (Optional[str]): The value of the 'Range' HTTP header.
        total_size (int): Total size of the file in bytes.

    Returns:
        Optional[Tuple[int, int]]: (start, end) byte positions or None if invalid.

    Raises:
        UtilsError: If any unexpected error occurs while parsing.
    """
    if not range_header:
        logger.debug("No Range header provided")
        return None
    if not range_header.startswith("bytes="):
        logger.warning("Unsupported Range header format: %s", range_header)
        return None

    try:
        rng = range_header.split("=", 1)[1].strip()

        # Only a single range is supported; multiple ranges not handled
        if "," in rng:
            logger.warning("Multiple ranges not supported: %s", rng)
            return None

        start_str, end_str = rng.split("-", 1)

        if start_str and end_str:
            start = int(start_str)
            end = int(end_str)
            if start > end:
                logger.warning("Invalid range: start > end (%d > %d)", start, end)
                return None
        elif start_str and not end_str:
            start = int(start_str)
            end = total_size - 1
        elif not start_str and end_str:
            length = int(end_str)
            if length <= 0:
                logger.warning("Invalid suffix length in Range header: %s", end_str)
                return None
            start = max(total_size - length, 0)
            end = total_size - 1
        else:
            logger.warning("Invalid Range header format: %s", range_header)
            return None

        if start < 0 or end < start or start >= total_size:
            logger.warning("Calculated range out of bounds: start=%d, end=%d, total_size=%d", start, end, total_size)
            return None

        end = min(end, total_size - 1)
        logger.debug("Parsed Range header: start=%d, end=%d", start, end)
        return (start, end)

    except Exception as e:
        logger.exception("Failed to parse Range header: %s", range_header)
        raise UtilsError(f"Failed to parse range: {e}") from e