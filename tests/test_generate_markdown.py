from scripts.generate_markdown import align_markdown_tables


def test_align_table_emits_exactly_one_separator() -> None:
    table = "| Prop | Type |\n| --- | --- |\n| `size` | `str` |"

    assert align_markdown_tables(table) == (
        "| Prop   | Type  |\n| ------ | ----- |\n| `size` | `str` |"
    )


def test_align_table_keeps_escaped_pipes_inside_cells() -> None:
    table = '| Prop | Type |\n| --- | --- |\n| `size` | `"sm" \\| "xs"` |'

    assert align_markdown_tables(table) == (
        "| Prop   | Type           |\n"
        "| ------ | -------------- |\n"
        '| `size` | `"sm" \\| "xs"` |'
    )


def test_align_table_preserves_column_alignment_markers() -> None:
    table = "| Left | Center | Right |\n| :--- | :---: | ---: |\n| a | b | c |"

    assert align_markdown_tables(table) == (
        "| Left | Center | Right |\n| :--- | :----: | ----: |\n| a    | b      | c     |"
    )


def test_align_table_stops_at_first_line_not_starting_with_pipe() -> None:
    table = "| A | B |\n| --- | --- |\n| a | b |\nUse a | b to pipe."

    assert align_markdown_tables(table) == (
        "| A   | B   |\n| --- | --- |\n| a   | b   |\nUse a | b to pipe."
    )


def test_align_table_keeps_last_cell_of_row_without_trailing_pipe() -> None:
    table = "| A | B |\n| --- | --- |\n| a | b"

    assert align_markdown_tables(table) == (
        "| A   | B   |\n| --- | --- |\n| a   | b   |"
    )
