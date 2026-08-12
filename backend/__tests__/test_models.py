from app.models import Usuario, RoleEnum, Servico, Agendamento, StatusAgendamento


def test_usuario_tablename_e_defaults():
    assert Usuario.__tablename__ == "usuarios"
    usuario = Usuario(nome="Teste", email="teste@teste.com", senha_hash="hash")
    assert usuario.role is None or isinstance(usuario.role, (RoleEnum, type(None)))


def test_servico_tablename():
    assert Servico.__tablename__ == "servicos"
    servico = Servico(nome="Corte", duracao_minutos=30, preco=50.0)
    assert servico.nome == "Corte"
    assert servico.duracao_minutos == 30


def test_agendamento_tablename_e_status_enum():
    assert Agendamento.__tablename__ == "agendamentos"
    assert set(StatusAgendamento) == {
        StatusAgendamento.PENDENTE,
        StatusAgendamento.CONFIRMADO,
        StatusAgendamento.CANCELADO,
    }


def test_role_enum_valores():
    assert {role.value for role in RoleEnum} == {"CLIENTE", "ADMIN", "FUNCIONARIO"}
