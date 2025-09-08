from mtcli_trade.ordem import criar_ordem, enviar_ordem


def test_enviar_ordem_sucesso(mock_mt5, capsys):
    ordem = criar_ordem("WINV25", 1, 150, 300, 123.45, mock_mt5.ORDER_TYPE_BUY, False)
    mock_mt5.order_send.return_value = type(
        "Result", (), {"retcode": mock_mt5.TRADE_RETCODE_DONE, "order": 123456}
    )()
    enviar_ordem(ordem, limit=False)
    output = capsys.readouterr().out
    assert "enviada com sucesso" in output


def test_enviar_ordem_falha(mock_mt5, capsys):
    ordem = criar_ordem("WINV25", 1, 150, 300, 123.45, mock_mt5.ORDER_TYPE_BUY, False)
    mock_mt5.order_send.return_value = type(
        "Result", (), {"retcode": 10013, "comment": "Volume inválido"}
    )()
    enviar_ordem(ordem, limit=False)
    output = capsys.readouterr().out
    assert "❌ Falha ao enviar" in output
