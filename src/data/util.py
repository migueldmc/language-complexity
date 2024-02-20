import pandas as pd

book_order = (
    "MAT", "MRK", "LUK", "JHN", "ACT", "ROM", "1CO", "2CO", "GAL",
    "EPH", "PHP", "COL", "1TH", "2TH", "1TI", "2TI", "TIT", "PHM",
    "HEB", "JAS", "1PE", "2PE", "1JN", "2JN", "3JN", "JUD", "REV",
)

book_to_index = { book : i for i, book in enumerate(book_order) }

def language_book_chapter_versicle(col: pd.Series) -> pd.Series:
    to_ret = col.map(book_to_index) if col.name == 'book' else col
    return to_ret

def sort_values(df):
    return df.sort_values(by=['language', 'book', 'chapter', 'versicle_number'], key=language_book_chapter_versicle)

def by_field(df, field):
    df = sort_values(df)
    to_ret = {
        k : df[df[field] == k].drop(field, axis=1).reset_index(drop=True)
        for k in df[field].unique()
    }
    return to_ret

def lcm(df):
    langs = by_field(df, 'language')
    idxs = []
    for lang, ldf in langs.items():
        idxs.append(ldf)
    cols = ['book', 'chapter', 'versicle_number']
    v = idxs.pop().loc[:, cols]
    while idxs:
        v = v.merge(idxs.pop(), how='inner', on=cols).loc[:, cols]
    return v

def lcm_with_cut(df, cut):
    cols = ['book', 'chapter', 'versicle_number']
    all_verses = df.loc[:, cols].drop_duplicates(ignore_index=True)
    return all_verses
