/* Atlas — registry-driven shell.
   Fetches atlas/registry.json and renders the featured worlds into the
   page's nav and grid. Exposes small building blocks on window.Atlas so
   later world pages can reuse them. */

(function () {
  "use strict";

  // Resolve registry.json as a sibling of this script, so any page that
  // includes atlas.js loads the correct file regardless of its own URL depth.
  var REGISTRY_PATH = new URL("registry.json", document.currentScript.src).href;

  // Atlas root = the directory one level above this script. atlas.js always
  // lives at <root>/atlas/atlas.js, so ".." resolves to <root>/ on any host.
  // Used to turn registry atlas_path values (e.g. "/archive") into absolute
  // URLs that work under GitHub Pages subpath deploys as well as root deploys.
  var ATLAS_ROOT = new URL("..", document.currentScript.src).href;

  function resolvePath(p) {
    if (!p) return "#";
    return ATLAS_ROOT + String(p).replace(/^\/+/, "");
  }

  function fetchRegistry() {
    return fetch(REGISTRY_PATH, { cache: "no-cache" }).then(function (res) {
      if (!res.ok) throw new Error("Registry load failed: " + res.status);
      return res.json();
    });
  }

  function featuredWorlds(registry) {
    return registry.entries.filter(function (e) {
      return e.category === "world" && e.visibility === "featured";
    });
  }

  // Minimal markdown renderer — covers what Atlas opening views use today:
  // frontmatter, # / ## / ### headings, paragraphs, and inline **bold**,
  // *italic*, `code`, [text](url). Upgrade when a world needs more.
  function renderMarkdown(md) {
    var body = String(md).replace(/^---[\s\S]*?---\s*/, "");
    var blocks = body.split(/\n\s*\n/);
    return blocks.map(function (block) {
      block = block.trim();
      if (!block) return "";
      var h = block.match(/^(#{1,6})\s+(.*)$/);
      if (h) {
        var level = h[1].length;
        return "<h" + level + ">" + renderInline(h[2]) + "</h" + level + ">";
      }
      return "<p>" + renderInline(block.replace(/\n/g, " ")) + "</p>";
    }).filter(Boolean).join("\n");
  }

  function renderInline(text) {
    text = escapeHtml(text);
    text = text.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g,
      '<a href="$2">$1</a>');
    text = text.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    text = text.replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, "$1<em>$2</em>");
    text = text.replace(/`([^`]+)`/g, "<code>$1</code>");
    return text;
  }

  function escapeHtml(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return (
        c === "&" ? "&amp;" :
        c === "<" ? "&lt;"  :
        c === ">" ? "&gt;"  :
        c === '"' ? "&quot;" :
        "&#39;"
      );
    });
  }

  function navLink(world) {
    return (
      '<li><a href="' + escapeHtml(resolvePath(world.atlas_path)) + '">' +
      escapeHtml(world.title || "") +
      "</a></li>"
    );
  }

  function worldCard(world) {
    return (
      '<a class="world-card" href="' + escapeHtml(resolvePath(world.atlas_path)) + '">' +
      '<h3 class="world-card__title">' + escapeHtml(world.title || "") + "</h3>" +
      '<p class="world-card__summary">' + escapeHtml(world.summary || "") + "</p>" +
      "</a>"
    );
  }

  function renderNav(el, worlds) {
    if (!el) return;
    el.innerHTML = worlds.map(navLink).join("");
  }

  function renderGrid(el, worlds) {
    if (!el) return;
    el.innerHTML = worlds.map(worldCard).join("");
  }

  function init() {
    var navEl = document.getElementById("worlds-nav");
    var gridEl = document.getElementById("world-grid");

    fetchRegistry()
      .then(function (registry) {
        var worlds = featuredWorlds(registry);
        renderNav(navEl, worlds);
        renderGrid(gridEl, worlds);
      })
      .catch(function (err) {
        console.error("Atlas: failed to load registry", err);
        if (gridEl) {
          gridEl.innerHTML =
            '<p class="atlas-error">Atlas is being prepared.</p>';
        }
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window.Atlas = {
    fetchRegistry: fetchRegistry,
    featuredWorlds: featuredWorlds,
    worldCard: worldCard,
    navLink: navLink,
    renderNav: renderNav,
    renderGrid: renderGrid,
    renderMarkdown: renderMarkdown
  };
})();
