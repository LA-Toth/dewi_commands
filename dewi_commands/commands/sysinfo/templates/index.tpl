<!DOCTYPE html>
<html lang="en-US">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="Expires" content="0">
    <title>SysInfo Results - {{ root.system.hostname }}</title>

    <link rel="stylesheet" href="assets/bootstrap/css/bootstrap.min.css">
    <link rel="stylesheet" href="assets/bootstrap/css/bootstrap-theme.min.css">
    <link rel="stylesheet" href="assets/font-awesome/css/font-awesome.min.css">

    <script src="assets/jquery/jquery.min.js"></script>
    <script src="assets/popperjs/popper.min.js"></script>
    <script src="assets/bootstrap/js/bootstrap.min.js"></script>

    {% include 'css.tpl' %}
    {% include 'javascript.tpl' %}
</head>
<body>
<div class="container">
    <header>
        <div class="page-header">
            <h1>SysInfo results
                <small>host {{ root.system.hostname }}</small>
            </h1>
        </div>
    </header>

    <nav>
        <div class="nav nav-tabs" id="dpTabs" role="tablist">
            <a class="nav-item nav-link active" data-toggle="tab" id="overview-tab" href="#overview"
               role="tab">Overview</a>
            <a class="nav-item nav-link" data-toggle="tab" id="details-tab" href="#details" role="tab">Details</a>
            <a class="nav-item nav-link" data-toggle="tab" id="messages-tab" href="#messages" role="tab">Messages</a>
            <a class="nav-item nav-link" data-toggle="tab" id="graphs-tab" href="#graphs" role="tab">Graphs</a>
        </div>
    </nav>
    <content class="tab-content" id="dpTabsContent">
        <div class="tab-pane fade show active" id="overview" role="tabpanel">
            {% include 'overview.tpl' %}
        </div>
        <div class="tab-pane fade" id="details" role="tabpanel">
            {% include 'details.tpl' %}
        </div>
        <div class="tab-pane fade" id="messages" role="tabpanel">
            {% include 'messages.tpl' %}
        </div>
        <div class="tab-pane fade" id="graphs" role="tabpanel">
            {% include 'graphs.tpl' %}
        </div>
    </content>
    <footer>

        <p>
            Processed at {{ root.processed }} <br>
            by
            <a href="https://github.com/LA-Toth/dewi">DEWI</a>, more precisely
            <a href="https://github.com/LA-Toth/dewi_Commands">DEWI commands</a>.
            <span class="pull-right">Host: {{ root.system.hostname }}</span>
        </p>
    </footer>
</div>
</body>
</html>
