from django import template
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.urls import reverse, NoReverseMatch

register = template.Library()

# Função auxiliar para resolver variáveis de contexto ou usar valores literais
def resolve_variable(value, context):
    if value is None:
        return ""
    try:
        # Tenta resolver como uma variável de contexto
        return template.Variable(value).resolve(context)
    except template.VariableDoesNotExist:
        # Se falhar, usa o valor como uma string literal, removendo aspas
        return str(value).strip('"\'')

# =========================
# BLOCO: ESTRUTURA PRINCIPAL DO HEADER
# =========================

# --- Tag: br_header ---
@register.tag(name='br_header')
def do_br_header(parser, token):
    bits = token.split_contents()
    extra_classes = None
    if len(bits) > 1 and 'class=' in bits[1]:
        extra_classes = bits[1].split('=', 1)[1]
    nodelist = parser.parse(('end_br_header',))
    parser.delete_first_token()
    return BRHeaderNode(nodelist, extra_classes)

class BRHeaderNode(template.Node):
    def __init__(self, nodelist, extra_classes=None):
        self.nodelist = nodelist
        self.extra_classes = extra_classes
    def render(self, context):
        extra_classes_str = f" {resolve_variable(self.extra_classes, context)}" if self.extra_classes else ""
        # Agora apenas renderiza o conteúdo, sem se preocupar com a busca.
        rendered_content = self.nodelist.render(context)
        return format_html(
            '<header class="br-header{}"><div class="container-lg">{}</div></header>',
            extra_classes_str, mark_safe(rendered_content)
        )

# --- Tags de Bloco Explícitas (sem fábrica) ---

# Tag: br_header_top
@register.tag(name='br_header_top')
def do_br_header_top(parser, token):
    nodelist = parser.parse(('end_br_header_top',))
    parser.delete_first_token()
    return BRHeaderTopNode(nodelist)

class BRHeaderTopNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    def render(self, context):
        content = self.nodelist.render(context)
        return format_html('<div class="header-top">{}</div>', mark_safe(content))

# Tag: br_header_bottom
@register.tag(name='br_header_bottom')
def do_br_header_bottom(parser, token):
    nodelist = parser.parse(('end_br_header_bottom',))
    parser.delete_first_token()
    return BRHeaderBottomNode(nodelist)

class BRHeaderBottomNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    def render(self, context):
        # Renderiza o conteúdo interno primeiro (o br_header_menu)
        content = self.nodelist.render(context)
        
        # Pega o HTML da busca que foi colocado no contexto
        search_html = context.get('br_header_search_html', '')
        
        # Limpa a variável para não vazar
        if 'br_header_search_html' in context:
            del context['br_header_search_html']
            
        return format_html(
            '<div class="header-bottom">{}{}</div>', 
            mark_safe(content), 
            mark_safe(search_html)
        )

# Tag: br_header_actions
@register.tag(name='br_header_actions')
def do_br_header_actions(parser, token):
    nodelist = parser.parse(('end_br_header_actions',))
    parser.delete_first_token()
    return BRHeaderActionsNode(nodelist)

class BRHeaderActionsNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    def render(self, context):
        content = self.nodelist.render(context)
        return format_html('<div class="header-actions">{}</div>', mark_safe(content))

# Tag: br_header_login
@register.tag(name='br_header_login')
def do_br_header_login(parser, token):
    nodelist = parser.parse(('end_br_header_login',))
    parser.delete_first_token()
    return BRHeaderLoginNode(nodelist)

class BRHeaderLoginNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    def render(self, context):
        content = self.nodelist.render(context)
        return format_html('<div class="header-login">{}</div>', mark_safe(content))

# Tag: br_list
@register.tag(name='br_list')
def do_br_list(parser, token):
    nodelist = parser.parse(('end_br_list',))
    parser.delete_first_token()
    return BRListNode(nodelist)

class BRListNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    def render(self, context):
        content = self.nodelist.render(context)
        return format_html('<div class="br-list">{}</div>', mark_safe(content))

# =========================
# BLOCO: LOGO E TÍTULOS
# =========================

