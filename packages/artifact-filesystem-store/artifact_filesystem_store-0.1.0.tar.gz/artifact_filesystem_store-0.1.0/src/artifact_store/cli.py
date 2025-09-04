import argparse
import fnmatch
import glob
import lzma
import os
import sys
import tarfile
import time
from functools import partial
from pathlib import Path

from . import ArtifactMetaData

_verbose = False


def vprint(*args, **kwargs):
    """Prints the arguments if verbose is True."""
    if _verbose:
        print(*args, **kwargs)


def fatal(*args, **kwargs):
    """Prints the arguments and raises."""
    print(*args, **kwargs)
    raise SystemExit(1)


_MAGIC_FILE_NAME = ".artifact_store"


def check_artifact_store(storage_path: Path):
    """Check if the given path is a valid artifact store."""
    magic_file = storage_path / _MAGIC_FILE_NAME
    if not storage_path.exists() or not storage_path.is_dir():
        fatal(f"Storage path '{storage_path}' does not exist or is not a directory.")
    if not magic_file.exists():
        fatal(f"Storage path '{storage_path}' is not a valid artifact store (missing {_MAGIC_FILE_NAME} file).")


def init(args):
    """Initialize the artifact store in the given storage path."""
    vprint(f"Initializing artifact store at '{args.storage_root}'")
    storage_path = args.storage_root
    try:
        storage_path.mkdir(parents=True, exist_ok=False)
        magic_file = storage_path / _MAGIC_FILE_NAME
        magic_file.touch()
        vprint(f"Artifact store initialized at '{storage_path}'")
    except Exception as e:
        fatal(f"Failed to initialize artifact store at '{storage_path}': {e}")
    check_artifact_store(storage_path)  # sanity check


def artifact_path(storage_root: Path, namespace: Path) -> Path:
    """Returns the path to the package directory for the current namespace."""
    return storage_root / namespace / 'artifacts'


def tag_path(storage_root: Path, namespace: Path) -> Path:
    """Returns the path to the package directory for the current namespace."""
    return storage_root / namespace / 'tags'


def tar_filter(exclude_globs, tarinfo):
    """Filter function for tarfile to exclude certain files."""
    for pattern in exclude_globs:
        if fnmatch.fnmatch(tarinfo.name, pattern):
            vprint(f"Excluding '{tarinfo.name}' from archive as per exclude pattern '{pattern}'")
            return None
    return tarinfo


def store(args):
    """Store a file or directory as an artifact."""
    check_artifact_store(args.storage_root)

    vprint(f"Storing artifact '{args.name}'")
    vprint(f"  with globs: '{args.glob}'")
    vprint(f"  setting revision: '{args.revision}'")
    vprint(f"  linking tag: {args.tag}")
    vprint(f"  copying files: {args.copy}")

    package_path = artifact_path(args.storage_root, args.namespace)
    vprint(f"  package path: '{package_path}'")

    # location of the artifact - either an archive or a directory
    artifact_location = package_path / f"{args.name}-{args.revision}"

    # metadata file location
    meta_filename = artifact_location.with_suffix(".meta.json")
    if meta_filename.is_file():
        fatal(f"Metadata file '{meta_filename}' already exists, fatal - exiting.")

    # create Metadata object
    meta = ArtifactMetaData({"__API__": "1"})
    meta.add("__created_at", int(time.time()))

    if args.meta:
        for item in args.meta:
            if '=' not in item:
                fatal(f"Invalid metadata format '{item}', expected key=value")
            key, value = item.split('=', 1)
            vprint(f"  adding metadata: {key}={value}")
            meta.add(key, value)

    # Ensure the package directory exists
    package_path.mkdir(parents=True, exist_ok=True)

    # tar or copy files
    if args.copy:
        raise NotImplementedError("Copying files is not implemented yet.")
    else:
        archive = artifact_location.with_suffix(".tar.xz")  # no check needed - checked above

        # Expand all include globs
        paths = set()
        for pattern in args.glob:
            vprint(f"  processing glob: '{pattern}'")
            paths.update(glob.glob(pattern, recursive=True))
            vprint(f"  after {paths}'")

        vprint(f"Creating tarball: {archive}, metadata: {meta_filename}")
        # Create a tarball of the specified location
        with lzma.open(archive, "wb", preset=2) as xz:  # preset = 0..9
            with tarfile.open(fileobj=xz, mode="w") as tar:
                for f in paths:
                    print(f"Adding '{f}' to archive")
                    tar.add(f,
                            filter=partial(tar_filter, args.exclude) if args.exclude else None)

        vprint(f"Tarball created: {archive}")

        # Add metadata next to the tarball
        with open(meta_filename, mode="w") as metafile:
            metafile.write(str(meta))

    if args.tag:
        tag_link = tag_path(args.storage_root, args.namespace) / f"{args.name}-{args.tag}"
        tag_link.parent.mkdir(parents=True, exist_ok=True)
        vprint(f"Linking tag: '{tag_link}' to '{archive}'")
        if tag_link.is_symlink() or tag_link.exists():
            tag_link.unlink()
        tag_link.symlink_to(archive)


