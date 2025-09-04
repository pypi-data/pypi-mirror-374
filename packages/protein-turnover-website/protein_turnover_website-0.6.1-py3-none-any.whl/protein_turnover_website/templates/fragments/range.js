"use strict";
function createslider(element) {
    const [inputStart, inputEnd] = element.querySelectorAll("input");
    const thumbLeft = element.querySelector(".thumb.left");
    const thumbRight = element.querySelector(".thumb.right");
    const rangeBetween = element.querySelector(".range-between");
    const labelMin = element.querySelector(".range-label-start");
    const labelMax = element.querySelector(".range-label-end");
    let step = 1.0;
    setStartValueCustomSlider();
    setEndValueCustomSlider();
    setEvents();
    return {
        reset
    };
    // functions
    function reset(config) {
        if (config.max <= config.min)
            return;
        step = config.step = config.step ? config.step : (config.max - config.min) / 100.0;
        inputStart.max = String(config.max);
        inputStart.min = String(config.min);
        inputStart.step = String(config.step);
        inputStart.value = String(inputStart.min);
        inputEnd.max = String(config.max);
        inputEnd.min = String(config.min);
        inputEnd.step = String(config.step);
        inputEnd.value = String(inputEnd.max);
        setTimeout(() => {
            setStartValueCustomSlider();
            setEndValueCustomSlider();
            setLabelValue(labelMin, inputStart);
            setLabelValue(labelMax, inputEnd);
        }, 0);
    }
    function setLabelValue(label, input) {
        label.innerHTML = `${input.value}`;
    }
    function setStartValueCustomSlider() {
        const maximum = Math.min(parseFloat(inputStart.value), parseFloat(inputEnd.value) - step);
        const percent = ((maximum - +inputStart.min) / (+inputStart.max - +inputStart.min)) * 100;
        thumbLeft.style.left = percent + "%";
        rangeBetween.style.left = percent + "%";
    }
    function setEndValueCustomSlider() {
        const minimum = Math.max(parseFloat(inputEnd.value), parseFloat(inputStart.value) + step);
        const percent = ((minimum - +inputEnd.min) / (+inputEnd.max - +inputEnd.min)) * 100;
        thumbRight.style.right = 100 - percent + "%";
        rangeBetween.style.right = 100 - percent + "%";
    }
    function setEvents() {
        inputStart.addEventListener("input", () => {
            setStartValueCustomSlider();
            setLabelValue(labelMin, inputStart);
        });
        inputEnd.addEventListener("input", () => {
            setEndValueCustomSlider();
            setLabelValue(labelMax, inputEnd);
        });
        // add css clases on hover and drag
        inputStart.addEventListener("mouseover", function () {
            thumbLeft.classList.add("hover");
        });
        inputStart.addEventListener("mouseout", function () {
            thumbLeft.classList.remove("hover");
        });
        inputStart.addEventListener("mousedown", function () {
            thumbLeft.classList.add("active");
        });
        inputStart.addEventListener("pointerup", function () {
            thumbLeft.classList.remove("active");
        });
        inputEnd.addEventListener("mouseover", function () {
            thumbRight.classList.add("hover");
        });
        inputEnd.addEventListener("mouseout", function () {
            thumbRight.classList.remove("hover");
        });
        inputEnd.addEventListener("mousedown", function () {
            thumbRight.classList.add("active");
        });
        inputEnd.addEventListener("pointerup", function () {
            thumbRight.classList.remove("active");
        });
        // Mobile
        inputStart.addEventListener("touchstart", function () {
            thumbLeft.classList.add("active");
        });
        inputStart.addEventListener("touchend", function () {
            thumbLeft.classList.remove("active");
        });
        inputEnd.addEventListener("touchstart", function () {
            thumbRight.classList.add("active");
        });
        inputEnd.addEventListener("touchend", function () {
            thumbRight.classList.remove("active");
        });
    }
}
