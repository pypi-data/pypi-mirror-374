// crumble/gates/gate.js
var Gate = class _Gate {
  /**
   * @param {!string} name
   * @param {!int|undefined} num_qubits
   * @param {!boolean} can_fuse
   * @param {!boolean} is_marker
   * @param {!Map<!string, !string>|undefined} tableau_map
   * @param {!function(!PauliFrame, !Array<!int>)} frameDo,
   * @param {!function(!PauliFrame, !Array<!int>)} frameUndo,
   * @param {!gateDrawCallback} drawer
   * @param {undefined|!number=undefined} defaultArgument
   */
  constructor(name, num_qubits, can_fuse, is_marker, tableau_map, frameDo, frameUndo, drawer, defaultArgument = void 0) {
    this.name = name;
    this.num_qubits = num_qubits;
    this.is_marker = is_marker;
    this.can_fuse = can_fuse;
    this.tableau_map = tableau_map;
    this.frameDo = frameDo;
    this.frameUndo = frameUndo;
    this.drawer = drawer;
    this.defaultArgument = defaultArgument;
  }
  /**
   * @param {!number} newDefaultArgument
   */
  withDefaultArgument(newDefaultArgument) {
    return new _Gate(
      this.name,
      this.num_qubits,
      this.can_fuse,
      this.is_marker,
      this.tableau_map,
      this.frameDo,
      this.frameUndo,
      this.drawer,
      newDefaultArgument
    );
  }
};

// crumble/circuit/operation.js
function expandBase(base) {
  let result = [];
  for (let k = 0; k < base.length; k++) {
    let prefix = "I".repeat(k);
    let suffix = "I".repeat(base.length - k - 1);
    if (base[k] === "X" || base[k] === "Y") {
      result.push(prefix + "X" + suffix);
    }
    if (base[k] === "Z" || base[k] === "Y") {
      result.push(prefix + "Z" + suffix);
    }
  }
  return result;
}
var Operation = class {
  /**
   * @param {!Gate} gate
   * @param {!string} tag
   * @param {!Float32Array} args
   * @param {!Uint32Array} targets
   */
  constructor(gate, tag, args, targets) {
    if (!(gate instanceof Gate)) {
      throw new Error(`!(gate instanceof Gate) gate=${gate}`);
    }
    if (!(args instanceof Float32Array)) {
      throw new Error("!(args instanceof Float32Array)");
    }
    if (!(targets instanceof Uint32Array)) {
      throw new Error("!(targets instanceof Uint32Array)");
    }
    this.gate = gate;
    this.tag = tag;
    this.args = args;
    this.id_targets = targets;
  }
  /**
   * @returns {!string}
   */
  toString() {
    return `${this.gate.name}[${this.tag}](${[...this.args].join(", ")}) ${[...this.id_targets].join(" ")}`;
  }
  /**
   * @returns {!int}
   */
  countMeasurements() {
    if (this.gate.name === "M" || this.gate.name === "MX" || this.gate.name === "MY" || this.gate.name === "MR" || this.gate.name === "MRX" || this.gate.name === "MRY") {
      return this.id_targets.length;
    }
    if (this.gate.name === "MXX" || this.gate.name === "MYY" || this.gate.name === "MZZ") {
      return this.id_targets.length / 2;
    }
    if (this.gate.name.startsWith("MPP:")) {
      return 1;
    }
    return 0;
  }
  /**
   * @param {!string} before
   * @returns {!string}
   */
  pauliFrameAfter(before) {
    let m = this.gate.tableau_map;
    if (m === void 0) {
      if (this.gate.name.startsWith("M")) {
        let bases2;
        if (this.gate.name.startsWith("MPP:")) {
          bases2 = this.gate.name.substring(4);
        } else {
          bases2 = this.gate.name.substring(1);
        }
        let differences = 0;
        for (let k = 0; k < before.length; k++) {
          let a = "XYZ".indexOf(before[k]);
          let b = "XYZ".indexOf(bases2[k]);
          if (a >= 0 && b >= 0 && a !== b) {
            differences++;
          }
        }
        if (differences % 2 !== 0) {
          return "ERR:" + before;
        }
        return before;
      } else if (this.gate.name.startsWith("SPP:") || this.gate.name.startsWith("SPP_DAG:")) {
        let dag = this.gate.name.startsWith("SPP_DAG:");
        let bases2 = this.gate.name.substring(dag ? 8 : 4);
        let differences = 0;
        let flipped = "";
        for (let k = 0; k < before.length; k++) {
          let a = "IXYZ".indexOf(before[k]);
          let b = "IXYZ".indexOf(bases2[k]);
          if (a > 0 && b > 0 && a !== b) {
            differences++;
          }
          flipped += "IXYZ"[a ^ b];
        }
        if (differences % 2 !== 0) {
          return flipped;
        }
        return before;
      } else if (this.gate.name === "POLYGON") {
        return before;
      } else {
        throw new Error(this.gate.name);
      }
    }
    if (before.length !== this.gate.num_qubits) {
      throw new Error(`before.length !== this.gate.num_qubits`);
    }
    if (m.has(before)) {
      return m.get(before);
    }
    let bases = expandBase(before);
    bases = bases.map((e) => m.get(e));
    let out = [0, 0];
    for (let b of bases) {
      for (let k = 0; k < before.length; k++) {
        if (b[k] === "X") {
          out[k] ^= 1;
        }
        if (b[k] === "Y") {
          out[k] ^= 3;
        }
        if (b[k] === "Z") {
          out[k] ^= 2;
        }
      }
    }
    let result = "";
    for (let k = 0; k < before.length; k++) {
      result += "IXZY"[out[k]];
    }
    return result;
  }
  /**
   * @param {!function(qubit: !int): ![!number, !number]} qubitCoordsFunc
   * @param {!CanvasRenderingContext2D} ctx
   */
  id_draw(qubitCoordsFunc, ctx) {
    ctx.save();
    try {
      this.gate.drawer(this, qubitCoordsFunc, ctx);
      if (this.tag !== "" && this.id_targets.length > 0) {
        let [x, y] = qubitCoordsFunc(this.id_targets[0]);
        ctx.fillText(this.tag, x, y + 16);
      }
    } finally {
      ctx.restore();
    }
  }
};

// crumble/draw/config.js
var pitch = 50;
var rad = 10;
var OFFSET_X = -pitch + Math.floor(pitch / 4) + 0.5;
var OFFSET_Y = -pitch + Math.floor(pitch / 4) + 0.5;
var indentCircuitLines = true;
var curveConnectors = true;
var setIndentCircuitLines = (newBool) => {
  if (typeof newBool !== "boolean") {
    throw new TypeError(`Expected a boolean, but got ${typeof newBool}`);
  }
  indentCircuitLines = newBool;
};
var setCurveConnectors = (newBool) => {
  if (typeof newBool !== "boolean") {
    throw new TypeError(`Expected a boolean, but got ${typeof newBool}`);
  }
  curveConnectors = newBool;
};

// crumble/gates/gate_draw_util.js
function draw_x_control(ctx, x, y) {
  if (x === void 0 || y === void 0) {
    return;
  }
  ctx.strokeStyle = "black";
  ctx.fillStyle = "white";
  ctx.beginPath();
  ctx.arc(x, y, rad, 0, 2 * Math.PI);
  ctx.fill();
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(x, y - rad);
  ctx.lineTo(x, y + rad);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(x - rad, y);
  ctx.lineTo(x + rad, y);
  ctx.stroke();
}
function draw_y_control(ctx, x, y) {
  if (x === void 0 || y === void 0) {
    return;
  }
  ctx.strokeStyle = "black";
  ctx.fillStyle = "#AAA";
  ctx.beginPath();
  ctx.moveTo(x, y + rad);
  ctx.lineTo(x + rad, y - rad);
  ctx.lineTo(x - rad, y - rad);
  ctx.lineTo(x, y + rad);
  ctx.stroke();
  ctx.fill();
}
function draw_z_control(ctx, x, y) {
  if (x === void 0 || y === void 0) {
    return;
  }
  ctx.fillStyle = "black";
  ctx.beginPath();
  ctx.arc(x, y, rad, 0, 2 * Math.PI);
  ctx.fill();
}
function draw_xswap_control(ctx, x, y) {
  if (x === void 0 || y === void 0) {
    return;
  }
  ctx.fillStyle = "white";
  ctx.strokeStyle = "black";
  ctx.beginPath();
  ctx.arc(x, y, rad, 0, 2 * Math.PI);
  ctx.fill();
  ctx.stroke();
  let r = rad * 0.4;
  ctx.strokeStyle = "black";
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(x - r, y - r);
  ctx.lineTo(x + r, y + r);
  ctx.stroke();
  ctx.moveTo(x - r, y + r);
  ctx.lineTo(x + r, y - r);
  ctx.stroke();
  ctx.lineWidth = 1;
}
function draw_zswap_control(ctx, x, y) {
  if (x === void 0 || y === void 0) {
    return;
  }
  ctx.fillStyle = "black";
  ctx.strokeStyle = "black";
  ctx.beginPath();
  ctx.arc(x, y, rad, 0, 2 * Math.PI);
  ctx.fill();
  ctx.stroke();
  let r = rad * 0.4;
  ctx.strokeStyle = "white";
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(x - r, y - r);
  ctx.lineTo(x + r, y + r);
  ctx.stroke();
  ctx.moveTo(x - r, y + r);
  ctx.lineTo(x + r, y - r);
  ctx.stroke();
  ctx.lineWidth = 1;
}
function draw_iswap_control(ctx, x, y) {
  if (x === void 0 || y === void 0) {
    return;
  }
  ctx.fillStyle = "#888";
  ctx.strokeStyle = "#222";
  ctx.beginPath();
  ctx.arc(x, y, rad, 0, 2 * Math.PI);
  ctx.fill();
  ctx.stroke();
  let r = rad * 0.4;
  ctx.lineWidth = 3;
  ctx.strokeStyle = "black";
  ctx.beginPath();
  ctx.moveTo(x - r, y - r);
  ctx.lineTo(x + r, y + r);
  ctx.stroke();
  ctx.moveTo(x - r, y + r);
  ctx.lineTo(x + r, y - r);
  ctx.stroke();
  ctx.lineWidth = 1;
}
function draw_swap_control(ctx, x, y) {
  if (x === void 0 || y === void 0) {
    return;
  }
  let r = rad / 3;
  ctx.strokeStyle = "black";
  ctx.beginPath();
  ctx.moveTo(x - r, y - r);
  ctx.lineTo(x + r, y + r);
  ctx.stroke();
  ctx.moveTo(x - r, y + r);
  ctx.lineTo(x + r, y - r);
  ctx.stroke();
}
function stroke_degenerate_connector(ctx, x, y) {
  if (x === void 0 || y === void 0) {
    return;
  }
  let r = rad * 1.1;
  ctx.strokeRect(x - r, y - r, r * 2, r * 2);
}
function stroke_connector_to(ctx, x1, y1, x2, y2) {
  if (x1 === void 0 || y1 === void 0 || x2 === void 0 || y2 === void 0) {
    stroke_degenerate_connector(ctx, x1, y1);
    stroke_degenerate_connector(ctx, x2, y2);
    return;
  }
  if (x2 < x1 || x2 === x1 && y2 < y1) {
    stroke_connector_to(ctx, x2, y2, x1, y1);
    return;
  }
  let dx = x2 - x1;
  let dy = y2 - y1;
  let d = Math.sqrt(dx * dx + dy * dy);
  let ux = dx / d * 14;
  let uy = dy / d * 14;
  let px = uy;
  let py = -ux;
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  if (!curveConnectors || d < pitch * 1.1) {
    ctx.lineTo(x2, y2);
  } else {
    ctx.bezierCurveTo(
      x1 + ux + px,
      y1 + uy + py,
      x2 - ux + px,
      y2 - uy + py,
      x2,
      y2
    );
  }
  ctx.stroke();
}
function draw_connector(ctx, x1, y1, x2, y2) {
  ctx.lineWidth = 2;
  ctx.strokeStyle = "black";
  stroke_connector_to(ctx, x1, y1, x2, y2);
  ctx.lineWidth = 1;
}

// crumble/gates/gateset_controlled_paulis.js
function* iter_gates_controlled_paulis() {
  yield new Gate(
    "CX",
    2,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["IX", "IX"],
      ["IZ", "ZZ"],
      ["XI", "XX"],
      ["ZI", "ZI"]
    ]),
    (frame, targets) => frame.do_cx(targets),
    (frame, targets) => frame.do_cx(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      let [x2, y2] = coordFunc(op.id_targets[1]);
      draw_connector(ctx, x1, y1, x2, y2);
      draw_z_control(ctx, x1, y1);
      draw_x_control(ctx, x2, y2);
    }
  );
  yield new Gate(
    "CY",
    2,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["IX", "ZX"],
      ["IZ", "ZZ"],
      ["XI", "XY"],
      ["ZI", "ZI"]
    ]),
    (frame, targets) => frame.do_cy(targets),
    (frame, targets) => frame.do_cy(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      let [x2, y2] = coordFunc(op.id_targets[1]);
      draw_connector(ctx, x1, y1, x2, y2);
      draw_z_control(ctx, x1, y1);
      draw_y_control(ctx, x2, y2);
    }
  );
  yield new Gate(
    "XCX",
    2,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["IX", "IX"],
      ["IZ", "XZ"],
      ["XI", "XI"],
      ["ZI", "ZX"]
    ]),
    (frame, targets) => frame.do_xcx(targets),
    (frame, targets) => frame.do_xcx(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      let [x2, y2] = coordFunc(op.id_targets[1]);
      draw_connector(ctx, x1, y1, x2, y2);
      draw_x_control(ctx, x1, y1);
      draw_x_control(ctx, x2, y2);
    }
  );
  yield new Gate(
    "XCY",
    2,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["IX", "XX"],
      ["IZ", "XZ"],
      ["XI", "XI"],
      ["ZI", "ZY"]
    ]),
    (frame, targets) => frame.do_xcy(targets),
    (frame, targets) => frame.do_xcy(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      let [x2, y2] = coordFunc(op.id_targets[1]);
      draw_connector(ctx, x1, y1, x2, y2);
      draw_x_control(ctx, x1, y1);
      draw_y_control(ctx, x2, y2);
    }
  );
  yield new Gate(
    "YCY",
    2,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["IX", "YX"],
      ["IZ", "YZ"],
      ["XI", "XY"],
      ["ZI", "ZY"]
    ]),
    (frame, targets) => frame.do_ycy(targets),
    (frame, targets) => frame.do_ycy(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      let [x2, y2] = coordFunc(op.id_targets[1]);
      draw_connector(ctx, x1, y1, x2, y2);
      draw_y_control(ctx, x1, y1);
      draw_y_control(ctx, x2, y2);
    }
  );
  yield new Gate(
    "CZ",
    2,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["IX", "ZX"],
      ["IZ", "IZ"],
      ["XI", "XZ"],
      ["ZI", "ZI"]
    ]),
    (frame, targets) => frame.do_cz(targets),
    (frame, targets) => frame.do_cz(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      let [x2, y2] = coordFunc(op.id_targets[1]);
      draw_connector(ctx, x1, y1, x2, y2);
      draw_z_control(ctx, x1, y1);
      draw_z_control(ctx, x2, y2);
    }
  );
}

// crumble/gates/gateset_demolition_measurements.js
function* iter_gates_demolition_measurements() {
  yield new Gate(
    "MR",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "ERR:I"],
      ["Y", "ERR:I"],
      ["Z", "I"]
    ]),
    (frame, targets) => frame.do_demolition_measure("Z", targets),
    (frame, targets) => frame.do_demolition_measure("Z", targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "gray";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("MR", x1, y1);
    }
  );
  yield new Gate(
    "MRY",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "ERR:I"],
      ["Y", "I"],
      ["Z", "ERR:I"]
    ]),
    (frame, targets) => frame.do_demolition_measure("Y", targets),
    (frame, targets) => frame.do_demolition_measure("Y", targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "gray";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("MRY", x1, y1);
    }
  );
  yield new Gate(
    "MRX",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "I"],
      ["Y", "ERR:I"],
      ["Z", "ERR:I"]
    ]),
    (frame, targets) => frame.do_demolition_measure("X", targets),
    (frame, targets) => frame.do_demolition_measure("X", targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "gray";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("MRX", x1, y1);
    }
  );
}

// crumble/gates/gateset_hadamard_likes.js
function* iter_gates_hadamard_likes() {
  yield new Gate(
    "H",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "Z"],
      ["Z", "X"]
    ]),
    (frame, targets) => frame.do_exchange_xz(targets),
    (frame, targets) => frame.do_exchange_xz(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "yellow";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("H", x1, y1);
    }
  );
  yield new Gate(
    "H_NXZ",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "Z"],
      ["Z", "X"]
    ]),
    (frame, targets) => frame.do_exchange_xz(targets),
    (frame, targets) => frame.do_exchange_xz(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "yellow";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("H", x1, y1 - rad / 3);
      ctx.fillText("NXZ", x1, y1 + rad / 3);
    }
  );
  yield new Gate(
    "H_XY",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "Y"],
      ["Z", "Z"]
      // -Z technically
    ]),
    (frame, targets) => frame.do_exchange_xy(targets),
    (frame, targets) => frame.do_exchange_xy(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "yellow";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("H", x1, y1 - rad / 3);
      ctx.fillText("XY", x1, y1 + rad / 3);
    }
  );
  yield new Gate(
    "H_NXY",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "Y"],
      ["Z", "Z"]
    ]),
    (frame, targets) => frame.do_exchange_xy(targets),
    (frame, targets) => frame.do_exchange_xy(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "yellow";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("H", x1, y1 - rad / 3);
      ctx.fillText("NXY", x1, y1 + rad / 3);
    }
  );
  yield new Gate(
    "H_YZ",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "X"],
      // -X technically
      ["Z", "Y"]
    ]),
    (frame, targets) => frame.do_exchange_yz(targets),
    (frame, targets) => frame.do_exchange_yz(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "yellow";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("H", x1, y1 - rad / 3);
      ctx.fillText("YZ", x1, y1 + rad / 3);
    }
  );
  yield new Gate(
    "H_NYZ",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "X"],
      // -X technically
      ["Z", "Y"]
    ]),
    (frame, targets) => frame.do_exchange_yz(targets),
    (frame, targets) => frame.do_exchange_yz(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "yellow";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("H", x1, y1 - rad / 3);
      ctx.fillText("NYZ", x1, y1 + rad / 3);
    }
  );
}

// crumble/draw/draw_util.js
function beginPathPolygon(ctx, coords) {
  ctx.beginPath();
  if (coords.length === 0) {
    return;
  }
  let n = coords.length;
  if (n === 1) {
    let [[x0, y0]] = coords;
    ctx.arc(x0, y0, rad * 1.7, 0, 2 * Math.PI);
  } else if (n === 2) {
    let [[x0, y0], [x1, y1]] = coords;
    let dx = x1 - x0;
    let dy = y1 - y0;
    let cx = (x1 + x0) / 2;
    let cy = (y1 + y0) / 2;
    let px = -dy;
    let py = dx;
    let pa = px * px + py * py;
    if (pa > 50 * 50) {
      let s = 50 / Math.sqrt(pa);
      px *= s;
      py *= s;
    }
    let ac1x = cx + px * 0.2 - dx * 0.2;
    let ac1y = cy + py * 0.2 - dy * 0.2;
    let ac2x = cx + px * 0.2 + dx * 0.2;
    let ac2y = cy + py * 0.2 + dy * 0.2;
    let bc1x = cx - px * 0.2 - dx * 0.2;
    let bc1y = cy - py * 0.2 - dy * 0.2;
    let bc2x = cx - px * 0.2 + dx * 0.2;
    let bc2y = cy - py * 0.2 + dy * 0.2;
    ctx.moveTo(x0, y0);
    ctx.bezierCurveTo(ac1x, ac1y, ac2x, ac2y, x1, y1);
    ctx.bezierCurveTo(bc2x, bc2y, bc1x, bc1y, x0, y0);
  } else {
    let [xn, yn] = coords[n - 1];
    ctx.moveTo(xn, yn);
    for (let k = 0; k < n; k++) {
      let [xk, yk] = coords[k];
      ctx.lineTo(xk, yk);
    }
  }
}

// crumble/gates/gateset_markers.js
function marker_placement(mi, key, hitCount) {
  let dx, dy, wx, wy;
  if (mi < 0 && hitCount !== void 0) {
    let d = hitCount.get(key);
    if (d === void 0) {
      d = 0;
    }
    hitCount.set(key, d + 1);
    dx = 9.5 - Math.round(d % 3.9 * 5);
    dy = 9.5 - Math.round(Math.floor(d / 4) % 3.8 * 5);
    wx = 3;
    wy = 3;
    if (mi < -1 << 28) {
      dx += 2;
      wx += 4;
      dy += 2;
      wy += 4;
    }
  } else if (mi === 0) {
    dx = rad;
    dy = rad + 5;
    wx = rad * 2;
    wy = 5;
  } else if (mi === 1) {
    dx = -rad;
    dy = rad;
    wx = 5;
    wy = rad * 2;
  } else if (mi === 2) {
    dx = rad;
    dy = -rad;
    wx = rad * 2;
    wy = 5;
  } else if (mi === 3) {
    dx = rad + 5;
    dy = rad;
    wx = 5;
    wy = rad * 2;
  } else {
    dx = Math.cos(mi * 0.6) * rad * 1.7;
    dy = Math.sin(mi * 0.6) * rad * 1.7;
    wx = 5;
    wy = 5;
    dx += wx / 2;
    dy += wy / 2;
  }
  return { dx, dy, wx, wy };
}
function make_marker_drawer(color) {
  return (op, coordFunc, ctx) => {
    let [x1, y1] = coordFunc(op.id_targets[0]);
    if (x1 === void 0 || y1 === void 0) {
      return;
    }
    let { dx, dy, wx, wy } = marker_placement(op.args[0]);
    ctx.fillStyle = color;
    if (wx === wy) {
      ctx.fillRect(x1 - dx - 2, y1 - dy - 2, wx + 4, wy + 4);
    } else {
      let x2 = x1 + (dx < 0 ? 1 : -1) * rad;
      let y2 = y1 + (dy < 0 ? 1 : -1) * rad;
      let x3 = x2 + (wx > rad ? 1 : 0) * rad * 2;
      let y3 = y2 + (wy > rad ? 1 : 0) * rad * 2;
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.lineTo(x3, y3);
      ctx.lineTo(x1, y1);
      ctx.fill();
    }
  };
}
function* iter_gates_markers() {
  yield new Gate(
    "POLYGON",
    void 0,
    false,
    true,
    void 0,
    () => {
    },
    () => {
    },
    (op, coordFunc, ctx) => {
      let transformedCoords = [];
      for (let t of op.id_targets) {
        let [x, y] = coordFunc(t);
        x -= 0.5;
        y -= 0.5;
        transformedCoords.push([x, y]);
      }
      beginPathPolygon(ctx, transformedCoords);
      ctx.globalAlpha *= op.args[3];
      ctx.fillStyle = `rgb(${op.args[0] * 255},${op.args[1] * 255},${op.args[2] * 255})`;
      ctx.fill();
    }
  );
  yield new Gate(
    "DETECTOR",
    void 0,
    false,
    true,
    void 0,
    () => {
    },
    () => {
    },
    (op, coordFunc, ctx) => {
    }
  );
  yield new Gate(
    "OBSERVABLE_INCLUDE",
    void 0,
    false,
    true,
    void 0,
    () => {
    },
    () => {
    },
    (op, coordFunc, ctx) => {
    }
  );
  yield new Gate(
    "MARKX",
    1,
    true,
    true,
    void 0,
    () => {
    },
    () => {
    },
    make_marker_drawer("red")
  );
  yield new Gate(
    "MARKY",
    1,
    true,
    true,
    void 0,
    () => {
    },
    () => {
    },
    make_marker_drawer("green")
  );
  yield new Gate(
    "MARKZ",
    1,
    true,
    true,
    void 0,
    () => {
    },
    () => {
    },
    make_marker_drawer("blue")
  );
  yield new Gate(
    "MARK",
    1,
    false,
    true,
    void 0,
    () => {
    },
    () => {
    },
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      if (x1 === void 0 || y1 === void 0) {
        return;
      }
      ctx.fillStyle = "magenta";
      ctx.fillRect(x1 - rad, y1 - rad, rad, rad);
    }
  );
}

