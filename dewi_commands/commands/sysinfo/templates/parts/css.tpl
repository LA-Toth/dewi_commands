<style>
    body {
        background-color: gray;
        position: relative;
    }

    body > div.container {
        background-color: white;
        min-width: 940px;
    }

    .h1, .h3 {
        margin-top: 1em;
    }

    .h1 small, .h2 small, h1 small, h2 small, footer > p {
        color: #777 !important;
        font-size: 65%
    }

    header > p {
        color: #777 !important;
        font-size: 120%;
    }

    .page-header {
        padding-bottom: 9px;
        margin: 20px 0 20px;
        border-bottom: 1px solid #eee;
    }

    .hidden {
        display: none;
    }

    .cursor-pointer {
        cursor: pointer;
    }

    .network-address {
        font-style: italic;
        text-align: right;
    }

    /* small screens */
    @media (max-width: 768px) {
        /* override the Affix plugin so that the navigation isn't sticky */
        nav.affix[data-toggle='toc'] {
            position: static;
        }

        /* alternatively, if you *do* want the second-level navigation to be shown (as seen on this page on mobile), use this */
        nav[data-toggle='toc'] .nav .nav {
            display: block;
        }
    }

    .msg-maybe-show-more {
        min-width: 11px;
    }

    .rrd-graph-show-more {
        min-width: 16px;
    }

    .fa-hide {
        color: transparent;
    }

    .fa-none:before {
        content: "\2122";
        color: transparent !important;
    }

    .msg-hint {
        font-style: italic;
        padding: 1em;
    }

    .rrd-graph-interval {
        padding-bottom: .5em;
    }

    .rrd-graph-interval-more {
        padding-top: 1em;
    }

</style>