def retrieve(args):
    """Retrieve an artifact by name and version or tag."""
    check_artifact_store(args.storage_root)

    vprint(f"Retrieving artifact '{args.name}'")
    vprint(f"  to location '{args.location}'")

    archive = None
    if args.revision:
        vprint(f"  retrieving revision: {args.revision}")
        archive = artifact_path(args.storage_root, args.namespace) / f"{args.name}-{args.revision}.tar.xz"

    if args.tag:
        vprint(f"  retrieving tag: {args.tag}")
        tag_link = tag_path(args.storage_root, args.namespace) / f"{args.name}-{args.tag}"
        if not tag_link.is_symlink():
            fatal(f"Tagged artifact '{tag_link}' is not a symlink, cannot retrieve.")
        archive = tag_link.resolve()

    vprint(f"  archive location: '{archive}'")

    if archive is None or not archive.is_file():
        fatal(f"Artifact '{archive}' does not exist.")
    vprint(f"  found archive: {archive}")

    # Ensure the target directory exists
    location = args.location
    location.mkdir(parents=True, exist_ok=True)
    vprint(f"  extracting to: {location}")

    # Extract the tarball to the specified location
    with tarfile.open(archive, "r:xz") as tar:
        if sys.version_info >= (3, 12):
            tar.extractall(path=location, filter='fully_trusted')
        else:
            tar.extractall(path=location)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Artifact Store interaction script")

    # Global (main) arguments
    parser.add_argument("-s", "--storage-root", type=Path, help="storage path (root of artifact store), "
                                                                "default: ARTIFACT_STORE_ROOT-environment-variable",
                        default=os.getenv("ARTIFACT_STORE_ROOT", None))
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    # Subparsers for subcommands
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: init
    parser_init = subparsers.add_parser("init", help="Initialize artifact store in the storage path")
    parser_init.set_defaults(func=init)

    # Subcommand: store
    parser_store = subparsers.add_parser("store", help="Store file/directory as artifact")
    parser_store.add_argument("-t", "--tag", type=str, help="tag artifact with a tag name (e.g. latest)")
    parser_store.add_argument("-r", "--revision", type=str, required=True, help="revision/unique-id of artifact")
    parser_store.add_argument("-c", "--copy", action="store_true", default=False,
                              help="copy files instead of creating a tar-package")
    parser_store.add_argument("-m", "--meta", action="append", help="Key-value pairs like key=value for metadata"
                                                                    "added to the artifact")
    parser_store.add_argument("-e", "--exclude", action="append", default=[],
                              help="a glob of directories or files to be excluded")

    parser_store.add_argument("namespace", type=str, help="namespace of the artifact")
    parser_store.add_argument("name", type=str, help="name of artifact")
    parser_store.add_argument("glob", type=str, nargs='+', help="globs for files and directories to store")

    parser_store.set_defaults(func=store)

    # Subcommand: retrieve
    parser_retrieve = subparsers.add_parser("retrieve", help="Retrieve a file an artifact")

    group = parser_retrieve.add_mutually_exclusive_group(required=True)
    group.add_argument("-t", "--tag", type=str, help="retrieve tag of artifact")
    group.add_argument("-r", "--revision", type=str, help="revision/unique-id of artifact to retrieve")

    parser_retrieve.add_argument("namespace", type=str, help="namespace of the artifact")
    parser_retrieve.add_argument("name", type=str, help="name of artifact")
    parser_retrieve.add_argument("location", type=Path, help="local directory location to retrieve to")

    parser_retrieve.set_defaults(func=retrieve)

    args = parser.parse_args(argv)
    global _verbose
    _verbose = args.verbose

    # bail out if storage is not set
    if args.storage_root is None:
        fatal("Storage path is not provided. Please set the --storage-root argument or "
              "the ARTIFACT_STORE_ROOT environment variable.")

    args.func(args)


if __name__ == "__main__":
    main(sys.argv[1:])
