type JobConfigClass = Readonly<{
    atomicProperties: { [key: string]: number[] }
    check_pepxml_url: URLStr
    check_protxml_url: URLStr
    check_mzml_url: URLStr
    change_directory_url: URLStr
    job_index_url: URLStr
}>
type Files = Readonly<{
    mountpoint: string
    parent: string
    files: string[]
}>

type Counts = Readonly<
    JsonReply & {
        counts: { [key: string]: number }
        has_peptide_prophet?: boolean
    }
>
type Proteins = Readonly<
    JsonReply & {
        proteins: number
    }
>
declare const JobConfig: JobConfigClass

jQuery(function ($) {
    // arm file explorer
    const e: ExplorerClass = {
        change_directory_url: JobConfig.change_directory_url,
        selector: "#file-explorer",
        multi: false,
        key: "pepxml"
    }
    // see protein_turnover_website/explorer/templates/explorer.ts
    const exp = explorer(e)

    close_dialog(e)

    showfiles("#pepxml-file", "pepxml", e)
    showfiles("#protxml-file", "protxml", e)
    showfiles("#mzml-files", "mzml", e)

    // save selected files to type="hidden" input values
    savefiles("#pepxmlfiles", "pepxml", e)
    savefiles("#protxmlfile", "protxml", e)
    savefiles("#mzmlfiles", "mzml", e)

    check_pepxml("pepxml", e)
    check_protxml("protxml", e)
    check_mzml("mzml", e)

    $("#show-pepxml").on("click", (e) => {
        exp.multi_select("pepxml", true)
    })
    $("#show-mzml").on("click", (e) => {
        exp.multi_select("mzml", true)
    })
    $("#show-protxml").on("click", (e) => {
        exp.multi_select("protxml", false)
    })

    // @ts-ignore
    $('[data-bs-toggle="popover"]').popover()

    if (window.localStorage) {
        arm_save_state(e, "explorer")
        const val = window.localStorage.getItem("explorer")
        if (val !== null) {
            const old = try_state(val)
            if (old !== null) exp.change_directory(old)
        }
    }

    // functions only ...

    function try_state(val: string): State | null {
        try {
            return JSON.parse(val)
        } catch (e) {
            return null
        }
    }

    function make_error(msg: string): string {
        return `<strong class="error mx-auto d-block">${msg}</strong>`
    }

    function showfiles(selector: string, key: Key, e: ExplorerClass) {
        const $selector = $(selector)
        let pepxmlcounts: { [key: string]: number } | null = null
        let selected_files: SelectedClass | null = null

        $(e.selector).on("selected.to", function (e: JQuery.Event, data: SelectedClass) {
            if (key !== data.key) return

            selected_files = data
            render_counts()
        })

        if (key === "mzml") {
            // listen for pepxml.to counts
            $(e.selector).on("pepxml.to", function (e: JQuery.Event, cnts) {
                pepxmlcounts = cnts
                render_counts()
            })
        }

        function match_runNames(): boolean {
            // return true;
            return $("#match-runNames").is(":checked")
        }

        function render_counts() {
            if (selected_files === null) return
            const state = selected_files.state
            const files = selected_files.selected
            if (files.length > 0) {
                const no_match_runNames = !match_runNames()
                let missing = 0
                const p = `<b>${state.mountpoint}</b>:${state.parent}`
                const s = files
                    .map((f) => {
                        const ok = no_match_runNames || has_run(f)
                        f = ok ? f : `<span class="norun">${f}</span>`
                        if (!ok) {
                            missing += 1
                        }
                        return `${p}/${f}${
                            ok ? "" : ': (<span class="norun">no matching runs</span>)'
                        }`
                    })
                    .join("</li><li>")
                $selector.html(`<ul class="files"><li>${s}</li></ul>`)
                if (missing > 0) {
                    toastr.warning(`mzML file${missing === 1 ? " has" : "s have"} no matching runs`)
                }
            } else {
                $selector.html("")
            }
        }

        function has_run(filename: string): boolean {
            let ok = true
            if (pepxmlcounts !== null) {
                const dot = filename.lastIndexOf(".")
                const runName = dot >= 0 ? filename.substring(0, dot) : filename
                ok = pepxmlcounts[runName] !== undefined
            }
            return ok
        }
    }
    function arm_save_state(e: ExplorerClass, key: string) {
        const $modal = $("#explorer-modal")
        let state: State | null = null

        $(e.selector).on("selected.to", function (e: JQuery.Event, data: SelectedClass) {
            state = data.state
        })
        $modal.on("hidden.bs.modal", function (e) {
            if (state !== null) window.localStorage.setItem(key, JSON.stringify(state))
        })
    }
    function savefiles(selector: string, key: Key, e: ExplorerClass) {
        // save data to input value specified by selector
        const $selector = $(selector) as JQuery<HTMLInputElement>

        $(e.selector).on("selected.to", function (evt: JQuery.Event, data: SelectedClass) {
            if (key !== data.key) return
            const state = data.state
            const files = data.selected
            // multi select mean mzml/pepxml otherwise protxml
            const save: Files = {
                mountpoint: state.mountpoint,
                parent: state.parent,
                files: files
            }
            if (files.length > 0) {
                $selector.val(JSON.stringify(save))
            } else {
                $selector.val("")
            }
        })
    }

    function check_pepxml(key: Key, e: ExplorerClass) {
        const $explorer = $(e.selector)
        const $pepxml_counts = $("#pepxml-counts")
        const $modal = $("#explorer-modal")
        const $pepxml_pp = $("#pepxml-pp")
        let save: any = null
        let check: boolean = false

        $(e.selector).on("selected.to", function (e: JQuery.Event, data: SelectedClass) {
            const state = data.state
            const files = data.selected
            check = data.key === key
            if (!check || files.length === 0) {
                return
            }
            save = { mountpoint: state.mountpoint, parent: state.parent, pepxmls: files }
        })
        $modal.on("hidden.bs.modal", function (e) {
            if (save === null || !check) return
            $pepxml_pp.empty()
            $pepxml_counts.empty()
            $.get(JobConfig.check_pepxml_url, save)
                .then((json: Counts) => {
                    if (json.status !== "OK") {
                        toastr.error(json.msg)
                        $pepxml_counts.html(make_error(json.msg))
                        return
                    }
                    $explorer.trigger("pepxml.to", json.counts)
                    if (!json.has_peptide_prophet) {
                        $pepxml_pp.text("No Peptide Prophet probabilities found!")
                    }
                    $pepxml_counts.html(make_table(json.counts))
                })
                .fail(() => {
                    const msg = "Can't determine spectra count!"
                    toastr.error(msg)
                    $pepxml_counts.html(make_error(msg))
                })
        })
    }
    function check_protxml(key: Key, e: ExplorerClass) {
        // const $explorer = $(e.selector)
        const $protxml_counts = $("#protxml-counts")
        const $modal = $("#explorer-modal")
        let save: any = null
        let check: boolean = false

        $(e.selector).on("selected.to", function (e: JQuery.Event, data: SelectedClass) {
            const state = data.state
            const files = data.selected
            check = data.key === key
            if (!check || files.length === 0) {
                return
            }
            save = { mountpoint: state.mountpoint, parent: state.parent, protxml: files[0] }
        })
        $modal.on("hidden.bs.modal", function (e) {
            if (save === null || !check) return
            $protxml_counts.empty()
            $.get(JobConfig.check_protxml_url, save)
                .then((json: Proteins) => {
                    if (json.status != "OK") {
                        toastr.error(json.msg)
                        $protxml_counts.html(make_error(json.msg))
                        return
                    }
                    $protxml_counts
                        .empty()
                        .html(`Total proteins found: <code>${json.proteins}</code>`)
                })
                .fail(() => {
                    const msg = "Can't determine spectra count!"
                    toastr.error(msg)
                    $protxml_counts.html(make_error(msg))
                })
        })
    }
    function check_mzml(key: Key, e: ExplorerClass) {
        // const $explorer = $(e.selector)
        // const $mzml_counts = $('#mzml-files')
        const $mzml_counts = $("#mzml-file-counts")
        const $mzml_error = $("#mzml-file-error")
        const $modal = $("#explorer-modal")
        let save: any = null
        let check: boolean = false

        $(e.selector).on("selected.to", function (e: JQuery.Event, data: SelectedClass) {
            const state = data.state
            const files = data.selected
            check = data.key === key
            if (!check || files.length === 0) {
                return
            }
            save = { mountpoint: state.mountpoint, parent: state.parent, mzml: files }
        })
        $modal.on("hidden.bs.modal", function (e) {
            if (save === null || !check) return
            $mzml_counts.empty()
            $mzml_error.empty()
            $.get(JobConfig.check_mzml_url, save)
                .then((json: Counts) => {
                    if (json.status !== "OK") {
                        toastr.error(json.msg)
                        $mzml_error.html(make_error(json.msg))
                        return
                    }
                    $mzml_counts.html(make_table(json.counts))
                })
                .fail(() => {
                    const msg = "Can't determine spectra count!"
                    toastr.error(msg)
                    $mzml_error.html(make_error(msg))
                })
        })
        function make_table(counts: { [key: string]: number }): string {
            const p = `<b>${save.mountpoint}</b>:${save.parent}`
            const l = ["<tr><th>file</th><th>spectra</th></tr>"]
            for (let key in counts) {
                const count = counts[key]
                l.push(`<tr><td>${p}/${key}</td><td>${count}</td></tr>`)
            }
            return `<table class="table file-list">${l.join("")}</table>`
        }
    }
    function make_table(json: { [key: string]: number }): string {
        const l = ["<tr><th>run</th><th>count</th></tr>"]
        for (let key in json) {
            const count = json[key]
            l.push(`<tr><td>${key}</td><td>${count}</td></tr>`)
        }
        return `<table class="table">${l.join("")}</table>`
    }

    function close_dialog(e: ExplorerClass) {
        const $explorer = $(e.selector)
        const $close = $explorer.parents(".modal").find('[data-bs-dismiss="modal"]')
        $explorer.on("doubleclick.to", function () {
            $close.trigger("click")
        })
    }
})

