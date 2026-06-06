# Design System Premium - VetLândia

**Versão:** 2.0 Premium  
**Data:** 2026-06-06  
**Inspiração:** MedIDData + Nubank + LinkedIn + iFood

---

## Filosofia

Design **mobile-first** pensado como **aplicativo nativo**, não website tradicional.

**Princípios:**
- App-like experience (futuro PWA/app nativo)
- Touch-friendly (alvos mínimo 44x44px)
- Microinterações e feedback visual
- Performance e fluidez
- Profissionalismo médico + acessibilidade

---

## Paleta de Cores Premium

### Primária - Azul Veterinário
```css
--vet-deep: #082D4D      /* Header, footer, elementos escuros */
--vet-primary: #0A4D68   /* Gradientes, destaques principais */
--vet-medium: #1A6BB5    /* Hover states */
--vet-light: #3B82F6     /* Elementos secundários */
```

### Accent - Teal (Vida Animal)
```css
--teal: #14B8A6          /* CTAs principais, badges profissionais */
--teal-light: #2DD4BF    /* Hover, highlights */
--teal-dark: #0D9488     /* Estados ativos */
```

### Accent - Laranja (Energia)
```css
--orange: #F77F00        /* CTAs secundários, badges especialidade */
--orange-light: #FCBF49  /* Avaliações, estrelas */
--orange-dark: #DC6803   /* Hover laranja */
```

### Superfícies
```css
--surface-base: #F8FAFC       /* Background geral */
--surface-secondary: #EFF4F9  /* Seções alternadas */
--surface-card: #FFFFFF       /* Cards, modais */
```

### Texto
```css
--text-primary: #1E293B    /* Títulos, textos principais */
--text-secondary: #475569  /* Descrições */
--text-tertiary: #94A3B8   /* Labels, metadados */
```

---

## Tipografia Premium

### Fontes
- **Display (Títulos):** Syne 600/700/800
- **Body (Textos):** DM Sans 300/400/500/600/700

### Hierarquia
```css
H1: Syne 800, 3rem (48px)           - Hero titles
H2: Syne 700, 2rem (32px)           - Section titles  
H3: Syne 600, 1.5rem (24px)         - Card titles
H4: DM Sans 600, 1.25rem (20px)     - Subsections
Body: DM Sans 400, 1rem (16px)      - Paragraphs
Small: DM Sans 400, 0.875rem (14px) - Metadata
```

### Letter Spacing
- Títulos: `-0.02em` (mais condensado, moderno)
- Body: `-0.01em` (legibilidade)
- Labels/Badges: `0.05em` (uppercase, espaçado)

---

## Componentes Premium

### Botões
```css
.btn-primary   → Gradiente azul (principal)
.btn-teal      → Gradiente teal (CTAs importantes)
.btn-orange    → Gradiente laranja (secundário)
.btn-outline   → Borda + hover fill
.btn-ghost     → Transparente, hover background

Efeito shine: shimmer ao hover
Transform: translateY(-2px) no hover
Shadow: elevação progressiva
```

### Cards
```css
Border-radius: 14px (var(--radius-lg))
Border: 1px solid var(--border-light)
Shadow: 0 1px 3px rgba(0,0,0,0.08)
Hover: translateY(-4px) + shadow-lg

Interactive: cursor pointer + touch feedback
Elevated: shadow-md permanente
```

### Badges
```css
Border-radius: 9999px (pill completo)
Font-size: 0.75rem
Text-transform: uppercase
Letter-spacing: 0.05em

Teal: perfis veterinários
Orange: especialidades
Blue: categorias
Gray: estados neutros
```

### Forms
```css
Border: 1.5px solid (mais definida)
Border-radius: 10px
Padding: 12px 16px
Focus: box-shadow teal + border teal

Placeholders: text-tertiary
Error state: border + shadow vermelho
```

---

## Layout & Grid

### Containers
```css
.container        → max-width: 1280px
.container-narrow → max-width: 920px
.container-wide   → max-width: 1440px
```

### Grid System
```css
.grid-2 → repeat(auto-fit, minmax(320px, 1fr))
.grid-3 → repeat(auto-fit, minmax(280px, 1fr))
.grid-4 → repeat(auto-fit, minmax(240px, 1fr))

Gap padrão: var(--space-6) = 24px
```

### Spacing (Sistema 4px)
```css
--space-1: 4px
--space-2: 8px
--space-3: 12px
--space-4: 16px
--space-5: 20px
--space-6: 24px
--space-8: 32px
--space-10: 40px
--space-12: 48px
--space-16: 64px
--space-20: 80px
```

