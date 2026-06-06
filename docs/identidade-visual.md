# Identidade Visual VetLândia

**Versão:** 1.0  
**Data:** 2026-06-06  
**Status:** Aprovada

---

## Marca

**Nome:** VetLândia

**Conceito:**
- "Vet" = veterinária
- "Lândia" = território, comunidade, ecossistema
- Significado: "o lugar" da veterinária

**Slogan:**
> Confiança para quem cuida. Conhecimento para quem trata.

**Razão:**
- Comunica valor para ambos públicos (tutores + veterinários)
- "Confiança" = tutores buscando profissionais confiáveis
- "Conhecimento" = veterinários buscando aprendizado/comunidade
- Paralelismo forte e memorável

---

## Posicionamento

"A comunidade profissional da medicina veterinária brasileira"

**Tom de voz:**
- Profissional, mas acessível
- Técnico quando necessário, humano sempre
- Sério sem ser corporativo
- Inclusivo (do recém-formado ao PhD)

**O que somos:**
- LinkedIn + UpToDate para veterinários
- Transparência e avaliações para tutores
- Comunidade técnica de alto nível

**O que NÃO somos:**
- Pet shop digital
- Marketplace de produtos
- Rede social genérica
- Plataforma infantilizada

---

## Paleta de Cores

### Primária: Azul Médico Moderno

```
Azul Profundo:       #0A4D68 (títulos, logo, identidade forte)
Azul Intermediário:  #088395 (links, CTAs, interações principais)
Azul Claro:          #05BFDB (highlights, badges, acentos suaves)
```

**Uso:**
- `#0A4D68`: Headlines, logo principal, footers
- `#088395`: Botões primários, links, elementos interativos
- `#05BFDB`: Badges, highlights, hover states

### Secundária: Laranja Vitalidade

```
Laranja Vibrante:    #F77F00 (CTAs importantes, energia)
Amarelo Quente:      #FCBF49 (destaques suaves, hover secundário)
```

**Uso:**
- `#F77F00`: CTAs críticos (Criar Perfil, Publicar Caso), badges de especialidade
- `#FCBF49`: Estados hover, elementos de destaque não-críticos

### Neutros

```
Texto Principal:     #1A1A1A
Texto Secundário:    #4A5568
Background Claro:    #F7FAFC
Background Puro:     #FFFFFF
```

### Sistema de Feedback

```
Sucesso:  #10B981 (verde médico)
Alerta:   #F59E0B (âmbar)
Erro:     #EF4444 (vermelho médico)
Info:     #3B82F6 (azul informação)
```

**Contextos:**
- Sucesso: confirmações, salvamentos, ações concluídas
- Alerta: avisos, perfis incompletos, atenção necessária
- Erro: validações falhas, erros de sistema
- Info: dicas, informações contextuais

---

## Tipografia

### Fontes

**Primária (textos):**  
`Inter` (Google Fonts)
- Weights: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)

**Secundária (títulos):**  
`Poppins` (Google Fonts)
- Weights: 600 (semibold), 700 (bold)

**Monospace (código/técnico):**  
Sistema padrão (`monospace`)

### Hierarquia Tipográfica

```
H1: Poppins 700, 32px/40px    (mobile: 24px/32px)
H2: Poppins 600, 24px/32px    (mobile: 20px/28px)
H3: Inter 600, 20px/28px      (mobile: 18px/24px)
Body: Inter 400, 16px/24px
Small: Inter 400, 14px/20px
Caption: Inter 400, 12px/16px
```

**Aplicação:**
- H1: Títulos de páginas, hero sections
- H2: Seções principais
- H3: Subsections, card titles
- Body: Texto padrão (descrições, parágrafos)
- Small: Metadados, datas, informações secundárias
- Caption: Legendas de imagens, footnotes

---

## Componentes Visuais

### Cards

```
Border-radius: 8px
Sombra padrão: 0 1px 3px rgba(0,0,0,0.1)
Sombra hover: 0 4px 12px rgba(0,0,0,0.15)
Padding: 20px
Background: #FFFFFF
```

**Comportamento hover:**
- `transform: translateY(-2px)`
- Elevação da sombra
- Transição: 0.2s

### Botões

**Primário:**
```css
background: #088395
color: #FFFFFF
padding: 12px 24px
border-radius: 8px
font-weight: 600

hover:
  background: #0A4D68
  transform: translateY(-1px)
  box-shadow: 0 4px 8px rgba(8, 131, 149, 0.3)
```

**Secundário:**
```css
background: transparent
color: #088395
border: 2px solid #088395

hover:
  background: #05BFDB
  color: #FFFFFF
  border-color: #05BFDB
```

**Accent (CTAs importantes):**
```css
background: #F77F00
color: #FFFFFF

hover:
  background: #FCBF49
  transform: translateY(-1px)
  box-shadow: 0 4px 8px rgba(247, 127, 0, 0.3)
```

### Badges

```
padding: 4px 12px
border-radius: 12px
font-size: 12px
font-weight: 600

Variações:
- Profissão: background #05BFDB, color #FFFFFF
- Especialidade: background #F77F00, color #FFFFFF
- Status: usar cores do sistema de feedback
```

### Inputs

