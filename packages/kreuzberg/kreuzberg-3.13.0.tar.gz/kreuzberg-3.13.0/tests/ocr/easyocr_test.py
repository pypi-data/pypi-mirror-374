from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Any
from unittest.mock import Mock, patch

import pytest
from PIL import Image

from kreuzberg import EasyOCRConfig
from kreuzberg._ocr._easyocr import (
    EasyOCRBackend,
)
from kreuzberg._types import ExtractionResult
from kreuzberg.exceptions import MissingDependencyError, OCRError, ValidationError

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture


def raise_import_error(name: str, *args: Any, **kwargs: Any) -> Any:
    if name == "easyocr":
        raise ImportError("No module named 'easyocr'")
    if name == "torch":
        raise ImportError("No module named 'torch'")
    return __import__(name, *args, **kwargs)


@pytest.fixture
def backend() -> EasyOCRBackend:
    EasyOCRBackend._reader = None
    return EasyOCRBackend()


@pytest.fixture
def config_dict() -> dict[str, Any]:
    return asdict(EasyOCRConfig())


@pytest.fixture
def mock_easyocr_reader() -> Mock:
    mock_reader = Mock()
    mock_reader.readtext.return_value = [
        (
            [[0, 0], [100, 0], [100, 20], [0, 20]],
            "Sample OCR text",
            0.95,
        )
    ]
    return mock_reader


@pytest.fixture(autouse=True)
def reset_reader(mocker: MockerFixture) -> None:
    EasyOCRBackend._reader = None


@pytest.mark.parametrize(
    "language_code,expected_result",
    [
        ("en", ["en"]),
        ("EN", ["en"]),
        ("fr", ["fr"]),
        ("de", ["de"]),
        ("ja", ["ja"]),
        ("ch_sim", ["ch_sim"]),
        ("ch_tra", ["ch_tra"]),
        ("ko", ["ko"]),
        ("en,fr", ["en", "fr"]),
        ("en,ch_sim", ["en", "ch_sim"]),
        ("en,fr,ja", ["en", "fr", "ja"]),
        ("en, fr", ["en", "fr"]),
        (" en , fr ", ["en", "fr"]),
    ],
)
def test_validate_language_code_valid(language_code: str, expected_result: list[str]) -> None:
    result = EasyOCRBackend._validate_language_code(language_code)
    assert result == expected_result


@pytest.mark.parametrize(
    "language_list,expected_result",
    [
        (["en"], ["en"]),
        (["en", "fr"], ["en", "fr"]),
        (["en", "ch_sim"], ["en", "ch_sim"]),
        (["EN", "FR", "JA"], ["en", "fr", "ja"]),
    ],
)
def test_validate_language_code_list_valid(language_list: list[str], expected_result: list[str]) -> None:
    result = EasyOCRBackend._validate_language_code(language_list)
    assert result == expected_result


@pytest.mark.parametrize(
    "invalid_language_code",
    [
        "invalid",
        "english",
        "español",
        "русский",
        "eng",
        "deu",
        "fra",
        "jpn",
        "",
        "123",
    ],
)
def test_validate_language_code_invalid(invalid_language_code: str) -> None:
    with pytest.raises(ValidationError) as excinfo:
        EasyOCRBackend._validate_language_code(invalid_language_code)

    assert "language_code" in excinfo.value.context
    assert excinfo.value.context["language_code"] == invalid_language_code
    assert "supported_languages" in excinfo.value.context
    assert "not supported by EasyOCR" in str(excinfo.value)


@pytest.mark.parametrize(
    "mixed_language_codes",
    [
        "en,invalid",
        "invalid,en",
        "en,invalid,fr",
        ["en", "invalid"],
        ["invalid", "en"],
        ["en", "invalid", "fr"],
        "en,eng",
    ],
)
def test_validate_language_code_mixed_invalid(mixed_language_codes: str | list[str]) -> None:
    from kreuzberg._ocr._easyocr import EASYOCR_SUPPORTED_LANGUAGE_CODES

    with pytest.raises(ValidationError) as excinfo:
        EasyOCRBackend._validate_language_code(mixed_language_codes)

    assert "language_code" in excinfo.value.context
    assert "not supported by EasyOCR" in str(excinfo.value)

    if isinstance(mixed_language_codes, str):
        invalid_codes = [
            lang.strip()
            for lang in mixed_language_codes.split(",")
            if lang.strip().lower() not in EASYOCR_SUPPORTED_LANGUAGE_CODES
        ]
    else:
        invalid_codes = [lang for lang in mixed_language_codes if lang.lower() not in EASYOCR_SUPPORTED_LANGUAGE_CODES]

    reported_invalid = excinfo.value.context["language_code"].split(",")
    assert len(reported_invalid) == len(invalid_codes)
    for invalid in invalid_codes:
        assert invalid.lower() in [r.lower() for r in reported_invalid]