@register.simple_tag(takes_context=True)
def br_header_logo(context, src, alt, signature="", signature_style="", href=""):
    resolved_src = resolve_variable(src, context)
    resolved_alt = resolve_variable(alt, context)
    logo_html = format_html('<img src="{}" alt="{}" />', resolved_src, resolved_alt)

    if href:
        resolved_href = resolve_variable(href, context)
        logo_html = format_html('<a href="{}">{}</a>', resolved_href, logo_html)

    if signature:
        resolved_signature = resolve_variable(signature, context)
        style_attr = ''
        if signature_style:
            resolved_style = resolve_variable(signature_style, context)
            style_attr = format_html(' style="{}"', resolved_style)
        return format_html(
            '<div class="header-logo">{}<span class="br-divider vertical"></span>'
            '<div class="header-sign"{}>{}</div></div>',
            logo_html, style_attr, resolved_signature
        )

    return format_html('<div class="header-logo">{}</div>', logo_html)

# --- Tags de Texto Explícitas ---

class TextNode(template.Node):
    def __init__(self, nodelist, element, default_class, style):
        self.nodelist = nodelist
        self.element = element
        self.default_class = default_class
        self.style = style
    def render(self, context):
        content = self.nodelist.render(context)
        style_attr = ''
        if self.style:
            resolved_style = resolve_variable(self.style, context)
            style_attr = format_html(' style="{}"', resolved_style)
        return format_html('<{0} class="{1}"{2}>{3}</{0}>', self.element, self.default_class, style_attr, mark_safe(content))

@register.tag(name='br_header_title')
def do_br_header_title(parser, token):
    bits = token.split_contents()
    style = None
    if len(bits) > 1 and 'style=' in bits[1]:
        style = bits[1].split('=', 1)[1]
    nodelist = parser.parse(('end_br_header_title',))
    parser.delete_first_token()
    return TextNode(nodelist, 'div', 'header-title', style)

@register.tag(name='br_header_subtitle')
def do_br_header_subtitle(parser, token):
    bits = token.split_contents()
    style = None
    if len(bits) > 1 and 'style=' in bits[1]:
        style = bits[1].split('=', 1)[1]
    nodelist = parser.parse(('end_br_header_subtitle',))
    parser.delete_first_token()
    return TextNode(nodelist, 'div', 'header-subtitle', style)

@register.tag(name='br_list_header')
def do_br_list_header(parser, token):
    bits = token.split_contents()
    style = None
    if len(bits) > 1 and 'style=' in bits[1]:
        style = bits[1].split('=', 1)[1]
    nodelist = parser.parse(('end_br_list_header',))
    parser.delete_first_token()
    return BRListHeaderNode(nodelist, style)

class BRListHeaderNode(template.Node):
    def __init__(self, nodelist, style):
        self.nodelist = nodelist
        self.style = style
    def render(self, context):
        content = self.nodelist.render(context)
        style_attr = ''
        if self.style:
            resolved_style = resolve_variable(self.style, context)
            style_attr = format_html(' style="{}"', resolved_style)
        return format_html('<div class="header"><div class="title"{}>{}</div></div>', style_attr, mark_safe(content))

# =========================
# BLOCO: MENU E DROPDOWNS
# =========================

@register.tag(name='br_header_menu')
def do_br_header_menu(parser, token):
    bits = token.split_contents()
    icon_style = None
    if len(bits) > 1 and 'icon_style=' in bits[1]:
        icon_style = bits[1].split('=', 1)[1]
    nodelist = parser.parse(('end_br_header_menu',))
    parser.delete_first_token()
    return BRHeaderMenuNode(nodelist, icon_style)

class BRHeaderMenuNode(template.Node):
    def __init__(self, nodelist, icon_style):
        self.nodelist = nodelist
        self.icon_style = icon_style
    def render(self, context):
        content = self.nodelist.render(context)
        style_attr = ''
        if self.icon_style:
            resolved_style = resolve_variable(self.icon_style, context)
            style_attr = format_html(' style="{}"', resolved_style)
        return format_html(
            '''<div class="header-menu">
                <div class="header-menu-trigger">
                    <button class="br-button small circle" type="button" aria-label="Menu" data-toggle="menu" data-target="#main-navigation" id="navigation">
                        <i class="fas fa-bars" aria-hidden="true"{}></i>
                    </button>
                </div>
                <div class="header-info">{}</div>
            </div>''',
            style_attr,
            mark_safe(content)
        )

