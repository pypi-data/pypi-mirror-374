from enum import Enum


class EFaseRetificacao(Enum):
    NaoIniciado = 0
    SolicitacaoXml = 1
    AguardandoXml = 2
    DownloadXml = 3
    ExtraindoDadosDoXml = 4
    AguardandoRubrica = 5
    AberturaDeCompetencia = 6
    ConsultandoESocialAberturaCompetencia = 7
    InclusaoDasRubricas = 8
    ConsultandoESocialInclusaoRubricas = 9
    ExclusaoDePagamentos = 10
    ConsultandoESocialExclusaoPagamentos = 11
    RetificacaoDaRemuneracao = 12
    ConsultandoESocialRetificacaoRemuneracao = 13
    InclusaoDosPagamentos = 14
    ConsultandoESocialInclusaoPagamentos = 15
    Desligamento = 16
    ConsultandoESocialDesligamento = 17
    FechamentoDeCompetencia = 18
    ConsultandoESocialFechamentoCompetencia = 19
    Finalizado = 20
