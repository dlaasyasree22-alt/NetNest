"""Phase 1: Cinematic Intro Component for NetNest Streamlit Demo.
5-Scene scroll and time-driven animated presentation.
"""

import streamlit as st
import streamlit.components.v1 as components

def render_cinematic_intro():
    intro_html = """
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>NetNest - What If Support Remembered?</title>
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Space+Grotesk:wght@600;700;800&display=swap" rel="stylesheet">
      <style>
        :root {
          --bg-dark: #0B0B1A;
          --violet: #7C3AED;
          --pink: #FF2E93;
          --cyan: #00E5FF;
          --lime: #B6FF3B;
          --orange: #FF8A00;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        html, body {
          width: 100%; height: 100%;
          background: #0B0B1A;
          color: #FFFFFF;
          font-family: 'Inter', sans-serif;
          overflow: hidden;
        }

        /* Container & Timeline Stage */
        .stage-container {
          position: relative;
          width: 100vw;
          height: 100vh;
          display: grid;
          place-items: center;
          background: radial-gradient(circle at 50% 40%, #1A0B36 0%, #0B0B1A 75%, #05040F 100%);
        }

        .scene {
          position: absolute;
          inset: 0;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 40px 24px;
          text-align: center;
          opacity: 0;
          pointer-events: none;
          transition: opacity 800ms cubic-bezier(0.16, 1, 0.3, 1), transform 800ms cubic-bezier(0.16, 1, 0.3, 1);
          transform: translateY(20px) scale(0.98);
        }

        .scene.active {
          opacity: 1;
          pointer-events: auto;
          transform: translateY(0) scale(1);
        }

        h1.scene-title {
          font-family: 'Space Grotesk', sans-serif;
          font-size: clamp(32px, 5.5vw, 64px);
          font-weight: 800;
          line-height: 1.15;
          letter-spacing: -0.03em;
          max-width: 900px;
          margin-bottom: 24px;
          background: linear-gradient(135deg, #FFFFFF 30%, #A5B4FC 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }

        .highlight-pink {
          background: linear-gradient(135deg, #FF2E93, #FF8A00);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }

        .highlight-cyan {
          background: linear-gradient(135deg, #00E5FF, #B6FF3B);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }

        /* Scene 1: Agent Increment Counter */
        .agent-counter-box {
          display: flex;
          align-items: center;
          gap: 20px;
          margin-top: 30px;
          padding: 16px 28px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.15);
          border-radius: 50px;
          backdrop-filter: blur(12px);
        }
        .avatar-ring {
          width: 52px; height: 52px;
          border-radius: 50%;
          border: 2px solid var(--cyan);
          display: grid; place-items: center;
          font-weight: 800;
          font-size: 20px;
          box-shadow: 0 0 20px rgba(0, 229, 255, 0.4);
        }
        .counter-number {
          font-family: 'Space Grotesk', sans-serif;
          font-size: 28px;
          font-weight: 800;
          color: var(--pink);
        }

        /* Scene 2: Stacking Speech Bubbles & Frustration Gauge */
        .bubble-stack-container {
          position: relative;
          width: 100%;
          max-width: 540px;
          height: 220px;
          margin-top: 20px;
          overflow: hidden;
        }
        .repeat-bubble {
          position: absolute;
          left: 50%;
          transform: translateX(-50%);
          width: 90%;
          padding: 14px 20px;
          background: rgba(255, 46, 147, 0.15);
          border: 1px solid rgba(255, 46, 147, 0.4);
          border-radius: 18px;
          font-size: 15px;
          font-weight: 600;
          color: #FFD1E6;
          box-shadow: 0 8px 24px rgba(0,0,0,0.4);
          animation: stackSlideIn 400ms cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
        }

        .frustration-bar-wrapper {
          width: 320px;
          height: 12px;
          background: rgba(255,255,255,0.1);
          border-radius: 10px;
          margin-top: 24px;
          overflow: hidden;
          position: relative;
        }
        .frustration-bar-fill {
          height: 100%;
          width: 0%;
          background: linear-gradient(90deg, #B6FF3B 0%, #FFD700 50%, #FF2E93 100%);
          border-radius: 10px;
          transition: width 400ms ease;
        }

        /* Scene 3: Glitching Modem & Wi-Fi */
        .modem-box {
          width: 180px;
          height: 110px;
          background: #120E2E;
          border: 2px solid rgba(255, 255, 255, 0.2);
          border-radius: 16px;
          margin-top: 24px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 12px;
          box-shadow: 0 0 30px rgba(124, 61, 237, 0.3);
        }
        .led-row {
          display: flex;
          gap: 14px;
        }
        .led-dot {
          width: 14px;
          height: 14px;
          border-radius: 50%;
          background: #334155;
        }
        .led-dot.blink-red {
          background: #FF2E93;
          box-shadow: 0 0 14px #FF2E93;
          animation: glitchBlink 600ms infinite alternate;
        }
        .led-dot.blink-orange {
          background: #FF8A00;
          box-shadow: 0 0 14px #FF8A00;
          animation: glitchBlink 900ms infinite alternate;
        }

        /* Scene 4: Particle Logo Morph */
        #particle-logo-canvas {
          width: 280px;
          height: 160px;
          margin-top: 20px;
        }

        /* Scene 5: Gooey Morph CTA Button */
        .cta-morph-btn {
          margin-top: 32px;
          padding: 18px 42px;
          font-family: 'Space Grotesk', sans-serif;
          font-size: 18px;
          font-weight: 700;
          color: #0B0B1A;
          background: linear-gradient(135deg, var(--cyan), var(--lime));
          border: none;
          border-radius: 50px;
          cursor: pointer;
          box-shadow: 0 0 35px rgba(0, 229, 255, 0.6);
          transition: all 300ms cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        .cta-morph-btn:hover {
          transform: scale(1.08) translateY(-2px);
          box-shadow: 0 0 50px rgba(0, 229, 255, 0.9);
        }

        /* Progress Dots & Navigation Controls */
        .timeline-controls {
          position: absolute;
          bottom: 30px;
          left: 50%;
          transform: translateX(-50%);
          display: flex;
          align-items: center;
          gap: 12px;
          z-index: 10;
        }
        .dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background: rgba(255, 255, 255, 0.2);
          cursor: pointer;
          transition: all 300ms ease;
        }
        .dot.active {
          width: 28px;
          border-radius: 20px;
          background: var(--cyan);
          box-shadow: 0 0 12px var(--cyan);
        }

        @keyframes glitchBlink {
          0% { opacity: 0.2; transform: scale(0.9); }
          100% { opacity: 1; transform: scale(1.1); }
        }
        @keyframes stackSlideIn {
          0% { opacity: 0; transform: translate(-50%, -20px) scale(0.9); }
          100% { opacity: 1; transform: translate(-50%, 0) scale(1); }
        }
      </style>
    </head>
    <body>
      <div class="stage-container">
        <!-- SCENE 1 -->
        <div class="scene active" id="scene-1">
          <h1 class="scene-title">Every time you call support...</h1>
          <p style="color: #94A3B8; font-size: 18px; max-width: 550px;">You get connected to someone completely new who knows zero context.</p>
          <div class="agent-counter-box">
            <div class="avatar-ring">👤</div>
            <div>
              <div style="font-size: 12px; color: #94A3B8; letter-spacing: 0.1em;">CONNECTING TO</div>
              <div class="counter-number" id="agent-counter">Agent #1</div>
            </div>
          </div>
        </div>

        <!-- SCENE 2 -->
        <div class="scene" id="scene-2">
          <h1 class="scene-title">Speech bubbles stack. <span class="highlight-pink">Frustration overflows.</span></h1>
          <div class="bubble-stack-container" id="bubble-stack"></div>
          <div class="frustration-bar-wrapper">
            <div class="frustration-bar-fill" id="frustration-fill"></div>
          </div>
        </div>

        <!-- SCENE 3 -->
        <div class="scene" id="scene-3">
          <h1 class="scene-title">You explain it again. <span class="highlight-pink">And again.</span></h1>
          <div class="modem-box">
            <div style="font-size: 12px; color: #94A3B8; letter-spacing: 0.1em;">MODEM STATUS</div>
            <div class="led-row">
              <div class="led-dot blink-red"></div>
              <div class="led-dot blink-orange"></div>
              <div class="led-dot blink-red"></div>
            </div>
          </div>
        </div>

        <!-- SCENE 4 -->
        <div class="scene" id="scene-4">
          <h1 class="scene-title">What if support <span class="highlight-cyan">remembered?</span></h1>
          <canvas id="particle-logo-canvas"></canvas>
        </div>

        <!-- SCENE 5 -->
        <div class="scene" id="scene-5">
          <h1 class="scene-title">Experience <span class="highlight-cyan">NetNest</span> Hindsight Memory</h1>
          <p style="color: #94A3B8; font-size: 18px; max-width: 580px;">Zero repeated steps. Instant context recall. Automatic human handoff.</p>
          <button class="cta-morph-btn" onclick="finishIntro()">See it in action ↗</button>
        </div>

        <!-- Controls -->
        <div class="timeline-controls">
          <div class="dot active" onclick="goToScene(0)"></div>
          <div class="dot" onclick="goToScene(1)"></div>
          <div class="dot" onclick="goToScene(2)"></div>
          <div class="dot" onclick="goToScene(3)"></div>
          <div class="dot" onclick="goToScene(4)"></div>
        </div>
      </div>

      <script>
        let currentScene = 0;
        const totalScenes = 5;
        const sceneDuration = 3600; // ms per scene
        let timer = null;

        const scenes = document.querySelectorAll('.scene');
        const dots = document.querySelectorAll('.dot');

        function goToScene(index) {
          scenes.forEach((s, i) => {
            s.classList.toggle('active', i === index);
            dots[i].classList.toggle('active', i === index);
          });
          currentScene = index;

          if (index === 0) runScene1();
          if (index === 1) runScene2();
          if (index === 3) runScene4();
        }

        function nextScene() {
          if (currentScene < totalScenes - 1) {
            goToScene(currentScene + 1);
          } else {
            clearInterval(timer);
          }
        }

        // Scene 1: Agent Counter
        function runScene1() {
          let count = 1;
          const counterEl = document.getElementById('agent-counter');
          const interval = setInterval(() => {
            count++;
            counterEl.textContent = `Agent #${count}`;
            if (count >= 5) clearInterval(interval);
          }, 600);
        }

        // Scene 2: Speech Stack & Frustration
        function runScene2() {
          const stack = document.getElementById('bubble-stack');
          const fill = document.getElementById('frustration-fill');
          stack.innerHTML = '';
          fill.style.width = '0%';

          const lines = [
            '"Have you tried restarting your modem?"',
            '"Can you confirm your account number?"',
            '"Let me transfer you to tier 2..."',
            '"Did you un-plug the coaxial cable?"'
          ];

          lines.forEach((text, i) => {
            setTimeout(() => {
              const b = document.createElement('div');
              b.className = 'repeat-bubble';
              b.style.top = `${i * 44}px`;
              b.textContent = text;
              stack.appendChild(b);
              fill.style.width = `${(i + 1) * 25}%`;
            }, i * 700);
          });
        }

        // Scene 4: Canvas Logo Assembly
        function runScene4() {
          const canvas = document.getElementById('particle-logo-canvas');
          if (!canvas) return;
          const ctx = canvas.getContext('2d');
          canvas.width = 280;
          canvas.height = 160;

          let particles = [];
          for (let i = 0; i < 60; i++) {
            particles.push({
              x: Math.random() * canvas.width,
              y: Math.random() * canvas.height,
              targetX: 60 + (i % 10) * 18,
              targetY: 40 + Math.floor(i / 10) * 18,
              vx: (Math.random() - 0.5) * 2,
              vy: (Math.random() - 0.5) * 2,
              color: i % 2 === 0 ? '#00E5FF' : '#7C3AED'
            });
          }

          function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles.forEach(p => {
              p.x += (p.targetX - p.x) * 0.08;
              p.y += (p.targetY - p.y) * 0.08;
              ctx.beginPath();
              ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
              ctx.fillStyle = p.color;
              ctx.shadowColor = p.color;
              ctx.shadowBlur = 10;
              ctx.fill();
            });
            requestAnimationFrame(draw);
          }
          draw();
        }

        function finishIntro() {
          // Send query param to parent window to finish story
          try {
            window.parent.location.search = '?skip_story=1';
          } catch(e) {
            window.location.search = '?skip_story=1';
          }
        }

        // Auto advance scenes
        timer = setInterval(nextScene, sceneDuration);
        runScene1();
      </script>
    </body>
    </html>
    """
    components.html(intro_html, height=720, scrolling=False)
