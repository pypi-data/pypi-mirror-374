#!/usr/bin/env python3
"""
OpenAPI Parameter and Response Extractor for Arazzo Runner

This module provides functionality to extract input parameters and output schemas
from an OpenAPI specification for a given API operation.
"""

import copy
import logging
import re
from typing import Any

import jsonpointer

from arazzo_runner.auth.models import SecurityOption
from arazzo_runner.executor.operation_finder import OperationFinder

# Configure logging (using the same logger as operation_finder for consistency)
logger = logging.getLogger("arazzo_runner.extractor")


def _format_security_options_to_dict_list(
    security_options_list: list[SecurityOption],
    operation_info: dict[str, Any],  # For logging context
) -> list[dict[str, list[str]]]:
    """
    Converts a list of SecurityOption objects into a list of dictionaries
    representing OpenAPI security requirements.

    Args:
        security_options_list: The list of SecurityOption objects.
        operation_info: The operation details dictionary for logging context.

    Returns:
        A list of dictionaries, where each dictionary represents an OR security option,
        and its key-value pairs represent ANDed security schemes.
    """
    formatted_requirements = []
    if not security_options_list:
        return formatted_requirements

    for sec_opt in security_options_list:
        current_option_dict = {}
        if sec_opt.requirements:  # Check if the list is not None and not empty
            for sec_req in sec_opt.requirements:
                try:
                    current_option_dict[sec_req.scheme_name] = sec_req.scopes
                except AttributeError as e:
                    op_path = operation_info.get("path", "unknown_path")
                    op_method = operation_info.get("http_method", "unknown_method").upper()
                    logger.warning(
                        f"Missing attributes on SecurityRequirement object for operation {op_method} {op_path}. Error: {e}"
                    )

        # Handle OpenAPI's concept of an empty security requirement object {},
        # (optional authentication), represented by an empty list of requirements.
        if sec_opt.requirements == []:  # Explicitly check for an empty list
            formatted_requirements.append({})
        elif current_option_dict:  # Add if populated from non-empty requirements
            formatted_requirements.append(current_option_dict)

    return formatted_requirements


def _schema_brief(schema: Any) -> str:
    """Return a short, non-recursive description of a schema to keep logs lightweight."""
    try:
        if isinstance(schema, dict):
            if "$ref" in schema and len(schema) == 1:
                return f"$ref({schema['$ref']})"
            t = schema.get("type")
            keys = list(schema.keys())
            return f"dict(type={t}, keys={keys[:6]}{'...' if len(keys)>6 else ''})"
        if isinstance(schema, list):
            return f"list(len={len(schema)})"
        return f"{type(schema).__name__}"
    except Exception:
        return "<unprintable schema>"


