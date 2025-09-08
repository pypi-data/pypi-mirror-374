from typing import List

from .data import Connection


def print_index_table(connections: List[Connection]):
    max_left = len(str(len(connections)))
    if max_left < 2:
        max_left = 2
    max_right = max(len(c.host) for c in connections)

    id_cell = "ID".rjust(max_left, " ")

    host_cell = "Host".ljust(max_right, " ")
    print(f"{id_cell} | {host_cell}")
    print(f"{"".ljust(max_left, "-")}-|-{"".ljust(max_right, "-")}")
    for index, connection in enumerate(connections):
        print(f"{str(index + 1).rjust(max_left, " ")} | {connection.host}")