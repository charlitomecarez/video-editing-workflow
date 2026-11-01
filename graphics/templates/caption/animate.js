// Pop the caption in, then give the highlighted word a small extra punch.
const t = document.getElementById("t"),
  w = document.createElement("div");
t.parentNode.insertBefore(w, t);
w.appendChild(t);
pop(w, 0);
tl.fromTo(
  ".hl",
  { scale: 1 },
  { scale: 1.16, duration: 0.09, yoyo: true, repeat: 1, ease: "power1.out" },
  0.2,
);
