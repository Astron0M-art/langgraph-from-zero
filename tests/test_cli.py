from pytest import CaptureFixture

from langgraph_from_zero.__main__ import main


def test_default_cli_composes_v01_to_v03_capabilities(capsys: CaptureFixture[str]) -> None:
    main()
    output = capsys.readouterr().out
    lines = output.strip().splitlines()

    assert [line.split()[1] for line in lines] == [
        "node=normalize",
        "node=collect",
        "node=collect",
        "node=review",
    ]
    assert "evidence': ['source-1', 'source-2']" in lines[-1]
    assert lines[-1].endswith("next=__end__")
