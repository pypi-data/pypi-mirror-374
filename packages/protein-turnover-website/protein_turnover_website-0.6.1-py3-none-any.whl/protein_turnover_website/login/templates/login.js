"use strict";
jQuery(function ($) {
    let $pw = $("{{ '#password' if badpwd else '#email' }}");
    arm($pw);
    shake($pw);
    function shake($pw) {
        let on = { position: "relative", left: 0 };
        let off = { position: "none" };
        let fwd = { left: "+=20px" };
        let rev = { left: "-=20px" };
        $pw.css(on)
            .animate(rev, { duration: "fast" })
            .animate(fwd, { duration: "fast" })
            .animate(rev, { duration: "fast" })
            .animate(fwd, { duration: "fast", complete: () => $pw.css(off) });
    }
    function arm($tgt) {
        // $tgt.addClass('is-invalid');
        function key() {
            $tgt.removeClass("is-invalid");
            $tgt.off("keyup.invalid", key);
        }
        $tgt.on("keyup.invalid", key);
    }
});
