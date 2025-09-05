const {
  SvelteComponent: h,
  append_hydration: v,
  attr: y,
  children: m,
  claim_element: g,
  claim_text: b,
  detach: _,
  element: w,
  init: A,
  insert_hydration: E,
  noop: f,
  safe_not_equal: j,
  text: q,
  toggle_class: s
} = window.__gradio__svelte__internal;
function C(n) {
  let e, i;
  return {
    c() {
      e = w("div"), i = q(
        /*names_string*/
        n[2]
      ), this.h();
    },
    l(t) {
      e = g(t, "DIV", { class: !0 });
      var a = m(e);
      i = b(
        a,
        /*names_string*/
        n[2]
      ), a.forEach(_), this.h();
    },
    h() {
      y(e, "class", "svelte-1gecy8w"), s(
        e,
        "table",
        /*type*/
        n[0] === "table"
      ), s(
        e,
        "gallery",
        /*type*/
        n[0] === "gallery"
      ), s(
        e,
        "selected",
        /*selected*/
        n[1]
      );
    },
    m(t, a) {
      E(t, e, a), v(e, i);
    },
    p(t, [a]) {
      a & /*type*/
      1 && s(
        e,
        "table",
        /*type*/
        t[0] === "table"
      ), a & /*type*/
      1 && s(
        e,
        "gallery",
        /*type*/
        t[0] === "gallery"
      ), a & /*selected*/
      2 && s(
        e,
        "selected",
        /*selected*/
        t[1]
      );
    },
    i: f,
    o: f,
    d(t) {
      t && _(e);
    }
  };
}
function D(n, e, i) {
  let { value: t } = e, { type: a } = e, { selected: d = !1 } = e, { choices: c } = e, u = (t ? Array.isArray(t) ? t : [t] : []).map((l) => {
    var r;
    return (r = c.find((o) => o[1] === l)) === null || r === void 0 ? void 0 : r[0];
  }).filter((l) => l !== void 0).join(", ");
  return n.$$set = (l) => {
    "value" in l && i(3, t = l.value), "type" in l && i(0, a = l.type), "selected" in l && i(1, d = l.selected), "choices" in l && i(4, c = l.choices);
  }, [a, d, u, t, c];
}
class V extends h {
  constructor(e) {
    super(), A(this, e, D, C, j, {
      value: 3,
      type: 0,
      selected: 1,
      choices: 4
    });
  }
}
export {
  V as default
};
