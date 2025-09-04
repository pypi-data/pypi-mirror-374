import sys
from pathlib import Path


class PathValidator:
    """This class provides methods to validate paths."""

    @staticmethod
    def validate_path(target_path: str) -> Path:
        """Validates the given paths.

        :param target_path: The target path to validate.

        :return: The absolute path for target.
        """

        if target_path is not None:
            target_path = Path(target_path).resolve()
            try:
                target_path.mkdir(parents=True, exist_ok=True)
            except:
                error_message = "ERROR: The path is not a valid path."
                print(error_message, file=sys.stderr)
                sys.exit(0)
            return target_path
        else:
            error_message = "ERROR: Please specify a target path."
            print(error_message, file=sys.stderr)
            sys.exit(0)
