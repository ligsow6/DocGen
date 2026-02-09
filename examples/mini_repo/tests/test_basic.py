from mini_app.main import main


def test_main(capsys) -> None:
    main()
    captured = capsys.readouterr()
    assert "Hello DocGen" in captured.out