// crumble/gates/gateset_pair_measurements.js
function* iter_gates_pair_measurements() {
  yield new Gate(
    "MXX",
    2,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["II", "II"],
      ["IX", "IX"],
      ["IY", "ERR:IY"],
      ["IZ", "ERR:IZ"],
      ["XI", "XI"],
      ["XX", "XX"],
      ["XY", "ERR:XY"],
      ["XZ", "ERR:XZ"],
      ["YI", "ERR:YI"],
      ["YX", "ERR:YX"],
      ["YY", "YY"],
      ["YZ", "YZ"],
      ["ZI", "ERR:ZI"],
      ["ZX", "ERR:ZX"],
      ["ZY", "ZY"],
      ["ZZ", "ZZ"]
    ]),
    (frame, targets) => frame.do_measure("XX", targets),
    (frame, targets) => frame.do_measure("XX", targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      let [x2, y2] = coordFunc(op.id_targets[1]);
      draw_connector(ctx, x1, y1, x2, y2);
      ctx.fillStyle = "gray";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillRect(x2 - rad, y2 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeRect(x2 - rad, y2 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("MXX", x1, y1);
      ctx.fillText("MXX", x2, y2);
    }
  );
  yield new Gate(
    "MYY",
    2,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["II", "II"],
      ["IX", "ERR:IX"],
      ["IY", "IY"],
      ["IZ", "ERR:IZ"],
      ["XI", "ERR:XI"],
      ["XX", "XX"],
      ["XY", "ERR:XY"],
      ["XZ", "XZ"],
      ["YI", "YI"],
      ["YX", "ERR:YX"],
      ["YY", "YY"],
      ["YZ", "ERR:YZ"],
      ["ZI", "ERR:ZI"],
      ["ZX", "ZX"],
      ["ZY", "ERR:ZY"],
      ["ZZ", "ZZ"]
    ]),
    (frame, targets) => frame.do_measure("YY", targets),
    (frame, targets) => frame.do_measure("YY", targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      let [x2, y2] = coordFunc(op.id_targets[1]);
      draw_connector(ctx, x1, y1, x2, y2);
      ctx.fillStyle = "gray";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillRect(x2 - rad, y2 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeRect(x2 - rad, y2 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("MYY", x1, y1);
      ctx.fillText("MYY", x2, y2);
    }
  );
  yield new Gate(
    "MZZ",
    2,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["II", "II"],
      ["IX", "ERR:IX"],
      ["IY", "ERR:IY"],
      ["IZ", "IZ"],
      ["XI", "ERR:XI"],
      ["XX", "XX"],
      ["XY", "XY"],
      ["XZ", "ERR:XZ"],
      ["YI", "ERR:YI"],
      ["YX", "YX"],
      ["YY", "YY"],
      ["YZ", "ERR:YZ"],
      ["ZI", "ZI"],
      ["ZX", "ERR:ZX"],
      ["ZY", "ERR:ZY"],
      ["ZZ", "ZZ"]
    ]),
    (frame, targets) => frame.do_measure("ZZ", targets),
    (frame, targets) => frame.do_measure("ZZ", targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      let [x2, y2] = coordFunc(op.id_targets[1]);
      draw_connector(ctx, x1, y1, x2, y2);
      ctx.fillStyle = "gray";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillRect(x2 - rad, y2 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeRect(x2 - rad, y2 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("MZZ", x1, y1);
      ctx.fillText("MZZ", x2, y2);
    }
  );
}

// crumble/gates/gateset_paulis.js
function* iter_gates_paulis() {
  yield new Gate(
    "ERR",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "X"],
      ["Z", "Z"]
    ]),
    () => {
    },
    () => {
    },
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "red";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("ERR", x1, y1);
    }
  );
  yield new Gate(
    "I",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "X"],
      ["Z", "Z"]
    ]),
    () => {
    },
    () => {
    },
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "white";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("I", x1, y1);
    }
  );
  yield new Gate(
    "X",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "X"],
      ["Z", "Z"]
    ]),
    () => {
    },
    () => {
    },
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "white";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("X", x1, y1);
    }
  );
  yield new Gate(
    "Y",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "X"],
      ["Z", "Z"]
    ]),
    () => {
    },
    () => {
    },
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "white";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("Y", x1, y1);
    }
  );
  yield new Gate(
    "Z",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "X"],
      ["Z", "Z"]
    ]),
    () => {
    },
    () => {
    },
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "white";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("Z", x1, y1);
    }
  );
}

// crumble/gates/gateset_quarter_turns.js
function* iter_gates_quarter_turns() {
  yield new Gate(
    "S",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "Y"],
      ["Z", "Z"]
    ]),
    (frame, targets) => frame.do_exchange_xy(targets),
    (frame, targets) => frame.do_exchange_xy(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "yellow";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("S", x1, y1);
    }
  );
  yield new Gate(
    "S_DAG",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "Y"],
      ["Z", "Z"]
    ]),
    (frame, targets) => frame.do_exchange_xy(targets),
    (frame, targets) => frame.do_exchange_xy(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "yellow";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("S\u2020", x1, y1);
    }
  );
  yield new Gate(
    "SQRT_X",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "X"],
      ["Z", "Y"]
    ]),
    (frame, targets) => frame.do_exchange_yz(targets),
    (frame, targets) => frame.do_exchange_yz(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "yellow";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("\u221AX", x1, y1);
    }
  );
  yield new Gate(
    "SQRT_X_DAG",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "X"],
      ["Z", "Y"]
    ]),
    (frame, targets) => frame.do_exchange_yz(targets),
    (frame, targets) => frame.do_exchange_yz(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "yellow";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("\u221AX\u2020", x1, y1);
    }
  );
  yield new Gate(
    "SQRT_Y",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "Z"],
      ["Z", "X"]
    ]),
    (frame, targets) => frame.do_exchange_xz(targets),
    (frame, targets) => frame.do_exchange_xz(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "yellow";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("\u221AY", x1, y1);
    }
  );
  yield new Gate(
    "SQRT_Y_DAG",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "Z"],
      ["Z", "X"]
    ]),
    (frame, targets) => frame.do_exchange_xz(targets),
    (frame, targets) => frame.do_exchange_xz(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "yellow";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("\u221AY\u2020", x1, y1);
    }
  );
}

// crumble/gates/gateset_resets.js
function* iter_gates_resets() {
  yield new Gate(
    "R",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "ERR:I"],
      ["Y", "ERR:I"],
      ["Z", "ERR:I"]
    ]),
    (frame, targets) => frame.do_discard(targets),
    (frame, targets) => frame.do_demolition_measure("Z", targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "gray";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("R", x1, y1);
    }
  );
  yield new Gate(
    "RX",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "ERR:I"],
      ["Y", "ERR:I"],
      ["Z", "ERR:I"]
    ]),
    (frame, targets) => frame.do_discard(targets),
    (frame, targets) => frame.do_demolition_measure("X", targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "gray";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("RX", x1, y1);
    }
  );
  yield new Gate(
    "RY",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "ERR:I"],
      ["Y", "ERR:I"],
      ["Z", "ERR:I"]
    ]),
    (frame, targets) => frame.do_discard(targets),
    (frame, targets) => frame.do_demolition_measure("Y", targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "gray";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("RY", x1, y1);
    }
  );
}

// crumble/gates/gateset_solo_measurements.js
function* iter_gates_solo_measurements() {
  yield new Gate(
    "M",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "ERR:X"],
      ["Y", "ERR:Y"],
      ["Z", "Z"]
    ]),
    (frame, targets) => frame.do_measure("Z", targets),
    (frame, targets) => frame.do_measure("Z", targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "gray";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("M", x1, y1);
      ctx.textAlign = "left";
    }
  );
  yield new Gate(
    "MX",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "X"],
      ["Y", "ERR:Y"],
      ["Z", "ERR:Z"]
    ]),
    (frame, targets) => frame.do_measure("X", targets),
    (frame, targets) => frame.do_measure("X", targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "gray";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("MX", x1, y1);
      ctx.textAlign = "left";
    }
  );
  yield new Gate(
    "MY",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "ERR:X"],
      ["Y", "Y"],
      ["Z", "ERR:Z"]
    ]),
    (frame, targets) => frame.do_measure("Y", targets),
    (frame, targets) => frame.do_measure("Y", targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "gray";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("MY", x1, y1);
      ctx.textAlign = "left";
    }
  );
}

// crumble/gates/gateset_sqrt_pauli_pairs.js
function* iter_gates_sqrt_pauli_pairs() {
  yield new Gate(
    "II",
    2,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["IX", "IX"],
      ["IZ", "IZ"],
      ["XI", "XI"],
      ["ZI", "ZI"]
    ]),
    (frame, targets) => void 0,
    (frame, targets) => void 0,
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      let [x2, y2] = coordFunc(op.id_targets[1]);
      draw_connector(ctx, x1, y1, x2, y2);
      for (let [x, y] of [
        [x1, y1],
        [x2, y2]
      ]) {
        ctx.fillStyle = "white";
        ctx.fillRect(x - rad, y - rad, rad * 2, rad * 2);
        ctx.strokeStyle = "black";
        ctx.strokeRect(x - rad, y - rad, rad * 2, rad * 2);
        ctx.fillStyle = "black";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("II", x, y);
      }
    }
  );
  yield new Gate(
    "SQRT_XX",
    2,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["IX", "IX"],
      ["IZ", "XY"],
      ["XI", "XI"],
      ["ZI", "YX"]
    ]),
    (frame, targets) => frame.do_sqrt_xx(targets),
    (frame, targets) => frame.do_sqrt_xx(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      let [x2, y2] = coordFunc(op.id_targets[1]);
      draw_connector(ctx, x1, y1, x2, y2);
      for (let [x, y] of [
        [x1, y1],
        [x2, y2]
      ]) {
        ctx.fillStyle = "yellow";
        ctx.fillRect(x - rad, y - rad, rad * 2, rad * 2);
        ctx.strokeStyle = "black";
        ctx.strokeRect(x - rad, y - rad, rad * 2, rad * 2);
        ctx.fillStyle = "black";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("\u221AXX", x, y);
      }
    }
  );
  yield new Gate(
    "SQRT_XX_DAG",
    2,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["IX", "IX"],
      ["IZ", "XY"],
      ["XI", "XI"],
      ["ZI", "YX"]
    ]),
    (frame, targets) => frame.do_sqrt_xx(targets),
    (frame, targets) => frame.do_sqrt_xx(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      let [x2, y2] = coordFunc(op.id_targets[1]);
      draw_connector(ctx, x1, y1, x2, y2);
      for (let [x, y] of [
        [x1, y1],
        [x2, y2]
      ]) {
        ctx.fillStyle = "yellow";
        ctx.fillRect(x - rad, y - rad, rad * 2, rad * 2);
        ctx.strokeStyle = "black";
        ctx.strokeRect(x - rad, y - rad, rad * 2, rad * 2);
        ctx.fillStyle = "black";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("\u221AXX\u2020", x, y);
      }
    }
  );
  yield new Gate(
    "SQRT_YY",
    2,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["IX", "YZ"],
      ["IZ", "YX"],
      ["XI", "ZY"],
      ["ZI", "XY"]
    ]),
    (frame, targets) => frame.do_sqrt_yy(targets),
    (frame, targets) => frame.do_sqrt_yy(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      let [x2, y2] = coordFunc(op.id_targets[1]);
      draw_connector(ctx, x1, y1, x2, y2);
      for (let [x, y] of [
        [x1, y1],
        [x2, y2]
      ]) {
        ctx.fillStyle = "yellow";
        ctx.fillRect(x - rad, y - rad, rad * 2, rad * 2);
        ctx.strokeStyle = "black";
        ctx.strokeRect(x - rad, y - rad, rad * 2, rad * 2);
        ctx.fillStyle = "black";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("\u221AYY", x, y);
      }
    }
  );
  yield new Gate(
    "SQRT_YY_DAG",
    2,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["IX", "YZ"],
      ["IZ", "YX"],
      ["XI", "ZY"],
      ["ZI", "XY"]
    ]),
    (frame, targets) => frame.do_sqrt_yy(targets),
    (frame, targets) => frame.do_sqrt_yy(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      let [x2, y2] = coordFunc(op.id_targets[1]);
      draw_connector(ctx, x1, y1, x2, y2);
      for (let [x, y] of [
        [x1, y1],
        [x2, y2]
      ]) {
        ctx.fillStyle = "yellow";
        ctx.fillRect(x - rad, y - rad, rad * 2, rad * 2);
        ctx.strokeStyle = "black";
        ctx.strokeRect(x - rad, y - rad, rad * 2, rad * 2);
        ctx.fillStyle = "black";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("\u221AYY\u2020", x, y);
      }
    }
  );
  yield new Gate(
    "SQRT_ZZ",
    2,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["IX", "ZY"],
      ["IZ", "IZ"],
      ["XI", "YZ"],
      ["ZI", "ZI"]
    ]),
    (frame, targets) => frame.do_sqrt_zz(targets),
    (frame, targets) => frame.do_sqrt_zz(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      let [x2, y2] = coordFunc(op.id_targets[1]);
      draw_connector(ctx, x1, y1, x2, y2);
      for (let [x, y] of [
        [x1, y1],
        [x2, y2]
      ]) {
        ctx.fillStyle = "yellow";
        ctx.fillRect(x - rad, y - rad, rad * 2, rad * 2);
        ctx.strokeStyle = "black";
        ctx.strokeRect(x - rad, y - rad, rad * 2, rad * 2);
        ctx.fillStyle = "black";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("\u221AZZ", x, y);
      }
    }
  );
  yield new Gate(
    "SQRT_ZZ_DAG",
    2,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["IX", "ZY"],
      ["IZ", "IZ"],
      ["XI", "YZ"],
      ["ZI", "ZI"]
    ]),
    (frame, targets) => frame.do_sqrt_zz(targets),
    (frame, targets) => frame.do_sqrt_zz(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      let [x2, y2] = coordFunc(op.id_targets[1]);
      draw_connector(ctx, x1, y1, x2, y2);
      for (let [x, y] of [
        [x1, y1],
        [x2, y2]
      ]) {
        ctx.fillStyle = "yellow";
        ctx.fillRect(x - rad, y - rad, rad * 2, rad * 2);
        ctx.strokeStyle = "black";
        ctx.strokeRect(x - rad, y - rad, rad * 2, rad * 2);
        ctx.fillStyle = "black";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("\u221AZZ\u2020", x, y);
      }
    }
  );
}

// crumble/gates/gateset_swaps.js
function* iter_gates_swaps() {
  yield new Gate(
    "ISWAP",
    2,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["IX", "YZ"],
      ["IZ", "ZI"],
      ["XI", "ZY"],
      ["ZI", "IZ"]
    ]),
    (frame, targets) => frame.do_iswap(targets),
    (frame, targets) => frame.do_iswap(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      let [x2, y2] = coordFunc(op.id_targets[1]);
      draw_connector(ctx, x1, y1, x2, y2);
      draw_iswap_control(ctx, x1, y1);
      draw_iswap_control(ctx, x2, y2);
    }
  );
  yield new Gate(
    "ISWAP_DAG",
    2,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["IX", "YZ"],
      ["IZ", "ZI"],
      ["XI", "ZY"],
      ["ZI", "IZ"]
    ]),
    (frame, targets) => frame.do_iswap(targets),
    (frame, targets) => frame.do_iswap(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      let [x2, y2] = coordFunc(op.id_targets[1]);
      draw_connector(ctx, x1, y1, x2, y2);
      draw_iswap_control(ctx, x1, y1);
      draw_iswap_control(ctx, x2, y2);
    }
  );
  yield new Gate(
    "SWAP",
    2,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["IX", "XI"],
      ["IZ", "ZI"],
      ["XI", "IX"],
      ["ZI", "IZ"]
    ]),
    (frame, targets) => frame.do_swap(targets),
    (frame, targets) => frame.do_swap(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      let [x2, y2] = coordFunc(op.id_targets[1]);
      draw_connector(ctx, x1, y1, x2, y2);
      draw_swap_control(ctx, x1, y1);
      draw_swap_control(ctx, x2, y2);
    }
  );
  yield new Gate(
    "CXSWAP",
    2,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["IX", "XI"],
      ["IZ", "ZZ"],
      ["XI", "XX"],
      ["ZI", "IZ"]
    ]),
    (frame, targets) => frame.do_cx_swap(targets),
    (frame, targets) => frame.do_swap_cx(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      let [x2, y2] = coordFunc(op.id_targets[1]);
      draw_connector(ctx, x1, y1, x2, y2);
      draw_zswap_control(ctx, x1, y1);
      draw_xswap_control(ctx, x2, y2);
    }
  );
  yield new Gate(
    "CZSWAP",
    2,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["IX", "XZ"],
      ["IZ", "ZI"],
      ["XI", "ZX"],
      ["ZI", "IZ"]
    ]),
    (frame, targets) => frame.do_cz_swap(targets),
    (frame, targets) => frame.do_cz_swap(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      let [x2, y2] = coordFunc(op.id_targets[1]);
      draw_connector(ctx, x1, y1, x2, y2);
      draw_zswap_control(ctx, x1, y1);
      draw_zswap_control(ctx, x2, y2);
    }
  );
}

// crumble/gates/gateset_third_turns.js
function* iter_gates_third_turns() {
  yield new Gate(
    "C_XYZ",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "Y"],
      ["Z", "X"]
    ]),
    (frame, targets) => frame.do_cycle_xyz(targets),
    (frame, targets) => frame.do_cycle_zyx(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "teal";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("C", x1, y1 - rad / 3);
      ctx.fillText("XYZ", x1, y1 + rad / 3);
    }
  );
  yield new Gate(
    "C_NXYZ",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "Y"],
      ["Z", "X"]
    ]),
    (frame, targets) => frame.do_cycle_xyz(targets),
    (frame, targets) => frame.do_cycle_zyx(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "teal";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("C", x1, y1 - rad / 3);
      ctx.fillText("NXYZ", x1, y1 + rad / 3);
    }
  );
  yield new Gate(
    "C_XNYZ",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "Y"],
      ["Z", "X"]
    ]),
    (frame, targets) => frame.do_cycle_xyz(targets),
    (frame, targets) => frame.do_cycle_zyx(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "teal";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("C", x1, y1 - rad / 3);
      ctx.fillText("XNYZ", x1, y1 + rad / 3);
    }
  );
  yield new Gate(
    "C_XYNZ",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "Y"],
      ["Z", "X"]
    ]),
    (frame, targets) => frame.do_cycle_xyz(targets),
    (frame, targets) => frame.do_cycle_zyx(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "teal";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("C", x1, y1 - rad / 3);
      ctx.fillText("XYNZ", x1, y1 + rad / 3);
    }
  );
  yield new Gate(
    "C_ZYX",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "Z"],
      ["Z", "Y"]
    ]),
    (frame, targets) => frame.do_cycle_zyx(targets),
    (frame, targets) => frame.do_cycle_xyz(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "teal";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("C", x1, y1 - rad / 3);
      ctx.fillText("ZYX", x1, y1 + rad / 3);
    }
  );
  yield new Gate(
    "C_ZYNX",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "Z"],
      ["Z", "Y"]
    ]),
    (frame, targets) => frame.do_cycle_zyx(targets),
    (frame, targets) => frame.do_cycle_xyz(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "teal";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("C", x1, y1 - rad / 3);
      ctx.fillText("ZYNX", x1, y1 + rad / 3);
    }
  );
  yield new Gate(
    "C_ZNYX",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "Z"],
      ["Z", "Y"]
    ]),
    (frame, targets) => frame.do_cycle_zyx(targets),
    (frame, targets) => frame.do_cycle_xyz(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "teal";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("C", x1, y1 - rad / 3);
      ctx.fillText("ZNYX", x1, y1 + rad / 3);
    }
  );
  yield new Gate(
    "C_NZYX",
    1,
    true,
    false,
    /* @__PURE__ */ new Map([
      ["X", "Z"],
      ["Z", "Y"]
    ]),
    (frame, targets) => frame.do_cycle_zyx(targets),
    (frame, targets) => frame.do_cycle_xyz(targets),
    (op, coordFunc, ctx) => {
      let [x1, y1] = coordFunc(op.id_targets[0]);
      ctx.fillStyle = "teal";
      ctx.fillRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.fillStyle = "black";
      ctx.strokeStyle = "black";
      ctx.strokeRect(x1 - rad, y1 - rad, rad * 2, rad * 2);
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("C", x1, y1 - rad / 3);
      ctx.fillText("NZYX", x1, y1 + rad / 3);
    }
  );
}

