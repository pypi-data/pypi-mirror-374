from __future__ import annotations

import platform
import warnings
from importlib.util import find_spec
from typing import TYPE_CHECKING, Any, ClassVar, Final

from PIL import Image

from kreuzberg._mime_types import PLAIN_TEXT_MIME_TYPE
from kreuzberg._ocr._base import OCRBackend
from kreuzberg._types import ExtractionResult, Metadata, PaddleOCRConfig
from kreuzberg._utils._device import DeviceInfo, validate_device_request
from kreuzberg._utils._string import normalize_spaces
from kreuzberg._utils._sync import run_sync
from kreuzberg.exceptions import MissingDependencyError, OCRError, ValidationError

if TYPE_CHECKING:
    from pathlib import Path

try:  # pragma: no cover
    from typing import Unpack  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover
    from typing_extensions import Unpack

try:
    import numpy as np
    from paddleocr import PaddleOCR

    HAS_PADDLEOCR = True
except ImportError:
    HAS_PADDLEOCR = False
    np = None  # type: ignore[assignment]
    PaddleOCR = None


PADDLEOCR_SUPPORTED_LANGUAGE_CODES: Final[set[str]] = {"ch", "en", "french", "german", "japan", "korean"}


class PaddleBackend(OCRBackend[PaddleOCRConfig]):
    _paddle_ocr: ClassVar[Any] = None

    async def process_image(self, image: Image.Image, **kwargs: Unpack[PaddleOCRConfig]) -> ExtractionResult:
        """Asynchronously process an image and extract its text and metadata using PaddleOCR.

        Args:
            image: An instance of PIL.Image representing the input image.
            **kwargs: Configuration parameters for PaddleOCR including language, detection thresholds, etc.

        Returns:
            ExtractionResult: The extraction result containing text content, mime type, and metadata.

        Raises:
            OCRError: If OCR processing fails.
        """
        await self._init_paddle_ocr(**kwargs)

        if image.mode != "RGB":
            image = image.convert("RGB")

        image_np = np.array(image)
        try:
            result = await run_sync(self._paddle_ocr.ocr, image_np, cls=kwargs.get("use_angle_cls", True))
            return self._process_paddle_result(result, image)
        except Exception as e:
            raise OCRError(f"Failed to OCR using PaddleOCR: {e}") from e

    async def process_file(self, path: Path, **kwargs: Unpack[PaddleOCRConfig]) -> ExtractionResult:
        """Asynchronously process a file and extract its text and metadata using PaddleOCR.

        Args:
            path: A Path object representing the file to be processed.
            **kwargs: Configuration parameters for PaddleOCR including language, detection thresholds, etc.

        Returns:
            ExtractionResult: The extraction result containing text content, mime type, and metadata.

        Raises:
            OCRError: If file loading or OCR processing fails.
        """
        await self._init_paddle_ocr(**kwargs)
        try:
            image = await run_sync(Image.open, path)
            return await self.process_image(image, **kwargs)
        except Exception as e:
            raise OCRError(f"Failed to load or process image using PaddleOCR: {e}") from e

    @staticmethod
    def _process_paddle_result(result: list[Any] | Any, image: Image.Image) -> ExtractionResult:
        """Process PaddleOCR result into an ExtractionResult with metadata.

        Args:
            result: The raw result from PaddleOCR.
            image: The original PIL image.

        Returns:
            ExtractionResult: The extraction result containing text content, mime type, and metadata.
        """
        text_content = ""
        confidence_sum = 0
        confidence_count = 0

        for page_result in result:
            if not page_result:
                continue

            # Group text boxes by lines based on Y coordinate  # ~keep
            sorted_boxes = sorted(page_result, key=lambda x: x[0][0][1])
            line_groups: list[list[Any]] = []
            current_line: list[Any] = []
            prev_y: float | None = None

            for box in sorted_boxes:
                box_points, (_, _) = box
                current_y = sum(point[1] for point in box_points) / 4
                min_box_distance = 20  # Minimum distance to consider as new line  # ~keep

                if prev_y is None or abs(current_y - prev_y) > min_box_distance:
                    if current_line:
                        line_groups.append(current_line)
                    current_line = [box]
                else:
                    current_line.append(box)

                prev_y = current_y

            if current_line:
                line_groups.append(current_line)

            for line in line_groups:
                line_sorted = sorted(line, key=lambda x: x[0][0][0])  # Sort boxes by X coordinate within line  # ~keep

                for box in line_sorted:
                    _, (text, confidence) = box
                    if text:
                        text_content += text + " "
                        confidence_sum += confidence
                        confidence_count += 1

                text_content += "\n"

        if hasattr(image, "width") and hasattr(image, "height"):
            width = image.width
            height = image.height
        else:
            width, height = image.size
        metadata = Metadata(
            width=width,
            height=height,
        )

        return ExtractionResult(
            content=normalize_spaces(text_content), mime_type=PLAIN_TEXT_MIME_TYPE, metadata=metadata, chunks=[]
        )

    @classmethod
    def _is_mkldnn_supported(cls) -> bool:
        """Check if the current architecture supports MKL-DNN optimization.

        Returns:
            True if MKL-DNN is supported on this architecture.
        """
        system = platform.system().lower()
        processor = platform.processor().lower()
        machine = platform.machine().lower()

        if system in ("linux", "windows"):
            return "intel" in processor or "x86" in machine or "amd64" in machine or "x86_64" in machine

        if system == "darwin":
            return machine == "x86_64"

        return False

    @classmethod
    async def _init_paddle_ocr(cls, **kwargs: Unpack[PaddleOCRConfig]) -> None:
        """Initialize PaddleOCR with the provided configuration.

        Args:
            **kwargs: Configuration parameters for PaddleOCR including language, detection thresholds, etc.

        Raises:
            MissingDependencyError: If PaddleOCR is not installed.
            OCRError: If initialization fails.
        """
        if cls._paddle_ocr is not None:
            return

        if not HAS_PADDLEOCR or PaddleOCR is None:
            raise MissingDependencyError.create_for_package(
                dependency_group="paddleocr", functionality="PaddleOCR as an OCR backend", package_name="paddleocr"
            )

        language = cls._validate_language_code(kwargs.pop("language", "en"))

        device_info = cls._resolve_device_config(**kwargs)
        use_gpu = device_info.device_type == "cuda"

        has_gpu_package = bool(find_spec("paddlepaddle_gpu"))
        kwargs.setdefault("use_angle_cls", True)
        kwargs["use_gpu"] = use_gpu and has_gpu_package
        kwargs.setdefault("enable_mkldnn", cls._is_mkldnn_supported() and not (use_gpu and has_gpu_package))
        kwargs.setdefault("det_db_thresh", 0.3)
        kwargs.setdefault("det_db_box_thresh", 0.5)
        kwargs.setdefault("det_db_unclip_ratio", 1.6)

        if device_info.device_type == "cuda" and kwargs.get("gpu_memory_limit"):
            kwargs["gpu_mem"] = int(kwargs["gpu_memory_limit"] * 1024)

        try:
            cls._paddle_ocr = await run_sync(PaddleOCR, lang=language, show_log=False, **kwargs)
        except Exception as e:
            raise OCRError(f"Failed to initialize PaddleOCR: {e}") from e

    @classmethod
    def _resolve_device_config(cls, **kwargs: Unpack[PaddleOCRConfig]) -> DeviceInfo:
        """Resolve device configuration with backward compatibility.

        Args:
            **kwargs: Configuration parameters including device settings.

        Returns:
            DeviceInfo object for the selected device.

        Raises:
            ValidationError: If requested device is not available and fallback is disabled.
        """
        use_gpu = kwargs.get("use_gpu", False)
        device = kwargs.get("device", "auto")
        memory_limit = kwargs.get("gpu_memory_limit")
        fallback_to_cpu = kwargs.get("fallback_to_cpu", True)

        if use_gpu and device == "auto":
            warnings.warn(
                "The 'use_gpu' parameter is deprecated and will be removed in a future version. "
                "Use 'device=\"cuda\"' or 'device=\"auto\"' instead.",
                DeprecationWarning,
                stacklevel=4,
            )

            device = "auto" if use_gpu else "cpu"
        elif use_gpu and device != "auto":
            warnings.warn(
                "Both 'use_gpu' and 'device' parameters specified. The 'use_gpu' parameter is deprecated. "
                "Using 'device' parameter value.",
                DeprecationWarning,
                stacklevel=4,
            )

        if device == "mps":
            warnings.warn(
                "PaddlePaddle does not support MPS (Apple Silicon) acceleration. Falling back to CPU.",
                UserWarning,
                stacklevel=4,
            )
            device = "cpu"

        try:
            return validate_device_request(
                device,
                "PaddleOCR",
                memory_limit=memory_limit,
                fallback_to_cpu=fallback_to_cpu,
            )
        except ValidationError:
            if not use_gpu and device == "cpu":
                return DeviceInfo(device_type="cpu", name="CPU")
            raise

    @staticmethod
    def _validate_language_code(lang_code: str) -> str:
        """Convert a language code to PaddleOCR format.

        Args:
            lang_code: ISO language code or language name

        Raises:
            ValidationError: If the language is not supported by PaddleOCR

        Returns:
            Language code compatible with PaddleOCR
        """
        normalized = lang_code.lower()
        if normalized in PADDLEOCR_SUPPORTED_LANGUAGE_CODES:
            return normalized

        raise ValidationError(
            "The provided language code is not supported by PaddleOCR",
            context={
                "language_code": lang_code,
                "supported_languages": ",".join(sorted(PADDLEOCR_SUPPORTED_LANGUAGE_CODES)),
            },
        )

    def process_image_sync(self, image: Image.Image, **kwargs: Unpack[PaddleOCRConfig]) -> ExtractionResult:
        """Synchronously process an image and extract its text and metadata using PaddleOCR.

        Args:
            image: An instance of PIL.Image representing the input image.
            **kwargs: Configuration parameters for PaddleOCR including language, detection thresholds, etc.

        Returns:
            ExtractionResult: The extraction result containing text content, mime type, and metadata.

        Raises:
            OCRError: If OCR processing fails.
        """
        self._init_paddle_ocr_sync(**kwargs)

        if image.mode != "RGB":
            image = image.convert("RGB")

        image_np = np.array(image)
        try:
            result = self._paddle_ocr.ocr(image_np, cls=kwargs.get("use_angle_cls", True))
            return self._process_paddle_result(result, image)
        except Exception as e:
            raise OCRError(f"Failed to OCR using PaddleOCR: {e}") from e

    def process_file_sync(self, path: Path, **kwargs: Unpack[PaddleOCRConfig]) -> ExtractionResult:
        """Synchronously process a file and extract its text and metadata using PaddleOCR.

        Args:
            path: A Path object representing the file to be processed.
            **kwargs: Configuration parameters for PaddleOCR including language, detection thresholds, etc.

        Returns:
            ExtractionResult: The extraction result containing text content, mime type, and metadata.

        Raises:
            OCRError: If file loading or OCR processing fails.
        """
        self._init_paddle_ocr_sync(**kwargs)
        try:
            image = Image.open(path)
            return self.process_image_sync(image, **kwargs)
        except Exception as e:
            raise OCRError(f"Failed to load or process image using PaddleOCR: {e}") from e

    @classmethod
    def _init_paddle_ocr_sync(cls, **kwargs: Unpack[PaddleOCRConfig]) -> None:
        """Synchronously initialize PaddleOCR with the provided configuration.

        Args:
            **kwargs: Configuration parameters for PaddleOCR including language, detection thresholds, etc.

        Raises:
            MissingDependencyError: If PaddleOCR is not installed.
            OCRError: If initialization fails.
        """
        if cls._paddle_ocr is not None:
            return

        if not HAS_PADDLEOCR or PaddleOCR is None:
            raise MissingDependencyError.create_for_package(
                dependency_group="paddleocr", functionality="PaddleOCR as an OCR backend", package_name="paddleocr"
            )

        language = cls._validate_language_code(kwargs.pop("language", "en"))

        device_info = cls._resolve_device_config(**kwargs)
        use_gpu = device_info.device_type == "cuda"

        has_gpu_package = bool(find_spec("paddlepaddle_gpu"))
        kwargs.setdefault("use_angle_cls", True)
        kwargs["use_gpu"] = use_gpu and has_gpu_package
        kwargs.setdefault("enable_mkldnn", cls._is_mkldnn_supported() and not (use_gpu and has_gpu_package))
        kwargs.setdefault("det_db_thresh", 0.3)
        kwargs.setdefault("det_db_box_thresh", 0.5)
        kwargs.setdefault("det_db_unclip_ratio", 1.6)

        if device_info.device_type == "cuda" and kwargs.get("gpu_memory_limit"):
            kwargs["gpu_mem"] = int(kwargs["gpu_memory_limit"] * 1024)

        try:
            cls._paddle_ocr = PaddleOCR(lang=language, show_log=False, **kwargs)
        except Exception as e:
            raise OCRError(f"Failed to initialize PaddleOCR: {e}") from e
