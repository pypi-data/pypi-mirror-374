from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.template.base import token_kwargs

register = template.Library()

@register.tag(name='br_menu_row')
def do_br_menu_row(parser, token):
    """
    Renderiza uma linha (row) para agrupar elementos do menu.
    Usado para estruturar o layout do menu principal.
    """
    nodelist = parser.parse(('end_br_menu_row',))
    parser.delete_first_token()
    return BRMenuRowNode(nodelist)

class BRMenuRowNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        content = self.nodelist.render(context)
        return format_html('<div class="row">{}</div>', mark_safe(content))

@register.tag(name='br_menu')
def do_br_menu(parser, token):
    """
    Tag de bloco principal para o menu.
    Cria a estrutura básica do menu, incluindo o painel de conteúdo e o scrim (camada de fundo).
    Abre a tag `br_menu` e fecha com `end_br_menu`.
    """
    nodelist = parser.parse(('end_br_menu',))
    parser.delete_first_token()
    return BRMenuNode(nodelist)

class BRMenuNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        content = self.nodelist.render(context)
        return format_html("""
            <div class="br-menu" id="main-navigation">
                <div class="menu-container">
                <div class="menu-panel">{}</div>
                <div class="menu-scrim" data-dismiss="menu" tabindex="0"></div>
                </div>
            </div>
            """, 
            content
        )

@register.tag(name='br_menu_header')
def do_br_menu_header(parser, token):
    """
    Tag de bloco para o cabeçalho do menu.
    Envolve o conteúdo do cabeçalho do menu, como título e logo.
    Adiciona um botão de fechar o menu com ícone de 'x'.
    """
    nodelist = parser.parse(('end_br_menu_header',))
    parser.delete_first_token()
    return BRMenuHeaderNode(nodelist)

class BRMenuHeaderNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    
    def render(self, context):
        content = self.nodelist.render(context)
        return mark_safe(f'''
            <div class="menu-header">
                {content}
                <div class="menu-close">
                    <button class="br-button circle" type="button" aria-label="Fechar o menu" data-dismiss="menu">
                        <i class="fas fa-times" aria-hidden="true"></i>
                    </button>
                </div>
            </div>
        ''')

@register.simple_tag(name='br_menu_header_logo')
def br_menu_header_logo(src):
    """
    Tag simples para exibir o logo no cabeçalho do menu.
    Recebe o caminho da imagem (`src`) como argumento.
    Retorna uma tag `<img>` com o src e um alt padrão.
    """
    return mark_safe(f'<img src="{src}" alt="Imagem ilustrativa"/>')

class BrMenuTitleNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        content = self.nodelist.render(context)
        return format_html('<div class="menu-title">{}</div>', content)

@register.tag
def br_menu_title(parser, token):
    """
    Tag de bloco para o título do menu.
    Envolve o texto do título do menu.
    """
    nodelist = parser.parse(['end_br_menu_title'])
    parser.delete_first_token()
    return BrMenuTitleNode(nodelist)
    
class BrMenuTitleLogoNode(template.Node):
    def __init__(self, src_expr=None, alt_expr=None):
        self.src_expr = src_expr
        self.alt_expr = alt_expr

    def render(self, context):
        """
        Nó interno para a tag `br_menu_title_logo`.
        Renderiza uma tag `<img>` com src e alt dinâmicos.
        Resolve os valores de src e alt a partir do contexto do template.
        """
        src = "data:image/png;base64,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"
        alt = "Imagem ilustrativa"
        try:
            if self.src_expr:
                src_resolved = self.src_expr.resolve(context)
                if src_resolved:
                    src = src_resolved
        except template.VariableDoesNotExist:
            pass

        try:
            if self.alt_expr:
                alt_resolved = self.alt_expr.resolve(context)
                if alt_resolved:
                    alt = alt_resolved
        except template.VariableDoesNotExist:
            pass

        return format_html('<img src="{}" alt="{}"/>', src, alt)

class BrMenuTitleTextNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        """
        Nó interno para a tag `br_menu_title_text`.
        Renderiza o texto do título dentro de uma tag `<span>`.
        """
        content = self.nodelist.render(context)
        return format_html('<span>{}</span>', content)

