"""Scroll story chapters rendered inside Streamlit's isolated HTML component."""

import streamlit.components.v1 as components


def show_chapter_one():
    """Render the hook and its loop icon; later chapters will join this scroll container."""
    components.html(
        """
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <style>
            /* WHY tokens live together: the story follows the same restricted palette and geometry. */
            :root {
              --white: #FFFFFF; --pink: #FF69B4; --teal: #069494; --cyan: #00F0FF;
              --ink: #1F2937; --pale-cyan: #E6FDFF; --pale-pink: #FFF0F7;
              --pale-teal: #E8F7F7; --card-radius: 18px; --control-radius: 16px;
              --border-pink: #FF69B477; --border-teal: #06949466;
              --duration-fast: 220ms; --duration-base: 420ms; --duration-reduced: .01ms;
              --duration-word-stagger: 60ms; --duration-word-spring: 560ms;
              --duration-arrow-draw: 700ms; --duration-loop-rotation: 18000ms;
              --duration-cue: 1400ms;
              --glow-pink: 0 8px 26px #FF69B435; --glow-cyan: 0 8px 26px #00F0FF35;
            }
            * { box-sizing: border-box; }
            html, body { width: 100%; height: 100%; margin: 0; color: var(--ink); background: var(--white); }
            body { overflow: hidden; font-family: Inter, ui-sans-serif, system-ui, -apple-system, sans-serif; }
            .story-scroll { width: 100%; height: 100vh; overflow-y: auto; overscroll-behavior: contain; scrollbar-color: var(--teal) var(--pale-cyan); background: linear-gradient(155deg, var(--white) 25%, var(--pale-cyan)); }
            .chapter { position: relative; height: 210vh; min-height: 980px; background: radial-gradient(ellipse at 50% 48%, var(--white) 0, var(--pale-cyan) 78%); }
            .hero { position: sticky; top: 0; display: flex; min-height: 100vh; flex-direction: column; align-items: center; justify-content: center; padding: 48px clamp(22px, 7vw, 90px); text-align: center; }
            .chapter-label { display: inline-flex; align-items: center; gap: 10px; color: var(--teal); font-size: 12px; font-weight: 800; letter-spacing: .15em; text-transform: uppercase; }
            .chapter-number { display: grid; width: 32px; height: 32px; place-items: center; border: 1px solid var(--border-teal); border-radius: 50%; background: var(--white); box-shadow: var(--glow-cyan); letter-spacing: 0; }
            h1 { max-width: 980px; margin: 24px 0 0; font-size: clamp(38px, 7vw, 76px); font-weight: 700; line-height: 1.08; letter-spacing: -.045em; text-wrap: balance; }
            .word { display: inline-block; overflow: hidden; vertical-align: bottom; }
            .word > span { display: inline-block; will-change: transform, opacity; }
            .loop-wrap { display: grid; width: 84px; height: 84px; place-items: center; margin-top: 40px; border: 1px solid var(--border-pink); border-radius: 50%; background: var(--white); box-shadow: var(--glow-pink); }
            .loop-mark { width: 42px; height: 42px; overflow: visible; }
            .loop-mark path { fill: none; stroke: var(--pink); stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round; }
            .scroll-cue { display: flex; align-items: center; gap: 9px; margin-top: 24px; color: var(--teal); font-size: 12px; letter-spacing: .06em; }
            .scroll-cue:before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: var(--cyan); box-shadow: var(--glow-cyan); }
            @media (max-width: 560px) { .chapter { min-height: 820px; } h1 { font-size: clamp(36px, 10vw, 52px); } .loop-wrap { width: 72px; height: 72px; margin-top: 30px; } }
            @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: var(--duration-reduced) !important; animation-iteration-count: 1 !important; scroll-behavior: auto !important; } }
          </style>
        </head>
        <body>
          <main class="story-scroll" id="story-scroll">
            <section class="chapter" id="chapter-one">
              <div class="hero">
                <div class="chapter-label"><span class="chapter-number">01</span> THE LOOP · BRE'S STORY</div>
                <h1 id="hook">Every support call starts with: 'Can you explain the problem again?'</h1>
                <div class="loop-wrap" id="loop-wrap" aria-label="A circular arrow, showing the repeated support loop">
                  <svg class="loop-mark" viewBox="0 0 48 48" role="img" aria-hidden="true">
                    <path id="loop-path" d="M37 18A15 15 0 0 0 10 15L7 19m0 0 1-8m-1 8 8-1M11 30a15 15 0 0 0 27 3l3-4m0 0-1 8m1-8-8 1" />
                  </svg>
                </div>
                <div class="scroll-cue">Scroll to follow Bre's story</div>
              </div>
            </section>
          </main>
          <script src="https://cdn.jsdelivr.net/npm/animejs@4/dist/bundles/anime.umd.min.js"></script>
          <script>
            // WHY keep static content as the fallback: animation and the CDN are optional to the story.
            try {
              const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
              if (!reducedMotion && window.anime) {
                const { animate, stagger, onScroll, splitText, spring, svg } = anime;
                const container = document.querySelector('#story-scroll');
                const { words } = splitText('#hook', { words: { wrap: 'clip' } });
                animate(words, {
                  y: [24, 0], opacity: [0, 1], delay: stagger(Number.parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--duration-word-stagger'))),
                  ease: spring({ bounce: 0.18, duration: Number.parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--duration-word-spring')) }),
                  autoplay: onScroll({ container, target: '#hook' })
                });

                // WHY draw the arrow with the v4 SVG helper: its growing stroke makes the loop symbol legible.
                const [drawable] = svg.createDrawable('#loop-path');
                animate(drawable, {
                  draw: ['0 0', '0 1'], duration: Number.parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--duration-arrow-draw')),
                  autoplay: onScroll({ container, target: '#loop-wrap' })
                });
                // WHY rotate the outer icon slowly: the loop remains noticeable without distracting from the hook.
                animate('.loop-mark', { rotate: 360, duration: Number.parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--duration-loop-rotation')), loop: true, ease: 'linear' });
              }
            } catch (error) {
              // WHY restore any split spans if setup fails partway: the headline must remain fully readable.
              document.querySelector('#hook').style.opacity = '1';
              document.querySelectorAll('#hook span').forEach(word => {
                word.style.transform = 'none';
                word.style.opacity = '1';
              });
              const arrow = document.querySelector('#loop-path');
              arrow.style.strokeDasharray = 'none';
              arrow.style.strokeDashoffset = '0';
            }
          </script>
        </body>
        </html>
        """,
        height=680,
        scrolling=False,
    )
