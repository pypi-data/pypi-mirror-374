from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# --- br_carousel_row ---
@register.tag
def br_carousel_row(parser, token):
    """
    Inicia um contêiner de linha (row) para o carousel.

    Uso no template:
        {% br_carousel_row %}
            ... conteúdo do carousel ...
        {% end_br_carousel_row %}
    """
    bits = token.split_contents()
    col_class = "col-sm-12 col-md-8"
    for bit in bits[1:]:
        if bit.startswith("cols="):
            col_class = bit.split("=", 1)[1].strip('"\'')
    nodelist = parser.parse(('end_br_carousel_row',))
    parser.delete_first_token()
    return CarouselRowNode(nodelist, col_class)

class CarouselRowNode(template.Node):
    def __init__(self, nodelist, col_class):
        self.nodelist = nodelist
        self.col_class = col_class

    def render(self, context):
        return mark_safe(f'''
            <div class="row">
              <div class="{self.col_class}">
                {self.nodelist.render(context)}
              </div>
            </div>
        ''')

# --- br_carousel ---
@register.tag
def br_carousel(parser, token):
    """
    Estrutura principal do carousel, incluindo botões de navegação.

    Uso no template:
        {% br_carousel %}
            ... conteúdo (stage e steps) ...
        {% end_br_carousel %}
    """
    nodelist = parser.parse(('end_br_carousel',))
    parser.delete_first_token()
    return CarouselNode(nodelist)

class CarouselNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        return mark_safe(f'''
            <div class="br-carousel" data-circular="true" aria-label="Carrossel de Exemplo" aria-roledescription="carousel">
              <div class="carousel-button">
                <button class="br-button carousel-btn-prev terciary circle" type="button" aria-label="Anterior">
                  <i class="fas fa-chevron-left" aria-hidden="true"></i>
                </button>
              </div>
              {self.nodelist.render(context)}
              <div class="carousel-button">
                <button class="br-button carousel-btn-next terciary circle" type="button" aria-label="Próximo">
                  <i class="fas fa-chevron-right" aria-hidden="true"></i>
                </button>
              </div>
            </div>
          ''')

# --- br_carousel_stage ---
@register.tag
def br_carousel_stage(parser, token):
    """
    Container que agrupa todas as páginas do carousel.

    Uso no template:
        {% br_carousel_stage %}
            {% br_carousel_page %} ... {% end_br_carousel_page %}
        {% end_br_carousel_stage %}
    """
    nodelist = parser.parse(('end_br_carousel_stage',))
    parser.delete_first_token()
    return CarouselStageNode(nodelist)

class CarouselStageNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        return mark_safe(f'''
            <div class="carousel-stage">
              {self.nodelist.render(context)}
            </div>
          ''')

# --- br_carousel_page ---
@register.tag
def br_carousel_page(parser, token):
    """
    Representa uma página (slide) do carousel.

    A primeira página recebe automaticamente o atributo active="active".

    Uso no template:
        {% br_carousel_page %}
            {% br_carousel_page_content class="bg-blue-10" %}
                Título ou conteúdo
            {% end_br_carousel_page_content %}
        {% end_br_carousel_page %}
    """
    nodelist = parser.parse(('end_br_carousel_page',))
    parser.delete_first_token()
    return CarouselPageNode(nodelist)

class CarouselPageNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        # Determina se é a primeira página (para aplicar active="active")
        if 'carousel_page_counter' not in context:
            context['carousel_page_counter'] = 1
        else:
            context['carousel_page_counter'] += 1

        active_attr = 'active="active"' if context['carousel_page_counter'] == 1 else ''
        return mark_safe(f'''
            <div class="carousel-page" role="group" aria-roledescription="slide" aria-live="polite" {active_attr}>
              {self.nodelist.render(context)}
            </div>
          ''')

# --- br_carousel_page_content ---
@register.tag
def br_carousel_page_content(parser, token):
    """
    Conteúdo interno de uma página do carousel.

    Args:
        class (str): Classe CSS extra para customizar o background.

    Uso no template:
        {% br_carousel_page_content class="bg-blue-10" %}
            Texto ou HTML do título
        {% end_br_carousel_page_content %}
    """
    nodelist = parser.parse(('end_br_carousel_page_content',))
    parser.delete_first_token()

    # Pega o argumento class="..."
    bits = token.split_contents()
    css_class = ""
    for bit in bits[1:]:
        if bit.startswith("class="):
            css_class = bit.split("=", 1)[1].strip('"\'')
    return CarouselPageContentNode(nodelist, css_class)

class CarouselPageContentNode(template.Node):
    def __init__(self, nodelist, css_class):
        self.nodelist = nodelist
        self.css_class = css_class

    def render(self, context):
        content = self.nodelist.render(context).strip()
        class_attr = f"carousel-content{(' ' + self.css_class) if self.css_class else ''}"
        return mark_safe(f'''
            <div class="{class_attr}">
              <div class="h3 carousel-title">{content}</div>
            </div>
        ''')

# --- br_carousel_step ---
@register.tag
def br_carousel_step(parser, token):
    """
    Container que agrupa os botões de passo (step buttons) do carousel.

    Uso no template:
        {% br_carousel_step %}
            {% br_step_button text="Rótulo 1" aria_posinset=1 aria_setsize=5 %}
            ...
        {% end_br_carousel_step %}
    """
    nodelist = parser.parse(('end_br_carousel_step',))
    parser.delete_first_token()
    return CarouselStepNode(nodelist)

class CarouselStepNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        return mark_safe(f'''
            <div class="carousel-step">
              <nav class="br-step" data-initial="1" data-type="simple" role="none">
                <div class="step-progress" role="listbox" aria-orientation="horizontal" aria-label="Lista de Opções">
                  {self.nodelist.render(context)}
                </div>
              </nav>
            </div>
          ''')

# --- br_step_button ---
@register.simple_tag
def br_step_button(text, aria_posinset, aria_setsize):
    """
    Gera um botão de etapa para o carousel step.

    Args:
        text (str): Texto/label visível do botão.
        aria_posinset (int): Posição do item no conjunto.
        aria_setsize (int): Total de itens no conjunto.
    """
    return mark_safe(f'''
      <button class="step-progress-btn" role="option" aria-posinset="{aria_posinset}" aria-setsize="{aria_setsize}" type="button">
        <span class="step-info">{text}</span>
      </button>
    ''')
