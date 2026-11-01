// Teams slide in, scores count up, the loser dims, the photo slowly zooms.
const bg = document.querySelector(".bg");
if (bg) tl.fromTo(bg, { scale: 1.12 }, { scale: 1, duration: D, ease: "power1.out" }, 0);
tl.fromTo(
  ".tag",
  { y: -50, opacity: 0 },
  { y: 0, opacity: 1, duration: 0.25, ease: "back.out(2)" },
  0,
)
  .fromTo(
    "#L",
    { x: -500, opacity: 0 },
    { x: 0, opacity: 1, duration: 0.3, ease: "power3.out" },
    0.05,
  )
  .fromTo(
    "#R",
    { x: 500, opacity: 0 },
    { x: 0, opacity: 1, duration: 0.3, ease: "power3.out" },
    0.05,
  )
  .fromTo("#vs", { scale: 0 }, { scale: 1, duration: 0.25, ease: "back.out(3)" }, 0.3);
counters(".score", 0.3, 0.8);
tl.fromTo(".lose .score", { opacity: 1 }, { opacity: 0.45, duration: 0.25 }, 1.15)
  .fromTo(
    ".team:not(.lose) .score",
    { scale: 1 },
    { scale: 1.1, duration: 0.12, yoyo: true, repeat: 1 },
    1.1,
  )
  .fromTo(
    ".sub",
    { y: 40, opacity: 0 },
    { y: 0, opacity: 1, duration: 0.25, ease: "power2.out" },
    0.45,
  );
