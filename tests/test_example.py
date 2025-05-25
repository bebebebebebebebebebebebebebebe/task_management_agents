from src.mcp_server.example import calc


def test_calc():
    assert calc(2, 3) == 5