class DropdownNode(template.Node):
    def __init__(self, nodelist, tag_class, icon_class, extra_classes, icon_style):
        self.nodelist = nodelist
        self.tag_class = tag_class
        self.icon_class = icon_class
        self.extra_classes = extra_classes
        self.icon_style = icon_style

    def render(self, context):
        content = self.nodelist.render(context)
        aria_label = "Abrir " + self.tag_class.replace('-', ' ').replace('header', '').strip().title()
        extra_classes_str = f" {resolve_variable(self.extra_classes, context)}" if self.extra_classes else ""
        icon_style_attr = ''
        if self.icon_style:
            resolved_style = resolve_variable(self.icon_style, context)
            icon_style_attr = format_html(' style="{}"', resolved_style)

        html = format_html(
            '''<div class="{0} dropdown{1}">
                <button class="br-button circle small" type="button" data-toggle="dropdown" aria-label="{2}">
                    <i class="fas {3}" aria-hidden="true"{4}></i>
                </button>
                {5}
            </div>''',
            self.tag_class, extra_classes_str, aria_label, self.icon_class, icon_style_attr, mark_safe(content)
        )
        if 'links' in self.tag_class:
            html += mark_safe('<span class="br-divider vertical mx-half mx-sm-1"></span>')
        return html

def create_dropdown_tag(name, tag_class, icon_class):
    @register.tag(name=name)
    def dropdown_tag_func(parser, token):
        bits = token.split_contents()
        icon_style = None
        extra_classes = None
        for bit in bits[1:]:
            if bit.startswith('icon_style='):
                icon_style = bit.split('=', 1)[1]
            elif bit.startswith('class='):
                extra_classes = bit.split('=', 1)[1]
        nodelist = parser.parse((f'end_{name}',))
        parser.delete_first_token()
        return DropdownNode(nodelist, tag_class, icon_class, extra_classes, icon_style)
    return dropdown_tag_func

create_dropdown_tag('br_header_links', 'header-links', 'fa-ellipsis-v')
create_dropdown_tag('br_header_functions', 'header-functions', 'fa-th')

# =========================
# BLOCO: ITENS DE LISTA
# =========================

@register.tag(name='br_header_link_item')
def do_br_header_link_item(parser, token):
    bits = token.split_contents()
    kwargs = {'href_str': None, 'extra_classes_expr': None, 'style_expr': None}

    for bit in bits[1:]:
        key, value = bit.split('=', 1)
        if key == 'href':
            kwargs['href_str'] = value
        elif key == 'extra_classes':
            kwargs['extra_classes_expr'] = parser.compile_filter(value)
        elif key == 'style':
            kwargs['style_expr'] = parser.compile_filter(value)

    nodelist = parser.parse(('end_br_header_link_item',))
    parser.delete_first_token()
    
    return BRHeaderLinkItemNode(nodelist, **kwargs)

class BRHeaderLinkItemNode(template.Node):
    def __init__(self, nodelist, href_str, extra_classes_expr, style_expr):
        self.nodelist = nodelist
        self.href_str = href_str
        self.extra_classes_expr = extra_classes_expr
        self.style_expr = style_expr

    def render(self, context):
        from django.template import Variable, VariableDoesNotExist

        content = self.nodelist.render(context)
        resolved_href = "#"

        if self.href_str:
            parts = self.href_str.split('|default:')
            primary_expr_str = parts[0].strip()
            secondary_expr_str = parts[1].strip() if len(parts) > 1 else None

            try:
                primary_value = Variable(primary_expr_str).resolve(context)
                if primary_value:
                    resolved_href = primary_value
            except VariableDoesNotExist:
                pass

            if resolved_href == "#" and secondary_expr_str:
                try:
                    base_obj = Variable(secondary_expr_str.split('.')[0]).resolve(context)
                    
                    if base_obj and hasattr(base_obj, 'url'):
                        url = getattr(base_obj, 'url')
                        if url:
                            resolved_href = url
                except VariableDoesNotExist:
                    pass
                except Exception:
                    pass

        # Resolve classes e estilos
        extra_classes = self.extra_classes_expr.resolve(context) if self.extra_classes_expr else ""
        style = self.style_expr.resolve(context) if self.style_expr else ""
        style_attr = format_html(' style="{}"', style) if style else ""

        return format_html(
            '<a class="br-item {}" href="{}"{}>{}</a>',
            extra_classes,
            resolved_href,
            style_attr,
            mark_safe(content)
        )

@register.tag(name='br_function_item')
def do_br_function_item(parser, token):
    bits = token.split_contents()
    kwargs = {
        'icon_class': None, 'label': None, 'aria_label': None, 
        'extra_classes': None, 'icon_style': None, 'label_style': None,
        'href': None
    }
    for bit in bits[1:]:
        if '=' in bit:
            key, value = bit.split('=', 1)
            if key in kwargs:
                kwargs[key] = parser.compile_filter(value)
    
    return BRFunctionItemNode(**kwargs)

