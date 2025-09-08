"""GitLab generic packages module"""

from glob import glob
from http.client import HTTPMessage
from json import loads
import logging
import os
from urllib import request, parse

logger = logging.getLogger(__name__)


class Packages:
    """Class to interact with GitLab packages REST API"""

    def __init__(self, host: str, token_type: str, token: str):
        """
        Creates a new instance of class.

        Parameters
        ----------
        host : str
            The GitLab instance hostname, without schema.
            The host will be used for the package API interaction.
            For example gitlab.com.
        token_type : str
            The token type or "user" to authenticate with GitLab REST API.
            For personal, project, and group tokens this is `PRIVATE-TOKEN`.
            For `CI_JOB_TOKEN` this is `JOB-TOKEN`.
            Can be left empty when authentication is not used.
        token : str
            The token (secret) to authenticate with GitLab REST API.
            This can be a personal token, project token, or`CI_JOB_TOKEN`.
            Leave empty when authentication is not used.
        """
        self.host = host
        self.token_type = token_type
        self.token = token

    def _url(self) -> str:
        """
        Returns the GitLab REST API URL by using the host variable.

        Returns
        -------
        str
            The GitLab REST API URL, for example `https://gitlab.com/api/v4/`.
        """
        return f"https://{self.host}/api/v4/"

    def _get_headers(self) -> dict:
        """
        Creates headers for a GitLab REST API call.

        The headers contain token for authentication according to the
        instance variables.

        Returns
        -------
        dict
            Headers for a REST API request, that contain the authentication token.
        """
        headers = {}
        if self.token_type and self.token:
            headers = {self.token_type: self.token}
        return headers

    def _parse_header_links(self, headers: HTTPMessage) -> dict:
        """
        Parses link field from HTTP headers to a dictionary where
        the link "rel" value is the key.

        This is useful for example with GitLab REST API to get the pagination links.

        Parameters
        ----------
        headers : HTTPMessage
            The HTTP response headers that contain the links

        Returns
        -------
        dict
            The header links in a dictionary, that can be used to for example pagination:
            _parse_header_links(headers).get("next") returns the next page link, or None.
        """
        links = {}
        header_links = headers.get("link")
        if header_links:
            items = header_links.split(",")
            # Values are <uri-reference>; param1=value1; param2="value2"
            for item in items:
                parts = item.split(";", 1)
                if parts:
                    # First value should be the URI
                    val = parts.pop(0).lstrip(" <").rstrip("> ")
                    # The rest are the parameters; let's take the first one that has rel=
                    # in it, split it with ; and take the first part as a value
                    typ = parts.pop()
                    typ = typ.split("rel=", 1).pop().split(";").pop(0).strip('" ')
                    links[typ] = val
        return links

    def _build_path(self, *paths: str) -> str:
        """
        Returns the path to be appended to the REST API URL

        Parameters
        ----------
        paths : str
            The path string that are joined with "/".

        Returns
        -------
        str
            A URL path, for example `projects/123/`
            or `projects/namespace%2Fproject/`
        """
        quoted_paths = []
        for subpath in paths:
            quoted_paths.append(subpath)
        return "/".join(quoted_paths)

    def build_query(self, **args: str) -> str:
        """
        Builds a query for a GitLab REST API request

        Parameters
        ----------
        args : str
            keyword arguments for the REST API query, like per_page=20, page=20

        Returns
        -------
        str
            A query string for a REST API request. Append this to
            the request URL. Example `?per_page=20&page=20`.
        """
        query = ""
        for key, value in args.items():
            query = "&".join(filter(None, (query, f"{key}={parse.quote_plus(value)}")))
        if query:
            query = "?" + query
        return query

    def _get(self, url: str, headers: dict) -> tuple[int, bytes, HTTPMessage]:
        """
        Makes a raw GET request to the given URL, and returns
        the response status, body, and headers.

        Parameters
        ----------
        url : str
            The URL of the HTTP request to make.
        headers: dict
            The HTTP headers used in the request.

        Returns
        -------
        int
            The HTTP response code, such as 200
        bytes
            The HTTP response body read as bytes
        HTTPMessage
            The HTTP response headers
        """
        logger.debug("Getting %s", url)
        req = request.Request(url, headers=headers)
        with request.urlopen(req) as response:
            return response.status, response.read(), response.headers

    def get(self, *paths: str, **query_params: str) -> tuple[int, bytes, HTTPMessage]:
        """
        Makes a HTTP GET request to the given GitLab path, and returns
        the response status, body, and headers.

        Parameters
        ----------
        paths : str
            The URL path of the HTTP request to make.
        query_params : str,  optional
            Dictionary of query parameters for the request, like package_name=mypackage

        Returns
        -------
        int
            The HTTP response code, such as 200
        bytes
            The HTTP response body read as bytes
        HTTPMessage
            The HTTP response headers
        """
        url = self._url() + self._build_path(*paths) + self.build_query(**query_params)
        headers = self._get_headers()
        return self._get(url, headers)

    def get_all(self, *paths: str, **query_params: str) -> list:
        """
        Returns data from the REST API endpoint. In case
        of multiple pages, all data will be returned.

        Parameters
        ----------
        paths : str
            The paths of the API endpoint that is called. For example projects, 123, packages
            would be querying the projects/123/packages endpoint.
        query_params : str, optional
            Additional arguments for the query of the URL, for example to filter
            results: package_name=mypackage

        Returns
        -------
        list
            Data from GitLab REST API endpoint with the arguments.
        """
        url = self._url() + self._build_path(*paths) + self.build_query(**query_params)
        data = []
        while url:
            res_status, res_data, res_headers = self._get(url, self._get_headers())
            logger.debug("Response status: %d", res_status)
            res_data = loads(res_data)
            logger.debug("Response data: %s", res_data)
            data = data + res_data
            url = self._parse_header_links(res_headers).get("next")
        return data

    def put(self, data: bytes, *paths: str, **query_params: str) -> int:
        """
        Makes a HTTP PUT request to the given GitLab path.

        Parameters
        ----------
        data : bytes
            The data to PUT.
        paths : str
            The URL path of the HTTP request to make.
        query_params : str, optional
            Additional arguments for the query of the URL, for example to filter
            results: package_name=mypackage

        Returns
        -------
        int
            0 If the request was successful.
        """
        ret = 1
        url = self._url() + self._build_path(*paths) + self.build_query(**query_params)
        logger.debug("Putting %s", url)
        req = request.Request(url, method="PUT", data=data, headers=self._get_headers())
        with request.urlopen(req) as res:
            if res.status == 201:  # 201 is created
                ret = 0
        return ret

    def delete(self, *paths: str, **query_params: str) -> int:
        """
        Makes a HTTP DELETE request to the given GitLab path.

        Parameters
        ----------
        paths : str
            The URL path of the HTTP request to make.
        query_params : str, optional
            Additional arguments for the query of the URL, for example to filter
            results: package_name=mypackage

        Returns
        -------
        int
            0 If the request was successful.
        """
        ret = 1
        url = self._url() + self._build_path(*paths) + self.build_query(**query_params)
        logger.debug("Deleting %s", url)
        req = request.Request(url, method="DELETE", headers=self._get_headers())
        with request.urlopen(req) as res:
            if res.status == 204:
                # 204 is no content, that GL responds when file deleted
                ret = 0
        return ret

    def get_versions(self, project_id: str, package_name: str) -> list:
        """
        Lists the available versions of the package

        Parameters
        ----------
        project_id : str
            The project ID or path, including namespace.
            Examples: `123` or `namespace/project`.
        package_name : str
            The name of the package that is listed.

        Returns
        -------
        list
            List of {package: name, version: version} that are available.
        """
        packages = []
        logger.debug("Listing packages with name %s", package_name)
        data = self.get_all(
            "projects",
            parse.quote_plus(project_id),
            "packages",
            package_name=package_name,
            package_type="generic",
        )
        for package in data:
            name = parse.unquote(package["name"])
            version = parse.unquote(package["version"])
            # GitLab API returns packages that have some match to the filter;
            # let's filter out non-exact matches
            if package_name != name:
                continue
            packages.append({"name": name, "version": version})
        return packages

    def get_files(self, project_id: str, package_id: int) -> dict:
        """
        Lists all files of a specific package ID from GitLab REST API

        Parameters
        ----------
        project_id : str
            The project ID or path, including namespace.
            Examples: `123` or `namespace/project`.
        package_id : int
            The package ID that is listed

        Return
        ------
        dict
            Dictionary of file (names) that are in the package, with
            each element containing a dictionary containing information
            of the file
        """
        files = {}
        logger.debug("Listing package %d files", package_id)
        data = self.get_all(
            "projects",
            parse.quote_plus(project_id),
            "packages",
            str(package_id),
            "package_files",
        )
        for package in data:
            # Only append the filename once to the list of files
            # as there's no way to download them separately through
            # the API
            filename = parse.unquote(package["file_name"])
            file_id = package["id"]
            if not files.get(filename):
                files[filename] = {"id": file_id}
        return files

    def get_id(self, project_id: str, package_name: str, package_version: str) -> int:
        """
        Gets the package ID of a specific package version.

        Parameters
        ----------
        project_id : str
            The project ID or path, including namespace.
            Examples: `123` or `namespace/project`.
        package_name : str
            The name of the package.
        package_version : str
            The version of the package

        Return
        ------
        int
            The ID of the package. -1 if no ID was found.
        """
        package_id = -1
        logger.debug("Fetching package %s (%s) ID", package_name, package_version)
        data = self.get_all(
            "projects",
            parse.quote_plus(project_id),
            "packages",
            package_name=package_name,
            package_version=package_version,
            package_type="generic",
        )
        if len(data) == 1:
            package = data.pop()
            package_id = package["id"]
        return package_id

    def download_file(
        self,
        project_id: str,
        package_name: str,
        package_version: str,
        filename: str,
        destination: str = "",
    ) -> int:
        """
        Downloads a file from a GitLab generic package

        Parameters
        ----------
        project_id : str
            The project ID or path, including namespace.
            Examples: `123` or `namespace/project`.
        package_name : str
            The name of the generic package.
        package_version : str
            The version of the generic package
        filename : str
            The file that is downloaded
        destination : str, optional
            The destination folder of the downloaded file. If not set,
            current working directory is used.

        Return
        ------
        int
            Zero if everything went fine, non-zero coke otherwise.
        """
        ret = 1
        logger.debug("Downloading file %s", filename)
        status, data, _ = self.get(
            "projects",
            parse.quote_plus(project_id),
            "packages",
            "generic",
            parse.quote_plus(package_name),
            parse.quote_plus(package_version),
            parse.quote(filename),
        )
        if status == 200:
            fpath = os.path.join(destination, filename)
            parent = os.path.dirname(fpath)
            if parent:
                # Create missing directories if needed
                # In case path has no parent, current
                # workind directory is used
                os.makedirs(os.path.dirname(fpath), exist_ok=True)
            with open(fpath, "wb") as file:
                file.write(data)
                ret = 0
        return ret

    def upload_file(
        self,
        project_id: str,
        package_name: str,
        package_version: str,
        filename: str,
        source: str,
    ) -> int:
        """
        Uploads file(s) to a GitLab generic package.

        Parameters
        ----------
        project_id : str
            The project ID or path, including namespace.
            Examples: `123` or `namespace/project`.
        package_name : str
            The name of the generic package.
        package_version : str
            The version of the generic package
        pfile : str
            The relative path of the file that is uploaded. If left empty,
            all files from the source folder, and it's subfolders, are uploaded.
        source : str
            The source folder that is used as root when uploading. If empty,
            current working directory is used.

        Return
        ------
        int
            Zero if everything went fine, non-zero coke otherwise.
        """
        files = []
        ret = 1
        if filename:
            files.append(filename)
        else:
            filelist = glob(os.path.join(source, "**"), recursive=True)
            for item in filelist:
                # Only add files, not folders
                if os.path.isfile(os.path.join(item)):
                    # Remove the source folder from the path of the files
                    files.append(os.path.relpath(item, source))
        for afile in files:
            ret = self._upload_file(
                project_id, package_name, package_version, afile, source
            )
            if ret:
                break
        return ret

    def _upload_file(
        self,
        project_id: str,
        package_name: str,
        package_version: str,
        filename: str,
        source: str,
    ) -> int:
        """
        Uploads a file to a GitLab generic package.

        Parameters
        ----------
        project_id : str
            The project ID or path, including namespace.
            Examples: `123` or `namespace/project`.
        package_name : str
            The name of the generic package.
        package_version : str
            The version of the generic package
        filename : str
            The relative path of the file that is uploaded.
        source : str
            The source folder that is used as root when uploading.

        Return
        ------
        int
            Zero if everything went fine, non-zero coke otherwise.
        """
        ret = 1
        fpath = os.path.join(source, filename)
        logger.debug("Uploading file %s from %s", filename, source)
        with open(fpath, "rb") as data:
            ret = self.put(
                data.read(),
                "projects",
                parse.quote_plus(project_id),
                "packages",
                "generic",
                parse.quote_plus(package_name),
                parse.quote_plus(package_version),
                parse.quote(filename),
            )
        return ret

    def delete_package(
        self, project_id: str, package_name: str, package_version: str
    ) -> int:
        """
        Deletes a version of a GitLab generic package.

        Parameters
        ----------
        project_id : str
            The project ID or path, including namespace.
            Examples: `123` or `namespace/project`.
        package_name : str
            The name of the generic package.
        package_version : str
            The version of the generic package that is deleted

        Return
        ------
        int
            Zero if everything went fine, non-zero coke otherwise.
        """
        ret = 1
        package_id = self.get_id(project_id, package_name, package_version)
        if package_id > 0:
            ret = self.delete(
                "projects", parse.quote_plus(project_id), "packages", str(package_id)
            )
        return ret

    def delete_file(
        self,
        project_id: str,
        package_name: str,
        package_version: str,
        filename: str,
    ) -> int:
        """
        Deletes a file from a GitLab generic package.

        Parameters
        ----------
        project_id : str
            The project ID or path, including namespace.
            Examples: `123` or `namespace/project`.
        package_name : str
            The name of the generic package.
        package_version : str
            The version of the generic package
        filename : str
            The path of the file to be deleted in the package.

        Return
        ------
        int
            Zero if everything went fine, non-zero coke otherwise.
        """
        ret = 1
        package_id = self.get_id(project_id, package_name, package_version)
        if package_id > 0:
            package_files = self.get_files(project_id, package_id)
            file_id = package_files.get(filename)
            if file_id and file_id.get("id"):
                file_id = file_id.get("id")
                ret = self._delete_file(project_id, package_id, file_id)
        return ret

    def _delete_file(self, project_id: str, package_id: int, file_id: int) -> int:
        ret = 1
        logger.info(
            "Deleting file %d from package %d from project %s",
            file_id,
            package_id,
            project_id,
        )
        ret = self.delete(
            "projects",
            parse.quote_plus(project_id),
            "packages",
            str(package_id),
            "package_files",
            str(file_id),
        )
        return ret
