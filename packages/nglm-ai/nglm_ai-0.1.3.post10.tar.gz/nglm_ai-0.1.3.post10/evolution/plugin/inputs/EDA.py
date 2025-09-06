from abc import abstractmethod, ABC
from pandas import DataFrame

class EDA(ABC):

    def load_data(self, df: DataFrame):
        self.df = df.copy()

    @abstractmethod
    def standardize_categories(self) -> DataFrame:
        mappings = {
            'PreferredLoginDevice': {'Phone': 'Mobile Phone'},
            'PreferredPaymentMode': {'Cash on Delivery': 'COD'},
            'PreferedOrderCat': {'Mobile': 'Mobile Phone'}
        }
        for column, replacement_map in mappings.items():
            if column in self.df.columns:
                self.df[column] = self.df[column].replace(replacement_map)
                # logging.info(f"Cleaned column: '{column}'")
            else:
                print(f"Column '{column}' not found in DataFrame. Skipping.")
        print("Category standardization complete.")
        return self.df

