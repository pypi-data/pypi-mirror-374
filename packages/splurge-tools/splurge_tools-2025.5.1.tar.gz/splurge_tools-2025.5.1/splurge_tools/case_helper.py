"""
case_helper.py

A utility module for case conversion operations.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

from splurge_tools.common_utils import safe_string_operation
from splurge_tools.decorators import handle_empty_value, handle_empty_value_classmethod


class CaseHelper:
    """
    A utility class for case conversion operations.

    This class provides methods to:
    - Convert strings to different cases (train, sentence, camel, snake, kebab, pascal)
    - Handle case-insensitive comparisons
    - Normalize string formatting by converting separators to spaces

    All methods support an optional normalize parameter (default: True) that:
    - Converts underscores and hyphens to spaces before processing
    - Ensures consistent handling of mixed input formats
    """

    @staticmethod
    @handle_empty_value
    def normalize(
        value: str,
    ) -> str:
        """
        Normalize a string by converting underscores and hyphens to spaces.
        This ensures consistent handling of mixed input formats.

        Args:
            value: Input string that may contain underscores or hyphens

        Returns:
            String with underscores and hyphens converted to spaces

        Example:
            "hello_world" -> "hello world"
            "hello-world" -> "hello world"
        """
        return value.replace("_", " ").replace("-", " ")

    @classmethod
    @handle_empty_value_classmethod
    def to_train(
        cls,
        value: str,
        *,
        normalize: bool = True,
    ) -> str:
        """
        Convert a string to train case (capitalized words separated by hyphens).

        Args:
            value: Input string to convert
            normalize: If True, converts underscores and hyphens to spaces first (default: True)

        Returns:
            String in train case format

        Example:
            "hello world" -> "Hello-World"
            "hello_world" -> "Hello-World"
        """
        if normalize:
            value = cls.normalize(value)
        return value.title().replace(" ", "-")

    @classmethod
    @handle_empty_value_classmethod
    def to_sentence(
        cls,
        value: str,
        *,
        normalize: bool = True,
    ) -> str:
        """
        Convert a string to sentence case (first word capitalized, rest lowercase).

        Args:
            value: Input string to convert
            normalize: If True, converts underscores and hyphens to spaces first (default: True)

        Returns:
            String in sentence case format

        Example:
            "hello world" -> "Hello world"
            "hello_world" -> "Hello world"
        """
        if normalize:
            value = cls.normalize(value)
        return value.capitalize()

    @classmethod
    @handle_empty_value_classmethod
    def to_camel(
        cls,
        value: str,
        *,
        normalize: bool = True,
    ) -> str:
        """
        Convert a string to camel case (first word lowercase, subsequent words capitalized).

        Args:
            value: Input string to convert
            normalize: If True, converts underscores and hyphens to spaces first (default: True)

        Returns:
            String in camel case format

        Example:
            "hello world" -> "helloWorld"
            "hello_world" -> "helloWorld"
        """
        if normalize:
            value = cls.normalize(value)

        words: list[str] = value.split()
        if not words:
            return ""

        return words[0].lower() + "".join(word.title() for word in words[1:])

    @classmethod
    @handle_empty_value_classmethod
    def to_snake(
        cls,
        value: str,
        *,
        normalize: bool = True,
    ) -> str:
        """
        Convert a string to snake case (all lowercase with underscore separators).

        Args:
            value: Input string to convert
            normalize: If True, converts underscores and hyphens to spaces first (default: True)

        Returns:
            String in snake case format

        Example:
            "hello world" -> "hello_world"
            "hello-world" -> "hello_world"
        """
        if normalize:
            value = cls.normalize(value)
        return value.lower().replace(" ", "_")

    @classmethod
    @handle_empty_value_classmethod
    def to_kebab(
        cls,
        value: str,
        *,
        normalize: bool = True,
    ) -> str:
        """
        Convert a string to kebab case (all lowercase with hyphen separators).

        Args:
            value: Input string to convert
            normalize: If True, converts underscores and hyphens to spaces first (default: True)

        Returns:
            String in kebab case format

        Example:
            "hello world" -> "hello-world"
            "hello_world" -> "hello-world"
        """
        if normalize:
            value = cls.normalize(value)
        return value.lower().replace(" ", "-")

    @classmethod
    @handle_empty_value_classmethod
    def to_pascal(
        cls,
        value: str,
        *,
        normalize: bool = True,
    ) -> str:
        """
        Convert a string to pascal case (all words capitalized, no separators).

        Args:
            value: Input string to convert
            normalize: If True, converts underscores and hyphens to spaces first (default: True)

        Returns:
            String in pascal case format

        Example:
            "hello world" -> "HelloWorld"
            "hello_world" -> "HelloWorld"
        """
        if normalize:
            value = cls.normalize(value)
        return "".join(word.title() for word in value.split())

    @classmethod
    def safe_convert_case(
        cls,
        value: str | None,
        case_type: str,
        *,
        normalize: bool = True,
    ) -> str:
        """
        Safely convert a string to a specific case type with consistent error handling.

        Args:
            value: String value to convert
            case_type: Type of case conversion ('train', 'sentence', 'camel', 'snake', 'kebab', 'pascal')
            normalize: Whether to normalize separators first

        Returns:
            Converted string value

        Raises:
            ValueError: If case_type is not recognized
        """
        case_operations = {
            "train": lambda v: cls.to_train(v, normalize=normalize),
            "sentence": lambda v: cls.to_sentence(v, normalize=normalize),
            "camel": lambda v: cls.to_camel(v, normalize=normalize),
            "snake": lambda v: cls.to_snake(v, normalize=normalize),
            "kebab": lambda v: cls.to_kebab(v, normalize=normalize),
            "pascal": lambda v: cls.to_pascal(v, normalize=normalize),
        }

        if case_type not in case_operations:
            msg = f"Unknown case type: {case_type}"
            raise ValueError(msg)

        return safe_string_operation(value, case_operations[case_type])
