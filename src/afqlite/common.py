from typing import Sequence

import prettytable as prettytable

TupleDesc = list[tuple[str, str]]


def td_add_alias(alias: str, td: TupleDesc) -> TupleDesc:
    return td if alias is None else \
        [("%s.%s" % (alias, name), t) for name, t in td]


class Tuple:
    def __init__(self, tupledesc: TupleDesc, values: Sequence):
        if len(tupledesc) != len(values):
            raise RuntimeError("tupledesc needs to match values")

        self.values = list(values)
        self.tupledesc = tupledesc

    def __add__(self, other: 'Tuple') -> 'Tuple':
        td = self.tupledesc + other.tupledesc
        return Tuple(td, self.values + other.values)

    def __getitem__(self, item):
        return self.values[item]

    def __str__(self):
        pairs = ["%s=%s" % (col[0], val) for col, val in zip(self.tupledesc, self.values)]
        return "Tuple(%s)" % (",".join(pairs),)

    def __repr__(self): return self.__str__()

    @staticmethod
    def empty():
        return Tuple([], [])


def format_results(tuples: list[Tuple], td: TupleDesc) -> str:
    if td is None:
        raise KeyError

    table = prettytable.PrettyTable([name for name, t in td])
    table.add_rows(t.values for t in tuples)

    return str(table)