from tests.mocks.openstack.openstack_connection_mock import OpenStackConnectionMock
from pathlib import Path
from os import path
from shutil import rmtree, copytree
from subprocess import run
from database.schema_manager import SchemaManager
from database.database_manager import DatabaseManager
from models.user.authenticated_user import AuthenticatedUser
from typing import Callable
import logging
import pytest
import sqlite3

MOCK_CLUSTERS_PATH = path.join("/tmp", "clusters")


def setup_mock_clusters(cluster_names):
    rmtree(MOCK_CLUSTERS_PATH, ignore_errors=True)
    for cluster_name in cluster_names:
        copytree(
            path.join(Path(__file__).parent, "mock-clusters", cluster_name),
            path.join(MOCK_CLUSTERS_PATH, cluster_name),
        )


def teardown_mock_clusters(cluster_names):
    for cluster_name in cluster_names:
        rmtree(path.join(MOCK_CLUSTERS_PATH, cluster_name))


@pytest.fixture(autouse=True)
def database_connection(mocker):
    # Using an in-memory database for faster unit tests with less disk IO
    mocker.patch("database.database_manager.DATABASE_PATH", new=":memory:")

    with DatabaseManager.connect() as database_connection:
        # The database :memory: only exist within a single connection.
        # Therefore, the DatabaseConnection object is mocked to always return the same connection.
        class MockDatabaseConnection:
            def __init__(self):
                self.__connection = None

            def __enter__(self) -> sqlite3.Connection:
                return database_connection

            def __exit__(self, type, value, traceback):
                pass

        mocker.patch(
            "database.database_manager.DatabaseManager.connect",
            return_value=MockDatabaseConnection(),
        )

        # Creating the DB schema
        SchemaManager(database_connection).update_schema()

        # Seeding test data
        test_magic_castle_rows_with_owner = [
            (
                "buildplanning.calculquebec.cloud",
                "buildplanning",
                "calculquebec.cloud",
                "plan_running",
                "build",
                "alice@computecanada.ca",
            ),
            (
                "created.calculquebec.cloud",
                "created",
                "calculquebec.cloud",
                "created",
                "build",
                "alice@computecanada.ca",
            ),
            (
                "empty.calculquebec.cloud",
                "empty",
                "calculquebec.cloud",
                "build_error",
                "none",
                "bob@computecanada.ca",
            ),
            (
                "missingfloatingips.c3.ca",
                "missingfloatingips",
                "c3.ca",
                "build_running",
                "none",
                "bob@computecanada.ca",
            ),
            (
                "missingnodes.sub.example.com",
                "missingnodes",
                "sub.example.com",
                "build_error",
                "none",
                "bob@computecanada.ca",
            ),
            (
                "valid1.calculquebec.cloud",
                "valid1",
                "calculquebec.cloud",
                "build_success",
                "destroy",
                "alice@computecanada.ca",
            ),
        ]
        test_magic_castle_rows_without_owner = [
            (
                "noowner.calculquebec.cloud",
                "noowner",
                "calculquebec.cloud",
                "build_success",
                "destroy",
            ),
        ]
        database_connection.executemany(
            "INSERT INTO magic_castles (hostname, cluster_name, domain, status, plan_type, owner) values (?, ?, ?, ?, ?, ?)",
            test_magic_castle_rows_with_owner,
        )
        database_connection.executemany(
            "INSERT INTO magic_castles (hostname, cluster_name, domain, status, plan_type) values (?, ?, ?, ?, ?)",
            test_magic_castle_rows_without_owner,
        )

        database_connection.commit()
        yield database_connection


@pytest.fixture
def alice() -> Callable[[sqlite3.Connection], AuthenticatedUser]:
    return lambda database_connection: AuthenticatedUser(
        database_connection,
        edu_person_principal_name="alice@computecanada.ca",
        given_name="Alice",
        surname="Tremblay",
        mail="alice.tremblay@example.com",
    )


@pytest.fixture
def bob() -> Callable[[sqlite3.Connection], AuthenticatedUser]:
    return lambda database_connection: AuthenticatedUser(
        database_connection,
        edu_person_principal_name="bob@computecanada.ca",
        given_name="Bob",
        surname="Rodriguez",
        mail="bob-rodriguez435@example.com",
    )


@pytest.fixture(autouse=True)
def mock_clusters_path(mocker):
    mocker.patch("models.magic_castle.magic_castle.CLUSTERS_PATH", new=MOCK_CLUSTERS_PATH)
    mocker.patch(
        "models.magic_castle.magic_castle_configuration.CLUSTERS_PATH", new=MOCK_CLUSTERS_PATH
    )


@pytest.fixture(autouse=True)
def generate_test_clusters():
    mock_cluster_names = [
        "buildplanning.calculquebec.cloud",
        "created.calculquebec.cloud",
        "empty.calculquebec.cloud",
        "missingnodes.sub.example.com",
        "valid1.calculquebec.cloud",
        "missingfloatingips.c3.ca",
    ]
    setup_mock_clusters(mock_cluster_names)
    yield
    teardown_mock_clusters(mock_cluster_names)


@pytest.fixture(autouse=True)
def mock_openstack_manager(mocker):
    mocker.patch("openstack.connect", return_value=OpenStackConnectionMock())
