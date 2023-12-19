import unicode.category as cat

from languages import WALS_LANG_CODES
from table import ExcelLoader, Key, Table

def all_but_language(lang):
    return WALS_LANG_CODES.keys() - lang

def delete_titles_from_non_greek(table):
    table.rm(lang=all_but_language('GREEK'), vers=0)
    return table

def increment_greek_vers(table):
    def increment_vers(key):
        kd = key.asdict()
        kd['vers'] += 1
        return Key(**kd)
    
    table.remap(increment_vers, lang=['GREEK'])
    return table

def remove_versicle_number_in_non_greek(table):
    def remove_versicle_number(vers):
        return ' '.join(vers.split()[1:])
    return table.map(remove_versicle_number, lang=all_but_language('GREEK'))
    return table

def ensure_versicles_end_with_punctuation(table):
    def put_punctuation_at_end(vers):
        vers += '' if cat(vers[-1]).startswith('P') else '.'
        return vers

    return table.map(put_punctuation_at_end)

def main():
    pass
