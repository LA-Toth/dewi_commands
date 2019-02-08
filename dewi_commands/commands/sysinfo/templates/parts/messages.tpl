<h2 class="page-header">Messages</h2>

{% for category in messages|sort %}
    <h3>{{ category }} </h3>
    <table class="table table-striped table-hover table-condensed">
        {% for subcategory in messages[category] %}
            <tr>
                <th>{{ subcategory }}</th>
            </tr>
            {% for msg in messages[category][subcategory] %}
                <tr>
                    <td>
                        {% if msg.details or msg.hint %}
                            <div onclick="messageToggle(this); return false;" class="cursor-pointer">
                                <span class="msg-show-more msg-maybe-show-more fa fa-angle-right"></span>{{ msg.message }}

                                {%- if msg.level == 'WARNING' %}
                                    <span class="badge badge-warning pull-right">Warning</span>
                                {%- elif msg.level == 'ALERT' %}
                                    <span class="badge badge-danger pull-right">Alert</span>
                                {% endif %}
                            </div>
                            {% if msg.hint %}
                                <div class="msg-hint hidden">
                                    {% for hint_line in msg.hint %}
                                        {{ hint_line }}<br/>
                                    {% endfor %}
                                </div>
                            {% endif %}
                            {% if msg.details %}
                                <div class="msg-details hidden card">
                                    <div class="card-block">
                                        {% for desc_line in msg.details %}
                                            {{ desc_line }}<br/>
                                        {% endfor %}
                                    </div>
                                </div>
                            {% endif %}
                        {% else %}
                            <span class="msg-maybe-show-more fa fa-none"></span>{{ msg.message }}
                            {%- if msg.level == 'WARNING' %} <span class="badge badge-warning pull-right">Warning</span>
                            {%- elif msg.level == 'ALERT' %}<span class="badge badge-danger pull-right">Alert</span>
                            {% endif %}
                        {% endif %}
                    </td>
                </tr>
            {% endfor %}
        {% endfor %}
    </table>
{% endfor %}
