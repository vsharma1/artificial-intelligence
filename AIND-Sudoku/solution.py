#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Code for solving a sudoku."""
import re
import doctest
from collections import defaultdict


assignments = []

# Set general values
rows = 'ABCDEFGHI'
cols = '123456789'
diagonals = [zip(rows, cols), zip(rows, cols[::-1])]


def cross(a, b):
    """Cross product of elements in a and elements in b."""
    return [s + t for s in a for t in b]

boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs)
                for rs in ('ABC', 'DEF', 'GHI')
                for cs in ('123', '456', '789')]
diagonal_units = [[row + col
                  for row, col in diagonal]
                  for diagonal in diagonals]

unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)


def assign_value(values, box, value):
    """
    Assign a value to a given box.

    If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())

    return values


def naked_twins(values):
    """
    Eliminate values using the naked twins strategy.

    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Find all instances of naked twins
    for unit in unitlist:
        # Group boxes that have the same possibilities
        siblings = defaultdict(set)
        for box in unit:
            value = values[box]

            # Only consider unsolved boxes
            if len(value) > 1:
                siblings[value].add(box)

        # Eliminate the naked twins as possibilities for their peers
        for value in siblings:
            sibling_set = siblings[value]
            if len(sibling_set) == len(value):
                # These siblings get to keep their value.
                # Everyone else deletes it.
                for box in unit:
                    if box in sibling_set:
                        continue

                    box_value = values[box]
                    new_value = re.sub('[%s]' % value, '', box_value)

                    if box_value != new_value:
                        assign_value(values, box, new_value)

    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.

    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'.
                    If the box is empty, then the value will be '123456789'

    >>> grid = ['.'] * 81
    >>> grid[0] = '1'
    >>> grid[8] = '2'
    >>> grid[9] = '3'
    >>> grid[79] = '4'
    >>> grid = ''.join(grid)

    >>> grid_dict = grid_values(grid)
    >>> grid_dict['A1']
    '1'
    >>> grid_dict['A9']
    '2'
    >>> grid_dict['B1']
    '3'
    >>> grid_dict['C3']
    '123456789'
    >>> grid_dict['I8']
    '4'
    """
    grid_dict = {}
    default = '123456789'

    for i, value in enumerate(grid):
        box_id = rows[i // 9] + cols[i % 9]
        grid_dict[box_id] = value if value != '.' else default

    return grid_dict


def display(values):
    """
    Display the values as a 2-D grid.

    Args:
        values(dict): The sudoku in dictionary form

    >>> grid = grid_values('.' * 81)
    >>> display(grid)
    |. . . | . . . | . . .|
    |. . . | . . . | . . .|
    |. . . | . . . | . . .|
    -----------------------
    |. . . | . . . | . . .|
    |. . . | . . . | . . .|
    |. . . | . . . | . . .|
    -----------------------
    |. . . | . . . | . . .|
    |. . . | . . . | . . .|
    |. . . | . . . | . . .|
    >>> grid['D6'] = '1'
    >>> grid['F3'] = '5'
    >>> display(grid)
    |. . . | . . . | . . .|
    |. . . | . . . | . . .|
    |. . . | . . . | . . .|
    -----------------------
    |. . . | . . 1 | . . .|
    |. . . | . . . | . . .|
    |. . 5 | . . . | . . .|
    -----------------------
    |. . . | . . . | . . .|
    |. . . | . . . | . . .|
    |. . . | . . . | . . .|
    """
    row_values = []
    for i, row in enumerate(rows):
        col_values = [
            values[row + col]
            if len(values[row + col]) == 1 else '.'
            for col in cols
        ]

        col_values.insert(6, '|')
        col_values.insert(3, '|')
        row_repr = '|%s|' % ' '.join(col_values)
        row_values.append(row_repr)

    row_values.insert(6, '-' * 23)
    row_values.insert(3, '-' * 23)

    print('\n'.join(row_values))


def eliminate(values):
    """Eliminate values from peer blocks based on placed values."""
    solved_boxes = [box for box in boxes if len(values[box]) == 1]
    for box in solved_boxes:
        value = values[box]
        for peer in peers[box]:
            peer_value = values[peer]
            if value in peer_value:
                assign_value(
                    values, peer,
                    peer_value.replace(value, ''))

    return values


def only_choice(values):
    """Set a value on a block when no other block in the unit can have it."""
    for unit in unitlist:
        for value in '123456789':
            possible_blocks = [box for box in unit if value in values[box]]
            if len(possible_blocks) == 1:
                block = possible_blocks[0]
                if values[block] != value:
                    assign_value(values, possible_blocks[0], value)

    return values


def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice() and recursive calls to search.

    If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If there is no change after an iteration, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        solved_values_before =\
            len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        solved_values_after =\
            len([box for box in values.keys() if len(values[box]) == 1])

        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """Using depth-first search and propagation, try all possible values."""
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False  # Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values  # Solved!

    # Chose one of the unfilled square s with the fewest possibilities
    n, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """
    Find the solution to a Sudoku grid.

    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid.
        False if no solution exists.
    """
    return search(grid_values(grid))


if __name__ == '__main__':
    doctest.testmod()
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)
    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
