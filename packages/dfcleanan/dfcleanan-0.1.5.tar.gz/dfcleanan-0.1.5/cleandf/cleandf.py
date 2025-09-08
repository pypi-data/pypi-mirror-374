import pandas as pd


class EmptyDataFrameError(Exception):
    # Error if DataFrame is empty
    pass


# This is a class that cleans a DataFrame of nan data.
class Cleandf:
    def __init__(self):
        pass

    # This error will be returned if the DataFrame is empty.
    def imputer(self , df:pd.DataFrame)-> pd.DataFrame:
        if df.empty:
            raise EmptyDataFrameError('The DataFrame is empty.')

        # If all values ​​in any column in a DataFrame are null values, delete the column.
        only_nan_columns = [col for col in df.columns if df[col].isna().all()]
        if only_nan_columns:
            df = df.drop(columns=only_nan_columns)
        

        # We take the float and integer columns from the DataFrame and fill it with the average value
        integer_column =  df.select_dtypes(include=["int64" , "float64"])
        if not integer_column.empty:
            for col in integer_column:
                if pd.api.types.is_integer_dtype(df[col]):
                    df[col] = df[col].fillna(int(df[col].mean()))
                else:
                    df[col]  = df[col].fillna(df[col].mean())
            

        # Finally, we extract the string columns and fill them with the most frequently occurring data.
        string_column = df.select_dtypes(include=["object"  , "string"])
        if not string_column.empty:
            for col in string_column:
                df[col] = df[col].fillna(df[col].mode()[0])
                
        return df
                
        
            
    
    
    