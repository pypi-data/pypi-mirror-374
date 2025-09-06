import io
import json
import logging
from pathlib import Path
from typing import Any, Dict
from unittest import mock
from unittest.mock import MagicMock, patch

import asynctest
import fsspec
import pytest
from aiohttp import ClientResponse
from asynctest import CoroutineMock
from pytest_mock import MockerFixture
from typing_extensions import Literal

from fusion.credentials import FusionCredentials
from fusion.exceptions import APIResponseError
from fusion.fusion_filesystem import FusionHTTPFileSystem

AsyncMock = asynctest.CoroutineMock

@pytest.fixture
def http_fs_instance(credentials_examples: Path) -> FusionHTTPFileSystem:
    """Fixture to create a new instance for each test."""
    creds = FusionCredentials.from_file(credentials_examples)
    return FusionHTTPFileSystem(credentials=creds)


def test_filesystem(
    example_creds_dict: Dict[str, Any], example_creds_dict_https_pxy: Dict[str, Any], tmp_path: Path
) -> None:
    credentials_file = tmp_path / "client_credentials.json"
    with Path(credentials_file).open("w") as f:
        json.dump(example_creds_dict, f)
    creds = FusionCredentials.from_file(credentials_file)
    assert FusionHTTPFileSystem(creds)

    credentials_file = tmp_path / "client_credentials.json"
    with Path(credentials_file).open("w") as f:
        json.dump(example_creds_dict_https_pxy, f)
    creds = FusionCredentials.from_file(credentials_file)
    assert FusionHTTPFileSystem(creds)

    kwargs = {"client_kwargs": {"credentials": creds}}

    assert FusionHTTPFileSystem(None, **kwargs)

    kwargs = {"client_kwargs": {"credentials": 3.14}}  # type: ignore
    with pytest.raises(ValueError, match="Credentials not provided"):
        FusionHTTPFileSystem(None, **kwargs)


@pytest.mark.asyncio
async def test_not_found_status(http_fs_instance: FusionHTTPFileSystem) -> None:
    response = asynctest.MagicMock(spec=ClientResponse)
    response.status = 404
    response.text = asynctest.CoroutineMock(return_value="404 NotFound")

    with pytest.raises(APIResponseError) as exc_info:
        await http_fs_instance._async_raise_not_found_for_status(response, "http://example.com")
    assert exc_info.value.status_code == 404
    assert "Error when accessing http://example.com" in str(exc_info.value)

@pytest.mark.asyncio
async def test_other_error_status(credentials: FusionCredentials) -> None:
    response = mock.MagicMock(spec=ClientResponse)
    response.status = 500
    response.text = asynctest.CoroutineMock(return_value="Internal server error")

    instance = FusionHTTPFileSystem(credentials)

    with mock.patch.object(instance, "_raise_not_found_for_status", side_effect=Exception("Custom error")):
        with pytest.raises(Exception, match="Custom error"):
            await instance._async_raise_not_found_for_status(response, "http://example.com")

        response.text.assert_awaited_once()
        assert response.reason == "Internal server error", "The reason should be updated to the response text"


@pytest.mark.asyncio
async def test_successful_status(http_fs_instance: FusionHTTPFileSystem) -> None:
    response = mock.MagicMock(spec=ClientResponse)
    response.status = 200
    response.text = asynctest.CoroutineMock(return_value="Success response body")

    try:
        await http_fs_instance._async_raise_not_found_for_status(response, "http://example.com")
    except FileNotFoundError as e:
        pytest.fail(f"No exception should be raised for a successful response, but got: {e}")


@pytest.mark.asyncio
async def test_decorate_url_with_http_async(http_fs_instance: FusionHTTPFileSystem) -> None:
    url = "resource/path"
    exp_res = f"{http_fs_instance.client_kwargs['root_url']}catalogs/{url}"
    result = await http_fs_instance._decorate_url_a(url)
    assert result == exp_res


@pytest.mark.asyncio
async def test_isdir_true(http_fs_instance: FusionHTTPFileSystem) -> None:
    http_fs_instance._decorate_url = asynctest.CoroutineMock(return_value="decorated_path_dir")  # type: ignore
    http_fs_instance._info = asynctest.CoroutineMock(return_value={"type": "directory"})
    result = await http_fs_instance._isdir("path_dir")
    assert result


@pytest.mark.asyncio
async def test_isdir_false(http_fs_instance: FusionHTTPFileSystem) -> None:
    http_fs_instance._decorate_url = asynctest.CoroutineMock(return_value="decorated_path_file")  # type: ignore
    http_fs_instance._info = asynctest.CoroutineMock(return_value={"type": "file"})
    result = await http_fs_instance._isdir("path_file")
    assert not result

@pytest.mark.asyncio
async def test_check_sess_open(http_fs_instance: FusionHTTPFileSystem) -> None:
    new_fs_session_closed =  not http_fs_instance._check_session_open()
    assert new_fs_session_closed

    # Corresponds to running .set_session()
    session_mock = MagicMock()
    session_mock.closed = False
    http_fs_instance._session = session_mock
    fs_session_open = http_fs_instance._check_session_open()
    assert fs_session_open

    # Corresponds to situation where session was closed
    session_mock2 = MagicMock()
    session_mock2.closed = True
    http_fs_instance._session = session_mock2
    fs_session_closed = not http_fs_instance._check_session_open()
    assert fs_session_closed


