"use strict";
// declare interface Window { dt: DataTables.Api; }
jQuery(function ($) {
    // protein table
    const $datatable = $("#datatable");
    // peptide table
    const $pep_table = $("#pep_table");
    const $pep_lpf = $("#pep_lpf");
    // plot images
    const $image = $("#image");
    // download plot image
    const $download = $("#image-download");
    const $refresh = $("#refresh");
    const $filter_peptides = $("#filter-peptides");
    const $enrichment_image = $("#enrichment-image");
    const $nnls_image = $("#nnls-image");
    const $selected_genes = $("#selected-genes");
    const $form = $("#filters");
    const $total_peptides = $("#total_peptides");
    const $close_img = $("#close-image-btn");
    const $image_div = $("#image-div");
    const $searchinfo = $("#searchinfo");
    const $enrichment_cols = $("#enrichment-cols");
    const $form_frag = $("#filters-frag");
    // const sliderconfig = createslider(document.querySelector(".range-slider") as HTMLElement)
    const filterid = "filters"; // just id!
    var dt = null; // data table
    var grp_dt = null;
    var filter_peptides = $filter_peptides.is(":checked");
    var current_length = Config.length;
    var selected_gene = null;
    $close_img.on("click", (e) => {
        $image.empty();
        $image_div.css({ display: "none" });
    });
    $refresh.on("click", (e) => {
        e.preventDefault();
        if (!isvalidform($form)) {
            return;
        }
        reload_proteins();
    });
    $filter_peptides.on("change", function () {
        filter_peptides = $filter_peptides.is(":checked");
        if (selected_gene !== null)
            fetch_peptides(selected_gene.group_number);
    });
    /*{# https://www.abeautifulsite.net/posts/smoothly-scroll-to-an-element-without-a-jquery-plugin-2 #}*/
    $datatable.on("click", "table > tbody > tr", () => {
        var _a;
        $([document.documentElement, document.body]).animate({
            scrollTop: (_a = $pep_table.offset()) === null || _a === void 0 ? void 0 : _a.top
        }, 500);
    });
    $image.on("dblclick", (e) => $image.toggleClass("zoom"));
    get_form_frag();
    // ----- functions ------
    function reload_proteins() {
        $refresh.prop("disabled", true);
        dt === null || dt === void 0 ? void 0 : dt.ajax.reload(on_protein_reload);
    }
    function isvalidform($elem) {
        const elem = $elem.get(0);
        return elem.reportValidity();
    }
    function on_protein_reload(data) {
        if (data.total_peptides !== undefined) {
            $total_peptides.text(data.total_peptides);
        }
        $refresh.prop("disabled", false);
        if (selected_gene !== null) {
            const std = dt.row(`#${selected_gene.DT_RowId}`);
            if (std.length === 0) {
                clear_grp_datatable();
                $pep_lpf.empty();
                show_row(null);
            }
            else {
                // refresh peptides table too
                fetch_peptides(selected_gene.group_number);
            }
        }
        refresh_nnls();
        refresh_enrichment();
    }
    function table_html(cls) {
        return `<table class="${Config.table_class} ${cls}"></table>`;
    }
    function load_data() {
        $.get(Config.data_url, { length: current_length })
            .then((json) => {
            if (json.ajax) {
                const ajax = json.ajax;
                ajax.data = add_filters;
                ajax.error = error;
            }
            json.initComplete = init_complete;
            dt = clear_datatable().append(table_html("proteins")).find("table").DataTable(json);
            // @ts-ignore
            window.dt = dt;
            dt.on("select", function (e, dt, type, indexes) {
                selected_gene = dt.rows(indexes).data()[0];
                fetch_peptides(selected_gene.group_number);
                show_row(selected_gene);
            });
            dt.on("deselect", function (e, dt, type, indexes) {
                selected_gene = null;
                clear_grp_datatable();
                $pep_lpf.empty();
                show_row(null);
            });
        })
            .fail(function () {
            toastr.error(`failed to load ${Config.data_url}`);
        });
        refresh_nnls();
        refresh_enrichment();
    }
    function show_row(gene) {
        if (gene == null) {
            $selected_genes.html("&nbsp;");
        }
        else {
            $selected_genes.text(`${gene.protein_name} of group: ${gene.group_number}`);
        }
    }
    function error(xhr, error, code) {
        let msg = `server down [${xhr.status}]?`;
        if (xhr.status == 404) {
            msg = "unknown or badly formatted file?";
        }
        toastr.error(msg, "Network Error", {
            closeButton: true,
            timeOut: 0,
            showDuration: 0,
            extendedTimeOut: 0
        });
    }
    function add_filters(d) {
        // request.values will have (filters[minPepProb],'.2')
        if (filter_peptides) {
            d.filters = serializeForm(filterid);
        }
        current_length = d.length; // pageLength
        const sf = {
            search: d.search.value,
            order_column: d.columns[d.order[0].column].data,
            ascending: d.order[0].dir === "asc"
        };
        // need this so that download can know the
        // current ordering and search query
        save_search_info(sf);
    }
    function save_search_info(sf) {
        const s = JSON.stringify(sf);
        $searchinfo.val(s);
    }
    function add_pep_filters(d) {
        d.filters = serializeForm(filterid);
        d.exclude = filter_peptides;
    }
    function make_url(url, rowid, enrichment_cols) {
        return url + "?" + $.param({ rowid, enrichment_cols });
        // return url.replace(/\/-1$/, `/${rowid}`)
    }
    function clear_datatable() {
        if (dt !== null) {
            dt.destroy();
            dt = null;
        }
        $datatable.empty();
        return $datatable;
    }
    function clear_grp_datatable() {
        if (grp_dt !== null) {
            grp_dt.destroy();
            grp_dt = null;
        }
        $pep_table.empty();
        return $pep_table;
    }
    function fetch_peptides(grp) {
        const data = { group: grp };
        add_pep_filters(data);
        return $.post(Config.group_url, data)
            .then((json) => {
            if (json.ajax) {
                ;
                json.ajax.data = add_pep_filters;
            }
            json.createdRow = peptideRowCallback;
            show_lpf_plot(json);
            grp_dt = clear_grp_datatable()
                .append(table_html("peptides"))
                .find("table")
                .DataTable(json);
            grp_dt.on("select", function (e, dt, type, indexes) {
                const gene = dt.rows(indexes).data()[0];
                const rowid = gene["DT_RowId"];
                // show_plot(rowid, gene.peptide)
                show_plot_url(rowid, gene.peptide);
            });
        })
            .fail(error);
    }
    function peptideRowCallback(row, data) {
        if (selected_gene && data.protein_names.indexOf(selected_gene.protein_name) >= 0) {
            $(row).addClass("selected-protein");
        }
    }
    function show_lpf_plot(data) {
        const lpf = data.lpf;
        if (lpf === undefined)
            return;
        $pep_lpf.empty().append($('<img class="lpf_image"/>').attr("src", lpf));
    }
    function show_plot_url(rowid, peptide) {
        const quit = SubaCrop.spinner();
        const enrichment_cols = $enrichment_cols.val();
        $image.css({ opacity: 0.6 });
        $.get(make_url(Config.plot_image_url, rowid, enrichment_cols))
            .then((json) => {
            const $img = $("<img/>");
            $img.attr("src", json.image_url);
            $image.empty().append($img);
            $download.attr("href", make_url(Config.pdf_url, rowid, enrichment_cols));
            $image_div.css({ display: "block" });
        })
            .always(always)
            .fail(() => toastr.error(`can't create image for ${peptide}`));
        function always() {
            quit();
            $image.css({ opacity: 1 });
        }
    }
    // function show_plot(rowid: string, peptide: string) {
    //     const img = $('<img/>').attr('src', make_url(Config.plot_url, rowid))
    //     const quit = SubaCrop.spinner()
    //     img.on('load', e => {
    //         quit();
    //         toastr.success(`${peptide} loaded`)
    //     }).on('error', e => {
    //         quit();
    //         toastr.error(`can't create image for ${peptide}`)
    //     })
    //     $download.attr('href', make_url(Config.pdf_url, rowid))
    //     $image.empty().append(img)
    // }
    function init_complete(settings, data) {
        // @ts-ignore
        if (data.total_peptides !== undefined) {
            $total_peptides.text(data.total_peptides);
        }
        $datatable
            .find(".dataTables_filter input")
            .off() // Unbind previous default bindings
            .on("keyup", search);
    }
    function search(e) {
        // If the length is 3 or more characters, or the user pressed ENTER, search
        const val = e.currentTarget.value || "";
        if (val.length >= Config.min_search_length || e.key === "Enter") {
            // Call the API search function
            dt.search(val).draw();
            return;
        }
        // Ensure we clear the search if they backspace far enough
        if (val === "") {
            dt.search("").draw();
        }
        return;
    }
    function refresh_enrichment() {
        const data = filter_peptides ? { filters: serializeForm(filterid) } : {};
        return $.post(Config.enrichment_url, data).then((json) => {
            $enrichment_image.attr("src", json.enrichment_url);
        });
    }
    function refresh_nnls() {
        const data = filter_peptides ? { filters: serializeForm(filterid) } : {};
        return $.post(Config.nnls_url, data).then((json) => {
            $nnls_image.attr("src", json.nnls_url);
        });
    }
    // function get_stats() {
    //     const $resid = $form.find('input[name="nnlsResidual"]')
    //     const $area = $form.find('input[name="maxPeakArea"]')
    //     const $residspan = $("#nnlsResidualid")
    //     const $areaspan = $form.find("#maxPeakAreaId")
    //     return $.get(Config.stats_url)
    //         .then((stats) => {
    //             // $resid.val(stats.max_nnls_residual)
    //             $resid.attr("max", stats.max_nnls_residual)
    //             $residspan.text(stats.max_nnls_residual)
    //             $area.attr("max", stats.max_maxPeakArea)
    //             $area.attr("step", stats.max_maxPeakArea / 100)
    //             $areaspan.text(stats.max_maxPeakArea.toExponential())
    //             // sliderconfig.reset({ max: stats.max_enrichment, min: stats.min_enrichment })
    //         })
    //         .then(() => {
    //             // nnls residuals filter has been updated
    //             reload_proteins()
    //         })
    // }
    function get_form_frag() {
        return $.get(Config.form_frag_html_url)
            .then((html) => {
            $form_frag.html(html);
            init_range('enrichmentMin');
            init_range('enrichmentMax');
            // const el = document.querySelector(".range-slider") as HTMLElement
            // if (el !== null) {
            //     createslider(el)
            // }
            arm_form();
            load_data();
        })
            .then(() => {
            // nnls residuals filter has been updated
            reload_proteins();
        });
    }
    function arm_form() {
        $form.find("input").on("keypress", function (e) {
            const isenter = e.code === "Enter";
            if (isenter) {
                e.preventDefault();
                e.stopPropagation();
                reload_proteins();
            }
            return !isenter;
        });
        $form.find('input[type="number"],input[type="range"],select').on("change", function (e) {
            e.preventDefault();
            e.stopPropagation();
            reload_proteins();
            return false;
        });
    }
    function init_range(id) {
        // This is an example script, please modify as needed
        const rangeInput = document.getElementById(id);
        const rangeOutput = document.getElementById(`${id}-output`);
        if (rangeInput === null || rangeOutput === null) {
            return;
        }
        // Set initial value
        rangeOutput.textContent = rangeInput.value;
        rangeInput.addEventListener('input', function () {
            rangeOutput.textContent = this.value;
        });
    }
});
function serializeForm(formid) {
    const elem = document.getElementById(formid);
    const obj = {};
    if (elem === null) {
        return obj;
    }
    const formData = new FormData(elem);
    for (let key of formData.keys()) {
        const v = formData.get(key);
        if (v !== null && !(v instanceof File))
            obj[key] = v;
    }
    return obj;
}
jQuery(function ($) {
    const $cw = $("#col-width");
    const $left = $("#protein-col");
    const $right = $("#peptide-col");
    const $th = $("#table-height");
    const $dt = $("#datatable");
    const key = "turnover-col-width";
    const v = window.localStorage.getItem(key);
    if (v !== null && v !== "") {
        $cw.val(v);
        set(v);
    }
    $cw.on("input", function () {
        const v = this.value;
        if (v === "")
            return;
        set(v);
    }).on("change", function () {
        const v = this.value;
        if (v === "")
            return;
        window.localStorage.setItem(key, v);
    });
    $th.on("change", function () {
        if ($th.is(":checked")) {
            $dt.addClass("datatable-height");
        }
        else {
            $dt.removeClass("datatable-height");
        }
    });
    function set(v) {
        $left.css("width", v + "%");
        $right.css("width", 100 - +v + "%");
    }
});