---

## Mobile-First (App-like)

### Viewport
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<meta name="theme-color" content="#0A4D68">
<meta name="apple-mobile-web-app-capable" content="yes">
```

### Menu Mobile
- Slide lateral (85% largura, max 360px)
- Overlay com blur
- Animação suave (0.3s)
- Touch-friendly links (padding generoso)

### Touch Targets
- Mínimo: 44x44px (WCAG)
- Botões: 14px padding vertical
- Links: 12px padding vertical
- Espaçamento entre elementos: 16px+

### Responsividade
```css
Desktop: > 1024px
Tablet:  640px - 1024px
Mobile:  < 640px

Mobile-first: escrever CSS para mobile, depois @media para desktop
```

---

## Microinterações

### Animações
```javascript
// Cards aparecem com fade + translateY
opacity: 0 → 1
transform: translateY(20px) → 0

// Botões com shimmer effect
Linear gradient sweep on hover

// Touch feedback
opacity: 1 → 0.7 (touchstart)
```

### Transições
```css
--transition-fast: 0.15s ease
--transition-base: 0.2s ease
--transition-slow: 0.3s ease
```

### Feedback Visual
- Hover: elevação + cor
- Active: escala ligeiramente menor
- Focus: outline teal + shadow
- Loading: spinner inline no botão

---

## Sombras Premium

```css
--shadow-xs: 0 1px 2px rgba(0,0,0,0.04)
--shadow-sm: 0 1px 3px rgba(0,0,0,0.08)
--shadow-md: 0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04)
--shadow-lg: 0 12px 24px rgba(0,0,0,0.12), 0 4px 8px rgba(0,0,0,0.06)
--shadow-xl: 0 20px 40px rgba(0,0,0,0.16), 0 8px 16px rgba(0,0,0,0.08)
```

Uso:
- xs: labels, badges
- sm: cards padrão
- md: cards hover
- lg: botões hover, modais
- xl: dropdowns, search box

---

## Gradientes

```css
--gradient-primary: linear-gradient(135deg, #082D4D 0%, #0A4D68 100%)
--gradient-teal: linear-gradient(135deg, #0D9488 0%, #14B8A6 100%)
--gradient-orange: linear-gradient(135deg, #DC6803 0%, #F77F00 100%)
```

Aplicação:
- Hero backgrounds
- CTAs principais
- Logo (text gradient)
- Destaques visuais

---

## Acessibilidade

### Contraste (WCAG AA)
✓ text-primary (#1E293B) em surface-card (#FFFFFF): AAA
✓ text-secondary (#475569) em surface-card: AAA
✓ teal (#14B8A6) em branco: AA
✓ vet-deep (#082D4D) em branco: AAA

### Navegação
- Tecla ESC fecha modais/menus
- Tab navigation funcional
- Focus states visíveis
- Labels semânticos

### Responsivo
- Tipografia escala em mobile
- Touch targets mínimo 44px
- Scroll suave
- Sem horizontal scroll

---

## Performance

### Otimizações
- Fontes Google Fonts com preconnect
- CSS inline crítico (futuro)
- Lazy load imagens (futuro)
- Intersection Observer para animações

### Loading States
- Skeleton screens
- Spinner inline em botões
- Feedback imediato (< 100ms)

---

## Checklist Implementação

Ao criar nova página/componente:

- [ ] Mobile-first CSS
- [ ] Touch targets >= 44px
- [ ] Animações suaves (0.2s padrão)
- [ ] Cores da paleta oficial
- [ ] Tipografia Syne + DM Sans
- [ ] Border-radius consistente (10-14px)
- [ ] Sombras apropriadas
- [ ] Hover/focus states
- [ ] Contraste WCAG AA
- [ ] Teste em mobile real

---

## Diferenças vs Versão 1.0

| Aspecto | V1 (Genérico) | V2 (Premium) |
|---------|---------------|---------------|
| Fontes | Inter + Poppins | Syne + DM Sans |
| Cores | Azul genérico | Gradientes premium |
| Mobile | Responsivo | App-like nativo |
| Animações | Básicas | Microinterações |
| Cards | 8px radius | 14px radius + elevação |
| Botões | Flat | Gradientes + shimmer |
| Menu Mobile | Básico | Slide lateral + overlay |
| Sombras | Simples | Sistema elevação 5 níveis |

---

**Resultado:** Design profissional, moderno e pronto para virar app nativo.
