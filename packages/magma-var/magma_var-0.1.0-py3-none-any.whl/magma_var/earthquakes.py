from dataclasses import dataclass
from functools import cached_property
from typing import List, Dict, Optional

import pandas as pd
from magma_var.const import EARTHQUAKE_TYPES


@dataclass
class Earthquake:
    """Earthquake metadata.

    Attributes:
        code (str): Earthquake code
        alias (str): Earthquake alias
        earthquake_id (str): Earthquake name in Indonesia
        earthquake_en (str): Earthquake name in English
        color (str): Earthquake color in hex
        column_name (str): Earthquake column name
    """

    code: str
    alias: str
    earthquake_id: str
    earthquake_en: str
    color: str
    column_name: str


@dataclass
class Earthquakes:
    """List of Earthquake.

    Attributes:
        earthquakes (List[Earthquake]): List of Earthquake class
    """

    earthquakes: List[Earthquake]

    def __iter__(self):
        return iter(self.earthquakes)

    def __len__(self):
        return len(self.earthquakes)

    @property
    def df(self) -> pd.DataFrame:
        """DataFrame representation."""
        return pd.DataFrame(self.earthquakes)

    @property
    def codes(self) -> List[str]:
        """List of Earthquake codes."""
        return self.df["code"].to_list()

    @property
    def colors(self) -> List[str]:
        """List of Earthquake codes."""
        return self.df["color"].to_list()

    def columns(self, locale: Optional[str] = "id") -> Dict[str, str]:
        """List of Earthquake column names.

        Args:
            locale (str, optional): Earthquake column name. Defaults to "id".

        Returns:
            Dict[str, str]: List of Earthquake column names.
        """
        columns = {}
        _dict = self.df[["column_name", f"earthquake_{locale}"]].to_dict("records")
        for row in _dict:
            columns[row["column_name"]] = row[f"earthquake_{locale}"]
        return columns

    def where(self, attribute: str, value: str) -> Earthquake | None:
        """Query earthquake by attribute and value.

        Args:
            attribute (str): Earthquake attribute
            value (str): Earthquake value

        Returns:
            Earthquake | None: Earthquake class if found
        """
        for earthquake in self.earthquakes:
            if getattr(earthquake, attribute) == value:
                return earthquake
        return None


earthquakes: Earthquakes = Earthquakes(
    earthquakes=[Earthquake(**eq) for eq in EARTHQUAKE_TYPES]
)
