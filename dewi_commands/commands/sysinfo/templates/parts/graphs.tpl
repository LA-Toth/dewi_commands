<h2 class="page-header">Graphs</h2>

{% for category in graphs.categories_ %}
    <h3>{{ category }}</h3>
    <table class="table table-striped table-hover table-condensed">
        {% for short_name in graphs['g'][category].short_names_ %}
            <tr>
                <td>
                    <div onclick="rrdGraphToggle(this); return false;" class="cursor-pointer">
                        <h4>
                            <span class="rrd-graph-show-more fa fa-angle-right"></span>
                            {{ graphs['g'][category]['s'][short_name]['title'] }}
                            <small>{{ short_name }}</small>
                        </h4>
                    </div>

                    {% for interval in graphs['g'][category]['s'][short_name]['intervals'] %}
                        <div class="rrd-graph-img
                                {% if interval != 'day' %}
                                    rrd-graph-img-toggle hidden
                                {% endif %}"
                        >
                            <div class="rrd-graph-interval {% if interval != 'day' %} rrd-graph-interval-more {% endif %} text-capitalize">{{ interval }} </div>
                            <img src="graphs/{{ graphs['g'][category]['s'][short_name]['intervals'][interval].filename }}">
                        </div>
                    {% endfor %}
                </td>
            </tr>
        {% endfor %}
    </table>
{% endfor %}
