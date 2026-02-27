"""
Sample regulatory texts for testing.

Contains various Brazilian Portuguese regulatory texts with different
characteristics for comprehensive testing of the regulatory AI pipeline.
"""

# Short regulation (~100 words)
SHORT_REGULATION = """
RESOLUÇÃO BCB Nº 123/2024

O Banco Central do Brasil, no uso de suas atribuições, resolve:

Art. 1º As instituições participantes do Pix devem implementar validação adicional 
de CPF/CNPJ para transações acima de R$ 5.000,00.

Art. 2º A validação deve verificar a autenticidade do documento junto à Receita Federal.

Art. 3º Esta resolução entra em vigor em 90 dias a partir da data de publicação.

Brasília, 15 de março de 2024.
"""

# Medium regulation (~500 words)
MEDIUM_REGULATION = """
RESOLUÇÃO BCB Nº 456/2024

Dispõe sobre requisitos de segurança para transações Pix e estabelece 
procedimentos obrigatórios para instituições financeiras.

O Banco Central do Brasil, no uso das atribuições que lhe conferem os arts. 
10 e 11 da Lei nº 4.595, de 31 de dezembro de 1964, resolve:

CAPÍTULO I - DISPOSIÇÕES GERAIS

Art. 1º Esta Resolução estabelece requisitos mínimos de segurança para 
transações realizadas através do Sistema de Pagamentos Instantâneos (Pix).

Art. 2º Para os fins desta Resolução, considera-se:
I - transação de alto valor: operação Pix superior a R$ 10.000,00;
II - horário não comercial: período entre 20h e 6h;
III - dispositivo confiável: equipamento previamente cadastrado pelo usuário.

CAPÍTULO II - REQUISITOS DE SEGURANÇA

Art. 3º As instituições participantes do Pix devem implementar:
I - autenticação multifator para transações de alto valor;
II - análise de comportamento do usuário em tempo real;
III - bloqueio temporário de transações suspeitas;
IV - notificação imediata ao usuário sobre transações bloqueadas.

Art. 4º Para transações realizadas em horário não comercial acima de R$ 5.000,00, 
é obrigatória a confirmação adicional através de:
I - biometria facial ou digital; ou
II - token gerado por dispositivo confiável; ou
III - senha transacional específica.

Art. 5º As instituições devem manter registro detalhado de todas as tentativas 
de transação, incluindo:
I - data e hora da operação;
II - valor e identificação das partes;
III - resultado da análise de segurança;
IV - motivo de eventual bloqueio.

CAPÍTULO III - PRAZOS E PENALIDADES

Art. 6º As instituições têm prazo de 180 dias, contados da publicação desta 
Resolução, para adequação completa aos requisitos estabelecidos.

§1º O descumprimento dos requisitos sujeitará a instituição à multa de 
R$ 100.000,00 por dia de atraso.

§2º Em caso de reincidência, a multa será aplicada em dobro.

Art. 7º Esta Resolução entra em vigor na data de sua publicação.

Brasília, 20 de abril de 2024.
Roberto Campos Neto
Presidente do Banco Central do Brasil
"""