// crumble/gates/gateset.js
function* iter_gates() {
  yield* iter_gates_controlled_paulis();
  yield* iter_gates_demolition_measurements();
  yield* iter_gates_hadamard_likes();
  yield* iter_gates_markers();
  yield* iter_gates_pair_measurements();
  yield* iter_gates_paulis();
  yield* iter_gates_quarter_turns();
  yield* iter_gates_resets();
  yield* iter_gates_solo_measurements();
  yield* iter_gates_sqrt_pauli_pairs();
  yield* iter_gates_swaps();
  yield* iter_gates_third_turns();
}
function make_gate_map() {
  let result = /* @__PURE__ */ new Map();
  for (let gate of iter_gates()) {
    result.set(gate.name, gate);
  }
  result.set("MZ", result.get("M"));
  result.set("RZ", result.get("R"));
  result.set("MRZ", result.get("MR"));
  return result;
}
function make_gate_alias_map() {
  let result = /* @__PURE__ */ new Map();
  result.set("CNOT", { name: "CX" });
  result.set("MZ", { name: "M" });
  result.set("MRZ", { name: "MR" });
  result.set("RZ", { name: "R" });
  result.set("H_XZ", { name: "H" });
  result.set("SQRT_Z", { name: "S" });
  result.set("SQRT_Z_DAG", { name: "S_DAG" });
  result.set("ZCX", { name: "CX" });
  result.set("ZCY", { name: "CY" });
  result.set("ZCZ", { name: "CZ" });
  result.set("SWAPCZ", { name: "CZSWAP" });
  result.set("XCZ", { name: "CX", rev_pair: true });
  result.set("YCX", { name: "XCY", rev_pair: true });
  result.set("YCZ", { name: "CY", rev_pair: true });
  result.set("SWAPCX", { name: "CXSWAP", rev_pair: true });
  result.set("CORRELATED_ERROR", { ignore: true });
  result.set("DEPOLARIZE1", { ignore: true });
  result.set("DEPOLARIZE2", { ignore: true });
  result.set("E", { ignore: true });
  result.set("ELSE_CORRELATED_ERROR", { ignore: true });
  result.set("PAULI_CHANNEL_1", { ignore: true });
  result.set("PAULI_CHANNEL_2", { ignore: true });
  result.set("X_ERROR", { ignore: true });
  result.set("I_ERROR", { ignore: true });
  result.set("II_ERROR", { ignore: true });
  result.set("Y_ERROR", { ignore: true });
  result.set("Z_ERROR", { ignore: true });
  result.set("HERALDED_ERASE", { ignore: true });
  result.set("HERALDED_PAULI_CHANNEL_1", { ignore: true });
  result.set("MPAD", { ignore: true });
  result.set("SHIFT_COORDS", { ignore: true });
  return result;
}
var GATE_MAP = (
  /** @type {Map<!string, !Gate>} */
  make_gate_map()
);
var GATE_ALIAS_MAP = (
  /** @type {!Map<!string, !{name: undefined|!string, rev_pair: undefined|!boolean, ignore: undefined|!boolean}>} */
  make_gate_alias_map()
);

// crumble/base/seq.js
function groupBy(items, func) {
  let result = /* @__PURE__ */ new Map();
  for (let item of items) {
    let key = func(item);
    let group = result.get(key);
    if (group === void 0) {
      result.set(key, [item]);
    } else {
      group.push(item);
    }
  }
  return result;
}

// crumble/circuit/layer.js
var Layer = class _Layer {
  constructor() {
    this.id_ops = /** @type {!Map<!int, !Operation>} */
    /* @__PURE__ */ new Map();
    this.markers = [];
  }
  /**
   * @returns {!string}
   */
  toString() {
    let result = "Layer {\n";
    result += "    id_ops {\n";
    for (let [key, val] of this.id_ops.entries()) {
      result += `        ${key}: ${val}
`;
    }
    result += "    }\n";
    result += "    markers {\n";
    for (let val of this.markers) {
      result += `        ${val}
`;
    }
    result += "    }\n";
    result += "}";
    return result;
  }
  /**
   * @returns {Map<!string, !Array<!Operation>>}
   */
  opsGroupedByNameWithArgs() {
    let opsByName = groupBy(this.iter_gates_and_markers(), (op) => {
      let key = op.gate.name;
      if (key.startsWith("MPP:") && !GATE_MAP.has(key)) {
        key = "MPP";
      }
      if (key.startsWith("SPP:") && !GATE_MAP.has(key)) {
        key = "SPP";
      }
      if (key.startsWith("SPP_DAG:") && !GATE_MAP.has(key)) {
        key = "SPP_DAG";
      }
      if (op.tag !== "") {
        key += "[" + op.tag.replace("\\", "\\B").replace("\r", "\\r").replace("\n", "\\n").replace("]", "\\C") + "]";
      }
      if (op.args.length > 0) {
        key += "(" + [...op.args].join(",") + ")";
      }
      return key;
    });
    let namesWithArgs = [...opsByName.keys()];
    namesWithArgs.sort((a, b) => {
      let ma = a.startsWith("MARK") || a.startsWith("POLY");
      let mb = b.startsWith("MARK") || b.startsWith("POLY");
      if (ma !== mb) {
        return ma < mb ? -1 : 1;
      }
      return a < b ? -1 : a > b ? 1 : 0;
    });
    return new Map(namesWithArgs.map((e) => [e, opsByName.get(e)]));
  }
  /**
   * @returns {!Layer}
   */
  copy() {
    let result = new _Layer();
    result.id_ops = new Map(this.id_ops);
    result.markers = [...this.markers];
    return result;
  }
  /**
   * @returns {!int}
   */
  countMeasurements() {
    let total = 0;
    for (let [target_id, op] of this.id_ops.entries()) {
      if (op.id_targets[0] === target_id) {
        total += op.countMeasurements();
      }
    }
    return total;
  }
  /**
   * @returns {!boolean}
   */
  hasDissipativeOperations() {
    let dissipative_gate_names = [
      "M",
      "MX",
      "MY",
      "MR",
      "MRX",
      "MRY",
      "MXX",
      "MYY",
      "MZZ",
      "RX",
      "RY",
      "R"
    ];
    for (let op of this.id_ops.values()) {
      if (op.gate.name.startsWith("MPP:") || dissipative_gate_names.indexOf(op.gate.name) !== -1) {
        return true;
      }
    }
    return false;
  }
  hasSingleQubitCliffords() {
    let dissipative_gate_names = [
      "M",
      "MX",
      "MY",
      "MR",
      "MRX",
      "MRY",
      "MXX",
      "MYY",
      "MZZ",
      "RX",
      "RY",
      "R"
    ];
    for (let op of this.id_ops.values()) {
      if (op.id_targets.length === 1 && dissipative_gate_names.indexOf(op.gate.name) === -1 && op.countMeasurements() === 0) {
        return true;
      }
    }
    return false;
  }
  /**
   * @returns {!boolean}
   */
  hasResetOperations() {
    let gateNames = ["MR", "MRX", "MRY", "RX", "RY", "R"];
    for (let op of this.id_ops.values()) {
      if (gateNames.indexOf(op.gate.name) !== -1) {
        return true;
      }
    }
    return false;
  }
  /**
   * @returns {!boolean}
   */
  hasMeasurementOperations() {
    let gateNames = ["M", "MX", "MY", "MR", "MRX", "MRY", "MXX", "MYY", "MZZ"];
    for (let op of this.id_ops.values()) {
      if (op.gate.name.startsWith("MPP:") || gateNames.indexOf(op.gate.name) !== -1) {
        return true;
      }
    }
    return false;
  }
  /**
   * @return {!boolean}
   */
  empty() {
    return this.id_ops.size === 0 && this.markers.length === 0;
  }
  /**
   * @param {!function(op: !Operation): !boolean} predicate
   * @returns {!Layer}
   */
  id_filtered(predicate) {
    let newLayer = new _Layer();
    for (let op of this.id_ops.values()) {
      if (predicate(op)) {
        newLayer.put(op);
      }
    }
    for (let op of this.markers) {
      if (predicate(op)) {
        newLayer.markers.push(op);
      }
    }
    return newLayer;
  }
  /**
   * @param {!function(qubit: !int): !boolean} predicate
   * @returns {!Layer}
   */
  id_filteredByQubit(predicate) {
    return this.id_filtered((op) => !op.id_targets.every((q) => !predicate(q)));
  }
  /**
   * @param {!Map<!int, !string>} before
   * @param {!int} marker_index
   * @returns {!Map<!int, !string>}
   */
  id_pauliFrameAfter(before, marker_index) {
    let after = /* @__PURE__ */ new Map();
    let handled = /* @__PURE__ */ new Set();
    for (let k of before.keys()) {
      let v = before.get(k);
      let op = this.id_ops.get(k);
      if (op !== void 0) {
        let already_done = false;
        let b = "";
        for (let q of op.id_targets) {
          if (handled.has(q)) {
            already_done = true;
          }
          handled.add(q);
          let r = before.get(q);
          if (r === void 0) {
            r = "I";
          }
          b += r;
        }
        let a = op.pauliFrameAfter(b);
        let hasErr = a.startsWith("ERR:");
        for (let qi = 0; qi < op.id_targets.length; qi++) {
          let q = op.id_targets[qi];
          if (hasErr) {
            after.set(q, "ERR:" + a[4 + qi]);
          } else {
            after.set(q, a[qi]);
          }
        }
      } else {
        after.set(k, v);
      }
    }
    for (let op of this.markers) {
      if (op.gate.name === "MARKX" && op.args[0] === marker_index) {
        let key = op.id_targets[0];
        let pauli = after.get(key);
        if (pauli === void 0 || pauli === "I") {
          pauli = "X";
        } else if (pauli === "X") {
          pauli = "I";
        } else if (pauli === "Y") {
          pauli = "Z";
        } else if (pauli === "Z") {
          pauli = "Y";
        }
        after.set(key, pauli);
      } else if (op.gate.name === "MARKY" && op.args[0] === marker_index) {
        let key = op.id_targets[0];
        let pauli = after.get(key);
        if (pauli === void 0 || pauli === "I") {
          pauli = "Y";
        } else if (pauli === "X") {
          pauli = "Z";
        } else if (pauli === "Y") {
          pauli = "I";
        } else if (pauli === "Z") {
          pauli = "X";
        }
        after.set(key, pauli);
      } else if (op.gate.name === "MARKZ" && op.args[0] === marker_index) {
        let key = op.id_targets[0];
        let pauli = after.get(key);
        if (pauli === void 0 || pauli === "I") {
          pauli = "Z";
        } else if (pauli === "X") {
          pauli = "Y";
        } else if (pauli === "Y") {
          pauli = "X";
        } else if (pauli === "Z") {
          pauli = "I";
        }
        after.set(key, pauli);
      }
    }
    return after;
  }
  /**
   * @returns {!boolean}
   */
  isEmpty() {
    return this.id_ops.size === 0 && this.markers.length === 0;
  }
  /**
   * @param {!int} qubit
   * @returns {!Operation|undefined}
   */
  id_pop_at(qubit) {
    this.markers = this.markers.filter(
      (op) => op.id_targets.indexOf(qubit) === -1
    );
    if (this.id_ops.has(qubit)) {
      let op = this.id_ops.get(qubit);
      for (let t of op.id_targets) {
        this.id_ops.delete(t);
      }
      return op;
    }
    return void 0;
  }
  /**
   * @param {!int} q
   * @param {undefined|!int} index
   */
  id_dropMarkersAt(q, index = void 0) {
    this.markers = this.markers.filter((op) => {
      if (index !== void 0 && op.args[0] !== index) {
        return true;
      }
      if (op.gate.name !== "MARKX" && op.gate.name !== "MARKY" && op.gate.name !== "MARKZ") {
        return true;
      }
      return op.id_targets[0] !== q;
    });
  }
  /**
   * @param {!Operation} op
   * @param {!boolean=true} allow_overwrite
   */
  put(op, allow_overwrite = true) {
    if (op.gate.is_marker) {
      if (op.gate.name === "MARKX" || op.gate.name === "MARKY" || op.gate.name === "MARKZ") {
        this.id_dropMarkersAt(op.id_targets[0], op.args[0]);
      }
      this.markers.push(op);
      return;
    }
    for (let t of op.id_targets) {
      if (this.id_ops.has(t)) {
        if (allow_overwrite) {
          this.id_pop_at(t);
        } else {
          throw new Error("Collision");
        }
      }
    }
    for (let t of op.id_targets) {
      this.id_ops.set(t, op);
    }
  }
  /**
   * @returns {!Iterator<!Operation>}
   */
  *iter_gates_and_markers() {
    for (let t of this.id_ops.keys()) {
      let op = this.id_ops.get(t);
      if (op.id_targets[0] === t) {
        yield op;
      }
    }
    yield* this.markers;
  }
};
function minXY(xys) {
  let minX = void 0;
  let minY = void 0;
  for (let [vx, vy] of xys) {
    if (minX === void 0 || vx < minX || vx === minX && vy < minY) {
      minX = vx;
      minY = vy;
    }
  }
  return [minX, minY];
}

// crumble/gates/gateset_mpp.js
function make_mpp_gate(bases) {
  return new Gate(
    "MPP:" + bases,
    bases.length,
    true,
    false,
    void 0,
    (frame, targets) => frame.do_mpp(bases, targets),
    (frame, targets) => frame.do_mpp(bases, targets),
    (op, coordFunc, ctx) => {
      let prev_x = void 0;
      let prev_y = void 0;
      for (let k = 0; k < op.id_targets.length; k++) {
        let t = op.id_targets[k];
        let [x, y] = coordFunc(t);
        if (prev_x !== void 0) {
          draw_connector(ctx, x, y, prev_x, prev_y);
        }
        prev_x = x;
        prev_y = y;
      }
      for (let k = 0; k < op.id_targets.length; k++) {
        let t = op.id_targets[k];
        let [x, y] = coordFunc(t);
        ctx.fillStyle = "gray";
        ctx.fillRect(x - rad, y - rad, rad * 2, rad * 2);
        ctx.strokeStyle = "black";
        ctx.strokeRect(x - rad, y - rad, rad * 2, rad * 2);
        ctx.fillStyle = "black";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.font = "bold 12pt monospace";
        ctx.fillText(bases[k], x, y - 1);
        ctx.font = "5pt monospace";
        ctx.fillText("MPP", x, y + 8);
      }
    }
  );
}
function make_spp_gate(bases, dag) {
  return new Gate(
    (dag ? "SPP_DAG:" : "SPP:") + bases,
    bases.length,
    true,
    false,
    void 0,
    (frame, targets) => frame.do_spp(bases, targets),
    (frame, targets) => frame.do_spp(bases, targets),
    (op, coordFunc, ctx) => {
      let prev_x = void 0;
      let prev_y = void 0;
      for (let k = 0; k < op.id_targets.length; k++) {
        let t = op.id_targets[k];
        let [x, y] = coordFunc(t);
        if (prev_x !== void 0) {
          draw_connector(ctx, x, y, prev_x, prev_y);
        }
        prev_x = x;
        prev_y = y;
      }
      for (let k = 0; k < op.id_targets.length; k++) {
        let t = op.id_targets[k];
        let [x, y] = coordFunc(t);
        ctx.fillStyle = "gray";
        ctx.fillRect(x - rad, y - rad, rad * 2, rad * 2);
        ctx.strokeStyle = "black";
        ctx.strokeRect(x - rad, y - rad, rad * 2, rad * 2);
        ctx.fillStyle = "black";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.font = "bold 12pt monospace";
        ctx.fillText(bases[k], x, y - 1);
        ctx.font = "5pt monospace";
        ctx.fillText(dag ? "SPP\u2020" : "SPP", x, y + 8);
      }
    }
  );
}

// crumble/base/describe.js
var COLLECTION_CUTOFF = 1e3;
var BAD_TO_STRING_RESULT = new function() {
}().toString();
var RECURSE_LIMIT_DESCRIPTION = "!recursion-limit!";
var DEFAULT_RECURSION_LIMIT = 10;
function try_describe_atomic(value) {
  if (value === null) {
    return "null";
  }
  if (value === void 0) {
    return "undefined";
  }
  if (typeof value === "string") {
    return `"${value}"`;
  }
  if (typeof value === "number") {
    return "" + value;
  }
  return void 0;
}
function try_describe_collection(value, recursionLimit) {
  if (recursionLimit === 0) {
    return RECURSE_LIMIT_DESCRIPTION;
  }
  if (value instanceof Map) {
    return describe_Map(value, recursionLimit);
  }
  if (value instanceof Set) {
    return describe_Set(value, recursionLimit);
  }
  if (value[Symbol.iterator] !== void 0) {
    return describe_Iterable(value, recursionLimit);
  }
  return void 0;
}
function describe_fallback(value, recursionLimit) {
  try {
    let defaultString = String(value);
    if (defaultString !== BAD_TO_STRING_RESULT) {
      return defaultString;
    }
  } catch {
  }
  return describe_Object(value, recursionLimit);
}
function describe(value, recursionLimit = DEFAULT_RECURSION_LIMIT) {
  return try_describe_atomic(value) || try_describe_collection(value, recursionLimit) || describe_fallback(value, recursionLimit);
}
function describe_Map(map, limit) {
  let entries = [];
  for (let [k, v] of map.entries()) {
    if (entries.length > COLLECTION_CUTOFF) {
      entries.push("[...]");
      break;
    }
    let keyDesc = describe(k, limit - 1);
    let valDesc = describe(v, limit - 1);
    entries.push(`${keyDesc}: ${valDesc}`);
  }
  return `Map{${entries.join(", ")}}`;
}
function describe_Set(set, limit) {
  let entries = [];
  for (let e of set) {
    if (entries.length > COLLECTION_CUTOFF) {
      entries.push("[...]");
      break;
    }
    entries.push(describe(e, limit - 1));
  }
  return `Set{${entries.join(", ")}}`;
}
function describe_Iterable(seq, limit) {
  let entries = [];
  for (let e of seq) {
    if (entries.length > COLLECTION_CUTOFF) {
      entries.push("[...]");
      break;
    }
    entries.push(describe(e, limit - 1));
  }
  let prefix = Array.isArray(seq) ? "" : seq.constructor.name;
  return `${prefix}[${entries.join(", ")}]`;
}
function describe_Object(value, limit) {
  let entries = [];
  for (let k in value) {
    if (!value.hasOwnProperty(k)) {
      continue;
    }
    if (entries.length > COLLECTION_CUTOFF) {
      entries.push("[...]");
      break;
    }
    let v = value[k];
    let keyDesc = describe(k, limit - 1);
    let valDesc = describe(v, limit - 1);
    entries.push(`${keyDesc}: ${valDesc}`);
  }
  if (value.constructor === void 0) {
    return `[an unknown non-primitive value with no constructor]`;
  }
  let typeName = value.constructor.name;
  let prefix = typeName === {}.constructor.name ? "" : `(Type: ${typeName})`;
  return `${prefix}{${entries.join(", ")}}`;
}

