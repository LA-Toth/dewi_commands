<div id="details1" class="container">
    <h2 class="page-header h2">Details</h2>
    <h3 class="h3">Overview of System</h3>
    <table class="table table-striped table-hover table-condensed">
        <thead>
        <tr>
            <th>Info</th>
            <th>Value</th>
        </tr>
        </thead>
        <tbody>
        <tr>
            <th>Hostname</th>
            <td>{{ root.system.hostname }}</td>
        </tr>
        </tbody>
    </table>

    <h3 class="h3">Details</h3>
    <table class="table table-striped table-hover table-condensed">
        <thead>
        <tr>
            <th>Description</th>
            <th>Entry</th>
        </tr>
        </thead>
        <tbody>
        <tr>
            <th colspan="2" class="text-center"><h4>File system and memory</h4></th>
        </tr>
        {% for fs in root.system.filesystems %}
            <tr>
                <th>Usage @ {{ fs.mount_path }}</th>
                <td>
                    {{ fs.usage_percent }}% (
                    {{ fs.used }} kiB of
                    {{ fs.total }} kiB;
                    {{ fs.free }} kiB free )
                </td>
            </tr>
        {% endfor %}
        {% include 'details-hardware.tpl' %}
        </tbody>
    </table>
</div>
