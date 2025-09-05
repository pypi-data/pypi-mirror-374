// static/js/wrappers/canvas-datagrid-wrapper.js

// Do NOT use import
// import CanvasDatagrid from './canvas-datagrid.js';

if (!customElements.get("canvas-datagrid")) {
  customElements.define("canvas-datagrid", window.canvasDatagrid);  // or just canvasDatagrid if global
}
