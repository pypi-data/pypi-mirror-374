from pathlib import Path
from typing import List, Dict, Any, Type, Optional, Tuple

from cerberus import Validator
import yaml


class _Loader(yaml.SafeLoader):
    """A custom `yaml.SafeLoader` that adds support for the `!include` tag."""
    def __init__(self, stream):
        """Initializes the loader and sets the root for relative includes."""
        try:
            self._root = Path(stream.name).parent
        except AttributeError:
            self._root = Path.cwd()
        super().__init__(stream)

def _include_constructor(loader: _Loader, node: yaml.Node) -> Dict:
    """Loads and parses a YAML file specified by an !include tag."""
    include_path = loader._root / Path(loader.construct_scalar(node))
    if not include_path.is_file():
        raise FileNotFoundError(f"Included file '{include_path}' not found.")
    with include_path.open('r', encoding='utf-8') as f:
        return yaml.load(f, Loader=_Loader) or {}

yaml.add_constructor('!include', _include_constructor, Loader=_Loader)


class ConfigLoader:
    """
    A reusable class to load, validate, and provide rich error reporting for YAML files.
    """
    def __init__(
            self, schema: Dict = None,
            custom_rules: Optional[List[Dict]] = None,
            validator_class: Type[Validator] = Validator
    ):
        """Initializes the ConfigLoader."""
        self.schema = schema
        # --- MODIFIED: Validator is now created once, as it should be ---
        self.validator = validator_class(self.schema) if self.schema else None
        self.rules = custom_rules or DEFAULT_TRANSLATION_RULES

    def read(
            self,
            config_file: Path,
            # --- NEW: Add allow_unknown as a direct parameter ---
            allow_unknown: bool = False,
            root_node: str | None = None,
            block_descriptor: str | None = None,
            normalize: bool = False
    ) -> dict:
        """
        Load and validate a YAML configuration file against the schema.

        Args:
            config_file (Path): Path to the YAML configuration file.
            allow_unknown (bool): If True, ignores and allows unrecognized
                keys at the top level of the configuration. Defaults to False.
            # ... (rest of docstring)
        """
        if not isinstance(config_file, Path):
            config_file = Path(config_file)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {Path.cwd()}/{config_file}")

        try:
            with config_file.open("r", encoding="utf-8") as f:
                yml_config = yaml.load(f, Loader=_Loader) or {}

        except yaml.YAMLError as e:
            # ---  uses the unified translation engine ---
            raw_error = str(e)
            problem, suggestion = self._translate_error_message(raw_error)

            error_message = (
                f"   Error: YAML syntax error in '{config_file}':\n"
                f"    {problem}\n"
                f"    {suggestion}\n\n"
                f"    Details:\n{raw_error}"
            )
            raise ValueError(error_message) from e

        if self.validator:
            # --- Set allow_unknown directly for this read operation ---
            self.validator.allow_unknown = allow_unknown

            if not self.validator.validate(yml_config):
                formatted_errors = "\n".join(self._format_yml_errors(
                    self.validator.errors,
                    yml_config,
                    root_node=root_node,
                    block_descriptor=block_descriptor
                ))
                raise ValueError(f"  ❌ Error: Configuration file '{config_file}' has errors:\n{formatted_errors}")

            return self.validator.normalized(yml_config) if normalize else yml_config

        # If no validator, just return the raw config
        return yml_config

    def _format_yml_errors(
            self,
            errors: Dict,
            data: Dict,
            prefix: str = "",
            root_node: str | None = None,
            block_descriptor: str | None = None
    ) -> List[str]:
        messages = []
        for field, issues in errors.items():
            full_path_str = f"{prefix}.{field}" if prefix else str(field)
            full_path_list = full_path_str.split('.')

            if isinstance(issues, list):
                for issue in issues:
                    if isinstance(issue, dict):
                        messages.extend(self._format_yml_errors(
                            issue, data, prefix=full_path_str,
                            root_node=root_node, block_descriptor=block_descriptor
                        ))
                    else:
                        location_messages = []
                        parent_data = None

                        if root_node and block_descriptor and full_path_list[0] == root_node and len(full_path_list) > 1:
                            block_path = full_path_list[:2]
                            block_data = self._get_value_from_path(data, block_path)
                            if isinstance(block_data, dict) and block_descriptor in block_data:
                                descriptor_value = block_data[block_descriptor]
                                location_messages.append(f"In the block with {block_descriptor} '{descriptor_value}'.")

                        if len(full_path_list) > 0:
                            parent_path = full_path_list[:-1]
                            parent_data = self._get_value_from_path(data, parent_path)
                            if isinstance(parent_data, list):
                                error_index = int(full_path_list[-1])
                                last_key = full_path_list[-2] if len(full_path_list) > 1 else 'list'
                                location_messages.append(f"The error is in the {self._format_human_readable_path(full_path_list[-1:])} in the '{last_key}' list.")
                                if error_index > 0:
                                    preceding = parent_data[max(0, error_index - 1):error_index]
                                    if preceding:
                                        location_messages.append(f"It comes right after '{preceding[0]}'.")

                        if not location_messages:
                            location_messages.append(f"The error is in {self._format_human_readable_path(full_path_list)}.")

                        problem, suggestion = self._translate_cerberus_issue(issue, full_path_list, parent_data)
                        found_value = self._get_value_from_path(data, full_path_list)

                        formatted_message = (
                            f"\n    Problem: {problem}"
                            f"\n    Found Value: {repr(found_value)}"
                            f"\n    {' '.join(location_messages)}"
                            f"\n    {suggestion}"
                            f"\n\n    "
                            f"\n      Item: {' / '.join(full_path_list)}"
                            f"\n      {issue}"
                        )
                        messages.append(formatted_message)
        return messages

    def _translate_error_message(self, error_string: str) -> tuple[str, str]:
        """
        Translates a raw error string using the configurable translation rules.
        """
        for rule in self.rules:
            trigger_phrase = rule.get("trigger_phrase", "")
            if trigger_phrase and trigger_phrase in error_string:
                # Found a matching rule.
                return rule["problem"], rule["suggestion"]

        # Generic fallback if no specific rule matched.
        problem = f"An unknown error occurred: {error_string}"
        suggestion = "Please check the file syntax and the documentation."
        return problem, suggestion

    # ---  This is  a thin wrapper ---
    def _translate_cerberus_issue(self, issue: str, path: List[str], parent_data: Any) -> tuple[str, str]:
        """
        Translates a single Cerberus error, enhancing it with contextual info.
        """
        field_name = path[-1] if path else "a setting"

        # Call the unified translator first to get the base message.
        problem, suggestion = self._translate_error_message(issue)

        # Format the base message with the specific field name.
        problem = problem.format(field_name=field_name)
        suggestion = suggestion.format(field_name=field_name)

        # Enhance "unallowed value" errors with specific details from the schema.
        if "unallowed value" in issue:
            schema_rule = self._get_schema_rule_from_path(self.validator.schema, path)
            allowed_values_str = ""
            if schema_rule and 'allowed' in schema_rule:
                allowed_values_str = ", ".join(f"'{v}'" for v in schema_rule['allowed'])

            if allowed_values_str:
                found_value = issue.split("'")[1] if "'" in issue else "an invalid value"
                problem = f"{problem} Expected: {allowed_values_str}. Found: '{found_value}'."

        return problem, suggestion

    def _get_schema_rule_from_path(self, schema: Any, path: List[str]) -> Optional[Dict]:
        """Navigates the schema dictionary using a path list to find a rule."""
        current_schema_item = schema

        # Handle cases where the schema is wrapped in a list. This makes the
        # function robust against this specific formatting issue.
        if isinstance(current_schema_item, list) and len(current_schema_item) > 0:
            current_schema_item = current_schema_item[0]

        for key in path:
            if not hasattr(current_schema_item, 'get'):
                return None  # Cannot traverse further if it's not a dictionary like

            current_schema_item = current_schema_item.get(key)
            if current_schema_item is None:
                return None

            # For list validation, the rule is nested under 'schema'
            if isinstance(current_schema_item, dict) and 'schema' in current_schema_item:
                current_schema_item = current_schema_item['schema']

        return current_schema_item if isinstance(current_schema_item, dict) else None

    @staticmethod
    def _get_value_from_path(data: Any, path: List[str]) -> Any:
        current = data
        for key in path:
            try:
                if isinstance(current, list) and key.isdigit():
                    current = current[int(key)]
                elif isinstance(current, dict):
                    current = current[key]
                else:
                    return None
            except (KeyError, IndexError, TypeError):
                return None
        return current

    @staticmethod
    def _parse_type_error(issue: str) -> tuple[str, str] | None:
        trigger_words = {'must', 'be', 'of', 'type'}
        type_map = {
            'string': ('text', "Ensure the value is text. If using a number or a word like 'yes', surround it with quotes (e.g., 'yes')."),
            'integer': ('an integer', "Use a number without decimals (e.g., 20 or -5)."),
            'float': ('a number', "Use a number. Decimals are allowed (e.g., 20.7)."),
            'number': ('a number', "Use a number. Decimals are allowed (e.g., 20.7)."),
            'boolean': ('a true/false value', "Use one of these values: true, false, yes, no, on, off."),
            'list': ('a list of items', 'Format the value as a list, with each item on a new line preceded by a hyphen (e.g., "- item1").'),
            'dict': ('a collection of key-value settings', "Format the value as a set of 'key: value' pairs.")
        }
        words = set(issue.lower().split())
        if not trigger_words.issubset(words): return None
        for technical_type, (human_name, suggestion) in type_map.items():
            if technical_type in words: return human_name, suggestion
        return None

    def _format_human_readable_path(self, path_list: List[str]) -> str:
        parts = []
        for key in path_list:
            if key.isdigit():
                human_index = int(key) + 1
                parts.append(f"the {self._get_ordinal(human_index)} item")
            else:
                parts.append(f"the '{key}' section")
        if len(parts) > 1: return f"{' in '.join(parts[::-1])}"
        return parts[0] if parts else "the top level"

    @staticmethod
    def _get_ordinal(n):
        if 11 <= (n % 100) <= 13: suffix = 'th'
        else: suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        return str(n) + suffix


