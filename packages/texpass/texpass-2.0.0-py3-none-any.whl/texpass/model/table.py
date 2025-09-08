from textual.fuzzy import Matcher


class Columns:
    """
    Columns of the Table

    Currently its hardcoded
    """
    class Column:
        def __init__(self, column_name: str, ratio: int = 0):
            """
            :param int ratio: Ratio of space taken up. To share space equally, set this to 1
                but to use minimum width set this to 0 (default)
            """
            self.column_name = column_name
            self.ratio = ratio

    def __init__(self):
        self.columns = [self.Column("ID", 0), self.Column("Website", 5), self.Column("Username", 4)]
        """ordered Column objects"""
        self.order = {"ID": 0, "Website": 1, "Username": 2}
        """maps column name to order in the `self.columns` list"""
        self.total_ratio = 0
        self.zero_ratio_cols = 0
        """number of columns with zero ratio"""

        for col in self.columns:
            self.total_ratio += col.ratio
            
            if self.total_ratio == 0:
                self.zero_ratio_cols += 1
    
    def get_free_column_space(self, cell_padding: int, total_min_width: int, table_width: int) -> int:
        """
        Get free space for use in filling up columns with ratioed width.

        It subtracts width of no ratio columns and padding of ratioed columns from table width
        """
        # Account for padding on both sides of each column which are not zero ratio
        # don't know why I remove no ratio column paddings, if I include them the columns dont expand to full width
        total_cell_padding = cell_padding * (len(self.columns)*2)

        return table_width - total_min_width - total_cell_padding

    def get_width(self, column_name: str, free_space: int):
        """
        Get width of column based on free column space
        """
        column = self.columns[self.order[column_name]]
        # get width
        if column.ratio > 0:
            width = int((column.ratio / self.total_ratio) * free_space)
            return width
        else:
            return 0


class Table:
    """
    Internal implementation of a table so it can be used to populate a Textual Datatable

    Note that indexing within this table starts from 1, for readability
    """                
    def __init__(self):
        self.columns = Columns()
        self.rows = []
        
    def populate_table(self, pg_records: list[tuple]):
        """
        Populates table from empty
        """
        self.rows = []

        for i, record in enumerate(pg_records, 1):
            self.rows.append((i, *record))

    def generator(self):
        """
        Returns a generator to iterate through when adding rows in table UI
        """
        for row in self.rows:
            yield row
    
    def get_key(self, row: tuple) -> str:
        # hardcoded ID column index
        return str(row[0])
    
    def get_fuzzied_records(self, query: str) -> list[tuple[tuple, int]]:
        """
        Do fuzzy search on all records

        Returns sorted by descending order, all scores greater than 0
        """
        def make_string(row):
            """Concatenate cells of a row as a string. For use in fuzzy matching"""
            return " ".join([str(cell) for cell in row])
        
        result = []

        matcher = Matcher(query)
        
        for row in self.rows:
            # get score
            score = matcher.match(make_string(row))

            if score > 0:
                # append to result list in the format ((id, website, username), score)
                # ... if score is higher than 0
                result.append((row, score))
            
        # sort in descending order by score
        return sorted(result, key = lambda x: x[-1], reverse = True)
    
    def add_record(self, website: str, username: str) -> int:
        """
        Appends new row to the table

        Returns ID of the new row
        """
        last = len(self.rows) + 1
        self.rows.append((last, website, username))

        return last