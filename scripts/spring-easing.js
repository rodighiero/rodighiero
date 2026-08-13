#!/usr/bin/env node
//
// Generates the CSS linear() easing curves used by _layouts/home.html.
//
//   node scripts/spring-easing.js
//
// A spring is the motion we want for anything that travels to a new place on the page —
// it decelerates into its destination and settles, where a bezier simply stops. Running
// one needs a JS animation library, which computes the curve frame by frame at runtime;
// the libraries that do this on the Web Animations API get there by generating a CSS
// linear() easing from the spring. So we generate it here instead, once, and paste the
// result into the stylesheet: the same shape, as a plain CSS transition, at no weight.
//
// Two variants, because a spring's overshoot is not always available to use:
//
//   underdamped  — overshoots its end value and settles back. Used for the gallery
//                  tiles' transform (damping 0.75, 2.8% overshoot, 420ms), where a tile
//                  can travel a hair past its slot and come back.
//   critical     — approaches from below, never crosses. Used for the bio panel's
//                  grid-template-rows + margin-bottom (400ms): a grid row cannot exceed
//                  1fr, so an overshoot there is clamped on the row but not on the
//                  margin, and the two come apart mid-open.
//
// omega0 is solved from the requested duration rather than chosen, so the spring has
// genuinely settled (residual < 0.2%) by its last sample. A curve still moving when it
// runs out of duration snaps to its final value — the discontinuity these curves exist
// to remove.

// x(t) = 1 - e^(-zeta*w*t) * (cos(wd*t) + (zeta*w/wd) * sin(wd*t))
function underdamped(zeta, duration, points) {
  const w = Math.log(500) / (zeta * duration);
  const wd = w * Math.sqrt(1 - zeta * zeta);
  return sample(
    (t) => 1 - Math.exp(-zeta * w * t) * (Math.cos(wd * t) + ((zeta * w) / wd) * Math.sin(wd * t)),
    duration,
    points
  );
}

// x(t) = 1 - (1 + w*t) * e^(-w*t)
function critical(duration, points) {
  let w = 1;
  while ((1 + w * duration) * Math.exp(-w * duration) >= 0.002) w += 0.25;
  return sample((t) => 1 - (1 + w * t) * Math.exp(-w * t), duration, points);
}

function sample(x, duration, points) {
  const pts = [];
  for (let i = 0; i <= points; i++) {
    const t = (i / points) * duration;
    pts.push(i === points ? 1 : Math.round(x(t) * 1000) / 1000);
  }
  return pts;
}

// Wraps at a comfortable width for pasting into the stylesheet.
function format(pts, indent) {
  const lines = [];
  let line = '';
  for (const p of pts) {
    const next = line ? line + ', ' + p : String(p);
    if (next.length > 84 - indent.length) {
      lines.push(line + ',');
      line = String(p);
    } else {
      line = next;
    }
  }
  lines.push(line);
  return 'linear(' + lines.join('\n' + indent) + ')';
}

const curves = [
  ['gallery tiles — transform 0.42s (underdamped 0.75, 2.8% overshoot)', underdamped(0.75, 0.42, 24)],
  ['bio panel — grid-template-rows/margin-bottom 0.4s (critically damped)', critical(0.4, 20)],
];

for (const [label, pts] of curves) {
  const peak = Math.max(...pts);
  const tail = pts[pts.length - 2];
  console.log(`\n/* ${label} */`);
  console.log(`/* peak ${peak}, last sample before 1: ${tail} */`);
  console.log('  ' + format(pts, '    '));
}
console.log('');
