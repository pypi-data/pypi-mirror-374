from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.template.base import token_kwargs

register = template.Library()

# --- TAGS DE BLOCO PRINCIPAIS DO FOOTER (RODAPÉ) ---

@register.tag(name='br_footer')
def do_footer(parser, token):
    bits = token.split_contents()
    extra_class = ''

    for bit in bits[1:]:
        if bit.startswith('class='):
            extra_class = bit.split('=', 1)[1]

    nodelist = parser.parse(('end_br_footer',))
    parser.delete_first_token()
    return FooterNode(nodelist, extra_class)

class FooterNode(template.Node):
    def __init__(self, nodelist, extra_class):
        self.nodelist = nodelist
        self.extra_class = extra_class

    def render(self, context):
        content = self.nodelist.render(context)
        
        try:
            resolved_extra = template.Variable(self.extra_class).resolve(context)
        except:
            resolved_extra = self.extra_class.strip('"') if self.extra_class else ''
        
        full_class = 'br-footer'
        if resolved_extra:
            full_class += f' {resolved_extra}'

        return format_html('<footer class="{}">{}</footer>', full_class, mark_safe(content))

@register.tag(name='br_footer_main')
def do_footer_main(parser, token):
    """
    Agrupa a parte principal do footer dentro de um container-lg.
    Isso resolve o problema do container global.
    """
    nodelist = parser.parse(('end_br_footer_main',))
    parser.delete_first_token()
    return MainContentNode(nodelist)

class MainContentNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    
    def render(self, context):
        content = self.nodelist.render(context)
        return format_html('<div class="container-lg">{}</div>', mark_safe(content))

# --- TAGS DE COLUNAS E ITENS DO FOOTER ---

@register.tag(name='br_footer_columns_group')
def do_footer_columns_group(parser, token):
    """Envolve todas as colunas no wrapper horizontal necessário."""
    nodelist = parser.parse(('end_br_footer_columns_group',))
    parser.delete_first_token()
    return ColumnsGroupNode(nodelist)

class ColumnsGroupNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    
    def render(self, context):
        content = self.nodelist.render(context)
        return format_html('<div class="br-list horizontal" data-toggle="data-toggle" data-sub="data-sub">{}</div>', mark_safe(content))

@register.tag(name='br_footer_column')
def do_footer_column(parser, token):
    nodelist = parser.parse(('end_br_footer_column',))
    parser.delete_first_token()
    return FooterColumnNode(nodelist)

class FooterColumnNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    
    def render(self, context):
        content = self.nodelist.render(context)
        # Cada coluna é um bloco completo e autocontido.
        return format_html('<div class="col-2">{}</div>', mark_safe(content))

@register.tag(name='br_item_header')
def do_item_header(parser, token):
    nodelist = parser.parse(('end_br_item_header',))
    parser.delete_first_token()
    return ItemHeaderNode(nodelist)

class ItemHeaderNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    
    def render(self, context):
        content = self.nodelist.render(context)
        return format_html(
            '''<a class="br-item header" href="javascript:void(0)">
                <div class="content text-down-01 text-bold text-uppercase">{}</div>
                <div class="support"><i class="fas fa-angle-down" aria-hidden="true"></i></div>
            </a>''',
            mark_safe(content)
        )

@register.tag(name='br_footer_list')
def do_footer_list(parser, token):
    nodelist = parser.parse(('end_br_footer_list',))
    parser.delete_first_token()
    return FooterListNode(nodelist)

class FooterListNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    
    def render(self, context):
        content = self.nodelist.render(context)
        return format_html(
            '<div class="br-list"><span class="br-divider d-md-none"></span>{}<span class="br-divider d-md-none"></span></div>',
            mark_safe(content)
        )

@register.tag(name='br_item')
def do_item(parser, token):
    try:
        tag_name, href = token.split_contents()
    except ValueError:
        href = '"#"'
    
    nodelist = parser.parse(('end_br_item',))
    parser.delete_first_token()
    return ItemNode(nodelist, href)

