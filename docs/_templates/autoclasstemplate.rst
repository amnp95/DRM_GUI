{{objname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   {% block methods %}
   .. rubric:: {{ _('Methods') }}
   .. container:: api-methods

      {% for item in methods %}
      * :py:meth:`~{{ name }}.{{ item }}` - {{ methods_summary.get(item, "") }}
      {%- endfor %}
   {% endblock %}

   {% block attributes %}
   .. rubric:: {{ _('Attributes') }}
   .. container:: api-attributes

      {% for item in attributes %}
      * :py:attr:`~{{ name }}.{{ item }}`
      {%- endfor %}
   {% endblock %}
   
   .. rubric:: {{ _('Details') }}
   
   {% block methoddocs %}
   {% for method in methods %}
   .. automethod:: {{ name }}.{{ method }}
   {%- endfor %}
   {% endblock %}
   
   {% block attributedocs %}
   {% for attribute in attributes %}
   .. autoattribute:: {{ name }}.{{ attribute }}
   {%- endfor %}
   {% endblock %}