/*! Bootstrap integration for DataTables' SearchPanes
 * ©2016 SpryMedia Ltd - datatables.net/license
 */
(function (factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD
        define(['jquery', 'datatables.net-zf', 'datatables.net-searchpanes'], function ($) {
            return factory($);
        });
    }
    else if (typeof exports === 'object') {
        // CommonJS
        module.exports = function (root, $) {
            if (!root) {
                root = window;
            }
            if (!$ || !$.fn.dataTable) {
                // eslint-disable-next-line @typescript-eslint/no-var-requires
                $ = require('datatables.net-zf')(root, $).$;
            }
            if (!$.fn.dataTable.SearchPanes) {
                // eslint-disable-next-line @typescript-eslint/no-var-requires
                require('datatables.net-searchpanes')(root, $);
            }
            return factory($);
        };
    }
    else {
        // Browser
        factory(jQuery);
    }
}(function ($) {
    'use strict';
    var dataTable = $.fn.dataTable;
    $.extend(true, dataTable.SearchPane.classes, {
        buttonGroup: 'c_SSC button-group',
        disabledButton: 'disabled',
        narrow: 'dtsp-narrow',
        narrowButton: 'dtsp-narrowButton',
        narrowSearch: 'dtsp-narrowSearch',
        paneButton: 'c_SSC button',
        pill: 'badge c_SSC',
        search: 'search',
        searchLabelCont: 'searchCont',
        show: 'col',
        table: 'unstriped'
    });
    $.extend(true, dataTable.SearchPanes.classes, {
        clearAll: 'dtsp-clearAll button c_SSC',
        collapseAll: 'dtsp-collapseAll button c_SSC',
        disabledButton: 'disabled',
        panes: 'panes dtsp-panesContainer',
        showAll: 'dtsp-showAll button c_SSC',
        title: 'dtsp-title'
    });
    return dataTable.searchPanes;
}));
