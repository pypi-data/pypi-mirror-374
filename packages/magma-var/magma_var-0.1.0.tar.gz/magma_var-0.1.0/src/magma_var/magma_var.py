import os
from datetime import datetime

from magma_var.utils import check_directory


class MagmaVar:
    def __init__(
        self,
        volcano_code: str,
        start_date: str,
        end_date: str,
        current_dir: str = None,
        locale: str = "id",
        verbose: bool = False,
        debug: bool = False,
    ):
        self.volcano_code = volcano_code.upper()
        self.start_date = start_date
        self.end_date = end_date
        self.locale = locale

        if current_dir is None:
            current_dir = os.getcwd()
        self.current_dir = current_dir

        self._validate()

        self.output_dir, self.figures_dir, self.magma_dir = check_directory(current_dir)
        self.magma_dir = os.path.join(self.magma_dir, "var")
        os.makedirs(self.magma_dir, exist_ok=True)

        self.json_dir: str = os.path.join(self.magma_dir, "json")

        self.filename = f"{self.volcano_code}_{self.start_date}_{self.end_date}"

        self.verbose = verbose
        self.debug = debug

    def _validate(self) -> None:
        """Validating parameters.

        Returns:
            None

        Raises:
            ValueError: If parameters are invalid.
            IsADirectoryError: If directory does not exist.
        """
        assert datetime.fromisoformat(self.start_date), ValueError(
            "❌ Start date must be in ISO 8601 format (YYYY-MM-DD)"
        )

        assert datetime.fromisoformat(self.end_date), ValueError(
            "❌ End date must be in ISO 8601 format (YYYY-MM-DD)"
        )

        assert datetime.fromisoformat(self.start_date) <= datetime.fromisoformat(
            self.end_date
        ), ValueError("❌ Start date must be before end date")

        assert self.locale in ["id", "en"], ValueError(
            f"❌ Locale must be 'id' or 'en'"
        )

        assert os.path.isdir(self.current_dir), IsADirectoryError(
            f"❌ Current directory: {self.current_dir} is not a directory"
        )
