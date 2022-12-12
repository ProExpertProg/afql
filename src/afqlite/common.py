from typing import Sequence

TupleDesc = dict[str, str]


def td_add_alias(alias: str, td: TupleDesc) -> TupleDesc:
    return td if alias is None else \
        {"%s.%s" % (alias, k): v for k, v in td}


class Tuple:
    def __init__(self, tupledesc: TupleDesc, values: Sequence):
        if len(tupledesc) != len(values):
            raise RuntimeError("tupledesc needs to match values")

        self.values = list(values)
        self.tupledesc = tupledesc

    def __or__(self, other: 'Tuple') -> 'Tuple':
        td = self.tupledesc | other.tupledesc
        return Tuple(td, self.values + other.values)

    def __getitem__(self, item):
        return self.values[item]

    @staticmethod
    def empty():
        return Tuple({}, [])
