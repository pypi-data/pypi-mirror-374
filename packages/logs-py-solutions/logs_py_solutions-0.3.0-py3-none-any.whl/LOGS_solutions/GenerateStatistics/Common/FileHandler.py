import re


class FileHandler:
    """A class to handle file operations.

    The class provides methods to prepare a name as a file name.
    """

    @staticmethod
    def clean_filename(name: str) -> str:
        """Prepare the name as a file name. Remove unwanted special characters
        and replace a space with _.

        :param name: The name to be used as the file name.
        :return: The prepared filename.
        """

        pattern_unwanted_chars = r'[\[\]()/\t\\:*?"<>|,+\x00-\x1F]'
        filename = re.sub(pattern_unwanted_chars, "", name)
        pattern_replace = r"[\s-]"
        return re.sub(pattern_replace, "_", filename)

    @staticmethod
    def clean_csv_text(name):
        pattern_unwanted_chars = r"[\n\r\t\x00-\x1F]"
        cleaned_name = re.sub(pattern_unwanted_chars, "", name)
        cleaned_name = cleaned_name.replace('"', '""')

        return cleaned_name
