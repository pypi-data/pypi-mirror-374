"""MCP tools for PyPI package queries.

This package contains the FastMCP tool implementations that provide
the user-facing interface for PyPI package operations.
"""

from .compatibility_check import (
    check_python_compatibility,
    get_compatible_python_versions,
    suggest_python_version_for_packages,
)
from .dependency_resolver import resolve_package_dependencies
from .download_stats import (
    get_package_download_stats,
    get_package_download_trends,
    get_top_packages_by_downloads,
)
from .package_downloader import download_package_with_dependencies
from .package_query import (
    query_package_dependencies,
    query_package_info,
    query_package_versions,
)
from .publishing import (
    check_pypi_credentials,
    delete_pypi_release,
    get_pypi_account_info,
    get_pypi_upload_history,
    manage_pypi_maintainers,
    upload_package_to_pypi,
)
from .metadata import (
    manage_package_keywords,
    manage_package_urls,
    set_package_visibility,
    update_package_metadata,
)
from .analytics import (
    analyze_pypi_competition,
    get_pypi_package_analytics,
    get_pypi_package_rankings,
    get_pypi_security_alerts,
)
from .discovery import (
    get_pypi_package_recommendations,
    get_pypi_trending_today,
    monitor_pypi_new_releases,
    search_pypi_by_maintainer,
)
from .workflow import (
    check_pypi_upload_requirements,
    get_pypi_build_logs,
    preview_pypi_package_page,
    validate_pypi_package_name,
)
from .community import (
    get_pypi_package_reviews,
    manage_pypi_package_discussions,
    get_pypi_maintainer_contacts,
)
from .search import (
    find_alternatives,
    get_trending_packages,
    search_by_category,
    search_packages,
)
from .security_tools import (
    bulk_scan_package_security,
    scan_pypi_package_security,
)
from .license_tools import (
    analyze_pypi_package_license,
    check_bulk_license_compliance,
)
from .health_tools import (
    assess_package_health_score,
    compare_packages_health_scores,
)
from .requirements_tools import (
    analyze_requirements_file_tool,
    compare_multiple_requirements_files,
)

__all__ = [
    # Core package tools
    "query_package_info",
    "query_package_versions",
    "query_package_dependencies",
    "check_python_compatibility",
    "get_compatible_python_versions",
    "suggest_python_version_for_packages",
    "resolve_package_dependencies",
    "download_package_with_dependencies",
    "get_package_download_stats",
    "get_package_download_trends",
    "get_top_packages_by_downloads",
    # Search tools
    "search_packages",
    "search_by_category",
    "find_alternatives",
    "get_trending_packages",
    # Publishing tools
    "upload_package_to_pypi",
    "check_pypi_credentials",
    "get_pypi_upload_history",
    "delete_pypi_release",
    "manage_pypi_maintainers",
    "get_pypi_account_info",
    # Metadata tools
    "update_package_metadata",
    "manage_package_urls",
    "set_package_visibility",
    "manage_package_keywords",
    # Analytics tools
    "get_pypi_package_analytics",
    "get_pypi_security_alerts",
    "get_pypi_package_rankings",
    "analyze_pypi_competition",
    # Discovery tools
    "monitor_pypi_new_releases",
    "get_pypi_trending_today",
    "search_pypi_by_maintainer",
    "get_pypi_package_recommendations",
    # Workflow tools
    "validate_pypi_package_name",
    "preview_pypi_package_page",
    "check_pypi_upload_requirements",
    "get_pypi_build_logs",
    # Community tools
    "get_pypi_package_reviews",
    "manage_pypi_package_discussions",
    "get_pypi_maintainer_contacts",
    # Security tools
    "scan_pypi_package_security",
    "bulk_scan_package_security",
    # License tools
    "analyze_pypi_package_license",
    "check_bulk_license_compliance",
    # Health tools
    "assess_package_health_score",
    "compare_packages_health_scores",
    # Requirements tools
    "analyze_requirements_file_tool",
    "compare_multiple_requirements_files",
]