jQuery(function ($) {
    // deal with form submission
    const $form = $("#job")
    const $elem = $form.find('[name="labelledElement"]') as JQuery<HTMLSelectElement>
    const $isotope = $form.find('[name="labelledIsotopeNumber"]') as JQuery<HTMLSelectElement>
    const $pepxmlfiles = $form.find('[name="pepxmlfiles"]') as JQuery<HTMLInputElement>
    const $mzmlfiles = $form.find('[name="mzmlfiles"]') as JQuery<HTMLInputElement>
    const $protxmlfile = $form.find('[name="protxmlfile"]') as JQuery<HTMLInputElement>

    $form.on("submit", function (e) {
        e.preventDefault()
        if ($pepxmlfiles.val() == "") {
            toastr.error("please select some pepxml files")
            return
        }
        if ($mzmlfiles.val() == "") {
            toastr.error("please select some spectrum files")
            return
        }
        if ($protxmlfile.val() == "") {
            toastr.error("please select a protein file")
            return
        }
        const fd = new FormData(asform($form))
        return $.ajax({
            url: $form.attr("action"),
            data: fd,
            enctype: "multipart/form-data",
            processData: false,
            contentType: false,
            cache: false,
            type: $form.attr("method")
        })
            .then((json: JsonReply) => {
                toastr.info(json.msg)
                if (json.status == "OK") {
                    // change to job list page after 1 sec
                    setTimeout(() => {
                        window.location.href = JobConfig.job_index_url
                    }, 1000)
                }
            })
            .fail(function () {
                toastr.error("can't create job!")
            })
    })
    // keep isotope numbers in sync with element
    $elem.on("change", function (e) {
        const val = $(this).val()
        if (val === undefined) {
            return
        }
        // C,H,N etc.
        const iso = JobConfig.atomicProperties[val as string]
        $isotope.empty()
        iso.forEach((n, i) => {
            const v = `${n}`
            $isotope.append(new Option(v, v, i === 0))
        })
    })

    function asform($o: JQuery<HTMLElement>): HTMLFormElement {
        return $o[0] as HTMLFormElement
    }
})
