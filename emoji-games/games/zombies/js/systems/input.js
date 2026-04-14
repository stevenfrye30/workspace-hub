const Input = {
  keys: {},
  mouse: { x: 0, y: 0, down: false, clicked: false },
  justPressed: new Set(),
};

function initInput(stage) {
  document.addEventListener("keydown", e => {
    const k = e.key.toLowerCase();
    if (!Input.keys[k]) Input.justPressed.add(k);
    Input.keys[k] = true;
    if (k === " " || k === "tab") e.preventDefault();
  });
  document.addEventListener("keyup", e => {
    Input.keys[e.key.toLowerCase()] = false;
  });
  const crosshair = document.getElementById("crosshair");
  stage.addEventListener("mousemove", e => {
    const r = stage.getBoundingClientRect();
    Input.mouse.x = e.clientX - r.left;
    Input.mouse.y = e.clientY - r.top;
    if (crosshair) {
      crosshair.style.left = Input.mouse.x + "px";
      crosshair.style.top = Input.mouse.y + "px";
    }
  });
  stage.addEventListener("mousedown", e => {
    Input.mouse.down = true;
    Input.mouse.clicked = true;
  });
  stage.addEventListener("mouseup", () => { Input.mouse.down = false; });
  stage.addEventListener("contextmenu", e => e.preventDefault());
}

function consumeJustPressed(key) {
  if (Input.justPressed.has(key)) { Input.justPressed.delete(key); return true; }
  return false;
}

function resetFrameInput() {
  Input.mouse.clicked = false;
  Input.justPressed.clear();
}
