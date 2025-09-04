"""Module for Jira search operations."""

import logging
import re

import requests
from requests.exceptions import HTTPError

from ..exceptions import MCPAtlassianAuthenticationError
from ..models.jira import JiraSearchResult
from .client import JiraClient
from .constants import DEFAULT_READ_JIRA_FIELDS
from .protocols import IssueOperationsProto

logger = logging.getLogger("mcp-jira")


def normalize_jql_for_cloud(jql: str) -> str:
    """
    Normalize JQL to work better with Jira Cloud API v3.
    
    Args:
        jql: Original JQL query
        
    Returns:
        Normalized JQL query
    """
    # Replace accountId('id') with direct accountId assignment
    # accountId('5d94e6fe6110c10ddb7a0435') -> '5d94e6fe6110c10ddb7a0435'
    pattern = r"accountId\('([^']+)'\)"
    normalized = re.sub(pattern, r"'\1'", jql)
    
    # Replace 'assignee in (accountId(...))' with 'assignee = accountId'
    pattern2 = r"assignee\s+in\s+\(([^)]+)\)"
    normalized = re.sub(pattern2, r"assignee = \1", normalized)
    
    logger.debug(f"JQL normalization: '{jql}' -> '{normalized}'")
    return normalized


def generate_jql_fallbacks(original_jql: str, account_id: str | None = None) -> list[str]:
    """
    Generate fallback JQL queries when the original fails.
    
    Args:
        original_jql: The original JQL that failed
        account_id: The account ID to use in fallbacks
        
    Returns:
        List of fallback JQL queries to try
    """
    fallbacks = []
    
    # Try normalized version first
    normalized = normalize_jql_for_cloud(original_jql)
    if normalized != original_jql:
        fallbacks.append(normalized)
    
    # If we have account_id, try some common variants
    if account_id:
        # Simple assignee with account ID
        if "assignee" in original_jql.lower():
            simple_assignee = f"assignee = '{account_id}'"
            if "statusCategory" in original_jql:
                simple_assignee += " AND statusCategory != Done"
            if "ORDER BY" in original_jql:
                simple_assignee += " ORDER BY updated DESC"
            fallbacks.append(simple_assignee)
        
        # Use currentUser() instead
        current_user_jql = original_jql.replace(f"assignee = '{account_id}'", "assignee = currentUser()")
        if current_user_jql != original_jql:
            fallbacks.append(current_user_jql)
    
    return fallbacks


