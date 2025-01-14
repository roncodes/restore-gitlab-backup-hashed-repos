# Restore Hashed GitLab Backup Repos

A Python script to extract repositories from a hashed GitLab backup and restore them into a structured directory format.

## Features

- Automatically extracts GitLab backups and restores repositories.
- Creates directory structure: `output/{groupName}/{repoName}`.
- Includes progress indicators and logging.
- Easy-to-use binary for distribution.

## Requirements

- Python 3.6 or later
- PostgreSQL installed and running locally
- Git installed and in `PATH`

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/roncodes/restore-gitlab-backup-hashed-repos.git
   cd restore-gitlab-backup-hashed-repos