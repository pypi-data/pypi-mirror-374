var Rt = Object.defineProperty;
var Oe = (i) => {
  throw TypeError(i);
};
var Lt = (i, t, e) => t in i ? Rt(i, t, { enumerable: !0, configurable: !0, writable: !0, value: e }) : i[t] = e;
var S = (i, t, e) => Lt(i, typeof t != "symbol" ? t + "" : t, e), It = (i, t, e) => t.has(i) || Oe("Cannot " + e);
var Me = (i, t, e) => t.has(i) ? Oe("Cannot add the same private member more than once") : t instanceof WeakSet ? t.add(i) : t.set(i, e);
var le = (i, t, e) => (It(i, t, "access private method"), e);
function ve() {
  return {
    async: !1,
    breaks: !1,
    extensions: null,
    gfm: !0,
    hooks: null,
    pedantic: !1,
    renderer: null,
    silent: !1,
    tokenizer: null,
    walkTokens: null
  };
}
let j = ve();
function it(i) {
  j = i;
}
const st = /[&<>"']/, $t = new RegExp(st.source, "g"), at = /[<>"']|&(?!(#\d{1,7}|#[Xx][a-fA-F0-9]{1,6}|\w+);)/, zt = new RegExp(at.source, "g"), Ot = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;"
}, Pe = (i) => Ot[i];
function L(i, t) {
  if (t) {
    if (st.test(i))
      return i.replace($t, Pe);
  } else if (at.test(i))
    return i.replace(zt, Pe);
  return i;
}
const Mt = /&(#(?:\d+)|(?:#x[0-9A-Fa-f]+)|(?:\w+));?/ig;
function Pt(i) {
  return i.replace(Mt, (t, e) => (e = e.toLowerCase(), e === "colon" ? ":" : e.charAt(0) === "#" ? e.charAt(1) === "x" ? String.fromCharCode(parseInt(e.substring(2), 16)) : String.fromCharCode(+e.substring(1)) : ""));
}
const Nt = /(^|[^\[])\^/g;
function _(i, t) {
  let e = typeof i == "string" ? i : i.source;
  t = t || "";
  const n = {
    replace: (r, a) => {
      let s = typeof a == "string" ? a : a.source;
      return s = s.replace(Nt, "$1"), e = e.replace(r, s), n;
    },
    getRegex: () => new RegExp(e, t)
  };
  return n;
}
function Ne(i) {
  try {
    i = encodeURI(i).replace(/%25/g, "%");
  } catch {
    return null;
  }
  return i;
}
const ee = { exec: () => null };
function He(i, t) {
  const e = i.replace(/\|/g, (a, s, u) => {
    let l = !1, m = s;
    for (; --m >= 0 && u[m] === "\\"; )
      l = !l;
    return l ? "|" : " |";
  }), n = e.split(/ \|/);
  let r = 0;
  if (n[0].trim() || n.shift(), n.length > 0 && !n[n.length - 1].trim() && n.pop(), t)
    if (n.length > t)
      n.splice(t);
    else
      for (; n.length < t; )
        n.push("");
  for (; r < n.length; r++)
    n[r] = n[r].trim().replace(/\\\|/g, "|");
  return n;
}
function oe(i, t, e) {
  const n = i.length;
  if (n === 0)
    return "";
  let r = 0;
  for (; r < n && i.charAt(n - r - 1) === t; )
    r++;
  return i.slice(0, n - r);
}
function Ht(i, t) {
  if (i.indexOf(t[1]) === -1)
    return -1;
  let e = 0;
  for (let n = 0; n < i.length; n++)
    if (i[n] === "\\")
      n++;
    else if (i[n] === t[0])
      e++;
    else if (i[n] === t[1] && (e--, e < 0))
      return n;
  return -1;
}
function qe(i, t, e, n) {
  const r = t.href, a = t.title ? L(t.title) : null, s = i[1].replace(/\\([\[\]])/g, "$1");
  if (i[0].charAt(0) !== "!") {
    n.state.inLink = !0;
    const u = {
      type: "link",
      raw: e,
      href: r,
      title: a,
      text: s,
      tokens: n.inlineTokens(s)
    };
    return n.state.inLink = !1, u;
  }
  return {
    type: "image",
    raw: e,
    href: r,
    title: a,
    text: L(s)
  };
}
function qt(i, t) {
  const e = i.match(/^(\s+)(?:```)/);
  if (e === null)
    return t;
  const n = e[1];
  return t.split(`
`).map((r) => {
    const a = r.match(/^\s+/);
    if (a === null)
      return r;
    const [s] = a;
    return s.length >= n.length ? r.slice(n.length) : r;
  }).join(`
`);
}
class fe {
  // set by the lexer
  constructor(t) {
    S(this, "options");
    S(this, "rules");
    // set by the lexer
    S(this, "lexer");
    this.options = t || j;
  }
  space(t) {
    const e = this.rules.block.newline.exec(t);
    if (e && e[0].length > 0)
      return {
        type: "space",
        raw: e[0]
      };
  }
  code(t) {
    const e = this.rules.block.code.exec(t);
    if (e) {
      const n = e[0].replace(/^ {1,4}/gm, "");
      return {
        type: "code",
        raw: e[0],
        codeBlockStyle: "indented",
        text: this.options.pedantic ? n : oe(n, `
`)
      };
    }
  }
  fences(t) {
    const e = this.rules.block.fences.exec(t);
    if (e) {
      const n = e[0], r = qt(n, e[3] || "");
      return {
        type: "code",
        raw: n,
        lang: e[2] ? e[2].trim().replace(this.rules.inline.anyPunctuation, "$1") : e[2],
        text: r
      };
    }
  }
  heading(t) {
    const e = this.rules.block.heading.exec(t);
    if (e) {
      let n = e[2].trim();
      if (/#$/.test(n)) {
        const r = oe(n, "#");
        (this.options.pedantic || !r || / $/.test(r)) && (n = r.trim());
      }
      return {
        type: "heading",
        raw: e[0],
        depth: e[1].length,
        text: n,
        tokens: this.lexer.inline(n)
      };
    }
  }
  hr(t) {
    const e = this.rules.block.hr.exec(t);
    if (e)
      return {
        type: "hr",
        raw: e[0]
      };
  }
  blockquote(t) {
    const e = this.rules.block.blockquote.exec(t);
    if (e) {
      let n = e[0].replace(/\n {0,3}((?:=+|-+) *)(?=\n|$)/g, `
    $1`);
      n = oe(n.replace(/^ *>[ \t]?/gm, ""), `
`);
      const r = this.lexer.state.top;
      this.lexer.state.top = !0;
      const a = this.lexer.blockTokens(n);
      return this.lexer.state.top = r, {
        type: "blockquote",
        raw: e[0],
        tokens: a,
        text: n
      };
    }
  }
  list(t) {
    let e = this.rules.block.list.exec(t);
    if (e) {
      let n = e[1].trim();
      const r = n.length > 1, a = {
        type: "list",
        raw: "",
        ordered: r,
        start: r ? +n.slice(0, -1) : "",
        loose: !1,
        items: []
      };
      n = r ? `\\d{1,9}\\${n.slice(-1)}` : `\\${n}`, this.options.pedantic && (n = r ? n : "[*+-]");
      const s = new RegExp(`^( {0,3}${n})((?:[	 ][^\\n]*)?(?:\\n|$))`);
      let u = "", l = "", m = !1;
      for (; t; ) {
        let D = !1;
        if (!(e = s.exec(t)) || this.rules.block.hr.test(t))
          break;
        u = e[0], t = t.substring(u.length);
        let k = e[2].split(`
`, 1)[0].replace(/^\t+/, (v) => " ".repeat(3 * v.length)), b = t.split(`
`, 1)[0], F = 0;
        this.options.pedantic ? (F = 2, l = k.trimStart()) : (F = e[2].search(/[^ ]/), F = F > 4 ? 1 : F, l = k.slice(F), F += e[1].length);
        let B = !1;
        if (!k && /^ *$/.test(b) && (u += b + `
`, t = t.substring(b.length + 1), D = !0), !D) {
          const v = new RegExp(`^ {0,${Math.min(3, F - 1)}}(?:[*+-]|\\d{1,9}[.)])((?:[ 	][^\\n]*)?(?:\\n|$))`), c = new RegExp(`^ {0,${Math.min(3, F - 1)}}((?:- *){3,}|(?:_ *){3,}|(?:\\* *){3,})(?:\\n+|$)`), o = new RegExp(`^ {0,${Math.min(3, F - 1)}}(?:\`\`\`|~~~)`), h = new RegExp(`^ {0,${Math.min(3, F - 1)}}#`);
          for (; t; ) {
            const g = t.split(`
`, 1)[0];
            if (b = g, this.options.pedantic && (b = b.replace(/^ {1,4}(?=( {4})*[^ ])/g, "  ")), o.test(b) || h.test(b) || v.test(b) || c.test(t))
              break;
            if (b.search(/[^ ]/) >= F || !b.trim())
              l += `
` + b.slice(F);
            else {
              if (B || k.search(/[^ ]/) >= 4 || o.test(k) || h.test(k) || c.test(k))
                break;
              l += `
` + b;
            }
            !B && !b.trim() && (B = !0), u += g + `
`, t = t.substring(g.length + 1), k = b.slice(F);
          }
        }
        a.loose || (m ? a.loose = !0 : /\n *\n *$/.test(u) && (m = !0));
        let w = null, x;
        this.options.gfm && (w = /^\[[ xX]\] /.exec(l), w && (x = w[0] !== "[ ] ", l = l.replace(/^\[[ xX]\] +/, ""))), a.items.push({
          type: "list_item",
          raw: u,
          task: !!w,
          checked: x,
          loose: !1,
          text: l,
          tokens: []
        }), a.raw += u;
      }
      a.items[a.items.length - 1].raw = u.trimEnd(), a.items[a.items.length - 1].text = l.trimEnd(), a.raw = a.raw.trimEnd();
      for (let D = 0; D < a.items.length; D++)
        if (this.lexer.state.top = !1, a.items[D].tokens = this.lexer.blockTokens(a.items[D].text, []), !a.loose) {
          const k = a.items[D].tokens.filter((F) => F.type === "space"), b = k.length > 0 && k.some((F) => /\n.*\n/.test(F.raw));
          a.loose = b;
        }
      if (a.loose)
        for (let D = 0; D < a.items.length; D++)
          a.items[D].loose = !0;
      return a;
    }
  }
  html(t) {
    const e = this.rules.block.html.exec(t);
    if (e)
      return {
        type: "html",
        block: !0,
        raw: e[0],
        pre: e[1] === "pre" || e[1] === "script" || e[1] === "style",
        text: e[0]
      };
  }
  def(t) {
    const e = this.rules.block.def.exec(t);
    if (e) {
      const n = e[1].toLowerCase().replace(/\s+/g, " "), r = e[2] ? e[2].replace(/^<(.*)>$/, "$1").replace(this.rules.inline.anyPunctuation, "$1") : "", a = e[3] ? e[3].substring(1, e[3].length - 1).replace(this.rules.inline.anyPunctuation, "$1") : e[3];
      return {
        type: "def",
        tag: n,
        raw: e[0],
        href: r,
        title: a
      };
    }
  }
  table(t) {
    const e = this.rules.block.table.exec(t);
    if (!e || !/[:|]/.test(e[2]))
      return;
    const n = He(e[1]), r = e[2].replace(/^\||\| *$/g, "").split("|"), a = e[3] && e[3].trim() ? e[3].replace(/\n[ \t]*$/, "").split(`
`) : [], s = {
      type: "table",
      raw: e[0],
      header: [],
      align: [],
      rows: []
    };
    if (n.length === r.length) {
      for (const u of r)
        /^ *-+: *$/.test(u) ? s.align.push("right") : /^ *:-+: *$/.test(u) ? s.align.push("center") : /^ *:-+ *$/.test(u) ? s.align.push("left") : s.align.push(null);
      for (const u of n)
        s.header.push({
          text: u,
          tokens: this.lexer.inline(u)
        });
      for (const u of a)
        s.rows.push(He(u, s.header.length).map((l) => ({
          text: l,
          tokens: this.lexer.inline(l)
        })));
      return s;
    }
  }
  lheading(t) {
    const e = this.rules.block.lheading.exec(t);
    if (e)
      return {
        type: "heading",
        raw: e[0],
        depth: e[2].charAt(0) === "=" ? 1 : 2,
        text: e[1],
        tokens: this.lexer.inline(e[1])
      };
  }
  paragraph(t) {
    const e = this.rules.block.paragraph.exec(t);
    if (e) {
      const n = e[1].charAt(e[1].length - 1) === `
` ? e[1].slice(0, -1) : e[1];
      return {
        type: "paragraph",
        raw: e[0],
        text: n,
        tokens: this.lexer.inline(n)
      };
    }
  }
  text(t) {
    const e = this.rules.block.text.exec(t);
    if (e)
      return {
        type: "text",
        raw: e[0],
        text: e[0],
        tokens: this.lexer.inline(e[0])
      };
  }
  escape(t) {
    const e = this.rules.inline.escape.exec(t);
    if (e)
      return {
        type: "escape",
        raw: e[0],
        text: L(e[1])
      };
  }
  tag(t) {
    const e = this.rules.inline.tag.exec(t);
    if (e)
      return !this.lexer.state.inLink && /^<a /i.test(e[0]) ? this.lexer.state.inLink = !0 : this.lexer.state.inLink && /^<\/a>/i.test(e[0]) && (this.lexer.state.inLink = !1), !this.lexer.state.inRawBlock && /^<(pre|code|kbd|script)(\s|>)/i.test(e[0]) ? this.lexer.state.inRawBlock = !0 : this.lexer.state.inRawBlock && /^<\/(pre|code|kbd|script)(\s|>)/i.test(e[0]) && (this.lexer.state.inRawBlock = !1), {
        type: "html",
        raw: e[0],
        inLink: this.lexer.state.inLink,
        inRawBlock: this.lexer.state.inRawBlock,
        block: !1,
        text: e[0]
      };
  }
  link(t) {
    const e = this.rules.inline.link.exec(t);
    if (e) {
      const n = e[2].trim();
      if (!this.options.pedantic && /^</.test(n)) {
        if (!/>$/.test(n))
          return;
        const s = oe(n.slice(0, -1), "\\");
        if ((n.length - s.length) % 2 === 0)
          return;
      } else {
        const s = Ht(e[2], "()");
        if (s > -1) {
          const l = (e[0].indexOf("!") === 0 ? 5 : 4) + e[1].length + s;
          e[2] = e[2].substring(0, s), e[0] = e[0].substring(0, l).trim(), e[3] = "";
        }
      }
      let r = e[2], a = "";
      if (this.options.pedantic) {
        const s = /^([^'"]*[^\s])\s+(['"])(.*)\2/.exec(r);
        s && (r = s[1], a = s[3]);
      } else
        a = e[3] ? e[3].slice(1, -1) : "";
      return r = r.trim(), /^</.test(r) && (this.options.pedantic && !/>$/.test(n) ? r = r.slice(1) : r = r.slice(1, -1)), qe(e, {
        href: r && r.replace(this.rules.inline.anyPunctuation, "$1"),
        title: a && a.replace(this.rules.inline.anyPunctuation, "$1")
      }, e[0], this.lexer);
    }
  }
  reflink(t, e) {
    let n;
    if ((n = this.rules.inline.reflink.exec(t)) || (n = this.rules.inline.nolink.exec(t))) {
      const r = (n[2] || n[1]).replace(/\s+/g, " "), a = e[r.toLowerCase()];
      if (!a) {
        const s = n[0].charAt(0);
        return {
          type: "text",
          raw: s,
          text: s
        };
      }
      return qe(n, a, n[0], this.lexer);
    }
  }
  emStrong(t, e, n = "") {
    let r = this.rules.inline.emStrongLDelim.exec(t);
    if (!r || r[3] && n.match(/[\p{L}\p{N}]/u))
      return;
    if (!(r[1] || r[2] || "") || !n || this.rules.inline.punctuation.exec(n)) {
      const s = [...r[0]].length - 1;
      let u, l, m = s, D = 0;
      const k = r[0][0] === "*" ? this.rules.inline.emStrongRDelimAst : this.rules.inline.emStrongRDelimUnd;
      for (k.lastIndex = 0, e = e.slice(-1 * t.length + s); (r = k.exec(e)) != null; ) {
        if (u = r[1] || r[2] || r[3] || r[4] || r[5] || r[6], !u)
          continue;
        if (l = [...u].length, r[3] || r[4]) {
          m += l;
          continue;
        } else if ((r[5] || r[6]) && s % 3 && !((s + l) % 3)) {
          D += l;
          continue;
        }
        if (m -= l, m > 0)
          continue;
        l = Math.min(l, l + m + D);
        const b = [...r[0]][0].length, F = t.slice(0, s + r.index + b + l);
        if (Math.min(s, l) % 2) {
          const w = F.slice(1, -1);
          return {
            type: "em",
            raw: F,
            text: w,
            tokens: this.lexer.inlineTokens(w)
          };
        }
        const B = F.slice(2, -2);
        return {
          type: "strong",
          raw: F,
          text: B,
          tokens: this.lexer.inlineTokens(B)
        };
      }
    }
  }
  codespan(t) {
    const e = this.rules.inline.code.exec(t);
    if (e) {
      let n = e[2].replace(/\n/g, " ");
      const r = /[^ ]/.test(n), a = /^ /.test(n) && / $/.test(n);
      return r && a && (n = n.substring(1, n.length - 1)), n = L(n, !0), {
        type: "codespan",
        raw: e[0],
        text: n
      };
    }
  }
  br(t) {
    const e = this.rules.inline.br.exec(t);
    if (e)
      return {
        type: "br",
        raw: e[0]
      };
  }
  del(t) {
    const e = this.rules.inline.del.exec(t);
    if (e)
      return {
        type: "del",
        raw: e[0],
        text: e[2],
        tokens: this.lexer.inlineTokens(e[2])
      };
  }
  autolink(t) {
    const e = this.rules.inline.autolink.exec(t);
    if (e) {
      let n, r;
      return e[2] === "@" ? (n = L(e[1]), r = "mailto:" + n) : (n = L(e[1]), r = n), {
        type: "link",
        raw: e[0],
        text: n,
        href: r,
        tokens: [
          {
            type: "text",
            raw: n,
            text: n
          }
        ]
      };
    }
  }
  url(t) {
    var n;
    let e;
    if (e = this.rules.inline.url.exec(t)) {
      let r, a;
      if (e[2] === "@")
        r = L(e[0]), a = "mailto:" + r;
      else {
        let s;
        do
          s = e[0], e[0] = ((n = this.rules.inline._backpedal.exec(e[0])) == null ? void 0 : n[0]) ?? "";
        while (s !== e[0]);
        r = L(e[0]), e[1] === "www." ? a = "http://" + e[0] : a = e[0];
      }
      return {
        type: "link",
        raw: e[0],
        text: r,
        href: a,
        tokens: [
          {
            type: "text",
            raw: r,
            text: r
          }
        ]
      };
    }
  }
  inlineText(t) {
    const e = this.rules.inline.text.exec(t);
    if (e) {
      let n;
      return this.lexer.state.inRawBlock ? n = e[0] : n = L(e[0]), {
        type: "text",
        raw: e[0],
        text: n
      };
    }
  }
}
const Gt = /^(?: *(?:\n|$))+/, Ut = /^( {4}[^\n]+(?:\n(?: *(?:\n|$))*)?)+/, jt = /^ {0,3}(`{3,}(?=[^`\n]*(?:\n|$))|~{3,})([^\n]*)(?:\n|$)(?:|([\s\S]*?)(?:\n|$))(?: {0,3}\1[~`]* *(?=\n|$)|$)/, ne = /^ {0,3}((?:-[\t ]*){3,}|(?:_[ \t]*){3,}|(?:\*[ \t]*){3,})(?:\n+|$)/, Zt = /^ {0,3}(#{1,6})(?=\s|$)(.*)(?:\n+|$)/, ut = /(?:[*+-]|\d{1,9}[.)])/, lt = _(/^(?!bull |blockCode|fences|blockquote|heading|html)((?:.|\n(?!\s*?\n|bull |blockCode|fences|blockquote|heading|html))+?)\n {0,3}(=+|-+) *(?:\n+|$)/).replace(/bull/g, ut).replace(/blockCode/g, / {4}/).replace(/fences/g, / {0,3}(?:`{3,}|~{3,})/).replace(/blockquote/g, / {0,3}>/).replace(/heading/g, / {0,3}#{1,6}/).replace(/html/g, / {0,3}<[^\n>]+>\n/).getRegex(), Se = /^([^\n]+(?:\n(?!hr|heading|lheading|blockquote|fences|list|html|table| +\n)[^\n]+)*)/, Xt = /^[^\n]+/, Be = /(?!\s*\])(?:\\.|[^\[\]\\])+/, Wt = _(/^ {0,3}\[(label)\]: *(?:\n *)?([^<\s][^\s]*|<.*?>)(?:(?: +(?:\n *)?| *\n *)(title))? *(?:\n+|$)/).replace("label", Be).replace("title", /(?:"(?:\\"?|[^"\\])*"|'[^'\n]*(?:\n[^'\n]+)*\n?'|\([^()]*\))/).getRegex(), Vt = _(/^( {0,3}bull)([ \t][^\n]+?)?(?:\n|$)/).replace(/bull/g, ut).getRegex(), Fe = "address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|frame|frameset|h[1-6]|head|header|hr|html|iframe|legend|li|link|main|menu|menuitem|meta|nav|noframes|ol|optgroup|option|p|param|search|section|summary|table|tbody|td|tfoot|th|thead|title|tr|track|ul", Te = /<!--(?:-?>|[\s\S]*?(?:-->|$))/, Yt = _("^ {0,3}(?:<(script|pre|style|textarea)[\\s>][\\s\\S]*?(?:</\\1>[^\\n]*\\n+|$)|comment[^\\n]*(\\n+|$)|<\\?[\\s\\S]*?(?:\\?>\\n*|$)|<![A-Z][\\s\\S]*?(?:>\\n*|$)|<!\\[CDATA\\[[\\s\\S]*?(?:\\]\\]>\\n*|$)|</?(tag)(?: +|\\n|/?>)[\\s\\S]*?(?:(?:\\n *)+\\n|$)|<(?!script|pre|style|textarea)([a-z][\\w-]*)(?:attribute)*? */?>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n *)+\\n|$)|</(?!script|pre|style|textarea)[a-z][\\w-]*\\s*>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n *)+\\n|$))", "i").replace("comment", Te).replace("tag", Fe).replace("attribute", / +[a-zA-Z:_][\w.:-]*(?: *= *"[^"\n]*"| *= *'[^'\n]*'| *= *[^\s"'=<>`]+)?/).getRegex(), ot = _(Se).replace("hr", ne).replace("heading", " {0,3}#{1,6}(?:\\s|$)").replace("|lheading", "").replace("|table", "").replace("blockquote", " {0,3}>").replace("fences", " {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list", " {0,3}(?:[*+-]|1[.)]) ").replace("html", "</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag", Fe).getRegex(), Qt = _(/^( {0,3}> ?(paragraph|[^\n]*)(?:\n|$))+/).replace("paragraph", ot).getRegex(), Re = {
  blockquote: Qt,
  code: Ut,
  def: Wt,
  fences: jt,
  heading: Zt,
  hr: ne,
  html: Yt,
  lheading: lt,
  list: Vt,
  newline: Gt,
  paragraph: ot,
  table: ee,
  text: Xt
}, Ge = _("^ *([^\\n ].*)\\n {0,3}((?:\\| *)?:?-+:? *(?:\\| *:?-+:? *)*(?:\\| *)?)(?:\\n((?:(?! *\\n|hr|heading|blockquote|code|fences|list|html).*(?:\\n|$))*)\\n*|$)").replace("hr", ne).replace("heading", " {0,3}#{1,6}(?:\\s|$)").replace("blockquote", " {0,3}>").replace("code", " {4}[^\\n]").replace("fences", " {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list", " {0,3}(?:[*+-]|1[.)]) ").replace("html", "</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag", Fe).getRegex(), Kt = {
  ...Re,
  table: Ge,
  paragraph: _(Se).replace("hr", ne).replace("heading", " {0,3}#{1,6}(?:\\s|$)").replace("|lheading", "").replace("table", Ge).replace("blockquote", " {0,3}>").replace("fences", " {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list", " {0,3}(?:[*+-]|1[.)]) ").replace("html", "</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag", Fe).getRegex()
}, Jt = {
  ...Re,
  html: _(`^ *(?:comment *(?:\\n|\\s*$)|<(tag)[\\s\\S]+?</\\1> *(?:\\n{2,}|\\s*$)|<tag(?:"[^"]*"|'[^']*'|\\s[^'"/>\\s]*)*?/?> *(?:\\n{2,}|\\s*$))`).replace("comment", Te).replace(/tag/g, "(?!(?:a|em|strong|small|s|cite|q|dfn|abbr|data|time|code|var|samp|kbd|sub|sup|i|b|u|mark|ruby|rt|rp|bdi|bdo|span|br|wbr|ins|del|img)\\b)\\w+(?!:|[^\\w\\s@]*@)\\b").getRegex(),
  def: /^ *\[([^\]]+)\]: *<?([^\s>]+)>?(?: +(["(][^\n]+[")]))? *(?:\n+|$)/,
  heading: /^(#{1,6})(.*)(?:\n+|$)/,
  fences: ee,
  // fences not supported
  lheading: /^(.+?)\n {0,3}(=+|-+) *(?:\n+|$)/,
  paragraph: _(Se).replace("hr", ne).replace("heading", ` *#{1,6} *[^
]`).replace("lheading", lt).replace("|table", "").replace("blockquote", " {0,3}>").replace("|fences", "").replace("|list", "").replace("|html", "").replace("|tag", "").getRegex()
}, ct = /^\\([!"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])/, en = /^(`+)([^`]|[^`][\s\S]*?[^`])\1(?!`)/, pt = /^( {2,}|\\)\n(?!\s*$)/, tn = /^(`+|[^`])(?:(?= {2,}\n)|[\s\S]*?(?:(?=[\\<!\[`*_]|\b_|$)|[^ ](?= {2,}\n)))/, re = "\\p{P}\\p{S}", nn = _(/^((?![*_])[\spunctuation])/, "u").replace(/punctuation/g, re).getRegex(), rn = /\[[^[\]]*?\]\([^\(\)]*?\)|`[^`]*?`|<[^<>]*?>/g, sn = _(/^(?:\*+(?:((?!\*)[punct])|[^\s*]))|^_+(?:((?!_)[punct])|([^\s_]))/, "u").replace(/punct/g, re).getRegex(), an = _("^[^_*]*?__[^_*]*?\\*[^_*]*?(?=__)|[^*]+(?=[^*])|(?!\\*)[punct](\\*+)(?=[\\s]|$)|[^punct\\s](\\*+)(?!\\*)(?=[punct\\s]|$)|(?!\\*)[punct\\s](\\*+)(?=[^punct\\s])|[\\s](\\*+)(?!\\*)(?=[punct])|(?!\\*)[punct](\\*+)(?!\\*)(?=[punct])|[^punct\\s](\\*+)(?=[^punct\\s])", "gu").replace(/punct/g, re).getRegex(), un = _("^[^_*]*?\\*\\*[^_*]*?_[^_*]*?(?=\\*\\*)|[^_]+(?=[^_])|(?!_)[punct](_+)(?=[\\s]|$)|[^punct\\s](_+)(?!_)(?=[punct\\s]|$)|(?!_)[punct\\s](_+)(?=[^punct\\s])|[\\s](_+)(?!_)(?=[punct])|(?!_)[punct](_+)(?!_)(?=[punct])", "gu").replace(/punct/g, re).getRegex(), ln = _(/\\([punct])/, "gu").replace(/punct/g, re).getRegex(), on = _(/^<(scheme:[^\s\x00-\x1f<>]*|email)>/).replace("scheme", /[a-zA-Z][a-zA-Z0-9+.-]{1,31}/).replace("email", /[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+(@)[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+(?![-_])/).getRegex(), cn = _(Te).replace("(?:-->|$)", "-->").getRegex(), pn = _("^comment|^</[a-zA-Z][\\w:-]*\\s*>|^<[a-zA-Z][\\w-]*(?:attribute)*?\\s*/?>|^<\\?[\\s\\S]*?\\?>|^<![a-zA-Z]+\\s[\\s\\S]*?>|^<!\\[CDATA\\[[\\s\\S]*?\\]\\]>").replace("comment", cn).replace("attribute", /\s+[a-zA-Z:_][\w.:-]*(?:\s*=\s*"[^"]*"|\s*=\s*'[^']*'|\s*=\s*[^\s"'=<>`]+)?/).getRegex(), De = /(?:\[(?:\\.|[^\[\]\\])*\]|\\.|`[^`]*`|[^\[\]\\`])*?/, hn = _(/^!?\[(label)\]\(\s*(href)(?:\s+(title))?\s*\)/).replace("label", De).replace("href", /<(?:\\.|[^\n<>\\])+>|[^\s\x00-\x1f]*/).replace("title", /"(?:\\"?|[^"\\])*"|'(?:\\'?|[^'\\])*'|\((?:\\\)?|[^)\\])*\)/).getRegex(), ht = _(/^!?\[(label)\]\[(ref)\]/).replace("label", De).replace("ref", Be).getRegex(), gt = _(/^!?\[(ref)\](?:\[\])?/).replace("ref", Be).getRegex(), gn = _("reflink|nolink(?!\\()", "g").replace("reflink", ht).replace("nolink", gt).getRegex(), Le = {
  _backpedal: ee,
  // only used for GFM url
  anyPunctuation: ln,
  autolink: on,
  blockSkip: rn,
  br: pt,
  code: en,
  del: ee,
  emStrongLDelim: sn,
  emStrongRDelimAst: an,
  emStrongRDelimUnd: un,
  escape: ct,
  link: hn,
  nolink: gt,
  punctuation: nn,
  reflink: ht,
  reflinkSearch: gn,
  tag: pn,
  text: tn,
  url: ee
}, dn = {
  ...Le,
  link: _(/^!?\[(label)\]\((.*?)\)/).replace("label", De).getRegex(),
  reflink: _(/^!?\[(label)\]\s*\[([^\]]*)\]/).replace("label", De).getRegex()
}, Ce = {
  ...Le,
  escape: _(ct).replace("])", "~|])").getRegex(),
  url: _(/^((?:ftp|https?):\/\/|www\.)(?:[a-zA-Z0-9\-]+\.?)+[^\s<]*|^email/, "i").replace("email", /[A-Za-z0-9._+-]+(@)[a-zA-Z0-9-_]+(?:\.[a-zA-Z0-9-_]*[a-zA-Z0-9])+(?![-_])/).getRegex(),
  _backpedal: /(?:[^?!.,:;*_'"~()&]+|\([^)]*\)|&(?![a-zA-Z0-9]+;$)|[?!.,:;*_'"~)]+(?!$))+/,
  del: /^(~~?)(?=[^\s~])([\s\S]*?[^\s~])\1(?=[^~]|$)/,
  text: /^([`~]+|[^`~])(?:(?= {2,}\n)|(?=[a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-]+@)|[\s\S]*?(?:(?=[\\<!\[`*~_]|\b_|https?:\/\/|ftp:\/\/|www\.|$)|[^ ](?= {2,}\n)|[^a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-](?=[a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-]+@)))/
}, fn = {
  ...Ce,
  br: _(pt).replace("{2,}", "*").getRegex(),
  text: _(Ce.text).replace("\\b_", "\\b_| {2,}\\n").replace(/\{2,\}/g, "*").getRegex()
}, ce = {
  normal: Re,
  gfm: Kt,
  pedantic: Jt
}, J = {
  normal: Le,
  gfm: Ce,
  breaks: fn,
  pedantic: dn
};
class O {
  constructor(t) {
    S(this, "tokens");
    S(this, "options");
    S(this, "state");
    S(this, "tokenizer");
    S(this, "inlineQueue");
    this.tokens = [], this.tokens.links = /* @__PURE__ */ Object.create(null), this.options = t || j, this.options.tokenizer = this.options.tokenizer || new fe(), this.tokenizer = this.options.tokenizer, this.tokenizer.options = this.options, this.tokenizer.lexer = this, this.inlineQueue = [], this.state = {
      inLink: !1,
      inRawBlock: !1,
      top: !0
    };
    const e = {
      block: ce.normal,
      inline: J.normal
    };
    this.options.pedantic ? (e.block = ce.pedantic, e.inline = J.pedantic) : this.options.gfm && (e.block = ce.gfm, this.options.breaks ? e.inline = J.breaks : e.inline = J.gfm), this.tokenizer.rules = e;
  }
  /**
   * Expose Rules
   */
  static get rules() {
    return {
      block: ce,
      inline: J
    };
  }
  /**
   * Static Lex Method
   */
  static lex(t, e) {
    return new O(e).lex(t);
  }
  /**
   * Static Lex Inline Method
   */
  static lexInline(t, e) {
    return new O(e).inlineTokens(t);
  }
  /**
   * Preprocessing
   */
  lex(t) {
    t = t.replace(/\r\n|\r/g, `
`), this.blockTokens(t, this.tokens);
    for (let e = 0; e < this.inlineQueue.length; e++) {
      const n = this.inlineQueue[e];
      this.inlineTokens(n.src, n.tokens);
    }
    return this.inlineQueue = [], this.tokens;
  }
  blockTokens(t, e = []) {
    this.options.pedantic ? t = t.replace(/\t/g, "    ").replace(/^ +$/gm, "") : t = t.replace(/^( *)(\t+)/gm, (u, l, m) => l + "    ".repeat(m.length));
    let n, r, a, s;
    for (; t; )
      if (!(this.options.extensions && this.options.extensions.block && this.options.extensions.block.some((u) => (n = u.call({ lexer: this }, t, e)) ? (t = t.substring(n.raw.length), e.push(n), !0) : !1))) {
        if (n = this.tokenizer.space(t)) {
          t = t.substring(n.raw.length), n.raw.length === 1 && e.length > 0 ? e[e.length - 1].raw += `
` : e.push(n);
          continue;
        }
        if (n = this.tokenizer.code(t)) {
          t = t.substring(n.raw.length), r = e[e.length - 1], r && (r.type === "paragraph" || r.type === "text") ? (r.raw += `
` + n.raw, r.text += `
` + n.text, this.inlineQueue[this.inlineQueue.length - 1].src = r.text) : e.push(n);
          continue;
        }
        if (n = this.tokenizer.fences(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.heading(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.hr(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.blockquote(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.list(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.html(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.def(t)) {
          t = t.substring(n.raw.length), r = e[e.length - 1], r && (r.type === "paragraph" || r.type === "text") ? (r.raw += `
` + n.raw, r.text += `
` + n.raw, this.inlineQueue[this.inlineQueue.length - 1].src = r.text) : this.tokens.links[n.tag] || (this.tokens.links[n.tag] = {
            href: n.href,
            title: n.title
          });
          continue;
        }
        if (n = this.tokenizer.table(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.lheading(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (a = t, this.options.extensions && this.options.extensions.startBlock) {
          let u = 1 / 0;
          const l = t.slice(1);
          let m;
          this.options.extensions.startBlock.forEach((D) => {
            m = D.call({ lexer: this }, l), typeof m == "number" && m >= 0 && (u = Math.min(u, m));
          }), u < 1 / 0 && u >= 0 && (a = t.substring(0, u + 1));
        }
        if (this.state.top && (n = this.tokenizer.paragraph(a))) {
          r = e[e.length - 1], s && r.type === "paragraph" ? (r.raw += `
` + n.raw, r.text += `
` + n.text, this.inlineQueue.pop(), this.inlineQueue[this.inlineQueue.length - 1].src = r.text) : e.push(n), s = a.length !== t.length, t = t.substring(n.raw.length);
          continue;
        }
        if (n = this.tokenizer.text(t)) {
          t = t.substring(n.raw.length), r = e[e.length - 1], r && r.type === "text" ? (r.raw += `
` + n.raw, r.text += `
` + n.text, this.inlineQueue.pop(), this.inlineQueue[this.inlineQueue.length - 1].src = r.text) : e.push(n);
          continue;
        }
        if (t) {
          const u = "Infinite loop on byte: " + t.charCodeAt(0);
          if (this.options.silent) {
            console.error(u);
            break;
          } else
            throw new Error(u);
        }
      }
    return this.state.top = !0, e;
  }
  inline(t, e = []) {
    return this.inlineQueue.push({ src: t, tokens: e }), e;
  }
  /**
   * Lexing/Compiling
   */
  inlineTokens(t, e = []) {
    let n, r, a, s = t, u, l, m;
    if (this.tokens.links) {
      const D = Object.keys(this.tokens.links);
      if (D.length > 0)
        for (; (u = this.tokenizer.rules.inline.reflinkSearch.exec(s)) != null; )
          D.includes(u[0].slice(u[0].lastIndexOf("[") + 1, -1)) && (s = s.slice(0, u.index) + "[" + "a".repeat(u[0].length - 2) + "]" + s.slice(this.tokenizer.rules.inline.reflinkSearch.lastIndex));
    }
    for (; (u = this.tokenizer.rules.inline.blockSkip.exec(s)) != null; )
      s = s.slice(0, u.index) + "[" + "a".repeat(u[0].length - 2) + "]" + s.slice(this.tokenizer.rules.inline.blockSkip.lastIndex);
    for (; (u = this.tokenizer.rules.inline.anyPunctuation.exec(s)) != null; )
      s = s.slice(0, u.index) + "++" + s.slice(this.tokenizer.rules.inline.anyPunctuation.lastIndex);
    for (; t; )
      if (l || (m = ""), l = !1, !(this.options.extensions && this.options.extensions.inline && this.options.extensions.inline.some((D) => (n = D.call({ lexer: this }, t, e)) ? (t = t.substring(n.raw.length), e.push(n), !0) : !1))) {
        if (n = this.tokenizer.escape(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.tag(t)) {
          t = t.substring(n.raw.length), r = e[e.length - 1], r && n.type === "text" && r.type === "text" ? (r.raw += n.raw, r.text += n.text) : e.push(n);
          continue;
        }
        if (n = this.tokenizer.link(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.reflink(t, this.tokens.links)) {
          t = t.substring(n.raw.length), r = e[e.length - 1], r && n.type === "text" && r.type === "text" ? (r.raw += n.raw, r.text += n.text) : e.push(n);
          continue;
        }
        if (n = this.tokenizer.emStrong(t, s, m)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.codespan(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.br(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.del(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (n = this.tokenizer.autolink(t)) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (!this.state.inLink && (n = this.tokenizer.url(t))) {
          t = t.substring(n.raw.length), e.push(n);
          continue;
        }
        if (a = t, this.options.extensions && this.options.extensions.startInline) {
          let D = 1 / 0;
          const k = t.slice(1);
          let b;
          this.options.extensions.startInline.forEach((F) => {
            b = F.call({ lexer: this }, k), typeof b == "number" && b >= 0 && (D = Math.min(D, b));
          }), D < 1 / 0 && D >= 0 && (a = t.substring(0, D + 1));
        }
        if (n = this.tokenizer.inlineText(a)) {
          t = t.substring(n.raw.length), n.raw.slice(-1) !== "_" && (m = n.raw.slice(-1)), l = !0, r = e[e.length - 1], r && r.type === "text" ? (r.raw += n.raw, r.text += n.text) : e.push(n);
          continue;
        }
        if (t) {
          const D = "Infinite loop on byte: " + t.charCodeAt(0);
          if (this.options.silent) {
            console.error(D);
            break;
          } else
            throw new Error(D);
        }
      }
    return e;
  }
}
class me {
  constructor(t) {
    S(this, "options");
    this.options = t || j;
  }
  code(t, e, n) {
    var a;
    const r = (a = (e || "").match(/^\S*/)) == null ? void 0 : a[0];
    return t = t.replace(/\n$/, "") + `
`, r ? '<pre><code class="language-' + L(r) + '">' + (n ? t : L(t, !0)) + `</code></pre>
` : "<pre><code>" + (n ? t : L(t, !0)) + `</code></pre>
`;
  }
  blockquote(t) {
    return `<blockquote>
${t}</blockquote>
`;
  }
  html(t, e) {
    return t;
  }
  heading(t, e, n) {
    return `<h${e}>${t}</h${e}>
`;
  }
  hr() {
    return `<hr>
`;
  }
  list(t, e, n) {
    const r = e ? "ol" : "ul", a = e && n !== 1 ? ' start="' + n + '"' : "";
    return "<" + r + a + `>
` + t + "</" + r + `>
`;
  }
  listitem(t, e, n) {
    return `<li>${t}</li>
`;
  }
  checkbox(t) {
    return "<input " + (t ? 'checked="" ' : "") + 'disabled="" type="checkbox">';
  }
  paragraph(t) {
    return `<p>${t}</p>
`;
  }
  table(t, e) {
    return e && (e = `<tbody>${e}</tbody>`), `<table>
<thead>
` + t + `</thead>
` + e + `</table>
`;
  }
  tablerow(t) {
    return `<tr>
${t}</tr>
`;
  }
  tablecell(t, e) {
    const n = e.header ? "th" : "td";
    return (e.align ? `<${n} align="${e.align}">` : `<${n}>`) + t + `</${n}>
`;
  }
  /**
   * span level renderer
   */
  strong(t) {
    return `<strong>${t}</strong>`;
  }
  em(t) {
    return `<em>${t}</em>`;
  }
  codespan(t) {
    return `<code>${t}</code>`;
  }
  br() {
    return "<br>";
  }
  del(t) {
    return `<del>${t}</del>`;
  }
  link(t, e, n) {
    const r = Ne(t);
    if (r === null)
      return n;
    t = r;
    let a = '<a href="' + t + '"';
    return e && (a += ' title="' + e + '"'), a += ">" + n + "</a>", a;
  }
  image(t, e, n) {
    const r = Ne(t);
    if (r === null)
      return n;
    t = r;
    let a = `<img src="${t}" alt="${n}"`;
    return e && (a += ` title="${e}"`), a += ">", a;
  }
  text(t) {
    return t;
  }
}
class Ie {
  // no need for block level renderers
  strong(t) {
    return t;
  }
  em(t) {
    return t;
  }
  codespan(t) {
    return t;
  }
  del(t) {
    return t;
  }
  html(t) {
    return t;
  }
  text(t) {
    return t;
  }
  link(t, e, n) {
    return "" + n;
  }
  image(t, e, n) {
    return "" + n;
  }
  br() {
    return "";
  }
}
class M {
  constructor(t) {
    S(this, "options");
    S(this, "renderer");
    S(this, "textRenderer");
    this.options = t || j, this.options.renderer = this.options.renderer || new me(), this.renderer = this.options.renderer, this.renderer.options = this.options, this.textRenderer = new Ie();
  }
  /**
   * Static Parse Method
   */
  static parse(t, e) {
    return new M(e).parse(t);
  }
  /**
   * Static Parse Inline Method
   */
  static parseInline(t, e) {
    return new M(e).parseInline(t);
  }
  /**
   * Parse Loop
   */
  parse(t, e = !0) {
    let n = "";
    for (let r = 0; r < t.length; r++) {
      const a = t[r];
      if (this.options.extensions && this.options.extensions.renderers && this.options.extensions.renderers[a.type]) {
        const s = a, u = this.options.extensions.renderers[s.type].call({ parser: this }, s);
        if (u !== !1 || !["space", "hr", "heading", "code", "table", "blockquote", "list", "html", "paragraph", "text"].includes(s.type)) {
          n += u || "";
          continue;
        }
      }
      switch (a.type) {
        case "space":
          continue;
        case "hr": {
          n += this.renderer.hr();
          continue;
        }
        case "heading": {
          const s = a;
          n += this.renderer.heading(this.parseInline(s.tokens), s.depth, Pt(this.parseInline(s.tokens, this.textRenderer)));
          continue;
        }
        case "code": {
          const s = a;
          n += this.renderer.code(s.text, s.lang, !!s.escaped);
          continue;
        }
        case "table": {
          const s = a;
          let u = "", l = "";
          for (let D = 0; D < s.header.length; D++)
            l += this.renderer.tablecell(this.parseInline(s.header[D].tokens), { header: !0, align: s.align[D] });
          u += this.renderer.tablerow(l);
          let m = "";
          for (let D = 0; D < s.rows.length; D++) {
            const k = s.rows[D];
            l = "";
            for (let b = 0; b < k.length; b++)
              l += this.renderer.tablecell(this.parseInline(k[b].tokens), { header: !1, align: s.align[b] });
            m += this.renderer.tablerow(l);
          }
          n += this.renderer.table(u, m);
          continue;
        }
        case "blockquote": {
          const s = a, u = this.parse(s.tokens);
          n += this.renderer.blockquote(u);
          continue;
        }
        case "list": {
          const s = a, u = s.ordered, l = s.start, m = s.loose;
          let D = "";
          for (let k = 0; k < s.items.length; k++) {
            const b = s.items[k], F = b.checked, B = b.task;
            let w = "";
            if (b.task) {
              const x = this.renderer.checkbox(!!F);
              m ? b.tokens.length > 0 && b.tokens[0].type === "paragraph" ? (b.tokens[0].text = x + " " + b.tokens[0].text, b.tokens[0].tokens && b.tokens[0].tokens.length > 0 && b.tokens[0].tokens[0].type === "text" && (b.tokens[0].tokens[0].text = x + " " + b.tokens[0].tokens[0].text)) : b.tokens.unshift({
                type: "text",
                text: x + " "
              }) : w += x + " ";
            }
            w += this.parse(b.tokens, m), D += this.renderer.listitem(w, B, !!F);
          }
          n += this.renderer.list(D, u, l);
          continue;
        }
        case "html": {
          const s = a;
          n += this.renderer.html(s.text, s.block);
          continue;
        }
        case "paragraph": {
          const s = a;
          n += this.renderer.paragraph(this.parseInline(s.tokens));
          continue;
        }
        case "text": {
          let s = a, u = s.tokens ? this.parseInline(s.tokens) : s.text;
          for (; r + 1 < t.length && t[r + 1].type === "text"; )
            s = t[++r], u += `
` + (s.tokens ? this.parseInline(s.tokens) : s.text);
          n += e ? this.renderer.paragraph(u) : u;
          continue;
        }
        default: {
          const s = 'Token with "' + a.type + '" type was not found.';
          if (this.options.silent)
            return console.error(s), "";
          throw new Error(s);
        }
      }
    }
    return n;
  }
  /**
   * Parse Inline Tokens
   */
  parseInline(t, e) {
    e = e || this.renderer;
    let n = "";
    for (let r = 0; r < t.length; r++) {
      const a = t[r];
      if (this.options.extensions && this.options.extensions.renderers && this.options.extensions.renderers[a.type]) {
        const s = this.options.extensions.renderers[a.type].call({ parser: this }, a);
        if (s !== !1 || !["escape", "html", "link", "image", "strong", "em", "codespan", "br", "del", "text"].includes(a.type)) {
          n += s || "";
          continue;
        }
      }
      switch (a.type) {
        case "escape": {
          const s = a;
          n += e.text(s.text);
          break;
        }
        case "html": {
          const s = a;
          n += e.html(s.text);
          break;
        }
        case "link": {
          const s = a;
          n += e.link(s.href, s.title, this.parseInline(s.tokens, e));
          break;
        }
        case "image": {
          const s = a;
          n += e.image(s.href, s.title, s.text);
          break;
        }
        case "strong": {
          const s = a;
          n += e.strong(this.parseInline(s.tokens, e));
          break;
        }
        case "em": {
          const s = a;
          n += e.em(this.parseInline(s.tokens, e));
          break;
        }
        case "codespan": {
          const s = a;
          n += e.codespan(s.text);
          break;
        }
        case "br": {
          n += e.br();
          break;
        }
        case "del": {
          const s = a;
          n += e.del(this.parseInline(s.tokens, e));
          break;
        }
        case "text": {
          const s = a;
          n += e.text(s.text);
          break;
        }
        default: {
          const s = 'Token with "' + a.type + '" type was not found.';
          if (this.options.silent)
            return console.error(s), "";
          throw new Error(s);
        }
      }
    }
    return n;
  }
}
class te {
  constructor(t) {
    S(this, "options");
    this.options = t || j;
  }
  /**
   * Process markdown before marked
   */
  preprocess(t) {
    return t;
  }
  /**
   * Process HTML after marked is finished
   */
  postprocess(t) {
    return t;
  }
  /**
   * Process all tokens before walk tokens
   */
  processAllTokens(t) {
    return t;
  }
}
S(te, "passThroughHooks", /* @__PURE__ */ new Set([
  "preprocess",
  "postprocess",
  "processAllTokens"
]));
var U, ye, ft;
class dt {
  constructor(...t) {
    Me(this, U);
    S(this, "defaults", ve());
    S(this, "options", this.setOptions);
    S(this, "parse", le(this, U, ye).call(this, O.lex, M.parse));
    S(this, "parseInline", le(this, U, ye).call(this, O.lexInline, M.parseInline));
    S(this, "Parser", M);
    S(this, "Renderer", me);
    S(this, "TextRenderer", Ie);
    S(this, "Lexer", O);
    S(this, "Tokenizer", fe);
    S(this, "Hooks", te);
    this.use(...t);
  }
  /**
   * Run callback for every token
   */
  walkTokens(t, e) {
    var r, a;
    let n = [];
    for (const s of t)
      switch (n = n.concat(e.call(this, s)), s.type) {
        case "table": {
          const u = s;
          for (const l of u.header)
            n = n.concat(this.walkTokens(l.tokens, e));
          for (const l of u.rows)
            for (const m of l)
              n = n.concat(this.walkTokens(m.tokens, e));
          break;
        }
        case "list": {
          const u = s;
          n = n.concat(this.walkTokens(u.items, e));
          break;
        }
        default: {
          const u = s;
          (a = (r = this.defaults.extensions) == null ? void 0 : r.childTokens) != null && a[u.type] ? this.defaults.extensions.childTokens[u.type].forEach((l) => {
            const m = u[l].flat(1 / 0);
            n = n.concat(this.walkTokens(m, e));
          }) : u.tokens && (n = n.concat(this.walkTokens(u.tokens, e)));
        }
      }
    return n;
  }
  use(...t) {
    const e = this.defaults.extensions || { renderers: {}, childTokens: {} };
    return t.forEach((n) => {
      const r = { ...n };
      if (r.async = this.defaults.async || r.async || !1, n.extensions && (n.extensions.forEach((a) => {
        if (!a.name)
          throw new Error("extension name required");
        if ("renderer" in a) {
          const s = e.renderers[a.name];
          s ? e.renderers[a.name] = function(...u) {
            let l = a.renderer.apply(this, u);
            return l === !1 && (l = s.apply(this, u)), l;
          } : e.renderers[a.name] = a.renderer;
        }
        if ("tokenizer" in a) {
          if (!a.level || a.level !== "block" && a.level !== "inline")
            throw new Error("extension level must be 'block' or 'inline'");
          const s = e[a.level];
          s ? s.unshift(a.tokenizer) : e[a.level] = [a.tokenizer], a.start && (a.level === "block" ? e.startBlock ? e.startBlock.push(a.start) : e.startBlock = [a.start] : a.level === "inline" && (e.startInline ? e.startInline.push(a.start) : e.startInline = [a.start]));
        }
        "childTokens" in a && a.childTokens && (e.childTokens[a.name] = a.childTokens);
      }), r.extensions = e), n.renderer) {
        const a = this.defaults.renderer || new me(this.defaults);
        for (const s in n.renderer) {
          if (!(s in a))
            throw new Error(`renderer '${s}' does not exist`);
          if (s === "options")
            continue;
          const u = s, l = n.renderer[u], m = a[u];
          a[u] = (...D) => {
            let k = l.apply(a, D);
            return k === !1 && (k = m.apply(a, D)), k || "";
          };
        }
        r.renderer = a;
      }
      if (n.tokenizer) {
        const a = this.defaults.tokenizer || new fe(this.defaults);
        for (const s in n.tokenizer) {
          if (!(s in a))
            throw new Error(`tokenizer '${s}' does not exist`);
          if (["options", "rules", "lexer"].includes(s))
            continue;
          const u = s, l = n.tokenizer[u], m = a[u];
          a[u] = (...D) => {
            let k = l.apply(a, D);
            return k === !1 && (k = m.apply(a, D)), k;
          };
        }
        r.tokenizer = a;
      }
      if (n.hooks) {
        const a = this.defaults.hooks || new te();
        for (const s in n.hooks) {
          if (!(s in a))
            throw new Error(`hook '${s}' does not exist`);
          if (s === "options")
            continue;
          const u = s, l = n.hooks[u], m = a[u];
          te.passThroughHooks.has(s) ? a[u] = (D) => {
            if (this.defaults.async)
              return Promise.resolve(l.call(a, D)).then((b) => m.call(a, b));
            const k = l.call(a, D);
            return m.call(a, k);
          } : a[u] = (...D) => {
            let k = l.apply(a, D);
            return k === !1 && (k = m.apply(a, D)), k;
          };
        }
        r.hooks = a;
      }
      if (n.walkTokens) {
        const a = this.defaults.walkTokens, s = n.walkTokens;
        r.walkTokens = function(u) {
          let l = [];
          return l.push(s.call(this, u)), a && (l = l.concat(a.call(this, u))), l;
        };
      }
      this.defaults = { ...this.defaults, ...r };
    }), this;
  }
  setOptions(t) {
    return this.defaults = { ...this.defaults, ...t }, this;
  }
  lexer(t, e) {
    return O.lex(t, e ?? this.defaults);
  }
  parser(t, e) {
    return M.parse(t, e ?? this.defaults);
  }
}
U = new WeakSet(), ye = function(t, e) {
  return (n, r) => {
    const a = { ...r }, s = { ...this.defaults, ...a };
    this.defaults.async === !0 && a.async === !1 && (s.silent || console.warn("marked(): The async option was set to true by an extension. The async: false option sent to parse will be ignored."), s.async = !0);
    const u = le(this, U, ft).call(this, !!s.silent, !!s.async);
    if (typeof n > "u" || n === null)
      return u(new Error("marked(): input parameter is undefined or null"));
    if (typeof n != "string")
      return u(new Error("marked(): input parameter is of type " + Object.prototype.toString.call(n) + ", string expected"));
    if (s.hooks && (s.hooks.options = s), s.async)
      return Promise.resolve(s.hooks ? s.hooks.preprocess(n) : n).then((l) => t(l, s)).then((l) => s.hooks ? s.hooks.processAllTokens(l) : l).then((l) => s.walkTokens ? Promise.all(this.walkTokens(l, s.walkTokens)).then(() => l) : l).then((l) => e(l, s)).then((l) => s.hooks ? s.hooks.postprocess(l) : l).catch(u);
    try {
      s.hooks && (n = s.hooks.preprocess(n));
      let l = t(n, s);
      s.hooks && (l = s.hooks.processAllTokens(l)), s.walkTokens && this.walkTokens(l, s.walkTokens);
      let m = e(l, s);
      return s.hooks && (m = s.hooks.postprocess(m)), m;
    } catch (l) {
      return u(l);
    }
  };
}, ft = function(t, e) {
  return (n) => {
    if (n.message += `
Please report this to https://github.com/markedjs/marked.`, t) {
      const r = "<p>An error occurred:</p><pre>" + L(n.message + "", !0) + "</pre>";
      return e ? Promise.resolve(r) : r;
    }
    if (e)
      return Promise.reject(n);
    throw n;
  };
};
const G = new dt();
function y(i, t) {
  return G.parse(i, t);
}
y.options = y.setOptions = function(i) {
  return G.setOptions(i), y.defaults = G.defaults, it(y.defaults), y;
};
y.getDefaults = ve;
y.defaults = j;
y.use = function(...i) {
  return G.use(...i), y.defaults = G.defaults, it(y.defaults), y;
};
y.walkTokens = function(i, t) {
  return G.walkTokens(i, t);
};
y.parseInline = G.parseInline;
y.Parser = M;
y.parser = M.parse;
y.Renderer = me;
y.TextRenderer = Ie;
y.Lexer = O;
y.lexer = O.lex;
y.Tokenizer = fe;
y.Hooks = te;
y.parse = y;
y.options;
y.setOptions;
y.use;
y.walkTokens;
y.parseInline;
M.parse;
O.lex;
function Dn(i) {
  if (typeof i == "function" && (i = {
    highlight: i
  }), !i || typeof i.highlight != "function")
    throw new Error("Must provide highlight function");
  return typeof i.langPrefix != "string" && (i.langPrefix = "language-"), typeof i.emptyLangClass != "string" && (i.emptyLangClass = ""), {
    async: !!i.async,
    walkTokens(t) {
      if (t.type !== "code")
        return;
      const e = Ue(t.lang);
      if (i.async)
        return Promise.resolve(i.highlight(t.text, e, t.lang || "")).then(je(t));
      const n = i.highlight(t.text, e, t.lang || "");
      if (n instanceof Promise)
        throw new Error("markedHighlight is not set to async but the highlight function is async. Set the async option to true on markedHighlight to await the async highlight function.");
      je(t)(n);
    },
    useNewRenderer: !0,
    renderer: {
      code(t, e, n) {
        typeof t == "object" && (n = t.escaped, e = t.lang, t = t.text);
        const r = Ue(e), a = r ? i.langPrefix + Xe(r) : i.emptyLangClass, s = a ? ` class="${a}"` : "";
        return t = t.replace(/\n$/, ""), `<pre><code${s}>${n ? t : Xe(t, !0)}
</code></pre>`;
      }
    }
  };
}
function Ue(i) {
  return (i || "").match(/\S*/)[0];
}
function je(i) {
  return (t) => {
    typeof t == "string" && t !== i.text && (i.escaped = !0, i.text = t);
  };
}
const Dt = /[&<>"']/, mn = new RegExp(Dt.source, "g"), mt = /[<>"']|&(?!(#\d{1,7}|#[Xx][a-fA-F0-9]{1,6}|\w+);)/, Fn = new RegExp(mt.source, "g"), bn = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;"
}, Ze = (i) => bn[i];
function Xe(i, t) {
  if (t) {
    if (Dt.test(i))
      return i.replace(mn, Ze);
  } else if (mt.test(i))
    return i.replace(Fn, Ze);
  return i;
}
const kn = /[\0-\x1F!-,\.\/:-@\[-\^`\{-\xA9\xAB-\xB4\xB6-\xB9\xBB-\xBF\xD7\xF7\u02C2-\u02C5\u02D2-\u02DF\u02E5-\u02EB\u02ED\u02EF-\u02FF\u0375\u0378\u0379\u037E\u0380-\u0385\u0387\u038B\u038D\u03A2\u03F6\u0482\u0530\u0557\u0558\u055A-\u055F\u0589-\u0590\u05BE\u05C0\u05C3\u05C6\u05C8-\u05CF\u05EB-\u05EE\u05F3-\u060F\u061B-\u061F\u066A-\u066D\u06D4\u06DD\u06DE\u06E9\u06FD\u06FE\u0700-\u070F\u074B\u074C\u07B2-\u07BF\u07F6-\u07F9\u07FB\u07FC\u07FE\u07FF\u082E-\u083F\u085C-\u085F\u086B-\u089F\u08B5\u08C8-\u08D2\u08E2\u0964\u0965\u0970\u0984\u098D\u098E\u0991\u0992\u09A9\u09B1\u09B3-\u09B5\u09BA\u09BB\u09C5\u09C6\u09C9\u09CA\u09CF-\u09D6\u09D8-\u09DB\u09DE\u09E4\u09E5\u09F2-\u09FB\u09FD\u09FF\u0A00\u0A04\u0A0B-\u0A0E\u0A11\u0A12\u0A29\u0A31\u0A34\u0A37\u0A3A\u0A3B\u0A3D\u0A43-\u0A46\u0A49\u0A4A\u0A4E-\u0A50\u0A52-\u0A58\u0A5D\u0A5F-\u0A65\u0A76-\u0A80\u0A84\u0A8E\u0A92\u0AA9\u0AB1\u0AB4\u0ABA\u0ABB\u0AC6\u0ACA\u0ACE\u0ACF\u0AD1-\u0ADF\u0AE4\u0AE5\u0AF0-\u0AF8\u0B00\u0B04\u0B0D\u0B0E\u0B11\u0B12\u0B29\u0B31\u0B34\u0B3A\u0B3B\u0B45\u0B46\u0B49\u0B4A\u0B4E-\u0B54\u0B58-\u0B5B\u0B5E\u0B64\u0B65\u0B70\u0B72-\u0B81\u0B84\u0B8B-\u0B8D\u0B91\u0B96-\u0B98\u0B9B\u0B9D\u0BA0-\u0BA2\u0BA5-\u0BA7\u0BAB-\u0BAD\u0BBA-\u0BBD\u0BC3-\u0BC5\u0BC9\u0BCE\u0BCF\u0BD1-\u0BD6\u0BD8-\u0BE5\u0BF0-\u0BFF\u0C0D\u0C11\u0C29\u0C3A-\u0C3C\u0C45\u0C49\u0C4E-\u0C54\u0C57\u0C5B-\u0C5F\u0C64\u0C65\u0C70-\u0C7F\u0C84\u0C8D\u0C91\u0CA9\u0CB4\u0CBA\u0CBB\u0CC5\u0CC9\u0CCE-\u0CD4\u0CD7-\u0CDD\u0CDF\u0CE4\u0CE5\u0CF0\u0CF3-\u0CFF\u0D0D\u0D11\u0D45\u0D49\u0D4F-\u0D53\u0D58-\u0D5E\u0D64\u0D65\u0D70-\u0D79\u0D80\u0D84\u0D97-\u0D99\u0DB2\u0DBC\u0DBE\u0DBF\u0DC7-\u0DC9\u0DCB-\u0DCE\u0DD5\u0DD7\u0DE0-\u0DE5\u0DF0\u0DF1\u0DF4-\u0E00\u0E3B-\u0E3F\u0E4F\u0E5A-\u0E80\u0E83\u0E85\u0E8B\u0EA4\u0EA6\u0EBE\u0EBF\u0EC5\u0EC7\u0ECE\u0ECF\u0EDA\u0EDB\u0EE0-\u0EFF\u0F01-\u0F17\u0F1A-\u0F1F\u0F2A-\u0F34\u0F36\u0F38\u0F3A-\u0F3D\u0F48\u0F6D-\u0F70\u0F85\u0F98\u0FBD-\u0FC5\u0FC7-\u0FFF\u104A-\u104F\u109E\u109F\u10C6\u10C8-\u10CC\u10CE\u10CF\u10FB\u1249\u124E\u124F\u1257\u1259\u125E\u125F\u1289\u128E\u128F\u12B1\u12B6\u12B7\u12BF\u12C1\u12C6\u12C7\u12D7\u1311\u1316\u1317\u135B\u135C\u1360-\u137F\u1390-\u139F\u13F6\u13F7\u13FE-\u1400\u166D\u166E\u1680\u169B-\u169F\u16EB-\u16ED\u16F9-\u16FF\u170D\u1715-\u171F\u1735-\u173F\u1754-\u175F\u176D\u1771\u1774-\u177F\u17D4-\u17D6\u17D8-\u17DB\u17DE\u17DF\u17EA-\u180A\u180E\u180F\u181A-\u181F\u1879-\u187F\u18AB-\u18AF\u18F6-\u18FF\u191F\u192C-\u192F\u193C-\u1945\u196E\u196F\u1975-\u197F\u19AC-\u19AF\u19CA-\u19CF\u19DA-\u19FF\u1A1C-\u1A1F\u1A5F\u1A7D\u1A7E\u1A8A-\u1A8F\u1A9A-\u1AA6\u1AA8-\u1AAF\u1AC1-\u1AFF\u1B4C-\u1B4F\u1B5A-\u1B6A\u1B74-\u1B7F\u1BF4-\u1BFF\u1C38-\u1C3F\u1C4A-\u1C4C\u1C7E\u1C7F\u1C89-\u1C8F\u1CBB\u1CBC\u1CC0-\u1CCF\u1CD3\u1CFB-\u1CFF\u1DFA\u1F16\u1F17\u1F1E\u1F1F\u1F46\u1F47\u1F4E\u1F4F\u1F58\u1F5A\u1F5C\u1F5E\u1F7E\u1F7F\u1FB5\u1FBD\u1FBF-\u1FC1\u1FC5\u1FCD-\u1FCF\u1FD4\u1FD5\u1FDC-\u1FDF\u1FED-\u1FF1\u1FF5\u1FFD-\u203E\u2041-\u2053\u2055-\u2070\u2072-\u207E\u2080-\u208F\u209D-\u20CF\u20F1-\u2101\u2103-\u2106\u2108\u2109\u2114\u2116-\u2118\u211E-\u2123\u2125\u2127\u2129\u212E\u213A\u213B\u2140-\u2144\u214A-\u214D\u214F-\u215F\u2189-\u24B5\u24EA-\u2BFF\u2C2F\u2C5F\u2CE5-\u2CEA\u2CF4-\u2CFF\u2D26\u2D28-\u2D2C\u2D2E\u2D2F\u2D68-\u2D6E\u2D70-\u2D7E\u2D97-\u2D9F\u2DA7\u2DAF\u2DB7\u2DBF\u2DC7\u2DCF\u2DD7\u2DDF\u2E00-\u2E2E\u2E30-\u3004\u3008-\u3020\u3030\u3036\u3037\u303D-\u3040\u3097\u3098\u309B\u309C\u30A0\u30FB\u3100-\u3104\u3130\u318F-\u319F\u31C0-\u31EF\u3200-\u33FF\u4DC0-\u4DFF\u9FFD-\u9FFF\uA48D-\uA4CF\uA4FE\uA4FF\uA60D-\uA60F\uA62C-\uA63F\uA673\uA67E\uA6F2-\uA716\uA720\uA721\uA789\uA78A\uA7C0\uA7C1\uA7CB-\uA7F4\uA828-\uA82B\uA82D-\uA83F\uA874-\uA87F\uA8C6-\uA8CF\uA8DA-\uA8DF\uA8F8-\uA8FA\uA8FC\uA92E\uA92F\uA954-\uA95F\uA97D-\uA97F\uA9C1-\uA9CE\uA9DA-\uA9DF\uA9FF\uAA37-\uAA3F\uAA4E\uAA4F\uAA5A-\uAA5F\uAA77-\uAA79\uAAC3-\uAADA\uAADE\uAADF\uAAF0\uAAF1\uAAF7-\uAB00\uAB07\uAB08\uAB0F\uAB10\uAB17-\uAB1F\uAB27\uAB2F\uAB5B\uAB6A-\uAB6F\uABEB\uABEE\uABEF\uABFA-\uABFF\uD7A4-\uD7AF\uD7C7-\uD7CA\uD7FC-\uD7FF\uE000-\uF8FF\uFA6E\uFA6F\uFADA-\uFAFF\uFB07-\uFB12\uFB18-\uFB1C\uFB29\uFB37\uFB3D\uFB3F\uFB42\uFB45\uFBB2-\uFBD2\uFD3E-\uFD4F\uFD90\uFD91\uFDC8-\uFDEF\uFDFC-\uFDFF\uFE10-\uFE1F\uFE30-\uFE32\uFE35-\uFE4C\uFE50-\uFE6F\uFE75\uFEFD-\uFF0F\uFF1A-\uFF20\uFF3B-\uFF3E\uFF40\uFF5B-\uFF65\uFFBF-\uFFC1\uFFC8\uFFC9\uFFD0\uFFD1\uFFD8\uFFD9\uFFDD-\uFFFF]|\uD800[\uDC0C\uDC27\uDC3B\uDC3E\uDC4E\uDC4F\uDC5E-\uDC7F\uDCFB-\uDD3F\uDD75-\uDDFC\uDDFE-\uDE7F\uDE9D-\uDE9F\uDED1-\uDEDF\uDEE1-\uDEFF\uDF20-\uDF2C\uDF4B-\uDF4F\uDF7B-\uDF7F\uDF9E\uDF9F\uDFC4-\uDFC7\uDFD0\uDFD6-\uDFFF]|\uD801[\uDC9E\uDC9F\uDCAA-\uDCAF\uDCD4-\uDCD7\uDCFC-\uDCFF\uDD28-\uDD2F\uDD64-\uDDFF\uDF37-\uDF3F\uDF56-\uDF5F\uDF68-\uDFFF]|\uD802[\uDC06\uDC07\uDC09\uDC36\uDC39-\uDC3B\uDC3D\uDC3E\uDC56-\uDC5F\uDC77-\uDC7F\uDC9F-\uDCDF\uDCF3\uDCF6-\uDCFF\uDD16-\uDD1F\uDD3A-\uDD7F\uDDB8-\uDDBD\uDDC0-\uDDFF\uDE04\uDE07-\uDE0B\uDE14\uDE18\uDE36\uDE37\uDE3B-\uDE3E\uDE40-\uDE5F\uDE7D-\uDE7F\uDE9D-\uDEBF\uDEC8\uDEE7-\uDEFF\uDF36-\uDF3F\uDF56-\uDF5F\uDF73-\uDF7F\uDF92-\uDFFF]|\uD803[\uDC49-\uDC7F\uDCB3-\uDCBF\uDCF3-\uDCFF\uDD28-\uDD2F\uDD3A-\uDE7F\uDEAA\uDEAD-\uDEAF\uDEB2-\uDEFF\uDF1D-\uDF26\uDF28-\uDF2F\uDF51-\uDFAF\uDFC5-\uDFDF\uDFF7-\uDFFF]|\uD804[\uDC47-\uDC65\uDC70-\uDC7E\uDCBB-\uDCCF\uDCE9-\uDCEF\uDCFA-\uDCFF\uDD35\uDD40-\uDD43\uDD48-\uDD4F\uDD74\uDD75\uDD77-\uDD7F\uDDC5-\uDDC8\uDDCD\uDDDB\uDDDD-\uDDFF\uDE12\uDE38-\uDE3D\uDE3F-\uDE7F\uDE87\uDE89\uDE8E\uDE9E\uDEA9-\uDEAF\uDEEB-\uDEEF\uDEFA-\uDEFF\uDF04\uDF0D\uDF0E\uDF11\uDF12\uDF29\uDF31\uDF34\uDF3A\uDF45\uDF46\uDF49\uDF4A\uDF4E\uDF4F\uDF51-\uDF56\uDF58-\uDF5C\uDF64\uDF65\uDF6D-\uDF6F\uDF75-\uDFFF]|\uD805[\uDC4B-\uDC4F\uDC5A-\uDC5D\uDC62-\uDC7F\uDCC6\uDCC8-\uDCCF\uDCDA-\uDD7F\uDDB6\uDDB7\uDDC1-\uDDD7\uDDDE-\uDDFF\uDE41-\uDE43\uDE45-\uDE4F\uDE5A-\uDE7F\uDEB9-\uDEBF\uDECA-\uDEFF\uDF1B\uDF1C\uDF2C-\uDF2F\uDF3A-\uDFFF]|\uD806[\uDC3B-\uDC9F\uDCEA-\uDCFE\uDD07\uDD08\uDD0A\uDD0B\uDD14\uDD17\uDD36\uDD39\uDD3A\uDD44-\uDD4F\uDD5A-\uDD9F\uDDA8\uDDA9\uDDD8\uDDD9\uDDE2\uDDE5-\uDDFF\uDE3F-\uDE46\uDE48-\uDE4F\uDE9A-\uDE9C\uDE9E-\uDEBF\uDEF9-\uDFFF]|\uD807[\uDC09\uDC37\uDC41-\uDC4F\uDC5A-\uDC71\uDC90\uDC91\uDCA8\uDCB7-\uDCFF\uDD07\uDD0A\uDD37-\uDD39\uDD3B\uDD3E\uDD48-\uDD4F\uDD5A-\uDD5F\uDD66\uDD69\uDD8F\uDD92\uDD99-\uDD9F\uDDAA-\uDEDF\uDEF7-\uDFAF\uDFB1-\uDFFF]|\uD808[\uDF9A-\uDFFF]|\uD809[\uDC6F-\uDC7F\uDD44-\uDFFF]|[\uD80A\uD80B\uD80E-\uD810\uD812-\uD819\uD824-\uD82B\uD82D\uD82E\uD830-\uD833\uD837\uD839\uD83D\uD83F\uD87B-\uD87D\uD87F\uD885-\uDB3F\uDB41-\uDBFF][\uDC00-\uDFFF]|\uD80D[\uDC2F-\uDFFF]|\uD811[\uDE47-\uDFFF]|\uD81A[\uDE39-\uDE3F\uDE5F\uDE6A-\uDECF\uDEEE\uDEEF\uDEF5-\uDEFF\uDF37-\uDF3F\uDF44-\uDF4F\uDF5A-\uDF62\uDF78-\uDF7C\uDF90-\uDFFF]|\uD81B[\uDC00-\uDE3F\uDE80-\uDEFF\uDF4B-\uDF4E\uDF88-\uDF8E\uDFA0-\uDFDF\uDFE2\uDFE5-\uDFEF\uDFF2-\uDFFF]|\uD821[\uDFF8-\uDFFF]|\uD823[\uDCD6-\uDCFF\uDD09-\uDFFF]|\uD82C[\uDD1F-\uDD4F\uDD53-\uDD63\uDD68-\uDD6F\uDEFC-\uDFFF]|\uD82F[\uDC6B-\uDC6F\uDC7D-\uDC7F\uDC89-\uDC8F\uDC9A-\uDC9C\uDC9F-\uDFFF]|\uD834[\uDC00-\uDD64\uDD6A-\uDD6C\uDD73-\uDD7A\uDD83\uDD84\uDD8C-\uDDA9\uDDAE-\uDE41\uDE45-\uDFFF]|\uD835[\uDC55\uDC9D\uDCA0\uDCA1\uDCA3\uDCA4\uDCA7\uDCA8\uDCAD\uDCBA\uDCBC\uDCC4\uDD06\uDD0B\uDD0C\uDD15\uDD1D\uDD3A\uDD3F\uDD45\uDD47-\uDD49\uDD51\uDEA6\uDEA7\uDEC1\uDEDB\uDEFB\uDF15\uDF35\uDF4F\uDF6F\uDF89\uDFA9\uDFC3\uDFCC\uDFCD]|\uD836[\uDC00-\uDDFF\uDE37-\uDE3A\uDE6D-\uDE74\uDE76-\uDE83\uDE85-\uDE9A\uDEA0\uDEB0-\uDFFF]|\uD838[\uDC07\uDC19\uDC1A\uDC22\uDC25\uDC2B-\uDCFF\uDD2D-\uDD2F\uDD3E\uDD3F\uDD4A-\uDD4D\uDD4F-\uDEBF\uDEFA-\uDFFF]|\uD83A[\uDCC5-\uDCCF\uDCD7-\uDCFF\uDD4C-\uDD4F\uDD5A-\uDFFF]|\uD83B[\uDC00-\uDDFF\uDE04\uDE20\uDE23\uDE25\uDE26\uDE28\uDE33\uDE38\uDE3A\uDE3C-\uDE41\uDE43-\uDE46\uDE48\uDE4A\uDE4C\uDE50\uDE53\uDE55\uDE56\uDE58\uDE5A\uDE5C\uDE5E\uDE60\uDE63\uDE65\uDE66\uDE6B\uDE73\uDE78\uDE7D\uDE7F\uDE8A\uDE9C-\uDEA0\uDEA4\uDEAA\uDEBC-\uDFFF]|\uD83C[\uDC00-\uDD2F\uDD4A-\uDD4F\uDD6A-\uDD6F\uDD8A-\uDFFF]|\uD83E[\uDC00-\uDFEF\uDFFA-\uDFFF]|\uD869[\uDEDE-\uDEFF]|\uD86D[\uDF35-\uDF3F]|\uD86E[\uDC1E\uDC1F]|\uD873[\uDEA2-\uDEAF]|\uD87A[\uDFE1-\uDFFF]|\uD87E[\uDE1E-\uDFFF]|\uD884[\uDF4B-\uDFFF]|\uDB40[\uDC00-\uDCFF\uDDF0-\uDFFF]/g, En = Object.hasOwnProperty;
class $e {
  /**
   * Create a new slug class.
   */
  constructor() {
    this.occurrences, this.reset();
  }
  /**
   * Generate a unique slug.
  *
  * Tracks previously generated slugs: repeated calls with the same value
  * will result in different slugs.
  * Use the `slug` function to get same slugs.
   *
   * @param  {string} value
   *   String of text to slugify
   * @param  {boolean} [maintainCase=false]
   *   Keep the current case, otherwise make all lowercase
   * @return {string}
   *   A unique slug string
   */
  slug(t, e) {
    const n = this;
    let r = An(t, e === !0);
    const a = r;
    for (; En.call(n.occurrences, r); )
      n.occurrences[a]++, r = a + "-" + n.occurrences[a];
    return n.occurrences[r] = 0, r;
  }
  /**
   * Reset - Forget all previous slugs
   *
   * @return void
   */
  reset() {
    this.occurrences = /* @__PURE__ */ Object.create(null);
  }
}
function An(i, t) {
  return typeof i != "string" ? "" : (t || (i = i.toLowerCase()), i.replace(kn, "").replace(/ /g, "-"));
}
let Ft = new $e(), bt = [];
function wn({ prefix: i = "", globalSlugs: t = !1 } = {}) {
  return {
    headerIds: !1,
    // prevent deprecation warning; remove this once headerIds option is removed
    hooks: {
      preprocess(e) {
        return t || xn(), e;
      }
    },
    renderer: {
      heading(e, n, r) {
        r = r.toLowerCase().trim().replace(/<[!\/a-z].*?>/gi, "");
        const a = `${i}${Ft.slug(r)}`, s = { level: n, text: e, id: a };
        return bt.push(s), `<h${n} id="${a}">${e}</h${n}>
`;
      }
    }
  };
}
function xn() {
  bt = [], Ft = new $e();
}
var We = typeof globalThis < "u" ? globalThis : typeof window < "u" ? window : typeof global < "u" ? global : typeof self < "u" ? self : {};
function Hr(i) {
  return i && i.__esModule && Object.prototype.hasOwnProperty.call(i, "default") ? i.default : i;
}
var kt = { exports: {} };
(function(i) {
  var t = typeof window < "u" ? window : typeof WorkerGlobalScope < "u" && self instanceof WorkerGlobalScope ? self : {};
  /**
   * Prism: Lightweight, robust, elegant syntax highlighting
   *
   * @license MIT <https://opensource.org/licenses/MIT>
   * @author Lea Verou <https://lea.verou.me>
   * @namespace
   * @public
   */
  var e = function(n) {
    var r = /(?:^|\s)lang(?:uage)?-([\w-]+)(?=\s|$)/i, a = 0, s = {}, u = {
      /**
       * By default, Prism will attempt to highlight all code elements (by calling {@link Prism.highlightAll}) on the
       * current page after the page finished loading. This might be a problem if e.g. you wanted to asynchronously load
       * additional languages or plugins yourself.
       *
       * By setting this value to `true`, Prism will not automatically highlight all code elements on the page.
       *
       * You obviously have to change this value before the automatic highlighting started. To do this, you can add an
       * empty Prism object into the global scope before loading the Prism script like this:
       *
       * ```js
       * window.Prism = window.Prism || {};
       * Prism.manual = true;
       * // add a new <script> to load Prism's script
       * ```
       *
       * @default false
       * @type {boolean}
       * @memberof Prism
       * @public
       */
      manual: n.Prism && n.Prism.manual,
      /**
       * By default, if Prism is in a web worker, it assumes that it is in a worker it created itself, so it uses
       * `addEventListener` to communicate with its parent instance. However, if you're using Prism manually in your
       * own worker, you don't want it to do this.
       *
       * By setting this value to `true`, Prism will not add its own listeners to the worker.
       *
       * You obviously have to change this value before Prism executes. To do this, you can add an
       * empty Prism object into the global scope before loading the Prism script like this:
       *
       * ```js
       * window.Prism = window.Prism || {};
       * Prism.disableWorkerMessageHandler = true;
       * // Load Prism's script
       * ```
       *
       * @default false
       * @type {boolean}
       * @memberof Prism
       * @public
       */
      disableWorkerMessageHandler: n.Prism && n.Prism.disableWorkerMessageHandler,
      /**
       * A namespace for utility methods.
       *
       * All function in this namespace that are not explicitly marked as _public_ are for __internal use only__ and may
       * change or disappear at any time.
       *
       * @namespace
       * @memberof Prism
       */
      util: {
        encode: function c(o) {
          return o instanceof l ? new l(o.type, c(o.content), o.alias) : Array.isArray(o) ? o.map(c) : o.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/\u00a0/g, " ");
        },
        /**
         * Returns the name of the type of the given value.
         *
         * @param {any} o
         * @returns {string}
         * @example
         * type(null)      === 'Null'
         * type(undefined) === 'Undefined'
         * type(123)       === 'Number'
         * type('foo')     === 'String'
         * type(true)      === 'Boolean'
         * type([1, 2])    === 'Array'
         * type({})        === 'Object'
         * type(String)    === 'Function'
         * type(/abc+/)    === 'RegExp'
         */
        type: function(c) {
          return Object.prototype.toString.call(c).slice(8, -1);
        },
        /**
         * Returns a unique number for the given object. Later calls will still return the same number.
         *
         * @param {Object} obj
         * @returns {number}
         */
        objId: function(c) {
          return c.__id || Object.defineProperty(c, "__id", { value: ++a }), c.__id;
        },
        /**
         * Creates a deep clone of the given object.
         *
         * The main intended use of this function is to clone language definitions.
         *
         * @param {T} o
         * @param {Record<number, any>} [visited]
         * @returns {T}
         * @template T
         */
        clone: function c(o, h) {
          h = h || {};
          var g, p;
          switch (u.util.type(o)) {
            case "Object":
              if (p = u.util.objId(o), h[p])
                return h[p];
              g = /** @type {Record<string, any>} */
              {}, h[p] = g;
              for (var d in o)
                o.hasOwnProperty(d) && (g[d] = c(o[d], h));
              return (
                /** @type {any} */
                g
              );
            case "Array":
              return p = u.util.objId(o), h[p] ? h[p] : (g = [], h[p] = g, /** @type {Array} */
              /** @type {any} */
              o.forEach(function(E, f) {
                g[f] = c(E, h);
              }), /** @type {any} */
              g);
            default:
              return o;
          }
        },
        /**
         * Returns the Prism language of the given element set by a `language-xxxx` or `lang-xxxx` class.
         *
         * If no language is set for the element or the element is `null` or `undefined`, `none` will be returned.
         *
         * @param {Element} element
         * @returns {string}
         */
        getLanguage: function(c) {
          for (; c; ) {
            var o = r.exec(c.className);
            if (o)
              return o[1].toLowerCase();
            c = c.parentElement;
          }
          return "none";
        },
        /**
         * Sets the Prism `language-xxxx` class of the given element.
         *
         * @param {Element} element
         * @param {string} language
         * @returns {void}
         */
        setLanguage: function(c, o) {
          c.className = c.className.replace(RegExp(r, "gi"), ""), c.classList.add("language-" + o);
        },
        /**
         * Returns the script element that is currently executing.
         *
         * This does __not__ work for line script element.
         *
         * @returns {HTMLScriptElement | null}
         */
        currentScript: function() {
          if (typeof document > "u")
            return null;
          if ("currentScript" in document)
            return (
              /** @type {any} */
              document.currentScript
            );
          try {
            throw new Error();
          } catch (g) {
            var c = (/at [^(\r\n]*\((.*):[^:]+:[^:]+\)$/i.exec(g.stack) || [])[1];
            if (c) {
              var o = document.getElementsByTagName("script");
              for (var h in o)
                if (o[h].src == c)
                  return o[h];
            }
            return null;
          }
        },
        /**
         * Returns whether a given class is active for `element`.
         *
         * The class can be activated if `element` or one of its ancestors has the given class and it can be deactivated
         * if `element` or one of its ancestors has the negated version of the given class. The _negated version_ of the
         * given class is just the given class with a `no-` prefix.
         *
         * Whether the class is active is determined by the closest ancestor of `element` (where `element` itself is
         * closest ancestor) that has the given class or the negated version of it. If neither `element` nor any of its
         * ancestors have the given class or the negated version of it, then the default activation will be returned.
         *
         * In the paradoxical situation where the closest ancestor contains __both__ the given class and the negated
         * version of it, the class is considered active.
         *
         * @param {Element} element
         * @param {string} className
         * @param {boolean} [defaultActivation=false]
         * @returns {boolean}
         */
        isActive: function(c, o, h) {
          for (var g = "no-" + o; c; ) {
            var p = c.classList;
            if (p.contains(o))
              return !0;
            if (p.contains(g))
              return !1;
            c = c.parentElement;
          }
          return !!h;
        }
      },
      /**
       * This namespace contains all currently loaded languages and the some helper functions to create and modify languages.
       *
       * @namespace
       * @memberof Prism
       * @public
       */
      languages: {
        /**
         * The grammar for plain, unformatted text.
         */
        plain: s,
        plaintext: s,
        text: s,
        txt: s,
        /**
         * Creates a deep copy of the language with the given id and appends the given tokens.
         *
         * If a token in `redef` also appears in the copied language, then the existing token in the copied language
         * will be overwritten at its original position.
         *
         * ## Best practices
         *
         * Since the position of overwriting tokens (token in `redef` that overwrite tokens in the copied language)
         * doesn't matter, they can technically be in any order. However, this can be confusing to others that trying to
         * understand the language definition because, normally, the order of tokens matters in Prism grammars.
         *
         * Therefore, it is encouraged to order overwriting tokens according to the positions of the overwritten tokens.
         * Furthermore, all non-overwriting tokens should be placed after the overwriting ones.
         *
         * @param {string} id The id of the language to extend. This has to be a key in `Prism.languages`.
         * @param {Grammar} redef The new tokens to append.
         * @returns {Grammar} The new language created.
         * @public
         * @example
         * Prism.languages['css-with-colors'] = Prism.languages.extend('css', {
         *     // Prism.languages.css already has a 'comment' token, so this token will overwrite CSS' 'comment' token
         *     // at its original position
         *     'comment': { ... },
         *     // CSS doesn't have a 'color' token, so this token will be appended
         *     'color': /\b(?:red|green|blue)\b/
         * });
         */
        extend: function(c, o) {
          var h = u.util.clone(u.languages[c]);
          for (var g in o)
            h[g] = o[g];
          return h;
        },
        /**
         * Inserts tokens _before_ another token in a language definition or any other grammar.
         *
         * ## Usage
         *
         * This helper method makes it easy to modify existing languages. For example, the CSS language definition
         * not only defines CSS highlighting for CSS documents, but also needs to define highlighting for CSS embedded
         * in HTML through `<style>` elements. To do this, it needs to modify `Prism.languages.markup` and add the
         * appropriate tokens. However, `Prism.languages.markup` is a regular JavaScript object literal, so if you do
         * this:
         *
         * ```js
         * Prism.languages.markup.style = {
         *     // token
         * };
         * ```
         *
         * then the `style` token will be added (and processed) at the end. `insertBefore` allows you to insert tokens
         * before existing tokens. For the CSS example above, you would use it like this:
         *
         * ```js
         * Prism.languages.insertBefore('markup', 'cdata', {
         *     'style': {
         *         // token
         *     }
         * });
         * ```
         *
         * ## Special cases
         *
         * If the grammars of `inside` and `insert` have tokens with the same name, the tokens in `inside`'s grammar
         * will be ignored.
         *
         * This behavior can be used to insert tokens after `before`:
         *
         * ```js
         * Prism.languages.insertBefore('markup', 'comment', {
         *     'comment': Prism.languages.markup.comment,
         *     // tokens after 'comment'
         * });
         * ```
         *
         * ## Limitations
         *
         * The main problem `insertBefore` has to solve is iteration order. Since ES2015, the iteration order for object
         * properties is guaranteed to be the insertion order (except for integer keys) but some browsers behave
         * differently when keys are deleted and re-inserted. So `insertBefore` can't be implemented by temporarily
         * deleting properties which is necessary to insert at arbitrary positions.
         *
         * To solve this problem, `insertBefore` doesn't actually insert the given tokens into the target object.
         * Instead, it will create a new object and replace all references to the target object with the new one. This
         * can be done without temporarily deleting properties, so the iteration order is well-defined.
         *
         * However, only references that can be reached from `Prism.languages` or `insert` will be replaced. I.e. if
         * you hold the target object in a variable, then the value of the variable will not change.
         *
         * ```js
         * var oldMarkup = Prism.languages.markup;
         * var newMarkup = Prism.languages.insertBefore('markup', 'comment', { ... });
         *
         * assert(oldMarkup !== Prism.languages.markup);
         * assert(newMarkup === Prism.languages.markup);
         * ```
         *
         * @param {string} inside The property of `root` (e.g. a language id in `Prism.languages`) that contains the
         * object to be modified.
         * @param {string} before The key to insert before.
         * @param {Grammar} insert An object containing the key-value pairs to be inserted.
         * @param {Object<string, any>} [root] The object containing `inside`, i.e. the object that contains the
         * object to be modified.
         *
         * Defaults to `Prism.languages`.
         * @returns {Grammar} The new grammar object.
         * @public
         */
        insertBefore: function(c, o, h, g) {
          g = g || /** @type {any} */
          u.languages;
          var p = g[c], d = {};
          for (var E in p)
            if (p.hasOwnProperty(E)) {
              if (E == o)
                for (var f in h)
                  h.hasOwnProperty(f) && (d[f] = h[f]);
              h.hasOwnProperty(E) || (d[E] = p[E]);
            }
          var A = g[c];
          return g[c] = d, u.languages.DFS(u.languages, function(C, T) {
            T === A && C != c && (this[C] = d);
          }), d;
        },
        // Traverse a language definition with Depth First Search
        DFS: function c(o, h, g, p) {
          p = p || {};
          var d = u.util.objId;
          for (var E in o)
            if (o.hasOwnProperty(E)) {
              h.call(o, E, o[E], g || E);
              var f = o[E], A = u.util.type(f);
              A === "Object" && !p[d(f)] ? (p[d(f)] = !0, c(f, h, null, p)) : A === "Array" && !p[d(f)] && (p[d(f)] = !0, c(f, h, E, p));
            }
        }
      },
      plugins: {},
      /**
       * This is the most high-level function in Prism’s API.
       * It fetches all the elements that have a `.language-xxxx` class and then calls {@link Prism.highlightElement} on
       * each one of them.
       *
       * This is equivalent to `Prism.highlightAllUnder(document, async, callback)`.
       *
       * @param {boolean} [async=false] Same as in {@link Prism.highlightAllUnder}.
       * @param {HighlightCallback} [callback] Same as in {@link Prism.highlightAllUnder}.
       * @memberof Prism
       * @public
       */
      highlightAll: function(c, o) {
        u.highlightAllUnder(document, c, o);
      },
      /**
       * Fetches all the descendants of `container` that have a `.language-xxxx` class and then calls
       * {@link Prism.highlightElement} on each one of them.
       *
       * The following hooks will be run:
       * 1. `before-highlightall`
       * 2. `before-all-elements-highlight`
       * 3. All hooks of {@link Prism.highlightElement} for each element.
       *
       * @param {ParentNode} container The root element, whose descendants that have a `.language-xxxx` class will be highlighted.
       * @param {boolean} [async=false] Whether each element is to be highlighted asynchronously using Web Workers.
       * @param {HighlightCallback} [callback] An optional callback to be invoked on each element after its highlighting is done.
       * @memberof Prism
       * @public
       */
      highlightAllUnder: function(c, o, h) {
        var g = {
          callback: h,
          container: c,
          selector: 'code[class*="language-"], [class*="language-"] code, code[class*="lang-"], [class*="lang-"] code'
        };
        u.hooks.run("before-highlightall", g), g.elements = Array.prototype.slice.apply(g.container.querySelectorAll(g.selector)), u.hooks.run("before-all-elements-highlight", g);
        for (var p = 0, d; d = g.elements[p++]; )
          u.highlightElement(d, o === !0, g.callback);
      },
      /**
       * Highlights the code inside a single element.
       *
       * The following hooks will be run:
       * 1. `before-sanity-check`
       * 2. `before-highlight`
       * 3. All hooks of {@link Prism.highlight}. These hooks will be run by an asynchronous worker if `async` is `true`.
       * 4. `before-insert`
       * 5. `after-highlight`
       * 6. `complete`
       *
       * Some the above hooks will be skipped if the element doesn't contain any text or there is no grammar loaded for
       * the element's language.
       *
       * @param {Element} element The element containing the code.
       * It must have a class of `language-xxxx` to be processed, where `xxxx` is a valid language identifier.
       * @param {boolean} [async=false] Whether the element is to be highlighted asynchronously using Web Workers
       * to improve performance and avoid blocking the UI when highlighting very large chunks of code. This option is
       * [disabled by default](https://prismjs.com/faq.html#why-is-asynchronous-highlighting-disabled-by-default).
       *
       * Note: All language definitions required to highlight the code must be included in the main `prism.js` file for
       * asynchronous highlighting to work. You can build your own bundle on the
       * [Download page](https://prismjs.com/download.html).
       * @param {HighlightCallback} [callback] An optional callback to be invoked after the highlighting is done.
       * Mostly useful when `async` is `true`, since in that case, the highlighting is done asynchronously.
       * @memberof Prism
       * @public
       */
      highlightElement: function(c, o, h) {
        var g = u.util.getLanguage(c), p = u.languages[g];
        u.util.setLanguage(c, g);
        var d = c.parentElement;
        d && d.nodeName.toLowerCase() === "pre" && u.util.setLanguage(d, g);
        var E = c.textContent, f = {
          element: c,
          language: g,
          grammar: p,
          code: E
        };
        function A(T) {
          f.highlightedCode = T, u.hooks.run("before-insert", f), f.element.innerHTML = f.highlightedCode, u.hooks.run("after-highlight", f), u.hooks.run("complete", f), h && h.call(f.element);
        }
        if (u.hooks.run("before-sanity-check", f), d = f.element.parentElement, d && d.nodeName.toLowerCase() === "pre" && !d.hasAttribute("tabindex") && d.setAttribute("tabindex", "0"), !f.code) {
          u.hooks.run("complete", f), h && h.call(f.element);
          return;
        }
        if (u.hooks.run("before-highlight", f), !f.grammar) {
          A(u.util.encode(f.code));
          return;
        }
        if (o && n.Worker) {
          var C = new Worker(u.filename);
          C.onmessage = function(T) {
            A(T.data);
          }, C.postMessage(JSON.stringify({
            language: f.language,
            code: f.code,
            immediateClose: !0
          }));
        } else
          A(u.highlight(f.code, f.grammar, f.language));
      },
      /**
       * Low-level function, only use if you know what you’re doing. It accepts a string of text as input
       * and the language definitions to use, and returns a string with the HTML produced.
       *
       * The following hooks will be run:
       * 1. `before-tokenize`
       * 2. `after-tokenize`
       * 3. `wrap`: On each {@link Token}.
       *
       * @param {string} text A string with the code to be highlighted.
       * @param {Grammar} grammar An object containing the tokens to use.
       *
       * Usually a language definition like `Prism.languages.markup`.
       * @param {string} language The name of the language definition passed to `grammar`.
       * @returns {string} The highlighted HTML.
       * @memberof Prism
       * @public
       * @example
       * Prism.highlight('var foo = true;', Prism.languages.javascript, 'javascript');
       */
      highlight: function(c, o, h) {
        var g = {
          code: c,
          grammar: o,
          language: h
        };
        if (u.hooks.run("before-tokenize", g), !g.grammar)
          throw new Error('The language "' + g.language + '" has no grammar.');
        return g.tokens = u.tokenize(g.code, g.grammar), u.hooks.run("after-tokenize", g), l.stringify(u.util.encode(g.tokens), g.language);
      },
      /**
       * This is the heart of Prism, and the most low-level function you can use. It accepts a string of text as input
       * and the language definitions to use, and returns an array with the tokenized code.
       *
       * When the language definition includes nested tokens, the function is called recursively on each of these tokens.
       *
       * This method could be useful in other contexts as well, as a very crude parser.
       *
       * @param {string} text A string with the code to be highlighted.
       * @param {Grammar} grammar An object containing the tokens to use.
       *
       * Usually a language definition like `Prism.languages.markup`.
       * @returns {TokenStream} An array of strings and tokens, a token stream.
       * @memberof Prism
       * @public
       * @example
       * let code = `var foo = 0;`;
       * let tokens = Prism.tokenize(code, Prism.languages.javascript);
       * tokens.forEach(token => {
       *     if (token instanceof Prism.Token && token.type === 'number') {
       *         console.log(`Found numeric literal: ${token.content}`);
       *     }
       * });
       */
      tokenize: function(c, o) {
        var h = o.rest;
        if (h) {
          for (var g in h)
            o[g] = h[g];
          delete o.rest;
        }
        var p = new k();
        return b(p, p.head, c), D(c, p, o, p.head, 0), B(p);
      },
      /**
       * @namespace
       * @memberof Prism
       * @public
       */
      hooks: {
        all: {},
        /**
         * Adds the given callback to the list of callbacks for the given hook.
         *
         * The callback will be invoked when the hook it is registered for is run.
         * Hooks are usually directly run by a highlight function but you can also run hooks yourself.
         *
         * One callback function can be registered to multiple hooks and the same hook multiple times.
         *
         * @param {string} name The name of the hook.
         * @param {HookCallback} callback The callback function which is given environment variables.
         * @public
         */
        add: function(c, o) {
          var h = u.hooks.all;
          h[c] = h[c] || [], h[c].push(o);
        },
        /**
         * Runs a hook invoking all registered callbacks with the given environment variables.
         *
         * Callbacks will be invoked synchronously and in the order in which they were registered.
         *
         * @param {string} name The name of the hook.
         * @param {Object<string, any>} env The environment variables of the hook passed to all callbacks registered.
         * @public
         */
        run: function(c, o) {
          var h = u.hooks.all[c];
          if (!(!h || !h.length))
            for (var g = 0, p; p = h[g++]; )
              p(o);
        }
      },
      Token: l
    };
    n.Prism = u;
    function l(c, o, h, g) {
      this.type = c, this.content = o, this.alias = h, this.length = (g || "").length | 0;
    }
    l.stringify = function c(o, h) {
      if (typeof o == "string")
        return o;
      if (Array.isArray(o)) {
        var g = "";
        return o.forEach(function(A) {
          g += c(A, h);
        }), g;
      }
      var p = {
        type: o.type,
        content: c(o.content, h),
        tag: "span",
        classes: ["token", o.type],
        attributes: {},
        language: h
      }, d = o.alias;
      d && (Array.isArray(d) ? Array.prototype.push.apply(p.classes, d) : p.classes.push(d)), u.hooks.run("wrap", p);
      var E = "";
      for (var f in p.attributes)
        E += " " + f + '="' + (p.attributes[f] || "").replace(/"/g, "&quot;") + '"';
      return "<" + p.tag + ' class="' + p.classes.join(" ") + '"' + E + ">" + p.content + "</" + p.tag + ">";
    };
    function m(c, o, h, g) {
      c.lastIndex = o;
      var p = c.exec(h);
      if (p && g && p[1]) {
        var d = p[1].length;
        p.index += d, p[0] = p[0].slice(d);
      }
      return p;
    }
    function D(c, o, h, g, p, d) {
      for (var E in h)
        if (!(!h.hasOwnProperty(E) || !h[E])) {
          var f = h[E];
          f = Array.isArray(f) ? f : [f];
          for (var A = 0; A < f.length; ++A) {
            if (d && d.cause == E + "," + A)
              return;
            var C = f[A], T = C.inside, Z = !!C.lookbehind, X = !!C.greedy, W = C.alias;
            if (X && !C.pattern.global) {
              var P = C.pattern.toString().match(/[imsuy]*$/)[0];
              C.pattern = RegExp(C.pattern.source, P + "g");
            }
            for (var V = C.pattern || C, R = g.next, z = p; R !== o.tail && !(d && z >= d.reach); z += R.value.length, R = R.next) {
              var Y = R.value;
              if (o.length > c.length)
                return;
              if (!(Y instanceof l)) {
                var ie = 1, I;
                if (X) {
                  if (I = m(V, z, c, Z), !I || I.index >= c.length)
                    break;
                  var se = I.index, Bt = I.index + I[0].length, N = z;
                  for (N += R.value.length; se >= N; )
                    R = R.next, N += R.value.length;
                  if (N -= R.value.length, z = N, R.value instanceof l)
                    continue;
                  for (var K = R; K !== o.tail && (N < Bt || typeof K.value == "string"); K = K.next)
                    ie++, N += K.value.length;
                  ie--, Y = c.slice(z, N), I.index -= z;
                } else if (I = m(V, 0, Y, Z), !I)
                  continue;
                var se = I.index, ae = I[0], be = Y.slice(0, se), ze = Y.slice(se + ae.length), ke = z + Y.length;
                d && ke > d.reach && (d.reach = ke);
                var ue = R.prev;
                be && (ue = b(o, ue, be), z += be.length), F(o, ue, ie);
                var Tt = new l(E, T ? u.tokenize(ae, T) : ae, W, ae);
                if (R = b(o, ue, Tt), ze && b(o, R, ze), ie > 1) {
                  var Ee = {
                    cause: E + "," + A,
                    reach: ke
                  };
                  D(c, o, h, R.prev, z, Ee), d && Ee.reach > d.reach && (d.reach = Ee.reach);
                }
              }
            }
          }
        }
    }
    function k() {
      var c = { value: null, prev: null, next: null }, o = { value: null, prev: c, next: null };
      c.next = o, this.head = c, this.tail = o, this.length = 0;
    }
    function b(c, o, h) {
      var g = o.next, p = { value: h, prev: o, next: g };
      return o.next = p, g.prev = p, c.length++, p;
    }
    function F(c, o, h) {
      for (var g = o.next, p = 0; p < h && g !== c.tail; p++)
        g = g.next;
      o.next = g, g.prev = o, c.length -= p;
    }
    function B(c) {
      for (var o = [], h = c.head.next; h !== c.tail; )
        o.push(h.value), h = h.next;
      return o;
    }
    if (!n.document)
      return n.addEventListener && (u.disableWorkerMessageHandler || n.addEventListener("message", function(c) {
        var o = JSON.parse(c.data), h = o.language, g = o.code, p = o.immediateClose;
        n.postMessage(u.highlight(g, u.languages[h], h)), p && n.close();
      }, !1)), u;
    var w = u.util.currentScript();
    w && (u.filename = w.src, w.hasAttribute("data-manual") && (u.manual = !0));
    function x() {
      u.manual || u.highlightAll();
    }
    if (!u.manual) {
      var v = document.readyState;
      v === "loading" || v === "interactive" && w && w.defer ? document.addEventListener("DOMContentLoaded", x) : window.requestAnimationFrame ? window.requestAnimationFrame(x) : window.setTimeout(x, 16);
    }
    return u;
  }(t);
  i.exports && (i.exports = e), typeof We < "u" && (We.Prism = e), e.languages.markup = {
    comment: {
      pattern: /<!--(?:(?!<!--)[\s\S])*?-->/,
      greedy: !0
    },
    prolog: {
      pattern: /<\?[\s\S]+?\?>/,
      greedy: !0
    },
    doctype: {
      // https://www.w3.org/TR/xml/#NT-doctypedecl
      pattern: /<!DOCTYPE(?:[^>"'[\]]|"[^"]*"|'[^']*')+(?:\[(?:[^<"'\]]|"[^"]*"|'[^']*'|<(?!!--)|<!--(?:[^-]|-(?!->))*-->)*\]\s*)?>/i,
      greedy: !0,
      inside: {
        "internal-subset": {
          pattern: /(^[^\[]*\[)[\s\S]+(?=\]>$)/,
          lookbehind: !0,
          greedy: !0,
          inside: null
          // see below
        },
        string: {
          pattern: /"[^"]*"|'[^']*'/,
          greedy: !0
        },
        punctuation: /^<!|>$|[[\]]/,
        "doctype-tag": /^DOCTYPE/i,
        name: /[^\s<>'"]+/
      }
    },
    cdata: {
      pattern: /<!\[CDATA\[[\s\S]*?\]\]>/i,
      greedy: !0
    },
    tag: {
      pattern: /<\/?(?!\d)[^\s>\/=$<%]+(?:\s(?:\s*[^\s>\/=]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s'">=]+(?=[\s>]))|(?=[\s/>])))+)?\s*\/?>/,
      greedy: !0,
      inside: {
        tag: {
          pattern: /^<\/?[^\s>\/]+/,
          inside: {
            punctuation: /^<\/?/,
            namespace: /^[^\s>\/:]+:/
          }
        },
        "special-attr": [],
        "attr-value": {
          pattern: /=\s*(?:"[^"]*"|'[^']*'|[^\s'">=]+)/,
          inside: {
            punctuation: [
              {
                pattern: /^=/,
                alias: "attr-equals"
              },
              {
                pattern: /^(\s*)["']|["']$/,
                lookbehind: !0
              }
            ]
          }
        },
        punctuation: /\/?>/,
        "attr-name": {
          pattern: /[^\s>\/]+/,
          inside: {
            namespace: /^[^\s>\/:]+:/
          }
        }
      }
    },
    entity: [
      {
        pattern: /&[\da-z]{1,8};/i,
        alias: "named-entity"
      },
      /&#x?[\da-f]{1,8};/i
    ]
  }, e.languages.markup.tag.inside["attr-value"].inside.entity = e.languages.markup.entity, e.languages.markup.doctype.inside["internal-subset"].inside = e.languages.markup, e.hooks.add("wrap", function(n) {
    n.type === "entity" && (n.attributes.title = n.content.replace(/&amp;/, "&"));
  }), Object.defineProperty(e.languages.markup.tag, "addInlined", {
    /**
     * Adds an inlined language to markup.
     *
     * An example of an inlined language is CSS with `<style>` tags.
     *
     * @param {string} tagName The name of the tag that contains the inlined language. This name will be treated as
     * case insensitive.
     * @param {string} lang The language key.
     * @example
     * addInlined('style', 'css');
     */
    value: function(r, a) {
      var s = {};
      s["language-" + a] = {
        pattern: /(^<!\[CDATA\[)[\s\S]+?(?=\]\]>$)/i,
        lookbehind: !0,
        inside: e.languages[a]
      }, s.cdata = /^<!\[CDATA\[|\]\]>$/i;
      var u = {
        "included-cdata": {
          pattern: /<!\[CDATA\[[\s\S]*?\]\]>/i,
          inside: s
        }
      };
      u["language-" + a] = {
        pattern: /[\s\S]+/,
        inside: e.languages[a]
      };
      var l = {};
      l[r] = {
        pattern: RegExp(/(<__[^>]*>)(?:<!\[CDATA\[(?:[^\]]|\](?!\]>))*\]\]>|(?!<!\[CDATA\[)[\s\S])*?(?=<\/__>)/.source.replace(/__/g, function() {
          return r;
        }), "i"),
        lookbehind: !0,
        greedy: !0,
        inside: u
      }, e.languages.insertBefore("markup", "cdata", l);
    }
  }), Object.defineProperty(e.languages.markup.tag, "addAttribute", {
    /**
     * Adds an pattern to highlight languages embedded in HTML attributes.
     *
     * An example of an inlined language is CSS with `style` attributes.
     *
     * @param {string} attrName The name of the tag that contains the inlined language. This name will be treated as
     * case insensitive.
     * @param {string} lang The language key.
     * @example
     * addAttribute('style', 'css');
     */
    value: function(n, r) {
      e.languages.markup.tag.inside["special-attr"].push({
        pattern: RegExp(
          /(^|["'\s])/.source + "(?:" + n + ")" + /\s*=\s*(?:"[^"]*"|'[^']*'|[^\s'">=]+(?=[\s>]))/.source,
          "i"
        ),
        lookbehind: !0,
        inside: {
          "attr-name": /^[^\s=]+/,
          "attr-value": {
            pattern: /=[\s\S]+/,
            inside: {
              value: {
                pattern: /(^=\s*(["']|(?!["'])))\S[\s\S]*(?=\2$)/,
                lookbehind: !0,
                alias: [r, "language-" + r],
                inside: e.languages[r]
              },
              punctuation: [
                {
                  pattern: /^=/,
                  alias: "attr-equals"
                },
                /"|'/
              ]
            }
          }
        }
      });
    }
  }), e.languages.html = e.languages.markup, e.languages.mathml = e.languages.markup, e.languages.svg = e.languages.markup, e.languages.xml = e.languages.extend("markup", {}), e.languages.ssml = e.languages.xml, e.languages.atom = e.languages.xml, e.languages.rss = e.languages.xml, function(n) {
    var r = /(?:"(?:\\(?:\r\n|[\s\S])|[^"\\\r\n])*"|'(?:\\(?:\r\n|[\s\S])|[^'\\\r\n])*')/;
    n.languages.css = {
      comment: /\/\*[\s\S]*?\*\//,
      atrule: {
        pattern: RegExp("@[\\w-](?:" + /[^;{\s"']|\s+(?!\s)/.source + "|" + r.source + ")*?" + /(?:;|(?=\s*\{))/.source),
        inside: {
          rule: /^@[\w-]+/,
          "selector-function-argument": {
            pattern: /(\bselector\s*\(\s*(?![\s)]))(?:[^()\s]|\s+(?![\s)])|\((?:[^()]|\([^()]*\))*\))+(?=\s*\))/,
            lookbehind: !0,
            alias: "selector"
          },
          keyword: {
            pattern: /(^|[^\w-])(?:and|not|only|or)(?![\w-])/,
            lookbehind: !0
          }
          // See rest below
        }
      },
      url: {
        // https://drafts.csswg.org/css-values-3/#urls
        pattern: RegExp("\\burl\\((?:" + r.source + "|" + /(?:[^\\\r\n()"']|\\[\s\S])*/.source + ")\\)", "i"),
        greedy: !0,
        inside: {
          function: /^url/i,
          punctuation: /^\(|\)$/,
          string: {
            pattern: RegExp("^" + r.source + "$"),
            alias: "url"
          }
        }
      },
      selector: {
        pattern: RegExp(`(^|[{}\\s])[^{}\\s](?:[^{};"'\\s]|\\s+(?![\\s{])|` + r.source + ")*(?=\\s*\\{)"),
        lookbehind: !0
      },
      string: {
        pattern: r,
        greedy: !0
      },
      property: {
        pattern: /(^|[^-\w\xA0-\uFFFF])(?!\s)[-_a-z\xA0-\uFFFF](?:(?!\s)[-\w\xA0-\uFFFF])*(?=\s*:)/i,
        lookbehind: !0
      },
      important: /!important\b/i,
      function: {
        pattern: /(^|[^-a-z0-9])[-a-z0-9]+(?=\()/i,
        lookbehind: !0
      },
      punctuation: /[(){};:,]/
    }, n.languages.css.atrule.inside.rest = n.languages.css;
    var a = n.languages.markup;
    a && (a.tag.addInlined("style", "css"), a.tag.addAttribute("style", "css"));
  }(e), e.languages.clike = {
    comment: [
      {
        pattern: /(^|[^\\])\/\*[\s\S]*?(?:\*\/|$)/,
        lookbehind: !0,
        greedy: !0
      },
      {
        pattern: /(^|[^\\:])\/\/.*/,
        lookbehind: !0,
        greedy: !0
      }
    ],
    string: {
      pattern: /(["'])(?:\\(?:\r\n|[\s\S])|(?!\1)[^\\\r\n])*\1/,
      greedy: !0
    },
    "class-name": {
      pattern: /(\b(?:class|extends|implements|instanceof|interface|new|trait)\s+|\bcatch\s+\()[\w.\\]+/i,
      lookbehind: !0,
      inside: {
        punctuation: /[.\\]/
      }
    },
    keyword: /\b(?:break|catch|continue|do|else|finally|for|function|if|in|instanceof|new|null|return|throw|try|while)\b/,
    boolean: /\b(?:false|true)\b/,
    function: /\b\w+(?=\()/,
    number: /\b0x[\da-f]+\b|(?:\b\d+(?:\.\d*)?|\B\.\d+)(?:e[+-]?\d+)?/i,
    operator: /[<>]=?|[!=]=?=?|--?|\+\+?|&&?|\|\|?|[?*/~^%]/,
    punctuation: /[{}[\];(),.:]/
  }, e.languages.javascript = e.languages.extend("clike", {
    "class-name": [
      e.languages.clike["class-name"],
      {
        pattern: /(^|[^$\w\xA0-\uFFFF])(?!\s)[_$A-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\.(?:constructor|prototype))/,
        lookbehind: !0
      }
    ],
    keyword: [
      {
        pattern: /((?:^|\})\s*)catch\b/,
        lookbehind: !0
      },
      {
        pattern: /(^|[^.]|\.\.\.\s*)\b(?:as|assert(?=\s*\{)|async(?=\s*(?:function\b|\(|[$\w\xA0-\uFFFF]|$))|await|break|case|class|const|continue|debugger|default|delete|do|else|enum|export|extends|finally(?=\s*(?:\{|$))|for|from(?=\s*(?:['"]|$))|function|(?:get|set)(?=\s*(?:[#\[$\w\xA0-\uFFFF]|$))|if|implements|import|in|instanceof|interface|let|new|null|of|package|private|protected|public|return|static|super|switch|this|throw|try|typeof|undefined|var|void|while|with|yield)\b/,
        lookbehind: !0
      }
    ],
    // Allow for all non-ASCII characters (See http://stackoverflow.com/a/2008444)
    function: /#?(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*(?:\.\s*(?:apply|bind|call)\s*)?\()/,
    number: {
      pattern: RegExp(
        /(^|[^\w$])/.source + "(?:" + // constant
        (/NaN|Infinity/.source + "|" + // binary integer
        /0[bB][01]+(?:_[01]+)*n?/.source + "|" + // octal integer
        /0[oO][0-7]+(?:_[0-7]+)*n?/.source + "|" + // hexadecimal integer
        /0[xX][\dA-Fa-f]+(?:_[\dA-Fa-f]+)*n?/.source + "|" + // decimal bigint
        /\d+(?:_\d+)*n/.source + "|" + // decimal number (integer or float) but no bigint
        /(?:\d+(?:_\d+)*(?:\.(?:\d+(?:_\d+)*)?)?|\.\d+(?:_\d+)*)(?:[Ee][+-]?\d+(?:_\d+)*)?/.source) + ")" + /(?![\w$])/.source
      ),
      lookbehind: !0
    },
    operator: /--|\+\+|\*\*=?|=>|&&=?|\|\|=?|[!=]==|<<=?|>>>?=?|[-+*/%&|^!=<>]=?|\.{3}|\?\?=?|\?\.?|[~:]/
  }), e.languages.javascript["class-name"][0].pattern = /(\b(?:class|extends|implements|instanceof|interface|new)\s+)[\w.\\]+/, e.languages.insertBefore("javascript", "keyword", {
    regex: {
      pattern: RegExp(
        // lookbehind
        // eslint-disable-next-line regexp/no-dupe-characters-character-class
        /((?:^|[^$\w\xA0-\uFFFF."'\])\s]|\b(?:return|yield))\s*)/.source + // Regex pattern:
        // There are 2 regex patterns here. The RegExp set notation proposal added support for nested character
        // classes if the `v` flag is present. Unfortunately, nested CCs are both context-free and incompatible
        // with the only syntax, so we have to define 2 different regex patterns.
        /\//.source + "(?:" + /(?:\[(?:[^\]\\\r\n]|\\.)*\]|\\.|[^/\\\[\r\n])+\/[dgimyus]{0,7}/.source + "|" + // `v` flag syntax. This supports 3 levels of nested character classes.
        /(?:\[(?:[^[\]\\\r\n]|\\.|\[(?:[^[\]\\\r\n]|\\.|\[(?:[^[\]\\\r\n]|\\.)*\])*\])*\]|\\.|[^/\\\[\r\n])+\/[dgimyus]{0,7}v[dgimyus]{0,7}/.source + ")" + // lookahead
        /(?=(?:\s|\/\*(?:[^*]|\*(?!\/))*\*\/)*(?:$|[\r\n,.;:})\]]|\/\/))/.source
      ),
      lookbehind: !0,
      greedy: !0,
      inside: {
        "regex-source": {
          pattern: /^(\/)[\s\S]+(?=\/[a-z]*$)/,
          lookbehind: !0,
          alias: "language-regex",
          inside: e.languages.regex
        },
        "regex-delimiter": /^\/|\/$/,
        "regex-flags": /^[a-z]+$/
      }
    },
    // This must be declared before keyword because we use "function" inside the look-forward
    "function-variable": {
      pattern: /#?(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*[=:]\s*(?:async\s*)?(?:\bfunction\b|(?:\((?:[^()]|\([^()]*\))*\)|(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*)\s*=>))/,
      alias: "function"
    },
    parameter: [
      {
        pattern: /(function(?:\s+(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*)?\s*\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\))/,
        lookbehind: !0,
        inside: e.languages.javascript
      },
      {
        pattern: /(^|[^$\w\xA0-\uFFFF])(?!\s)[_$a-z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*=>)/i,
        lookbehind: !0,
        inside: e.languages.javascript
      },
      {
        pattern: /(\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\)\s*=>)/,
        lookbehind: !0,
        inside: e.languages.javascript
      },
      {
        pattern: /((?:\b|\s|^)(?!(?:as|async|await|break|case|catch|class|const|continue|debugger|default|delete|do|else|enum|export|extends|finally|for|from|function|get|if|implements|import|in|instanceof|interface|let|new|null|of|package|private|protected|public|return|set|static|super|switch|this|throw|try|typeof|undefined|var|void|while|with|yield)(?![$\w\xA0-\uFFFF]))(?:(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*\s*)\(\s*|\]\s*\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\)\s*\{)/,
        lookbehind: !0,
        inside: e.languages.javascript
      }
    ],
    constant: /\b[A-Z](?:[A-Z_]|\dx?)*\b/
  }), e.languages.insertBefore("javascript", "string", {
    hashbang: {
      pattern: /^#!.*/,
      greedy: !0,
      alias: "comment"
    },
    "template-string": {
      pattern: /`(?:\\[\s\S]|\$\{(?:[^{}]|\{(?:[^{}]|\{[^}]*\})*\})+\}|(?!\$\{)[^\\`])*`/,
      greedy: !0,
      inside: {
        "template-punctuation": {
          pattern: /^`|`$/,
          alias: "string"
        },
        interpolation: {
          pattern: /((?:^|[^\\])(?:\\{2})*)\$\{(?:[^{}]|\{(?:[^{}]|\{[^}]*\})*\})+\}/,
          lookbehind: !0,
          inside: {
            "interpolation-punctuation": {
              pattern: /^\$\{|\}$/,
              alias: "punctuation"
            },
            rest: e.languages.javascript
          }
        },
        string: /[\s\S]+/
      }
    },
    "string-property": {
      pattern: /((?:^|[,{])[ \t]*)(["'])(?:\\(?:\r\n|[\s\S])|(?!\2)[^\\\r\n])*\2(?=\s*:)/m,
      lookbehind: !0,
      greedy: !0,
      alias: "property"
    }
  }), e.languages.insertBefore("javascript", "operator", {
    "literal-property": {
      pattern: /((?:^|[,{])[ \t]*)(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*:)/m,
      lookbehind: !0,
      alias: "property"
    }
  }), e.languages.markup && (e.languages.markup.tag.addInlined("script", "javascript"), e.languages.markup.tag.addAttribute(
    /on(?:abort|blur|change|click|composition(?:end|start|update)|dblclick|error|focus(?:in|out)?|key(?:down|up)|load|mouse(?:down|enter|leave|move|out|over|up)|reset|resize|scroll|select|slotchange|submit|unload|wheel)/.source,
    "javascript"
  )), e.languages.js = e.languages.javascript, function() {
    if (typeof e > "u" || typeof document > "u")
      return;
    Element.prototype.matches || (Element.prototype.matches = Element.prototype.msMatchesSelector || Element.prototype.webkitMatchesSelector);
    var n = "Loading…", r = function(w, x) {
      return "✖ Error " + w + " while fetching file: " + x;
    }, a = "✖ Error: File does not exist or is empty", s = {
      js: "javascript",
      py: "python",
      rb: "ruby",
      ps1: "powershell",
      psm1: "powershell",
      sh: "bash",
      bat: "batch",
      h: "c",
      tex: "latex"
    }, u = "data-src-status", l = "loading", m = "loaded", D = "failed", k = "pre[data-src]:not([" + u + '="' + m + '"]):not([' + u + '="' + l + '"])';
    function b(w, x, v) {
      var c = new XMLHttpRequest();
      c.open("GET", w, !0), c.onreadystatechange = function() {
        c.readyState == 4 && (c.status < 400 && c.responseText ? x(c.responseText) : c.status >= 400 ? v(r(c.status, c.statusText)) : v(a));
      }, c.send(null);
    }
    function F(w) {
      var x = /^\s*(\d+)\s*(?:(,)\s*(?:(\d+)\s*)?)?$/.exec(w || "");
      if (x) {
        var v = Number(x[1]), c = x[2], o = x[3];
        return c ? o ? [v, Number(o)] : [v, void 0] : [v, v];
      }
    }
    e.hooks.add("before-highlightall", function(w) {
      w.selector += ", " + k;
    }), e.hooks.add("before-sanity-check", function(w) {
      var x = (
        /** @type {HTMLPreElement} */
        w.element
      );
      if (x.matches(k)) {
        w.code = "", x.setAttribute(u, l);
        var v = x.appendChild(document.createElement("CODE"));
        v.textContent = n;
        var c = x.getAttribute("data-src"), o = w.language;
        if (o === "none") {
          var h = (/\.(\w+)$/.exec(c) || [, "none"])[1];
          o = s[h] || h;
        }
        e.util.setLanguage(v, o), e.util.setLanguage(x, o);
        var g = e.plugins.autoloader;
        g && g.loadLanguages(o), b(
          c,
          function(p) {
            x.setAttribute(u, m);
            var d = F(x.getAttribute("data-range"));
            if (d) {
              var E = p.split(/\r\n?|\n/g), f = d[0], A = d[1] == null ? E.length : d[1];
              f < 0 && (f += E.length), f = Math.max(0, Math.min(f - 1, E.length)), A < 0 && (A += E.length), A = Math.max(0, Math.min(A, E.length)), p = E.slice(f, A).join(`
`), x.hasAttribute("data-start") || x.setAttribute("data-start", String(f + 1));
            }
            v.textContent = p, e.highlightElement(v);
          },
          function(p) {
            x.setAttribute(u, D), v.textContent = p;
          }
        );
      }
    }), e.plugins.fileHighlight = {
      /**
       * Executes the File Highlight plugin for all matching `pre` elements under the given container.
       *
       * Note: Elements which are already loaded or currently loading will not be touched by this method.
       *
       * @param {ParentNode} [container=document]
       */
      highlight: function(x) {
        for (var v = (x || document).querySelectorAll(k), c = 0, o; o = v[c++]; )
          e.highlightElement(o);
      }
    };
    var B = !1;
    e.fileHighlight = function() {
      B || (console.warn("Prism.fileHighlight is deprecated. Use `Prism.plugins.fileHighlight.highlight` instead."), B = !0), e.plugins.fileHighlight.highlight.apply(this, arguments);
    };
  }();
})(kt);
var Ae = kt.exports;
Prism.languages.python = {
  comment: {
    pattern: /(^|[^\\])#.*/,
    lookbehind: !0,
    greedy: !0
  },
  "string-interpolation": {
    pattern: /(?:f|fr|rf)(?:("""|''')[\s\S]*?\1|("|')(?:\\.|(?!\2)[^\\\r\n])*\2)/i,
    greedy: !0,
    inside: {
      interpolation: {
        // "{" <expression> <optional "!s", "!r", or "!a"> <optional ":" format specifier> "}"
        pattern: /((?:^|[^{])(?:\{\{)*)\{(?!\{)(?:[^{}]|\{(?!\{)(?:[^{}]|\{(?!\{)(?:[^{}])+\})+\})+\}/,
        lookbehind: !0,
        inside: {
          "format-spec": {
            pattern: /(:)[^:(){}]+(?=\}$)/,
            lookbehind: !0
          },
          "conversion-option": {
            pattern: /![sra](?=[:}]$)/,
            alias: "punctuation"
          },
          rest: null
        }
      },
      string: /[\s\S]+/
    }
  },
  "triple-quoted-string": {
    pattern: /(?:[rub]|br|rb)?("""|''')[\s\S]*?\1/i,
    greedy: !0,
    alias: "string"
  },
  string: {
    pattern: /(?:[rub]|br|rb)?("|')(?:\\.|(?!\1)[^\\\r\n])*\1/i,
    greedy: !0
  },
  function: {
    pattern: /((?:^|\s)def[ \t]+)[a-zA-Z_]\w*(?=\s*\()/g,
    lookbehind: !0
  },
  "class-name": {
    pattern: /(\bclass\s+)\w+/i,
    lookbehind: !0
  },
  decorator: {
    pattern: /(^[\t ]*)@\w+(?:\.\w+)*/m,
    lookbehind: !0,
    alias: ["annotation", "punctuation"],
    inside: {
      punctuation: /\./
    }
  },
  keyword: /\b(?:_(?=\s*:)|and|as|assert|async|await|break|case|class|continue|def|del|elif|else|except|exec|finally|for|from|global|if|import|in|is|lambda|match|nonlocal|not|or|pass|print|raise|return|try|while|with|yield)\b/,
  builtin: /\b(?:__import__|abs|all|any|apply|ascii|basestring|bin|bool|buffer|bytearray|bytes|callable|chr|classmethod|cmp|coerce|compile|complex|delattr|dict|dir|divmod|enumerate|eval|execfile|file|filter|float|format|frozenset|getattr|globals|hasattr|hash|help|hex|id|input|int|intern|isinstance|issubclass|iter|len|list|locals|long|map|max|memoryview|min|next|object|oct|open|ord|pow|property|range|raw_input|reduce|reload|repr|reversed|round|set|setattr|slice|sorted|staticmethod|str|sum|super|tuple|type|unichr|unicode|vars|xrange|zip)\b/,
  boolean: /\b(?:False|None|True)\b/,
  number: /\b0(?:b(?:_?[01])+|o(?:_?[0-7])+|x(?:_?[a-f0-9])+)\b|(?:\b\d+(?:_\d+)*(?:\.(?:\d+(?:_\d+)*)?)?|\B\.\d+(?:_\d+)*)(?:e[+-]?\d+(?:_\d+)*)?j?(?!\w)/i,
  operator: /[-+%=]=?|!=|:=|\*\*?=?|\/\/?=?|<[<=>]?|>[=>]?|[&|^~]/,
  punctuation: /[{}[\];(),.:]/
};
Prism.languages.python["string-interpolation"].inside.interpolation.inside.rest = Prism.languages.python;
Prism.languages.py = Prism.languages.python;
(function(i) {
  var t = /\\(?:[^a-z()[\]]|[a-z*]+)/i, e = {
    "equation-command": {
      pattern: t,
      alias: "regex"
    }
  };
  i.languages.latex = {
    comment: /%.*/,
    // the verbatim environment prints whitespace to the document
    cdata: {
      pattern: /(\\begin\{((?:lstlisting|verbatim)\*?)\})[\s\S]*?(?=\\end\{\2\})/,
      lookbehind: !0
    },
    /*
     * equations can be between $$ $$ or $ $ or \( \) or \[ \]
     * (all are multiline)
     */
    equation: [
      {
        pattern: /\$\$(?:\\[\s\S]|[^\\$])+\$\$|\$(?:\\[\s\S]|[^\\$])+\$|\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]/,
        inside: e,
        alias: "string"
      },
      {
        pattern: /(\\begin\{((?:align|eqnarray|equation|gather|math|multline)\*?)\})[\s\S]*?(?=\\end\{\2\})/,
        lookbehind: !0,
        inside: e,
        alias: "string"
      }
    ],
    /*
     * arguments which are keywords or references are highlighted
     * as keywords
     */
    keyword: {
      pattern: /(\\(?:begin|cite|documentclass|end|label|ref|usepackage)(?:\[[^\]]+\])?\{)[^}]+(?=\})/,
      lookbehind: !0
    },
    url: {
      pattern: /(\\url\{)[^}]+(?=\})/,
      lookbehind: !0
    },
    /*
     * section or chapter headlines are highlighted as bold so that
     * they stand out more
     */
    headline: {
      pattern: /(\\(?:chapter|frametitle|paragraph|part|section|subparagraph|subsection|subsubparagraph|subsubsection|subsubsubparagraph)\*?(?:\[[^\]]+\])?\{)[^}]+(?=\})/,
      lookbehind: !0,
      alias: "class-name"
    },
    function: {
      pattern: t,
      alias: "selector"
    },
    punctuation: /[[\]{}&]/
  }, i.languages.tex = i.languages.latex, i.languages.context = i.languages.latex;
})(Prism);
(function(i) {
  var t = "\\b(?:BASH|BASHOPTS|BASH_ALIASES|BASH_ARGC|BASH_ARGV|BASH_CMDS|BASH_COMPLETION_COMPAT_DIR|BASH_LINENO|BASH_REMATCH|BASH_SOURCE|BASH_VERSINFO|BASH_VERSION|COLORTERM|COLUMNS|COMP_WORDBREAKS|DBUS_SESSION_BUS_ADDRESS|DEFAULTS_PATH|DESKTOP_SESSION|DIRSTACK|DISPLAY|EUID|GDMSESSION|GDM_LANG|GNOME_KEYRING_CONTROL|GNOME_KEYRING_PID|GPG_AGENT_INFO|GROUPS|HISTCONTROL|HISTFILE|HISTFILESIZE|HISTSIZE|HOME|HOSTNAME|HOSTTYPE|IFS|INSTANCE|JOB|LANG|LANGUAGE|LC_ADDRESS|LC_ALL|LC_IDENTIFICATION|LC_MEASUREMENT|LC_MONETARY|LC_NAME|LC_NUMERIC|LC_PAPER|LC_TELEPHONE|LC_TIME|LESSCLOSE|LESSOPEN|LINES|LOGNAME|LS_COLORS|MACHTYPE|MAILCHECK|MANDATORY_PATH|NO_AT_BRIDGE|OLDPWD|OPTERR|OPTIND|ORBIT_SOCKETDIR|OSTYPE|PAPERSIZE|PATH|PIPESTATUS|PPID|PS1|PS2|PS3|PS4|PWD|RANDOM|REPLY|SECONDS|SELINUX_INIT|SESSION|SESSIONTYPE|SESSION_MANAGER|SHELL|SHELLOPTS|SHLVL|SSH_AUTH_SOCK|TERM|UID|UPSTART_EVENTS|UPSTART_INSTANCE|UPSTART_JOB|UPSTART_SESSION|USER|WINDOWID|XAUTHORITY|XDG_CONFIG_DIRS|XDG_CURRENT_DESKTOP|XDG_DATA_DIRS|XDG_GREETER_DATA_DIR|XDG_MENU_PREFIX|XDG_RUNTIME_DIR|XDG_SEAT|XDG_SEAT_PATH|XDG_SESSION_DESKTOP|XDG_SESSION_ID|XDG_SESSION_PATH|XDG_SESSION_TYPE|XDG_VTNR|XMODIFIERS)\\b", e = {
    pattern: /(^(["']?)\w+\2)[ \t]+\S.*/,
    lookbehind: !0,
    alias: "punctuation",
    // this looks reasonably well in all themes
    inside: null
    // see below
  }, n = {
    bash: e,
    environment: {
      pattern: RegExp("\\$" + t),
      alias: "constant"
    },
    variable: [
      // [0]: Arithmetic Environment
      {
        pattern: /\$?\(\([\s\S]+?\)\)/,
        greedy: !0,
        inside: {
          // If there is a $ sign at the beginning highlight $(( and )) as variable
          variable: [
            {
              pattern: /(^\$\(\([\s\S]+)\)\)/,
              lookbehind: !0
            },
            /^\$\(\(/
          ],
          number: /\b0x[\dA-Fa-f]+\b|(?:\b\d+(?:\.\d*)?|\B\.\d+)(?:[Ee]-?\d+)?/,
          // Operators according to https://www.gnu.org/software/bash/manual/bashref.html#Shell-Arithmetic
          operator: /--|\+\+|\*\*=?|<<=?|>>=?|&&|\|\||[=!+\-*/%<>^&|]=?|[?~:]/,
          // If there is no $ sign at the beginning highlight (( and )) as punctuation
          punctuation: /\(\(?|\)\)?|,|;/
        }
      },
      // [1]: Command Substitution
      {
        pattern: /\$\((?:\([^)]+\)|[^()])+\)|`[^`]+`/,
        greedy: !0,
        inside: {
          variable: /^\$\(|^`|\)$|`$/
        }
      },
      // [2]: Brace expansion
      {
        pattern: /\$\{[^}]+\}/,
        greedy: !0,
        inside: {
          operator: /:[-=?+]?|[!\/]|##?|%%?|\^\^?|,,?/,
          punctuation: /[\[\]]/,
          environment: {
            pattern: RegExp("(\\{)" + t),
            lookbehind: !0,
            alias: "constant"
          }
        }
      },
      /\$(?:\w+|[#?*!@$])/
    ],
    // Escape sequences from echo and printf's manuals, and escaped quotes.
    entity: /\\(?:[abceEfnrtv\\"]|O?[0-7]{1,3}|U[0-9a-fA-F]{8}|u[0-9a-fA-F]{4}|x[0-9a-fA-F]{1,2})/
  };
  i.languages.bash = {
    shebang: {
      pattern: /^#!\s*\/.*/,
      alias: "important"
    },
    comment: {
      pattern: /(^|[^"{\\$])#.*/,
      lookbehind: !0
    },
    "function-name": [
      // a) function foo {
      // b) foo() {
      // c) function foo() {
      // but not “foo {”
      {
        // a) and c)
        pattern: /(\bfunction\s+)[\w-]+(?=(?:\s*\(?:\s*\))?\s*\{)/,
        lookbehind: !0,
        alias: "function"
      },
      {
        // b)
        pattern: /\b[\w-]+(?=\s*\(\s*\)\s*\{)/,
        alias: "function"
      }
    ],
    // Highlight variable names as variables in for and select beginnings.
    "for-or-select": {
      pattern: /(\b(?:for|select)\s+)\w+(?=\s+in\s)/,
      alias: "variable",
      lookbehind: !0
    },
    // Highlight variable names as variables in the left-hand part
    // of assignments (“=” and “+=”).
    "assign-left": {
      pattern: /(^|[\s;|&]|[<>]\()\w+(?:\.\w+)*(?=\+?=)/,
      inside: {
        environment: {
          pattern: RegExp("(^|[\\s;|&]|[<>]\\()" + t),
          lookbehind: !0,
          alias: "constant"
        }
      },
      alias: "variable",
      lookbehind: !0
    },
    // Highlight parameter names as variables
    parameter: {
      pattern: /(^|\s)-{1,2}(?:\w+:[+-]?)?\w+(?:\.\w+)*(?=[=\s]|$)/,
      alias: "variable",
      lookbehind: !0
    },
    string: [
      // Support for Here-documents https://en.wikipedia.org/wiki/Here_document
      {
        pattern: /((?:^|[^<])<<-?\s*)(\w+)\s[\s\S]*?(?:\r?\n|\r)\2/,
        lookbehind: !0,
        greedy: !0,
        inside: n
      },
      // Here-document with quotes around the tag
      // → No expansion (so no “inside”).
      {
        pattern: /((?:^|[^<])<<-?\s*)(["'])(\w+)\2\s[\s\S]*?(?:\r?\n|\r)\3/,
        lookbehind: !0,
        greedy: !0,
        inside: {
          bash: e
        }
      },
      // “Normal” string
      {
        // https://www.gnu.org/software/bash/manual/html_node/Double-Quotes.html
        pattern: /(^|[^\\](?:\\\\)*)"(?:\\[\s\S]|\$\([^)]+\)|\$(?!\()|`[^`]+`|[^"\\`$])*"/,
        lookbehind: !0,
        greedy: !0,
        inside: n
      },
      {
        // https://www.gnu.org/software/bash/manual/html_node/Single-Quotes.html
        pattern: /(^|[^$\\])'[^']*'/,
        lookbehind: !0,
        greedy: !0
      },
      {
        // https://www.gnu.org/software/bash/manual/html_node/ANSI_002dC-Quoting.html
        pattern: /\$'(?:[^'\\]|\\[\s\S])*'/,
        greedy: !0,
        inside: {
          entity: n.entity
        }
      }
    ],
    environment: {
      pattern: RegExp("\\$?" + t),
      alias: "constant"
    },
    variable: n.variable,
    function: {
      pattern: /(^|[\s;|&]|[<>]\()(?:add|apropos|apt|apt-cache|apt-get|aptitude|aspell|automysqlbackup|awk|basename|bash|bc|bconsole|bg|bzip2|cal|cargo|cat|cfdisk|chgrp|chkconfig|chmod|chown|chroot|cksum|clear|cmp|column|comm|composer|cp|cron|crontab|csplit|curl|cut|date|dc|dd|ddrescue|debootstrap|df|diff|diff3|dig|dir|dircolors|dirname|dirs|dmesg|docker|docker-compose|du|egrep|eject|env|ethtool|expand|expect|expr|fdformat|fdisk|fg|fgrep|file|find|fmt|fold|format|free|fsck|ftp|fuser|gawk|git|gparted|grep|groupadd|groupdel|groupmod|groups|grub-mkconfig|gzip|halt|head|hg|history|host|hostname|htop|iconv|id|ifconfig|ifdown|ifup|import|install|ip|java|jobs|join|kill|killall|less|link|ln|locate|logname|logrotate|look|lpc|lpr|lprint|lprintd|lprintq|lprm|ls|lsof|lynx|make|man|mc|mdadm|mkconfig|mkdir|mke2fs|mkfifo|mkfs|mkisofs|mknod|mkswap|mmv|more|most|mount|mtools|mtr|mutt|mv|nano|nc|netstat|nice|nl|node|nohup|notify-send|npm|nslookup|op|open|parted|passwd|paste|pathchk|ping|pkill|pnpm|podman|podman-compose|popd|pr|printcap|printenv|ps|pushd|pv|quota|quotacheck|quotactl|ram|rar|rcp|reboot|remsync|rename|renice|rev|rm|rmdir|rpm|rsync|scp|screen|sdiff|sed|sendmail|seq|service|sftp|sh|shellcheck|shuf|shutdown|sleep|slocate|sort|split|ssh|stat|strace|su|sudo|sum|suspend|swapon|sync|sysctl|tac|tail|tar|tee|time|timeout|top|touch|tr|traceroute|tsort|tty|umount|uname|unexpand|uniq|units|unrar|unshar|unzip|update-grub|uptime|useradd|userdel|usermod|users|uudecode|uuencode|v|vcpkg|vdir|vi|vim|virsh|vmstat|wait|watch|wc|wget|whereis|which|who|whoami|write|xargs|xdg-open|yarn|yes|zenity|zip|zsh|zypper)(?=$|[)\s;|&])/,
      lookbehind: !0
    },
    keyword: {
      pattern: /(^|[\s;|&]|[<>]\()(?:case|do|done|elif|else|esac|fi|for|function|if|in|select|then|until|while)(?=$|[)\s;|&])/,
      lookbehind: !0
    },
    // https://www.gnu.org/software/bash/manual/html_node/Shell-Builtin-Commands.html
    builtin: {
      pattern: /(^|[\s;|&]|[<>]\()(?:\.|:|alias|bind|break|builtin|caller|cd|command|continue|declare|echo|enable|eval|exec|exit|export|getopts|hash|help|let|local|logout|mapfile|printf|pwd|read|readarray|readonly|return|set|shift|shopt|source|test|times|trap|type|typeset|ulimit|umask|unalias|unset)(?=$|[)\s;|&])/,
      lookbehind: !0,
      // Alias added to make those easier to distinguish from strings.
      alias: "class-name"
    },
    boolean: {
      pattern: /(^|[\s;|&]|[<>]\()(?:false|true)(?=$|[)\s;|&])/,
      lookbehind: !0
    },
    "file-descriptor": {
      pattern: /\B&\d\b/,
      alias: "important"
    },
    operator: {
      // Lots of redirections here, but not just that.
      pattern: /\d?<>|>\||\+=|=[=~]?|!=?|<<[<-]?|[&\d]?>>|\d[<>]&?|[<>][&=]?|&[>&]?|\|[&|]?/,
      inside: {
        "file-descriptor": {
          pattern: /^\d/,
          alias: "important"
        }
      }
    },
    punctuation: /\$?\(\(?|\)\)?|\.\.|[{}[\];\\]/,
    number: {
      pattern: /(^|\s)(?:[1-9]\d*|0)(?:[.,]\d+)?\b/,
      lookbehind: !0
    }
  }, e.inside = i.languages.bash;
  for (var r = [
    "comment",
    "function-name",
    "for-or-select",
    "assign-left",
    "parameter",
    "string",
    "environment",
    "function",
    "keyword",
    "builtin",
    "boolean",
    "file-descriptor",
    "operator",
    "punctuation",
    "number"
  ], a = n.variable[1].inside, s = 0; s < r.length; s++)
    a[r[s]] = i.languages.bash[r[s]];
  i.languages.sh = i.languages.bash, i.languages.shell = i.languages.bash;
})(Prism);
const Cn = '<svg class="md-link-icon" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true" fill="currentColor"><path d="m7.775 3.275 1.25-1.25a3.5 3.5 0 1 1 4.95 4.95l-2.5 2.5a3.5 3.5 0 0 1-4.95 0 .751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018 1.998 1.998 0 0 0 2.83 0l2.5-2.5a2.002 2.002 0 0 0-2.83-2.83l-1.25 1.25a.751.751 0 0 1-1.042-.018.751.751 0 0 1-.018-1.042Zm-4.69 9.64a1.998 1.998 0 0 0 2.83 0l1.25-1.25a.751.751 0 0 1 1.042.018.751.751 0 0 1 .018 1.042l-1.25 1.25a3.5 3.5 0 1 1-4.95-4.95l2.5-2.5a3.5 3.5 0 0 1 4.95 0 .751.751 0 0 1-.018 1.042.751.751 0 0 1-1.042.018 1.998 1.998 0 0 0-2.83 0l-2.5 2.5a1.998 1.998 0 0 0 0 2.83Z"></path></svg>', yn = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 15 15" color="currentColor" aria-hidden="true" aria-label="Copy" stroke-width="1.3" width="15" height="15">
  <path fill="currentColor" d="M12.728 4.545v8.182H4.545V4.545zm0 -0.909H4.545a0.909 0.909 0 0 0 -0.909 0.909v8.182a0.909 0.909 0 0 0 0.909 0.909h8.182a0.909 0.909 0 0 0 0.909 -0.909V4.545a0.909 0.909 0 0 0 -0.909 -0.909"/>
  <path fill="currentColor" d="M1.818 8.182H0.909V1.818a0.909 0.909 0 0 1 0.909 -0.909h6.364v0.909H1.818Z"/>
</svg>

`, _n = `<svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 17 17" aria-hidden="true" aria-label="Copied" fill="none" stroke="currentColor" stroke-width="1.3">
  <path d="m13.813 4.781 -7.438 7.438 -3.188 -3.188"/>
</svg>
`, Ve = `<button title="copy" class="copy_code_button">
  <span class="copy-text">${yn}</span>
  <span class="check">${_n}</span>
</button>`, Et = /[&<>"']/, vn = new RegExp(Et.source, "g"), At = /[<>"']|&(?!(#\d{1,7}|#[Xx][a-fA-F0-9]{1,6}|\w+);)/, Sn = new RegExp(At.source, "g"), Bn = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;"
}, Ye = (i) => Bn[i] || "";
function we(i, t) {
  if (t) {
    if (Et.test(i))
      return i.replace(vn, Ye);
  } else if (At.test(i))
    return i.replace(Sn, Ye);
  return i;
}
function Tn(i) {
  const t = i.map((e) => ({
    start: new RegExp(e.left.replace(/[-\/\\^$*+?.()|[\]{}]/g, "\\$&")),
    end: new RegExp(e.right.replace(/[-\/\\^$*+?.()|[\]{}]/g, "\\$&"))
  }));
  return {
    name: "latex",
    level: "block",
    start(e) {
      for (const n of t) {
        const r = e.match(n.start);
        if (r)
          return r.index;
      }
      return -1;
    },
    tokenizer(e, n) {
      for (const r of t) {
        const a = new RegExp(
          `${r.start.source}([\\s\\S]+?)${r.end.source}`
        ).exec(e);
        if (a)
          return {
            type: "latex",
            raw: a[0],
            text: a[1].trim()
          };
      }
    },
    renderer(e) {
      return `<div class="latex-block">${e.text}</div>`;
    }
  };
}
function Rn() {
  return {
    name: "mermaid",
    level: "block",
    start(i) {
      var t;
      return (t = i.match(/^```mermaid\s*\n/)) == null ? void 0 : t.index;
    },
    tokenizer(i) {
      const t = /^```mermaid\s*\n([\s\S]*?)```\s*(?:\n|$)/.exec(i);
      if (t)
        return {
          type: "mermaid",
          raw: t[0],
          text: t[1].trim()
        };
    },
    renderer(i) {
      return `<div class="mermaid">${i.text}</div>
`;
    }
  };
}
const Ln = {
  code(i, t, e) {
    var r;
    const n = ((r = (t ?? "").match(/\S*/)) == null ? void 0 : r[0]) ?? "";
    return i = i.replace(/\n$/, "") + `
`, !n || n === "mermaid" ? '<div class="code_wrap">' + Ve + "<pre><code>" + (e ? i : we(i, !0)) + `</code></pre></div>
` : '<div class="code_wrap">' + Ve + '<pre><code class="language-' + we(n) + '">' + (e ? i : we(i, !0)) + `</code></pre></div>
`;
  }
}, In = new $e();
function $n({
  header_links: i,
  line_breaks: t,
  latex_delimiters: e
}) {
  const n = new dt();
  n.use(
    {
      gfm: !0,
      pedantic: !1,
      breaks: t
    },
    Dn({
      highlight: (s, u) => {
        var l;
        return (l = Ae.languages) != null && l[u] ? Ae.highlight(s, Ae.languages[u], u) : s;
      }
    }),
    { renderer: Ln }
  ), i && (n.use(wn()), n.use({
    extensions: [
      {
        name: "heading",
        level: "block",
        renderer(s) {
          const u = s.raw.toLowerCase().trim().replace(/<[!\/a-z].*?>/gi, ""), l = "h" + In.slug(u), m = s.depth, D = this.parser.parseInline(s.tokens);
          return `<h${m} id="${l}"><a class="md-header-anchor" href="#${l}">${Cn}</a>${D}</h${m}>
`;
        }
      }
    ]
  }));
  const r = Rn(), a = Tn(e);
  return n.use({
    extensions: [r, a]
  }), n;
}
const _e = (i) => JSON.parse(JSON.stringify(i)), zn = (i) => i.nodeType === 1, On = (i) => ir.has(i.tagName), Mn = (i) => "action" in i, Pn = (i) => i.tagName === "IFRAME", Nn = (i) => "formAction" in i, Hn = (i) => "protocol" in i, pe = /* @__PURE__ */ (() => {
  const i = /^(?:\w+script|data):/i;
  return (t) => i.test(t);
})(), qn = /* @__PURE__ */ (() => {
  const i = /(?:script|data):/i;
  return (t) => i.test(t);
})(), Gn = (i) => {
  const t = {};
  for (let e = 0, n = i.length; e < n; e++) {
    const r = i[e];
    for (const a in r)
      t[a] ? t[a] = t[a].concat(r[a]) : t[a] = r[a];
  }
  return t;
}, wt = (i, t) => {
  let e = i.firstChild;
  for (; e; ) {
    const n = e.nextSibling;
    zn(e) && (t(e, i), e.parentNode && wt(e, t)), e = n;
  }
}, Un = (i, t) => {
  const e = document.createNodeIterator(i, NodeFilter.SHOW_ELEMENT);
  let n;
  for (; n = e.nextNode(); ) {
    const r = n.parentNode;
    r && t(n, r);
  }
}, jn = (i, t) => !!globalThis.document && !!globalThis.document.createNodeIterator ? Un(i, t) : wt(i, t), xt = [
  "a",
  "abbr",
  "acronym",
  "address",
  "area",
  "article",
  "aside",
  "audio",
  "b",
  "bdi",
  "bdo",
  "bgsound",
  "big",
  "blockquote",
  "body",
  "br",
  "button",
  "canvas",
  "caption",
  "center",
  "cite",
  "code",
  "col",
  "colgroup",
  "datalist",
  "dd",
  "del",
  "details",
  "dfn",
  "dialog",
  "dir",
  "div",
  "dl",
  "dt",
  "em",
  "fieldset",
  "figcaption",
  "figure",
  "font",
  "footer",
  "form",
  "h1",
  "h2",
  "h3",
  "h4",
  "h5",
  "h6",
  "head",
  "header",
  "hgroup",
  "hr",
  "html",
  "i",
  "img",
  "input",
  "ins",
  "kbd",
  "keygen",
  "label",
  "layer",
  "legend",
  "li",
  "link",
  "listing",
  "main",
  "map",
  "mark",
  "marquee",
  "menu",
  "meta",
  "meter",
  "nav",
  "nobr",
  "ol",
  "optgroup",
  "option",
  "output",
  "p",
  "picture",
  "popup",
  "pre",
  "progress",
  "q",
  "rb",
  "rp",
  "rt",
  "rtc",
  "ruby",
  "s",
  "samp",
  "section",
  "select",
  "selectmenu",
  "small",
  "source",
  "span",
  "strike",
  "strong",
  "style",
  "sub",
  "summary",
  "sup",
  "table",
  "tbody",
  "td",
  "tfoot",
  "th",
  "thead",
  "time",
  "tr",
  "track",
  "tt",
  "u",
  "ul",
  "var",
  "video",
  "wbr"
], Zn = [
  "basefont",
  "command",
  "data",
  "iframe",
  "image",
  "plaintext",
  "portal",
  "slot",
  // 'template', //TODO: Not exactly correct to never allow this, too strict
  "textarea",
  "title",
  "xmp"
], Xn = /* @__PURE__ */ new Set([
  ...xt,
  ...Zn
]), Ct = [
  "svg",
  "a",
  "altglyph",
  "altglyphdef",
  "altglyphitem",
  "animatecolor",
  "animatemotion",
  "animatetransform",
  "circle",
  "clippath",
  "defs",
  "desc",
  "ellipse",
  "filter",
  "font",
  "g",
  "glyph",
  "glyphref",
  "hkern",
  "image",
  "line",
  "lineargradient",
  "marker",
  "mask",
  "metadata",
  "mpath",
  "path",
  "pattern",
  "polygon",
  "polyline",
  "radialgradient",
  "rect",
  "stop",
  "style",
  "switch",
  "symbol",
  "text",
  "textpath",
  "title",
  "tref",
  "tspan",
  "view",
  "vkern",
  /* FILTERS */
  "feBlend",
  "feColorMatrix",
  "feComponentTransfer",
  "feComposite",
  "feConvolveMatrix",
  "feDiffuseLighting",
  "feDisplacementMap",
  "feDistantLight",
  "feFlood",
  "feFuncA",
  "feFuncB",
  "feFuncG",
  "feFuncR",
  "feGaussianBlur",
  "feImage",
  "feMerge",
  "feMergeNode",
  "feMorphology",
  "feOffset",
  "fePointLight",
  "feSpecularLighting",
  "feSpotLight",
  "feTile",
  "feTurbulence"
], Wn = [
  "animate",
  "color-profile",
  "cursor",
  "discard",
  "fedropshadow",
  "font-face",
  "font-face-format",
  "font-face-name",
  "font-face-src",
  "font-face-uri",
  "foreignobject",
  "hatch",
  "hatchpath",
  "mesh",
  "meshgradient",
  "meshpatch",
  "meshrow",
  "missing-glyph",
  "script",
  "set",
  "solidcolor",
  "unknown",
  "use"
], Vn = /* @__PURE__ */ new Set([
  ...Ct,
  ...Wn
]), yt = [
  "math",
  "menclose",
  "merror",
  "mfenced",
  "mfrac",
  "mglyph",
  "mi",
  "mlabeledtr",
  "mmultiscripts",
  "mn",
  "mo",
  "mover",
  "mpadded",
  "mphantom",
  "mroot",
  "mrow",
  "ms",
  "mspace",
  "msqrt",
  "mstyle",
  "msub",
  "msup",
  "msubsup",
  "mtable",
  "mtd",
  "mtext",
  "mtr",
  "munder",
  "munderover"
], Yn = [
  "maction",
  "maligngroup",
  "malignmark",
  "mlongdiv",
  "mscarries",
  "mscarry",
  "msgroup",
  "mstack",
  "msline",
  "msrow",
  "semantics",
  "annotation",
  "annotation-xml",
  "mprescripts",
  "none"
], Qn = /* @__PURE__ */ new Set([
  ...yt,
  ...Yn
]), Kn = [
  "abbr",
  "accept",
  "accept-charset",
  "accesskey",
  "action",
  "align",
  "alink",
  "allow",
  "allowfullscreen",
  "alt",
  "anchor",
  "archive",
  "as",
  "async",
  "autocapitalize",
  "autocomplete",
  "autocorrect",
  "autofocus",
  "autopictureinpicture",
  "autoplay",
  "axis",
  "background",
  "behavior",
  "bgcolor",
  "border",
  "bordercolor",
  "capture",
  "cellpadding",
  "cellspacing",
  "challenge",
  "char",
  "charoff",
  "charset",
  "checked",
  "cite",
  "class",
  "classid",
  "clear",
  "code",
  "codebase",
  "codetype",
  "color",
  "cols",
  "colspan",
  "compact",
  "content",
  "contenteditable",
  "controls",
  "controlslist",
  "conversiondestination",
  "coords",
  "crossorigin",
  "csp",
  "data",
  "datetime",
  "declare",
  "decoding",
  "default",
  "defer",
  "dir",
  "direction",
  "dirname",
  "disabled",
  "disablepictureinpicture",
  "disableremoteplayback",
  "disallowdocumentaccess",
  "download",
  "draggable",
  "elementtiming",
  "enctype",
  "end",
  "enterkeyhint",
  "event",
  "exportparts",
  "face",
  "for",
  "form",
  "formaction",
  "formenctype",
  "formmethod",
  "formnovalidate",
  "formtarget",
  "frame",
  "frameborder",
  "headers",
  "height",
  "hidden",
  "high",
  "href",
  "hreflang",
  "hreftranslate",
  "hspace",
  "http-equiv",
  "id",
  "imagesizes",
  "imagesrcset",
  "importance",
  "impressiondata",
  "impressionexpiry",
  "incremental",
  "inert",
  "inputmode",
  "integrity",
  "invisible",
  "ismap",
  "keytype",
  "kind",
  "label",
  "lang",
  "language",
  "latencyhint",
  "leftmargin",
  "link",
  "list",
  "loading",
  "longdesc",
  "loop",
  "low",
  "lowsrc",
  "manifest",
  "marginheight",
  "marginwidth",
  "max",
  "maxlength",
  "mayscript",
  "media",
  "method",
  "min",
  "minlength",
  "multiple",
  "muted",
  "name",
  "nohref",
  "nomodule",
  "nonce",
  "noresize",
  "noshade",
  "novalidate",
  "nowrap",
  "object",
  "open",
  "optimum",
  "part",
  "pattern",
  "ping",
  "placeholder",
  "playsinline",
  "policy",
  "poster",
  "preload",
  "pseudo",
  "readonly",
  "referrerpolicy",
  "rel",
  "reportingorigin",
  "required",
  "resources",
  "rev",
  "reversed",
  "role",
  "rows",
  "rowspan",
  "rules",
  "sandbox",
  "scheme",
  "scope",
  "scopes",
  "scrollamount",
  "scrolldelay",
  "scrolling",
  "select",
  "selected",
  "shadowroot",
  "shadowrootdelegatesfocus",
  "shape",
  "size",
  "sizes",
  "slot",
  "span",
  "spellcheck",
  "src",
  "srclang",
  "srcset",
  "standby",
  "start",
  "step",
  "style",
  "summary",
  "tabindex",
  "target",
  "text",
  "title",
  "topmargin",
  "translate",
  "truespeed",
  "trusttoken",
  "type",
  "usemap",
  "valign",
  "value",
  "valuetype",
  "version",
  "virtualkeyboardpolicy",
  "vlink",
  "vspace",
  "webkitdirectory",
  "width",
  "wrap"
], Jn = [
  "accent-height",
  "accumulate",
  "additive",
  "alignment-baseline",
  "ascent",
  "attributename",
  "attributetype",
  "azimuth",
  "basefrequency",
  "baseline-shift",
  "begin",
  "bias",
  "by",
  "class",
  "clip",
  "clippathunits",
  "clip-path",
  "clip-rule",
  "color",
  "color-interpolation",
  "color-interpolation-filters",
  "color-profile",
  "color-rendering",
  "cx",
  "cy",
  "d",
  "dx",
  "dy",
  "diffuseconstant",
  "direction",
  "display",
  "divisor",
  "dominant-baseline",
  "dur",
  "edgemode",
  "elevation",
  "end",
  "fill",
  "fill-opacity",
  "fill-rule",
  "filter",
  "filterunits",
  "flood-color",
  "flood-opacity",
  "font-family",
  "font-size",
  "font-size-adjust",
  "font-stretch",
  "font-style",
  "font-variant",
  "font-weight",
  "fx",
  "fy",
  "g1",
  "g2",
  "glyph-name",
  "glyphref",
  "gradientunits",
  "gradienttransform",
  "height",
  "href",
  "id",
  "image-rendering",
  "in",
  "in2",
  "k",
  "k1",
  "k2",
  "k3",
  "k4",
  "kerning",
  "keypoints",
  "keysplines",
  "keytimes",
  "lang",
  "lengthadjust",
  "letter-spacing",
  "kernelmatrix",
  "kernelunitlength",
  "lighting-color",
  "local",
  "marker-end",
  "marker-mid",
  "marker-start",
  "markerheight",
  "markerunits",
  "markerwidth",
  "maskcontentunits",
  "maskunits",
  "max",
  "mask",
  "media",
  "method",
  "mode",
  "min",
  "name",
  "numoctaves",
  "offset",
  "operator",
  "opacity",
  "order",
  "orient",
  "orientation",
  "origin",
  "overflow",
  "paint-order",
  "path",
  "pathlength",
  "patterncontentunits",
  "patterntransform",
  "patternunits",
  "points",
  "preservealpha",
  "preserveaspectratio",
  "primitiveunits",
  "r",
  "rx",
  "ry",
  "radius",
  "refx",
  "refy",
  "repeatcount",
  "repeatdur",
  "restart",
  "result",
  "rotate",
  "scale",
  "seed",
  "shape-rendering",
  "specularconstant",
  "specularexponent",
  "spreadmethod",
  "startoffset",
  "stddeviation",
  "stitchtiles",
  "stop-color",
  "stop-opacity",
  "stroke-dasharray",
  "stroke-dashoffset",
  "stroke-linecap",
  "stroke-linejoin",
  "stroke-miterlimit",
  "stroke-opacity",
  "stroke",
  "stroke-width",
  "style",
  "surfacescale",
  "systemlanguage",
  "tabindex",
  "targetx",
  "targety",
  "transform",
  "transform-origin",
  "text-anchor",
  "text-decoration",
  "text-rendering",
  "textlength",
  "type",
  "u1",
  "u2",
  "unicode",
  "values",
  "viewbox",
  "visibility",
  "version",
  "vert-adv-y",
  "vert-origin-x",
  "vert-origin-y",
  "width",
  "word-spacing",
  "wrap",
  "writing-mode",
  "xchannelselector",
  "ychannelselector",
  "x",
  "x1",
  "x2",
  "xmlns",
  "y",
  "y1",
  "y2",
  "z",
  "zoomandpan"
], er = [
  "accent",
  "accentunder",
  "align",
  "bevelled",
  "close",
  "columnsalign",
  "columnlines",
  "columnspan",
  "denomalign",
  "depth",
  "dir",
  "display",
  "displaystyle",
  "encoding",
  "fence",
  "frame",
  "height",
  "href",
  "id",
  "largeop",
  "length",
  "linethickness",
  "lspace",
  "lquote",
  "mathbackground",
  "mathcolor",
  "mathsize",
  "mathvariant",
  "maxsize",
  "minsize",
  "movablelimits",
  "notation",
  "numalign",
  "open",
  "rowalign",
  "rowlines",
  "rowspacing",
  "rowspan",
  "rspace",
  "rquote",
  "scriptlevel",
  "scriptminsize",
  "scriptsizemultiplier",
  "selection",
  "separator",
  "separators",
  "stretchy",
  "subscriptshift",
  "supscriptshift",
  "symmetric",
  "voffset",
  "width",
  "xmlns"
], $ = {
  HTML: "http://www.w3.org/1999/xhtml",
  SVG: "http://www.w3.org/2000/svg",
  MATH: "http://www.w3.org/1998/Math/MathML"
}, tr = {
  [$.HTML]: Xn,
  [$.SVG]: Vn,
  [$.MATH]: Qn
}, nr = {
  [$.HTML]: "html",
  [$.SVG]: "svg",
  [$.MATH]: "math"
}, rr = {
  [$.HTML]: "",
  [$.SVG]: "svg:",
  [$.MATH]: "math:"
}, ir = /* @__PURE__ */ new Set([
  "A",
  "AREA",
  "BUTTON",
  "FORM",
  "IFRAME",
  "INPUT"
]), _t = {
  allowComments: !0,
  allowCustomElements: !1,
  allowUnknownMarkup: !1,
  allowElements: [
    ...xt,
    ...Ct.map((i) => `svg:${i}`),
    ...yt.map((i) => `math:${i}`)
  ],
  allowAttributes: Gn([
    Object.fromEntries(Kn.map((i) => [i, ["*"]])),
    Object.fromEntries(Jn.map((i) => [i, ["svg:*"]])),
    Object.fromEntries(er.map((i) => [i, ["math:*"]]))
  ])
};
var xe = function(i, t, e, n, r) {
  if (n === "m") throw new TypeError("Private method is not writable");
  if (n === "a" && !r) throw new TypeError("Private accessor was defined without a setter");
  if (typeof t == "function" ? i !== t || !r : !t.has(i)) throw new TypeError("Cannot write private member to an object whose class did not declare it");
  return n === "a" ? r.call(i, e) : r ? r.value = e : t.set(i, e), e;
}, q = function(i, t, e, n) {
  if (e === "a" && !n) throw new TypeError("Private accessor was defined without a getter");
  if (typeof t == "function" ? i !== t || !n : !t.has(i)) throw new TypeError("Cannot read private member from an object whose class did not declare it");
  return e === "m" ? n : e === "a" ? n.call(i) : n ? n.value : t.get(i);
}, H, ge, de;
class vt {
  /* CONSTRUCTOR */
  constructor(t = {}) {
    H.set(this, void 0), ge.set(this, void 0), de.set(this, void 0), this.getConfiguration = () => _e(q(this, H, "f")), this.sanitize = (D) => {
      const k = q(this, ge, "f"), b = q(this, de, "f");
      return jn(D, (F, B) => {
        const w = F.namespaceURI || $.HTML, x = B.namespaceURI || $.HTML, v = tr[w], c = nr[w], o = rr[w], h = F.tagName.toLowerCase(), g = `${o}${h}`, d = `${o}*`;
        if (!v.has(h) || !k.has(g) || w !== x && h !== c)
          B.removeChild(F);
        else {
          const E = F.getAttributeNames(), f = E.length;
          if (f) {
            for (let A = 0; A < f; A++) {
              const C = E[A], T = b[C];
              (!T || !T.has(d) && !T.has(g)) && F.removeAttribute(C);
            }
            if (On(F))
              if (Hn(F)) {
                const A = F.getAttribute("href");
                A && qn(A) && pe(F.protocol) && F.removeAttribute("href");
              } else Mn(F) ? pe(F.action) && F.removeAttribute("action") : Nn(F) ? pe(F.formAction) && F.removeAttribute("formaction") : Pn(F) && (pe(F.src) && F.removeAttribute("formaction"), F.setAttribute("sandbox", "allow-scripts"));
          }
        }
      }), D;
    }, this.sanitizeFor = (D, k) => {
      throw new Error('"sanitizeFor" is not implemented yet');
    };
    const { allowComments: e, allowCustomElements: n, allowUnknownMarkup: r, blockElements: a, dropElements: s, dropAttributes: u } = t;
    if (e === !1)
      throw new Error('A false "allowComments" is not supported yet');
    if (n)
      throw new Error('A true "allowCustomElements" is not supported yet');
    if (r)
      throw new Error('A true "allowUnknownMarkup" is not supported yet');
    if (a)
      throw new Error('"blockElements" is not supported yet, use "allowElements" instead');
    if (s)
      throw new Error('"dropElements" is not supported yet, use "allowElements" instead');
    if (u)
      throw new Error('"dropAttributes" is not supported yet, use "allowAttributes" instead');
    xe(this, H, _e(_t), "f");
    const { allowElements: l, allowAttributes: m } = t;
    l && (q(this, H, "f").allowElements = t.allowElements), m && (q(this, H, "f").allowAttributes = t.allowAttributes), xe(this, ge, new Set(q(this, H, "f").allowElements), "f"), xe(this, de, Object.fromEntries(Object.entries(q(this, H, "f").allowAttributes || {}).map(([D, k]) => [D, new Set(k)])), "f");
  }
}
H = /* @__PURE__ */ new WeakMap(), ge = /* @__PURE__ */ new WeakMap(), de = /* @__PURE__ */ new WeakMap();
vt.getDefaultConfiguration = () => _e(_t);
const sr = (i, t = location.href) => {
  try {
    return !!i && new URL(i).origin !== new URL(t).origin;
  } catch {
    return !1;
  }
};
function Qe(i) {
  const t = new vt(), e = new DOMParser().parseFromString(i, "text/html");
  return St(e.body, "A", (n) => {
    n instanceof HTMLElement && "target" in n && sr(n.getAttribute("href"), location.href) && (n.setAttribute("target", "_blank"), n.setAttribute("rel", "noopener noreferrer"));
  }), t.sanitize(e).body.innerHTML;
}
function St(i, t, e) {
  i && (i.nodeName === t || typeof t == "function") && e(i);
  const n = (i == null ? void 0 : i.childNodes) || [];
  for (let r = 0; r < n.length; r++)
    St(n[r], t, e);
}
const Ke = [
  "!--",
  "!doctype",
  "a",
  "abbr",
  "acronym",
  "address",
  "applet",
  "area",
  "article",
  "aside",
  "audio",
  "b",
  "base",
  "basefont",
  "bdi",
  "bdo",
  "big",
  "blockquote",
  "body",
  "br",
  "button",
  "canvas",
  "caption",
  "center",
  "cite",
  "code",
  "col",
  "colgroup",
  "data",
  "datalist",
  "dd",
  "del",
  "details",
  "dfn",
  "dialog",
  "dir",
  "div",
  "dl",
  "dt",
  "em",
  "embed",
  "fieldset",
  "figcaption",
  "figure",
  "font",
  "footer",
  "form",
  "frame",
  "frameset",
  "h1",
  "h2",
  "h3",
  "h4",
  "h5",
  "h6",
  "head",
  "header",
  "hgroup",
  "hr",
  "html",
  "i",
  "iframe",
  "img",
  "input",
  "ins",
  "kbd",
  "label",
  "legend",
  "li",
  "link",
  "main",
  "map",
  "mark",
  "menu",
  "meta",
  "meter",
  "nav",
  "noframes",
  "noscript",
  "object",
  "ol",
  "optgroup",
  "option",
  "output",
  "p",
  "param",
  "picture",
  "pre",
  "progress",
  "q",
  "rp",
  "rt",
  "ruby",
  "s",
  "samp",
  "script",
  "search",
  "section",
  "select",
  "small",
  "source",
  "span",
  "strike",
  "strong",
  "style",
  "sub",
  "summary",
  "sup",
  "svg",
  "table",
  "tbody",
  "td",
  "template",
  "textarea",
  "tfoot",
  "th",
  "thead",
  "time",
  "title",
  "tr",
  "track",
  "tt",
  "u",
  "ul",
  "var",
  "video",
  "wbr"
], ar = [
  // Base structural elements
  "g",
  "defs",
  "use",
  "symbol",
  // Shape elements
  "rect",
  "circle",
  "ellipse",
  "line",
  "polyline",
  "polygon",
  "path",
  "image",
  // Text elements
  "text",
  "tspan",
  "textPath",
  // Gradient and effects
  "linearGradient",
  "radialGradient",
  "stop",
  "pattern",
  "clipPath",
  "mask",
  "filter",
  // Filter effects
  "feBlend",
  "feColorMatrix",
  "feComponentTransfer",
  "feComposite",
  "feConvolveMatrix",
  "feDiffuseLighting",
  "feDisplacementMap",
  "feGaussianBlur",
  "feMerge",
  "feMorphology",
  "feOffset",
  "feSpecularLighting",
  "feTurbulence",
  "feMergeNode",
  "feFuncR",
  "feFuncG",
  "feFuncB",
  "feFuncA",
  "feDistantLight",
  "fePointLight",
  "feSpotLight",
  "feFlood",
  "feTile",
  // Animation elements
  "animate",
  "animateTransform",
  "animateMotion",
  "mpath",
  "set",
  // Interactive and other elements
  "view",
  "cursor",
  "foreignObject",
  "desc",
  "title",
  "metadata",
  "switch"
], ur = [
  ...Ke,
  ...ar.filter((i) => !Ke.includes(i))
], {
  HtmlTagHydration: lr,
  SvelteComponent: or,
  attr: cr,
  binding_callbacks: pr,
  children: hr,
  claim_element: gr,
  claim_html_tag: dr,
  detach: Je,
  element: fr,
  init: Dr,
  insert_hydration: mr,
  noop: et,
  safe_not_equal: Fr,
  toggle_class: he
} = window.__gradio__svelte__internal, { afterUpdate: br, tick: kr, onMount: qr } = window.__gradio__svelte__internal;
function Er(i) {
  let t, e;
  return {
    c() {
      t = fr("span"), e = new lr(!1), this.h();
    },
    l(n) {
      t = gr(n, "SPAN", { class: !0 });
      var r = hr(t);
      e = dr(r, !1), r.forEach(Je), this.h();
    },
    h() {
      e.a = null, cr(t, "class", "md svelte-1m32c2s"), he(
        t,
        "chatbot",
        /*chatbot*/
        i[0]
      ), he(
        t,
        "prose",
        /*render_markdown*/
        i[1]
      );
    },
    m(n, r) {
      mr(n, t, r), e.m(
        /*html*/
        i[3],
        t
      ), i[11](t);
    },
    p(n, [r]) {
      r & /*html*/
      8 && e.p(
        /*html*/
        n[3]
      ), r & /*chatbot*/
      1 && he(
        t,
        "chatbot",
        /*chatbot*/
        n[0]
      ), r & /*render_markdown*/
      2 && he(
        t,
        "prose",
        /*render_markdown*/
        n[1]
      );
    },
    i: et,
    o: et,
    d(n) {
      n && Je(t), i[11](null);
    }
  };
}
function tt(i) {
  return i.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
function Ar(i, t, e) {
  var n = this && this.__awaiter || function(p, d, E, f) {
    function A(C) {
      return C instanceof E ? C : new E(function(T) {
        T(C);
      });
    }
    return new (E || (E = Promise))(function(C, T) {
      function Z(P) {
        try {
          W(f.next(P));
        } catch (V) {
          T(V);
        }
      }
      function X(P) {
        try {
          W(f.throw(P));
        } catch (V) {
          T(V);
        }
      }
      function W(P) {
        P.done ? C(P.value) : A(P.value).then(Z, X);
      }
      W((f = f.apply(p, d || [])).next());
    });
  };
  let { chatbot: r = !0 } = t, { message: a } = t, { sanitize_html: s = !0 } = t, { latex_delimiters: u = [] } = t, { render_markdown: l = !0 } = t, { line_breaks: m = !0 } = t, { header_links: D = !1 } = t, { allow_tags: k = !1 } = t, { theme_mode: b = "system" } = t, F, B, w = !1;
  const x = $n({
    header_links: D,
    line_breaks: m,
    latex_delimiters: u || []
  });
  function v(p) {
    return !u || u.length === 0 ? !1 : u.some((d) => p.includes(d.left) && p.includes(d.right));
  }
  function c(p, d) {
    if (d === !0) {
      const E = /<\/?([a-zA-Z][a-zA-Z0-9-]*)([\s>])/g;
      return p.replace(E, (f, A, C) => ur.includes(A.toLowerCase()) ? f : f.replace(/</g, "&lt;").replace(/>/g, "&gt;"));
    }
    if (Array.isArray(d)) {
      const E = d.map((A) => ({
        open: new RegExp(`<(${A})(\\s+[^>]*)?>`, "gi"),
        close: new RegExp(`</(${A})>`, "gi")
      }));
      let f = p;
      return E.forEach((A) => {
        f = f.replace(A.open, (C) => C.replace(/</g, "&lt;").replace(/>/g, "&gt;")), f = f.replace(A.close, (C) => C.replace(/</g, "&lt;").replace(/>/g, "&gt;"));
      }), f;
    }
    return p;
  }
  function o(p) {
    let d = p;
    if (l) {
      const E = [];
      u.forEach((f, A) => {
        const C = tt(f.left), T = tt(f.right), Z = new RegExp(`${C}([\\s\\S]+?)${T}`, "g");
        d = d.replace(Z, (X, W) => (E.push(X), `%%%LATEX_BLOCK_${E.length - 1}%%%`));
      }), d = x.parse(d), d = d.replace(/%%%LATEX_BLOCK_(\d+)%%%/g, (f, A) => E[parseInt(A, 10)]);
    }
    return k && (d = c(d, k)), s && Qe && (d = Qe(d)), d;
  }
  function h(p) {
    return n(this, void 0, void 0, function* () {
      if (u.length > 0 && p && v(p))
        if (!w)
          yield Promise.all([
            Promise.resolve({              }),
            import("./auto-render-BwaQGe8P.js")
          ]).then(([, { default: d }]) => {
            w = !0, d(F, {
              delimiters: u,
              throwOnError: !1
            });
          });
        else {
          const { default: d } = yield import("./auto-render-BwaQGe8P.js");
          d(F, {
            delimiters: u,
            throwOnError: !1
          });
        }
      if (F) {
        const d = F.querySelectorAll(".mermaid");
        if (d.length > 0) {
          yield kr();
          const { default: E } = yield import("./mermaid.core-KthD0Gaq.js").then((f) => f.bC);
          E.initialize({
            startOnLoad: !1,
            theme: b === "dark" ? "dark" : "default",
            securityLevel: "antiscript"
          }), yield E.run({
            nodes: Array.from(d).map((f) => f)
          });
        }
      }
    });
  }
  br(() => n(void 0, void 0, void 0, function* () {
    F && document.body.contains(F) ? yield h(a) : console.error("Element is not in the DOM");
  }));
  function g(p) {
    pr[p ? "unshift" : "push"](() => {
      F = p, e(2, F);
    });
  }
  return i.$$set = (p) => {
    "chatbot" in p && e(0, r = p.chatbot), "message" in p && e(4, a = p.message), "sanitize_html" in p && e(5, s = p.sanitize_html), "latex_delimiters" in p && e(6, u = p.latex_delimiters), "render_markdown" in p && e(1, l = p.render_markdown), "line_breaks" in p && e(7, m = p.line_breaks), "header_links" in p && e(8, D = p.header_links), "allow_tags" in p && e(9, k = p.allow_tags), "theme_mode" in p && e(10, b = p.theme_mode);
  }, i.$$.update = () => {
    i.$$.dirty & /*message*/
    16 && (a && a.trim() ? e(3, B = o(a)) : e(3, B = ""));
  }, [
    r,
    l,
    F,
    B,
    a,
    s,
    u,
    m,
    D,
    k,
    b,
    g
  ];
}
class wr extends or {
  constructor(t) {
    super(), Dr(this, t, Ar, Er, Fr, {
      chatbot: 0,
      message: 4,
      sanitize_html: 5,
      latex_delimiters: 6,
      render_markdown: 1,
      line_breaks: 7,
      header_links: 8,
      allow_tags: 9,
      theme_mode: 10
    });
  }
}
const {
  SvelteComponent: xr,
  attr: Cr,
  children: yr,
  claim_component: _r,
  claim_element: vr,
  create_component: Sr,
  destroy_component: Br,
  detach: nt,
  element: Tr,
  init: Rr,
  insert_hydration: Lr,
  mount_component: Ir,
  safe_not_equal: $r,
  toggle_class: Q,
  transition_in: zr,
  transition_out: Or
} = window.__gradio__svelte__internal;
function Mr(i) {
  let t, e, n;
  return e = new wr({
    props: {
      message: rt(
        /*value*/
        i[0]
      ),
      latex_delimiters: (
        /*latex_delimiters*/
        i[5]
      ),
      sanitize_html: (
        /*sanitize_html*/
        i[3]
      ),
      line_breaks: (
        /*line_breaks*/
        i[4]
      ),
      chatbot: !1
    }
  }), {
    c() {
      t = Tr("div"), Sr(e.$$.fragment), this.h();
    },
    l(r) {
      t = vr(r, "DIV", { class: !0 });
      var a = yr(t);
      _r(e.$$.fragment, a), a.forEach(nt), this.h();
    },
    h() {
      Cr(t, "class", "prose svelte-1gecy8w"), Q(
        t,
        "table",
        /*type*/
        i[1] === "table"
      ), Q(
        t,
        "gallery",
        /*type*/
        i[1] === "gallery"
      ), Q(
        t,
        "selected",
        /*selected*/
        i[2]
      );
    },
    m(r, a) {
      Lr(r, t, a), Ir(e, t, null), n = !0;
    },
    p(r, [a]) {
      const s = {};
      a & /*value*/
      1 && (s.message = rt(
        /*value*/
        r[0]
      )), a & /*latex_delimiters*/
      32 && (s.latex_delimiters = /*latex_delimiters*/
      r[5]), a & /*sanitize_html*/
      8 && (s.sanitize_html = /*sanitize_html*/
      r[3]), a & /*line_breaks*/
      16 && (s.line_breaks = /*line_breaks*/
      r[4]), e.$set(s), (!n || a & /*type*/
      2) && Q(
        t,
        "table",
        /*type*/
        r[1] === "table"
      ), (!n || a & /*type*/
      2) && Q(
        t,
        "gallery",
        /*type*/
        r[1] === "gallery"
      ), (!n || a & /*selected*/
      4) && Q(
        t,
        "selected",
        /*selected*/
        r[2]
      );
    },
    i(r) {
      n || (zr(e.$$.fragment, r), n = !0);
    },
    o(r) {
      Or(e.$$.fragment, r), n = !1;
    },
    d(r) {
      r && nt(t), Br(e);
    }
  };
}
function rt(i, t = 60) {
  if (!i) return "";
  const e = String(i);
  return e.length <= t ? e : e.slice(0, t) + "...";
}
function Pr(i, t, e) {
  let { value: n } = t, { type: r } = t, { selected: a = !1 } = t, { sanitize_html: s } = t, { line_breaks: u } = t, { latex_delimiters: l } = t;
  return i.$$set = (m) => {
    "value" in m && e(0, n = m.value), "type" in m && e(1, r = m.type), "selected" in m && e(2, a = m.selected), "sanitize_html" in m && e(3, s = m.sanitize_html), "line_breaks" in m && e(4, u = m.line_breaks), "latex_delimiters" in m && e(5, l = m.latex_delimiters);
  }, [n, r, a, s, u, l];
}
class Gr extends xr {
  constructor(t) {
    super(), Rr(this, t, Pr, Mr, $r, {
      value: 0,
      type: 1,
      selected: 2,
      sanitize_html: 3,
      line_breaks: 4,
      latex_delimiters: 5
    });
  }
}
export {
  Gr as E,
  We as c,
  Hr as g
};