@register.tag
def br_menu_title_text(parser, token):
    """
    Tag de bloco para o texto do título do menu.
    """
    nodelist = parser.parse(['end_br_menu_title_text'])
    parser.delete_first_token()
    return BrMenuTitleTextNode(nodelist)

@register.tag
def br_menu_title_logo(parser, token):
    """
    Tag de bloco para o logo do título do menu.
    Recebe os argumentos `src` e `alt` para a imagem.
    Compila as expressões de filtro para resolver variáveis no contexto do template.
    """
    bits = token.split_contents()
    src_expr = None
    alt_expr = None

    for bit in bits[1:]:
        if bit.startswith("src="):
            src_expr = parser.compile_filter(bit.split("=", 1)[1])
        elif bit.startswith("alt="):
            alt_expr = parser.compile_filter(bit.split("=", 1)[1])

    return BrMenuTitleLogoNode(src_expr, alt_expr)

@register.tag(name='br_menu_body')
def do_br_menu_body(parser, token):
    """
    Tag de bloco para o corpo do menu.
    Envolve a navegação principal (`nav`).
    Adiciona a classe `menu-body` e o atributo `role="tree"`.
    """
    nodelist = parser.parse(('end_br_menu_body',))
    parser.delete_first_token()
    return BRMenuBodyNode(nodelist)

class BRMenuBodyNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    
    def render(self, context):
        content = self.nodelist.render(context)
        return mark_safe(f'<nav class="menu-body" role="tree">{content}</nav>')


@register.tag(name='br_menu_folder')
def do_br_menu_folder(parser, token):
    """
    Tag de bloco para criar uma pasta/seção no menu.
    Gera uma div com a classe `menu-folder`.
    """
    nodelist = parser.parse(('end_br_menu_folder',))
    parser.delete_first_token()
    return BRMenuFolderNode(nodelist)

class BRMenuFolderNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    
    def render(self, context):
        content = self.nodelist.render(context)
        return mark_safe(f'<div class="menu-folder">{content}</div>')

@register.tag(name='br_menu_item')
def do_br_menu_item(parser, token):
    """
    Tag de bloco para criar um item de menu clicável.
    Recebe os argumentos `href` e opcionalmente `icone`.
    Gera uma tag `<a>` com as classes `menu-item` e `divider`, e o atributo `role="treeitem"`.
    Resolve as variáveis `href` e `icone` do contexto.
    """
    bits = token.split_contents()
    tag_name = bits[0]
    
    # Extrai os argumentos kwargs
    kwargs = {}
    for bit in bits[1:]:
        if '=' in bit:
            name, value = bit.split('=', 1)
            kwargs[name] = value
        else:
            raise template.TemplateSyntaxError(f"Argumento inválido em '{tag_name}': '{bit}'. Esperado 'nome=valor'.")

    href_expr = kwargs.get('href')
    icon_expr = kwargs.get('icone')

    if not href_expr:
        raise template.TemplateSyntaxError(f"'{tag_name}' requer o argumento 'href'")

    # Compila as expressões para que possam ser resolvidas depois
    href_filter_expression = parser.compile_filter(href_expr)
    
    icon_filter_expression = None
    if icon_expr:
        icon_filter_expression = parser.compile_filter(icon_expr)

    nodelist = parser.parse(('end_br_menu_item',))
    parser.delete_first_token()
    
    return BRMenuItemNode(nodelist, href_filter_expression, icon_filter_expression)

class BRMenuItemNode(template.Node):
    def __init__(self, nodelist, href_filter_expression, icon_filter_expression):
        self.nodelist = nodelist
        self.href = href_filter_expression
        self.icon = icon_filter_expression

    def render(self, context):
        # Resolve a expressão do href usando o contexto atual do template
        href = self.href.resolve(context)

        icon_html = ''
        if self.icon:
            # Resolve a expressão do ícone, se existir
            icon = self.icon.resolve(context)
            if icon:
                icon_html = format_html(
                    '<span class="icon"><i class="fas {}" aria-hidden="true"></i></span>',
                    icon
                )

        content = self.nodelist.render(context)

        return format_html(
            '<a class="menu-item divider" href="{}" role="treeitem">{}<span class="content">{}</span></a>',
            href,
            mark_safe(icon_html),
            content
        )

