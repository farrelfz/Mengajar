/* ==========================================================================
   KIR & MENGAJAR STUDIO DASHBOARD - JAVASCRIPT CONTROLLER
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // State
  let activeModel = '';
  let allModels = [];
  let currentEventSource = null;

  // DOM Elements
  const tabLinks = document.querySelectorAll('.nav-item');
  const tabViews = document.querySelectorAll('.tab-view');
  const formatOptions = document.querySelectorAll('.format-option');
  
  // Status Elements
  const dot9Router = document.getElementById('dot9Router');
  const label9Router = document.getElementById('label9Router');
  const labelActiveModel = document.getElementById('labelActiveModel');
  const btnRefreshStatus = document.getElementById('btnRefreshStatus');

  // Studio Elements
  const selectStudioModel = document.getElementById('selectStudioModel');
  const selectMatpel = document.getElementById('selectMatpel');
  const selectJenjang = document.getElementById('selectJenjang');
  const inputTitle = document.getElementById('inputTitle');
  const inputRawContent = document.getElementById('inputRawContent');
  const wordCountLabel = document.getElementById('wordCountLabel');
  const btnLoadSampleKir = document.getElementById('btnLoadSampleKir');
  const btnLoadSamplePhysics = document.getElementById('btnLoadSamplePhysics');
  const btnStartGenerate = document.getElementById('btnStartGenerate');
  const progressFillBar = document.getElementById('progressFillBar');
  const progressPercentLabel = document.getElementById('progressPercentLabel');
  const progressStepLabel = document.getElementById('progressStepLabel');
  const jobStatusBadge = document.getElementById('jobStatusBadge');
  const terminalLogs = document.getElementById('terminalLogs');
  const resultBox = document.getElementById('resultBox');
  const resultDetails = document.getElementById('resultDetails');
  const btnPreviewPdf = document.getElementById('btnPreviewPdf');
  const btnDownloadPdf = document.getElementById('btnDownloadPdf');

  // Modal Elements
  const pdfModal = document.getElementById('pdfModal');
  const pdfFrame = document.getElementById('pdfFrame');
  const pdfModalTitle = document.getElementById('pdfModalTitle');
  const btnCloseModal = document.getElementById('btnCloseModal');
  const btnModalDownload = document.getElementById('btnModalDownload');

  // Playground Elements
  const selectPlaygroundModel = document.getElementById('selectPlaygroundModel');
  const inputPlaygroundPrompt = document.getElementById('inputPlaygroundPrompt');
  const btnRunPlaygroundTest = document.getElementById('btnRunPlaygroundTest');
  const playgroundResponseBox = document.getElementById('playgroundResponseBox');
  const metricLatency = document.getElementById('metricLatency');
  const metricTokens = document.getElementById('metricTokens');

  // Model Hub & Benchmarks
  const modelsGrid = document.getElementById('modelsGrid');
  const searchModels = document.getElementById('searchModels');
  const filterCapability = document.getElementById('filterCapability');
  const benchmarkTableBody = document.getElementById('benchmarkTableBody');
  const btnRunBenchmark = document.getElementById('btnRunBenchmark');
  const benchmarkLoading = document.getElementById('benchmarkLoading');
  const docGrid = document.getElementById('docGrid');
  const doctorChecksList = document.getElementById('doctorChecksList');

  // ─────────────────────────────────────────────────────────────
  // 1. Navigation & Tab Switching
  // ─────────────────────────────────────────────────────────────
  tabLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetTab = link.getAttribute('data-tab');
      
      tabLinks.forEach(l => l.classList.remove('active'));
      tabViews.forEach(v => v.classList.remove('active'));

      link.classList.add('active');
      const targetView = document.getElementById(`view-${targetTab}`);
      if (targetView) targetView.classList.add('active');

      // Lazy loads
      if (targetTab === 'library') loadDocuments();
      if (targetTab === 'benchmarks') loadBenchmarks();
      if (targetTab === 'doctor') loadDoctor();
    });
  });

  // Format selection toggle
  formatOptions.forEach(opt => {
    opt.addEventListener('click', () => {
      formatOptions.forEach(o => o.classList.remove('active'));
      opt.classList.add('active');
    });
  });

  // Word count update
  inputRawContent.addEventListener('input', () => {
    const text = inputRawContent.value.trim();
    const words = text ? text.split(/\s+/).length : 0;
    wordCountLabel.textContent = `${words} kata`;
  });

  // ─────────────────────────────────────────────────────────────
  // 2. Gateway Status Check
  // ─────────────────────────────────────────────────────────────
  async function refreshStatus() {
    try {
      const res = await fetch('/api/status');
      const data = await res.json();
      
      const nr = data.nine_router;
      const isOnline = nr && (nr.api_reachable || nr.port_listening || nr.process_running || nr.is_running);
      if (isOnline) {
        dot9Router.className = 'pill-dot pulse-green';
        const lat = nr.latency_ms ? ` (${Math.round(nr.latency_ms)}ms)` : '';
        label9Router.textContent = `9Router :20128${lat}`;
      } else {
        dot9Router.className = 'pill-dot pulse-amber';
        label9Router.textContent = '9Router :20128 (Offline/Connecting)';
      }

      activeModel = data.active_model || 'ag/gemini-3.7-flash-high';
      labelActiveModel.textContent = activeModel;
      if (selectStudioModel && selectStudioModel.value !== activeModel) {
        selectStudioModel.value = activeModel;
      }
    } catch (err) {
      dot9Router.className = 'pill-dot pulse-amber';
      label9Router.textContent = 'Gateway 9Router Unreachable';
    }
  }

  btnRefreshStatus.addEventListener('click', () => {
    btnRefreshStatus.style.transform = 'rotate(180deg)';
    setTimeout(() => { btnRefreshStatus.style.transform = 'none'; }, 300);
    refreshStatus();
  });

  // ─────────────────────────────────────────────────────────────
  // 3. Model Hub & Dropdown Populator
  // ─────────────────────────────────────────────────────────────
  async function loadModels() {
    try {
      const res = await fetch('/api/models');
      const data = await res.json();
      allModels = data.models || [];
      activeModel = data.active_model || activeModel;

      populateDropdowns();
      renderModelsGrid();
    } catch (err) {
      console.error('Failed to load models:', err);
    }
  }

  function populateDropdowns() {
    const opts = allModels.map(m => {
      const id = m.id || m;
      const isSel = id === activeModel ? 'selected' : '';
      return `<option value="${id}" ${isSel}>${id}</option>`;
    }).join('');

    selectStudioModel.innerHTML = opts || `<option value="${activeModel}">${activeModel}</option>`;
    selectPlaygroundModel.innerHTML = opts || `<option value="${activeModel}">${activeModel}</option>`;
  }

  function renderModelsGrid() {
    const query = (searchModels.value || '').toLowerCase();
    const capFilter = filterCapability.value;

    const filtered = allModels.filter(m => {
      const id = (m.id || '').toLowerCase();
      const matchQuery = id.includes(query);
      if (!matchQuery) return false;

      const caps = m.capabilities || {};
      if (capFilter === 'reasoning') return !!caps.reasoning;
      if (capFilter === 'vision') return !!caps.vision;
      if (capFilter === 'tools') return !!caps.tools;
      return true;
    });

    modelsGrid.innerHTML = filtered.map(m => {
      const id = m.id;
      const isActive = id === activeModel;
      const caps = m.capabilities || {};
      const ctx = m.context_length ? `${Math.round(m.context_length / 1000)}k ctx` : '';

      return `
        <div class="model-card ${isActive ? 'active-model-card' : ''}">
          <div>
            <div class="model-header">
              <div class="model-name">${id}</div>
              ${isActive ? '<span style="font-size:0.7rem; font-weight:700; color:var(--accent-cyan);">AKTIF</span>' : ''}
            </div>
            <div class="model-provider" style="margin-top:4px;">${m.owned_by || 'provider'} · ${ctx}</div>
          </div>
          <div class="tags-row">
            ${caps.reasoning ? '<span class="tag tag-reasoning">Reasoning</span>' : ''}
            ${caps.vision ? '<span class="tag tag-vision">Vision</span>' : ''}
            ${caps.tools ? '<span class="tag tag-tools">Tools</span>' : ''}
          </div>
          <button class="btn-secondary btn-switch-model" data-model="${id}" style="width:100%; text-align:center;">
            ${isActive ? '✓ Model Aktif' : 'Gunakan Model Ini'}
          </button>
        </div>
      `;
    }).join('');

    document.querySelectorAll('.btn-switch-model').forEach(btn => {
      btn.addEventListener('click', async () => {
        const modelId = btn.getAttribute('data-model');
        await switchActiveModel(modelId);
      });
    });
  }

  async function switchActiveModel(modelId) {
    try {
      const res = await fetch('/api/active-model', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: modelId }),
      });
      const data = await res.json();
      activeModel = data.active_model;
      labelActiveModel.textContent = activeModel;
      populateDropdowns();
      renderModelsGrid();
      appendTerminalLog(`Model aktif diubah menjadi: ${activeModel}`, 'info');
    } catch (err) {
      alert('Gagal mengganti model aktif: ' + err);
    }
  }

  searchModels.addEventListener('input', renderModelsGrid);
  filterCapability.addEventListener('change', renderModelsGrid);

  // ─────────────────────────────────────────────────────────────
  // 4. Studio Generator & SSE Pipeline Execution
  // ─────────────────────────────────────────────────────────────
  async function loadSampleByType(type) {
    try {
      const res = await fetch(`/api/sample-input?sample_type=${type}`);
      const data = await res.json();
      inputTitle.value = data.title;
      inputRawContent.value = data.content;
      if (data.matpel && selectMatpel) {
        selectMatpel.value = data.matpel;
      }
      inputRawContent.dispatchEvent(new Event('input'));
      const sampleLabel = type === 'kir' ? '🔬 Eksperimen (KIR) Enzim Katalase' : '🔥 Hand Fire Physics';
      appendTerminalLog(`Contoh materi "${sampleLabel}" berhasil dimuat. Format & mata pelajaran disesuaikan.`, 'success');
    } catch (err) {
      console.error(err);
      appendTerminalLog(`Gagal memuat contoh materi: ${err.message}`, 'error');
    }
  }

  if (btnLoadSampleKir) {
    btnLoadSampleKir.addEventListener('click', () => loadSampleByType('kir'));
  }
  if (btnLoadSamplePhysics) {
    btnLoadSamplePhysics.addEventListener('click', () => loadSampleByType('physics'));
  }

  // File Upload Ingestion (PDF / Markdown / TXT)
  const fileUploadInput = document.getElementById('fileUploadInput');
  if (fileUploadInput) {
    fileUploadInput.addEventListener('change', async (e) => {
      const file = e.target.files && e.target.files[0];
      if (!file) return;
      const formData = new FormData();
      formData.append('file', file);
      appendTerminalLog(`Mengunggah dan mengekstrak dokumen "${file.name}"...`, 'info');
      if (jobStatusBadge) jobStatusBadge.textContent = 'MENGUNGGAH';
      try {
        const res = await fetch('/api/upload', { method: 'POST', body: formData });
        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || `HTTP ${res.status}`);
        }
        const data = await res.json();
        if (data.status === 'ok') {
          if (data.title && inputTitle) inputTitle.value = data.title;
          if (inputRawContent) {
            inputRawContent.value = data.content || '';
            inputRawContent.dispatchEvent(new Event('input'));
          }
          if (jobStatusBadge) jobStatusBadge.textContent = 'TERUNGGAH';
          appendTerminalLog(`Dokumen "${data.filename}" berhasil di-ingest (${data.size_kb} KB, ${data.page_count} hal). Siap digenerate.`, 'success');
        }
      } catch (err) {
        console.error(err);
        appendTerminalLog(`Gagal memproses dokumen: ${err.message}`, 'error');
        if (jobStatusBadge) jobStatusBadge.textContent = 'GAGAL UPLOAD';
      } finally {
        fileUploadInput.value = '';
      }
    });
  }


  // Log Controls (Copy & Clear)
  const btnCopyLogs = document.getElementById('btnCopyLogs');
  const btnClearLogs = document.getElementById('btnClearLogs');

  if (btnCopyLogs) {
    btnCopyLogs.addEventListener('click', () => {
      const text = terminalLogs.innerText;
      if (!text.trim()) return;
      navigator.clipboard.writeText(text).then(() => {
        const originalText = btnCopyLogs.textContent;
        btnCopyLogs.textContent = '✓ Disalin!';
        setTimeout(() => { btnCopyLogs.textContent = originalText; }, 1800);
      }).catch(err => {
        alert('Gagal menyalin log: ' + err);
      });
    });
  }

  if (btnClearLogs) {
    btnClearLogs.addEventListener('click', () => {
      terminalLogs.innerHTML = '<div class="terminal-line info">[System] Log dibersihkan.</div>';
    });
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function getTagClass(tag) {
    const t = (tag || '').toLowerCase();
    if (t.includes('router')) return 'tag-router';
    if (t.includes('normal') || t.includes('segment') || t.includes('intel')) return 'tag-normalizer';
    if (t.includes('visual') || t.includes('intent') || t.includes('blueprint')) return 'tag-visual';
    if (t.includes('layout') || t.includes('html') || t.includes('asset')) return 'tag-layout';
    if (t.includes('render') || t.includes('playwright') || t.includes('pdf') || t.includes('pymupdf')) return 'tag-playwright';
    return 'tag-intel';
  }

  function appendTerminalLog(rawMsg, defaultType = 'normal') {
    const line = document.createElement('div');
    const msg = String(rawMsg);

    // Check for Task Start
    const taskStartMatch = msg.match(/(?:\[\d{2}:\d{2}:\d{2}\]\s*)?▶\s*\[(?:TASK\s*)?(\d+)\/(\d+)\]\s*(.*)/i);
    if (taskStartMatch) {
      line.className = 'terminal-line task-start';
      line.innerHTML = `<span class="log-badge-task">TASK ${taskStartMatch[1]}/${taskStartMatch[2]}</span> <span class="log-task-name">${escapeHtml(taskStartMatch[3])}</span>`;
      terminalLogs.appendChild(line);
      terminalLogs.scrollTop = terminalLogs.scrollHeight;
      return;
    }

    // Check for Task Desc
    const taskDescMatch = msg.match(/(?:\[\d{2}:\d{2}:\d{2}\]\s*)?└─\s*(.*)/);
    if (taskDescMatch) {
      line.className = 'terminal-line task-desc';
      line.innerHTML = `<span class="log-arrow">└─</span> ${escapeHtml(taskDescMatch[1])}`;
      terminalLogs.appendChild(line);
      terminalLogs.scrollTop = terminalLogs.scrollHeight;
      return;
    }

    // Check for Substep
    const substepMatch = msg.match(/(?:\[\d{2}:\d{2}:\d{2}\]\s*)?↳\s*\[(.*?)\]\s*(.*)/);
    if (substepMatch) {
      const tag = substepMatch[1];
      const detail = substepMatch[2];
      const tagClass = getTagClass(tag);
      line.className = 'terminal-line substep';
      line.innerHTML = `<span class="log-arrow">↳</span> <span class="log-tag ${tagClass}">[${escapeHtml(tag)}]</span> ${escapeHtml(detail)}`;
      terminalLogs.appendChild(line);
      terminalLogs.scrollTop = terminalLogs.scrollHeight;
      return;
    }

    // Check for Task Done
    const taskDoneMatch = msg.match(/(?:\[\d{2}:\d{2}:\d{2}\]\s*)?✓\s*\[SELESAI\s*(\d+)\/(\d+)\]\s*(.*)/i);
    if (taskDoneMatch) {
      line.className = 'terminal-line task-done';
      line.innerHTML = `<span class="log-check">✓</span> <strong>[SELESAI ${taskDoneMatch[1]}/${taskDoneMatch[2]}]</strong> ${escapeHtml(taskDoneMatch[3])}`;
      terminalLogs.appendChild(line);
      terminalLogs.scrollTop = terminalLogs.scrollHeight;
      return;
    }

    // Check for Next Task
    const nextMatch = msg.match(/(?:\[\d{2}:\d{2}:\d{2}\]\s*)?⏩\s*(.*)/);
    if (nextMatch) {
      line.className = 'terminal-line task-next';
      line.innerHTML = `<span class="log-arrow">⏩</span> ${escapeHtml(nextMatch[1])}`;
      terminalLogs.appendChild(line);
      terminalLogs.scrollTop = terminalLogs.scrollHeight;
      return;
    }

    // Check for Completion Summary
    if (msg.includes('🎉') || msg.includes('Dokumen PDF siap:')) {
      line.className = 'terminal-line completed-summary';
      line.innerHTML = escapeHtml(msg);
      terminalLogs.appendChild(line);
      terminalLogs.scrollTop = terminalLogs.scrollHeight;
      return;
    }

    // Default formatting
    line.className = `terminal-line ${defaultType}`;
    line.textContent = msg;
    terminalLogs.appendChild(line);
    terminalLogs.scrollTop = terminalLogs.scrollHeight;
  }

  function setStageActive(taskIdx) {
    const nodes = [
      document.getElementById('stageNode1'),
      document.getElementById('stageNode2'),
      document.getElementById('stageNode3'),
      document.getElementById('stageNode4'),
      document.getElementById('stageNode5'),
      document.getElementById('stageNode6'),
      document.getElementById('stageNode7'),
      document.getElementById('stageNode8'),
      document.getElementById('stageNode9'),
      document.getElementById('stageNode10'),
    ].filter(Boolean);

    nodes.forEach((node, i) => {
      const idx = i + 1;
      if (idx < taskIdx) {
        node.className = 'stage-node completed';
      } else if (idx === taskIdx) {
        node.className = 'stage-node active';
      } else {
        node.className = 'stage-node';
      }
    });
  }

  function updateStages(percent) {
    const nodes = [
      document.getElementById('stageNode1'),
      document.getElementById('stageNode2'),
      document.getElementById('stageNode3'),
      document.getElementById('stageNode4'),
      document.getElementById('stageNode5'),
      document.getElementById('stageNode6'),
      document.getElementById('stageNode7'),
      document.getElementById('stageNode8'),
      document.getElementById('stageNode9'),
      document.getElementById('stageNode10'),
    ].filter(Boolean);

    nodes.forEach(s => s.className = 'stage-node');

    if (percent >= 100) {
      nodes.forEach(s => s.className = 'stage-node completed');
      return;
    }

    const stageThresholds = [10, 20, 30, 40, 50, 60, 70, 80, 90, 95];
    let currentActive = 0;
    for (let i = 0; i < stageThresholds.length; i++) {
      if (percent >= stageThresholds[i]) {
        currentActive = i + 1;
      }
    }

    nodes.forEach((node, i) => {
      if (i < currentActive) {
        node.className = 'stage-node completed';
      } else if (i === currentActive) {
        node.className = 'stage-node active';
      } else {
        node.className = 'stage-node';
      }
    });
  }

  btnStartGenerate.addEventListener('click', async () => {
    const content = inputRawContent.value.trim();
    if (!content) {
      alert('Silakan masukkan materi mentah terlebih dahulu atau klik "Muat Contoh"!');
      return;
    }

    const activeFormat = document.querySelector('.format-option.active');
    const formatKey = activeFormat ? activeFormat.getAttribute('data-format') : 'teaching_presentation';

    const payload = {
      title: inputTitle.value.trim() || 'Dokumen Baru',
      raw_content: content,
      format: formatKey,
      matpel: selectMatpel.value,
      jenjang: selectJenjang.value,
      model: selectStudioModel.value || activeModel,
      enable_quality: true,
    };

    // UI Reset
    btnStartGenerate.disabled = true;
    resultBox.classList.remove('show');
    terminalLogs.innerHTML = '';
    progressFillBar.style.width = '0%';
    progressPercentLabel.textContent = '0%';
    progressStepLabel.textContent = 'Mengirim request ke pipeline...';
    jobStatusBadge.textContent = 'Running';
    jobStatusBadge.style.color = 'var(--accent-cyan)';
    appendTerminalLog(`[Studio] Memulai proses generate: ${payload.title}`, 'info');

    try {
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Gagal memulai job');

      const jobId = data.job_id;
      appendTerminalLog(`[Job ID: ${jobId}] Terdaftar di antrean execution server.`, 'info');

      // Start SSE Stream
      listenToJobStream(jobId);
    } catch (err) {
      alert('Error: ' + err.message);
      btnStartGenerate.disabled = false;
      jobStatusBadge.textContent = 'Failed';
      jobStatusBadge.style.color = 'var(--accent-rose)';
    }
  });

  function listenToJobStream(jobId) {
    if (currentEventSource) {
      currentEventSource.close();
    }

    currentEventSource = new EventSource(`/api/jobs/${jobId}/stream`);

    currentEventSource.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        const ev = payload.event;
        const data = payload.data || {};

        if (ev === 'init') {
          const pct = data.percent || 0;
          progressFillBar.style.width = `${pct}%`;
          progressPercentLabel.textContent = `${pct}%`;
          if (data.step) progressStepLabel.textContent = data.step;
          updateStages(pct);

          if (data.logs && Array.isArray(data.logs)) {
            terminalLogs.innerHTML = '';
            data.logs.forEach(l => appendTerminalLog(l));
          }
        } else if (ev === 'task_start') {
          const pct = data.percent || 15;
          progressFillBar.style.width = `${pct}%`;
          progressPercentLabel.textContent = `${pct}%`;
          progressStepLabel.textContent = `[TASK ${data.task_idx}/${data.total_tasks}] ${data.name}...`;
          setStageActive(data.task_idx);

          if (data.line_start) appendTerminalLog(data.line_start);
          if (data.line_desc) appendTerminalLog(data.line_desc);
        } else if (ev === 'substep') {
          if (data.line) appendTerminalLog(data.line);
        } else if (ev === 'task_done') {
          if (data.line_done) appendTerminalLog(data.line_done);
          if (data.line_next) appendTerminalLog(data.line_next);
        } else if (ev === 'progress') {
          const pct = data.percent || 0;
          progressFillBar.style.width = `${pct}%`;
          progressPercentLabel.textContent = `${pct}%`;
          if (data.step) progressStepLabel.textContent = data.step;
          updateStages(pct);
        } else if (ev === 'completed') {
          progressFillBar.style.width = '100%';
          progressPercentLabel.textContent = '100%';
          progressStepLabel.textContent = 'Selesai! PDF berhasil dibuat.';
          updateStages(100);
          btnStartGenerate.disabled = false;
          jobStatusBadge.textContent = 'Completed';
          jobStatusBadge.style.color = 'var(--accent-green)';

          // Show result box
          resultDetails.textContent = `${data.filename} · ${data.size_kb} KB · ${data.page_count} Halaman`;
          btnDownloadPdf.href = data.pdf_url;
          btnPreviewPdf.onclick = () => openPdfModal(data.filename, data.pdf_url);
          resultBox.classList.add('show');
          if (data.message) {
            appendTerminalLog(data.message, 'success');
          } else {
            appendTerminalLog(`🎉 [Sukses] Dokumen PDF siap: ${data.filename} (${data.size_kb} KB, ${data.page_count} Halaman)`, 'success');
          }

          currentEventSource.close();
        } else if (ev === 'blocked') {
          btnStartGenerate.disabled = false;
          jobStatusBadge.textContent = 'Blocked (Quality)';
          jobStatusBadge.style.color = 'var(--accent-amber)';
          appendTerminalLog(`⛔ [PIPELINE BLOCKED — QUALITY GATES NOT CONVERGED] ${data.reason || data.error}`, 'error');
          currentEventSource.close();
        } else if (ev === 'failed') {
          btnStartGenerate.disabled = false;
          jobStatusBadge.textContent = 'Failed';
          jobStatusBadge.style.color = 'var(--accent-rose)';
          appendTerminalLog(`❌ [Gagal] ${data.error}`, 'error');
          currentEventSource.close();
        }
      } catch (e) {
        console.error('SSE parse error:', e);
      }
    };

    currentEventSource.onerror = () => {
      console.warn('SSE connection lost or closed.');
      btnStartGenerate.disabled = false;
      currentEventSource.close();
    };
  }

  // ─────────────────────────────────────────────────────────────
  // 5. PDF Modal Viewer
  // ─────────────────────────────────────────────────────────────
  function openPdfModal(title, url) {
    pdfModalTitle.textContent = title;
    pdfFrame.src = url;
    btnModalDownload.href = url;
    pdfModal.classList.add('open');
  }

  btnCloseModal.addEventListener('click', () => {
    pdfModal.classList.remove('open');
    pdfFrame.src = 'about:blank';
  });

  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && pdfModal.classList.contains('open')) {
      btnCloseModal.click();
    }
  });

  // ─────────────────────────────────────────────────────────────
  // 6. Playground Test Runner
  // ─────────────────────────────────────────────────────────────
  btnRunPlaygroundTest.addEventListener('click', async () => {
    const model = selectPlaygroundModel.value;
    const prompt = inputPlaygroundPrompt.value.trim();
    if (!prompt) return;

    btnRunPlaygroundTest.disabled = true;
    playgroundResponseBox.textContent = 'Mengirim request ke 9Router… Mohon tunggu.';
    metricLatency.textContent = 'Menghitung…';
    metricTokens.textContent = 'Menghitung…';

    try {
      const res = await fetch('/api/test-model', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model, prompt }),
      });
      const data = await res.json();
      if (data.success) {
        playgroundResponseBox.textContent = data.response;
        metricLatency.textContent = `${Math.round(data.latency_ms)} ms (${(data.latency_ms / 1000).toFixed(2)}s)`;
        metricTokens.textContent = `${data.tokens} tokens`;
      } else {
        playgroundResponseBox.textContent = `[Error] ${data.response}`;
      }
    } catch (err) {
      playgroundResponseBox.textContent = `[Request Failed] ${err.message}`;
    } finally {
      btnRunPlaygroundTest.disabled = false;
    }
  });

  // ─────────────────────────────────────────────────────────────
  // 7. Benchmarks Loader
  // ─────────────────────────────────────────────────────────────
  async function loadBenchmarks(runNow = false) {
    benchmarkLoading.style.display = 'block';
    benchmarkTableBody.innerHTML = '';

    try {
      const res = await fetch(`/api/benchmarks?run_now=${runNow}`);
      const data = await res.json();
      const results = data.results || [];

      results.sort((a, b) => a.latency_ms - b.latency_ms);

      benchmarkTableBody.innerHTML = results.map((item, idx) => {
        const rank = idx + 1;
        const latency = Math.round(item.latency_ms);
        let speedBadge = '<span style="color:var(--accent-green)">Sangat Cepat</span>';
        if (latency > 3000) speedBadge = '<span style="color:var(--accent-amber)">Sedang</span>';
        if (latency > 7000) speedBadge = '<span style="color:var(--text-muted)">Lambat</span>';

        return `
          <tr style="border-bottom: 1px solid var(--border-subtle);">
            <td style="padding: 12px 14px; font-weight:700;">#${rank}</td>
            <td style="padding: 12px 14px; font-family:var(--font-mono);">${item.model}</td>
            <td style="padding: 12px 14px; color:var(--accent-cyan); font-weight:600;">${latency} ms</td>
            <td style="padding: 12px 14px;">${speedBadge}</td>
            <td style="padding: 12px 14px; color:var(--accent-green);">✓ OK (${item.tokens} tok)</td>
          </tr>
        `;
      }).join('');
    } catch (err) {
      console.error(err);
    } finally {
      benchmarkLoading.style.display = 'none';
    }
  }

  btnRunBenchmark.addEventListener('click', () => loadBenchmarks(true));

  // ─────────────────────────────────────────────────────────────
  // 8. Document Library Loader
  // ─────────────────────────────────────────────────────────────
  async function loadDocuments() {
    try {
      const res = await fetch('/api/documents');
      const docs = await res.json();

      if (!docs.length) {
        docGrid.innerHTML = '<div style="color:var(--text-muted); grid-column:1/-1;">Belum ada dokumen PDF yang digenerate.</div>';
        return;
      }

      docGrid.innerHTML = docs.map(d => {
        const dateStr = new Date(d.modified * 1000).toLocaleString('id-ID');
        return `
          <div class="doc-card" onclick="openPdfModal('${d.name}', '${d.download_url}')">
            <div style="display:flex; gap:12px; align-items:center;">
              <div class="doc-icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
              </div>
              <div style="overflow:hidden;">
                <div style="font-weight:600; font-size:0.85rem; color:#fff; white-space:nowrap; text-overflow:ellipsis; overflow:hidden;">${d.name}</div>
                <div style="font-size:0.72rem; color:var(--text-muted);">${d.size_kb} KB · ${dateStr}</div>
              </div>
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:8px;">
              <span style="font-size:0.75rem; color:var(--accent-cyan);">Buka Preview ↗</span>
              <a href="${d.download_url}" target="_blank" onclick="event.stopPropagation();" style="font-size:0.75rem; color:var(--text-secondary); text-decoration:none;">⬇ Download</a>
            </div>
          </div>
        `;
      }).join('');
    } catch (err) {
      console.error(err);
    }
  }

  // ─────────────────────────────────────────────────────────────
  // 9. System Doctor Loader
  // ─────────────────────────────────────────────────────────────
  async function loadDoctor() {
    try {
      const res = await fetch('/api/status');
      const data = await res.json();
      const nr = data.nine_router || {};

      const procOk = !!(nr.process_running || nr.port_listening || nr.is_running);
      const checks = [
        { label: '9Router Gateway Process', ok: procOk, note: procOk ? 'Running di background' : 'Offline' },
        { label: '9Router Port 20128 (TCP)', ok: nr.port_listening, note: nr.port_listening ? 'LISTENING' : 'Port Tertutup' },
        { label: '9Router /v1/models API', ok: nr.api_reachable, note: `${nr.available_models_count || 0} model terdeteksi (${Math.round(nr.latency_ms || 0)}ms)` },
        { label: 'Web Dashboard Port 20129', ok: true, note: 'Aktif di localhost:20129' },
        { label: 'Model AI Default', ok: true, note: data.active_model },
        { label: 'Playwright & Chromium Driver', ok: data.environment.playwright, note: 'Driver reachable untuk render PDF' },
        { label: 'Jinja2 Templating Engine', ok: data.environment.jinja2, note: 'Engine aktif untuk HTML master' },
      ];

      doctorChecksList.innerHTML = checks.map(c => `
        <div style="display:flex; justify-content:space-between; align-items:center; padding:12px 16px; background:rgba(15,23,42,0.4); border-radius:8px; border:1px solid var(--border-subtle);">
          <div style="display:flex; align-items:center; gap:10px;">
            <span>${c.ok ? '✅' : '⚠️'}</span>
            <span style="font-weight:600; font-size:0.85rem;">${c.label}</span>
          </div>
          <span style="font-size:0.8rem; color:${c.ok ? 'var(--accent-green)' : 'var(--accent-amber)'};">${c.note}</span>
        </div>
      `).join('');
    } catch (err) {
      console.error(err);
    }
  }

  // Initial Boot & periodic status sync
  refreshStatus();
  loadModels();
  setInterval(refreshStatus, 8000);
});
