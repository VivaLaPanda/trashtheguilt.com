// Open a collapsed section when a link points into it.
function reveal(id) {
  const target = id && document.getElementById(id);
  if (!target) return;
  for (let d = target.closest("details"); d; d = d.parentElement.closest("details")) d.open = true;
  if (target.tagName === "DETAILS") target.open = true;
}

// Open first, then jump, so the browser can scroll to a target that was hidden.
document.addEventListener("click", (e) => {
  const a = e.target.closest('a[href^="#"]');
  if (!a) return;
  const id = a.getAttribute("href").slice(1);
  const target = id && document.getElementById(id);
  if (!target || !target.closest("details:not([open])")) return;
  e.preventDefault();
  reveal(id);
  if (location.hash === "#" + id) target.scrollIntoView({ block: "center" });
  else location.hash = id;
});
reveal(location.hash.slice(1));

// Share buttons: native share sheet where available, else copy the link.
const status = document.querySelector(".share .status");
for (const b of document.querySelectorAll(".share button")) {
  b.addEventListener("click", async () => {
    const url = b.dataset.url;
    if (navigator.share) {
      try {
        await navigator.share({ url, text: b.dataset.text });
        return;
      } catch (err) {
        if (err.name === "AbortError") return;
      }
    }
    try {
      await navigator.clipboard.writeText(url);
      status.textContent = "Link copied: " + url;
    } catch {
      status.textContent = url;
    }
  });
}
