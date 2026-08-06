function calculateSurplus() {
  const income = parseFloat(document.getElementById('income').value) || 0;
  const expense = parseFloat(document.getElementById('expense').value) || 0;
  const result = income - expense;

  let suggestion = "";
  if (result < 0) {
    suggestion = "You are in a deficit. Consider reducing non-essential expenses.";
  } else if (result > 0) {
    suggestion = "You are in surplus. Consider saving or investing the extra amount.";
  } else {
    suggestion = "You are breaking even. Keep monitoring your spending.";
  }
  sessionStorage.setItem("suggestion", suggestion);

  sessionStorage.setItem('income', income);
  sessionStorage.setItem('expense', expense);

  const summary = document.getElementById('summary');
  if (result > 0) {
    summary.textContent = `You have a surplus of $${result}`;
    summary.style.color = "green";
  } else if (result < 0) {
    summary.textContent = `You have a deficit of $${Math.abs(result)}`;
    summary.style.color = "red";
  } else {
    summary.textContent = "Your budget is balanced.";
    summary.style.color = "black";
  }
}

function analyze() {
  window.location.href = "/analysis";
}

function generateColors(count) {
  const colors = [];
  for (let i = 0; i < count; i++) {
    const r = Math.floor(Math.random() * 200);
    const g = Math.floor(Math.random() * 200);
    const b = Math.floor(Math.random() * 200);
    colors.push(`rgba(${r}, ${g}, ${b}, 0.7)`);
  }
  return colors;
}


class CustomChart {
  constructor(canvasId, type, data, colors = null) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext("2d");

    this.type = type;              // "pie" or "bar"
    this.data = data;              // [{ label, amount }]
    this.colors = (colors && colors.length)
      ? colors
      : [ "#e6194b", // red
          "#3cb44b", // green
          "#ffe119", // yellow
          "#4363d8", // blue
          "#f58231", // orange
          "#911eb4", // purple
          "#46f0f0", // light blue
          "#f032e6", // dark pink
          "#bcf60c", // light green
          "#fabebe"  // pink
        ];

    this.slices = [];
    this.bars = [];
    this.tooltip = null;

    // Hover handlers
    this.canvas.addEventListener("mousemove", (e) => this.handleHover(e));
    this.canvas.addEventListener("mouseout", () => { this.tooltip = null; this.draw(1); });

