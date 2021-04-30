import logging
from jinja2 import Template


logger = logging.getLogger(__name__)

vlan_jinja = """
{% if vlans_to_delete is defined and vlans_to_delete %}
{% for vlan in vlans_to_delete -%}
no vlan {{ vlan }}
{% endfor -%}
{% endif %}

{% if vlans_to_add is defined and vlans_to_add %}
{% for vlan in vlans_to_add -%}
vlan {{ vlan['id'] }}
  name {{ vlan['name'] }}
{% endfor %}
{% endif %}

"""


def render_vlan_config(vlans_to_delete=None, vlans_to_add=None):
    #vlans_to_delete = [
    #    5,7
    #]
    t = Template(vlan_jinja.strip())
    cfg = t.render(vlans_to_delete=vlans_to_delete, vlans_to_add=vlans_to_add)
    cset = cfg.split("\n")
    print(cset)
    #print(cfg)
    logger.info(f"Render onfiguration \n{cfg}")
    return cfg