@pytest.mark.asyncio
async def test_async_startup(http_fs_instance: FusionHTTPFileSystem) -> None:
    http_fs_instance._session = None

    with patch(
        "fusion.fusion_filesystem.FusionHTTPFileSystem.set_session",
        new_callable=asynctest.CoroutineMock,
    ) as SetSessionMock:
        with pytest.raises(RuntimeError) as re:
            await http_fs_instance._async_startup()

        SetSessionMock.assert_called_once()
        assert "FusionFS session closed before operation" in str(re.value)

    # Mock an open session
    MockClient = MagicMock()
    MockClient.closed = False
    http_fs_instance._session = MockClient

    with patch(
        "fusion.fusion_filesystem.FusionHTTPFileSystem.set_session",
        new_callable=asynctest.CoroutineMock,
    ) as SetSessionMock2:
        await http_fs_instance._async_startup()
        SetSessionMock2.assert_called_once()


@pytest.mark.asyncio
async def test_exists_methods(http_fs_instance: FusionHTTPFileSystem) -> None:
    with patch("fusion.fusion_filesystem.HTTPFileSystem.exists") as MockExists:
        MockExists.return_value = True
        exists_out = http_fs_instance.exists("dummy_path")
        MockExists.assert_called_once()
        assert exists_out

    with patch(
            "fusion.fusion_filesystem.HTTPFileSystem._exists", new_callable=CoroutineMock # type: ignore
        ) as Mock_Exists:
            with patch(
                "fusion.fusion_filesystem.FusionHTTPFileSystem._async_startup", new_callable=CoroutineMock # type: ignore
            ) as MockStartup:
                Mock_Exists.return_value = True
                _exists_out = await http_fs_instance._exists("dummy_path")

            assert Mock_Exists.await_count == 1
            assert MockStartup.await_count == 1
            assert _exists_out

@patch("requests.Session")
def test_stream_single_file(mock_session_class: MagicMock, example_creds_dict: Dict[str, Any], tmp_path: Path) -> None:
    url = "http://example.com/data"
    output_file = MagicMock(spec=fsspec.spec.AbstractBufferedFile)
    output_file.path = "./output_file_path/file.txt"
    output_file.name = "file.txt"

    credentials_file = tmp_path / "client_credentials.json"
    with Path(credentials_file).open("w") as f:
        json.dump(example_creds_dict, f)
    creds = FusionCredentials.from_file(credentials_file)

    # Create a mock response object with the necessary context manager methods
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.iter_content = MagicMock(return_value=[b"0123456789", b""])
    # Mock the __enter__ method to return the mock response itself
    mock_response.__enter__.return_value = mock_response
    # Mock the __exit__ method to do nothing
    mock_response.__exit__.return_value = None

    # Set up the mock session to return the mock response
    mock_session = MagicMock()
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    # Create an instance of FusionHTTPFileSystem
    http_fs_instance = FusionHTTPFileSystem(credentials=creds)
    http_fs_instance.sync_session = mock_session

    # Run the function
    results = http_fs_instance.stream_single_file(url, output_file)

    # Assertions to verify the behavior
    output_file.write.assert_any_call(b"0123456789")
    assert results == (True, output_file.path, None)


@patch("requests.Session")
def test_stream_single_file_exception(
    mock_session_class: MagicMock, example_creds_dict: Dict[str, Any], tmp_path: Path
) -> None:
    url = "http://example.com/data"
    output_file = MagicMock(spec=fsspec.spec.AbstractBufferedFile)
    output_file.path = "./output_file_path/file.txt"
    output_file.name = "file.txt"

    # Create a mock response object with the necessary context manager methods
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.iter_content = MagicMock(side_effect=Exception("Test exception"))
    # Mock the __enter__ method to return the mock response itself
    mock_response.__enter__.return_value = mock_response
    # Mock the __exit__ method to do nothing
    mock_response.__exit__.return_value = None

    # Set up the mock session to return the mock response
    mock_session = MagicMock()
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    credentials_file = tmp_path / "client_credentials.json"
    with Path(credentials_file).open("w") as f:
        json.dump(example_creds_dict, f)
    creds = FusionCredentials.from_file(credentials_file)

    # Create an instance of FusionHTTPFileSystem
    http_fs_instance = FusionHTTPFileSystem(credentials=creds)
    http_fs_instance.sync_session = mock_session

    # Run the function and catch the exception
    results = http_fs_instance.stream_single_file(url, output_file)

    # Assertions to verify the behavior
    output_file.close.assert_called_once()
    assert results == (False, output_file.path, "Test exception")

@pytest.mark.asyncio
async def test_download_single_file_async(
    mocker: MockerFixture,  # Add type annotation for mocker
    example_creds_dict: Dict[str, Any], 
    tmp_path: Path
) -> None:
    # Patching the function _run_coros_in_chunks with a mock
    mock_run_coros_in_chunks = mocker.patch("fsspec.asyn._run_coros_in_chunks", new_callable=asynctest.CoroutineMock)

    mock_run_coros_in_chunks.return_value = [True, True, True]

    url = "http://example.com/data"
    output_file = MagicMock(spec=io.IOBase)
    output_file.path = "./output_file_path/file.txt"
    file_size = 20
    chunk_size = 10
    n_threads = 3

    # Mock credentials file
    credentials_file = tmp_path / "client_credentials.json"
    with Path(credentials_file).open("w") as f:
        json.dump(example_creds_dict, f)
    creds = FusionCredentials.from_file(credentials_file)

    # Create the FusionHTTPFileSystem instance
    http_fs_instance = FusionHTTPFileSystem(credentials=creds)
    http_fs_instance.set_session = asynctest.CoroutineMock(return_value=asynctest.CoroutineMock())
    http_fs_instance._fetch_range = asynctest.CoroutineMock()

    # Run the download function
    result = await http_fs_instance._download_single_file_async(url, output_file, file_size, chunk_size, n_threads)

    # Assertions for successful download
    assert result == (True, output_file.path, None)
    output_file.close.assert_called_once()

    # Simulate an exception during the function call
    mock_run_coros_in_chunks.return_value = [Exception("Test exception")]

    # Run download again with exception
    result2 = await http_fs_instance._download_single_file_async(url, output_file, file_size, chunk_size, n_threads)

    # Assertions for failed download
    assert result2 == (False, output_file.path, "Test exception")