    // Starts with a full draw - no animation to keep hover geometry consistent
    this.draw(1);
  }

  draw(progress = 1) {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    if (this.type === "pie") this.drawPie(progress);
    if (this.type === "bar") this.drawBar(progress);

    if (this.tooltip) this.drawTooltip(this.tooltip);
  }

  getPieGeometry() {
    // Keeps reserved legend column on the right
    const legendWidth = 160;
    const pad = 12;

    const availW = Math.max(50, this.canvas.width - legendWidth - pad * 2);
    const availH = Math.max(50, this.canvas.height - pad * 2);

    const radius = Math.max(
      10,
      Math.min(availW, availH) / 2 - 10
    );

    const cx = pad + availW / 2;
    const cy = this.canvas.height / 2;

    return { cx, cy, radius, legendWidth, pad };
  }

  drawLegend() {
    const ctx = this.ctx;
    const { legendWidth, pad } = this.getPieGeometry();

    const startX = this.canvas.width - legendWidth + pad;
    const colWidth = (legendWidth - pad * 2) / 2; // auto-wrap into two columns if tall
    const lineH = 20;
    const maxRows = Math.max(1, Math.floor((this.canvas.height - pad * 2) / lineH));

    ctx.save();
    ctx.font = "14px Arial";
    ctx.textBaseline = "middle";

    let row = 0, col = 0;
    for (let i = 0; i < this.data.length; i++) {
      const x = startX + col * colWidth;
      const y = pad + row * lineH;

      ctx.fillStyle = this.colors[i % this.colors.length];
      ctx.fillRect(x, y - 6, 12, 12);

      ctx.fillStyle = "#000";
      ctx.fillText(this.data[i].label, x + 18, y);

      row++;
      if (row >= maxRows) { row = 0; col++; }
    }
    ctx.restore();
  }

  // pie 
  drawPie(progress) {
    const ctx = this.ctx;
    const total = Math.max(1e-9, this.data.reduce((s, d) => s + d.amount, 0));
    const { cx, cy, radius } = this.getPieGeometry();

    this.slices = [];
    let start = 0;

    for (let i = 0; i < this.data.length; i++) {
      const item = this.data[i];
      const sliceAngle = (item.amount / total) * 2 * Math.PI * progress;
      const end = start + sliceAngle;

      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.arc(cx, cy, radius, start, end);
      ctx.closePath();
      ctx.fillStyle = this.colors[i % this.colors.length];
      ctx.fill();

      this.slices.push({ start, end, label: item.label, value: item.amount });
      start = end;
    }

    this.drawLegend();
  }

  // bar
  drawBar(progress) {
    const ctx = this.ctx;
    const h = this.canvas.height;
    const w = this.canvas.width;

    const leftPad = 45;
    const rightPad = 20;
    const bottomPad = 40;
    const topPad = 20;

    const maxVal = Math.max(1e-9, Math.max(...this.data.map(d => d.amount)));
    const plotW = w - leftPad - rightPad;
    const plotH = h - topPad - bottomPad;

    const gap = 16;
    const barWidth = Math.max(8, (plotW / this.data.length) - gap);

    // axes
    ctx.save();
    ctx.strokeStyle = "#333";
    ctx.lineWidth = 1;
    // X
    ctx.beginPath();
    ctx.moveTo(leftPad, h - bottomPad + 0.5);
    ctx.lineTo(w - rightPad, h - bottomPad + 0.5);
    ctx.stroke();
    // Y
    ctx.beginPath();
    ctx.moveTo(leftPad + 0.5, topPad);
    ctx.lineTo(leftPad + 0.5, h - bottomPad);
    ctx.stroke();
    ctx.restore();

    // bars
    this.bars = [];
    let x = leftPad + gap / 2;

    for (let i = 0; i < this.data.length; i++) {
      const item = this.data[i];
      const barH = (item.amount / maxVal) * plotH * progress;
      const y = h - bottomPad - barH; // sits exactly on the x-axis

      ctx.fillStyle = this.colors[i % this.colors.length];
      ctx.fillRect(x, y, barWidth, barH);

      this.bars.push({ x, y, w: barWidth, h: barH, label: item.label, value: item.amount });
      x += barWidth + gap;
    }
  }

  // hover + tooltip 
  handleHover(event) {
    const rect = this.canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    let hovered = null;

    if (this.type === "pie") {
      const { cx, cy, radius } = this.getPieGeometry();
      const dx = x - cx, dy = y - cy;
      const dist = Math.hypot(dx, dy);

      if (dist <= radius) {
        let angle = Math.atan2(dy, dx);
        if (angle < 0) angle += 2 * Math.PI;

        // find slice by angle
        for (const s of this.slices) {
          if (angle >= s.start && angle < s.end) { hovered = s; break; }
        }
      }
    } else if (this.type === "bar") {
      hovered = this.bars.find(b => x >= b.x && x <= b.x + b.w && y >= b.y && y <= b.y + b.h) || null;
    }

    this.tooltip = hovered ? { x, y, text: `${hovered.label}: $${hovered.value}` } : null;
    this.draw(1);
  }

  
  drawTooltip({ x, y, text }) {
    const ctx = this.ctx;
    ctx.save();
    ctx.font = "16px Arial";
    ctx.textBaseline = "middle";

    const padding = 8;
    const textW = ctx.measureText(text).width;
    const boxW = textW + padding * 2;
    const boxH = 26;

    let bx = x + 12;
    let by = y - boxH - 8;

    // keep on-canvas
    if (bx + boxW > this.canvas.width - 4) bx = this.canvas.width - boxW - 4;
    if (by < 4) by = y + 12;

    ctx.fillStyle = "rgba(0,0,0,0.78)";
    ctx.fillRect(bx, by, boxW, boxH);

    ctx.fillStyle = "#fff";
    ctx.fillText(text, bx + padding, by + boxH / 2);
    ctx.restore();
  }
}


document.querySelectorAll('.nav-center a').forEach(link => {
  if (link.href === window.location.href) {
    link.classList.add('active');
  }
});


/* View Password */
function togglePassword(fieldId) {
  const input = document.getElementById(fieldId);
  const icon = document.getElementById('eye-icon-' + fieldId);
  if (input.type === 'password') {
    input.type = 'text';
    icon.innerHTML = `
      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
      <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
      <line x1="1" y1="1" x2="23" y2="23"/>`;
  } else {
    input.type = 'password';
    icon.innerHTML = `
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
      <circle cx="12" cy="12" r="3"/>`;
  }
}