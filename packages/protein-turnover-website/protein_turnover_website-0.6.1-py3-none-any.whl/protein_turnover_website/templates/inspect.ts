type ConfigClass = Readonly<{
    dataid: string

    data_url: URLStr // inspect.datatable
    group_url: URLStr // inspect.group
    plot_url: URLStr // inspect.plot
    enrichment_url: URLStr // inspect.enrichment_plot
    nnls_url: URLStr // inspect.nnls_plot
    plot_image_url: URLStr // inspect.plot_url
    pdf_url: URLStr // inspect.pdf
    // stats_url: URLStr // inspect.stats
    form_frag_html_url: URLStr // inspect.form_frag_html

    max_download_attempts: number

    length: number // pageLength
    table_class: string
    min_search_length: number
}>

type DTSearchInfo = {
    search: string
    order_column: string
    ascending: boolean
}

type Extra = {
    total_peptides?: number
}

// type Gene = Readonly<{
//     prStr: string,
//     description: string,
//     prGroup: number
// }>

type Gene = Readonly<{
    DT_RowId: string
    protein_name: string
    protein_description: string
    group_number: number
}>
type Peptide = Readonly<{
    DT_RowId: number
    enrichment: number
    heavyCor: number
    modcol: string
    nnls_residual: number
    peptide: string
    peptideprophet_probability: number
    protein_names: string[]
    relativeIsotopeAbundance: number
}>

type SubaCropClass = {
    spinner: () => () => void
}

declare const SubaCrop: SubaCropClass
declare const Config: ConfigClass
// declare interface Window { dt: DataTables.Api; }

