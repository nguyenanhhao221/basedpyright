from __future__ import annotations

import os
from json import loads
from pathlib import Path
from shutil import copyfile, copytree
from typing import TYPE_CHECKING, TypedDict, cast

from nodejs import node

if TYPE_CHECKING:
    # https://github.com/samwillis/nodejs-pypi/pull/23
    from subprocess import run  # noqa: S404

    from pdm.backend.hooks import Context
else:
    from nodejs.npm import run


# these are hook functions where all args are required regardless of whether or not they are used
# ruff: noqa: ARG001


class PackageJson(TypedDict):
    bin: dict[str, str]


def pdm_build_update_files(context: Context, files: dict[str, Path]):
    # ah yes, the classic "wrong path" moment!
    os.environ["PATH"] = os.pathsep.join([str(Path(node.__file__).parent), os.environ["PATH"]])

    if not Path("node_modules").exists():
        _ = run(["ci"], check=True)
    _ = run(["run", "build:cli:dev"], check=True)

    npm_package_dir = Path("packages/pyright")
    pypi_package_dir = Path("basedpyright")

    copytree(npm_package_dir / "dist", pypi_package_dir / "dist", dirs_exist_ok=True)
    for script_path in cast(PackageJson, loads((npm_package_dir / "package.json").read_text()))[
        "bin"
    ].values():
        _ = copyfile(npm_package_dir / script_path, pypi_package_dir / script_path)