class SearchMixin(JiraClient, IssueOperationsProto):
    """Mixin for Jira search operations."""

    def search_issues(
        self,
        jql: str,
        fields: list[str] | tuple[str, ...] | set[str] | str | None = None,
        start: int = 0,
        limit: int = 50,
        expand: str | None = None,
        projects_filter: str | None = None,
    ) -> JiraSearchResult:
        """
        Search for issues using JQL (Jira Query Language).

        Args:
            jql: JQL query string
            fields: Fields to return (comma-separated string, list, tuple, set, or "*all")
            start: Starting index if number of issues is greater than the limit
                  Note: This parameter is ignored in Cloud environments and results will always
                  start from the first page.
            limit: Maximum issues to return
            expand: Optional items to expand (comma-separated)
            projects_filter: Optional comma-separated list of project keys to filter by, overrides config

        Returns:
            JiraSearchResult object containing issues and metadata (total, start_at, max_results)

        Raises:
            MCPAtlassianAuthenticationError: If authentication fails with the Jira API (401/403)
            Exception: If there is an error searching for issues
        """
        try:
            # Use projects_filter parameter if provided, otherwise fall back to config
            filter_to_use = projects_filter or self.config.projects_filter

            # Apply projects filter if present
            if filter_to_use:
                # Split projects filter by commas and handle possible whitespace
                projects = [p.strip() for p in filter_to_use.split(",")]

                # Build the project filter query part
                if len(projects) == 1:
                    project_query = f'project = "{projects[0]}"'
                else:
                    quoted_projects = [f'"{p}"' for p in projects]
                    projects_list = ", ".join(quoted_projects)
                    project_query = f"project IN ({projects_list})"

                # Add the project filter to existing query
                if not jql:
                    # Empty JQL - just use project filter
                    jql = project_query
                elif jql.strip().upper().startswith("ORDER BY"):
                    # JQL starts with ORDER BY - prepend project filter
                    jql = f"{project_query} {jql}"
                elif "project = " not in jql and "project IN" not in jql:
                    # Only add if not already filtering by project
                    jql = f"({jql}) AND {project_query}"

                logger.info(f"Applied projects filter to query: {jql}")

            # Normalize JQL for better Jira Cloud compatibility
            if jql:
                original_jql = jql
                jql = normalize_jql_for_cloud(jql)
                if jql != original_jql:
                    logger.info(f"Normalized JQL: {original_jql} -> {jql}")

            # Convert fields to proper format if it's a list/tuple/set
            fields_param: str | None
            if fields is None:  # Use default if None
                fields_param = ",".join(DEFAULT_READ_JIRA_FIELDS)
            elif isinstance(fields, list | tuple | set):
                fields_param = ",".join(fields)
            else:
                fields_param = fields

            if self.config.is_cloud:
                actual_total = -1
                try:
                    # Call 1: Get metadata (including total) using standard search API
                    metadata_params = {"jql": jql, "maxResults": 0}
                    metadata_response = self.jira.get(
                        self.jira.resource_url("search"), params=metadata_params
                    )

                    if (
                        isinstance(metadata_response, dict)
                        and "total" in metadata_response
                    ):
                        try:
                            actual_total = int(metadata_response["total"])
                        except (ValueError, TypeError):
                            logger.warning(
                                f"Could not parse 'total' from metadata response for JQL: {jql}. Received: {metadata_response.get('total')}"
                            )
                    else:
                        logger.warning(
                            f"Could not retrieve total count from metadata response for JQL: {jql}. Response type: {type(metadata_response)}"
                        )
                except Exception as meta_err:
                    logger.error(
                        f"Error fetching metadata for JQL '{jql}': {str(meta_err)}"
                    )

                # Call 2: Get the actual issues using the enhanced method
                issues_response_list = self.jira.enhanced_jql_get_list_of_tickets(
                    jql, fields=fields_param, limit=limit, expand=expand
                )

                if not isinstance(issues_response_list, list):
                    msg = f"Unexpected return value type from `jira.enhanced_jql_get_list_of_tickets`: {type(issues_response_list)}"
                    logger.error(msg)
                    raise TypeError(msg)

                response_dict_for_model = {
                    "issues": issues_response_list,
                    "total": actual_total,
                }

                search_result = JiraSearchResult.from_api_response(
                    response_dict_for_model,
                    base_url=self.config.url,
                    requested_fields=fields_param,
                )

                # Return the full search result object
                return search_result
            else:
                limit = min(limit, 50)
                
                # Normalize JQL for better Jira Cloud compatibility
                normalized_jql = normalize_jql_for_cloud(jql)
                logger.debug(f"Original JQL: {jql}")
                logger.debug(f"Normalized JQL: {normalized_jql}")
                
                # Use API v3 search endpoint directly
                params = {
                    "jql": normalized_jql,  # Use normalized JQL
                    "startAt": start,
                    "maxResults": limit,
                    "fields": fields_param,
                }
                if expand:
                    params["expand"] = expand
                
                logger.debug(f"JQL search params: {params}")
                response = self.jira.get("/rest/api/3/search", params=params)
                logger.debug(f"JQL search response type: {type(response)}")
                logger.debug(f"JQL search response keys: {list(response.keys()) if isinstance(response, dict) else 'N/A'}")
                if isinstance(response, dict):
                    logger.debug(f"Response total: {response.get('total')}, startAt: {response.get('startAt')}, maxResults: {response.get('maxResults')}")
                    logger.debug(f"Issues count in response: {len(response.get('issues', []))}")
                
                if not isinstance(response, dict):
                    msg = f"Unexpected return value type from JQL search API: {type(response)}"
                    logger.error(msg)
                    raise TypeError(msg)

                # Convert the response to a search result model
                search_result = JiraSearchResult.from_api_response(
                    response, base_url=self.config.url, requested_fields=fields_param
                )

                # Return the full search result object
                return search_result

        except HTTPError as http_err:
            logger.error(f"HTTP error during JQL search: {http_err}")
            if http_err.response is not None:
                logger.error(f"Response status: {http_err.response.status_code}")
                logger.error(f"Response content: {http_err.response.text}")
                
                if http_err.response.status_code in [401, 403]:
                    error_msg = (
                        f"Authentication failed for Jira API ({http_err.response.status_code}). "
                        "Token may be expired or invalid. Please verify credentials."
                    )
                    logger.error(error_msg)
                    raise MCPAtlassianAuthenticationError(error_msg) from http_err
                elif http_err.response.status_code == 400:
                    error_msg = f"Bad request - possibly invalid JQL: {jql}"
                    logger.error(error_msg)
                    raise Exception(error_msg) from http_err
            else:
                logger.error(f"HTTP error during API call: {http_err}", exc_info=False)
                raise http_err
        except Exception as e:
            logger.error(f"Error searching issues with JQL '{jql}': {str(e)}")
            raise Exception(f"Error searching issues: {str(e)}") from e

    def get_board_issues(
        self,
        board_id: str,
        jql: str,
        fields: str | None = None,
        start: int = 0,
        limit: int = 50,
        expand: str | None = None,
    ) -> JiraSearchResult:
        """
        Get all issues linked to a specific board.

        Args:
            board_id: The ID of the board
            jql: JQL query string
            fields: Fields to return (comma-separated string or "*all")
            start: Starting index
            limit: Maximum issues to return
            expand: Optional items to expand (comma-separated)

        Returns:
            JiraSearchResult object containing board issues and metadata

        Raises:
            Exception: If there is an error getting board issues
        """
        try:
            # Determine fields_param
            fields_param = fields
            if fields_param is None:
                fields_param = ",".join(DEFAULT_READ_JIRA_FIELDS)

            # Use direct API v3 call instead of library method
            params = {
                "jql": jql,
                "fields": fields_param,
                "startAt": start,
                "maxResults": limit,
            }
            if expand:
                params["expand"] = expand
            
            response = self.jira.get(f"/rest/agile/1.0/board/{board_id}/issue", params=params)
            if not isinstance(response, dict):
                msg = f"Unexpected return value type from board issues API: {type(response)}"
                logger.error(msg)
                raise TypeError(msg)

            # Convert the response to a search result model
            search_result = JiraSearchResult.from_api_response(
                response, base_url=self.config.url, requested_fields=fields_param
            )
            return search_result
        except requests.HTTPError as e:
            logger.error(
                f"Error searching issues for board with JQL '{board_id}': {str(e.response.content)}"
            )
            raise Exception(
                f"Error searching issues for board with JQL: {str(e.response.content)}"
            ) from e
        except Exception as e:
            logger.error(f"Error searching issues for board with JQL '{jql}': {str(e)}")
            raise Exception(
                f"Error searching issues for board with JQL {str(e)}"
            ) from e

    def get_sprint_issues(
        self,
        sprint_id: str,
        fields: str | None = None,
        start: int = 0,
        limit: int = 50,
    ) -> JiraSearchResult:
        """
        Get all issues linked to a specific sprint.

        Args:
            sprint_id: The ID of the sprint
            fields: Fields to return (comma-separated string or "*all")
            start: Starting index
            limit: Maximum issues to return

        Returns:
            JiraSearchResult object containing sprint issues and metadata

        Raises:
            Exception: If there is an error getting board issues
        """
        try:
            # Determine fields_param
            fields_param = fields
            if fields_param is None:
                fields_param = ",".join(DEFAULT_READ_JIRA_FIELDS)

            # Use direct API call instead of library method
            params = {
                "startAt": start,
                "maxResults": limit,
            }
            
            response = self.jira.get(f"/rest/agile/1.0/sprint/{sprint_id}/issue", params=params)
            if not isinstance(response, dict):
                msg = f"Unexpected return value type from sprint issues API: {type(response)}"
                logger.error(msg)
                raise TypeError(msg)

            # Convert the response to a search result model
            search_result = JiraSearchResult.from_api_response(
                response, base_url=self.config.url, requested_fields=fields_param
            )
            return search_result
        except requests.HTTPError as e:
            logger.error(
                f"Error searching issues for sprint '{sprint_id}': {str(e.response.content)}"
            )
            raise Exception(
                f"Error searching issues for sprint: {str(e.response.content)}"
            ) from e
        except Exception as e:
            logger.error(f"Error searching issues for sprint: {sprint_id}': {str(e)}")
            raise Exception(f"Error searching issues for sprint: {str(e)}") from e