jQuery(function ($: JQueryStatic) {
    // protein table
    const $datatable = $("#datatable")
    // peptide table
    const $pep_table = $("#pep_table")
    const $pep_lpf = $("#pep_lpf")
    // plot images
    const $image = $("#image")
    // download plot image
    const $download = $("#image-download")
    const $refresh = $("#refresh")

    const $filter_peptides = $("#filter-peptides")
    const $enrichment_image = $("#enrichment-image")
    const $nnls_image = $("#nnls-image")
    const $selected_genes = $("#selected-genes")
    const $form = $("#filters")
    const $total_peptides = $("#total_peptides")
    const $close_img = $("#close-image-btn")
    const $image_div = $("#image-div")
    const $searchinfo = $("#searchinfo")
    const $enrichment_cols = $("#enrichment-cols")
    const $form_frag = $("#filters-frag")

    // const sliderconfig = createslider(document.querySelector(".range-slider") as HTMLElement)

    const filterid = "filters" // just id!

    var dt: DataTables.Api | null = null // data table
    var grp_dt: DataTables.Api | null = null
    var filter_peptides: boolean = $filter_peptides.is(":checked")
    var current_length: number = Config.length
    var selected_gene: Gene | null = null


    $close_img.on("click", (e) => {
        $image.empty()
        $image_div.css({ display: "none" })
    })

    $refresh.on("click", (e) => {
        e.preventDefault()
        if (!isvalidform($form)) {
            return
        }
        reload_proteins()
    })

    $filter_peptides.on("change", function () {
        filter_peptides = $filter_peptides.is(":checked")
        if (selected_gene !== null) fetch_peptides(selected_gene.group_number)
    })
    /*{# https://www.abeautifulsite.net/posts/smoothly-scroll-to-an-element-without-a-jquery-plugin-2 #}*/
    $datatable.on("click", "table > tbody > tr", () => {
        $([document.documentElement, document.body]).animate(
            {
                scrollTop: $pep_table.offset()?.top
            },
            500
        )
    })

    $image.on("dblclick", (e) => $image.toggleClass("zoom"))

    get_form_frag()

    // ----- functions ------

    function reload_proteins() {
        $refresh.prop("disabled", true)
        dt?.ajax.reload(on_protein_reload)
    }

    function isvalidform($elem: JQuery): boolean {
        const elem = $elem.get(0) as HTMLFormElement
        return elem!.reportValidity()
    }

    function on_protein_reload(data: DataTables.AjaxData & Extra) {
        if (data.total_peptides !== undefined) {
            $total_peptides.text(data.total_peptides)
        }
        $refresh.prop("disabled", false)
        if (selected_gene !== null) {
            const std = dt!.row(`#${selected_gene.DT_RowId}`)
            if (std.length === 0) {
                clear_grp_datatable()
                $pep_lpf.empty()
                show_row(null)
            } else {
                // refresh peptides table too
                fetch_peptides(selected_gene.group_number)
            }
        }
        refresh_nnls()
        refresh_enrichment()
    }

    function table_html(cls: string): string {
        return `<table class="${Config.table_class} ${cls}"></table>`
    }

    function load_data() {
        $.get(Config.data_url, { length: current_length })
            .then((json: DataTables.Settings) => {
                if (json.ajax) {
                    const ajax = json.ajax as DataTables.AjaxSettings
                    ajax.data = add_filters
                    ajax.error = error
                }
                json.initComplete = init_complete
                dt = clear_datatable().append(table_html("proteins")).find("table").DataTable(json)
                // @ts-ignore
                window.dt = dt
                dt.on("select", function (e, dt, type, indexes) {
                    selected_gene = dt.rows(indexes).data()[0]
                    fetch_peptides(selected_gene!.group_number)
                    show_row(selected_gene!)
                })
                dt.on("deselect", function (e, dt, type, indexes) {
                    selected_gene = null
                    clear_grp_datatable()
                    $pep_lpf.empty()
                    show_row(null)
                })
            })
            .fail(function () {
                toastr.error(`failed to load ${Config.data_url}`)
            })
        refresh_nnls()
        refresh_enrichment()
    }

    function show_row(gene: Gene | null) {
        if (gene == null) {
            $selected_genes.html("&nbsp;")
        } else {
            $selected_genes.text(`${gene.protein_name} of group: ${gene.group_number}`)
        }
    }

    function error(xhr: JQuery.jqXHR, error: any, code: string) {
        let msg = `server down [${xhr.status}]?`
        if (xhr.status == 404) {
            msg = "unknown or badly formatted file?"
        }
        toastr.error(msg, "Network Error", {
            closeButton: true,
            timeOut: 0,
            showDuration: 0,
            extendedTimeOut: 0
        })
    }

    function add_filters(d: any) {
        // request.values will have (filters[minPepProb],'.2')
        if (filter_peptides) {
            d.filters = serializeForm(filterid)
        }
        current_length = d.length // pageLength
        const sf: DTSearchInfo = {
            search: d.search.value,
            order_column: d.columns[d.order[0].column].data,
            ascending: d.order[0].dir === "asc"
        }
        // need this so that download can know the
        // current ordering and search query
        save_search_info(sf)
    }

    function save_search_info(sf: DTSearchInfo) {
        const s = JSON.stringify(sf)
        $searchinfo.val(s)
    }
    function add_pep_filters(d: any) {
        d.filters = serializeForm(filterid)
        d.exclude = filter_peptides
    }

    function make_url(
        url: string,
        rowid: string,
        enrichment_cols: string | number | undefined
    ): string {
        return url + "?" + $.param({ rowid, enrichment_cols })
        // return url.replace(/\/-1$/, `/${rowid}`)
    }

    function clear_datatable(): JQuery<HTMLElement> {
        if (dt !== null) {
            dt.destroy()
            dt = null
        }
        $datatable.empty()
        return $datatable
    }
    function clear_grp_datatable(): JQuery<HTMLElement> {
        if (grp_dt !== null) {
            grp_dt.destroy()
            grp_dt = null
        }
        $pep_table.empty()
        return $pep_table
    }

    function fetch_peptides(grp: number): JQuery.Promise<any> {
        const data = { group: grp }
        add_pep_filters(data)
        return $.post(Config.group_url, data)
            .then((json) => {
                if (json.ajax) {
                    ; (json.ajax as DataTables.AjaxSettings).data = add_pep_filters
                }
                json.createdRow = peptideRowCallback
                show_lpf_plot(json)
                grp_dt = clear_grp_datatable()
                    .append(table_html("peptides"))
                    .find("table")
                    .DataTable(json)

                grp_dt.on("select", function (e, dt, type, indexes) {
                    const gene = dt.rows(indexes).data()[0]
                    const rowid = gene["DT_RowId"]
                    // show_plot(rowid, gene.peptide)
                    show_plot_url(rowid, gene.peptide)
                })
            })
            .fail(error)
    }

    function peptideRowCallback(row: HTMLElement, data: Peptide) {
        if (selected_gene && data.protein_names.indexOf(selected_gene.protein_name) >= 0) {
            $(row).addClass("selected-protein")
        }
    }

    function show_lpf_plot(data: any): void {
        const lpf = data.lpf
        if (lpf === undefined) return
        $pep_lpf.empty().append($('<img class="lpf_image"/>').attr("src", lpf))
    }

    function show_plot_url(rowid: string, peptide: string) {
        const quit = SubaCrop.spinner()
        const enrichment_cols = $enrichment_cols.val() as string | number | undefined
        $image.css({ opacity: 0.6 })

        $.get(make_url(Config.plot_image_url, rowid, enrichment_cols))
            .then((json) => {
                const $img = $("<img/>")
                $img.attr("src", json.image_url)
                $image.empty().append($img)
                $download.attr("href", make_url(Config.pdf_url, rowid, enrichment_cols))
                $image_div.css({ display: "block" })
            })
            .always(always)
            .fail(() => toastr.error(`can't create image for ${peptide}`))

        function always() {
            quit()
            $image.css({ opacity: 1 })
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

    function init_complete(settings: DataTables.SettingsLegacy, data: object & Extra) {
        // @ts-ignore
        if (data.total_peptides !== undefined) {
            $total_peptides.text(data.total_peptides)
        }
        $datatable
            .find(".dataTables_filter input")
            .off() // Unbind previous default bindings
            .on("keyup", search)
    }

    function search(e: JQuery.KeyUpEvent) {
        // If the length is 3 or more characters, or the user pressed ENTER, search
        const val = e.currentTarget.value || ""
        if (val.length >= Config.min_search_length || e.key === "Enter") {
            // Call the API search function
            dt!.search(val).draw()
            return
        }
        // Ensure we clear the search if they backspace far enough
        if (val === "") {
            dt!.search("").draw()
        }
        return
    }

    function refresh_enrichment() {
        const data = filter_peptides ? { filters: serializeForm(filterid) } : {}
        return $.post(Config.enrichment_url, data).then((json) => {
            $enrichment_image.attr("src", json.enrichment_url)
        })
    }

    function refresh_nnls() {
        const data = filter_peptides ? { filters: serializeForm(filterid) } : {}

        return $.post(Config.nnls_url, data).then((json) => {
            $nnls_image.attr("src", json.nnls_url)
        })
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
                $form_frag.html(html)
                init_range('enrichmentMin')
                init_range('enrichmentMax')
                // const el = document.querySelector(".range-slider") as HTMLElement
                // if (el !== null) {
                //     createslider(el)
                // }
                arm_form()
                load_data()
            })
            .then(() => {
                // nnls residuals filter has been updated
                reload_proteins()
            })
    }

    function arm_form() {
        $form.find("input").on("keypress", function (e) {
            const isenter = e.code === "Enter"
            if (isenter) {
                e.preventDefault()
                e.stopPropagation()
                reload_proteins()
            }
            return !isenter
        })
        $form.find('input[type="number"],input[type="range"],select').on("change", function (e) {
            e.preventDefault()
            e.stopPropagation()
            reload_proteins()
            return false
        })
    }

    function init_range(id: string) {
        // This is an example script, please modify as needed
        const rangeInput = document.getElementById(id) as HTMLInputElement;
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
})

function serializeForm(formid: string): { [index: string]: string } {
    const elem = document.getElementById(formid) as HTMLFormElement
    const obj: { [key: string]: any } = {}
    if (elem === null) {
        return obj
    }
    const formData = new FormData(elem)
    for (let key of formData.keys()) {
        const v = formData.get(key)
        if (v !== null && !(v instanceof File)) obj[key] = v
    }
    return obj
}

jQuery(function ($: JQueryStatic) {
    const $cw = $("#col-width")
    const $left = $("#protein-col")
    const $right = $("#peptide-col")
    const $th = $("#table-height")
    const $dt = $("#datatable")
    const key = "turnover-col-width"

    const v = window.localStorage.getItem(key)

    if (v !== null && v !== "") {
        $cw.val(v)
        set(v)
    }

    $cw.on("input", function () {
        const v = (this as HTMLInputElement).value
        if (v === "") return
        set(v)
    }).on("change", function () {
        const v = (this as HTMLInputElement).value
        if (v === "") return
        window.localStorage.setItem(key, v)
    })
    $th.on("change", function () {
        if ($th.is(":checked")) {
            $dt.addClass("datatable-height")
        } else {
            $dt.removeClass("datatable-height")
        }
    })

    function set(v: string) {
        $left.css("width", v + "%")
        $right.css("width", 100 - +v + "%")
    }
})