# Long regulation (~2000 words)
LONG_REGULATION = """
RESOLUÇÃO BCB Nº 789/2024

Estabelece diretrizes abrangentes para governança, conformidade e gestão de riscos 
no Sistema de Pagamentos Instantâneos (Pix), e dá outras providências.

O Banco Central do Brasil, no uso das atribuições que lhe conferem os arts. 10 e 11 
da Lei nº 4.595, de 31 de dezembro de 1964, e tendo em vista o disposto na Lei nº 
12.865, de 9 de outubro de 2013, resolve:

CAPÍTULO I - DISPOSIÇÕES PRELIMINARES

Art. 1º Esta Resolução estabelece requisitos de governança, conformidade e gestão 
de riscos aplicáveis às instituições participantes do Sistema de Pagamentos 
Instantâneos (Pix).

Art. 2º Para os fins desta Resolução, considera-se:
I - instituição participante: instituição financeira ou de pagamento autorizada 
pelo Banco Central a operar no Pix;
II - usuário final: pessoa física ou jurídica que utiliza serviços Pix;
III - transação instantânea: transferência de recursos concluída em até 10 segundos;
IV - chave Pix: identificador vinculado a uma conta para recebimento de pagamentos;
V - QR Code dinâmico: código de resposta rápida com informações variáveis;
VI - API Pix: interface de programação para integração com o sistema;
VII - liquidação: transferência efetiva de recursos entre contas de liquidação.

CAPÍTULO II - ESTRUTURA DE GOVERNANÇA

Art. 3º As instituições participantes devem estabelecer estrutura de governança 
específica para operações Pix, incluindo:
I - comitê executivo responsável por decisões estratégicas;
II - área técnica dedicada à manutenção e evolução dos sistemas;
III - equipe de segurança da informação especializada;
IV - função de conformidade independente;
V - auditoria interna com escopo específico para Pix.

Art. 4º O comitê executivo deve reunir-se no mínimo trimestralmente para:
I - avaliar indicadores de desempenho operacional;
II - analisar incidentes de segurança e fraudes;
III - revisar políticas e procedimentos;
IV - aprovar investimentos em infraestrutura;
V - deliberar sobre adequação a novas regulamentações.

Art. 5º As instituições devem documentar formalmente:
I - políticas de segurança da informação;
II - procedimentos operacionais padrão;
III - planos de continuidade de negócios;
IV - matriz de riscos e controles;
V - trilhas de auditoria completas.

CAPÍTULO III - REQUISITOS TÉCNICOS E OPERACIONAIS

Art. 6º Os sistemas que suportam operações Pix devem atender aos seguintes requisitos:
I - disponibilidade mínima de 99,9% ao mês;
II - tempo de resposta máximo de 10 segundos para transações;
III - capacidade de processar no mínimo 1.000 transações por segundo;
IV - redundância geográfica com failover automático;
V - backup em tempo real com retenção mínima de 5 anos.

Art. 7º As instituições devem implementar controles de segurança incluindo:
I - criptografia end-to-end para todas as comunicações;
II - certificados digitais ICP-Brasil para autenticação;
III - segregação de ambientes de produção, homologação e desenvolvimento;
IV - controle de acesso baseado em funções (RBAC);
V - monitoramento contínuo de vulnerabilidades;
VI - testes de penetração semestrais por empresa independente;
VII - programa de gestão de patches com SLA de 48 horas para vulnerabilidades críticas.

Art. 8º Para prevenção de fraudes, as instituições devem:
I - implementar motor de análise de risco em tempo real;
II - utilizar machine learning para detecção de padrões anômalos;
III - manter lista de dispositivos e IPs confiáveis por usuário;
IV - aplicar regras de negócio baseadas em perfil transacional;
V - bloquear automaticamente operações com score de risco acima do limite;
VI - notificar usuários sobre transações suspeitas em até 1 minuto.

CAPÍTULO IV - GESTÃO DE CHAVES PIX

Art. 9º O gerenciamento de chaves Pix deve observar:
I - validação obrigatória de titularidade antes do registro;
II - limite de 20 chaves por CPF em instituições diferentes;
III - processo de portabilidade concluído em até 7 dias;
IV - exclusão lógica com período de quarentena de 30 dias;
V - auditoria completa de todas as operações sobre chaves.

Art. 10 Para chaves do tipo telefone celular e e-mail:
I - envio de código de confirmação para validação;
II - prazo de 48 horas para confirmação;
III - exclusão automática se não confirmada no prazo;
IV - notificação ao usuário sobre tentativas de registro não autorizadas.

CAPÍTULO V - LIMITES E CONTROLES TRANSACIONAIS

Art. 11 As instituições devem estabelecer limites transacionais considerando:
I - perfil de risco do usuário;
II - histórico de utilização do serviço;
III - horário da transação;
IV - dispositivo utilizado;
V - localização geográfica.

Art. 12 São obrigatórios os seguintes limites mínimos de segurança:
I - R$ 1.000,00 para transações no período noturno (20h às 6h) sem autenticação adicional;
II - R$ 5.000,00 para transações em dispositivos não cadastrados;
III - R$ 20.000,00 para transações diárias por usuário pessoa física;
IV - R$ 100.000,00 para transações diárias por usuário pessoa jurídica.

§1º Os limites podem ser aumentados mediante solicitação do usuário e análise de risco.
§2º Reduções de limite devem ser processadas imediatamente.
§3º Aumentos de limite têm carência de 24 horas para entrada em vigor.

CAPÍTULO VI - TRATAMENTO DE INCIDENTES

Art. 13 As instituições devem manter equipe de resposta a incidentes disponível 24x7.

Art. 14 Incidentes de segurança devem ser classificados em:
I - crítico: indisponibilidade total ou vazamento de dados;
II - alto: indisponibilidade parcial ou tentativa de fraude em massa;
III - médio: degradação de performance ou fraude isolada;
IV - baixo: anomalias sem impacto aos usuários.

Art. 15 O Banco Central deve ser notificado em até:
I - 1 hora para incidentes críticos;
II - 4 horas para incidentes de nível alto;
III - 24 horas para incidentes de nível médio.

Art. 16 Relatório detalhado do incidente deve ser enviado em até 5 dias úteis, contendo:
I - descrição do evento e causa raiz;
II - impacto quantificado (usuários, transações, valores);
III - ações de contenção e remediação;
IV - plano de ação preventiva;
V - cronograma de implementação das melhorias.

CAPÍTULO VII - CONFORMIDADE E AUDITORIA

Art. 17 As instituições devem realizar:
I - auditoria interna anual específica para Pix;
II - auditoria externa independente a cada 2 anos;
III - testes de continuidade de negócios semestrais;
IV - avaliação de conformidade regulatória trimestral.

Art. 18 Relatórios de auditoria devem ser mantidos por 10 anos e disponibilizados 
ao Banco Central quando solicitado.

CAPÍTULO VIII - PRAZOS E DISPOSIÇÕES FINAIS

Art. 19 As instituições participantes têm os seguintes prazos para adequação:
I - 90 dias para requisitos de governança (Capítulo II);
II - 180 dias para requisitos técnicos e operacionais (Capítulo III);
III - 120 dias para gestão de chaves (Capítulo IV);
IV - 60 dias para limites transacionais (Capítulo V);
V - 30 dias para procedimentos de incidentes (Capítulo VI);
VI - 90 dias para conformidade e auditoria (Capítulo VII).

§1º Os prazos são contados a partir da data de publicação desta Resolução.
§2º Prorrogações podem ser solicitadas mediante justificativa fundamentada.
§3º Pedidos de prorrogação devem ser protocolados com antecedência mínima de 30 dias.

Art. 20 O descumprimento desta Resolução sujeitará a instituição às seguintes penalidades:
I - advertência, em caso de primeira infração de natureza leve;
II - multa de R$ 50.000,00 a R$ 500.000,00, conforme gravidade;
III - suspensão temporária de novas adesões de usuários;
IV - suspensão temporária de operações Pix;
V - exclusão do sistema em caso de reincidência grave.

Art. 21 Esta Resolução entra em vigor na data de sua publicação.

Art. 22 Ficam revogadas as Resoluções BCB nº 100/2020 e nº 150/2021.

Brasília, 1º de junho de 2024.
Roberto Campos Neto
Presidente do Banco Central do Brasil
"""