// crumble/circuit/circuit.js
function processTargetsTextIntoTargets(targetText) {
  let targets = [];
  let flush = () => {
    if (curTarget !== "") {
      targets.push(curTarget);
      curTarget = "";
    }
  };
  let curTarget = "";
  for (let c of targetText) {
    if (c === " ") {
      flush();
    } else if (c === "*") {
      flush();
      targets.push("*");
    } else {
      curTarget += c;
    }
  }
  flush();
  return targets;
}
function splitUncombinedTargets(targets) {
  let result = [];
  let start = 0;
  while (start < targets.length) {
    let end = start + 1;
    while (end < targets.length && targets[end] === "*") {
      end += 2;
    }
    if (end > targets.length) {
      throw Error(`Dangling combiner in ${targets}.`);
    }
    let term = [];
    for (let k = start; k < end; k += 2) {
      if (targets[k] === "*") {
        if (k === 0) {
          throw Error(`Leading combiner in ${targets}.`);
        }
        throw Error(`Adjacent combiners in ${targets}.`);
      }
      term.push(targets[k]);
    }
    result.push(term);
    start = end;
  }
  return result;
}
function simplifiedMPP(tag, args, combinedTargets, convertIntoOtherGates) {
  let bases = "";
  let qubits = [];
  for (let t of combinedTargets) {
    if (t[0] === "!") {
      t = t.substring(1);
    }
    if (t[0] === "X" || t[0] === "Y" || t[0] === "Z") {
      bases += t[0];
      let v = parseInt(t.substring(1));
      if (v !== v) {
        throw Error(`Non-Pauli target given to MPP: ${combinedTargets}`);
      }
      qubits.push(v);
    } else {
      throw Error(`Non-Pauli target given to MPP: ${combinedTargets}`);
    }
  }
  let gate = void 0;
  if (convertIntoOtherGates) {
    gate = GATE_MAP.get("M" + bases);
  }
  if (gate === void 0) {
    gate = GATE_MAP.get("MPP:" + bases);
  }
  if (gate === void 0) {
    gate = make_mpp_gate(bases);
  }
  return new Operation(gate, tag, args, new Uint32Array(qubits));
}
function simplifiedSPP(tag, args, dag, combinedTargets) {
  let bases = "";
  let qubits = [];
  for (let t of combinedTargets) {
    if (t[0] === "!") {
      t = t.substring(1);
    }
    if (t[0] === "X" || t[0] === "Y" || t[0] === "Z") {
      bases += t[0];
      let v = parseInt(t.substring(1));
      if (v !== v) {
        throw Error(`Non-Pauli target given to SPP: ${combinedTargets}`);
      }
      qubits.push(v);
    } else {
      throw Error(`Non-Pauli target given to SPP: ${combinedTargets}`);
    }
  }
  let gate = GATE_MAP.get((dag ? "SPP_DAG:" : "SPP:") + bases);
  if (gate === void 0) {
    gate = make_spp_gate(bases, dag);
  }
  return new Operation(gate, tag, args, new Uint32Array(qubits));
}
var Circuit = class _Circuit {
  /**
   * @param {!Float64Array} qubitCoordData
   * @param {!Array<!Layer>} layers
   */
  constructor(qubitCoordData, layers = []) {
    if (!(qubitCoordData instanceof Float64Array)) {
      throw new Error("!(qubitCoords instanceof Float64Array)");
    }
    if (!Array.isArray(layers)) {
      throw new Error("!Array.isArray(layers)");
    }
    if (!layers.every((e) => e instanceof Layer)) {
      throw new Error("!layers.every(e => e instanceof Layer)");
    }
    this.qubitCoordData = qubitCoordData;
    this.layers = layers;
  }
  /**
   * @param {!string} stimCircuit
   * @returns {!Circuit}
   */
  static fromStimCircuit(stimCircuit) {
    let lines = stimCircuit.replaceAll(";", "\n").replaceAll("#!pragma ERR", "ERR").replaceAll("#!pragma MARK", "MARK").replaceAll("#!pragma POLYGON", "POLYGON").replaceAll("_", " ").replaceAll("Q(", "QUBIT_COORDS(").replaceAll("DT", "DETECTOR").replaceAll("OI", "OBSERVABLE_INCLUDE").replaceAll(" COORDS", "_COORDS").replaceAll(" ERROR", "_ERROR").replaceAll("C XYZ", "C_XYZ").replaceAll("C NXYZ", "C_NXYZ").replaceAll("C XNYZ", "C_XNYZ").replaceAll("C XYNZ", "C_XYNZ").replaceAll("H XY", "H_XY").replaceAll("H XZ", "H_XZ").replaceAll("H YZ", "H_YZ").replaceAll("H NXY", "H_NXY").replaceAll("H NXZ", "H_NXZ").replaceAll("H NYZ", "H_NYZ").replaceAll(" INCLUDE", "_INCLUDE").replaceAll("SQRT ", "SQRT_").replaceAll(" DAG ", "_DAG ").replaceAll("C ZYX", "C_ZYX").replaceAll("C NZYX", "C_NZYX").replaceAll("C ZNYX", "C_ZNYX").replaceAll("C ZYNX", "C_ZYNX").split("\n");
    let layers = [new Layer()];
    let num_detectors = 0;
    let i2q = /* @__PURE__ */ new Map();
    let used_positions = /* @__PURE__ */ new Set();
    let findEndOfBlock = (lines2, startIndex, endIndex) => {
      let nestLevel = 0;
      for (let k = startIndex; k < endIndex; k++) {
        let line = lines2[k];
        line = line.split("#")[0].trim();
        if (line.toLowerCase().startsWith("repeat ")) {
          nestLevel++;
        } else if (line === "}") {
          nestLevel--;
          if (nestLevel === 0) {
            return k;
          }
        }
      }
      throw Error("Repeat block didn't end");
    };
    let processLineChunk = (lines2, startIndex, endIndex, repetitions) => {
      if (!layers[layers.length - 1].empty()) {
        layers.push(new Layer());
      }
      for (let rep = 0; rep < repetitions; rep++) {
        for (let k = startIndex; k < endIndex; k++) {
          let line = lines2[k];
          line = line.split("#")[0].trim();
          if (line.toLowerCase().startsWith("repeat ")) {
            let reps = parseInt(line.split(" ")[1]);
            let k2 = findEndOfBlock(lines2, k, endIndex);
            processLineChunk(lines2, k + 1, k2, reps);
            k = k2;
          } else {
            processLine(line);
          }
        }
        if (!layers[layers.length - 1].empty()) {
          layers.push(new Layer());
        }
      }
    };
    let measurement_locs = [];
    let processLine = (line) => {
      let args = [];
      let targets = [];
      let tag = "";
      let name = "";
      let firstSpace = line.indexOf(" ");
      let firstParens = line.indexOf("(");
      let tagStart = line.indexOf("[");
      let tagEnd = line.indexOf("]");
      if (tagStart !== -1 && firstSpace !== -1 && firstSpace < tagStart) {
        tagStart = -1;
      }
      if (tagStart !== -1 && firstParens !== -1 && firstParens < tagStart) {
        tagStart = -1;
      }
      if (tagStart !== -1 && tagEnd > tagStart) {
        tag = line.substring(tagStart + 1, tagEnd).replaceAll("\\C", "]").replaceAll("\\r", "\r").replaceAll("\\n", "\n").replaceAll("\\B", "\\");
        line = line.substring(0, tagStart) + " " + line.substring(tagEnd + 1);
      }
      if (line.indexOf(")") !== -1) {
        let [ab, c] = line.split(")");
        let [a2, b] = ab.split("(");
        name = a2.trim();
        args = b.split(",").map((e) => e.trim()).map(parseFloat);
        targets = processTargetsTextIntoTargets(c);
      } else {
        let ab = line.split(" ").map((e) => e.trim()).filter((e) => e !== "");
        if (ab.length === 0) {
          return;
        }
        let [a2, ...b] = ab;
        name = a2.trim();
        args = [];
        targets = b.flatMap(processTargetsTextIntoTargets);
      }
      let reverse_pairs = false;
      if (name === "") {
        return;
      }
      if (args.length > 0 && [
        "M",
        "MX",
        "MY",
        "MZ",
        "MR",
        "MRX",
        "MRY",
        "MRZ",
        "MPP",
        "MPAD"
      ].indexOf(name) !== -1) {
        args = [];
      }
      let alias = GATE_ALIAS_MAP.get(name);
      if (alias !== void 0) {
        if (alias.ignore) {
          return;
        } else if (alias.name !== void 0) {
          reverse_pairs = alias.rev_pair !== void 0 && alias.rev_pair;
          name = alias.name;
        } else {
          throw new Error(`Unimplemented alias ${name}: ${describe(alias)}.`);
        }
      } else if (name === "TICK") {
        layers.push(new Layer());
        return;
      } else if (name === "MPP") {
        let combinedTargets = splitUncombinedTargets(targets);
        let layer2 = layers[layers.length - 1];
        for (let combo of combinedTargets) {
          let op = simplifiedMPP(tag, new Float32Array(args), combo, false);
          try {
            layer2.put(op, false);
          } catch (_) {
            layers.push(new Layer());
            layer2 = layers[layers.length - 1];
            layer2.put(op, false);
          }
          measurement_locs.push({
            layer: layers.length - 1,
            targets: op.id_targets
          });
        }
        return;
      } else if (name === "DETECTOR" || name === "OBSERVABLE_INCLUDE") {
        let isDet = name === "DETECTOR";
        let argIndex = isDet ? num_detectors : args.length > 0 ? Math.round(args[0]) : 0;
        for (let target of targets) {
          if (!target.startsWith("rec[-") || !target.endsWith("]")) {
            console.warn(
              "Ignoring instruction due to non-record target: " + line
            );
            return;
          }
          let index = measurement_locs.length + Number.parseInt(target.substring(4, target.length - 1));
          if (index < 0 || index >= measurement_locs.length) {
            console.warn(
              "Ignoring instruction due to out of range record target: " + line
            );
            return;
          }
          let loc = measurement_locs[index];
          layers[loc.layer].markers.push(
            new Operation(
              GATE_MAP.get(name),
              tag,
              new Float32Array([argIndex]),
              new Uint32Array([loc.targets[0]])
            )
          );
        }
        num_detectors += isDet;
        return;
      } else if (name === "SPP" || name === "SPP_DAG") {
        let dag = name === "SPP_DAG";
        let combinedTargets = splitUncombinedTargets(targets);
        let layer2 = layers[layers.length - 1];
        for (let combo of combinedTargets) {
          try {
            layer2.put(
              simplifiedSPP(tag, new Float32Array(args), dag, combo),
              false
            );
          } catch (_) {
            layers.push(new Layer());
            layer2 = layers[layers.length - 1];
            layer2.put(
              simplifiedSPP(tag, new Float32Array(args), dag, combo),
              false
            );
          }
        }
        return;
      } else if (name.startsWith("QUBIT_COORDS")) {
        let x = args.length < 1 ? 0 : args[0];
        let y = args.length < 2 ? 0 : args[1];
        for (let targ of targets) {
          let t = parseInt(targ);
          if (i2q.has(t)) {
            console.warn(
              `Ignoring "${line}" because there's already coordinate data for qubit ${t}.`
            );
          } else if (used_positions.has(`${x},${y}`)) {
            console.warn(
              `Ignoring "${line}" because there's already a qubit placed at ${x},${y}.`
            );
          } else {
            i2q.set(t, [x, y]);
            used_positions.add(`${x},${y}`);
          }
        }
        return;
      }
      let has_feedback = false;
      for (let targ of targets) {
        if (targ.startsWith("rec[")) {
          if (name === "CX" || name === "CY" || name === "CZ" || name === "ZCX" || name === "ZCY") {
            has_feedback = true;
          }
        } else if (typeof parseInt(targ) !== "number") {
          throw new Error(line);
        }
      }
      if (has_feedback) {
        let clean_targets = [];
        for (let k = 0; k < targets.length; k += 2) {
          let b0 = targets[k].startsWith("rec[");
          let b1 = targets[k + 1].startsWith("rec[");
          if (b0 || b1) {
            if (!b0) {
              layers[layers.length - 1].put(
                new Operation(
                  GATE_MAP.get("ERR"),
                  tag,
                  new Float32Array([]),
                  new Uint32Array([targets[k]])
                )
              );
            }
            if (!b1) {
              layers[layers.length - 1].put(
                new Operation(
                  GATE_MAP.get("ERR"),
                  tag,
                  new Float32Array([]),
                  new Uint32Array([targets[k + 1]])
                )
              );
            }
            console.warn(
              "Feedback isn't supported yet. Ignoring",
              name,
              targets[k],
              targets[k + 1]
            );
          } else {
            clean_targets.push(targets[k]);
            clean_targets.push(targets[k + 1]);
          }
        }
        targets = clean_targets;
        if (targets.length === 0) {
          return;
        }
      }
      let gate = GATE_MAP.get(name);
      if (gate === void 0) {
        console.warn("Ignoring unrecognized instruction: " + line);
        return;
      }
      let a = new Float32Array(args);
      let layer = layers[layers.length - 1];
      if (gate.num_qubits === void 0) {
        layer.put(new Operation(gate, tag, a, new Uint32Array(targets)));
      } else {
        if (targets.length % gate.num_qubits !== 0) {
          throw new Error("Incorrect number of targets in line " + line);
        }
        for (let k = 0; k < targets.length; k += gate.num_qubits) {
          let sub_targets = targets.slice(k, k + gate.num_qubits);
          if (reverse_pairs) {
            sub_targets.reverse();
          }
          let qs = new Uint32Array(sub_targets);
          let op = new Operation(gate, tag, a, qs);
          try {
            layer.put(op, false);
          } catch (_) {
            layers.push(new Layer());
            layer = layers[layers.length - 1];
            layer.put(op, false);
          }
          if (op.countMeasurements() > 0) {
            measurement_locs.push({
              layer: layers.length - 1,
              targets: op.id_targets
            });
          }
        }
      }
    };
    processLineChunk(lines, 0, lines.length, 1);
    if (layers.length > 0 && layers[layers.length - 1].isEmpty()) {
      layers.pop();
    }
    let next_auto_position_x = 0;
    let ensure_has_coords = (t) => {
      let b = true;
      while (!i2q.has(t)) {
        let x = b ? t : next_auto_position_x;
        let k = `${x},0`;
        if (!used_positions.has(k)) {
          used_positions.add(k);
          i2q.set(t, [x, 0]);
        }
        next_auto_position_x += !b;
        b = false;
      }
    };
    for (let layer of layers) {
      for (let op of layer.iter_gates_and_markers()) {
        for (let t of op.id_targets) {
          ensure_has_coords(t);
        }
      }
    }
    let numQubits = Math.max(...i2q.keys(), 0) + 1;
    let qubitCoords = new Float64Array(numQubits * 2);
    for (let q = 0; q < numQubits; q++) {
      ensure_has_coords(q);
      let [x, y] = i2q.get(q);
      qubitCoords[2 * q] = x;
      qubitCoords[2 * q + 1] = y;
    }
    return new _Circuit(qubitCoords, layers);
  }
  /**
   * @returns {!Set<!int>}
   */
  allQubits() {
    let result = /* @__PURE__ */ new Set();
    for (let layer of this.layers) {
      for (let op of layer.iter_gates_and_markers()) {
        for (let t of op.id_targets) {
          result.add(t);
        }
      }
    }
    return result;
  }
  /**
   * @returns {!Circuit}
   */
  rotated45() {
    return this.afterCoordTransform((x, y) => [x - y, x + y]);
  }
  coordTransformForRectification() {
    let coordSet = /* @__PURE__ */ new Map();
    for (let k = 0; k < this.qubitCoordData.length; k += 2) {
      let x = this.qubitCoordData[k];
      let y = this.qubitCoordData[k + 1];
      coordSet.set(`${x},${y}`, [x, y]);
    }
    let minX = Infinity;
    let minY = Infinity;
    let step = 256;
    for (let [x, y] of coordSet.values()) {
      minX = Math.min(x, minX);
      minY = Math.min(y, minY);
      while ((x % step !== 0 || y % step !== 0) && step > 1 / 256) {
        step /= 2;
      }
    }
    let scale;
    if (step <= 1 / 256) {
      scale = 1;
    } else {
      scale = 1 / step;
      let mask = 0;
      for (let [x, y] of coordSet.values()) {
        let b1 = (x - minX + y - minY) % (2 * step);
        let b2 = (x - minX - y + minY) % (2 * step);
        mask |= b1 === 0 ? 1 : 2;
        mask |= b2 === 0 ? 4 : 8;
      }
      if (mask === (1 | 4)) {
        scale /= 2;
      } else if (mask === (2 | 8)) {
        minX -= step;
        scale /= 2;
      }
    }
    let offsetX = -minX;
    let offsetY = -minY;
    return (x, y) => [(x + offsetX) * scale, (y + offsetY) * scale];
  }
  /**
   * @returns {!Circuit}
   */
  afterRectification() {
    return this.afterCoordTransform(this.coordTransformForRectification());
  }
  /**
   * @param {!number} dx
   * @param {!number} dy
   * @returns {!Circuit}
   */
  shifted(dx, dy) {
    return this.afterCoordTransform((x, y) => [x + dx, y + dy]);
  }
  /**
   * @return {!Circuit}
   */
  copy() {
    return this.shifted(0, 0);
  }
  /**
   * @param {!function(!number, !number): ![!number, !number]} coordTransform
   * @returns {!Circuit}
   */
  afterCoordTransform(coordTransform) {
    let newCoords = new Float64Array(this.qubitCoordData.length);
    for (let k = 0; k < this.qubitCoordData.length; k += 2) {
      let x = this.qubitCoordData[k];
      let y = this.qubitCoordData[k + 1];
      let [x2, y2] = coordTransform(x, y);
      newCoords[k] = x2;
      newCoords[k + 1] = y2;
    }
    let newLayers = this.layers.map((e) => e.copy());
    return new _Circuit(newCoords, newLayers);
  }
  /**
   * @param {!boolean} orderForToStimCircuit
   * @returns {!{dets: !Array<!{mids: !Array<!int>, qids: !Array<!int>}>, obs: !Map<!int, !Array.<!int>>}}
   */
  collectDetectorsAndObservables(orderForToStimCircuit) {
    let m2d = /* @__PURE__ */ new Map();
    for (let k = 0; k < this.layers.length; k++) {
      let layer = this.layers[k];
      if (orderForToStimCircuit) {
        for (let group of layer.opsGroupedByNameWithArgs().values()) {
          for (let op of group) {
            if (op.countMeasurements() > 0) {
              let target_id = op.id_targets[0];
              m2d.set(`${k}:${target_id}`, {
                mid: m2d.size,
                qids: op.id_targets
              });
            }
          }
        }
      } else {
        for (let [target_id, op] of layer.id_ops.entries()) {
          if (op.id_targets[0] === target_id) {
            if (op.countMeasurements() > 0) {
              m2d.set(`${k}:${target_id}`, {
                mid: m2d.size,
                qids: op.id_targets
              });
            }
          }
        }
      }
    }
    let detectors = [];
    let observables = /* @__PURE__ */ new Map();
    for (let k = 0; k < this.layers.length; k++) {
      let layer = this.layers[k];
      for (let op of layer.markers) {
        if (op.gate.name === "DETECTOR") {
          let d = Math.round(op.args[0]);
          while (detectors.length <= d) {
            detectors.push({ mids: [], qids: [] });
          }
          let det_entry = detectors[d];
          let key = `${k}:${op.id_targets[0]}`;
          let v = m2d.get(key);
          if (v !== void 0) {
            det_entry.mids.push(v.mid - m2d.size);
            det_entry.qids.push(...v.qids);
          }
        } else if (op.gate.name === "OBSERVABLE_INCLUDE") {
          let d = Math.round(op.args[0]);
          let entries = observables.get(d);
          if (entries === void 0) {
            entries = [];
            observables.set(d, entries);
          }
          let key = `${k}:${op.id_targets[0]}`;
          if (m2d.has(key)) {
            entries.push(m2d.get(key).mid - m2d.size);
          }
        }
      }
    }
    let seen = /* @__PURE__ */ new Set();
    let keptDetectors = [];
    for (let ds of detectors) {
      if (ds.mids.length > 0) {
        ds.mids = [...new Set(ds.mids)];
        ds.mids.sort((a, b) => b - a);
        let key = ds.mids.join(":");
        if (!seen.has(key)) {
          seen.add(key);
          keptDetectors.push(ds);
        }
      }
    }
    for (let [k, vs] of observables.entries()) {
      vs = [...new Set(vs)];
      vs.sort((a, b) => b - a);
      observables.set(k, vs);
    }
    keptDetectors.sort((a, b) => a.mids[0] - b.mids[0]);
    return { dets: keptDetectors, obs: observables };
  }
  /**
   * @returns {!string}
   */
  toStimCircuit() {
    let usedQubits = /* @__PURE__ */ new Set();
    for (let layer of this.layers) {
      for (let op of layer.iter_gates_and_markers()) {
        for (let t of op.id_targets) {
          usedQubits.add(t);
        }
      }
    }
    let { dets: remainingDetectors, obs: remainingObservables } = this.collectDetectorsAndObservables(true);
    remainingDetectors.reverse();
    let seenMeasurements = 0;
    let totalMeasurements = this.countMeasurements();
    let packedQubitCoords = [];
    for (let q of usedQubits) {
      let x = this.qubitCoordData[2 * q];
      let y = this.qubitCoordData[2 * q + 1];
      packedQubitCoords.push({ q, x, y });
    }
    packedQubitCoords.sort((a, b) => {
      if (a.x !== b.x) {
        return a.x - b.x;
      }
      if (a.y !== b.y) {
        return a.y - b.y;
      }
      return a.q - b.q;
    });
    let old2new = /* @__PURE__ */ new Map();
    let out = [];
    for (let q = 0; q < packedQubitCoords.length; q++) {
      let { q: old_q, x, y } = packedQubitCoords[q];
      old2new.set(old_q, q);
      out.push(`QUBIT_COORDS(${x}, ${y}) ${q}`);
    }
    let detectorLayer = 0;
    let usedDetectorCoords = /* @__PURE__ */ new Set();
    for (let layer of this.layers) {
      let opsByName = layer.opsGroupedByNameWithArgs();
      for (let [nameWithArgs, group] of opsByName.entries()) {
        let targetGroups = [];
        let gateName = nameWithArgs.split("(")[0].split("[")[0];
        if (gateName === "DETECTOR" || gateName === "OBSERVABLE_INCLUDE") {
          continue;
        }
        let gate = GATE_MAP.get(gateName);
        if (gate === void 0 && (gateName === "MPP" || gateName === "SPP" || gateName === "SPP_DAG")) {
          let line = [gateName + " "];
          for (let op of group) {
            seenMeasurements += op.countMeasurements();
            let bases = op.gate.name.substring(gateName.length + 1);
            for (let k = 0; k < op.id_targets.length; k++) {
              line.push(bases[k] + old2new.get(op.id_targets[k]));
              line.push("*");
            }
            line.pop();
            line.push(" ");
          }
          out.push(line.join("").trim());
        } else {
          if (gate !== void 0 && gate.can_fuse) {
            let flatTargetGroups = [];
            for (let op of group) {
              seenMeasurements += op.countMeasurements();
              flatTargetGroups.push(...op.id_targets);
            }
            targetGroups.push(flatTargetGroups);
          } else {
            for (let op of group) {
              seenMeasurements += op.countMeasurements();
              targetGroups.push([...op.id_targets]);
            }
          }
          for (let targetGroup of targetGroups) {
            let line = [nameWithArgs];
            for (let t of targetGroup) {
              line.push(old2new.get(t));
            }
            out.push(line.join(" "));
          }
        }
      }
      let nextDetectorLayer = detectorLayer;
      while (remainingDetectors.length > 0) {
        let candidate = remainingDetectors[remainingDetectors.length - 1];
        let offset = totalMeasurements - seenMeasurements;
        if (candidate.mids[0] + offset >= 0) {
          break;
        }
        remainingDetectors.pop();
        let cxs = [];
        let cys = [];
        let sx = 0;
        let sy = 0;
        for (let q of candidate.qids) {
          let cx = this.qubitCoordData[2 * q];
          let cy = this.qubitCoordData[2 * q + 1];
          sx += cx;
          sy += cy;
          cxs.push(cx);
          cys.push(cy);
        }
        if (candidate.qids.length > 0) {
          sx /= candidate.qids.length;
          sy /= candidate.qids.length;
          sx = Math.round(sx * 2) / 2;
          sy = Math.round(sy * 2) / 2;
        }
        cxs.push(sx);
        cys.push(sy);
        let name;
        let dt = detectorLayer;
        for (let k = 0; ; k++) {
          if (k >= cxs.length) {
            k = 0;
            dt += 1;
          }
          name = `DETECTOR(${cxs[k]}, ${cys[k]}, ${dt})`;
          if (!usedDetectorCoords.has(name)) {
            break;
          }
        }
        usedDetectorCoords.add(name);
        let line = [name];
        for (let d of candidate.mids) {
          line.push(`rec[${d + offset}]`);
        }
        out.push(line.join(" "));
        nextDetectorLayer = Math.max(nextDetectorLayer, dt + 1);
      }
      detectorLayer = nextDetectorLayer;
      for (let [obsIndex, candidate] of [...remainingObservables.entries()]) {
        let offset = totalMeasurements - seenMeasurements;
        if (candidate[0] + offset >= 0) {
          continue;
        }
        remainingObservables.delete(obsIndex);
        let line = [`OBSERVABLE_INCLUDE(${obsIndex})`];
        for (let d of candidate) {
          line.push(`rec[${d + offset}]`);
        }
        out.push(line.join(" "));
      }
      out.push(`TICK`);
    }
    while (out.length > 0 && out[out.length - 1] === "TICK") {
      out.pop();
    }
    return out.join("\n");
  }
  /**
   * @returns {!int}
   */
  countMeasurements() {
    let total = 0;
    for (let layer of this.layers) {
      total += layer.countMeasurements();
    }
    return total;
  }
  /**
   * @param {!Iterable<![!number, !number]>} coords
   */
  withCoordsIncluded(coords) {
    let coordMap = this.coordToQubitMap();
    let extraCoordData = [];
    for (let [x, y] of coords) {
      let key = `${x},${y}`;
      if (!coordMap.has(key)) {
        coordMap.set(key, coordMap.size);
        extraCoordData.push(x, y);
      }
    }
    return new _Circuit(
      new Float64Array([...this.qubitCoordData, ...extraCoordData]),
      this.layers.map((e) => e.copy())
    );
  }
  /**
   * @returns {!Map<!string, !int>}
   */
  coordToQubitMap() {
    let result = /* @__PURE__ */ new Map();
    for (let q = 0; q < this.qubitCoordData.length; q += 2) {
      let x = this.qubitCoordData[q];
      let y = this.qubitCoordData[q + 1];
      result.set(`${x},${y}`, q / 2);
    }
    return result;
  }
  /**
   * @returns {!string}
   */
  toString() {
    return this.toStimCircuit();
  }
  /**
   * @param {*} other
   * @returns {!boolean}
   */
  isEqualTo(other) {
    if (!(other instanceof _Circuit)) {
      return false;
    }
    return this.toStimCircuit() === other.toStimCircuit();
  }
};

