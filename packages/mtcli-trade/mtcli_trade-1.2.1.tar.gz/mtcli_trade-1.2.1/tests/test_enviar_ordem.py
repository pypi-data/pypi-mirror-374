from unittest.mock import patch, MagicMock
from mtcli_trade.ordem import enviar_ordem


@patch("mtcli_trade.ordem.mt5.order_send")
def test_enviar_ordem_sucesso(mock_send):
    resultado = MagicMock()
    resultado.retcode = 10009  # TRADE_RETCODE_DONE
    resultado.order = 123456
    mock_send.return_value = resultado

    ordem = {"mock": "ordem"}
    enviar_ordem(ordem, limit=False)
    mock_send.assert_called_once_with(ordem)


@patch("mtcli_trade.ordem.mt5.order_send")
def test_enviar_ordem_falha(mock_send):
    resultado = MagicMock()
    resultado.retcode = 10013  # erro qualquer
    resultado.comment = "Invalid stops"
    mock_send.return_value = resultado

    ordem = {"mock": "ordem"}
    enviar_ordem(ordem, limit=True)
    mock_send.assert_called_once_with(ordem)
