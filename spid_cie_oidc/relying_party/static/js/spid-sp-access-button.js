jQuery && function (t) {
    function i(i, n) {
        var d = i ? t(this) : n, o = t(d.attr("spid-idp-button")), r = d.hasClass("spid-idp-button-open")
        if (i) {
            if (t(i.target).hasClass("spid-idp-button-ignore")) return
            i.preventDefault(), i.stopPropagation()
        } else if (d !== n.target && t(n.target).hasClass("spid-idp-button-ignore")) return
        s(), r || d.hasClass("spid-idp-button-disabled") || (d.addClass("spid-idp-button-open"), o.data("spid-idp-button-trigger", d).show(), e(), o.trigger("show", { spidIDPButton: o, trigger: d }))
    } 
    
    function s(i) {
        var s = i ? t(i.target).parents().addBack() : null
        if (s && s.is(".spid-idp-button")) {
            if (!s.is(".spid-idp-button-menu")) return
            if (!s.is("A")) return
        } 
        t(document).find(".spid-idp-button:visible").each(function () {
            var i = t(this)
            i.hide().removeData("spid-idp-button-trigger").trigger("hide", { spidIDPButton: i })
        }), t(document).find(".spid-idp-button-open").removeClass("spid-idp-button-open")
    } 
    
    function e() {
        var i = t(".spid-idp-button:visible").eq(0), s = i.data("spid-idp-button-trigger"), e = s ? parseInt(s.attr("data-horizontal-offset") || 0, 10) : null, n = s ? parseInt(s.attr("data-vertical-offset") || 0, 10) : null
        0 !== i.length && s && (i.hasClass("spid-idp-button-relative") ? i.css({ left: i.hasClass("spid-idp-button-anchor-right") ? s.position().left - (i.outerWidth(!0) - s.outerWidth(!0)) - parseInt(s.css("margin-right"), 10) + e : s.position().left + parseInt(s.css("margin-left"), 10) + e, top: s.position().top + s.outerHeight(!0) - parseInt(s.css("margin-top"), 10) + n }) : i.css({ left: i.hasClass("spid-idp-button-anchor-right") ? s.offset().left - (i.outerWidth() - s.outerWidth()) + e : s.offset().left + e, top: s.offset().top + s.outerHeight() + n }))
    } t.extend(t.fn, {
        spidIDPButton: function (e, n) {
            switch (e) {
                case "show": return i(null, t(this)), t(this)
                case "hide": return s(), t(this)
                case "attach": return t(this).attr("spid-idp-button", n)
                case "detach": return s(), t(this).removeAttr("spid-idp-button")
                case "disable": return t(this).addClass("spid-idp-button-disabled")
                case "enable": return s(), t(this).removeClass("spid-idp-button-disabled")
            }
        }
    }), t(document).on("click.spid-idp-button", "[spid-idp-button]", i), t(document).on("click.spid-idp-button", s), t(window).on("resize", e)
}(jQuery)


jQuery && function (t) {
    function i(i, n) {
        var d = i ? t(this) : n, o = t(d.attr("cie-idp-button")), r = d.hasClass("cie-idp-button-open")
        if (i) {
            if (t(i.target).hasClass("cie-idp-button-ignore")) return
            i.preventDefault(), i.stopPropagation()
        } else if (d !== n.target && t(n.target).hasClass("cie-idp-button-ignore")) return
        s(), r || d.hasClass("cie-idp-button-disabled") || (d.addClass("cie-idp-button-open"), o.data("cie-idp-button-trigger", d).show(), e(), o.trigger("show", { cieIDPButton: o, trigger: d }))
    } 
    
    function s(i) {
        var s = i ? t(i.target).parents().addBack() : null
        if (s && s.is(".cie-idp-button")) {
            if (!s.is(".cie-idp-button-menu")) return
            if (!s.is("A")) return
        } 
        t(document).find(".cie-idp-button:visible").each(function () {
            var i = t(this)
            i.hide().removeData("cie-idp-button-trigger").trigger("hide", { cieIDPButton: i })
        }), t(document).find(".cie-idp-button-open").removeClass("cie-idp-button-open")
    } 
    
    function e() {
        var i = t(".cie-idp-button:visible").eq(0), s = i.data("cie-idp-button-trigger"), e = s ? parseInt(s.attr("data-horizontal-offset") || 0, 10) : null, n = s ? parseInt(s.attr("data-vertical-offset") || 0, 10) : null
        0 !== i.length && s && (i.hasClass("cie-idp-button-relative") ? i.css({ left: i.hasClass("cie-idp-button-anchor-right") ? s.position().left - (i.outerWidth(!0) - s.outerWidth(!0)) - parseInt(s.css("margin-right"), 10) + e : s.position().left + parseInt(s.css("margin-left"), 10) + e, top: s.position().top + s.outerHeight(!0) - parseInt(s.css("margin-top"), 10) + n }) : i.css({ left: i.hasClass("cie-idp-button-anchor-right") ? s.offset().left - (i.outerWidth() - s.outerWidth()) + e : s.offset().left + e, top: s.offset().top + s.outerHeight() + n }))
    } t.extend(t.fn, {
        cieIDPButton: function (e, n) {
            switch (e) {
                case "show": return i(null, t(this)), t(this)
                case "hide": return s(), t(this)
                case "attach": return t(this).attr("cie-idp-button", n)
                case "detach": return s(), t(this).removeAttr("cie-idp-button")
                case "disable": return t(this).addClass("cie-idp-button-disabled")
                case "enable": return s(), t(this).removeClass("cie-idp-button-disabled")
            }
        }
    }), t(document).on("click.cie-idp-button", "[cie-idp-button]", i), t(document).on("click.cie-idp-button", s), t(window).on("resize", e)
}(jQuery)