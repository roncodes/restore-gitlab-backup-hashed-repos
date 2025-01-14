import os
import tempfile
import subprocess
import gzip
from pathlib import Path

import pytest
from src.script import extract_backup, setup_temp_database, fetch_repository_mapping, construct_bundle_path

@pytest.fixture
def temp_backup_file():
    """Create a temporary backup tarball for testing."""
    temp_dir = tempfile.mkdtemp()
    tar_path = os.path.join(temp_dir, "test_backup.tar.gz")

    # Simulate creating a test tarball
    with tempfile.TemporaryDirectory() as mock_data_dir:
        db_dir = os.path.join(mock_data_dir, "db")
        os.makedirs(db_dir, exist_ok=True)

        # Simulate database.sql.gz
        with open(os.path.join(db_dir, "database.sql.gz"), "wb") as f:
            f.write(b"Mock database data")

        # Simulate repositories directory
        os.makedirs(os.path.join(mock_data_dir, "repositories/@hashed"), exist_ok=True)

        # Create tarball
        subprocess.run(["tar", "-czf", tar_path, "-C", mock_data_dir, "."], check=True)

    yield tar_path
    # Cleanup
    if os.path.exists(temp_dir):
        os.remove(tar_path)


def test_extract_backup(temp_backup_file):
    """Test the extract_backup function."""
    temp_dir = tempfile.mkdtemp()
    db_path = extract_backup(temp_backup_file, temp_dir)

    assert db_path is not None
    assert os.path.exists(db_path)
    assert db_path.endswith("database.sql.gz")


def test_setup_temp_database(temp_backup_file):
    """Test the setup_temp_database function."""
    temp_dir = tempfile.mkdtemp()
    
    # Simulate extracting a valid gzip database file
    db_dir = os.path.join(temp_dir, "db")
    os.makedirs(db_dir, exist_ok=True)
    db_file_path = os.path.join(db_dir, "database.sql.gz")
    with gzip.open(db_file_path, "wb") as f:
        f.write(b"CREATE DATABASE gitlab_temp_backup;")
    
    # Decompress the database and set up a temporary DB
    try:
        setup_temp_database(db_file_path)
    except subprocess.CalledProcessError as e:
        pytest.fail(f"setup_temp_database raised an error: {e}")


def test_fetch_repository_mapping():
    """Test fetch_repository_mapping function."""
    # Assumes a database has been set up with dummy data
    repositories = fetch_repository_mapping()
    assert isinstance(repositories, list)
    assert len(repositories) >= 0


def test_construct_bundle_path():
    """Test the construct_bundle_path function."""
    base_path = "/tmp/mock"
    hashed_path = "@hashed/@h/as/@hashed/28/58/2858dcd1057d3eae7f7d5f782167e24b61153c01551450a628cee722509f6529"
    result = construct_bundle_path(base_path, hashed_path)

    expected_path = "/tmp/mock/repositories/@hashed/28/58/2858dcd1057d3eae7f7d5f782167e24b61153c01551450a628cee722509f6529"
    assert result == expected_path


@pytest.mark.parametrize("group_path, project_name, hashed_path", [
    ("group1", "project1", "@hashed/28/58/2858dcd.bundle"),
    ("group2", "project2", "@hashed/41/52/4152dcd.bundle"),
])
def test_bundle_extraction(group_path, project_name, hashed_path):
    """Test the process of bundle extraction."""
    output_dir = tempfile.mkdtemp()
    backup_dir = tempfile.mkdtemp()
    
    # Simulate hashed paths in the backup
    hashed_segments = hashed_path.split("/")
    hashed_dir = os.path.join(backup_dir, "repositories", *hashed_segments[:-1])
    os.makedirs(hashed_dir, exist_ok=True)
    mock_bundle_path = os.path.join(hashed_dir, hashed_segments[-1])
    with open(mock_bundle_path, "wb") as f:
        f.write(b"mock bundle data")
    
    constructed_path = construct_bundle_path(backup_dir, hashed_path)
    assert os.path.exists(constructed_path), f"Constructed path does not exist: {constructed_path}"