# Regulation with explicit deadline
REGULATION_WITH_DEADLINE = """
CIRCULAR BCB Nº 4.321/2024

Estabelece prazo para implementação de validação de CPF em transações Pix.

O Banco Central do Brasil, no uso de suas atribuições, torna público que:

Art. 1º As instituições participantes do Pix devem implementar validação 
automática de CPF/CNPJ para todas as transações.

Art. 2º A validação deve consultar a base de dados da Receita Federal em tempo real.

Art. 3º Transações com documentos inválidos devem ser rejeitadas automaticamente.

Art. 4º O prazo para implementação é de 120 dias corridos, com término em 31 de dezembro de 2024.

Art. 5º Instituições que não cumprirem o prazo estarão sujeitas a multa diária 
de R$ 10.000,00.

Art. 6º Esta Circular entra em vigor na data de sua publicação.

Brasília, 3 de setembro de 2024.
"""

# Regulation specifically about Pix
REGULATION_WITH_PIX = """
RESOLUÇÃO BCB Nº 555/2024

Altera requisitos de QR Code dinâmico para transações Pix.

O Banco Central do Brasil resolve:

Art. 1º Os QR Codes dinâmicos gerados para transações Pix devem incluir:
I - identificador único da transação (txid);
II - valor da transação em centavos;
III - chave Pix do recebedor;
IV - nome do recebedor;
V - cidade do recebedor;
VI - timestamp de geração;
VII - prazo de validade (máximo 24 horas).

Art. 2º O formato deve seguir o padrão EMV QR Code especificado pelo Banco Central.

Art. 3º APIs de geração de QR Code devem validar todos os campos obrigatórios.

Art. 4º QR Codes expirados devem retornar erro específico ao usuário.

Art. 5º As instituições devem adequar seus sistemas em até 60 dias.

Art. 6º Esta Resolução entra em vigor em 1º de novembro de 2024.

Brasília, 1º de setembro de 2024.
"""

# Informational text (no regulatory changes)
INFORMATIONAL_TEXT = """
COMUNICADO BCB Nº 40.123/2024

O Banco Central do Brasil informa que o Sistema de Pagamentos Instantâneos (Pix) 
completou 4 anos de operação com resultados expressivos.

Desde seu lançamento em novembro de 2020, o Pix processou mais de 50 bilhões de 
transações, movimentando R$ 30 trilhões.

Atualmente, mais de 150 milhões de brasileiros utilizam o Pix regularmente, 
com média de 200 milhões de transações por dia.

O sistema conta com mais de 800 instituições participantes, incluindo bancos, 
fintechs e cooperativas de crédito.

O Banco Central continua trabalhando em melhorias e novas funcionalidades para 
tornar o Pix ainda mais seguro e conveniente para todos os usuários.

Para mais informações, acesse www.bcb.gov.br/pix

Brasília, 10 de novembro de 2024.
"""

# Collection of all texts for easy iteration in tests
ALL_REGULATORY_TEXTS = {
    "short": SHORT_REGULATION,
    "medium": MEDIUM_REGULATION,
    "long": LONG_REGULATION,
    "with_deadline": REGULATION_WITH_DEADLINE,
    "with_pix": REGULATION_WITH_PIX,
    "informational": INFORMATIONAL_TEXT,
}
