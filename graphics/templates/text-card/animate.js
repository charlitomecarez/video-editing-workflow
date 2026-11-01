// big: numbers count up and the card pops. chapter: slides in with a small glitch shake.
// placeholder: no animation (it gets replaced anyway).
const v = document.body.className;
if (v.includes("v-big")) {
  counters(".text .hl", 0.05, 0.55);
  pop(".text", 0);
  tl.fromTo(".hl", { scale: 1 }, { scale: 1.12, duration: 0.1, yoyo: true, repeat: 1 }, 0.6);
} else if (v.includes("v-chapter")) {
  tl.fromTo(
    ".text",
    { x: -140, opacity: 0 },
    { x: 0, opacity: 1, duration: 0.22, ease: "power3.out" },
    0,
  )
    .to(".text", { x: 10, duration: 0.03 }, 0.3)
    .to(".text", { x: -8, duration: 0.03 }, 0.33)
    .to(".text", { x: 0, duration: 0.03 }, 0.36);
}
if (document.querySelector(".sub") && !v.includes("v-placeholder"))
  tl.fromTo(
    ".sub",
    { y: 40, opacity: 0 },
    { y: 0, opacity: 0.8, duration: 0.25, ease: "power2.out" },
    0.4,
  );