@register.tag(name='br_menu_divider_item')
def do_br_menu_divider_item(parser, token):
    """
    Tag de bloco para um item de menu divisor.
    Parecido com `br_menu_item`, mas com comportamento de divisor.
    Recebe os argumentos `href` e opcionalmente `icone`.
    """
    try:
        bits = token.split_contents()
        tag_name = bits[0]
        kwargs = token_kwargs(bits[1:], parser)
        href = kwargs.get('href', '"javascript: void(0)"')
        icon = kwargs.get('icone', '""')
    except Exception as e:
        raise template.TemplateSyntaxError(f"Erro na tag {tag_name}: {str(e)}")

    nodelist = parser.parse(('end_br_menu_divider_item',))
    parser.delete_first_token()
    return BRMenuDividerItemNode(nodelist, href, icon)

class BRMenuDividerItemNode(template.Node):
    def __init__(self, nodelist, href, icon):
        self.nodelist = nodelist
        self.href = href
        self.icon = icon

    def render(self, context):
        href = self.href.resolve(context) if self.href else "javascript: void(0)"
        icon = self.icon.resolve(context) if self.icon else ""

        content = self.nodelist.render(context).strip()
        icon_html = ''
        if icon:
            icon_html = format_html(
                '<span class="icon"><i class="{}" aria-hidden="true"></i></span>', icon
            )

        return format_html(
            '<a class="menu-item divider" href="{}" role="treeitem">{}{}</a>',
            href,
            mark_safe(icon_html),
            format_html('<span class="content">{}</span>', content)
        )

@register.tag(name='br_menu_footer')
def do_br_menu_footer(parser, token):
    """
    Tag de bloco para o rodapé do menu.
    Gera uma div com a classe `menu-footer`.
    """
    nodelist = parser.parse(('end_br_menu_footer',))
    parser.delete_first_token()
    return BRMenuFooterNode(nodelist)

class BRMenuFooterNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    
    def render(self, context):
        content = self.nodelist.render(context)
        return format_html('<div class="menu-footer">{}</div>', mark_safe(content))

class BRMenuFooterLogosNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        """
        Tag de bloco para a seção de logos no rodapé do menu.
        Gera uma div com a classe `menu-logos`.
        """
        content = self.nodelist.render(context).strip()
        return format_html('<div class="menu-logos">{}</div>', mark_safe(content))

@register.tag(name='br_menu_footer_logos')
def do_br_menu_footer_logos(parser, token):
    """
    Tag de bloco para a seção de logos no rodapé do menu.
    Gera uma div com a classe `menu-logos`.
    """
    nodelist = parser.parse(('end_br_menu_footer_logos',))
    parser.delete_first_token()
    return BRMenuFooterLogosNode(nodelist)

class BRMenuLogoNode(template.Node):
    def __init__(self, src_expr, alt_expr):
        self.src_expr = src_expr
        self.alt_expr = alt_expr or template.FilterExpression('"Imagem ilustrativa"', parser=None)

    def render(self, context):
        """
        Nó interno para a tag `br_menu_logo`.
        Renderiza a tag `<img>` para o logo no rodapé.
        Lida com a resolução de variáveis para src e alt, com valores padrão.
        """
        try:
            src = self.src_expr.resolve(context)
        except template.VariableDoesNotExist:
            src = "data:image/png;base64,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"

        try:
            alt = self.alt_expr.resolve(context)
        except template.VariableDoesNotExist:
            alt = "Imagem ilustrativa"

        return format_html('<img src="{}" alt="{}"/>', src, alt)

