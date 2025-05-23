import os
import shutil
import zipfile

import pytest
import vcr
from datasets import Dataset

os.environ["TELEMETRY_ENABLED"] = "false"
mode = os.environ.get("VCR_MODE", None)
_KEY_MAP = {
    "openai": "OPENAI_API_KEY",
    "litellm": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "deepinfra": "DEEPINFRA_API_KEY",
    "vllm": "VLLM_API_KEY",
    "gemini": "GEMINI_API_KEY",
}


@pytest.fixture
def temp_working_dir(request):
    backend = request.param["integration"]
    cached_working_dir = request.param.get("cached_working_dir", False)
    if mode is None:
        os.environ[_KEY_MAP[backend.split("/")[-1]]] = "sk-mocked-**"
        backend = backend.split("/")[0]
    os.environ["HF_DATASETS_CACHE"] = "/dev/null"
    temp_working_dir = f"tests/integrations/{backend}/fixtures/.test_cache"

    if cached_working_dir:
        working_dir_zip = f"tests/integrations/{backend}/fixtures/.test_cache.zip"
        with zipfile.ZipFile(working_dir_zip, "r") as zip_ref:
            zip_ref.extractall(os.path.split(temp_working_dir)[0])

    vcr_path = request.param.get("vcr_path", None)
    if not vcr_path:
        vcr_path = f"tests/integrations/{backend}/fixtures"

    vcr_config = vcr.VCR(
        serializer="yaml",
        cassette_library_dir=vcr_path,
        record_mode=mode,
    )
    os.makedirs(temp_working_dir, exist_ok=True)

    try:
        yield temp_working_dir, backend, vcr_config
    finally:
        shutil.rmtree(temp_working_dir)


@pytest.fixture
def mock_dataset():
    dataset = Dataset.from_parquet("tests/integrations/common_fixtures/dataset.parquet")
    try:
        yield dataset
    finally:
        # TODO: cleanup?
        pass


@pytest.fixture
def mock_reasoning_dataset():
    dataset = Dataset.from_parquet("tests/integrations/common_fixtures/reasoning_dataset.parquet")
    yield dataset


@pytest.fixture
def camel_gt_dataset():
    dataset = Dataset.from_parquet("tests/integrations/common_fixtures/camel_gt_dataset.parquet")
    yield dataset
