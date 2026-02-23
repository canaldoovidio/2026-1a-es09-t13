# Aula: Visões de Arquitetura de Sistemas Distribuídos

## Módulo ES09 - Engenharia de Software | Turma T13

### Informações da Aula

| Campo | Valor |
|-------|-------|
| **Tema** | Visões de Arquitetura de Sistemas Distribuídos sob o ponto de vista de TDD |
| **Duração** | 1h45 (105 minutos) |
| **Instrutor** | Reginaldo Arakaki |
| **Parceiro** | ASIS by Sankhya |

---

## Objetivos de Aprendizagem

Ao final desta aula, o aluno será capaz de:

1. **Revisar e aplicar** o conceito das visões de arquitetura de sistema, direcionado pelo Negócio
2. **Aplicar** o conceito de fluxo crítico de negócio como elemento de arquitetura não funcional
3. **Exercitar na prática** como elementos arquiteturais se conectam do negócio para requisitos

---

## Estrutura da Aula

| Tempo | Bloco | Descrição |
|-------|-------|-----------|
| 15 min | Abertura e Conexão | Quiz de aquecimento sobre autoestudos |
| 20 min | Revisão Conceitual | RM-ODP e as 5 visões de arquitetura |
| 20 min | Business Drivers | Fluxos críticos e mapeamento em grupos |
| 25 min | Arquitetura as Code | Cenários de arquitetura como testes |
| 15 min | Integração e Síntese | Mapa mental colaborativo |
| 10 min | Encerramento | Resumo e próximos passos |

---

## Como Usar a Apresentação

### Navegação

- **Setas do teclado** (← →): Navegar entre slides
- **Barra de espaço**: Próximo slide
- **Home/End**: Ir para primeiro/último slide
- **F**: Modo tela cheia
- **Botões na tela**: Navegação visual

### Funcionalidades Interativas

1. **Quiz de Aquecimento** (Slides 4-6)
   - Clique nas opções para responder
   - Feedback imediato com destaque da resposta correta

2. **Diagrama RM-ODP** (Slide 8)
   - Clique em cada visão para ver detalhes em modal
   - Pressione ESC ou clique no X para fechar

3. **Atividade em Grupo** (Slide 18)
   - Timer integrado de 15 minutos
   - Botão para iniciar/pausar/reiniciar

4. **Compartilhamento** (Slide 19)
   - Espaço para anotações dos grupos

---

## Conteúdo Técnico Abordado

### RM-ODP (ISO/IEC 10746)

As 5 visões de arquitetura:

1. **Enterprise Viewpoint**: Propósito, escopo e políticas
2. **Information Viewpoint**: Semântica da informação
3. **Computational Viewpoint**: Decomposição funcional
4. **Engineering Viewpoint**: Mecanismos de distribuição
5. **Technology Viewpoint**: Escolha tecnológica

### ISO/IEC 25010

Características de qualidade de software:
- Functional Suitability
- Performance Efficiency
- Compatibility
- Interaction Capability
- Reliability
- Security
- Maintainability
- Flexibility
- Safety

### Business Drivers

Direcionadores de negócio que impactam decisões arquiteturais:
- Volumetria
- Segurança
- Integração
- Custos
- Restrições

---

## Pré-requisitos (Autoestudos)

Os alunos devem ter completado antes da aula:

1. **Business Drivers como arquitetura** (25 min)
   - ISO 10746 e conceitos de Business Drivers
   - [Link do material](https://drive.google.com/drive/folders/1eTIiz23me9zB6mFodrk18kPis103B3E9)

2. **Business Drivers como Código** (20 min)
   - Documento como regra de negócio
   - [Link do material](https://drive.google.com/drive/folders/1QLbEqkfOqZDo9lQVXdyI-9XlAKyIjUfV)

---

## Como Usar no GitHub Codespaces

Este repositório está configurado para ser executado diretamente no **GitHub Codespaces**:

1. Clique no botão **Code** no seu repositório GitHub.
2. Selecione a aba **Codespaces** e clique em **Create codespace on main**.
3. O ambiente será configurado automaticamente com todas as extensões necessárias.
4. Para ver os slides, abra qualquer arquivo `.html` (ex: `aula03.html`) e use a extensão **Live Server** (ícone "Go Live" no canto inferior direito).

## Laboratório de Business Drivers (Semana 03)

O código fonte do laboratório prático está na pasta `asis-bd-lab`. Para criar o repositório separado no seu GitHub:

1. Execute o script de preparação:
   ```bash
   ./create_repo.sh
   ```
2. Siga as instruções impressas no terminal para fazer o push para o seu GitHub em `canaldoovidio/asis-bd-lab`.

---

## Novidades desta Versão

- **Personalização:** Slides das aulas 03 e 04 atualizados com contexto do **BBB 26** (Chaiany, Dummy), **Supercopa 2026** (Corinthians 2x0 Flamengo) e imagens reais.
- **Codespaces:** Suporte nativo para desenvolvimento em nuvem tanto na raiz quanto no laboratório.
- **Automação:** Script facilitador para criação de repositórios individuais para os alunos.

---

## Arquivos da Apresentação

```
aula-visoes-arquitetura/
├── index.html      # Estrutura HTML dos slides
├── styles.css      # Estilos visuais (template Inteli)
├── script.js       # Lógica de navegação e interatividade
└── README.md       # Este arquivo
```

---

## Tecnologias Utilizadas

- HTML5 semântico
- CSS3 com variáveis customizadas
- JavaScript vanilla (sem dependências)
- Google Fonts (Manrope, Space Mono)
- Material Icons Outlined

---

## Compatibilidade

- Chrome/Edge (recomendado)
- Firefox
- Safari
- Responsivo para diferentes tamanhos de tela

---

## Licença

Material desenvolvido para uso educacional no Inteli - Instituto de Tecnologia e Liderança.

© 2026 Inteli
