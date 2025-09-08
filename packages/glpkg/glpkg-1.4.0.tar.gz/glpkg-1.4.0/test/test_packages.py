import urllib
from gitlab.packages import *
from unittest.mock import mock_open, patch

from utils import (
    ResponseMock,
    test_gitlab,
    mock_empty_response,
    mock_one_response,
    mock_five_response,
    mock_paginate_1,
    mock_paginate_2,
)


class TestPackages:

    def test_api_url(self, test_gitlab):
        url = "https://gl-host/api/v4/"
        assert url == test_gitlab._url()

    def test_project_path(self, test_gitlab):
        url = "projects/24"
        assert url == test_gitlab._build_path("projects", "24")

    def test_build_query_empty(self, test_gitlab):
        args = ""
        assert args == test_gitlab.build_query()

    def test_build_query_one(self, test_gitlab):
        args = "?package_name=name"
        assert args == test_gitlab.build_query(package_name="name")

    def test_build_query_two(self, test_gitlab):
        args = "?package_name=name&package_version=version"
        assert args == test_gitlab.build_query(
            package_name="name", package_version="version"
        )

    def test_project_path_name(self, test_gitlab):
        url = "projects/namespace%2Fpath"
        assert url == test_gitlab._build_path(
            "projects", parse.quote_plus("namespace/path")
        )

    def test_get_headers(self, test_gitlab):
        assert test_gitlab._get_headers() == {"token-name": "token-value"}

    def test_get_headers_no_name(self):
        test_gitlab = Packages("gl-host", "", "token-value")
        assert test_gitlab._get_headers() == {}

    def test_get_headers_no_value(self):
        test_gitlab = Packages("gl-host", "token-name", "")
        assert test_gitlab._get_headers() == {}

    def test_get_headers_no_name_no_value(self):
        test_gitlab = Packages("gl-host", "", "")
        assert test_gitlab._get_headers() == {}

    def test_list_packages_none(self, test_gitlab, mock_empty_response):
        with patch.object(urllib.request, "urlopen", return_value=mock_empty_response):
            packages = test_gitlab.get_versions("24", "package-name")
            assert len(packages) == 0

    def test_list_packages_one(self, test_gitlab, mock_one_response):
        with patch.object(urllib.request, "urlopen", return_value=mock_one_response):
            packages = test_gitlab.get_versions("18105942", "ABCComponent")
            assert len(packages) == 1

    def test_list_packages_paginate(
        self, test_gitlab, mock_paginate_1, mock_paginate_2
    ):
        side_effects = [mock_paginate_1, mock_paginate_2]
        with patch.object(urllib.request, "urlopen", side_effect=side_effects):
            packages = test_gitlab.get_versions("18105942", "ABCComponent")
            assert len(packages) == 18

    def test_list_name_packages_filter(self, test_gitlab):
        data = ResponseMock(
            200,
            '[{"name": "package-name", "version": "0.1.2"}, {"name": "package-name-something", "version": "0.1.2"}]',
        )
        with patch.object(urllib.request, "urlopen", return_value=data):
            packages = test_gitlab.get_versions("24", "package-name")
            assert len(packages) == 1

    def test_list_name_packages_five(self, test_gitlab, mock_five_response):
        with patch.object(urllib.request, "urlopen", return_value=mock_five_response):
            packages = test_gitlab.get_versions("18105942", "ABCComponent")
            assert len(packages) == 5

    def test_list_files_none(self, test_gitlab, mock_empty_response):
        with patch.object(urllib.request, "urlopen", return_value=mock_empty_response):
            packages = test_gitlab.get_files("24", "123").keys()
            assert len(packages) == 0

    def test_list_files_one(self, test_gitlab):
        data = ResponseMock(200, '[{"id": 1, "file_name": "filea.txt"}]')
        with patch.object(urllib.request, "urlopen", return_value=data):
            packages = test_gitlab.get_files("24", "123").keys()
            assert len(packages) == 1

    def test_list_files_five(self, test_gitlab):
        data = ResponseMock(
            200,
            '[{"id": 1, "file_name": "filea.txt"}, {"id": 2, "file_name": "fileb.txt"}, {"id": 3, "file_name": "filec.txt"}, {"id": 4, "file_name": "filed.txt"}, {"id": 5, "file_name": "filee.txt"}]',
        )
        with patch.object(urllib.request, "urlopen", return_value=data):
            packages = test_gitlab.get_files("24", "123").keys()
            assert len(packages) == 5

    def test_package_id_none(self, test_gitlab, mock_empty_response):
        with patch.object(urllib.request, "urlopen", return_value=mock_empty_response):
            packages = test_gitlab.get_id("24", "package-name", "0.1")
            assert packages == -1

    def test_package_id_one(self, test_gitlab):
        data = ResponseMock(200, '[{"id": 123}]')
        with patch.object(urllib.request, "urlopen", return_value=data):
            packages = test_gitlab.get_id("24", "package-name", "0.1")
            assert packages == 123

    def test_upload_file(self, test_gitlab):
        data = ResponseMock(201, "[]")
        with patch("builtins.open", mock_open(read_data="data")):
            with patch.object(urllib.request, "urlopen", return_value=data):
                success = test_gitlab.upload_file(
                    "24", "package-name", "0.1", "file", ""
                )
                assert success == 0

    def test_upload_files(self, test_gitlab):
        data = ResponseMock(201, "[]")
        with patch("builtins.open", mock_open(read_data="data")) as p_open:
            with patch.object(urllib.request, "urlopen", return_value=data):
                success = test_gitlab.upload_file(
                    "24", "package-name", "0.1", "", "test/data"
                )
                # This magic number is just the number of files in test/data folder.
                # In case files are added or removed... This should be updated.
                assert p_open.call_count == 10
                assert success == 0

    def test_download_file(self, test_gitlab):
        data = ResponseMock(200, "file-content")
        with patch("builtins.open", mock_open()) as file_mock:
            # mock_open.write.return_value = 0
            with patch.object(urllib.request, "urlopen", return_value=data):
                ret = test_gitlab.download_file("24", "package-name", "0.1", "file.txt")
                assert ret == 0
            file_mock.assert_called_once_with("file.txt", "wb")
            file_mock().write.assert_called_once_with("file-content")

    def test_delete_file(self, test_gitlab):
        packages = ResponseMock(200, '[{"id": 123}]')
        files = ResponseMock(200, '[{"id": 2, "file_name": "file.txt"}]')
        data = ResponseMock(204, None)
        side_effects = [packages, files, data]
        # mock_open.write.return_value = 0
        with patch.object(urllib.request, "urlopen", side_effect=side_effects):
            ret = test_gitlab.delete_file("24", "package-name", "0.1", "file.txt")
            assert ret == 0

    def test_delete_package(self, test_gitlab):
        packages = ResponseMock(200, '[{"id": 123}]')
        data = ResponseMock(204, None)
        side_effects = [packages, data]
        # mock_open.write.return_value = 0
        with patch.object(urllib.request, "urlopen", side_effect=side_effects):
            ret = test_gitlab.delete_package("24", "package-name", "0.1")
            assert ret == 0