// crumble/draw/timeline_viewer.js
var TIMELINE_PITCH = 32;
var PADDING_VERTICAL = rad;
var MAX_CANVAS_WIDTH = 4096;
function drawTimelineMarkers(ctx, ds, qubitTimeCoordFunc, propagatedMarkers, mi, min_t, max_t, x_pitch, hitCounts) {
  for (let t = min_t - 1; t <= max_t; t++) {
    if (!hitCounts.has(t)) {
      hitCounts.set(t, /* @__PURE__ */ new Map());
    }
    let hitCount = hitCounts.get(t);
    let p1 = propagatedMarkers.atLayer(t + 0.5);
    let p0 = propagatedMarkers.atLayer(t);
    for (let [q, b] of p1.bases.entries()) {
      let { dx, dy, wx, wy } = marker_placement(mi, q, hitCount);
      if (mi >= 0 && mi < 4) {
        dx = 0;
        wx = x_pitch;
        wy = 5;
        if (mi === 0) {
          dy = 10;
        } else if (mi === 1) {
          dy = 5;
        } else if (mi === 2) {
          dy = 0;
        } else if (mi === 3) {
          dy = -5;
        }
      } else {
        dx -= x_pitch / 2;
      }
      let [x, y] = qubitTimeCoordFunc(q, t);
      if (x === void 0 || y === void 0) {
        continue;
      }
      if (b === "X") {
        ctx.fillStyle = "red";
      } else if (b === "Y") {
        ctx.fillStyle = "green";
      } else if (b === "Z") {
        ctx.fillStyle = "blue";
      } else {
        throw new Error("Not a pauli: " + b);
      }
      ctx.fillRect(x - dx, y - dy, wx, wy);
    }
    for (let q of p0.errors) {
      let { dx, dy, wx, wy } = marker_placement(mi, q, hitCount);
      dx -= x_pitch / 2;
      let [x, y] = qubitTimeCoordFunc(q, t - 0.5);
      if (x === void 0 || y === void 0) {
        continue;
      }
      ctx.strokeStyle = "magenta";
      ctx.lineWidth = 8;
      ctx.strokeRect(x - dx, y - dy, wx, wy);
      ctx.lineWidth = 1;
      ctx.fillStyle = "black";
      ctx.fillRect(x - dx, y - dy, wx, wy);
    }
    for (let { q1, q2, color } of p0.crossings) {
      let [x1, y1] = qubitTimeCoordFunc(q1, t);
      let [x2, y2] = qubitTimeCoordFunc(q2, t);
      if (color === "X") {
        ctx.strokeStyle = "red";
      } else if (color === "Y") {
        ctx.strokeStyle = "green";
      } else if (color === "Z") {
        ctx.strokeStyle = "blue";
      } else {
        ctx.strokeStyle = "purple";
      }
      ctx.lineWidth = 8;
      stroke_connector_to(ctx, x1, y1, x2, y2);
      ctx.lineWidth = 1;
    }
  }
}
function drawTimeline(ctx, snap, propagatedMarkerLayers, timesliceQubitCoordsFunc, numLayers) {
  let w = MAX_CANVAS_WIDTH;
  let qubits = snap.timelineQubits();
  qubits.sort((a, b) => {
    let [x1, y1] = timesliceQubitCoordsFunc(a);
    let [x2, y2] = timesliceQubitCoordsFunc(b);
    if (y1 !== y2) {
      return y1 - y2;
    }
    return x1 - x2;
  });
  let base_y2xy = /* @__PURE__ */ new Map();
  let prev_y = void 0;
  let cur_x = 0;
  let cur_y = PADDING_VERTICAL + rad;
  let max_run = 0;
  let cur_run = 0;
  for (let q of qubits) {
    let [x, y] = timesliceQubitCoordsFunc(q);
    if (prev_y !== y) {
      cur_x = w / 2;
      max_run = Math.max(max_run, cur_run);
      cur_run = 0;
      if (prev_y !== void 0) {
        cur_y += TIMELINE_PITCH * 0.25;
      }
      prev_y = y;
    } else {
      if (indentCircuitLines) {
        cur_x += rad * 0.25;
      }
      cur_run++;
    }
    base_y2xy.set(`${x},${y}`, [
      Math.round(cur_x) + 0.5,
      Math.round(cur_y) + 0.5
    ]);
    cur_y += TIMELINE_PITCH;
  }
  let x_pitch = TIMELINE_PITCH + Math.ceil(rad * max_run * 0.25);
  let num_cols_half = Math.floor(w / 2 / x_pitch);
  let min_t_free = snap.curLayer - num_cols_half + 1;
  let min_t_clamp = Math.max(
    0,
    Math.min(min_t_free, numLayers - num_cols_half * 2 + 1)
  );
  let max_t = Math.min(min_t_clamp + num_cols_half * 2 + 2, numLayers);
  let t2t = (t) => {
    let dt = t - snap.curLayer;
    dt -= min_t_clamp - min_t_free;
    return dt * x_pitch;
  };
  let coordTransform_t = ([x, y, t]) => {
    let key = `${x},${y}`;
    if (!base_y2xy.has(key)) {
      return [void 0, void 0];
    }
    let [xb, yb] = base_y2xy.get(key);
    return [xb + t2t(t), yb];
  };
  let qubitTimeCoords = (q, t) => {
    let [x, y] = timesliceQubitCoordsFunc(q);
    return coordTransform_t([x, y, t]);
  };
  ctx.save();
  let maxLabelWidth = 0;
  let topLeftX = qubitTimeCoords(qubits[0], min_t_clamp - 1)[0];
  for (let q of qubits) {
    let [x, y] = qubitTimeCoords(q, min_t_clamp - 1);
    let qx = snap.circuit.qubitCoordData[q * 2];
    let qy = snap.circuit.qubitCoordData[q * 2 + 1];
    let label = `${qx},${qy}:`;
    let labelWidth = ctx.measureText(label).width;
    let labelWidthFromTop = labelWidth - (x - topLeftX);
    maxLabelWidth = Math.max(maxLabelWidth, labelWidthFromTop);
  }
  let textOverflowLen = Math.max(0, maxLabelWidth - topLeftX);
  let labelShiftedQTC = (q, t) => {
    let [x, y] = qubitTimeCoords(q, t);
    return [x + Math.ceil(textOverflowLen) + 3, y];
  };
  let timelineHeight = labelShiftedQTC(qubits.at(-1), max_t + 1)[1] + rad + PADDING_VERTICAL;
  let timelineWidth = Math.max(
    ...qubits.map((q) => labelShiftedQTC(q, max_t + 1)[0])
  );
  ctx.canvas.width = Math.floor(timelineWidth);
  ctx.canvas.height = Math.floor(timelineHeight);
  try {
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    let hitCounts = /* @__PURE__ */ new Map();
    for (let [mi, p] of propagatedMarkerLayers.entries()) {
      drawTimelineMarkers(
        ctx,
        snap,
        labelShiftedQTC,
        p,
        mi,
        min_t_clamp,
        max_t,
        x_pitch,
        hitCounts
      );
    }
    ctx.strokeStyle = "black";
    ctx.fillStyle = "black";
    for (let q of qubits) {
      let [x0, y0] = labelShiftedQTC(q, min_t_clamp - 1);
      let [x1, y1] = labelShiftedQTC(q, max_t + 1);
      ctx.beginPath();
      ctx.moveTo(x0, y0);
      ctx.lineTo(x1, y1);
      ctx.stroke();
    }
    ctx.textAlign = "right";
    ctx.textBaseline = "middle";
    for (let q of qubits) {
      let [x, y] = labelShiftedQTC(q, min_t_clamp - 1);
      let qx = snap.circuit.qubitCoordData[q * 2];
      let qy = snap.circuit.qubitCoordData[q * 2 + 1];
      let label = `${qx},${qy}:`;
      ctx.fillText(label, x, y);
    }
    for (let time = min_t_clamp; time <= max_t; time++) {
      let qubitsCoordsFuncForLayer = (q) => labelShiftedQTC(q, time);
      let layer = snap.circuit.layers[time];
      if (layer === void 0) {
        continue;
      }
      for (let op of layer.iter_gates_and_markers()) {
        op.id_draw(qubitsCoordsFuncForLayer, ctx);
      }
    }
  } finally {
    ctx.restore();
  }
}

// crumble/circuit/pauli_frame.js
var PauliFrame = class _PauliFrame {
  /**
   * @param {!int} num_frames
   * @param {!int} num_qubits
   */
  constructor(num_frames, num_qubits) {
    if (num_frames > 32) {
      throw new Error("num_frames > 32");
    }
    this.num_qubits = num_qubits;
    this.num_frames = num_frames;
    this.xs = new Uint32Array(num_qubits);
    this.zs = new Uint32Array(num_qubits);
    this.flags = new Uint32Array(num_qubits);
  }
  /**
   * @returns {!PauliFrame}
   */
  copy() {
    let result = new _PauliFrame(this.num_frames, this.num_qubits);
    for (let q = 0; q < this.num_qubits; q++) {
      result.xs[q] = this.xs[q];
      result.zs[q] = this.zs[q];
      result.flags[q] = this.flags[q];
    }
    return result;
  }
  /**
   * @param {!Array<!string>} qubit_keys
   * @returns {!Array<!Map<!string, !string>>}
   */
  to_dicts(qubit_keys) {
    if (qubit_keys.length !== this.num_qubits) {
      throw new Error("qubit_keys.length !== this.num_qubits");
    }
    let result = [];
    for (let k = 0; k < this.num_frames; k++) {
      result.push(/* @__PURE__ */ new Map());
    }
    for (let q = 0; q < this.num_qubits; q++) {
      let key = qubit_keys[q];
      let x = this.xs[q];
      let z = this.zs[q];
      let f = this.flags[q];
      let m = x | z | f;
      let k = 0;
      while (m) {
        if (m & 1) {
          if (f & 1) {
            result[k].set(key, "ERR:flag");
          } else if (x & z & 1) {
            result[k].set(key, "Y");
          } else if (x & 1) {
            result[k].set(key, "X");
          } else {
            result[k].set(key, "Z");
          }
        }
        k++;
        x >>= 1;
        z >>= 1;
        f >>= 1;
        m >>= 1;
      }
    }
    return result;
  }
  /**
   * @param {!Array<!string>} strings
   * @returns {!PauliFrame}
   */
  static from_strings(strings) {
    let num_frames = strings.length;
    if (num_frames === 0) {
      throw new Error("strings.length === 0");
    }
    let num_qubits = strings[0].length;
    for (let s of strings) {
      if (s.length !== num_qubits) {
        throw new Error("Inconsistent string length.");
      }
    }
    let result = new _PauliFrame(num_frames, num_qubits);
    for (let f = 0; f < num_frames; f++) {
      for (let q = 0; q < num_qubits; q++) {
        let c = strings[f][q];
        if (c === "X") {
          result.xs[q] |= 1 << f;
        } else if (c === "Y") {
          result.xs[q] |= 1 << f;
          result.zs[q] |= 1 << f;
        } else if (c === "Z") {
          result.zs[q] |= 1 << f;
        } else if (c === "I" || c === "_") {
        } else if (c === "!") {
          result.flags[q] |= 1 << f;
        } else if (c === "%") {
          result.flags[q] |= 1 << f;
          result.xs[q] |= 1 << f;
        } else if (c === "&") {
          result.flags[q] |= 1 << f;
          result.xs[q] |= 1 << f;
          result.zs[q] |= 1 << f;
        } else if (c === "$") {
          result.flags[q] |= 1 << f;
          result.zs[q] |= 1 << f;
        } else {
          throw new Error("Unrecognized pauli string character: '" + c + "'");
        }
      }
    }
    return result;
  }
  /**
   * @returns {!Array<!string>}
   */
  to_strings() {
    let result = [];
    for (let f = 0; f < this.num_frames; f++) {
      let s = "";
      for (let q = 0; q < this.num_qubits; q++) {
        let flag = this.flags[q] >> f & 1;
        let x = this.xs[q] >> f & 1;
        let z = this.zs[q] >> f & 1;
        s += "_XZY!%$&"[x + 2 * z + 4 * flag];
      }
      result.push(s);
    }
    return result;
  }
  /**
   * @param {!Array<!Map<!string, !string>>} dicts
   * @param {!Array<!string>} qubit_keys
   * @returns {!PauliFrame}
   */
  static from_dicts(dicts, qubit_keys) {
    let result = new _PauliFrame(dicts.length, qubit_keys.length);
    for (let f = 0; f < dicts.length; f++) {
      for (let q = 0; q < qubit_keys.length; q++) {
        let p = dicts[f].get(qubit_keys[q]);
        if (p === "X") {
          result.xs[q] |= 1 << f;
        } else if (p === "Z") {
          result.zs[q] |= 1 << f;
        } else if (p === "Y") {
          result.xs[q] |= 1 << f;
          result.zs[q] |= 1 << f;
        } else if (p !== "I" && p !== void 0) {
          result.flags[q] |= 1 << f;
        }
      }
    }
    return result;
  }
  /**
   * @param {!Array<!int>} targets
   */
  do_exchange_xz(targets) {
    for (let t of targets) {
      let x = this.xs[t];
      let z = this.zs[t];
      this.zs[t] = x;
      this.xs[t] = z;
    }
  }
  /**
   * @param {!Array<!int>} targets
   */
  do_exchange_xy(targets) {
    for (let t of targets) {
      this.zs[t] ^= this.xs[t];
    }
  }
  /**
   * @param {!Array<!int>} targets
   */
  do_exchange_yz(targets) {
    for (let t of targets) {
      this.xs[t] ^= this.zs[t];
    }
  }
  /**
   * @param {!Array<!int>} targets
   */
  do_discard(targets) {
    for (let t of targets) {
      this.flags[t] |= this.xs[t];
      this.flags[t] |= this.zs[t];
      this.xs[t] = 0;
      this.zs[t] = 0;
    }
  }
  /**
   * @param {!string} observable
   * @param {!Array<!int>} targets
   */
  do_measure(observable, targets) {
    for (let k = 0; k < targets.length; k += observable.length) {
      let anticommutes = 0;
      for (let k2 = 0; k2 < observable.length; k2++) {
        let t = targets[k + k2];
        let obs = observable[k2];
        if (obs === "X") {
          anticommutes ^= this.zs[t];
        } else if (obs === "Z") {
          anticommutes ^= this.xs[t];
        } else if (obs === "Y") {
          anticommutes ^= this.xs[t] ^ this.zs[t];
        } else {
          throw new Error(`Unrecognized measure obs: '${obs}'`);
        }
      }
      for (let k2 = 0; k2 < observable.length; k2++) {
        let t = targets[k + k2];
        this.flags[t] |= anticommutes;
      }
    }
  }
  /**
   * @param {!string} bases
   * @param {!Uint32Array|!Array.<!int>} targets
   */
  do_mpp(bases, targets) {
    if (bases.length !== targets.length) {
      throw new Error("bases.length !== targets.length");
    }
    let anticommutes = 0;
    for (let k = 0; k < bases.length; k++) {
      let t = targets[k];
      let obs = bases[k];
      if (obs === "X") {
        anticommutes ^= this.zs[t];
      } else if (obs === "Z") {
        anticommutes ^= this.xs[t];
      } else if (obs === "Y") {
        anticommutes ^= this.xs[t] ^ this.zs[t];
      } else {
        throw new Error(`Unrecognized measure obs: '${obs}'`);
      }
    }
    for (let k = 0; k < bases.length; k++) {
      let t = targets[k];
      this.flags[t] |= anticommutes;
    }
  }
  /**
   * @param {!string} bases
   * @param {!Uint32Array|!Array.<!int>} targets
   */
  do_spp(bases, targets) {
    if (bases.length !== targets.length) {
      throw new Error("bases.length !== targets.length");
    }
    let anticommutes = 0;
    for (let k = 0; k < bases.length; k++) {
      let t = targets[k];
      let obs = bases[k];
      if (obs === "X") {
        anticommutes ^= this.zs[t];
      } else if (obs === "Z") {
        anticommutes ^= this.xs[t];
      } else if (obs === "Y") {
        anticommutes ^= this.xs[t] ^ this.zs[t];
      } else {
        throw new Error(`Unrecognized spp obs: '${obs}'`);
      }
    }
    for (let k = 0; k < bases.length; k++) {
      let t = targets[k];
      let obs = bases[k];
      let x = 0;
      let z = 0;
      if (obs === "X") {
        x = 1;
      } else if (obs === "Z") {
        z = 1;
      } else if (obs === "Y") {
        x = 1;
        z = 1;
      } else {
        throw new Error(`Unrecognized spp obs: '${obs}'`);
      }
      if (x) {
        this.xs[t] ^= anticommutes;
      }
      if (z) {
        this.zs[t] ^= anticommutes;
      }
    }
  }
  /**
   * @param {!string} observable
   * @param {!Array<!int>} targets
   */
  do_demolition_measure(observable, targets) {
    if (observable === "X") {
      for (let q of targets) {
        this.flags[q] |= this.zs[q];
        this.xs[q] = 0;
        this.zs[q] = 0;
      }
    } else if (observable === "Z") {
      for (let q of targets) {
        this.flags[q] |= this.xs[q];
        this.xs[q] = 0;
        this.zs[q] = 0;
      }
    } else if (observable === "Y") {
      for (let q of targets) {
        this.flags[q] |= this.xs[q] ^ this.zs[q];
        this.xs[q] = 0;
        this.zs[q] = 0;
      }
    } else {
      throw new Error("Unrecognized demolition obs");
    }
  }
  /**
   * @param {!Array<!int>} targets
   */
  do_cycle_xyz(targets) {
    for (let t of targets) {
      this.xs[t] ^= this.zs[t];
      this.zs[t] ^= this.xs[t];
    }
  }
  /**
   * @param {!Array<!int>} targets
   */
  do_cycle_zyx(targets) {
    for (let t of targets) {
      this.zs[t] ^= this.xs[t];
      this.xs[t] ^= this.zs[t];
    }
  }
  /**
   * @param {!Array<!int>} targets
   */
  do_swap(targets) {
    for (let k = 0; k < targets.length; k += 2) {
      let a = targets[k];
      let b = targets[k + 1];
      let xa = this.xs[a];
      let za = this.zs[a];
      let xb = this.xs[b];
      let zb = this.zs[b];
      this.xs[a] = xb;
      this.zs[a] = zb;
      this.xs[b] = xa;
      this.zs[b] = za;
    }
  }
  /**
   * @param {!Array<!int>} targets
   */
  do_iswap(targets) {
    for (let k = 0; k < targets.length; k += 2) {
      let a = targets[k];
      let b = targets[k + 1];
      let xa = this.xs[a];
      let za = this.zs[a];
      let xb = this.xs[b];
      let zb = this.zs[b];
      let xab = xa ^ xb;
      this.xs[a] = xb;
      this.zs[a] = zb ^ xab;
      this.xs[b] = xa;
      this.zs[b] = za ^ xab;
    }
  }
  /**
   * @param {!Array<!int>} targets
   */
  do_sqrt_xx(targets) {
    for (let k = 0; k < targets.length; k += 2) {
      let a = targets[k];
      let b = targets[k + 1];
      let zab = this.zs[a] ^ this.zs[b];
      this.xs[a] ^= zab;
      this.xs[b] ^= zab;
    }
  }
  /**
   * @param {!Array<!int>} targets
   */
  do_sqrt_yy(targets) {
    for (let k = 0; k < targets.length; k += 2) {
      let a = targets[k];
      let b = targets[k + 1];
      let xa = this.xs[a];
      let za = this.zs[a];
      let xb = this.xs[b];
      let zb = this.zs[b];
      za ^= xa;
      zb ^= xb;
      xa ^= zb;
      xb ^= za;
      zb ^= xb;
      za ^= xa;
      this.xs[a] = za;
      this.zs[a] = xa;
      this.xs[b] = zb;
      this.zs[b] = xb;
    }
  }
  /**
   * @param {!Array<!int>} targets
   */
  do_sqrt_zz(targets) {
    for (let k = 0; k < targets.length; k += 2) {
      let a = targets[k];
      let b = targets[k + 1];
      let xab = this.xs[a] ^ this.xs[b];
      this.zs[a] ^= xab;
      this.zs[b] ^= xab;
    }
  }
  /**
   * @param {!Array<!int>} targets
   */
  do_xcx(targets) {
    for (let k = 0; k < targets.length; k += 2) {
      let control = targets[k];
      let target = targets[k + 1];
      this.xs[target] ^= this.zs[control];
      this.xs[control] ^= this.zs[target];
    }
  }
  /**
   * @param {!Array<!int>} targets
   */
  do_xcy(targets) {
    for (let k = 0; k < targets.length; k += 2) {
      let control = targets[k];
      let target = targets[k + 1];
      this.xs[target] ^= this.zs[control];
      this.zs[target] ^= this.zs[control];
      this.xs[control] ^= this.xs[target];
      this.xs[control] ^= this.zs[target];
    }
  }
  /**
   * @param {!Array<!int>} targets
   */
  do_ycy(targets) {
    for (let k = 0; k < targets.length; k += 2) {
      let control = targets[k];
      let target = targets[k + 1];
      let y = this.xs[control] ^ this.zs[control];
      this.xs[target] ^= y;
      this.zs[target] ^= y;
      y = this.xs[target] ^ this.zs[target];
      this.xs[control] ^= y;
      this.zs[control] ^= y;
    }
  }
  /**
   * @param {!Array<!int>} targets
   */
  do_cx(targets) {
    for (let k = 0; k < targets.length; k += 2) {
      let control = targets[k];
      let target = targets[k + 1];
      this.xs[target] ^= this.xs[control];
      this.zs[control] ^= this.zs[target];
    }
  }
  /**
   * @param {!Array<!int>} targets
   */
  do_cx_swap(targets) {
    for (let k = 0; k < targets.length; k += 2) {
      let c = targets[k];
      let t = targets[k + 1];
      let xc = this.xs[c];
      let zc = this.zs[c];
      let xt = this.xs[t];
      let zt = this.zs[t];
      this.xs[c] = xt ^ xc;
      this.zs[c] = zt;
      this.xs[t] = xc;
      this.zs[t] = zc ^ zt;
    }
  }
  /**
   * @param {!Array<!int>} targets
   */
  do_swap_cx(targets) {
    for (let k = 0; k < targets.length; k += 2) {
      let c = targets[k];
      let t = targets[k + 1];
      let xc = this.xs[c];
      let zc = this.zs[c];
      let xt = this.xs[t];
      let zt = this.zs[t];
      this.xs[c] = xt;
      this.zs[c] = zc ^ zt;
      this.xs[t] = xt ^ xc;
      this.zs[t] = zc;
    }
  }
  /**
   * @param {!Array<!int>} targets
   */
  do_cz_swap(targets) {
    for (let k = 0; k < targets.length; k += 2) {
      let c = targets[k];
      let t = targets[k + 1];
      let xc = this.xs[c];
      let zc = this.zs[c];
      let xt = this.xs[t];
      let zt = this.zs[t];
      this.xs[c] = xt;
      this.zs[c] = zt ^ xc;
      this.xs[t] = xc;
      this.zs[t] = zc ^ xt;
    }
  }
  /**
   * @param {!Array<!int>} targets
   */
  do_cy(targets) {
    for (let k = 0; k < targets.length; k += 2) {
      let control = targets[k];
      let target = targets[k + 1];
      this.xs[target] ^= this.xs[control];
      this.zs[target] ^= this.xs[control];
      this.zs[control] ^= this.zs[target];
      this.zs[control] ^= this.xs[target];
    }
  }
  /**
   * @param {!Array<!int>} targets
   */
  do_cz(targets) {
    for (let k = 0; k < targets.length; k += 2) {
      let control = targets[k];
      let target = targets[k + 1];
      this.zs[target] ^= this.xs[control];
      this.zs[control] ^= this.xs[target];
    }
  }
  /**
   * @param {!Gate} gate
   * @param {!Array<!int>} targets
   */
  do_gate(gate, targets) {
    gate.frameDo(this, targets);
  }
  /**
   * @param {!Gate} gate
   * @param {!Array<!int>} targets
   */
  undo_gate(gate, targets) {
    gate.frameUndo(this, targets);
  }
  /**
   * @param {*} other
   * @returns {!boolean}
   */
  isEqualTo(other) {
    if (!(other instanceof _PauliFrame) || other.num_frames !== this.num_frames || other.num_qubits !== this.num_qubits) {
      return false;
    }
    for (let q = 0; q < this.num_qubits; q++) {
      if (this.xs[q] !== other.xs[q] || this.zs[q] !== other.zs[q] || this.flags[q] !== other.flags[q]) {
        return false;
      }
    }
    return true;
  }
  /**
   * @returns {!string}
   */
  toString() {
    return this.to_strings().join("\n");
  }
};