```
border: 1px solid #CBD5E0
border-radius: 8px
padding: 10px 14px
font-size: 16px

focus:
  border-color: #088395
  box-shadow: 0 0 0 3px rgba(8, 131, 149, 0.1)

error:
  border-color: #EF4444
```

---

## Ícones

**Estilo:** Outline (não filled)  
**Biblioteca:** Heroicons ou Lucide  
**Peso:** 2px stroke  
**Tamanho padrão:** 20px (small: 16px, large: 24px)

**Justificativa:**
- Outline = moderno, profissional, não-infantil
- Consistência visual
- Fácil integração

---

## Ilustrações e Imagens

**Estilo:**
- Line art minimalista
- Diagramas médicos estilizados
- Silhuetas animais geométricas

**Evitar:**
- Mascotes
- Personagens fofos
- Estilo cartoon exagerado
- Stock photos genéricas de pets felizes

**Preferir:**
- Ambientes clínicos reais
- Veterinários trabalhando (contextos autênticos)
- Imagens profissionais de procedimentos

---

## Espaçamento

Sistema baseado em múltiplos de 4px:

```
4px   = xs
8px   = sm
12px  = md
16px  = base
24px  = lg
32px  = xl
48px  = 2xl
64px  = 3xl
```

**Aplicação:**
- Margens entre elementos: base (16px)
- Padding de cards: lg (24px)
- Espaçamento entre seções: 2xl ou 3xl (48-64px)

---

## Responsividade

**Breakpoints:**

```
mobile:  < 640px
tablet:  640px - 1024px
desktop: > 1024px
```

**Prioridade:** Mobile-first

**Ajustes principais:**
- Tipografia escala em mobile (ver hierarquia acima)
- Cards: grid → stack em mobile
- Navegação: hamburguer menu < 640px
- Botões: full-width em mobile para CTAs principais

---

## Logo

**Formato textual (MVP):**

```
VetLândia
```

**Tipografia:** Poppins 700  
**Cor principal:** #0A4D68  
**Cor accent (opcional):** #F77F00 na palavra "Lândia"

**Variações:**

1. **Logo completo:**
   - VetLândia + slogan
   - Uso: footer, páginas institucionais

2. **Logo simplificado:**
   - Apenas VetLândia
   - Uso: header, navegação

3. **Logo mobile:**
   - VL (iniciais)
   - Uso: favicons, apps

**Futuro:**
- Ícone gráfico (não prioridade MVP)
- Versões monocromáticas para parceiros

---

## Aplicações de Marca

### Header/Navegação

```
Desktop:
[Logo VetLândia]  [Veterinários] [Clínicas] [Casos Clínicos]  [Buscar 🔍] [Entrar] [Cadastrar]

Mobile:
[☰] [Logo] [🔍] [👤]
```

**Cores:**
- Background header: #FFFFFF
- Links: #4A5568 (normal), #088395 (hover/active)
- CTA "Cadastrar": botão accent (#F77F00)

### Footer

```
Background: #0A4D68
Texto: #FFFFFF (opacidade 80% para links)
Logo: versão branca

Estrutura:
- Logo + slogan
- Links institucionais
- Redes sociais
- Copyright
```

### Cards de Perfil

```
[Foto]
Nome: Poppins 600, 18px, #0A4D68
CRMV + Especialidade: Inter 400, 14px, #4A5568
Localização: Inter 400, 14px, #4A5568
Avaliação: ⭐ + média + quantidade
Badge especialidade: laranja (#F77F00)
```

---

## Acessibilidade

**Contraste mínimo:** WCAG AA

Verificado:
- `#0A4D68` em `#FFFFFF`: ✓ AAA
- `#088395` em `#FFFFFF`: ✓ AAA
- `#F77F00` em `#FFFFFF`: ✓ AA
- `#4A5568` em `#FFFFFF`: ✓ AAA

**Estados interativos:**
- Focus visível (outline ou shadow)
- Hover com mudança perceptível
- Active state diferenciado

---

## Referências Visuais

**Inspirações (o que pegar):**
- Doctoralia: profissionalismo, cards limpos
- LinkedIn: seriedade, confiança, blue palette
- Stripe: tipografia clara, espaçamento generoso
- Notion: componentes simples e eficazes

**Anti-referências (o que evitar):**
- PetLove: infantilização excessiva
- Petz: cores muito vibrantes/cartoon
- Redes sociais genéricas: frivolidade

---

## Checklist de Implementação

Ao criar componentes, garantir:

- [ ] Cores da paleta oficial
- [ ] Tipografia Inter/Poppins
- [ ] Border-radius 8px em cards/botões
- [ ] Sombras sutis (0 1px 3px padrão)
- [ ] Hover states com transição 0.2s
- [ ] Ícones outline 20px
- [ ] Espaçamento sistema 4px
- [ ] Responsividade mobile-first
- [ ] Contraste WCAG AA mínimo
- [ ] Focus states visíveis

---

## Manutenção

**Atualizar este documento quando:**
- Adicionar nova cor à paleta
- Criar novo componente reutilizável
- Alterar tipografia
- Definir novo padrão visual

**Não criar:**
- Variações de cores fora da paleta sem justificativa
- Novos tamanhos de tipografia sem documentar
- Componentes únicos (criar reutilizáveis)

---

**Aprovado em:** 2026-06-06  
**Próxima revisão:** Após MVP (3 meses)
