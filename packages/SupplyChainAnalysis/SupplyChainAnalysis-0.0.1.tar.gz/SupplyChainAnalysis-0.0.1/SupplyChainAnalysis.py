#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This module provides CLI and functions to analyse supply chain and
#    dependencies in python packages and apt packages.
#    Copyright (C) 2025  SupplyChainAnalysis

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
This module provides CLI and functions to analyse supply chain and
dependencies in python packages and apt packages.
"""

__version__ = "0.0.1"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
This module provides CLI and functions to analyse supply chain and
dependencies in python packages and apt packages.
"""
__url__ = "https://github.com/mauricelambert/SupplyChainAnalysis"

# __all__ = []

__license__ = "GPL-3.0 License"
__copyright__ = """
SupplyChainAnalysis  Copyright (C) 2025  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
copyright = __copyright__
license = __license__

print(copyright)

from pkg_resources import get_distribution, working_set, DistributionNotFound
from importlib.metadata import distributions, requires
from collections import defaultdict, namedtuple
from sys import argv, exit, stderr, executable
from dataclasses import dataclass, field
from typing import Iterable, Dict, Set

# from importlib.util import find_spec
from abc import ABC, abstractmethod

try:
    from apt import Cache
except ImportError:
    apt_imported = False
else:
    cache = Cache()
    apt_imported = True

PackageSeenTree = namedtuple("PackageSeenTree", ["name", "level", "seen"])
installed_packages_names = {dist.metadata["Name"] for dist in distributions()}


@dataclass
class PackageCounter:
    counter: int = 0
    dependencies: Set[str] = field(default_factory=set)


class _PackagesAnalysisTemplate(ABC):
    """
    This class implements the package analysis base template.
    """

    @abstractmethod
    def check_exists(self, package_name: str) -> bool:
        """
        This method should True if package exists else False.
        """

    @abstractmethod
    def get_all(self) -> Iterable[str]:
        """
        This method should returns an iterable with all package names.
        """

    @abstractmethod
    def get_dependencies(self, package_name: str) -> Iterable[str]:
        """
        This method should returns an iterable with
        all dependency names for a package.
        """

    def package_seen_tree(
        self, package_name: str, level: int = 0, seen: set = None
    ) -> Iterable[PackageSeenTree]:
        """
        This generator yields dependencies recursively
        with level and seen state.
        """

        if seen is None:
            seen = set()

        _seen = package_name in seen
        yield PackageSeenTree(package_name, level, seen)

        if _seen:
            return None

        seen.add(package_name)

        for dependency in self.get_dependencies(package_name):
            yield from self.package_seen_tree(dependency, level + 1, seen)

    def print_dependencies_tree(self, package_name: str) -> None:
        """
        This method prints dependencies tree for a package.
        """

        for package in self.package_seen_tree(package_name):
            indent = (
                ("|   " * (package.level - 1) + "|---")
                if package.level
                else ""
            )
            print(f"{indent}{package.name}")

    def dependencies_count(
        self,
        package_name: str,
        package_counters: Dict[str, PackageCounter] = None,
    ) -> Dict[str, PackageCounter]:
        """
        This method counts the dependencies number and
        the seen time number.
        """

        parents = []
        if package_counters is None:
            package_counters = defaultdict(PackageCounter)

        for package in self.package_seen_tree(package_name):
            package_counters[package.name].counter += 1
            while len(parents) > package.level:
                parents.pop()
            for parent in parents:
                package_counters[parent].dependencies.add(package.name)
            parents.append(package.name)

        return package_counters

    @staticmethod
    def print_package_counter(counters: Dict[str, PackageCounter]) -> None:
        """
        This method prints package counters and statistics.
        """

        print("Seen".ljust(10), "Dependencies".ljust(20), "Name", sep="| ")
        print("-" * 10, "-" * 20, "-" * 25, sep="|-")
        for name, counter in sorted(
            counters.items(),
            key=lambda x: (len(x[1].dependencies), x[1].counter),
        ):
            print(
                str(counter.counter).ljust(10),
                str(len(counter.dependencies)).ljust(20),
                name,
                sep="| ",
            )

    def make_statistics(self) -> Dict[str, PackageCounter]:
        """
        This method make statistics about packages and dependencies.
        """

        package_counters = defaultdict(PackageCounter)
        for package_name in self.get_all():
            self.dependencies_count(
                package_name, package_counters=package_counters
            )
        return package_counters

    @staticmethod
    def print_line_grepable_details(
        counters: Dict[str, PackageCounter]
    ) -> None:
        """
        This method prints details in grepable lines.
        """

        for name, counter in sorted(
            counters.items(),
            key=lambda x: (len(x[1].dependencies), x[1].counter),
        ):
            print(
                counter.counter,
                len(counter.dependencies),
                name,
                ",".join(counter.dependencies),
            )


class AptPackagesAnalysis(_PackagesAnalysisTemplate):
    """
    This class implements package dependencies analysis for apt.
    """

    def check_exists(self, package_name: str) -> bool:
        """
        This method should True if package exists else False.
        """

        return package_name in cache

    def get_all(self) -> Iterable[str]:
        """
        The generator yields all installed packages from apt cache.
        """

        for pkg in cache:
            if pkg.is_installed:
                yield pkg.name

    def get_dependencies(self, package_name: str) -> Iterable[str]:
        """
        This generator yields all installed dependencies
        names for a package name.
        """

        for dep_or in cache[package_name].installed.dependencies:
            for dep in dep_or:
                if dep.name in cache and cache[dep.name].is_installed:
                    yield dep.name


class ImportlibPackagesAnalysis(_PackagesAnalysisTemplate):
    """
    This class implements package dependencies analysis for python packages.
    """

    def check_exists(self, package_name: str) -> bool:
        """
        This method should True if package exists else False.
        """

        # try:
        #     return find_spec(package_name) is not None
        # except ModuleNotFoundError:
        #     return False

        return package_name in installed_packages_names

    def get_all(self) -> Iterable[str]:
        """
        The generator yields all installed packages from importlib.
        """

        for name in installed_packages_names:
            yield name

    def get_dependencies(self, package_name: str) -> Iterable[str]:
        """
        This generator yields all installed dependencies
        names for a package name.
        """

        for requirement in requires(package_name) or []:
            name = requirement.split(";", maxsplit=1)[0]
            if ">" in name:
                name = name.split(">", maxsplit=1)[0]
            elif "<" in name:
                name = name.split("<", maxsplit=1)[0]
            elif "=" in name:
                name = name.split("=", maxsplit=1)[0]
            if self.check_exists(name):
                yield name


class PkgResourcesPackagesAnalysis(_PackagesAnalysisTemplate):
    """
    This class implements package dependencies analysis for python packages.
    """

    def check_exists(self, package_name: str) -> bool:
        """
        This method should True if package exists else False.
        """

        try:
            get_distribution(package_name)
        except DistributionNotFound:
            return False
        else:
            return True

    def get_all(self) -> Iterable[str]:
        """
        The generator yields all installed packages from importlib.
        """

        for package in working_set:
            yield package.project_name

    def get_dependencies(self, package_name: str) -> Iterable[str]:
        """
        This generator yields all installed dependencies
        names for a package name.
        """

        try:
            distribution = get_distribution(package_name)
        except DistributionNotFound:
            return None

        for requirement in distribution.requires():
            yield requirement.project_name


modules = {
    "importlib": ImportlibPackagesAnalysis,
    "pkg_resources": PkgResourcesPackagesAnalysis,
}

if apt_imported:
    modules["apt"] = AptPackagesAnalysis


def main() -> int:
    """
    This function is the main function
    to start the module from command line.
    """

    argv_copy = argv.copy()

    if len(argv) < 2 or argv[1] not in modules:
        print(
            "USAGES:",
            executable,
            argv[0],
            (
                "module ([--count/-c]|[--details/-s]|"
                "[--packages|-p]|[package names, ...])"
            ),
            file=stderr,
        )
        print("Modules:", ", ".join(modules.keys()), file=stderr)
        print("Examples:", file=stderr)
        print("\t", executable, argv[0], "apt -c", file=stderr)
        print("\t", executable, argv[0], "apt --count", file=stderr)
        print("\t", executable, argv[0], "apt -d | grep gnome", file=stderr)
        print(
            "\t",
            executable,
            argv[0],
            "apt --details | grep python3 | awk '{ print $3 }'",
            file=stderr,
        )
        print("\t", executable, argv[0], "apt python3 perl bash", file=stderr)
        return 1

    module = argv_copy.pop(1)
    instance = modules[module]()

    error = 0
    if len(argv_copy) > 1:
        if len(argv_copy) == 2 and (
            argv_copy[1] == "--count" or argv_copy[1] == "-c"
        ):
            instance.print_package_counter(instance.make_statistics())
            return error
        elif len(argv_copy) == 2 and (
            argv_copy[1] == "--details" or argv_copy[1] == "-d"
        ):
            instance.print_line_grepable_details(instance.make_statistics())
            return error
        elif len(argv_copy) == 2 and (
            argv_copy[1] == "--packages" or argv_copy[1] == "-p"
        ):
            for name in instance.get_all():
                print(name)
            return error
        for name in argv_copy[1:]:
            if name not in cache:
                error += 1
                print("[ERROR] package not found:", name, file=stderr)
                continue
            instance.print_dependencies_tree(name)
        return error

    for name in instance.get_all():
        instance.print_deps_tree(name)

    return error


if __name__ == "__main__":
    exit(main())
