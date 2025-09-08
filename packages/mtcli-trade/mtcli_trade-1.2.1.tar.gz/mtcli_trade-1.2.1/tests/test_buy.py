import pytest
from unittest.mock import patch, MagicMock
from mtcli_trade.buy import buy


@patch("mtcli_trade.buy.inicializar")
@patch("mtcli_trade.buy.criar_ordem")
@patch("mtcli_trade.buy.enviar_ordem")
@patch("mtcli_trade.buy.shutdown")
@patch("mtcli_trade.buy.conectar")
@pytest.mark.skip(reason="Teste desativado temporariamente")
def test_buy_market(
    mock_conectar, mock_shutdown, mock_enviar, mock_criar, mock_inicializar
):
    ctx = MagicMock()
    ctx.invoke = buy.callback

    mock_inicializar.return_value = MagicMock(ask=100000)
    mock_criar.return_value = {"mock": "ordem"}

    result = buy.callback(
        symbol="WINV25", lot=1.0, sl=150, tp=300, limit=False, preco=None
    )

    mock_conectar.assert_called_once()
    mock_inicializar.assert_called_once_with("WINV25")
    mock_criar.assert_called_once()
    mock_enviar.assert_called_once()
    mock_shutdown.assert_called_once()


@patch("mtcli_trade.buy.inicializar")
@patch("mtcli_trade.buy.criar_ordem")
@patch("mtcli_trade.buy.enviar_ordem")
@patch("mtcli_trade.buy.shutdown")
@patch("mtcli_trade.buy.conectar")
@pytest.mark.skip(reason="Teste desativado temporariamente")
def test_buy_limit(
    mock_conectar, mock_shutdown, mock_enviar, mock_criar, mock_inicializar
):
    mock_inicializar.return_value = MagicMock(ask=100000)

    result = buy.callback(
        symbol="WINV25", lot=1.0, sl=150, tp=300, limit=True, preco=99900
    )

    mock_conectar.assert_called_once()
    mock_inicializar.assert_called_once()
    mock_criar.assert_called_once_with(
        "WINV25", 1.0, 150, 300, 99900, 2, True  # ORDER_TYPE_BUY_LIMIT = 2
    )
    mock_enviar.assert_called_once()
    mock_shutdown.assert_called_once()


@patch("mtcli_trade.buy.inicializar")
@patch("mtcli_trade.buy.shutdown")
@patch("mtcli_trade.buy.conectar")
@pytest.mark.skip(reason="Teste desativado temporariamente")
def test_buy_inicializar_falha(mock_conectar, mock_shutdown, mock_inicializar):
    mock_inicializar.return_value = None

    result = buy.callback(
        symbol="INVALIDO", lot=1.0, sl=150, tp=300, limit=False, preco=None
    )

    mock_conectar.assert_called_once()
    mock_inicializar.assert_called_once()
    mock_shutdown.assert_called_once()