@pytest.mark.anyio
async def test_init_easyocr_with_invalid_language(backend: EasyOCRBackend) -> None:
    with pytest.raises(ValidationError, match="not supported by EasyOCR"):
        await backend._init_easyocr(language="invalid")


def test_is_gpu_available() -> None:
    mock_torch = Mock()
    mock_torch.cuda.is_available.return_value = True

    with patch.object(EasyOCRBackend, "_is_gpu_available", return_value=True):
        assert EasyOCRBackend._is_gpu_available() is True

    with patch.object(EasyOCRBackend, "_is_gpu_available", return_value=False):
        assert EasyOCRBackend._is_gpu_available() is False


@pytest.mark.anyio
async def test_init_easyocr_missing_dependency() -> None:
    with patch(
        "builtins.__import__", side_effect=lambda name, *args, **kwargs: raise_import_error(name, *args, **kwargs)
    ):
        backend = EasyOCRBackend()
        with pytest.raises(MissingDependencyError) as excinfo:
            await backend._init_easyocr(language="en")

        error_message = str(excinfo.value)
        assert "easyocr" in error_message
        assert "required" in error_message
        assert "kreuzberg" in error_message


@pytest.mark.anyio
async def test_init_easyocr(mock_easyocr_reader: Mock) -> None:
    mock_easyocr = Mock()
    mock_reader_class = Mock(return_value=mock_easyocr_reader)
    mock_easyocr.Reader = mock_reader_class

    with (
        patch.dict("sys.modules", {"easyocr": mock_easyocr}),
        patch("kreuzberg._ocr._easyocr.run_sync", return_value=mock_easyocr_reader) as run_sync_mock,
    ):
        backend = EasyOCRBackend()
        await backend._init_easyocr(language="en")

        run_sync_mock.assert_called_once()
        assert run_sync_mock.call_args[0][0] == mock_easyocr.Reader
        assert run_sync_mock.call_args[0][1] == ["en"]
        assert "verbose" in run_sync_mock.call_args[1]
        assert run_sync_mock.call_args[1]["verbose"] is False


@pytest.mark.anyio
async def test_init_easyocr_comma_separated_languages(mock_easyocr_reader: Mock) -> None:
    mock_easyocr = Mock()
    mock_reader_class = Mock(return_value=mock_easyocr_reader)
    mock_easyocr.Reader = mock_reader_class

    with (
        patch.dict("sys.modules", {"easyocr": mock_easyocr}),
        patch("kreuzberg._ocr._easyocr.run_sync", return_value=mock_easyocr_reader) as run_sync_mock,
    ):
        EasyOCRBackend._reader = None
        backend = EasyOCRBackend()

        await backend._init_easyocr(language="en,ch_sim")
        assert run_sync_mock.call_args[0][1] == ["en", "ch_sim"]


@pytest.mark.anyio
async def test_init_easyocr_language_list(mock_easyocr_reader: Mock) -> None:
    mock_easyocr = Mock()
    mock_reader_class = Mock(return_value=mock_easyocr_reader)
    mock_easyocr.Reader = mock_reader_class

    with (
        patch.dict("sys.modules", {"easyocr": mock_easyocr}),
        patch("kreuzberg._ocr._easyocr.run_sync", return_value=mock_easyocr_reader) as run_sync_mock,
    ):
        EasyOCRBackend._reader = None
        backend = EasyOCRBackend()

        await backend._init_easyocr(language=["en", "ch_sim"])
        assert run_sync_mock.call_args[0][1] == ["en", "ch_sim"]


@pytest.mark.anyio
async def test_init_easyocr_error(mocker: MockerFixture) -> None:
    error_message = "Failed to initialize"
    mocker.patch("kreuzberg._ocr._easyocr.run_sync", side_effect=Exception(error_message))

    backend = EasyOCRBackend()
    with pytest.raises(OCRError, match=f"Failed to initialize EasyOCR: {error_message}"):
        await backend._init_easyocr()