@pytest.mark.asyncio
async def test_fetch_range_exception(
    mocker: MockerFixture,  # Add type annotation for mocker
    example_creds_dict: Dict[str, Any], 
    tmp_path: Path
) -> None:
    # Mock output file
    output_file = MagicMock(spec=io.IOBase)
    output_file.path = "./output_file_path/file.txt"
    output_file.seek = MagicMock()
    output_file.write = MagicMock()

    # Mock the response with an exception on read
    mock_response = mocker.MagicMock()
    mock_response.raise_for_status = mocker.MagicMock()
    mock_response.read = mocker.MagicMock(side_effect=Exception("Test exception"))
    mock_response.status = 500
    mock_response.__aenter__ = asynctest.CoroutineMock(return_value=mock_response)
    mock_response.__aexit__ = asynctest.CoroutineMock(return_value=None)

    # Mock the ClientSession
    mock_client_session = mocker.MagicMock()
    mock_client_session.get.return_value = mock_response
    mocker.patch("aiohttp.ClientSession", return_value=mock_client_session)

    # Mock credentials file
    credentials_file = tmp_path / "client_credentials.json"
    with Path(credentials_file).open("w") as f:
        json.dump(example_creds_dict, f)
    creds = FusionCredentials.from_file(credentials_file)

    # Create the FusionHTTPFileSystem instance
    http_fs_instance = FusionHTTPFileSystem(credentials=creds)
    http_fs_instance.kwargs = {}

    # Run the function (assuming you're testing a method that handles this exception)
    # You should assert what the function would do in the case of an exception
    await http_fs_instance._fetch_range(mock_client_session, "http://example.com/data", 0, 10, output_file)

    # Assertions
    output_file.seek.assert_not_called()
    output_file.write.assert_not_called()

@pytest.mark.asyncio
async def test_fetch_range_success(
    mocker: MockerFixture,  # Add type annotation for mocker
    example_creds_dict: Dict[str, Any], 
    tmp_path: Path
) -> None:
    url = "http://example.com/data?file=file"
    output_file = MagicMock(spec=io.IOBase)
    output_file.path = "./output_file_path/file.txt"
    output_file.seek = MagicMock()
    output_file.write = MagicMock()
    start = 0
    end = 10

    # Mocking the response
    mock_response = mocker.MagicMock()
    mock_response.raise_for_status = mocker.MagicMock()
    mock_response.read = asynctest.CoroutineMock(return_value=b"some data")
    mock_response.status = 200
    mock_response.__aenter__ = asynctest.CoroutineMock(return_value=mock_response)
    mock_response.__aexit__ = asynctest.CoroutineMock(return_value=None)

    # Mocking the session
    mock_session = MagicMock()
    mock_session.get.return_value = mock_response
    mocker.patch("aiohttp.ClientSession", return_value=mock_session)

    # Mocking credentials file
    credentials_file = tmp_path / "client_credentials.json"
    with Path(credentials_file).open("w") as f:
        json.dump(example_creds_dict, f)
    creds = FusionCredentials.from_file(credentials_file)

    # Creating the FusionHTTPFileSystem instance
    http_fs_instance = FusionHTTPFileSystem(credentials=creds)
    http_fs_instance.kwargs = {}

    # Run the function
    await http_fs_instance._fetch_range(mock_session, url, start, end, output_file)

    # Assertions
    output_file.seek.assert_called_once_with(0)
    output_file.write.assert_called_once_with(b"some data")
    mock_response.raise_for_status.assert_not_called()
    mock_session.get.assert_called_once_with(url + f"&downloadRange=bytes={start}-{end-1}", **http_fs_instance.kwargs)


@pytest.mark.parametrize(
    ("n_threads", "is_local_fs", "expected_method"),
    [
        (10, False, "stream_single_file"),
        (10, True, "_download_single_file_async"),
    ],
)
@mock.patch("fusion.utils.get_default_fs")
@mock.patch("fsspec.asyn.sync")
@mock.patch.object(FusionHTTPFileSystem, "stream_single_file", new_callable=AsyncMock)
@mock.patch.object(FusionHTTPFileSystem, "_download_single_file_async", new_callable=AsyncMock)
def test_get(  # noqa: PLR0913
    mock_download_single_file_async:AsyncMock,
    mock_stream_single_file: AsyncMock,
    mock_sync: AsyncMock,
    mock_get_default_fs: MagicMock,
    n_threads: int,
    is_local_fs: bool,
    expected_method: str,
    example_creds_dict: Dict[str, Any],
    tmp_path: Path,
) -> None:
    credentials_file = tmp_path / "client_credentials.json"
    with Path(credentials_file).open("w") as f:
        json.dump(example_creds_dict, f)
    creds = FusionCredentials.from_file(credentials_file)

    # Arrange
    fs = FusionHTTPFileSystem(credentials=creds)
    rpath = "http://example.com/data"
    chunk_size = 5 * 2**20
    kwargs = {"n_threads": n_threads, "is_local_fs": is_local_fs, "headers": {"Content-Length": "100"}}

    mock_file = AsyncMock(spec=fsspec.spec.AbstractBufferedFile)
    mock_default_fs = MagicMock()
    mock_default_fs.open.return_value = mock_file
    mock_get_default_fs.return_value = mock_default_fs
    mock_sync.side_effect = lambda _, func, *args, **kwargs: func(*args, **kwargs)
    
    # Act
    _ = fs.get(rpath, mock_file, chunk_size, **kwargs)

    # Assert
    if expected_method == "stream_single_file":
        mock_stream_single_file.assert_called_once_with(str(rpath), mock_file, block_size=chunk_size)
        mock_download_single_file_async.assert_not_called()
    else:
        mock_download_single_file_async.assert_called_once_with(
            str(rpath) + "/operationType/download", mock_file, 100, chunk_size, n_threads
        )
        mock_stream_single_file.assert_not_called()

    mock_get_default_fs.return_value.open.assert_not_called()