class BRFunctionItemNode(template.Node):
    def __init__(self, icon_class, label, aria_label, extra_classes, icon_style, label_style, href):
        self.icon_class = icon_class
        self.label = label
        self.aria_label = aria_label
        self.extra_classes = extra_classes
        self.icon_style = icon_style
        self.label_style = label_style
        self.href = href

    def render(self, context):
        def resolve_filter(f):
            return f.resolve(context) if f else ""

        resolved_label = resolve_filter(self.label)
        resolved_aria_label = resolve_filter(self.aria_label) or resolved_label
        resolved_icon_class = resolve_filter(self.icon_class)
        resolved_href = resolve_filter(self.href)

        extra_classes_str = resolve_filter(self.extra_classes)
        icon_style_attr = format_html(' style="{}"', resolve_filter(self.icon_style)) if self.icon_style else ""
        label_style_attr = format_html(' style="{}"', resolve_filter(self.label_style)) if self.label_style else ""

        inner_content = format_html(
            '<i class="fas {}" aria-hidden="true"{}></i><span class="text"{}>{}</span>',
            resolved_icon_class, icon_style_attr, label_style_attr, resolved_label
        )

        if resolved_href:
            return format_html(
                '''<div class="br-item {}">
                    <a class="br-button circle small" href="{}" aria-label="{}">
                        {}
                    </a>
                </div>''',
                extra_classes_str, resolved_href, resolved_aria_label, inner_content
            )
        else:
            return format_html(
                '''<div class="br-item {}">
                    <button class="br-button circle small" type="button" aria-label="{}">
                        {}
                    </button>
                </div>''',
                extra_classes_str, resolved_aria_label, inner_content
            )

# =========================
# BLOCO: BUSCA E LOGIN
# =========================

@register.simple_tag(takes_context=True)
def br_header_search(context, placeholder="O que você procura?", icon_style="", action_url=None):
    """
    Renderiza um campo de busca genérico para o header.
    - placeholder: texto exibido no input
    - icon_style: CSS inline opcional para o ícone
    - action_url: para onde enviar a busca (se None, tenta resolver 'search', senão usa '/search/')
    """

    # Resolve estilos
    icon_style_attr = f' style="{icon_style}"' if icon_style else ""

    # Resolve URL de destino da busca
    if action_url is None:
        try:
            action_url = reverse("search")
        except NoReverseMatch:
            action_url = "/search/"

    # Monta o HTML
    search_html = format_html(
        '''
        <div class="header-search">
            <form method="get" action="{}">
                <div class="br-input has-icon">
                    <label for="searchbox-header">Texto da pesquisa</label>
                    <input id="searchbox-header" type="text" name="query" placeholder="{}"/>
                    <button class="br-button circle small" type="submit" aria-label="Pesquisar">
                        <i class="fas fa-search" aria-hidden="true"></i>
                    </button>
                </div>
            </form>
            <button class="br-button circle search-close ml-1" type="button" aria-label="Fechar Busca" data-dismiss="search">
                <i class="fas fa-times" aria-hidden="true"{}></i>
            </button>
        </div>
        ''',
        action_url,
        placeholder,
        icon_style_attr,
    )

    return search_html

@register.simple_tag(takes_context=True)
def br_header_search_trigger(context, icon_style=""):
    icon_style_attr = ''
    if icon_style:
        resolved_style = resolve_variable(icon_style, context)
        icon_style_attr = format_html(' style="{}"', resolved_style)
    return mark_safe(
        f'''<div class="header-search-trigger">
            <button class="br-button circle" type="button" aria-label="Abrir Busca" data-toggle="search" data-target=".header-search">
                <i class="fas fa-search" aria-hidden="true"{icon_style_attr}></i>
            </button>
        </div>'''
    )

@register.simple_tag
def br_header_signin_button():
    return mark_safe(
        '''<div class="header-sign-in">
            <button class="br-sign-in small" type="button" data-trigger="login">
                <i class="fas fa-user" aria-hidden="true"></i><span class="d-sm-inline">Entrar</span>
            </button>
        </div>'''
    )

@register.simple_tag
def br_header_avatar():
    return mark_safe('<div class="header-avatar"></div>')