@pytest.mark.anyio
async def test_process_image(backend: EasyOCRBackend, mock_easyocr_reader: Mock, config_dict: dict[str, Any]) -> None:
    image = Image.new("RGB", (100, 100))

    with patch.object(backend, "_init_easyocr", return_value=None):
        backend._reader = mock_easyocr_reader  # type: ignore[misc]

        with patch("kreuzberg._ocr._easyocr.run_sync", return_value=mock_easyocr_reader.readtext.return_value):
            result = await backend.process_image(image, **config_dict)

            assert isinstance(result, ExtractionResult)
            assert "Sample OCR text" in result.content
            assert result.mime_type == "text/plain"
            assert isinstance(result.metadata, dict)
            assert result.metadata["width"] == 100
            assert result.metadata["height"] == 100


@pytest.mark.anyio
async def test_process_image_error(backend: EasyOCRBackend, config_dict: dict[str, Any]) -> None:
    image = Image.new("RGB", (100, 100))

    with patch.object(backend, "_init_easyocr", return_value=None):
        backend._reader = Mock()  # type: ignore[misc]

        error_message = "OCR processing failed"
        with patch("kreuzberg._ocr._easyocr.run_sync", side_effect=Exception(error_message)):
            with pytest.raises(OCRError) as excinfo:
                await backend.process_image(image, **config_dict)

            assert "Failed to OCR using EasyOCR" in str(excinfo.value)


@pytest.mark.anyio
async def test_process_file(backend: EasyOCRBackend, tmp_path: Path) -> None:
    test_image = Image.new("RGB", (100, 100))
    image_path = tmp_path / "test_image.png"
    test_image.save(image_path)

    expected_result = ExtractionResult(
        content="Sample OCR text", mime_type="text/plain", metadata={"width": 100, "height": 100}, chunks=[]
    )

    with (
        patch.object(backend, "process_image", return_value=expected_result),
        patch.object(backend, "_init_easyocr", return_value=None),
    ):
        result = await backend.process_file(image_path, language="en")

        assert result == expected_result
        backend.process_image.assert_called_once()  # type: ignore[attr-defined]


@pytest.mark.anyio
async def test_process_file_error(backend: EasyOCRBackend, tmp_path: Path) -> None:
    test_image = Image.new("RGB", (100, 100))
    image_path = tmp_path / "test_image.png"
    test_image.save(image_path)

    with patch.object(backend, "_init_easyocr", return_value=None):
        error_message = "Failed to load image"
        with patch.object(backend, "process_image", side_effect=Exception(error_message)):
            with pytest.raises(OCRError) as excinfo:
                await backend.process_file(image_path, language="en")

            assert "Failed to load or process image using EasyOCR" in str(excinfo.value)


@pytest.mark.anyio
async def test_process_easyocr_result_empty(backend: EasyOCRBackend) -> None:
    image = Image.new("RGB", (100, 100))
    result = backend._process_easyocr_result([], image)

    assert result.content == ""
    assert result.mime_type == "text/plain"
    assert result.metadata["width"] == 100
    assert result.metadata["height"] == 100


@pytest.mark.anyio
async def test_process_easyocr_result_simple_format(backend: EasyOCRBackend) -> None:
    image = Image.new("RGB", (100, 100))
    easyocr_result = [
        ("Line 1", 0.95),
        ("Line 2", 0.90),
    ]

    result = backend._process_easyocr_result(easyocr_result, image)

    assert "Line 1" in result.content
    assert "Line 2" in result.content
    assert result.mime_type == "text/plain"
    assert result.metadata["width"] == 100
    assert result.metadata["height"] == 100


@pytest.mark.anyio
async def test_process_easyocr_result_full_format(backend: EasyOCRBackend) -> None:
    image = Image.new("RGB", (100, 100))
    easyocr_result = [
        (
            [[0, 0], [100, 0], [100, 20], [0, 20]],
            "Line 1",
            0.95,
        ),
        (
            [[0, 30], [100, 30], [100, 50], [0, 50]],
            "Line 2",
            0.90,
        ),
    ]

    result = backend._process_easyocr_result(easyocr_result, image)

    assert "Line 1" in result.content
    assert "Line 2" in result.content
    assert result.mime_type == "text/plain"
    assert result.metadata["width"] == 100
    assert result.metadata["height"] == 100


