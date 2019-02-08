{% if alerts or warnings %}
    <h2 class="page-header h2">Messages Overview</h2>
    {% if alerts %}
        <h3>Alerts <span class="badge badge-danger pull-right">Alert</span></h3>
        <ul>
            {% for msg in alerts %}
                <li>{{ msg }}</li>
            {% endfor %}
        </ul>
    {% endif %}
    {% if warnings %}
        <h3>Warnings <span class="badge badge-warning pull-right">Warning</span></h3>
        <ul>
            {% for msg in warnings %}
                <li>{{ msg }}</li>
            {% endfor %}
        </ul>
    {% endif %}
{% endif %}
