<script>
    function messageToggle(elem) {
        $(elem).parent().children('div[class~="msg-details"]').toggleClass('hidden');
        $(elem).parent().children('div[class~="msg-hint"]').toggleClass('hidden');

        // parent().children() -> same element. Its childe is the span
        $(elem).parent().children().children('span[class~="msg-show-more"]')
            .toggleClass('fa-angle-right').toggleClass('fa-angle-up');
    }

    function rrdGraphToggle(elem) {
        $(elem).parent().children('div[class~="rrd-graph-img-toggle"]').toggleClass('hidden');

        // parent().children() --> same div; inside div: h4 > span
        $(elem).parent().children().children().children('span[class~="rrd-graph-show-more"]')
            .toggleClass('fa-angle-right').toggleClass('fa-angle-up');
    }
</script>