def test_is_gpu_available_with_torch() -> None:
    mock_torch = Mock()
    mock_torch.cuda.is_available.return_value = True

    with patch.dict("sys.modules", {"torch": mock_torch}):
        result = EasyOCRBackend._is_gpu_available()
        assert result is True
        mock_torch.cuda.is_available.assert_called_once()


def test_is_gpu_available_without_torch() -> None:
    with patch("builtins.__import__", side_effect=ImportError("No module named 'torch'")):
        result = EasyOCRBackend._is_gpu_available()
        assert result is False


def test_resolve_device_config_deprecated_use_gpu_true() -> None:
    with pytest.warns(DeprecationWarning, match="The 'use_gpu' parameter is deprecated"):
        device_info = EasyOCRBackend._resolve_device_config(use_gpu=True, device="auto")

        assert device_info.device_type in ["cpu", "cuda", "mps"]


def test_resolve_device_config_deprecated_use_gpu_conflicts() -> None:
    with pytest.warns(DeprecationWarning, match="Both 'use_gpu' and 'device' parameters specified"):
        device_info = EasyOCRBackend._resolve_device_config(use_gpu=True, device="cpu")

        assert device_info.device_type == "cpu"


def test_resolve_device_config_validation_error_fallback() -> None:
    with patch(
        "kreuzberg._utils._device.validate_device_request", side_effect=ValidationError("Device validation failed")
    ):
        device_info = EasyOCRBackend._resolve_device_config(use_gpu=False, device="cpu")
        assert device_info.device_type == "cpu"
        assert device_info.name == "CPU"


def test_resolve_device_config_validation_error_reraise_other_cases() -> None:
    with pytest.raises(ValidationError, match="Requested device.*not available"):
        EasyOCRBackend._resolve_device_config(use_gpu=True, device="cuda", fallback_to_cpu=False)


def test_resolve_device_config_validation_error_reraise() -> None:
    with pytest.raises(ValidationError, match="Requested device 'invalid' is not available"):
        EasyOCRBackend._resolve_device_config(use_gpu=True, device="invalid", fallback_to_cpu=False)


def test_process_results_edge_cases() -> None:
    mock_results = [
        ([[10, 10], [50, 10], [50, 30], [10, 30]], "Hello", 0.9),
        ([[60, 12], [100, 12], [100, 32], [60, 32]], "World", 0.8),
        ([[10, 50], [80, 50], [80, 70], [10, 70]], "", 0.7),
    ]

    test_image = Image.new("RGB", (100, 100), color="white")

    result = EasyOCRBackend._process_easyocr_result(mock_results, test_image)

    assert "Hello World" in result.content


@pytest.mark.anyio
async def test_init_easyocr_already_initialized() -> None:
    original_reader = EasyOCRBackend._reader
    EasyOCRBackend._reader = Mock()

    try:
        await EasyOCRBackend._init_easyocr(language="en")

        assert EasyOCRBackend._reader is not None
        assert isinstance(EasyOCRBackend._reader, Mock)
    finally:
        EasyOCRBackend._reader = original_reader


def test_process_image_sync(backend: EasyOCRBackend) -> None:
    from unittest.mock import Mock, patch

    image = Image.new("RGB", (100, 100))

    mock_reader = Mock()
    mock_reader.readtext.return_value = [("Sample OCR text", 0.95)]

    with patch.object(backend, "_init_easyocr_sync"), patch.object(backend, "_reader", mock_reader):
        result = backend.process_image_sync(image, beam_width=5, language="en")

        assert isinstance(result, ExtractionResult)
        assert result.content.strip() == "Sample OCR text"
        assert result.metadata["width"] == 100
        assert result.metadata["height"] == 100


def test_process_file_sync(backend: EasyOCRBackend, tmp_path: Path) -> None:
    from unittest.mock import Mock, patch

    test_image = Image.new("RGB", (100, 100))
    image_path = tmp_path / "test_image.png"
    test_image.save(image_path)

    mock_reader = Mock()
    mock_reader.readtext.return_value = [("Sample file text", 0.90)]

    with patch.object(backend, "_init_easyocr_sync"), patch.object(backend, "_reader", mock_reader):
        result = backend.process_file_sync(image_path, beam_width=5, language="en")

        assert isinstance(result, ExtractionResult)
        assert result.content.strip() == "Sample file text"