// crumble/base/equate.js
function equate(subject, other) {
  if (subject === other || isExactlyNaN(subject) && isExactlyNaN(other)) {
    return true;
  }
  let customEquality = tryEquate_custom(subject, other);
  if (customEquality !== void 0) {
    return customEquality;
  }
  if (isAtomic(subject) || isAtomic(other) || !eqType(subject, other)) {
    return false;
  }
  if (subject instanceof Map) {
    return equate_Maps(subject, other);
  }
  if (subject instanceof Set) {
    return equate_Sets(subject, other);
  }
  if (isIndexable(subject)) {
    return equate_Indexables(subject, other);
  }
  return equate_Objects(subject, other);
}
var GENERIC_ARRAY_TYPES = [
  Float32Array,
  Float64Array,
  Int8Array,
  Int16Array,
  Int32Array,
  Uint8Array,
  Uint16Array,
  Uint32Array,
  Uint8ClampedArray
];
function isExactlyNaN(v) {
  return typeof v === "number" && isNaN(v);
}
function tryEquate_custom(subject, other) {
  if (!isAtomic(subject) && subject.constructor !== void 0 && subject.constructor.prototype.hasOwnProperty("isEqualTo")) {
    return subject.isEqualTo(other);
  }
  if (!isAtomic(other) && other.constructor !== void 0 && other.constructor.prototype.hasOwnProperty("isEqualTo")) {
    return other.isEqualTo(subject);
  }
  return void 0;
}
function isAtomic(value) {
  return value === null || value === void 0 || typeof value === "string" || typeof value === "number" || typeof value === "boolean";
}
function isIndexable(value) {
  return Array.isArray(value) || !GENERIC_ARRAY_TYPES.every((t) => !(value instanceof t));
}
function eqType(subject, other) {
  return subject.constructor.name === other.constructor.name;
}
function equate_Indexables(subject, other) {
  if (subject.length !== other.length) {
    return false;
  }
  for (let i = 0; i < subject.length; i++) {
    if (!equate(subject[i], other[i])) {
      return false;
    }
  }
  return true;
}
function equate_Iterables(subject, other) {
  let otherIter = other[Symbol.iterator]();
  for (let subjectItem of subject) {
    let otherItemDone = otherIter.next();
    if (otherItemDone.done || !equate(subjectItem, otherItemDone.value)) {
      return false;
    }
  }
  return otherIter.next().done;
}
function equate_Maps(subject, other) {
  if (subject.size !== other.size) {
    return false;
  }
  for (let [k, v] of subject) {
    if (!other.has(k)) {
      return false;
    }
    let otherV = other.get(k);
    if (!equate(v, otherV)) {
      return false;
    }
  }
  return true;
}
function equate_Sets(subject, other) {
  if (subject.size !== other.size) {
    return false;
  }
  for (let k of subject) {
    if (!other.has(k)) {
      return false;
    }
  }
  return true;
}
function objectKeys(obj) {
  let result = /* @__PURE__ */ new Set();
  for (let k in obj) {
    if (obj.hasOwnProperty(k)) {
      result.add(k);
    }
  }
  return result;
}
function equate_Objects(subject, other) {
  let keys = objectKeys(subject);
  if (!equate_Sets(keys, objectKeys(other))) {
    return false;
  }
  for (let k of keys) {
    if (k === Symbol.iterator) {
      continue;
    }
    if (!equate(subject[k], other[k])) {
      return false;
    }
  }
  let hasSubjectIter = subject[Symbol.iterator] !== void 0;
  let hasOtherIter = other[Symbol.iterator] !== void 0;
  if (hasSubjectIter !== hasOtherIter) {
    return false;
  }
  if (hasSubjectIter && hasOtherIter) {
    if (!equate_Iterables(
      /** @type {!Iterable} */
      subject,
      /** @type {!Iterable} */
      other
    )) {
      return false;
    }
  }
  return true;
}

// crumble/circuit/propagated_pauli_frames.js
var PropagatedPauliFrameLayer = class _PropagatedPauliFrameLayer {
  /**
   * @param {!Map<!int, !string>} bases
   * @param {!Set<!int>} errors
   * @param {!Array<!{q1: !int, q2: !int, color: !string}>} crossings
   */
  constructor(bases, errors, crossings) {
    this.bases = bases;
    this.errors = errors;
    this.crossings = crossings;
  }
  /**
   * @param {!Set<!int>} qids
   * @returns {!boolean}
   */
  touchesQidSet(qids) {
    for (let q of this.bases.keys()) {
      if (qids.has(q)) {
        return true;
      }
    }
    for (let q of this.errors.keys()) {
      if (qids.has(q)) {
        return true;
      }
    }
    return false;
  }
  /**
   * @param {!PropagatedPauliFrameLayer} other
   * @returns {!PropagatedPauliFrameLayer}
   */
  mergedWith(other) {
    return new _PropagatedPauliFrameLayer(
      new Map([...this.bases.entries(), ...other.bases.entries()]),
      /* @__PURE__ */ new Set([...this.errors, ...other.errors]),
      [...this.crossings, ...other.crossings]
    );
  }
  /**
   * @returns {!string}
   */
  toString() {
    let num_qubits = 0;
    for (let q of this.bases.keys()) {
      num_qubits = Math.max(num_qubits, q + 1);
    }
    for (let q of this.errors) {
      num_qubits = Math.max(num_qubits, q + 1);
    }
    for (let [q1, q2] of this.crossings) {
      num_qubits = Math.max(num_qubits, q1 + 1);
      num_qubits = Math.max(num_qubits, q2 + 1);
    }
    let result = '"';
    for (let q = 0; q < num_qubits; q++) {
      let b = this.bases.get(q);
      if (b === void 0) {
        b = "_";
      }
      if (this.errors.has(q)) {
        b = "E";
      }
      result += b;
    }
    result += '"';
    return result;
  }
};
var PropagatedPauliFrames = class _PropagatedPauliFrames {
  /**
   * @param {!Map<!int, !PropagatedPauliFrameLayer>} layers
   */
  constructor(layers) {
    this.id_layers = layers;
  }
  /**
   * @param {*} other
   * @returns {!boolean}
   */
  isEqualTo(other) {
    return other instanceof _PropagatedPauliFrames && equate(this.id_layers, other.id_layers);
  }
  /**
   * @returns {!string}
   */
  toString() {
    let layers = [...this.id_layers.keys()];
    layers.sort((a, b) => a - b);
    let lines = ["PropagatedPauliFrames {"];
    for (let k of layers) {
      lines.push(`    ${k}: ${this.id_layers.get(k)}`);
    }
    lines.push("}");
    return lines.join("\n");
  }
  /**
   * @param {!int} layer
   * @returns {!PropagatedPauliFrameLayer}
   */
  atLayer(layer) {
    let result = this.id_layers.get(layer);
    if (result === void 0) {
      result = new PropagatedPauliFrameLayer(/* @__PURE__ */ new Map(), /* @__PURE__ */ new Set(), []);
    }
    return result;
  }
  /**
   * @param {!Circuit} circuit
   * @param {!int} marker_index
   * @returns {!PropagatedPauliFrames}
   */
  static fromCircuit(circuit, marker_index) {
    let result = new _PropagatedPauliFrames(/* @__PURE__ */ new Map());
    let bases = (
      /** @type {!Map<!int, !string>} */
      /* @__PURE__ */ new Map()
    );
    for (let k = 0; k < circuit.layers.length; k++) {
      let layer = circuit.layers[k];
      let prevBases = bases;
      bases = layer.id_pauliFrameAfter(bases, marker_index);
      let errors = /* @__PURE__ */ new Set();
      for (let key of [...bases.keys()]) {
        let val = bases.get(key);
        if (val.startsWith("ERR:")) {
          errors.add(key);
          bases.set(key, val.substring(4));
        }
        if (bases.get(key) === "I") {
          bases.delete(key);
        }
      }
      let crossings = (
        /** @type {!Array<!{q1: !int, q2: !int, color: !string}>} */
        []
      );
      for (let op of layer.iter_gates_and_markers()) {
        if (op.gate.num_qubits === 2 && !op.gate.is_marker) {
          let [q1, q2] = op.id_targets;
          let differences = /* @__PURE__ */ new Set();
          for (let t of op.id_targets) {
            let b1 = bases.get(t);
            let b2 = prevBases.get(t);
            if (b1 !== b2) {
              if (b1 !== void 0) {
                differences.add(b1);
              }
              if (b2 !== void 0) {
                differences.add(b2);
              }
            }
          }
          if (differences.size > 0) {
            let color = "I";
            if (differences.size === 1) {
              color = [...differences][0];
            }
            crossings.push({ q1, q2, color });
          }
        }
      }
      if (bases.size > 0) {
        result.id_layers.set(
          k + 0.5,
          new PropagatedPauliFrameLayer(bases, /* @__PURE__ */ new Set(), [])
        );
      }
      if (errors.size > 0 || crossings.length > 0) {
        result.id_layers.set(
          k,
          new PropagatedPauliFrameLayer(/* @__PURE__ */ new Map(), errors, crossings)
        );
      }
    }
    return result;
  }
  /**
   * @param {!Circuit} circuit
   * @param {!Array<!int>} measurements
   * @returns {!PropagatedPauliFrames}
   */
  static fromMeasurements(circuit, measurements) {
    return _PropagatedPauliFrames.batchFromMeasurements(circuit, [
      measurements
    ])[0];
  }
  /**
   * @param {!Circuit} circuit
   * @param {!Array<!Array<!int>>} batchMeasurements
   * @returns {!Array<!PropagatedPauliFrames>}
   */
  static batchFromMeasurements(circuit, batchMeasurements) {
    let result = [];
    for (let k = 0; k < batchMeasurements.length; k += 32) {
      let batch = [];
      for (let j = k; j < k + 32 && j < batchMeasurements.length; j++) {
        batch.push(batchMeasurements[j]);
      }
      result.push(
        ..._PropagatedPauliFrames.batch32FromMeasurements(circuit, batch)
      );
    }
    return result;
  }
  /**
   * @param {!Circuit} circuit
   * @param {!Array<!Array<!int>>} batchMeasurements
   * @returns {!Array<!PropagatedPauliFrames>}
   */
  static batch32FromMeasurements(circuit, batchMeasurements) {
    let results = [];
    for (let k = 0; k < batchMeasurements.length; k++) {
      results.push(new _PropagatedPauliFrames(/* @__PURE__ */ new Map()));
    }
    let frame = new PauliFrame(
      batchMeasurements.length,
      circuit.allQubits().size
    );
    let measurementsBack = 0;
    let events = [];
    for (let k = 0; k < batchMeasurements.length; k++) {
      for (let k2 = 0; k2 < batchMeasurements[k].length; k2++) {
        events.push([k, batchMeasurements[k][k2]]);
      }
    }
    events.sort((a, b) => a[1] - b[1]);
    for (let k = circuit.layers.length - 1; k >= -1; k--) {
      let layer = k >= 0 ? circuit.layers[k] : new Layer();
      let targets = [...layer.id_ops.keys()];
      targets.reverse();
      for (let id of targets) {
        let op = layer.id_ops.get(id);
        if (op.id_targets[0] !== id) {
          continue;
        }
        frame.undo_gate(op.gate, [...op.id_targets]);
        for (let nm = op.countMeasurements(); nm > 0; nm -= 1) {
          measurementsBack -= 1;
          let target_mask = 0;
          while (events.length > 0 && events[events.length - 1][1] === measurementsBack) {
            let ev = events[events.length - 1];
            events.pop();
            target_mask ^= 1 << ev[0];
          }
          if (target_mask === 0) {
            continue;
          }
          for (let t_id = 0; t_id < op.id_targets.length; t_id++) {
            let t = op.id_targets[t_id];
            let basis;
            if (op.gate.name === "MX" || op.gate.name === "MRX" || op.gate.name === "MXX") {
              basis = "X";
            } else if (op.gate.name === "MY" || op.gate.name === "MRY" || op.gate.name === "MYY") {
              basis = "Y";
            } else if (op.gate.name === "M" || op.gate.name === "MR" || op.gate.name === "MZZ") {
              basis = "Z";
            } else if (op.gate.name === "MPAD") {
              continue;
            } else if (op.gate.name.startsWith("MPP:")) {
              basis = op.gate.name[t_id + 4];
            } else {
              throw new Error("Unhandled measurement gate: " + op.gate.name);
            }
            if (basis === "X") {
              frame.xs[t] ^= target_mask;
            } else if (basis === "Y") {
              frame.xs[t] ^= target_mask;
              frame.zs[t] ^= target_mask;
            } else if (basis === "Z") {
              frame.zs[t] ^= target_mask;
            } else {
              throw new Error("Unhandled measurement gate: " + op.gate.name);
            }
          }
        }
      }
      for (let t = 0; t < batchMeasurements.length; t++) {
        let m = 1 << t;
        let bases = /* @__PURE__ */ new Map();
        let errors = /* @__PURE__ */ new Set();
        for (let q = 0; q < frame.xs.length; q++) {
          let x = (frame.xs[q] & m) !== 0;
          let z = (frame.zs[q] & m) !== 0;
          if (x | z) {
            bases.set(q, "_XZY"[x + 2 * z]);
          }
          if (frame.flags[q] & m) {
            errors.add(q);
          }
        }
        if (bases.size > 0) {
          results[t].id_layers.set(
            k - 0.5,
            new PropagatedPauliFrameLayer(bases, /* @__PURE__ */ new Set(), [])
          );
        }
        if (errors.size > 0) {
          results[t].id_layers.set(
            k,
            new PropagatedPauliFrameLayer(/* @__PURE__ */ new Map(), errors, [])
          );
        }
      }
      for (let q = 0; q < frame.xs.length; q++) {
        frame.flags[q] = 0;
      }
    }
    return results;
  }
};

// crumble/draw/main_draw.js
function xyToPos(x, y) {
  if (x === void 0 || y === void 0) {
    return [void 0, void 0];
  }
  let focusX = x / pitch;
  let focusY = y / pitch;
  let roundedX = Math.floor(focusX * 2 + 0.5) / 2;
  let roundedY = Math.floor(focusY * 2 + 0.5) / 2;
  let centerX = roundedX * pitch;
  let centerY = roundedY * pitch;
  if (Math.abs(centerX - x) <= rad && Math.abs(centerY - y) <= rad && roundedX % 1 === roundedY % 1) {
    return [roundedX, roundedY];
  }
  return [void 0, void 0];
}
function draw(ctx, snap) {
  let circuit = snap.circuit;
  let numPropagatedLayers = 0;
  for (let layer of circuit.layers) {
    for (let op of layer.markers) {
      let gate = op.gate;
      if (gate.name === "MARKX" || gate.name === "MARKY" || gate.name === "MARKZ") {
        numPropagatedLayers = Math.max(numPropagatedLayers, op.args[0] + 1);
      }
    }
  }
  let c2dCoordTransform = (x, y) => [
    x * pitch - OFFSET_X,
    y * pitch - OFFSET_Y
  ];
  let qubitDrawCoords = (q) => {
    let x = circuit.qubitCoordData[2 * q];
    let y = circuit.qubitCoordData[2 * q + 1];
    return c2dCoordTransform(x, y);
  };
  let propagatedMarkerLayers = (
    /** @type {!Map<!int, !PropagatedPauliFrames>} */
    /* @__PURE__ */ new Map()
  );
  for (let mi = 0; mi < numPropagatedLayers; mi++) {
    propagatedMarkerLayers.set(
      mi,
      PropagatedPauliFrames.fromCircuit(circuit, mi)
    );
  }
  let { dets, obs } = circuit.collectDetectorsAndObservables(false);
  let batch_input = [];
  for (let mi = 0; mi < dets.length; mi++) {
    batch_input.push(dets[mi].mids);
  }
  for (let mi of obs.keys()) {
    batch_input.push(obs.get(mi));
  }
  let batch_output = PropagatedPauliFrames.batchFromMeasurements(
    circuit,
    batch_input
  );
  let batch_index = 0;
  for (let mi = 0; mi < dets.length; mi++) {
    propagatedMarkerLayers.set(~mi, batch_output[batch_index++]);
  }
  for (let mi of obs.keys()) {
    propagatedMarkerLayers.set(~mi ^ 1 << 30, batch_output[batch_index++]);
  }
  drawTimeline(
    ctx,
    snap,
    propagatedMarkerLayers,
    qubitDrawCoords,
    circuit.layers.length
  );
  ctx.save();
}

// crumble/keyboard/chord.js
var ChordEvent = class _ChordEvent {
  /**
   * @param {!boolean} inProgress
   * @param {!Set<!string>} chord
   * @param {!boolean} altKey
   * @param {!boolean} ctrlKey
   * @param {!boolean} metaKey
   * @param {!boolean} shiftKey
   */
  constructor(inProgress, chord, altKey, ctrlKey, metaKey, shiftKey) {
    this.inProgress = inProgress;
    this.chord = chord;
    this.altKey = altKey;
    this.shiftKey = shiftKey;
    this.ctrlKey = ctrlKey;
    this.metaKey = metaKey;
  }
  /**
   * @param {*} other
   * @return {!boolean}
   */
  isEqualTo(other) {
    return other instanceof _ChordEvent && this.inProgress === other.inProgress && equate(this.chord, other.chord) && this.altKey === other.altKey && this.shiftKey === other.shiftKey && this.ctrlKey === other.ctrlKey && this.metaKey === other.metaKey;
  }
  /**
   * @return {!string}
   */
  toString() {
    return `ChordEvent(
    inProgress=${this.inProgress},
    chord=${describe(this.chord)},
    altKey=${this.altKey},
    shiftKey=${this.shiftKey},
    ctrlKey=${this.ctrlKey},
    metaKey=${this.metaKey},
)`;
  }
};
var MODIFIER_KEYS = /* @__PURE__ */ new Set(["alt", "shift", "control", "meta"]);
var ACTION_KEYS = /* @__PURE__ */ new Set([
  "1",
  "2",
  "3",
  "4",
  "5",
  "6",
  "7",
  "8",
  "9",
  "0",
  "-",
  "=",
  "\\",
  "`"
]);
var Chorder = class {
  constructor() {
    this.curModifiers = /** @type {!Set<!string>} */
    /* @__PURE__ */ new Set();
    this.curPressed = /** @type {!Set<!string>} */
    /* @__PURE__ */ new Set();
    this.curChord = /** @type {!Set<!string>} */
    /* @__PURE__ */ new Set();
    this.queuedEvents = /** @type {!Array<!ChordEvent>} */
    [];
  }
  /**
   * @param {!boolean} inProgress
   */
  toEvent(inProgress) {
    return new ChordEvent(
      inProgress,
      new Set(this.curChord),
      this.curModifiers.has("alt"),
      this.curModifiers.has("control"),
      this.curModifiers.has("meta"),
      this.curModifiers.has("shift")
    );
  }
  /**
   * @param {!boolean} inProgress
   * @private
   */
  _queueEvent(inProgress) {
    this.queuedEvents.push(this.toEvent(inProgress));
  }
  handleFocusChanged() {
    this.curPressed.clear();
    this.curChord.clear();
    this.curModifiers.clear();
  }
  /**
   * @param {!KeyboardEvent} ev
   */
  handleKeyEvent(ev) {
    let key = ev.key.toLowerCase();
    if (key === "escape") {
      this.handleFocusChanged();
    }
    if (ev.type === "keydown") {
      let flag_key_pairs = [
        [ev.altKey, "alt"],
        [ev.shiftKey, "shift"],
        [ev.ctrlKey, "control"],
        [ev.metaKey, "meta"]
      ];
      for (let [b, k] of flag_key_pairs) {
        if (b) {
          this.curModifiers.add(k);
        } else {
          this.curModifiers.delete(k);
        }
      }
      if (!MODIFIER_KEYS.has(key)) {
        this.curPressed.add(key);
        this.curChord.add(key);
      }
      this._queueEvent(true);
    } else if (ev.type === "keyup") {
      if (!MODIFIER_KEYS.has(key)) {
        this.curPressed.delete(key);
        this._queueEvent(this.curPressed.size > 0 && !ACTION_KEYS.has(key));
        if (ACTION_KEYS.has(key)) {
          this.curChord.delete(key);
        }
        if (this.curPressed.size === 0) {
          this.curModifiers.clear();
          this.curChord.clear();
        }
      }
    } else {
      throw new Error("Not a recognized key event type: " + ev.type);
    }
  }
};

