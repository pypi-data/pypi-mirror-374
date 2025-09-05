# import pyspark
# from delta.tables import *
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.filedatalake import (
    # DataLakeServiceClient,
    DataLakeFileClient,
    DataLakeDirectoryClient,
    FileSystemClient,
)
from azure.identity import DefaultAzureCredential, AzurePowerShellCredential
from io import BytesIO
import os
import time


class adls_util:

    # global variables
    UPLOAD_TIMEOUT_SECS = 5 * 3600
    UPLOAD_CHUNK_SIZE = 10 * 1024 * 1024
    AZ_CREDENTIAL = None

    @classmethod
    def get_azure_credential(cls):
        if cls.AZ_CREDENTIAL == None:
            cls.AZ_CREDENTIAL = DefaultAzureCredential(
                exclude_interactive_browser_credential=False
            )
        return cls.AZ_CREDENTIAL

    @classmethod
    def create_directory(
        cls,
        file_system_client: FileSystemClient,
        directory_name: str,
    ) -> DataLakeDirectoryClient:
        directory_client = file_system_client.create_directory(directory_name)

        return directory_client

    @classmethod
    def list_directory_contents(
        cls,
        file_system_client: FileSystemClient,
        directory_name: str,
    ):
        paths = file_system_client.get_paths(path=directory_name)

        for path in paths:
            print(path.name + "\n")

    @classmethod
    def file_exists(cls, file_client: DataLakeFileClient):
        try:
            file_client.get_file_properties()
            return True
        except ResourceNotFoundError:
            return False

    @classmethod
    def upload_file_to_directory(
        cls,
        directory_client: DataLakeDirectoryClient,
        upload_file_name: str,
        local_file_name: str,
        local_path: str,  # directory path
    ):
        file_client = directory_client.get_file_client(upload_file_name)

        # handle existing file conflict
        if cls.file_exists(file_client):
            file_timestamp = time.strftime("%Y%m%d%H%M", time.localtime())
            split_file_name = upload_file_name.split(".")
            old_renamed_file_name = f"{'.'.join(split_file_name[:-1])}_{file_timestamp}_bak.{split_file_name[-1]}"
            cls.rename_file(
                directory_client=directory_client,
                old_file_name=upload_file_name,
                new_file_name=old_renamed_file_name,
            )
            print(
                f"{upload_file_name} already exist in azure directory, and it has been renamed with a timestamp."
            )
        # upload file
        with open(file=os.path.join(local_path, local_file_name), mode="rb") as data:
            # to adjust additional options, see: https://learn.microsoft.com/en-us/python/api/azure-storage-file-datalake/azure.storage.filedatalake.datalakefileclient?view=azure-python#azure-storage-filedatalake-datalakefileclient-upload-data
            file_client.upload_data(
                data,
                overwrite=True,
                timeout=cls.UPLOAD_TIMEOUT_SECS,
                chunk_size=cls.UPLOAD_CHUNK_SIZE,
            )
            # alternative method that is more verbose
            # file_client.create_file()
            # file_client.append_data(data, offset=0, length=len(data))
            # file_client.flush_data(len(data))
        print(f"succesfully uploaded {local_file_name}")

    @classmethod
    def read_bytes_from_directory(
        cls,
        directory_client: DataLakeDirectoryClient,
        file_name: str,
    ):
        file_client = directory_client.get_file_client(file_name)

        if cls.file_exists(file_client):
            data_bytes = file_client.download_file().readall()
            bytes_io = BytesIO(data_bytes)
            print(f"succesfully downloaded {file_name} and cached.")
            return bytes_io
        else:
            print(
                f"abort download since {file_name} does not exist in azure directory."
            )

    @classmethod
    def rename_file(
        cls,
        directory_client: DataLakeDirectoryClient,
        old_file_name: str,
        new_file_name: str,
    ):
        file_client = directory_client.get_file_client(old_file_name)
        new_file_client = directory_client.get_file_client(new_file_name)
        nfc_fs_name = new_file_client.file_system_name
        nfc_path_name = new_file_client.path_name
        nfc_full_path = f"{nfc_fs_name}/{nfc_path_name}"
        # to rename, new file name must not already exist and old file name must exist
        if cls.file_exists(file_client) and not cls.file_exists(new_file_client):
            file_client.rename_file(nfc_full_path)
            print(f"succesfully rename {old_file_name} to {new_file_name}")
        else:
            print(
                f"cannot rename {old_file_name} to {new_file_name} due to filename issues"
            )

    @classmethod
    def get_fs_directory_object(
        cls,
        account_url: str,
        file_system_name: str,
        directory_name: str,
        credential: DefaultAzureCredential,
    ):
        # get reference to Azure file system
        az_fs_client = FileSystemClient(
            account_url=account_url,
            file_system_name=file_system_name,
            credential=credential,
        )
        # get directory reference
        az_dir_client = DataLakeDirectoryClient(
            account_url, file_system_name, directory_name, credential
        )
        if not az_dir_client.exists():
            az_dir_client = cls.create_directory(
                file_system_client=az_fs_client, directory_name=directory_name
            )

        return az_fs_client, az_dir_client


class adls_tables:
    """Collection of tools to read and write data tables of specific formats in the Azure Data Lake Storage Gen2"""

    @staticmethod
    def get_cache_file_path(uri):
        cache_dir = os.environ.get("TLPT_ADLS_CACHE_DIR", "C:/Temp/tlpytools/adls")
        file_name = uri.split("/")[-1]
        cache_file = os.path.join(cache_dir, file_name)
        os.makedirs(cache_dir, exist_ok=True)
        return cache_file

    @classmethod
    def get_table_by_name(cls, uri):
        """returns byte io and cache location of table given uri

        Args:
            uri (str): uri starts with https for azure data lake store
        """
        # parse uri
        ADLS_URL = "/".join(uri.split("/")[0:3])
        ADLS_CONTAINER = uri.split("/")[3]
        ADLS_DIR = "/".join(uri.split("/")[4:-1])
        ADLS_FILE = "/".join(uri.split("/")[-1:])

        # get directory object from name
        az_fs, az_dir = adls_util.get_fs_directory_object(
            account_url=ADLS_URL,
            file_system_name=ADLS_CONTAINER,
            directory_name=ADLS_DIR,
            credential=adls_util.get_azure_credential(),
        )
        return adls_util.read_bytes_from_directory(
            directory_client=az_dir, file_name=ADLS_FILE
        )

    @classmethod
    def write_table_by_name(cls, uri, local_path, file_name):
        # parse uri
        ADLS_URL = "/".join(uri.split("/")[0:3])
        ADLS_CONTAINER = uri.split("/")[3]
        ADLS_DIR = "/".join(uri.split("/")[4:-1])
        ADLS_FILE = "/".join(uri.split("/")[-1:])

        # get directory object from name
        az_fs, az_dir = adls_util.get_fs_directory_object(
            account_url=ADLS_URL,
            file_system_name=ADLS_CONTAINER,
            directory_name=ADLS_DIR,
            credential=adls_util.get_azure_credential(),
        )
        adls_util.upload_file_to_directory(
            directory_client=az_dir,
            upload_file_name=ADLS_FILE,
            local_file_name=file_name,
            local_path=local_path,
        )
