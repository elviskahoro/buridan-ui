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
