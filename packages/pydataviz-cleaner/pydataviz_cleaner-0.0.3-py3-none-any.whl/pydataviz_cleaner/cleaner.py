import pandas as pd

class DataCleaner:
    def __init__(self, df:pd.DataFrame):
        self.df = df

    def drop_missing(self):
        self.df = self.df.dropna()
        return self

    def drop_duplicates(self):
        self.df = self.df.drop_duplicates()
        return self

    def standardize_dates(self, column, fmt="%Y-%m-%d"):
        self.df[column] = pd.to_datetime(self.df[column], errors="coerce").dt.strftime(fmt)
        return self

    def get_df(self):
        return self.df