// Fixed architecture of this lab; highlights describe an observation boundary,
// not a replay of every internal action or a causal provenance graph.
const FLOW_EVENT_MAP = Object.freeze({
  RUN_STARTED: {nodes:["runner"],edges:[],text:"本次实验进入运行器；此时尚未表示模型或工具已经执行。"},
  RUN_END: {nodes:["runner"],edges:[],text:"运行器记录最终运行状态。RUN_END 本身不是 utility 评估通过的证据。"},
  EPISODE_STARTED: {nodes:["pipeline"],edges:[],text:"开始一次完整 query；随后才初始化系统提示和用户 query。"},
  EPISODE_ENDED: {nodes:["exit"],edges:[],text:"本次 pipeline 返回或抛错。suite 可能重试；此事件不等于任务成功。"},
  MODEL_REQUEST: {nodes:["request"],edges:["request_api"],text:"在 HTTP 出站边界记录实际请求体，不证明服务端已经收到。"},
  MODEL_RESPONSE: {nodes:["api"],edges:["api_parse"],text:"客户端收到 HTTP 响应；响应可能含错误，尚未完成原生消息解析。"},
  MODEL_PARSED: {nodes:["parse"],edges:[],text:"响应已转换为原生 assistant 消息；没有工具调用也不自动表示任务成功。"},
  MODEL_ERROR: {nodes:["request","api","parse"],edges:[],text:"异常属于模型调用 / 适配边界，可能来自传输、SDK 或解析；日志未进一步定位时显示整个范围。"},
  TOOL_CALL_PROPOSED: {nodes:["parse"],edges:[],text:"记录模型原始工具调用提议，尚未经过执行器处理，也不代表工具已经执行。"},
  TOOL_RUNTIME_STARTED: {nodes:["runtime"],edges:[],text:"进入顶层 FunctionsRuntime；随后才进行内部参数校验、默认值补全和依赖注入。"},
  TOOL_RUNTIME_RETURNED: {nodes:["runtime"],edges:[],text:"顶层 runtime 已返回原始结果或错误；此时尚不等于工具消息已经加入历史。"},
  ENVIRONMENT_CHANGE: {nodes:["environment"],edges:[],text:"观察到工具调用前后环境状态变化。这份环境快照不等于模型输入。"},
  TOOL_RESULT: {nodes:["result"],edges:["result_history"],text:"执行器完成批次后形成工具消息并加入历史；未知工具也可直接产生错误消息而不进入 runtime。"},
  TOOL_OUTPUT_EXPOSED: {nodes:["history","request"],edges:["history_request"],text:"某条工具消息实际包含在本轮出站请求中；不证明模型注意或使用了它。"}
});

function eventHasError(event) {
  const data = event?.data && typeof event.data === "object" ? event.data : {};
  return event?.event_type === "MODEL_ERROR" || !!data.error || !!data.message?.error ||
    !!data.raised_exception_type || !!data.error_type ||
    (typeof data.status_code === "number" && data.status_code >= 400) ||
    ["error","failed","completed_with_issues"].includes(data.status);
}

function flowLocation(event) {
  if (!event) return {nodes:[],edges:[],tone:"none",text:"选择时间线事件，在流程图中查看它的位置。"};
  const key = typeof event.event_type === "string" ? event.event_type : "";
  const match = Object.prototype.hasOwnProperty.call(FLOW_EVENT_MAP,key) ? FLOW_EVENT_MAP[key] : null;
  return {
    nodes:match ? [...match.nodes] : [],
    edges:match ? [...match.edges] : [],
    tone:eventHasError(event) ? "error" : match ? "active" : "unknown",
    text:match ? match.text : "此事件暂未映射到已知组件；原始事件仍保留在详情中。"
  };
}

function updateFlow(event) {
  const state = flowLocation(event);
  let focusNode = null;
  for (const node of document.querySelectorAll("[data-flow-node]")) {
    const active = state.nodes.includes(node.getAttribute("data-flow-node"));
    node.classList.toggle("is-active",active);
    node.classList.toggle("is-error",active && state.tone === "error");
    if (active) {
      node.setAttribute("aria-current","step");
      focusNode ??= node;
    }
    else node.removeAttribute("aria-current");
  }
  for (const edge of document.querySelectorAll("[data-flow-edge]")) {
    const active = state.edges.includes(edge.getAttribute("data-flow-edge"));
    edge.classList.toggle("is-active",active);
    edge.classList.toggle("is-error",active && state.tone === "error");
  }
  const status = document.getElementById("flow-selection");
  status.textContent = event ? "所选事件 #" + String(event.event_sequence ?? "—") + " · " + String(event.event_type ?? "未知类型") : "尚未选择事件";
  status.dataset.tone = state.tone;
  document.getElementById("flow-explanation").textContent = state.text;
  // Keep the highlighted component in the diagram's horizontal viewport without
  // scrolling the page away from the user's selected timeline row.
  const viewport = document.getElementById("flow-scroll");
  if (focusNode?.getBoundingClientRect && viewport?.getBoundingClientRect) {
    const target = focusNode.getBoundingClientRect(), bounds = viewport.getBoundingClientRect();
    if (target.right > bounds.right - 12) viewport.scrollLeft += target.right - bounds.right + 12;
    else if (target.left < bounds.left + 12) viewport.scrollLeft += target.left - bounds.left - 12;
  }
}

function initializeFlow(mode) {
  if (mode === false) {
    document.getElementById("flow-api-label").textContent = "脚本模型响应";
    document.getElementById("flow-api-sub").textContent = "MockTransport · 离线";
  } else if (mode !== true) {
    document.getElementById("flow-api-label").textContent = "模型接口（类型未知）";
  }
  updateFlow(null);
}