class ItemNode(template.Node):
    def __init__(self, nodelist, href):
        self.nodelist = nodelist
        self.href = href
    
    def render(self, context):
        content = self.nodelist.render(context)
        resolved_href = template.Variable(self.href).resolve(context)
        return format_html('<a class="br-item" href="{}"><div class="content">{}</div></a>', resolved_href, mark_safe(content))

# --- TAGS DE LOGO, REDES SOCIAIS E COPYRIGHT DO FOOTER ---

@register.simple_tag
def br_logo(src, alt="", extra_classes="", extra_styles=""):
    """
    Renderiza o logo com ou sem wrapper <div class="logo">.

    Se o usuário fornecer extra_classes ou extra_styles, assume que quer controle total
    e remove o wrapper por padrão.
    """
    img_html = format_html(
        '<img src="{}" alt="{}" class="{}" style="{}"/>',
        src, alt, extra_classes, extra_styles
    )

    # Se o usuário passou estilos ou classes, damos controle total (sem <div class="logo">)
    if extra_classes or extra_styles:
        return img_html
    else:
        return format_html('<div class="logo">{}</div>', img_html)

@register.tag(name='br_footer_social_section')
def do_footer_social_section(parser, token):
    """
    Esta tag agora lida com TODA a seção social,
    incluindo o layout de linha e colunas, resolvendo o problema de coordenação.
    """
    bits = token.split_contents()
    kwargs = token_kwargs(bits[1:], parser)
    nodelist = parser.parse(('end_br_footer_social_section',))
    parser.delete_first_token()
    return SocialSectionNode(nodelist, kwargs)

class SocialSectionNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        # Pega o título se tiver, senão usa padrão
        title = self.kwargs.get('title')
        if title:
            title = title.resolve(context)
        else:
            title = "Redes Sociais"

        # Coleta os dados
        social_links = []
        assign_images = []
        with context.push(social_links=social_links, assign_images=assign_images):
            self.nodelist.render(context)

        # HTML dos ícones e imagens
        social_links_html = ''.join([
            format_html(
                '<a class="br-button circle" href="{}" aria-label="{}">'
                '<i class="fab {} {}" aria-hidden="true"></i></a>',
                link['href'], link['aria_label'], link['icone'], link.get('extra_classes', '')
            )
            for link in social_links
        ])

        assign_images_html = ''.join([
            format_html(
                '<a href="{}"><img class="ml-4" src="{}" alt="{}"/></a>',
                img['href'], img['src'], img['alt']
            ) if img.get('href') else format_html(
                '<img class="ml-4" src="{}" alt="{}"/>',
                img['src'], img['alt']
            )
            for img in assign_images
        ])

        return format_html(
            '''<div class="d-none d-sm-block">
                <div class="row align-items-end justify-content-between py-5">
                    <div class="col">
                        <div class="social-network">
                            <div class="social-network-title">{}</div>
                            <div class="d-flex">{}</div>
                        </div>
                    </div>
                    <div class="col assigns text-right">{}</div>
                </div>
            </div>''',
            title,
            mark_safe(social_links_html),
            mark_safe(assign_images_html)
        )

@register.simple_tag(takes_context=True)
def br_footer_rede_social(context, href, icone, aria_label, extra_classes=''):
    # Esta tag apenas adiciona dados à lista.
    context['social_links'].append({'href': href, 'icone': icone, 'aria_label': aria_label, 'extra_classes': extra_classes})
    return ''

@register.simple_tag(takes_context=True)
def br_footer_imagem(context, src, alt, href=None):
    # Esta tag apenas adiciona dados à lista.
    context['assign_images'].append({'src': src, 'alt': alt, 'href': href})
    return ''

@register.tag(name='br_footer_copyright')
def do_footer_copyright(parser, token):
    nodelist = parser.parse(('end_br_footer_copyright',))
    parser.delete_first_token()
    return FooterCopyrightNode(nodelist)

class FooterCopyrightNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    
    def render(self, context):
        content = self.nodelist.render(context)
        # O copyright gerencia seu próprio container e o divider.
        return format_html(
            '''<span class="br-divider my-3"></span>
            <div class="container-lg">
                <div class="info">
                    <div class="text-down-01 text-medium pb-3">{}</div>
                </div>
            </div>''',
            mark_safe(content)
        )