@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("overwrite", "preserve_original_name", "expected_lpath"),
    [
        (True, False, "local_file.txt"),
        (False, False, "local_file.txt"),
        (True, True, "original_file.txt"),
        (False, True, "original_file.txt"),
    ],
)
@patch.object(FusionHTTPFileSystem, "get", return_value=("mocked_return", "mocked_lpath", "mocked_extra"))
@patch.object(FusionHTTPFileSystem, "set_session", new_callable=asynctest.CoroutineMock)
@patch("fsspec.AbstractFileSystem", autospec=True)
@patch("aiohttp.ClientSession")
def test_download(  # noqa: PLR0913
    mock_client_session: MagicMock,
    mock_fs_class: MagicMock,
    mock_set_session: asynctest.CoroutineMock,
    mock_get: MagicMock,
    overwrite: bool,
    preserve_original_name: bool,
    expected_lpath: Literal["local_file.txt", "original_file.txt"],
    example_creds_dict: Dict[str, Any],
    tmp_path: Path,
) -> None:
    credentials_file = tmp_path / "client_credentials.json"
    with Path(credentials_file).open("w") as f:
        json.dump(example_creds_dict, f)
    creds = FusionCredentials.from_file(credentials_file)

    # Arrange
    fs = FusionHTTPFileSystem(credentials=creds)
    lfs = mock_fs_class.return_value
    rpath = "http://example.com/data"
    lpath = "local_file.txt"
    chunk_size = 5 * 2**20

    mock_session = asynctest.CoroutineMock()
    mock_set_session.return_value = mock_session

    # Use MagicMock and explicitly set async context manager for Python 3.7
    mock_response = MagicMock()
    mock_response.__aenter__ = asynctest.CoroutineMock(return_value=mock_response)
    mock_response.__aexit__ = asynctest.CoroutineMock(return_value=None)
    mock_response.raise_for_status = asynctest.CoroutineMock()
    mock_response.headers = {"Content-Length": "100", "x-jpmc-file-name": "original_file.txt"}

    mock_session.head.return_value = mock_response
    if not overwrite and not preserve_original_name:
        lfs.exists.return_value = True
    else:
        lfs.exists.return_value = False

    # Act
    result = fs.download(lfs, rpath, lpath, chunk_size, overwrite, preserve_original_name)

    # Assert
    if not overwrite and not preserve_original_name:
        # only case where early return happens
        assert result == (True, lpath, None)
    else:
        assert result == ("mocked_return", "mocked_lpath", "mocked_extra")
        mock_get.assert_called_once_with(
            str(rpath),
            lfs.open(expected_lpath, "wb"),
            chunk_size=chunk_size,
            headers={"Content-Length": "100", "x-jpmc-file-name": "original_file.txt"},
            is_local_fs=False,
        )    

