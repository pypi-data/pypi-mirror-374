from enum import Enum


class EFaseRetificacao(Enum):
    NaoIniciado = 0
    SolicitacaoXml = 1
    AguardandoXml = 2
    DownloadXml = 3
    ExtraindoDadosDoXml = 4
    AguardandoRubrica = 5
    EstruturandoXmlAberturaCompetencia = 6
    EstruturandoXmlExclusaoPagamentos = 7
    EstruturandoXmlRetificacaoRemuneracao = 8
    EstruturandoXmlInclusaoPagamentos = 9
    EstruturandoXmlDesligamento = 10
    EstruturandoXmlFechamentoCompetencia = 11
    AberturaDeCompetencia = 12
    ConsultandoESocialAberturaCompetencia = 13
    InclusaoDasRubricas = 14
    ConsultandoESocialInclusaoRubricas = 15
    ExclusaoDePagamentos = 16
    ConsultandoESocialExclusaoPagamentos = 17
    RetificacaoDaRemuneracao = 18
    ConsultandoESocialRetificacaoRemuneracao = 19
    InclusaoDosPagamentos = 20
    ConsultandoESocialInclusaoPagamentos = 21
    Desligamento = 22
    ConsultandoESocialDesligamento = 23
    FechamentoDeCompetencia = 24
    ConsultandoESocialFechamentoCompetencia = 25
    Finalizado = 26