@register.tag(name='br_menu_logo')
def do_br_menu_logo(parser, token):
    """
    Tag para exibir um logo no rodapé do menu.
    Requer o argumento `src` e aceita opcionalmente `alt`.
    """
    bits = token.split_contents()
    src_expr = None
    alt_expr = None

    for bit in bits[1:]:
        if bit.startswith("src="):
            src_expr = parser.compile_filter(bit.split("=", 1)[1])
        elif bit.startswith("alt="):
            alt_expr = parser.compile_filter(bit.split("=", 1)[1])

    if src_expr is None:
        raise template.TemplateSyntaxError("A tag 'br_menu_logo' requer o argumento 'src'.")

    return BRMenuLogoNode(src_expr, alt_expr)

@register.tag(name="br_menu_links")
def do_br_menu_links(parser, token):
    """
    Tag de bloco para a seção de links no rodapé do menu.
    Gera uma div com a classe `menu-links`.
    """
    nodelist = parser.parse(("end_br_menu_links",))
    parser.delete_first_token()
    return BRMenuLinksNode(nodelist)

class BRMenuLinksNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        content = self.nodelist.render(context).strip()
        return format_html('<div class="menu-links">{}</div>', mark_safe(content))
    
@register.tag(name='br_menu_list')
def do_br_menu_list(parser, token):
    """
    Tag de bloco para criar uma lista (`<ul>`) no menu.
    Usada para agrupar itens de lista (`<li>`).
    """
    nodelist = parser.parse(('end_br_menu_list',))
    parser.delete_first_token()
    return BRMenuListNode(nodelist)

class BRMenuListNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        content = self.nodelist.render(context)
        return format_html('<ul>{}</ul>', mark_safe(content))
    
@register.tag(name='br_menu_list_item')
def do_br_menu_list_item(parser, token):
    """
    Tag de bloco para criar um item de lista (`<li>`) no menu.
    """
    nodelist = parser.parse(('end_br_menu_list_item',))
    parser.delete_first_token()
    return BRMenuListItemNode(nodelist)

class BRMenuListItemNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        content = self.nodelist.render(context)
        return format_html('<li>{}</li>', mark_safe(content))
    
@register.tag(name="br_menu_link")
def do_br_menu_link(parser, token):
    """
    Tag de bloco para um link simples no menu.
    Recebe os argumentos opcionais `href` e `icone`.
    Gera uma tag `<a>` com o conteúdo e o ícone.
    """
    bits = token.split_contents()
    href_expr = None
    icon_expr = None

    for bit in bits[1:]:
        if bit.startswith("href="):
            href_expr = parser.compile_filter(bit.split("=", 1)[1])
        elif bit.startswith("icone=") or bit.startswith("icon="):
            icon_expr = parser.compile_filter(bit.split("=", 1)[1])

    nodelist = parser.parse(("end_br_menu_link",))
    parser.delete_first_token()
    return BRMenuLinkNode(nodelist, href_expr, icon_expr)

class BRMenuLinkNode(template.Node):
    def __init__(self, nodelist, href_expr=None, icon_expr=None):
        self.nodelist = nodelist
        self.href_expr = href_expr
        self.icon_expr = icon_expr

    def render(self, context):
        content = self.nodelist.render(context).strip()

        href = "javascript: void(0)"
        icon_class = "fas fa-external-link-square-alt"

        if self.href_expr:
            try:
                href = self.href_expr.resolve(context)
            except template.VariableDoesNotExist:
                pass

        if self.icon_expr:
            try:
                resolved_icon = self.icon_expr.resolve(context)
                if resolved_icon:
                    icon_class = f"fas fa-{resolved_icon}"
            except template.VariableDoesNotExist:
                pass

        return format_html(
            '<a href="{}"><span class="mr-1">{}</span><i class="{}" aria-hidden="true"></i></a>',
            href, content, icon_class
        )

@register.tag(name='br_menu_social_network')
def do_br_menu_social_network(parser, token):
    """
    Tag de bloco para a seção de redes sociais no menu.
    Gera uma div com a classe `social-network`.
    """
    nodelist = parser.parse(('end_br_menu_social_network',))
    parser.delete_first_token()
    return BRMenuSocialNetworkNode(nodelist)

class BRMenuSocialNetworkNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    
    def render(self, context):
        content = self.nodelist.render(context)
        return mark_safe(f'''
        <div class="social-network">
            {content}
        </div>
        ''')

@register.tag(name='br_menu_social_network_title')
def do_br_menu_social_network_title(parser, token):
    """
    Tag de bloco para o título da seção de redes sociais.
    Gera uma div com a classe `social-network-title`.
    """
    nodelist = parser.parse(('end_br_menu_social_network_title',))
    parser.delete_first_token()
    return BRMenuSocialNetworkTitleNode(nodelist)

class BRMenuSocialNetworkTitleNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    
    def render(self, context):
        content = self.nodelist.render(context)
        return mark_safe(f'<div class="social-network-title">{content}</div>')

@register.simple_tag(name='br_menu_social_network_icons', takes_context=True)
def br_menu_social_network_icons(context, href, icon, extra_classes=""):
    """
    Tag simples para ícones de redes sociais.
    Recebe `href`, `icon` (classe do ícone) e `extra_classes` como argumentos.
    Renderiza um botão redondo com o link e o ícone.
    """
    # Remove aspas se for um valor literal
    href = href.strip('"\'')
    
    # Tenta resolver como variável de contexto se estiver entre {{ }}
    if href.startswith('{{') and href.endswith('}}'):
        var_name = href[2:-2].strip()
        try:
            href = template.Variable(var_name).resolve(context)
        except template.VariableDoesNotExist:
            href = var_name
    
    return mark_safe(f'''
    <a class="br-button circle {extra_classes}" href="{href}" aria-label="Compartilhar por {icon}">
        <i class="fab {icon}" aria-hidden="true"></i>
    </a>
    ''')

@register.tag(name='br_menu_copyright')
def do_br_menu_copyright(parser, token):
    """
    Tag de bloco para a seção de copyright no menu.
    Gera uma div com a classe `menu-info` e o texto com a classe `text-center text-down-01`.
    """
    nodelist = parser.parse(('end_br_menu_copyright',))
    parser.delete_first_token()
    return BRMenuCopyrightNode(nodelist)

class BRMenuCopyrightNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    
    def render(self, context):
        content = self.nodelist.render(context).strip()
        return format_html(
            '<div class="menu-info"><div class="text-center text-down-01">{}</div></div>',
            mark_safe(content)
        )

class BrMenuToggleNode(template.Node):
    def __init__(self, label_expr=None, target_expr=None):
        self.label_expr = label_expr
        self.target_expr = target_expr

    def render(self, context):
        """
        Nó interno para a tag `br_menu_toggle`.
        Renderiza um botão para abrir o menu.
        Lida com a resolução de variáveis para o label e o alvo (`target`).
        """
        label = "Menu"
        target = "#main-navigation"

        if self.label_expr:
            try:
                resolved_label = self.label_expr.resolve(context)
                if resolved_label:
                    label = resolved_label
            except template.VariableDoesNotExist:
                pass

        if self.target_expr:
            try:
                resolved_target = self.target_expr.resolve(context)
                if resolved_target:
                    target = resolved_target
            except template.VariableDoesNotExist:
                pass

        return format_html(
            """
            <div class="col">
              <div class="d-flex align-items-center">
                <div>
                  <button class="br-button small circle" type="button" aria-label="Menu" data-toggle="menu" data-target="{}">
                    <i class="fas fa-bars" aria-hidden="true"></i>
                  </button>
                </div>
                <div class="ml-3">{}</div>
              </div>
            </div>
            """,
            target, label
        )

@register.tag
def br_menu_toggle(parser, token):
    """
    Tag de bloco para criar um botão de "toggle" (alternar) para o menu.
    Recebe os argumentos opcionais `label` e `target`.
    """
    bits = token.split_contents()
    label_expr = None
    target_expr = None

    for bit in bits[1:]:
        if bit.startswith("label="):
            label_expr = parser.compile_filter(bit.split("=", 1)[1])
        elif bit.startswith("target="):
            target_expr = parser.compile_filter(bit.split("=", 1)[1])

    return BrMenuToggleNode(label_expr, target_expr)