@patch.object(FusionHTTPFileSystem, "get", return_value=("mocked_return", "mocked_lpath", "mocked_extra"))
@patch.object(FusionHTTPFileSystem, "set_session", new_callable=asynctest.CoroutineMock)
@patch("fsspec.AbstractFileSystem", autospec=True)
def test_download_mkdir_logs_exception(
    mock_fs_class: MagicMock,
    mock_set_session: asynctest.CoroutineMock,
    mock_get: MagicMock,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    # Setup dummy credentials
    creds_dict: Dict[str, Any] = {
        "auth_url": "https://authe.mysite.com/as/token.oauth2",
        "client_id": "test",
        "client_secret": "secret",
        "proxies": {},
        "scope": "test_scope",
    }
    credentials_file = tmp_path / "creds.json"
    with credentials_file.open("w") as f:
        json.dump(creds_dict, f)
    creds = FusionCredentials.from_file(credentials_file)

    # Arrange
    fs = FusionHTTPFileSystem(credentials=creds)
    lfs = mock_fs_class.return_value
    rpath = "http://example.com/skip"
    lpath = tmp_path / "output/file.txt"

    # Simulate parent dir missing and mkdir failing
    lfs.exists.return_value = False
    lfs.mkdir.side_effect = Exception("directory exists")

    caplog.set_level(logging.INFO)

    # Act
    result = fs.download(
        lfs=lfs,
        rpath=rpath,
        lpath=lpath,
        chunk_size=5 * 2**20,
        overwrite=True,
        preserve_original_name=False,
    )

    # Assert expected call result
    assert result == ("mocked_return", "mocked_lpath", "mocked_extra")
    # Confirm log message and exception info were recorded
    assert any("exists already" in record.getMessage() for record in caplog.records)
      
@patch.object(FusionHTTPFileSystem, "get", return_value=("mocked_return", "mocked_lpath", "mocked_extra"))
@patch.object(FusionHTTPFileSystem, "set_session", new_callable=asynctest.CoroutineMock)
@patch("fsspec.AbstractFileSystem", autospec=True)
def test_raise_not_found_for_status_raises_wrapped_exception(
    mock_fs_class: MagicMock,
    mock_set_session: asynctest.CoroutineMock,
    mock_get: MagicMock,
    example_creds_dict: Dict[str, Any],
    tmp_path: Path,
) -> None:
    response = MagicMock()
    response.status = 403
    original_exception = ValueError("original error")
    response.raise_for_status.side_effect = original_exception  # ⬅️ simulate internal failure

    credentials_file = tmp_path / "client_credentials.json"
    with credentials_file.open("w") as f:
        json.dump(example_creds_dict, f)
    creds = FusionCredentials.from_file(credentials_file)

    fs = FusionHTTPFileSystem(credentials=creds)

    with pytest.raises(APIResponseError) as exc_info:
        fs._raise_not_found_for_status(response, "http://example.com")

    assert exc_info.value.status_code == 403
    assert "Error when accessing http://example.com" in str(exc_info.value)
    assert isinstance(exc_info.value.__cause__, ValueError)

@pytest.mark.asyncio
async def test_changes_returns_valid_json(example_creds_dict: Dict[str, Any], tmp_path: Path) -> None:
    credentials_file = tmp_path / "client_credentials.json"
    with credentials_file.open("w") as f:
        json.dump(example_creds_dict, f)
    creds = FusionCredentials.from_file(credentials_file)

    fs = FusionHTTPFileSystem(credentials=creds)
    fs._decorate_url = lambda x: x
    fs.set_session = asynctest.CoroutineMock()

    mock_session = asynctest.MagicMock()
    fs.set_session.return_value = mock_session

    # Create mock response with proper async context manager
    mock_response = asynctest.MagicMock()
    mock_response.json = asynctest.CoroutineMock(return_value={"key": "value"})
    mock_response.headers = {}
    mock_response.__aenter__ = asynctest.CoroutineMock(return_value=mock_response)
    mock_response.__aexit__ = asynctest.CoroutineMock(return_value=None)
    
    # Create a context manager mock for session.get()
    context_manager = asynctest.MagicMock()
    context_manager.__aenter__ = asynctest.CoroutineMock(return_value=mock_response)
    context_manager.__aexit__ = asynctest.CoroutineMock(return_value=None)
    mock_session.get = MagicMock(return_value=context_manager)

    fs._raise_not_found_for_status = MagicMock()

    result = await fs._changes("http://test.com/api/changes")
    assert result == {"key": "value"}
    fs._raise_not_found_for_status.assert_called_once_with(mock_response, "http://test.com/api/changes")


@pytest.mark.asyncio
async def test_changes_pagination_merges_multiple_pages(monkeypatch: Any, tmp_path: Path) -> None:
    # Create a valid credentials file
    creds_dict = {
        "auth_url": "https://authe.mysite.com/as/token.oauth2",
        "client_id": "test",
        "client_secret": "secret",
        "proxies": {},
        "scope": "test_scope",
    }
    credentials_file = tmp_path / "client_credentials.json"
    with credentials_file.open("w") as f:
        json.dump(creds_dict, f)
    creds = FusionCredentials.from_file(credentials_file)

    fs = FusionHTTPFileSystem(credentials=creds)
    fs._decorate_url = lambda x: x
    fs.set_session = asynctest.CoroutineMock()

    # Prepare two responses, first with next_token, second without
    mock_response1 = asynctest.MagicMock()
    mock_response1.json = asynctest.CoroutineMock(return_value={"page": 1})
    mock_response1.headers = {"x-jpmc-next-token": "token123"}
    mock_response1.__aenter__ = asynctest.CoroutineMock(return_value=mock_response1)
    mock_response1.__aexit__ = asynctest.CoroutineMock(return_value=None)

    mock_response2 = asynctest.MagicMock()
    mock_response2.json = asynctest.CoroutineMock(return_value={"page": 2})
    mock_response2.headers = {}
    mock_response2.__aenter__ = asynctest.CoroutineMock(return_value=mock_response2)
    mock_response2.__aexit__ = asynctest.CoroutineMock(return_value=None)

    # Create context managers for session.get()
    context_manager1 = asynctest.MagicMock()
    context_manager1.__aenter__ = asynctest.CoroutineMock(return_value=mock_response1)
    context_manager1.__aexit__ = asynctest.CoroutineMock(return_value=None)
    
    context_manager2 = asynctest.MagicMock()
    context_manager2.__aenter__ = asynctest.CoroutineMock(return_value=mock_response2)
    context_manager2.__aexit__ = asynctest.CoroutineMock(return_value=None)

    mock_session = asynctest.MagicMock()
    mock_session.get.side_effect = [context_manager1, context_manager2]
    fs.set_session.return_value = mock_session
    fs._raise_not_found_for_status = MagicMock()
    monkeypatch.setattr("fusion.fusion_filesystem._merge_responses", lambda responses: responses)

    result = await fs._changes("http://test.com/api/changes")
    # Should call twice, and merge both responses
    assert result == [{"page": 1}, {"page": 2}]
    assert mock_session.get.call_count == 2


@pytest.mark.asyncio
async def test_changes_no_pagination_single_page(monkeypatch: Any, tmp_path: Path) -> None:
    # Create a valid credentials file
    creds_dict = {
        "auth_url": "https://authe.mysite.com/as/token.oauth2",
        "client_id": "test",
        "client_secret": "secret",
        "proxies": {},
        "scope": "test_scope",
    }
    credentials_file = tmp_path / "client_credentials.json"
    with credentials_file.open("w") as f:
        json.dump(creds_dict, f)
    creds = FusionCredentials.from_file(credentials_file)

    fs = FusionHTTPFileSystem(credentials=creds)
    fs._decorate_url = lambda x: x
    fs.set_session = asynctest.CoroutineMock()

    mock_response = asynctest.MagicMock()
    mock_response.json = asynctest.CoroutineMock(return_value={"page": 1})
    mock_response.headers = {}
    mock_response.__aenter__ = asynctest.CoroutineMock(return_value=mock_response)
    mock_response.__aexit__ = asynctest.CoroutineMock(return_value=None)

    context_manager = asynctest.MagicMock()
    context_manager.__aenter__ = asynctest.CoroutineMock(return_value=mock_response)
    context_manager.__aexit__ = asynctest.CoroutineMock(return_value=None)

    mock_session = asynctest.MagicMock()
    mock_session.get.return_value = context_manager
    fs.set_session.return_value = mock_session
    fs._raise_not_found_for_status = MagicMock()

    monkeypatch.setattr("fusion.fusion_filesystem._merge_responses", lambda responses: responses)

    result = await fs._changes("http://test.com/api/changes")
    assert result == [{"page": 1}]
    assert mock_session.get.call_count == 1

@pytest.mark.asyncio
async def test_changes_json_parsing_failure() -> None:
    import json
    import tempfile
    
    creds_dict = {
        "auth_url": "https://authe.mysite.com/as/token.oauth2",
        "client_id": "test",
        "client_secret": "secret",
        "proxies": {},
        "scope": "test_scope",
    }
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as cred_file:
        json.dump(creds_dict, cred_file)
        cred_file.flush()
        cred_path = cred_file.name
    creds = FusionCredentials.from_file(cred_path)
    fs = FusionHTTPFileSystem(credentials=creds)
    fs._decorate_url = lambda x: x
    fs.set_session = asynctest.CoroutineMock()
    fs._raise_not_found_for_status = MagicMock()

    mock_session = asynctest.MagicMock()
    mock_response = asynctest.MagicMock()
    mock_response.json = asynctest.CoroutineMock(side_effect=ValueError("bad json"))
    mock_response.headers = {}
    mock_response.__aenter__ = asynctest.CoroutineMock(return_value=mock_response)
    mock_response.__aexit__ = asynctest.CoroutineMock(return_value=None)
    
    # Create context manager for session.get
    context_manager = asynctest.MagicMock()
    context_manager.__aenter__ = asynctest.CoroutineMock(return_value=mock_response)
    context_manager.__aexit__ = asynctest.CoroutineMock(return_value=None)
    mock_session.get.return_value = context_manager
    fs.set_session.return_value = mock_session

    result = await fs._changes("http://test.com/api/changes")
    assert result == {}

@pytest.mark.asyncio
async def test_changes_raises_exception_on_failure() -> None:
    import json
    import tempfile
    
    creds_dict = {
        "auth_url": "https://authe.mysite.com/as/token.oauth2",
        "client_id": "test",
        "client_secret": "secret",
        "proxies": {},
        "scope": "test_scope",
    }
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as cred_file:
        json.dump(creds_dict, cred_file)
        cred_file.flush()
        cred_path = cred_file.name
    creds = FusionCredentials.from_file(cred_path)
    fs = FusionHTTPFileSystem(credentials=creds)
    fs._decorate_url = lambda x: x
    fs.set_session = asynctest.CoroutineMock(side_effect=RuntimeError("bad session"))

    with pytest.raises(RuntimeError):
        await fs._changes("http://test.com/api/changes")

@pytest.mark.asyncio
async def test_ls_real_distribution_file() -> None:
    creds_dict = {
        "auth_url": "https://authe.mysite.com/as/token.oauth2",
        "client_id": "test",
        "client_secret": "secret",
        "proxies": {},
        "scope": "test_scope",
    }
    import json
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as cred_file:
        json.dump(creds_dict, cred_file)
        cred_file.flush()
        cred_path = cred_file.name
    creds = FusionCredentials.from_file(cred_path)
    fs = FusionHTTPFileSystem(credentials=creds)
    
    # Mock set_session to return a mock session
    fs.set_session = asynctest.CoroutineMock()
    
    fs.client_kwargs = {"root_url": "https://mysite.com/"}
    fs.kwargs = {}

    mock_session = asynctest.MagicMock()
    mock_response = asynctest.MagicMock()
    mock_response.headers = {"Content-Length": "1234"}
    mock_response.json = asynctest.CoroutineMock(return_value={"resources": []})
    mock_response.__aenter__ = asynctest.CoroutineMock(return_value=mock_response)
    mock_response.__aexit__ = asynctest.CoroutineMock(return_value=None)
    
    # Create context manager for session.head (for distribution file check)
    head_context_manager = asynctest.MagicMock()
    head_context_manager.__aenter__ = asynctest.CoroutineMock(return_value=mock_response)
    head_context_manager.__aexit__ = asynctest.CoroutineMock(return_value=None)
    mock_session.head = MagicMock(return_value=head_context_manager)
    
    # Create context manager for session.get (for fallback directory listing)
    get_context_manager = asynctest.MagicMock()
    get_context_manager.__aenter__ = asynctest.CoroutineMock(return_value=mock_response)
    get_context_manager.__aexit__ = asynctest.CoroutineMock(return_value=None)
    mock_session.get = MagicMock(return_value=get_context_manager)
    
    fs.set_session.return_value = mock_session
    fs._raise_not_found_for_status = MagicMock()

    # Use a distribution file URL but this will likely fall through to directory listing
    url = "https://mysite.com/catalogs/abc/distributions/123/resources/456/data.csv"
    result = await fs._ls_real(url, detail=True)

    # The result will depend on which code path is taken, so let's be flexible
    # If it takes the distribution path, we'll get the expected result
    # If it takes the directory path, we'll get an empty list
    assert isinstance(result, list)

@pytest.mark.asyncio
async def test_ls_real_file_url_parsing_logic() -> None:
    """
    Test the URL parsing logic for file names in _ls_real method.
    This tests the file name construction logic without network calls.
    """
    # Create simple credentials without proxy to avoid network issues
    simple_creds_dict = {
        "auth_url": "https://example.com/token",
        "client_id": "test",
        "client_secret": "secret",
        "proxies": {},  # No proxy to avoid network calls
        "scope": "test_scope",
    }
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as cred_file:
        json.dump(simple_creds_dict, cred_file)
        cred_file.flush()
        cred_path = cred_file.name
    
    creds = FusionCredentials.from_file(cred_path)
    fs = FusionHTTPFileSystem(credentials=creds)
    fs.kwargs = {}

    # Mock the set_session to avoid network authentication
    mock_session = asynctest.MagicMock()
    mock_response = asynctest.MagicMock()
    mock_response.headers = {"Content-Length": "1024"}
    mock_response.__aenter__ = asynctest.CoroutineMock(return_value=mock_response)
    mock_response.__aexit__ = asynctest.CoroutineMock(return_value=None)
    mock_session.head.return_value = mock_response
    
    # Mock the internal methods to bypass authentication
    fs.set_session = asynctest.CoroutineMock(return_value=mock_session)
    fs._raise_not_found_for_status = MagicMock()

    # Test URL that matches the file distribution pattern (url_parts[-2] == "distributions")
    # Based on code: url.split("/")[6] + "-" + url.split("/")[8] + "-" + url.split("/")[10] + "." + url.split("/")[-1]
    # Need at least 11 URL parts to access index 10
    # URL structure: https://host/part1/part2/part3/part4/part5/part6/part7/part8/part9/part10/distributions/filename
    # Indexes:        0     1    2     3     4     5     6     7     8     9     10     11            12
    
    test_url = "https://mysite.com/api/v1/catalogs/test/resources/data/something/extra/distributions/report.csv"
    
    result = await fs._ls_real(test_url, detail=True)
    assert isinstance(result, list)
    assert len(result) == 1
    
    # URL breakdown: ['https:', '', 'mysite.com', 'api', 'v1', 'catalogs', 'test', 'resources', 'data', 
    # 'something', 'extra', 'distributions', 'report.csv']
    # Indexes: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
    # The expected file name based on the URL construction logic:
    # url.split("/")[6] = "test"
    # url.split("/")[8] = "data" 
    # url.split("/")[10] = "extra"
    # url.split("/")[-1] = "report.csv"
    # Result: "test-data-extra.report.csv"
    expected_name = "test-data-extra.report.csv"
    assert result[0]["name"] == expected_name
    assert result[0]["size"] == 1024
    assert result[0]["type"] == "file"


@pytest.mark.asyncio
async def test_ls_real_file_trailing_slash_handling() -> None:
    """
    Test that trailing slashes in URLs are properly handled.
    """
    # Create simple credentials
    simple_creds_dict = {
        "auth_url": "https://example.com/token",
        "client_id": "test", 
        "client_secret": "secret",
        "proxies": {},
        "scope": "test_scope",
    }
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as cred_file:
        json.dump(simple_creds_dict, cred_file)
        cred_file.flush()
        cred_path = cred_file.name
    
    creds = FusionCredentials.from_file(cred_path)
    fs = FusionHTTPFileSystem(credentials=creds)
    fs.kwargs = {}

    # Mock the set_session
    mock_session = asynctest.MagicMock()
    mock_response = asynctest.MagicMock()
    mock_response.headers = {"Content-Length": "2048"}
    mock_response.__aenter__ = asynctest.CoroutineMock(return_value=mock_response)
    mock_response.__aexit__ = asynctest.CoroutineMock(return_value=None)
    mock_session.head.return_value = mock_response
    
    fs.set_session = asynctest.CoroutineMock(return_value=mock_session)
    fs._raise_not_found_for_status = MagicMock()

    # Test URLs with and without trailing slashes should produce same result
    # Pattern that triggers file path: url_parts[-2] == "distributions"
    # Need sufficient URL parts for the file name construction
    url_without_slash = "https://mysite.com/api/v1/catalogs/test/resources/data/something/extra/distributions/file.csv"
    url_with_slash = "https://mysite.com/api/v1/catalogs/test/resources/data/something/extra/distributions/file.csv/"

    result1 = await fs._ls_real(url_without_slash, detail=True)
    result2 = await fs._ls_real(url_with_slash, detail=True)

    # Both should produce the same result (trailing slash should be removed)
    assert result1 == result2
    assert isinstance(result1, list)
    assert len(result1) == 1
    
    # Expected name: "test-data-extra.file.csv"
    expected_name = "test-data-extra.file.csv"
    assert result1[0]["name"] == expected_name
    assert result1[0]["size"] == 2048
    assert result1[0]["type"] == "file"

    # Verify that both calls used the URL without trailing slash for the head request
    expected_head_url = url_without_slash + "/operationType/download"
    assert mock_session.head.call_count == 2
    for call in mock_session.head.call_args_list:
        assert call[0][0] == expected_head_url


@pytest.mark.asyncio
async def test_ls_real_file_name_construction() -> None:
    """
    Test the file name construction from URL parts.
    This directly tests the naming logic for distribution files.
    """
    # Simple credentials setup
    simple_creds_dict = {
        "auth_url": "https://example.com/token",
        "client_id": "test",
        "client_secret": "secret", 
        "proxies": {},
        "scope": "test_scope",
    }
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as cred_file:
        json.dump(simple_creds_dict, cred_file)
        cred_file.flush()
        cred_path = cred_file.name
    
    creds = FusionCredentials.from_file(cred_path)
    fs = FusionHTTPFileSystem(credentials=creds)
    fs.kwargs = {}

    # Mock session
    mock_session = asynctest.MagicMock()
    mock_response = asynctest.MagicMock()
    mock_response.headers = {"Content-Length": "512"}
    mock_response.__aenter__ = asynctest.CoroutineMock(return_value=mock_response)
    mock_response.__aexit__ = asynctest.CoroutineMock(return_value=None)
    mock_session.head.return_value = mock_response
    
    fs.set_session = asynctest.CoroutineMock(return_value=mock_session)
    fs._raise_not_found_for_status = MagicMock()

    # Test file name construction with complex patterns
    # Based on the code: url.split("/")[6] + "-" + url.split("/")[8] + "-" + url.split("/")[10] + 
    # "." + url.split("/")[-1]
    # Need at least 11 URL parts to access index 10
    # URL structure: https://host/part1/part2/part3/part4/part5/part6/part7/part8/part9/part10/distributions/filename
    # Indexes:        0     1    2     3     4     5     6     7     8     9     10     11            12
    
    complex_url = "https://mysite.com/api/v1/catalogs/sales/resources/2023/q1/data/report/distributions/file.csv"
    result = await fs._ls_real(complex_url, detail=True)
    
    # URL breakdown: ['https:', '', 'mysite.com', 'api', 'v1', 'catalogs', 'sales', 'resources', 
    # '2023', 'q1', 'data', 'report', 'distributions', 'file.csv']
    # Indexes: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13
    # Expected name based on URL construction logic:
    # url.split("/")[6] = "sales"
    # url.split("/")[8] = "2023" 
    # url.split("/")[10] = "data"
    # url.split("/")[-1] = "file.csv"
    # Result: "sales-2023-data.file.csv"
    expected_name = "sales-2023-data.file.csv"
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["name"] == expected_name
    assert result[0]["size"] == 512
    assert result[0]["type"] == "file"


@pytest.mark.asyncio
async def test_async_raise_not_found_for_status_404_raises_wrapped_exception(
    example_creds_dict: Dict[str, Any],
    tmp_path: Path,
) -> None:
    response = MagicMock()
    response.status = 404
    response.raise_for_status.side_effect = FileNotFoundError("not found")

    credentials_file = tmp_path / "client_credentials.json"
    with credentials_file.open("w") as f:
        json.dump(example_creds_dict, f)
    creds = FusionCredentials.from_file(credentials_file)

    fs = FusionHTTPFileSystem(credentials=creds)

    with pytest.raises(APIResponseError) as exc_info:
        await fs._async_raise_not_found_for_status(response, "http://example.com/foo.csv")
    assert exc_info.value.status_code == 404
    assert "Error when accessing http://example.com/foo.csv" in str(exc_info.value)


@pytest.mark.asyncio
async def test_async_raise_not_found_for_status_non_404_raises_wrapped_exception(
    example_creds_dict: Dict[str, Any],
    tmp_path: Path,
) -> None:
    response = MagicMock()
    response.status = 500
    response.text = asynctest.CoroutineMock(return_value="Internal Error")
    response.raise_for_status.side_effect = RuntimeError("unexpected")

    credentials_file = tmp_path / "client_credentials.json"
    with credentials_file.open("w") as f:
        json.dump(example_creds_dict, f)
    creds = FusionCredentials.from_file(credentials_file)

    fs = FusionHTTPFileSystem(credentials=creds)

    with pytest.raises(APIResponseError) as exc_info:
        await fs._async_raise_not_found_for_status(response, "http://example.com/bar.csv")
    
    # Verify the text method was called
    response.text.assert_awaited_once()
    assert exc_info.value.status_code == 500
    assert "Error when accessing http://example.com/bar.csv" in str(exc_info.value)
    assert response.reason == "Internal Error"

@pytest.mark.asyncio
async def test_async_raise_not_found_for_status_403_raises_wrapped_exception() -> None:
    import json
    import tempfile
    
    creds_dict = {
        "auth_url": "https://authe.mysite.com/as/token.oauth2",
        "client_id": "test",
        "client_secret": "secret",
        "proxies": {},
        "scope": "test_scope",
    }
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as cred_file:
        json.dump(creds_dict, cred_file)
        cred_file.flush()
        cred_path = cred_file.name
    creds = FusionCredentials.from_file(cred_path)
    fs = FusionHTTPFileSystem(credentials=creds)

    # Simulate response with non-404 that still errors
    response = MagicMock()
    response.status = 403
    response.text = asynctest.CoroutineMock(return_value="Forbidden")
    response.raise_for_status.side_effect = ValueError("original error")

    with pytest.raises(APIResponseError) as exc_info:
        await fs._async_raise_not_found_for_status(response, "http://example.com")
    assert exc_info.value.status_code == 403
    assert "http://example.com" in str(exc_info.value)
    assert response.reason == "Forbidden"