def _resolve_ref(spec: dict[str, Any], ref: str) -> dict[str, Any]:
    """
    Resolve a single JSON Pointer ``$ref`` to its target object.

    Scope and behavior:
    - Low-level dereference for any OpenAPI object (Parameter, Response, Schema, etc.).
    - Resolves only the given pointer; it does NOT recursively walk nested structures.
    - Does NOT perform sibling-merge semantics. Sibling merge is schema-specific and
      intentionally omitted here to avoid corrupting non-schema objects.
    - Cycle-safe: if a direct/indirect cycle is detected along the current path, returns
      a placeholder ``{"$ref": ref}`` to break recursion.
    - Uses a small per-call memoization cache to avoid redundant pointer resolution.
    """
    logger.debug(f"Attempting to resolve ref: {ref}")

    # Use function attributes for per-call caches without changing the signature.
    # These are reset on each top-level invocation.
    def _resolve_with_state(
        spec: dict[str, Any], ref: str, stack: set[str], cache: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        # Ensure the ref starts with '#/' as expected for internal refs
        if not ref.startswith("#/"):
            raise ValueError(
                f"Invalid or unsupported $ref format: {ref}. Only internal refs starting with '#/' are supported."
            )

        # Return from cache when available
        if ref in cache:
            return copy.deepcopy(cache[ref])

        # Detect circular references along the current resolution path
        if ref in stack:
            logger.debug(
                f"Circular $ref detected while resolving {ref}. Returning non-expanded $ref to break the cycle."
            )
            # Do not expand further; return the $ref dict as a safe placeholder
            return {"$ref": ref}

        stack.add(ref)
        try:
            resolved_data = jsonpointer.resolve_pointer(spec, ref[1:])

            # If the resolved item is itself a $ref wrapper, resolve it with the same state
            if isinstance(resolved_data, dict) and "$ref" in resolved_data:
                inner_ref = resolved_data["$ref"]
                result = _resolve_with_state(spec, inner_ref, stack, cache)
            else:
                if not isinstance(resolved_data, dict):
                    logger.warning(
                        f"Resolved $ref '{ref}' is not a dictionary, returning empty dict."
                    )
                    result = {}
                else:
                    result = copy.deepcopy(resolved_data)

            # Memoize before returning
            cache[ref] = result
            return copy.deepcopy(result)
        except jsonpointer.JsonPointerException as e:
            logger.error(f"Could not resolve reference '{ref}': {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during $ref resolution for {ref}: {e}")
            raise
        finally:
            # Ensure current ref is popped even on exceptions
            stack.discard(ref)

    try:
        return _resolve_with_state(spec, ref, stack=set(), cache={})
    except ValueError as e:
        logger.error(f"Invalid or unsupported $ref format: {e}")
        raise


def _resolve_schema_refs(
    schema_part: Any,
    full_spec: dict[str, Any],
    visited_refs: set[str] | None = None,
    cache: dict[str, Any] | None = None,
) -> Any:
    """
    Recursively resolve ``$ref`` within a schema fragment with cycle safety and memoization.

    Scope and behavior:
    - Intended only for Schema Objects or schema-like fragments (dict/list trees).
    - Walks dicts and lists recursively, expanding internal ``$ref`` where safe.
    - Cycle-safe: uses a path-level stack to detect cycles and returns a placeholder
      ``{"$ref": path}`` at the cycle boundary (prevents infinite recursion).
    - Memoization cache avoids repeated expansions of the same component.
    - Sibling merge: if a node has ``{"$ref": X, ...siblings}``, merge the referenced
      target with sibling keys, where the referenced target takes precedence on conflicts
      (i.e., siblings only fill in missing keys). This prioritizes structural fidelity
      from the referenced schema over sibling metadata.
    - Combinators (``allOf``, ``oneOf``, ``anyOf``) are preserved structurally; this
      function does not attempt JSON Schema evaluation or flattening—only ref expansion.

    - This is a schema-aware tree walker with schema-specific semantics (sibling merge),
      which would be incorrect for generic OpenAPI objects.
    - Callers that need simple pointer dereference without transformation should use
      ``_resolve_ref`` instead.
    """
    stack = visited_refs if visited_refs is not None else set()
    memo = cache if cache is not None else {}

    # Primitives pass through
    if not isinstance(schema_part, dict | list):
        return schema_part

    if isinstance(schema_part, dict):
        if "$ref" in schema_part:
            ref = schema_part["$ref"]
            if ref in memo:
                result = memo[ref]
            else:
                if ref in stack:
                    logger.debug(
                        f"Circular reference detected for '{ref}'. Returning $ref placeholder."
                    )
                    return {"$ref": ref}
                stack.add(ref)
                try:
                    target = jsonpointer.resolve_pointer(full_spec, ref[1:])
                    if not isinstance(target, dict | list):
                        logger.warning(
                            f"Resolved $ref '{ref}' is not a dict/list. Returning empty dict."
                        )
                        result = {}
                    else:
                        # Provisional entry breaks indirect cycles
                        memo[ref] = {"$ref": ref}
                        result = _resolve_schema_refs(target, full_spec, stack, memo)
                        memo[ref] = result
                except (jsonpointer.JsonPointerException, ValueError, KeyError) as e:
                    logger.warning(f"Could not resolve nested $ref '{ref}': {e}")
                    result = {"$ref": ref}
                finally:
                    stack.discard(ref)

            # Merge siblings (referenced target takes precedence) if any
            siblings = {k: v for k, v in schema_part.items() if k != "$ref"}
            if siblings and isinstance(result, dict):
                # Resolve sibling values first
                resolved_siblings: dict[str, Any] = {}
                for k, v in siblings.items():
                    resolved_siblings[k] = _resolve_schema_refs(v, full_spec, stack, memo)
                # Start from siblings, then overlay result so result wins on conflicts
                merged: dict[str, Any] = dict(resolved_siblings)
                for k, v in result.items():
                    merged[k] = v
                return merged
            return result

        # Regular dict: resolve entries
        return {k: _resolve_schema_refs(v, full_spec, stack, memo) for k, v in schema_part.items()}

    # List: resolve items
    return [_resolve_schema_refs(item, full_spec, stack, memo) for item in schema_part]


def extract_operation_io(
    spec: dict[str, Any],
    http_path: str,
    http_method: str,
    input_max_depth: int | None = None,
    output_max_depth: int | None = None,
) -> dict[str, dict[str, Any]]:
    """
    Finds the specified operation within the spec and extracts input parameters
    structured as an OpenAPI object schema and the full schema for the success
    (200 or 201) response.

    Args:
        spec: The full OpenAPI specification dictionary.
        http_path: The HTTP path of the target operation (e.g., '/users/{id}').
        http_method: The HTTP method of the target operation (e.g., 'get', 'post').
        input_max_depth: If set, limits the depth of the input structure.
        output_max_depth: If set, limits the depth of the output structure.

    Returns:
        A dictionary containing 'inputs', 'outputs', and 'security_requirements'.
        Returns the full, unsimplified dict structure if both max depth arguments are None.
        'inputs' is structured like an OpenAPI schema object:
            {'type': 'object', 'properties': {param_name: {param_schema_or_simple_type}, ...}}
            Non-body params map to {'type': openapi_type_string}.
            The JSON request body schema is included under the 'body' key if present.
        'outputs' contains the full resolved schema for the 200 JSON response.
        'security_requirements' contains the security requirements for the operation.

        Example:
        {
            "inputs": {
                "type": "object",
                "properties": {
                    "userId": {"type": "integer"},   # Non-body param
                    "limit": {"type": "integer"},
                    "body": {                     # Full resolved schema for JSON request body
                        "type": "object",
                        "properties": {
                            "items": {"type": "array", "items": {"type": "string"}},
                            "customer_notes": {"type": "string"}
                        },
                        "required": ["items"]
                    }
                }
            },
            "outputs": { # Full resolved schema for 200 JSON response
                 "type": "object",
                 "properties": {
                      "id": {"type": "string", "format": "uuid"},
                      "status": {"type": "string", "enum": ["pending", "shipped"]}
                 }
            },
            "security_requirements": [
                # List of SecurityOption objects
            ]
        }
    """
    # Find the operation first using OperationFinder
    # Wrap the spec for OperationFinder
    source_name = spec.get("info", {}).get("title", "default_spec")
    source_descriptions = {source_name: spec}
    finder = OperationFinder(source_descriptions)
    operation_info = finder.find_by_http_path_and_method(http_path, http_method.lower())

    if not operation_info:
        logger.warning(f"Operation {http_method.upper()} {http_path} not found in the spec.")
        # Return early if operation not found
        return {"inputs": {}, "outputs": {}, "security_requirements": []}

    # Initialize with new structure for inputs
    extracted_details: dict[str, Any] = {
        "inputs": {"type": "object", "properties": {}, "required": []},
        "outputs": {},
        "security_requirements": [],
    }
    operation = operation_info.get("operation")
    if not operation or not isinstance(operation, dict):
        logger.warning("Operation object missing or invalid in operation_info.")
        return extracted_details

    # Extract security requirements using OperationFinder
    security_options_list: list[SecurityOption] = finder.extract_security_requirements(
        operation_info
    )

    extracted_details["security_requirements"] = _format_security_options_to_dict_list(
        security_options_list, operation_info
    )

    all_parameters = []
    seen_params = set()

    # Check for path-level parameters first
    path_item_ref = f"#/paths/{operation_info.get('path', '').lstrip('/')}"
    try:
        escaped_path = (
            operation_info.get("path", "").lstrip("/").replace("~", "~0").replace("/", "~1")
        )
        path_item_ref = f"#/paths/{escaped_path}"
        path_item = jsonpointer.resolve_pointer(spec, path_item_ref[1:])
        if path_item and isinstance(path_item, dict) and "parameters" in path_item:
            for param in path_item["parameters"]:
                try:
                    resolved_param = param
                    if "$ref" in param:
                        resolved_param = _resolve_ref(spec, param["$ref"])
                    param_key = (resolved_param.get("name"), resolved_param.get("in"))
                    if param_key not in seen_params:
                        all_parameters.append(resolved_param)
                        seen_params.add(param_key)
                except (jsonpointer.JsonPointerException, ValueError, KeyError) as e:
                    logger.warning(
                        f"Skipping path-level parameter due to resolution/format error: {e}"
                    )
    except jsonpointer.JsonPointerException:
        logger.debug(f"Could not find or resolve path item: {path_item_ref}")

    # Add/override with operation-level parameters
    if "parameters" in operation:
        for param in operation["parameters"]:
            try:
                resolved_param = param
                if "$ref" in param:
                    resolved_param = _resolve_ref(spec, param["$ref"])
                param_key = (resolved_param.get("name"), resolved_param.get("in"))
                existing_index = next(
                    (
                        i
                        for i, p in enumerate(all_parameters)
                        if (p.get("name"), p.get("in")) == param_key
                    ),
                    None,
                )
                if existing_index is not None:
                    all_parameters[existing_index] = resolved_param
                elif param_key not in seen_params:
                    all_parameters.append(resolved_param)
                    seen_params.add(param_key)
            except (jsonpointer.JsonPointerException, ValueError, KeyError) as e:
                logger.warning(
                    f"Skipping operation-level parameter due to resolution/format error: {e}"
                )

    # --- Ensure all URL path parameters are present and required ---
    # Find all {param} in the http_path
    url_param_names = re.findall(r"{([^}/]+)}", http_path)
    for url_param in url_param_names:
        param_key = (url_param, "path")
        if param_key not in seen_params:
            all_parameters.append(
                {"name": url_param, "in": "path", "required": True, "schema": {"type": "string"}}
            )
            seen_params.add(param_key)
    # --- End ensure URL params ---

    # Process collected parameters into simplified inputs
    for param in all_parameters:
        param_name = param.get("name")
        param_in = param.get("in")
        param_schema = param.get("schema")
        if param_name and param_in != "body":  # Body handled separately
            if not param_schema:
                logger.warning(
                    f"Parameter '{param_name}' in '{param_in}' is missing schema, mapping type to 'any'"
                )
            else:
                # Resolve schema ref if present
                if isinstance(param_schema, dict) and "$ref" in param_schema:
                    # Defer full resolution to _resolve_schema_refs to properly handle cycles
                    try:
                        param_schema = _resolve_schema_refs(param_schema, spec)
                    except Exception as ref_e:
                        logger.warning(
                            f"Could not resolve schema $ref for parameter '{param_name}': {ref_e}"
                        )
                        param_schema = {}  # Fallback to empty schema
            openapi_type = "string"  # Default OpenAPI type
            if isinstance(param_schema, dict):
                oapi_type_from_schema = param_schema.get("type")
                # Map to basic OpenAPI types
                if oapi_type_from_schema in [
                    "string",
                    "integer",
                    "number",
                    "boolean",
                    "array",
                    "object",
                ]:
                    openapi_type = oapi_type_from_schema
                # TODO: More nuanced mapping (e.g., number format to float/double?)?

            # Add to properties as { 'type': 'openapi_type_string' }
            # Required status will be tracked in the top-level 'required' list
            is_required = param.get("required", False)  # Default to false if not present
            param_input = {"type": openapi_type, "schema": param_schema or {}}
            # Add description if it exists
            param_description = param.get("description")
            if param_description:
                param_input["description"] = param_description
            extracted_details["inputs"]["properties"][param_name] = param_input
            if is_required:
                # Add to top-level required list if not already present
                if param_name not in extracted_details["inputs"]["required"]:
                    extracted_details["inputs"]["required"].append(param_name)

    # Process Request Body for inputs
    if "requestBody" in operation:
        try:
            request_body = operation["requestBody"]
            if "$ref" in request_body:
                # Resolve requestBody schema using cycle-safe resolver.
                try:
                    request_body = _resolve_schema_refs(request_body, spec)
                except Exception as e:
                    # Continue with execution even if schema could not be fully resolved
                    logger.warning(f"Could not resolve requestBody: {e}")

            # Check for application/json content
            json_content = request_body.get("content", {}).get("application/json", {})
            body_schema = json_content.get("schema")

            if body_schema:
                # Let the recursive resolver handle any $ref and cycles

                # Recursively resolve nested refs within the body schema
                fully_resolved_body_schema = _resolve_schema_refs(body_schema, spec)

                # --- Flatten body properties into inputs ---
                if (
                    isinstance(fully_resolved_body_schema, dict)
                    and fully_resolved_body_schema.get("type") == "object"
                ):
                    body_properties = fully_resolved_body_schema.get("properties", {})
                    for prop_name, prop_schema in body_properties.items():
                        if prop_name in extracted_details["inputs"]["properties"]:
                            # Handle potential name collisions (e.g., param 'id' and body field 'id')
                            # Current approach: Body property overwrites if name collides. Log warning.
                            logger.warning(
                                f"Body property '{prop_name}' overwrites existing parameter with the same name."
                            )
                        extracted_details["inputs"]["properties"][prop_name] = prop_schema

                    # Add required body properties to the main 'required' list
                    body_required = fully_resolved_body_schema.get("required", [])
                    for req_prop_name in body_required:
                        if req_prop_name not in extracted_details["inputs"]["required"]:
                            extracted_details["inputs"]["required"].append(req_prop_name)
                else:
                    # If body is not an object (e.g., array, primitive) or has no properties, don't flatten.
                    # Log a warning as we are not adding it under 'body' key either per the requirement.
                    logger.warning(
                        f"Request body for {http_method.upper()} {http_path} is not an object with properties. Skipping flattening."
                    )
                # --- End flatten ---

                # Removed code that added the schema under 'body'
                # Removed code that checked 'required' on the nested 'body' object

        except (jsonpointer.JsonPointerException, ValueError, KeyError) as e:
            logger.warning(f"Skipping request body processing due to error: {e}")

    # Process 200 or 201 Response for outputs
    if "responses" in operation:
        responses = operation.get("responses", {})
        # Prioritize 200, fallback to 201 for success output schema
        success_response = responses.get("200") or responses.get("201")
        if success_response:
            try:
                resolved_response = success_response
                if isinstance(success_response, dict) and "$ref" in success_response:
                    # Resolve response object safely with schema resolver
                    resolved_response = _resolve_schema_refs(success_response, spec)

                # Check for application/json content in the resolved successful response
                json_content = resolved_response.get("content", {}).get("application/json", {})
                response_schema = json_content.get("schema")

                if response_schema:
                    # Recursively resolve nested refs within the response schema
                    logger.debug(
                        f"Output schema BEFORE recursive resolve: {_schema_brief(response_schema)}"
                    )
                    fully_resolved_output_schema = _resolve_schema_refs(response_schema, spec)
                    logger.debug(
                        f"Output schema AFTER recursive resolve: {_schema_brief(fully_resolved_output_schema)}"
                    )
                    extracted_details["outputs"] = fully_resolved_output_schema

            except (jsonpointer.JsonPointerException, ValueError, KeyError) as e:
                logger.warning(f"Skipping success response processing due to error: {e}")
        else:
            logger.debug("No '200' or '201' response found for this operation.")

    # --- Limit output depth (conditionally) ---
    if input_max_depth is not None:
        if isinstance(extracted_details.get("inputs"), dict | list):
            extracted_details["inputs"] = _limit_dict_depth(
                extracted_details["inputs"], input_max_depth
            )
    if output_max_depth is not None:
        if isinstance(extracted_details.get("outputs"), dict | list):
            extracted_details["outputs"] = _limit_dict_depth(
                extracted_details["outputs"], output_max_depth
            )

    # If both max depths are None, return the full, unsimplified details
    return extracted_details


def _limit_dict_depth(
    data: dict | list | Any, max_depth: int, current_depth: int = 0
) -> dict | list | Any:
    """Recursively limits the depth of a dictionary or list structure."""

    if isinstance(data, dict):
        if current_depth >= max_depth:
            return data.get("type", "object")  # Limit hit for dict
        else:
            # Recurse into dict
            limited_dict = {}
            for key, value in data.items():
                # Special case to preserve enum lists
                if key == "enum" and isinstance(value, list):
                    limited_dict[key] = value
                else:
                    limited_dict[key] = _limit_dict_depth(value, max_depth, current_depth + 1)
            return limited_dict
    elif isinstance(data, list):
        if current_depth >= max_depth:
            return "array"  # Limit hit for list
        else:
            # Recurse into list
            limited_list = []
            for item in data:
                limited_list.append(_limit_dict_depth(item, max_depth, current_depth + 1))
            return limited_list
    else:
        # It's a primitive, return the value itself regardless of depth
        return data
