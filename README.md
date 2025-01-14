# Restore GitLab Backup Hashed Repos

**Restore GitLab Backup Hashed Repos** is a Python utility to extract and restore repositories from a GitLab backup tarball. This script automates the process of converting hashed GitLab repository backups into a human-readable structure with organized directories, making it easy to identify and restore repositories.

## Features

- **Automated Repository Extraction**: Extract and restore repositories from hashed GitLab backups into a structured directory format.
- **Database Interaction**: Reads and processes the database dump from the GitLab backup to fetch project and repository mappings.
- **Zero Configuration**: Automatically sets up a temporary PostgreSQL database and restores data without requiring pre-existing configurations.
- **User-Friendly Output**: Logs informative progress, errors, and warnings, including a tabulated view of repository mappings.
- **Cross-Platform Compatibility**: Works on Unix-based systems with Python 3.8+.

## Prerequisites

- **Python**: Version 3.8 or higher
- **PostgreSQL**: Ensure `psql` is installed and accessible in your system's `PATH`
- **Git**: Required for cloning repository bundles
- **GNU Tar**: For handling `.tar.gz` files
- Install required Python dependencies via `pip`.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/roncodes/restore-gitlab-backup-hashed-repos.git
   cd restore-gitlab-backup-hashed-repos
   ```

2. **Install Dependencies**:
   Use the `requirements.txt` file to install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Installation**:
   Ensure the script is executable by running:
   ```bash
   python src/script.py --help
   ```

## Usage

Run the script with the required parameters to extract repositories from a GitLab backup tarball:

```bash
python src/script.py --backup <path-to-gitlab-backup.tar> --output <output-directory>
```

### Arguments

- `--backup` $begin:math:text$required$end:math:text$: Path to the GitLab backup tarball (e.g., `1732982737_gitlab_backup.tar`).
- `--output` $begin:math:text$required$end:math:text$: Path to the output directory where repositories will be extracted.

### Example

```bash
python src/script.py --backup ~/Desktop/gitlab_backup.tar --output ~/Desktop/restored-gitlab-repos
```

### Expected Output

After execution, the script organizes repositories into the specified output directory:

```
<output-directory>/
├── group-name/
│   ├── repo-name-1/
│   ├── repo-name-2/
│   └── ...
└── another-group/
    ├── repo-name-3/
    └── ...
```

### Debugging

For debugging purposes, the script displays a tabulated view of the repository mappings $begin:math:text$project name, group path, and hashed path$end:math:text$ and logs progress at every step.

## Development

### Setting Up Development Environment

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/<your-username>/restore-gitlab-backup-hashed-repos.git
   cd restore-gitlab-backup-hashed-repos
   ```

2. **Install Development Dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Run Tests**:
   ```bash
   pytest
   ```

### Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

### Build and Release

The project uses GitHub Actions for automated builds. To build a binary for distribution:

1. Install `pyinstaller`:
   ```bash
   pip install pyinstaller
   ```

2. Build the binary:
   ```bash
   pyinstaller --onefile src/script.py --name restore-hashed-gitlab-backup-repos
   ```

3. The binary will be available in the `dist` directory.

## License

This project is licensed under the $begin:math:display$MIT License$end:math:display$$begin:math:text$LICENSE$end:math:text$.

## Acknowledgments

Special thanks to contributors and the open-source community for support and feedback.