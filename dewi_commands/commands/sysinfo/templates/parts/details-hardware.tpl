<tr>
    <th colspan="3" class="text-center"><h4>Hardware</h4></th>
</tr>
<tr>
    <th>Hardware type (dmidecode)</th>
    {% if root.system.hw.dmidecode.product %}
        <td>{{ root.system.hw.dmidecode.manufacturer }} -
            {{ root.system.hw.dmidecode.product }}<br>
            {{ root.system.hw.dmidecode.serial }}
        </td>
    {% else %}
        <td>N/A</td>
    {% endif %}
</tr>
{% for iface in root.system.hw.network_interfaces.keys() %}
    <tr>
        <th>NIC - {{ iface }}</th>
        <td>
            {% if root.system.hw.network_interfaces[iface] %}
                {{ root.system.hw.network_interfaces[iface]['hmac'] }}<br>
                <span class="network-vendor">{{ root.system.hw.network_interfaces[iface]['vendor'] }}</span>
                {% for inet in  root.system.hw.network_interfaces[iface]['inet'] %}
                    <br/><span class="network-address">IPv4 - {{ inet }}</span>
                {% endfor %}
                {% for inet6 in  root.system.hw.network_interfaces[iface]['inet6'] %}
                    <br/><span class="network-address">IPv6 - {{ inet6 }}</span>
                {% endfor %}

            {% else %}
                -
            {% endif %}
        </td>

    </tr>
{% endfor %}
