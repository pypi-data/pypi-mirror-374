"use strict";
jQuery(function ($) {
    const $download = $('button[form="filters"][type="submit"]');
    const $download_all = $("#download-all");
    const $form = $("#filters");
    const form = $form[0];
    $download.on("click", download);
    $download_all.on("click", download);
    function download(e) {
        if (!form.checkValidity()) {
            return;
        }
        const $self = $(e.currentTarget);
        // don't prevent form submission... delay off
        setTimeout(() => {
            blockResubmit($self, Config.dataid, "fa-download");
        }, 0);
    }
});
jQuery(function ($) {
    const $download = $("#image-download");
    $download.on("click", download);
    function download(e) {
        const $self = $(e.currentTarget);
        const name = $self.attr("href") || Config.dataid;
        setTimeout(() => {
            blockResubmit($self, name, "fa-image");
        }, 0);
    }
});
// Prevents double-submits by waiting for a cookie from the server.
function blockResubmit($self, name, icon) {
    const spinner = "fa-spin fa-spinner";
    const cookie = "fileDownload";
    const spincls = spinner
        .split(/\s+/)
        .map((a) => `.${a}`)
        .join("");
    const quit = off($self);
    var attempts = Config.max_download_attempts;
    const downloadTimer = window.setInterval(function () {
        const ok = getCookie(cookie) === "true";
        if (ok || attempts <= 0) {
            unblockSubmit(ok);
        }
        attempts--;
    }, 1000);
    function unblockSubmit(ok) {
        window.clearInterval(downloadTimer);
        expireCookie(cookie);
        on($self, ok, name);
        quit();
    }
    function getCookie(name) {
        const parts = document.cookie.split(name + "=");
        if (parts.length === 2)
            return parts[1].split(";")[0];
    }
    function expireCookie(name) {
        document.cookie =
            encodeURIComponent(name) + "=deleted; path=/; expires=" + new Date(0).toUTCString();
    }
    function on($self, ok, name) {
        $self.prop("disabled", false);
        $self.find(spincls).removeClass(spinner).addClass(icon);
        if (ok) {
            toastr.info(`Downloaded ${name}`);
        }
        else {
            toastr.warning(`Still waiting on download of ${name}`);
        }
    }
    function off($self) {
        $self.prop("disabled", true);
        $self
            .find("." + icon)
            .removeClass(icon)
            .addClass(spinner);
        return SubaCrop.spinner();
    }
}
