import json


def raw_transfrom(raw_df, schema_filepath):
    """
    Transform raw data
    - Rename column names
    - Drop NaNs
    - Enforce a schema
    """
    column_names = {c: c.replace(' ', '_') for c in raw_df.columns}
    df = raw_df.rename(columns=column_names)
    
    df = df.dropna()
    n_discards = (len(df) - len(raw_df)) / len(raw_df)
    print(f"Removed NaN records: {n_discards:.0%}")

    schema = load_json(schema_filepath)
    df = df.astype(schema)

    return df


def load_json(filepath):
    """
    Load json config into Python dictionary.
    """
    with open(filepath, 'r') as f:
        d = json.load(f)

    return d