DEFAULT_TRANSLATION_RULES = [
    # --- Rules for PyYAML parsing errors ---
    {
        "key": "YAML_QUOTED_SCALAR",
        "trigger_phrase": "while scanning a quoted scalar",
        "problem": "Invalid syntax in quoted text.",
        "suggestion": "Please check for syntax errors inside a string, such as unescaped characters or missing end-quote."
    },
    {
        "key": "YAML_UNEXPECTED_END",
        "trigger_phrase": "unexpected end of stream",
        "problem": "The file ended unexpectedly while parsing a value.",
        "suggestion": "This is often caused by a missing closing quote (' or \") or a misplaced colon (:)."
    },
    # --- Rules for Cerberus validation errors ---
    {
        "key": "CONFIG_TYPE_MISMATCH",
        "field_name": "config_type",
        "trigger_phrase": "unallowed value",
        "problem": "The config_type for this config file is incorrect",
        "suggestion": "Please check your build configuration to ensure the correct file is being passed for this parameter.",
    },
    {
        "key": "REQUIRED_FIELD",
        "trigger_phrase": "required field",
        "problem": "The required setting '{field_name}' is missing.",
        "suggestion": "Please add '{field_name}: <value>' to this section.",
    },
    {
        "key": "NULL_VALUE",
        "trigger_phrase": "null value",
        "problem": "The setting '{field_name}' is empty.",
        "suggestion": "Please add a value for '{field_name}'.",
    },
    {
        "key": "UNKNOWN_FIELD",
        "trigger_phrase": "unknown field",
        "problem": "The setting '{field_name}' is not allowed here.",
        "suggestion": "Please remove it or check for a typo.",
    },
]