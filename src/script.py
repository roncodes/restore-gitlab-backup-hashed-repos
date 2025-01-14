import os
import subprocess
import tarfile
import psycopg2
import argparse
import tempfile
import shutil
import logging
import getpass
from tabulate import tabulate
from tqdm import tqdm

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

DB_SETTINGS = {
    "dbname": "gitlab_temp_backup", 
    "user": getpass.getuser(), 
    "password": "",
    "host": "localhost",
    "port": 5432
}

def extract_backup(backup_tar_path, extract_to):
    try:
        logging.info(f"Extracting backup tarball: {backup_tar_path}")
        with tarfile.open(backup_tar_path, "r") as tar:
            tar.extractall(path=extract_to)
        logging.info(f"Backup extracted to: {extract_to}")
        return os.path.join(extract_to, "db", "database.sql.gz")
    except tarfile.ReadError as e:
        logging.error(f"Error extracting backup: {e}")
        return None

def setup_temp_database(database_sql_gz_path):
    try:
        logging.info("Decompressing database dump.")
        database_sql_path = database_sql_gz_path.replace(".gz", "")
        subprocess.run(["gunzip", database_sql_gz_path], check=True)

        logging.info(f"Checking if the database '{DB_SETTINGS['dbname']}' exists.")
        result = subprocess.run(
            ["psql", "-d", "postgres", "-tAc", f"SELECT 1 FROM pg_database WHERE datname = '{DB_SETTINGS['dbname']}'"],
            capture_output=True, text=True, check=True
        )
        if result.stdout.strip() != "1":
            logging.info(f"Creating database: {DB_SETTINGS['dbname']}.")
            subprocess.run(["createdb", DB_SETTINGS["dbname"], "-U", DB_SETTINGS["user"]], check=True)
        else:
            logging.info(f"Database '{DB_SETTINGS['dbname']}' already exists.")

        logging.info("Restoring database dump.")
        subprocess.run(
            ["psql", "-d", DB_SETTINGS["dbname"], "-f", database_sql_path, "-U", DB_SETTINGS["user"]],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=True
        )
        logging.info("Database restored successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error restoring database: {e}")
        raise

def print_debug_table(repositories):
    # Unpack the tuples directly into table data
    table_data = [
        [repo[1], repo[2], repo[3]]  # Use tuple indices: [project_name, group_path, hashed_path]
        for repo in repositories
    ]
    headers = ["Project Name", "Group Path", "Hashed Path"]
    print("\nRepository Mapping:")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def fetch_repository_mapping():
    query = """
    SELECT 
        p.id AS project_id,
        p.name AS project_name,
        n.path AS group_path,
        CONCAT('@hashed/', LEFT(pr.disk_path, 2), '/', SUBSTRING(pr.disk_path, 3, 2), '/', pr.disk_path, '.bundle') AS hashed_path
    FROM projects p
    JOIN namespaces n ON p.namespace_id = n.id
    JOIN project_repositories pr ON p.id = pr.project_id;
    """
    try:
        logging.info("Fetching repository mapping from the database.")
        conn = psycopg2.connect(**DB_SETTINGS)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        logging.info(f"Fetched {len(results)} repositories.")
        print_debug_table(results)
        return results
    except Exception as e:
        logging.error(f"Error fetching repository mapping: {e}")
        return []

def construct_bundle_path(base_path, hashed_path):
    # Remove redundant '@h/as/@hashed/' from the hashed path
    corrected_hashed_path = hashed_path.replace("@hashed/@h/as/@hashed/", "@hashed/")
    return os.path.join(base_path, "repositories", corrected_hashed_path)

def extract_bundles(backup_path, output_path, repository_mapping):
    os.makedirs(output_path, exist_ok=True)
    for _, project_name, group_path, hashed_path in tqdm(repository_mapping, desc="Extracting bundles"):
        # Construct the correct bundle path
        bundle_path = construct_bundle_path(backup_path, hashed_path)

        if not os.path.exists(bundle_path):
            logging.warning(f"Bundle not found: {bundle_path}")
            continue

        project_output_dir = os.path.join(output_path, group_path, project_name)
        os.makedirs(project_output_dir, exist_ok=True)

        logging.info(f"Extracting {bundle_path} to {project_output_dir}")
        try:
            subprocess.run(["git", "clone", bundle_path, project_output_dir], check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Error extracting {bundle_path}: {e}")

def cleanup_temp_database():
    try:
        logging.info("Dropping temporary database.")
        subprocess.run(["dropdb", DB_SETTINGS["dbname"]], check=True)
        logging.info("Temporary database dropped.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error cleaning up temporary database: {e}")

def main():
    parser = argparse.ArgumentParser(description="Extract GitLab bundles to structured directories.")
    parser.add_argument("--backup", required=True, help="Path to the GitLab backup tar.gz file.")
    parser.add_argument("--output", required=True, help="Path to the desired output directory.")
    args = parser.parse_args()

    temp_dir = tempfile.mkdtemp()

    try:
        database_sql_gz_path = extract_backup(args.backup, temp_dir)
        if not database_sql_gz_path:
            logging.error("Failed to extract backup. Exiting.")
            return

        setup_temp_database(database_sql_gz_path)

        repository_mapping = fetch_repository_mapping()
        if not repository_mapping:
            logging.error("No repository mapping found. Exiting.")
            return

        extract_bundles(temp_dir, args.output, repository_mapping)
    finally:
        cleanup_temp_database()
        # shutil.rmtree(temp_dir)
        # logging.info("Cleanup completed.")

if __name__ == "__main__":
    main()