from jinja2 import Environment, FileSystemLoader, TemplateNotFound

def render(TemplateName, TemplateDIR='templates', *args, **kwargs):
    env = Environment(loader=FileSystemLoader(TemplateDIR))
    __template = env.get_template(TemplateName)
    __str = __template.render(*args, **kwargs)
    return __str