// crumble/base/cooldown_throttle.js
var CooldownThrottle = class {
  /**
   * @param {!function() : void} action
   * @param {!number} cooldownMs
   * @param {!number} slowActionCooldownPumpUpFactor
   * @param {!boolean=false} waitWithRequestAnimationFrame
   * @constructor
   */
  constructor(action, cooldownMs, slowActionCooldownPumpUpFactor = 0, waitWithRequestAnimationFrame = false) {
    this.action = action;
    this.cooldownDuration = cooldownMs;
    this.slowActionCooldownPumpupFactor = slowActionCooldownPumpUpFactor;
    this._waitWithRequestAnimationFrame = waitWithRequestAnimationFrame;
    this._state = "idle";
    this._cooldownStartTime = -Infinity;
  }
  _triggerIdle() {
    let remainingCooldownDuration = this.cooldownDuration - (performance.now() - this._cooldownStartTime);
    if (remainingCooldownDuration > 0) {
      this._forceIdleTriggerAfter(remainingCooldownDuration);
      return;
    }
    this._state = "running";
    let t0 = performance.now();
    try {
      this.action();
    } finally {
      let dt = performance.now() - t0;
      this._cooldownStartTime = performance.now() + dt * this.slowActionCooldownPumpupFactor;
      if (this._state === "running-and-triggered") {
        this._forceIdleTriggerAfter(this.cooldownDuration);
      } else {
        this._state = "idle";
      }
    }
  }
  /**
   * Asks for the action to be performed as soon as possible.
   * (No effect if the action was already requested but not performed yet.)
   */
  trigger() {
    switch (this._state) {
      case "idle":
        this._triggerIdle();
        break;
      case "waiting":
        break;
      case "running":
        this._state = "running-and-triggered";
        break;
      case "running-and-triggered":
        break;
      default:
        throw new Error("Unrecognized throttle state: " + this._state);
    }
  }
  /**
   * @private
   */
  _forceIdleTriggerAfter(duration) {
    this._state = "waiting";
    if (this._waitWithRequestAnimationFrame) {
      let iter;
      let start = performance.now();
      iter = () => {
        if (performance.now() < start + duration) {
          requestAnimationFrame(iter);
          return;
        }
        this._state = "idle";
        this._cooldownStartTime = -Infinity;
        this.trigger();
      };
      iter();
    } else {
      setTimeout(() => {
        this._state = "idle";
        this._cooldownStartTime = -Infinity;
        this.trigger();
      }, duration);
    }
  }
};

// crumble/base/obs.js
var Observable = class _Observable {
  /**
   * @param {!function(!function(T):void): (!function():void)} subscribe
   * @template T
   */
  constructor(subscribe) {
    this._subscribe = subscribe;
  }
  /**
   * @param {!function(T):void} observer
   * @returns {!function():void} unsubscriber
   * @template T
   */
  subscribe(observer) {
    return this._subscribe(observer);
  }
  /**
   * @param {T} items
   * @returns {!Observable.<T>} An observable that immediately forwards all the given items to any new subscriber.
   * @template T
   */
  static of(...items) {
    return new _Observable((observer) => {
      for (let item of items) {
        observer(item);
      }
      return () => {
      };
    });
  }
  /**
   * Subscribes to the receiving observable for a moment and returns any collected items.
   * @returns {!Array.<T>}
   * @template T
   */
  snapshot() {
    let result = [];
    let unsub = this.subscribe((e) => result.push(e));
    unsub();
    return result;
  }
  /**
   * @param {!function(TIn) : TOut} transformFunc
   * @returns {!Observable.<TOut>} An observable with the same items, but transformed by the given function.
   * @template TIn, TOut
   */
  map(transformFunc) {
    return new _Observable(
      (observer) => this.subscribe((item) => observer(transformFunc(item)))
    );
  }
  /**
   * @param {!function(T) : !boolean} predicate
   * @returns {!Observable.<T>} An observable with the same items, but skipping items that don't match the predicate.
   * @template T
   */
  filter(predicate) {
    return new _Observable(
      (observer) => this.subscribe((item) => {
        if (predicate(item)) {
          observer(item);
        }
      })
    );
  }
  /**
   * @param {!Observable.<T2>} other
   * @param {!function(T1, T2): TOut} mergeFunc
   * @returns {!Observable.<TOut>}
   * @template T1, T2, TOut
   */
  zipLatest(other, mergeFunc) {
    return new _Observable((observer) => {
      let has1 = false;
      let has2 = false;
      let last1;
      let last2;
      let unreg1 = this.subscribe((e1) => {
        last1 = e1;
        has1 = true;
        if (has2) {
          observer(mergeFunc(last1, last2));
        }
      });
      let unreg2 = other.subscribe((e2) => {
        last2 = e2;
        has2 = true;
        if (has1) {
          observer(mergeFunc(last1, last2));
        }
      });
      return () => {
        unreg1();
        unreg2();
      };
    });
  }
  /**
   * Returns an observable that keeps requesting animations frame callbacks and calling observers when they arrive.
   * @returns {!Observable.<undefined>}
   */
  static requestAnimationTicker() {
    return new _Observable((observer) => {
      let iter;
      let isDone = false;
      iter = () => {
        if (!isDone) {
          observer(void 0);
          window.requestAnimationFrame(iter);
        }
      };
      iter();
      return () => {
        isDone = true;
      };
    });
  }
  /**
   * @returns {!Observable.<T>} An observable that subscribes to each sub-observables arriving on this observable
   * in turns, only forwarding items from the latest sub-observable.
   * @template T
   */
  flattenLatest() {
    return new _Observable((observer) => {
      let unregLatest = () => {
      };
      let isDone = false;
      let unregAll = this.subscribe((subObservable) => {
        if (isDone) {
          return;
        }
        let prevUnreg = unregLatest;
        unregLatest = subObservable.subscribe(observer);
        prevUnreg();
      });
      return () => {
        isDone = true;
        unregLatest();
        unregAll();
      };
    });
  }
  /**
   * @param {!function(T):void} action
   * @returns {!Observable.<T>}
   * @template T
   */
  peek(action) {
    return this.map((e) => {
      action(e);
      return e;
    });
  }
  /**
   * @returns {!Observable.<T>} An observable that forwards all the items from all the observables observed by the
   * receiving observable of observables.
   * @template T
   */
  flatten() {
    return new _Observable((observer) => {
      let unsubs = [];
      unsubs.push(
        this.subscribe(
          (observable) => unsubs.push(observable.subscribe(observer))
        )
      );
      return () => {
        for (let unsub of unsubs) {
          unsub();
        }
      };
    });
  }
  /**
   * Starts a timer after each completed send, delays sending any more values until the timer expires, and skips
   * intermediate values when a newer value arrives from the source while the timer is still running down.
   * @param {!number} cooldownMillis
   * @returns {!Observable.<T>}
   * @template T
   */
  throttleLatest(cooldownMillis) {
    return new _Observable((observer) => {
      let latest = void 0;
      let isKilled = false;
      let throttle = new CooldownThrottle(() => {
        if (!isKilled) {
          observer(latest);
        }
      }, cooldownMillis);
      let unsub = this.subscribe((e) => {
        latest = e;
        throttle.trigger();
      });
      return () => {
        isKilled = true;
        unsub();
      };
    });
  }
  /**
   * @param {!HTMLElement|!HTMLDocument} element
   * @param {!string} eventKey
   * @returns {!Observable.<*>} An observable corresponding to an event fired from an element.
   */
  static elementEvent(element, eventKey) {
    return new _Observable((observer) => {
      element.addEventListener(eventKey, observer);
      return () => element.removeEventListener(eventKey, observer);
    });
  }
  /**
   *
   * @param {!int} count
   * @returns {!Observable.<T>}
   * @template T
   */
  skip(count) {
    return new _Observable((observer) => {
      let remaining = count;
      return this.subscribe((item) => {
        if (remaining > 0) {
          remaining -= 1;
        } else {
          observer(item);
        }
      });
    });
  }
  /**
   * @returns {!Observable.<T>} An observable with the same events, but filtering out any event value that's the same
   * as the previous one.
   * @template T
   */
  whenDifferent(equater = void 0) {
    let eq = equater || ((e1, e2) => e1 === e2);
    return new _Observable((observer) => {
      let hasLast = false;
      let last = void 0;
      return this.subscribe((item) => {
        if (!hasLast || !eq(last, item)) {
          last = item;
          hasLast = true;
          observer(item);
        }
      });
    });
  }
};
var ObservableSource = class {
  constructor() {
    this._observers = [];
    this._observable = new Observable((observer) => {
      this._observers.push(observer);
      let didRun = false;
      return () => {
        if (!didRun) {
          didRun = true;
          this._observers.splice(this._observers.indexOf(observer), 1);
        }
      };
    });
  }
  /**
   * @returns {!Observable.<T>}
   * @template T
   */
  observable() {
    return this._observable;
  }
  /**
   * @param {T} eventValue
   * @template T
   */
  send(eventValue) {
    for (let obs of this._observers) {
      obs(eventValue);
    }
  }
};
var ObservableValue = class {
  /**
   * @param {T=undefined} initialValue
   * @template T
   */
  constructor(initialValue = void 0) {
    this._value = initialValue;
    this._source = new ObservableSource();
    this._observable = new Observable((observer) => {
      observer(this._value);
      return this._source.observable().subscribe(observer);
    });
  }
  /**
   * @returns {!Observable}
   */
  observable() {
    return this._observable;
  }
  /**
   * @param {T} newValue
   * @template T
   */
  set(newValue) {
    this._value = newValue;
    this._source.send(newValue);
  }
  /**
   * @returns {T} The current value.
   * @template T
   */
  get() {
    return this._value;
  }
};

// crumble/base/revision.js
var Revision = class _Revision {
  /**
   * @param {!Array.<*>} history
   * @param {!int} index
   * @param {!boolean} isWorkingOnCommit
   */
  constructor(history, index, isWorkingOnCommit) {
    if (index < 0 || index >= history.length) {
      throw new Error(`Bad index: ${{ history, index, isWorkingOnCommit }}`);
    }
    if (!Array.isArray(history)) {
      throw new Error(`Bad history: ${{ history, index, isWorkingOnCommit }}`);
    }
    this.history = history;
    this.index = index;
    this.isWorkingOnCommit = isWorkingOnCommit;
    this._changes = new ObservableSource();
    this._latestActiveCommit = new ObservableValue(this.history[this.index]);
  }
  /**
   * @returns {!Observable.<*>}
   */
  changes() {
    return this._changes.observable();
  }
  /**
   * @returns {!Observable.<*>}
   */
  latestActiveCommit() {
    return this._latestActiveCommit.observable();
  }
  /**
   * Returns a snapshot of the current commit.
   * @returns {*}
   */
  peekActiveCommit() {
    return this._latestActiveCommit.get();
  }
  /**
   * Returns a cleared revision history, starting at the given state.
   * @param {*} state
   */
  static startingAt(state) {
    return new _Revision([state], 0, false);
  }
  /**
   * @returns {!boolean}
   */
  isAtBeginningOfHistory() {
    return this.index === 0 && !this.isWorkingOnCommit;
  }
  /**
   * @returns {!boolean}
   */
  isAtEndOfHistory() {
    return this.index === this.history.length - 1;
  }
  /**
   * Throws away all revisions and resets the given state.
   * @param {*} state
   * @returns {void}
   */
  clear(state) {
    this.history = [state];
    this.index = 0;
    this.isWorkingOnCommit = false;
    this._latestActiveCommit.set(state);
    this._changes.send(state);
  }
  /**
   * Indicates that there are pending changes, so that a following 'undo' will return to the current state instead of
   * the previous state.
   * @returns {void}
   */
  startedWorkingOnCommit(newCheckpoint) {
    this.isWorkingOnCommit = newCheckpoint !== this.history[this.index];
    this._changes.send(void 0);
  }
  /**
   * Indicates that pending changes were discarded, so that a following 'undo' should return to the previous state
   * instead of the current state.
   * @returns {*} The new current state.
   */
  cancelCommitBeingWorkedOn() {
    this.isWorkingOnCommit = false;
    let result = this.history[this.index];
    this._latestActiveCommit.set(result);
    this._changes.send(result);
    return result;
  }
  /**
   * Throws away future states, appends the given state, and marks it as the current state
   * @param {*} newCheckpoint
   * @returns {void}
   */
  commit(newCheckpoint) {
    if (newCheckpoint === this.history[this.index]) {
      this.cancelCommitBeingWorkedOn();
      return;
    }
    this.isWorkingOnCommit = false;
    this.index += 1;
    this.history.splice(this.index, this.history.length - this.index);
    this.history.push(newCheckpoint);
    this._latestActiveCommit.set(newCheckpoint);
    this._changes.send(newCheckpoint);
  }
  /**
   * Marks the previous state as the current state and returns it (or resets to the current state if
   * 'working on a commit' was indicated).
   * @returns {undefined|*} The new current state, or undefined if there's nothing to undo.
   */
  undo() {
    if (!this.isWorkingOnCommit) {
      if (this.index === 0) {
        return void 0;
      }
      this.index -= 1;
    }
    this.isWorkingOnCommit = false;
    let result = this.history[this.index];
    this._latestActiveCommit.set(result);
    this._changes.send(result);
    return result;
  }
  /**
   * Marks the next state as the current state and returns it (or does nothing if there is no next state).
   * @returns {undefined|*} The new current state, or undefined if there's nothing to redo.
   */
  redo() {
    if (this.index + 1 === this.history.length) {
      return void 0;
    }
    this.index += 1;
    this.isWorkingOnCommit = false;
    let result = this.history[this.index];
    this._latestActiveCommit.set(result);
    this._changes.send(result);
    return result;
  }
  /**
   * @returns {!string} A description of the revision.
   */
  toString() {
    return "Revision(" + describe({
      index: this.index,
      count: this.history.length,
      workingOnCommit: this.isWorkingOnCommit,
      head: this.history[this.index]
    }) + ")";
  }
  /**
   * Determines if two revisions currently have the same state.
   * @param {*|!Revision} other
   * @returns {!boolean}
   */
  isEqualTo(other) {
    return other instanceof _Revision && this.index === other.index && this.isWorkingOnCommit === other.isWorkingOnCommit && equate(this.history, other.history);
  }
};

// crumble/draw/state_snapshot.js
var StateSnapshot = class {
  /**
   * @param {!Circuit} circuit
   * @param {!int} curLayer
   * @param {!Map<!string, ![!number, !number]>} focusedSet
   * @param {!Map<!string, ![!number, !number]>} timelineSet
   * @param {!number} curMouseX
   * @param {!number} curMouseY
   * @param {!number} mouseDownX
   * @param {!number} mouseDownY
   * @param {!Array<![!number, !number]>} boxHighlightPreview
   */
  constructor(circuit, curLayer, focusedSet, timelineSet, curMouseX, curMouseY, mouseDownX, mouseDownY, boxHighlightPreview) {
    this.circuit = circuit.copy();
    this.curLayer = curLayer;
    this.focusedSet = new Map(focusedSet.entries());
    this.timelineSet = new Map(timelineSet.entries());
    this.curMouseX = curMouseX;
    this.curMouseY = curMouseY;
    this.mouseDownX = mouseDownX;
    this.mouseDownY = mouseDownY;
    this.boxHighlightPreview = [...boxHighlightPreview];
    while (this.circuit.layers.length <= this.curLayer) {
      this.circuit.layers.push(new Layer());
    }
  }
  /**
   * @returns {!Set<!int>}
   */
  id_usedQubits() {
    return this.circuit.allQubits();
  }
  /**
   * @returns {!Array<!int>}
   */
  timelineQubits() {
    let used = this.id_usedQubits();
    let qubits = [];
    if (this.timelineSet.size > 0) {
      let c2q = this.circuit.coordToQubitMap();
      for (let key of this.timelineSet.keys()) {
        let q = c2q.get(key);
        if (q !== void 0) {
          qubits.push(q);
        }
      }
    } else {
      qubits.push(...used.values());
    }
    return qubits.filter((q) => used.has(q));
  }
};

// crumble/editor/editor_state.js
function rotated45Transform(steps) {
  let vx = [1, 0];
  let vy = [0, 1];
  let s = (x, y) => [x - y, x + y];
  steps %= 8;
  steps += 8;
  steps %= 8;
  for (let k = 0; k < steps; k++) {
    vx = s(vx[0], vx[1]);
    vy = s(vy[0], vy[1]);
  }
  return (x, y) => [vx[0] * x + vy[0] * y, vx[1] * x + vy[1] * y];
}
var EditorState = class {
  /**
   * @param {!HTMLCanvasElement} canvas
   */
  constructor(canvas) {
    this.rev = Revision.startingAt("");
    this.canvas = canvas;
    this.curMouseY = /** @type {undefined|!number} */
    void 0;
    this.curMouseX = /** @type {undefined|!number} */
    void 0;
    this.chorder = new Chorder();
    this.curLayer = 0;
    this.focusedSet = /** @type {!Map<!string, ![!number, !number]>} */
    /* @__PURE__ */ new Map();
    this.timelineSet = /** @type {!Map<!string, ![!number, !number]>} */
    /* @__PURE__ */ new Map();
    this.mouseDownX = /** @type {undefined|!number} */
    void 0;
    this.mouseDownY = /** @type {undefined|!number} */
    void 0;
    this.obs_val_draw_state = /** @type {!ObservableValue<StateSnapshot>} */
    new ObservableValue(
      this.toSnapshot(void 0)
    );
  }
  flipTwoQubitGateOrderAtFocus(preview) {
    let newCircuit = this.copyOfCurCircuit();
    let layer = newCircuit.layers[this.curLayer];
    let flipped_op_first_targets = /* @__PURE__ */ new Set();
    let pairs = [
      ["CX", "reverse"],
      ["CY", "reverse"],
      ["XCY", "reverse"],
      ["CXSWAP", "reverse"],
      ["XCZ", "reverse"],
      ["XCY", "reverse"],
      ["YCX", "reverse"],
      ["SWAPCX", "reverse"],
      ["RX", "MX"],
      ["R", "M"],
      ["RY", "MY"]
    ];
    let rev = /* @__PURE__ */ new Map();
    for (let p of pairs) {
      rev.set(p[0], p[1]);
      rev.set(p[1], p[0]);
    }
    for (let q of this.focusedSet.keys()) {
      let op = layer.id_ops.get(newCircuit.coordToQubitMap().get(q));
      if (op !== void 0 && rev.has(op.gate.name)) {
        flipped_op_first_targets.add(op.id_targets[0]);
      }
    }
    for (let q of flipped_op_first_targets) {
      let op = layer.id_ops.get(q);
      let other = rev.get(op.gate.name);
      if (other === "reverse") {
        layer.id_ops.get(q).id_targets.reverse();
      } else {
        op.gate = GATE_MAP.get(other);
      }
    }
    this.commit_or_preview(newCircuit, preview);
  }
  reverseLayerOrderFromFocusToEmptyLayer(preview) {
    let newCircuit = this.copyOfCurCircuit();
    let end = this.curLayer;
    while (end < newCircuit.layers.length && !newCircuit.layers[end].empty()) {
      end += 1;
    }
    let layers = [];
    for (let k = this.curLayer; k < end; k++) {
      layers.push(newCircuit.layers[k]);
    }
    layers.reverse();
    for (let k = this.curLayer; k < end; k++) {
      newCircuit.layers[k] = layers[k - this.curLayer];
    }
    this.commit_or_preview(newCircuit, preview);
  }
  /**
   * @return {!Circuit}
   */
  copyOfCurCircuit() {
    let result = Circuit.fromStimCircuit(this.rev.peekActiveCommit());
    while (result.layers.length <= this.curLayer) {
      result.layers.push(new Layer());
    }
    return result;
  }
  clearFocus() {
    this.focusedSet.clear();
    this.force_redraw();
  }
  /**
   * @param {!boolean} preview
   */
  deleteAtFocus(preview) {
    let newCircuit = this.copyOfCurCircuit();
    let c2q = newCircuit.coordToQubitMap();
    for (let key of this.focusedSet.keys()) {
      let q = c2q.get(key);
      if (q !== void 0) {
        newCircuit.layers[this.curLayer].id_pop_at(q);
      }
    }
    this.commit_or_preview(newCircuit, preview);
  }
  /**
   * @param {!boolean} preview
   */
  deleteCurLayer(preview) {
    let c = this.copyOfCurCircuit();
    c.layers.splice(this.curLayer, 1);
    this.commit_or_preview(c, preview);
  }
  /**
   * @param {!boolean} preview
   */
  insertLayer(preview) {
    let c = this.copyOfCurCircuit();
    c.layers.splice(this.curLayer, 0, new Layer());
    this.commit_or_preview(c, preview);
  }
  undo() {
    this.rev.undo();
  }
  redo() {
    this.rev.redo();
  }
  /**
   * @param {!Circuit} newCircuit
   * @param {!boolean} preview
   */
  commit_or_preview(newCircuit, preview) {
    if (preview) {
      this.preview(newCircuit);
    } else {
      this.commit(newCircuit);
    }
  }
  /**
   * @param {!Circuit} newCircuit
   */
  commit(newCircuit) {
    while (newCircuit.layers.length > 0 && newCircuit.layers[newCircuit.layers.length - 1].isEmpty()) {
      newCircuit.layers.pop();
    }
    this.rev.commit(newCircuit.toStimCircuit());
  }
  /**
   * @param {!Circuit} newCircuit
   */
  preview(newCircuit) {
    this.rev.startedWorkingOnCommit(newCircuit.toStimCircuit());
    this.obs_val_draw_state.set(this.toSnapshot(newCircuit));
  }
  /**
   * @param {undefined|!Circuit} previewCircuit
   * @returns {!StateSnapshot}
   */
  toSnapshot(previewCircuit) {
    if (previewCircuit === void 0) {
      previewCircuit = this.copyOfCurCircuit();
    }
    return new StateSnapshot(
      previewCircuit,
      this.curLayer,
      this.focusedSet,
      this.timelineSet,
      this.curMouseX,
      this.curMouseY,
      this.mouseDownX,
      this.mouseDownY,
      this.currentPositionsBoxesByMouseDrag(
        this.chorder.curModifiers.has("alt")
      )
    );
  }
  force_redraw() {
    let previewedCircuit = this.obs_val_draw_state.get().circuit;
    this.obs_val_draw_state.set(this.toSnapshot(previewedCircuit));
  }
  clearCircuit() {
    this.commit(new Circuit(new Float64Array([]), []));
  }
  clearMarkers() {
    let c = this.copyOfCurCircuit();
    for (let layer of c.layers) {
      layer.markers = layer.markers.filter(
        (e) => e.gate.name !== "MARKX" && e.gate.name !== "MARKY" && e.gate.name !== "MARKZ"
      );
    }
    this.commit(c);
  }
  /**
   * @param {!boolean} parityLock
   * @returns {!Array<![!int, !int]>}
   */
  currentPositionsBoxesByMouseDrag(parityLock) {
    let curMouseX = this.curMouseX;
    let curMouseY = this.curMouseY;
    let mouseDownX = this.mouseDownX;
    let mouseDownY = this.mouseDownY;
    let result = [];
    if (curMouseX !== void 0 && mouseDownX !== void 0) {
      let [sx, sy] = xyToPos(mouseDownX, mouseDownY);
      let x1 = Math.min(curMouseX, mouseDownX);
      let x2 = Math.max(curMouseX, mouseDownX);
      let y1 = Math.min(curMouseY, mouseDownY);
      let y2 = Math.max(curMouseY, mouseDownY);
      let gap = pitch / 4 - rad;
      x1 += gap;
      x2 -= gap;
      y1 += gap;
      y2 -= gap;
      x1 = Math.floor(x1 * 2 / pitch + 0.5) / 2;
      x2 = Math.floor(x2 * 2 / pitch + 0.5) / 2;
      y1 = Math.floor(y1 * 2 / pitch + 0.5) / 2;
      y2 = Math.floor(y2 * 2 / pitch + 0.5) / 2;
      let b = 1;
      if (x1 === x2 || y1 === y2) {
        b = 2;
      }
      for (let x = x1; x <= x2; x += 0.5) {
        for (let y = y1; y <= y2; y += 0.5) {
          if (x % 1 === y % 1) {
            if (!parityLock || sx % b === x % b && sy % b === y % b) {
              result.push([x, y]);
            }
          }
        }
      }
    }
    return result;
  }
  /**
   * @param {!function(!number, !number): ![!number, !number]} coordTransform
   * @param {!boolean} preview
   * @param {!boolean} moveFocus
   */
  applyCoordinateTransform(coordTransform, preview, moveFocus) {
    let c = this.copyOfCurCircuit();
    c = c.afterCoordTransform(coordTransform);
    if (!preview && moveFocus) {
      let trans = (m) => {
        let new_m = /* @__PURE__ */ new Map();
        for (let [x, y] of m.values()) {
          [x, y] = coordTransform(x, y);
          new_m.set(`${x},${y}`, [x, y]);
        }
        return new_m;
      };
      this.timelineSet = trans(this.timelineSet);
      this.focusedSet = trans(this.focusedSet);
    }
    this.commit_or_preview(c, preview);
  }
  /**
   * @param {!int} steps
   * @param {!boolean} preview
   */
  rotate45(steps, preview) {
    let t1 = rotated45Transform(steps);
    let t2 = this.copyOfCurCircuit().afterCoordTransform(t1).coordTransformForRectification();
    this.applyCoordinateTransform(
      (x, y) => {
        [x, y] = t1(x, y);
        return t2(x, y);
      },
      preview,
      true
    );
  }
  /**
   * @param {!int} newLayer
   */
  changeCurLayerTo(newLayer) {
    this.curLayer = Math.max(newLayer, 0);
    this.force_redraw();
  }
  /**
   * @param {!Array<![!number, !number]>} newFocus
   * @param {!boolean} unionMode
   * @param {!boolean} xorMode
   */
  changeFocus(newFocus, unionMode, xorMode) {
    if (!unionMode && !xorMode) {
      this.focusedSet.clear();
    }
    for (let [x, y] of newFocus) {
      let k = `${x},${y}`;
      if (xorMode && this.focusedSet.has(k)) {
        this.focusedSet.delete(k);
      } else {
        this.focusedSet.set(k, [x, y]);
      }
    }
    this.force_redraw();
  }
  /**
   * @param {!Iterable<int>} affectedQubits
   * @returns {!Map<!int, !string>}
   * @private
   */
  _inferBases(affectedQubits) {
    let inferredBases = /* @__PURE__ */ new Map();
    let layer = this.copyOfCurCircuit().layers[this.curLayer];
    for (let q of [...affectedQubits]) {
      let op = layer.id_ops.get(q);
      if (op !== void 0) {
        if (op.gate.name === "RX" || op.gate.name === "MX" || op.gate.name === "MRX") {
          inferredBases.set(q, "X");
        } else if (op.gate.name === "RY" || op.gate.name === "MY" || op.gate.name === "MRY") {
          inferredBases.set(q, "Y");
        } else if (op.gate.name === "R" || op.gate.name === "M" || op.gate.name === "MR") {
          inferredBases.set(q, "Z");
        } else if (op.gate.name === "MXX" || op.gate.name === "MYY" || op.gate.name === "MZZ") {
          let opBasis = op.gate.name[1];
          for (let q2 of op.id_targets) {
            inferredBases.set(q2, opBasis);
          }
        } else if (op.gate.name.startsWith("MPP:") && op.gate.tableau_map === void 0 && op.id_targets.length === op.gate.name.length - 4) {
          let bases = op.gate.name.substring(4);
          for (let k = 0; k < op.id_targets.length; k++) {
            let q2 = op.id_targets[k];
            inferredBases.set(q2, bases[k]);
          }
        }
      }
    }
    return inferredBases;
  }
  /**
   * @param {!boolean} preview
   * @param {!int} markIndex
   */
  markFocusInferBasis(preview, markIndex) {
    let newCircuit = this.copyOfCurCircuit().withCoordsIncluded(
      this.focusedSet.values()
    );
    let c2q = newCircuit.coordToQubitMap();
    let affectedQubits = /* @__PURE__ */ new Set();
    for (let key of this.focusedSet.keys()) {
      affectedQubits.add(c2q.get(key));
    }
    let forcedBases = this._inferBases(affectedQubits);
    for (let q of forcedBases.keys()) {
      affectedQubits.add(q);
    }
    let seenBases = new Set(forcedBases.values());
    seenBases.delete(void 0);
    let defaultBasis;
    if (seenBases.size === 1) {
      defaultBasis = [...seenBases][0];
    } else {
      defaultBasis = "Z";
    }
    let layer = newCircuit.layers[this.curLayer];
    for (let q of affectedQubits) {
      let basis = forcedBases.get(q);
      if (basis === void 0) {
        basis = defaultBasis;
      }
      let gate = GATE_MAP.get(`MARK${basis}`).withDefaultArgument(markIndex);
      layer.put(
        new Operation(
          gate,
          "",
          new Float32Array([markIndex]),
          new Uint32Array([q])
        )
      );
    }
    this.commit_or_preview(newCircuit, preview);
  }
  /**
   * @param {!boolean} preview
   */
  unmarkFocusInferBasis(preview) {
    let newCircuit = this.copyOfCurCircuit().withCoordsIncluded(
      this.focusedSet.values()
    );
    let c2q = newCircuit.coordToQubitMap();
    let affectedQubits = /* @__PURE__ */ new Set();
    for (let key of this.focusedSet.keys()) {
      affectedQubits.add(c2q.get(key));
    }
    let inferredBases = this._inferBases(affectedQubits);
    for (let q of inferredBases.keys()) {
      affectedQubits.add(q);
    }
    for (let q of affectedQubits) {
      if (q !== void 0) {
        newCircuit.layers[this.curLayer].id_dropMarkersAt(q);
      }
    }
    this.commit_or_preview(newCircuit, preview);
  }
  /**
   * @param {!boolean} preview
   * @param {!Gate} gate
   * @param {!Array<!number>} gate_args
   */
  _writeSingleQubitGateToFocus(preview, gate, gate_args) {
    let newCircuit = this.copyOfCurCircuit().withCoordsIncluded(
      this.focusedSet.values()
    );
    let c2q = newCircuit.coordToQubitMap();
    for (let key of this.focusedSet.keys()) {
      newCircuit.layers[this.curLayer].put(
        new Operation(
          gate,
          "",
          new Float32Array(gate_args),
          new Uint32Array([c2q.get(key)])
        )
      );
    }
    this.commit_or_preview(newCircuit, preview);
  }
  /**
   * @param {!boolean} preview
   * @param {!Gate} gate
   * @param {!Array<!number>} gate_args
   */
  _writeTwoQubitGateToFocus(preview, gate, gate_args) {
    let newCircuit = this.copyOfCurCircuit();
    let [x, y] = xyToPos(this.curMouseX, this.curMouseY);
    let [minX, minY] = minXY(this.focusedSet.values());
    let coords = [];
    if (x !== void 0 && minX !== void 0 && !this.focusedSet.has(`${x},${y}`)) {
      let dx = x - minX;
      let dy = y - minY;
      for (let [vx, vy] of this.focusedSet.values()) {
        coords.push([vx, vy]);
        coords.push([vx + dx, vy + dy]);
      }
    } else if (this.focusedSet.size === 2) {
      for (let [vx, vy] of this.focusedSet.values()) {
        coords.push([vx, vy]);
      }
    }
    if (coords.length > 0) {
      newCircuit = newCircuit.withCoordsIncluded(coords);
      let c2q = newCircuit.coordToQubitMap();
      for (let k = 0; k < coords.length; k += 2) {
        let [x0, y0] = coords[k];
        let [x1, y1] = coords[k + 1];
        let q0 = c2q.get(`${x0},${y0}`);
        let q1 = c2q.get(`${x1},${y1}`);
        newCircuit.layers[this.curLayer].put(
          new Operation(
            gate,
            "",
            new Float32Array(gate_args),
            new Uint32Array([q0, q1])
          )
        );
      }
    }
    this.commit_or_preview(newCircuit, preview);
  }
  /**
   * @param {!boolean} preview
   * @param {!Gate} gate
   * @param {!Array<!number>} gate_args
   */
  _writeVariableQubitGateToFocus(preview, gate, gate_args) {
    if (this.focusedSet.size === 0) {
      return;
    }
    let pairs = [];
    let cx = 0;
    let cy = 0;
    for (let xy of this.focusedSet.values()) {
      pairs.push(xy);
      cx += xy[0];
      cy += xy[1];
    }
    cx /= pairs.length;
    cy /= pairs.length;
    pairs.sort((a, b) => {
      let [x1, y1] = a;
      let [x2, y2] = b;
      return Math.atan2(y1 - cy, x1 - cx) - Math.atan2(y2 - cy, x2 - cx);
    });
    let newCircuit = this.copyOfCurCircuit().withCoordsIncluded(
      this.focusedSet.values()
    );
    let c2q = newCircuit.coordToQubitMap();
    let qs = new Uint32Array(this.focusedSet.size);
    for (let k = 0; k < pairs.length; k++) {
      let [x, y] = pairs[k];
      qs[k] = c2q.get(`${x},${y}`);
    }
    newCircuit.layers[this.curLayer].put(
      new Operation(gate, "", new Float32Array(gate_args), qs)
    );
    this.commit_or_preview(newCircuit, preview);
  }
  /**
   * @param {!boolean} preview
   * @param {!Gate} gate
   * @param {undefined|!Array<!number>=} gate_args
   */
  writeGateToFocus(preview, gate, gate_args = void 0) {
    if (gate_args === void 0) {
      if (gate.defaultArgument === void 0) {
        gate_args = [];
      } else {
        gate_args = [gate.defaultArgument];
      }
    }
    if (gate.num_qubits === 1) {
      this._writeSingleQubitGateToFocus(preview, gate, gate_args);
    } else if (gate.num_qubits === 2) {
      this._writeTwoQubitGateToFocus(preview, gate, gate_args);
    } else {
      this._writeVariableQubitGateToFocus(preview, gate, gate_args);
    }
  }
  writeMarkerToObservable(preview, marker_index) {
    this._writeMarkerToDetOrObs(preview, marker_index, false);
  }
  writeMarkerToDetector(preview, marker_index) {
    this._writeMarkerToDetOrObs(preview, marker_index, true);
  }
  _writeMarkerToDetOrObs(preview, marker_index, isDet) {
    let newCircuit = this.copyOfCurCircuit();
    let argIndex = isDet ? newCircuit.collectDetectorsAndObservables(false).dets.length : marker_index;
    let prop = PropagatedPauliFrames.fromCircuit(newCircuit, marker_index);
    for (let k = 0; k < newCircuit.layers.length; k++) {
      let before = k === 0 ? new PropagatedPauliFrameLayer(/* @__PURE__ */ new Map(), /* @__PURE__ */ new Set(), []) : prop.atLayer(k - 0.5);
      let after = prop.atLayer(k + 0.5);
      let layer = newCircuit.layers[k];
      for (let q of /* @__PURE__ */ new Set([...before.bases.keys(), ...after.bases.keys()])) {
        let b1 = before.bases.get(q);
        let b2 = after.bases.get(q);
        let op = layer.id_ops.get(q);
        let name = op !== void 0 ? op.gate.name : void 0;
        let transition = void 0;
        if (name === "MR" || name === "MRX" || name === "MRY") {
          transition = b1;
        } else if (op !== void 0 && op.countMeasurements() > 0) {
          if (b1 === void 0) {
            transition = b2;
          } else if (b2 === void 0) {
            transition = b1;
          } else if (b1 !== b2) {
            let s = /* @__PURE__ */ new Set(["X", "Y", "Z"]);
            s.delete(b1);
            s.delete(b2);
            transition = [...s][0];
          }
        }
        if (transition !== void 0) {
          layer.markers.push(
            new Operation(
              GATE_MAP.get(isDet ? "DETECTOR" : "OBSERVABLE_INCLUDE"),
              "",
              new Float32Array([argIndex]),
              op.id_targets
            )
          );
        }
      }
      layer.markers = layer.markers.filter(
        (op) => !op.gate.name.startsWith("MARK") || op.args[0] !== marker_index
      );
    }
    this.commit_or_preview(newCircuit, preview);
  }
  addDissipativeOverlapToMarkers(preview, marker_index) {
    let newCircuit = this.copyOfCurCircuit();
    let prop = PropagatedPauliFrames.fromCircuit(newCircuit, marker_index);
    let k = this.curLayer;
    let before = k === 0 ? new PropagatedPauliFrameLayer(/* @__PURE__ */ new Map(), /* @__PURE__ */ new Set(), []) : prop.atLayer(k - 0.5);
    let after = prop.atLayer(k + 0.5);
    let layer = newCircuit.layers[k];
    let processedQubits = /* @__PURE__ */ new Set();
    for (let q of /* @__PURE__ */ new Set([...before.bases.keys(), ...after.bases.keys()])) {
      if (processedQubits.has(q)) {
        continue;
      }
      let b1 = before.bases.get(q);
      let b2 = after.bases.get(q);
      let op = layer.id_ops.get(q);
      if (op === void 0) {
        continue;
      }
      let name = op.gate.name;
      let basis = void 0;
      if (name === "R" || name === "M" || name === "MR") {
        basis = "Z";
      } else if (name === "RX" || name === "MX" || name === "MRX") {
        basis = "X";
      } else if (name === "RY" || name === "MY" || name === "MRY") {
        basis = "Y";
      } else if (name === "MXX" || name === "MYY" || name === "MZZ") {
        basis = name[1];
        let score = 0;
        for (let q2 of op.id_targets) {
          if (processedQubits.has(q2)) {
            score = -1;
            break;
          }
          score += before.bases.get(q2) === basis;
        }
        if (score === 2) {
          for (let q2 of op.id_targets) {
            processedQubits.add(q2);
            layer.markers.push(
              new Operation(
                GATE_MAP.get(`MARK${basis}`),
                "",
                new Float32Array([marker_index]),
                new Uint32Array([q2])
              )
            );
          }
        }
        continue;
      } else if (name.startsWith("MPP:")) {
        let score = 0;
        for (let k2 = 0; k2 < op.id_targets.length; k2++) {
          let q2 = op.id_targets[k2];
          basis = name[k2 + 4];
          if (processedQubits.has(q2)) {
            score = -1;
            break;
          }
          score += before.bases.get(q2) === basis;
        }
        if (score > op.id_targets.length / 2) {
          for (let k2 = 0; k2 < op.id_targets.length; k2++) {
            let q2 = op.id_targets[k2];
            basis = name[k2 + 4];
            processedQubits.add(q2);
            layer.markers.push(
              new Operation(
                GATE_MAP.get(`MARK${basis}`),
                "",
                new Float32Array([marker_index]),
                new Uint32Array([q2])
              )
            );
          }
        }
        continue;
      } else {
        continue;
      }
      if (b1 !== void 0 || b2 !== void 0) {
        layer.markers.push(
          new Operation(
            GATE_MAP.get(`MARK${basis}`),
            "",
            new Float32Array([marker_index]),
            new Uint32Array([q])
          )
        );
        processedQubits.add(q);
      }
    }
    this.commit_or_preview(newCircuit, preview);
  }
  moveDetOrObsAtFocusIntoMarker(preview, marker_index) {
    let circuit = this.copyOfCurCircuit();
    let focusSetQids = /* @__PURE__ */ new Set();
    let c2q = circuit.coordToQubitMap();
    for (let s of this.focusedSet.keys()) {
      focusSetQids.add(c2q.get(s));
    }
    let find_overlapping_region = () => {
      let { dets, obs } = circuit.collectDetectorsAndObservables(false);
      for (let det_id = 0; det_id < dets.length; det_id++) {
        let prop2 = PropagatedPauliFrames.fromMeasurements(
          circuit,
          dets[det_id].mids
        );
        if (prop2.atLayer(this.curLayer + 0.5).touchesQidSet(focusSetQids)) {
          return [
            prop2,
            new Operation(
              GATE_MAP.get("DETECTOR"),
              "",
              new Float32Array([det_id]),
              new Uint32Array([])
            )
          ];
        }
      }
      for (let [obs_id, obs_val] of obs.entries()) {
        let prop2 = PropagatedPauliFrames.fromMeasurements(circuit, obs_val);
        if (prop2.atLayer(this.curLayer + 0.5).touchesQidSet(focusSetQids)) {
          return [
            prop2,
            new Operation(
              GATE_MAP.get("OBSERVABLE_INCLUDE"),
              "",
              new Float32Array([obs_id]),
              new Uint32Array([])
            )
          ];
        }
      }
      return void 0;
    };
    let overlap = find_overlapping_region();
    if (overlap === void 0) {
      return;
    }
    let [prop, rep_op] = overlap;
    let newCircuit = this.copyOfCurCircuit();
    for (let k = 0; k < newCircuit.layers.length; k++) {
      let before = k === 0 ? new PropagatedPauliFrameLayer(/* @__PURE__ */ new Map(), /* @__PURE__ */ new Set(), []) : prop.atLayer(k - 0.5);
      let after = prop.atLayer(k + 0.5);
      let layer = newCircuit.layers[k];
      for (let q of /* @__PURE__ */ new Set([...before.bases.keys(), ...after.bases.keys()])) {
        let b1 = before.bases.get(q);
        let b2 = after.bases.get(q);
        let op = layer.id_ops.get(q);
        let name = op !== void 0 ? op.gate.name : void 0;
        let transition = void 0;
        if (name === "MR" || name === "MRX" || name === "MRY" || name === "R" || name === "RX" || name === "RY") {
          transition = b2;
        } else if (op !== void 0 && op.countMeasurements() > 0) {
          if (b1 === void 0) {
            transition = b2;
          } else if (b2 === void 0) {
            transition = b1;
          } else if (b1 !== b2) {
            let s = /* @__PURE__ */ new Set(["X", "Y", "Z"]);
            s.delete(b1);
            s.delete(b2);
            transition = [...s][0];
          }
        }
        if (transition !== void 0) {
          layer.markers.push(
            new Operation(
              GATE_MAP.get(`MARK${transition}`),
              "",
              new Float32Array([marker_index]),
              new Uint32Array([q])
            )
          );
        }
      }
      layer.markers = layer.markers.filter(
        (op) => op.gate.name !== rep_op.gate.name || op.args[0] !== rep_op.args[0]
      );
    }
    this.commit_or_preview(newCircuit, preview);
  }
};

// crumble/main.js
var CANVAS_W = 600;
var CANVAS_H = 300;
function initCanvas(el) {
  let scrollWrap = document.createElement("div");
  scrollWrap.setAttribute("style", "overflow-x: auto; overflow-y: hidden;");
  let canvas = document.createElement("canvas");
  canvas.id = "cvn";
  canvas.setAttribute("style", `margin: 0; padding: 0;`);
  canvas.tabIndex = 0;
  canvas.width = CANVAS_W;
  canvas.height = CANVAS_H;
  scrollWrap.appendChild(canvas);
  el.appendChild(scrollWrap);
  return canvas;
}
function render({ model, el }) {
  const traitlets = {
    getStim: () => model.get("stim"),
    getIndentCircuitLines: () => model.get("indentCircuitLines"),
    getCurveConnectors: () => model.get("curveConnectors")
  };
  const canvas = initCanvas(el);
  let editorState = (
    /** @type {!EditorState} */
    new EditorState(canvas)
  );
  const exportCurrentState = () => editorState.copyOfCurCircuit().toStimCircuit().replaceAll("\nPOLYGON", "\n#!pragma POLYGON").replaceAll("\nERR", "\n#!pragma ERR").replaceAll("\nMARK", "\n#!pragma MARK");
  function commitStimCircuit(stim_str) {
    let circuit = Circuit.fromStimCircuit(stim_str);
    editorState.commit(circuit);
  }
  model.on("change:stim", () => commitStimCircuit(traitlets.getStim()));
  model.on("change:indentCircuitLines", () => {
    setIndentCircuitLines(traitlets.getIndentCircuitLines());
    editorState.force_redraw();
  });
  model.on("change:curveConnectors", () => {
    setCurveConnectors(traitlets.getCurveConnectors());
    editorState.force_redraw();
  });
  editorState.rev.changes().subscribe(() => {
    editorState.obs_val_draw_state.set(editorState.toSnapshot(void 0));
  });
  editorState.obs_val_draw_state.observable().subscribe(
    (ds) => requestAnimationFrame(() => {
      draw(editorState.canvas.getContext("2d"), ds);
    })
  );
  setIndentCircuitLines(traitlets.getIndentCircuitLines());
  setCurveConnectors(traitlets.getCurveConnectors());
  commitStimCircuit(traitlets.getStim());
}
var main_default = { render };
export {
  main_default as default
};
