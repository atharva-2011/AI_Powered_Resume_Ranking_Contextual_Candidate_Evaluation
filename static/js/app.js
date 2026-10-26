document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const resumeDropzone = document.getElementById('resumeDropzone');
  const resumeInput = document.getElementById('resumeInput');
  const resumeFileList = document.getElementById('resumeFileList');

  const jdDropzone = document.getElementById('jdDropzone');
  const jdFileInput = document.getElementById('jdFileInput');
  const jdFileList = document.getElementById('jdFileList');
  const jdText = document.getElementById('jdText');

  const analyzeBtn = document.getElementById('analyzeBtn');
  const loadingBox = document.getElementById('loadingBox');
  const loadingStatusText = document.getElementById('loadingStatusText');
  const resultsSection = document.getElementById('resultsSection');
  const candidatesContainer = document.getElementById('candidatesContainer');

  const metricEvaluated = document.getElementById('metricEvaluated');
  const metricStrong = document.getElementById('metricStrong');
  const metricConsider = document.getElementById('metricConsider');
  const metricReject = document.getElementById('metricReject');
  const metricAvgScore = document.getElementById('metricAvgScore');

  let resumeFiles = [];
  let jdFile = null;

  // File Upload Handlers - Resumes
  resumeDropzone.addEventListener('click', (e) => {
    if (e.target !== resumeInput) resumeInput.click();
  });

  resumeInput.addEventListener('change', (e) => {
    addResumeFiles(Array.from(e.target.files));
    resumeInput.value = '';
  });

  ['dragenter', 'dragover'].forEach(name => {
    resumeDropzone.addEventListener(name, (e) => {
      e.preventDefault();
      resumeDropzone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(name => {
    resumeDropzone.addEventListener(name, (e) => {
      e.preventDefault();
      resumeDropzone.classList.remove('dragover');
    });
  });

  resumeDropzone.addEventListener('drop', (e) => {
    if (e.dataTransfer.files.length) {
      addResumeFiles(Array.from(e.dataTransfer.files));
    }
  });

  function addResumeFiles(files) {
    const validExts = ['.pdf', '.docx', '.txt'];
    files.forEach(file => {
      const ext = '.' + file.name.split('.').pop().toLowerCase();
      if (validExts.includes(ext)) {
        if (!resumeFiles.some(f => f.name === file.name && f.size === file.size)) {
          resumeFiles.push(file);
        }
      }
    });
    renderResumeList();
  }

  function renderResumeList() {
    resumeFileList.innerHTML = '';
    resumeFiles.forEach((file, idx) => {
      const item = document.createElement('div');
      item.className = 'file-item';
      item.innerHTML = `
        <div class="file-item-info">
          <span>📄</span>
          <span>${file.name}</span>
          <span style="color:var(--text-muted); font-size:0.75rem;">(${(file.size / 1024).toFixed(1)} KB)</span>
        </div>
        <button type="button" class="remove-btn" data-index="${idx}">&times;</button>
      `;
      resumeFileList.appendChild(item);
    });

    resumeFileList.querySelectorAll('.remove-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const index = parseInt(e.target.getAttribute('data-index'));
        resumeFiles.splice(index, 1);
        renderResumeList();
      });
    });
  }

  // Job Description Dropzone
  jdDropzone.addEventListener('click', (e) => {
    if (e.target !== jdFileInput) jdFileInput.click();
  });

  jdFileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
      jdFile = e.target.files[0];
      renderJdFile();
    }
    jdFileInput.value = '';
  });

  ['dragenter', 'dragover'].forEach(name => {
    jdDropzone.addEventListener(name, (e) => {
      e.preventDefault();
      jdDropzone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(name => {
    jdDropzone.addEventListener(name, (e) => {
      e.preventDefault();
      jdDropzone.classList.remove('dragover');
    });
  });

  jdDropzone.addEventListener('drop', (e) => {
    if (e.dataTransfer.files.length) {
      jdFile = e.dataTransfer.files[0];
      renderJdFile();
    }
  });

  function renderJdFile() {
    jdFileList.innerHTML = '';
    if (jdFile) {
      const item = document.createElement('div');
      item.className = 'file-item';
      item.innerHTML = `
        <div class="file-item-info">
          <span>📋</span>
          <span>${jdFile.name}</span>
        </div>
        <button type="button" class="remove-btn" id="removeJdBtn">&times;</button>
      `;
      jdFileList.appendChild(item);

      document.getElementById('removeJdBtn').addEventListener('click', () => {
        jdFile = null;
        renderJdFile();
      });
    }
  }

  // Analysis Trigger
  analyzeBtn.addEventListener('click', async () => {
    if (resumeFiles.length === 0) {
      alert('Please upload at least one candidate resume.');
      return;
    }
    if (!jdFile && !jdText.value.trim()) {
      alert('Please provide a Job Description by uploading a file or typing/pasting text.');
      return;
    }

    const formData = new FormData();
    resumeFiles.forEach(file => {
      formData.append('resumes', file);
    });

    if (jdFile) {
      formData.append('jd_file', jdFile);
    }
    if (jdText.value.trim()) {
      formData.append('jd_text', jdText.value.trim());
    }

    // UI State: Loading
    analyzeBtn.disabled = true;
    loadingBox.style.display = 'block';
    resultsSection.style.display = 'none';
    loadingStatusText.textContent = `Processing ${resumeFiles.length} candidate resume(s) through hybrid neural pipeline...`;

    try {
      const response = await fetch('/api/analyze/', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok || data.error) {
        throw new Error(data.error || 'Server returned an error.');
      }

      displayResults(data);
    } catch (err) {
      alert(`Evaluation Error: ${err.message}`);
    } finally {
      analyzeBtn.disabled = false;
      loadingBox.style.display = 'none';
    }
  });

  // Display Evaluation Results
  function displayResults(data) {
    const { cohort, candidates } = data;

    // Metrics
    metricEvaluated.textContent = cohort.total_evaluated;
    metricStrong.textContent = cohort.strong;
    metricConsider.textContent = cohort.consider;
    metricReject.textContent = cohort.reject;
    metricAvgScore.textContent = `${cohort.average_score}%`;

    // Candidate Cards
    candidatesContainer.innerHTML = '';

    candidates.forEach(cand => {
      const score = Math.round(cand.scores.final_score);
      const tierColor = cand.tier === 'strong' ? '#10b981' : cand.tier === 'consider' ? '#f59e0b' : '#ef4444';
      const tierGlow = cand.tier === 'strong' ? 'rgba(16, 185, 129, 0.25)' : cand.tier === 'consider' ? 'rgba(245, 158, 11, 0.25)' : 'rgba(239, 68, 68, 0.25)';

      const card = document.createElement('div');
      card.className = 'candidate-card';

      // Skills chips
      const skillsHtml = cand.skills && cand.skills.length > 0
        ? cand.skills.slice(0, 16).map(s => `<span class="skill-chip">${escapeHtml(s)}</span>`).join('')
        : '<span style="color:var(--text-muted); font-size:0.82rem;">No explicit skills extracted</span>';

      // Flags
      const greenFlagsHtml = cand.explanation.green_flags && cand.explanation.green_flags.length > 0
        ? cand.explanation.green_flags.map(f => `<div class="flag-item item-green">✓ ${escapeHtml(f)}</div>`).join('')
        : '<div style="color:var(--text-muted); font-size:0.8rem;">No key green flags identified</div>';

      const redFlagsHtml = cand.explanation.red_flags && cand.explanation.red_flags.length > 0
        ? cand.explanation.red_flags.map(f => `<div class="flag-item item-red">⚠ ${escapeHtml(f)}</div>`).join('')
        : '<div style="color:var(--text-muted); font-size:0.8rem;">No critical red flags identified</div>';

      // Social Links
      let socialsHtml = '';
      if (cand.socials.linkedin) socialsHtml += `<a href="${cand.socials.linkedin}" target="_blank" style="color:var(--accent-cyan); text-decoration:none;">LinkedIn ↗</a>`;
      if (cand.socials.github) socialsHtml += ` · <a href="${cand.socials.github}" target="_blank" style="color:var(--accent-cyan); text-decoration:none;">GitHub ↗</a>`;
      if (cand.socials.portfolio) socialsHtml += ` · <a href="${cand.socials.portfolio}" target="_blank" style="color:var(--accent-cyan); text-decoration:none;">Portfolio ↗</a>`;

      card.innerHTML = `
        <div class="candidate-card-layout">
          <!-- Column 1: Score & Tier -->
          <div class="score-circle-wrapper">
            <div class="radial-progress" style="background: conic-gradient(${tierColor} ${score * 3.6}deg, rgba(71, 85, 105, 0.3) 0deg);">
              <div class="radial-inner">
                <span class="radial-score" style="color:${tierColor};">${score}</span>
                <span class="radial-total">/ 100</span>
              </div>
            </div>
            <div class="rank-badge">Rank #${cand.rank}</div>
            <div class="tier-pill tier-${cand.tier}">
              <span>${cand.tier_badge}</span>
              <span>${cand.tier_label}</span>
            </div>
          </div>

          <!-- Column 2: Profile & Skills -->
          <div>
            <div class="cand-name">${escapeHtml(cand.name)}</div>
            <div class="cand-meta">
              <span>📧 ${escapeHtml(cand.email || 'Not provided')}</span>
              <span>·</span>
              <span>📞 ${escapeHtml(cand.phone || 'Not provided')}</span>
            </div>
            <div class="cand-submeta">
              <div><strong>${escapeHtml(cand.degree || 'Degree not stated')}</strong> ${cand.institution ? `· ${escapeHtml(cand.institution)}` : ''}</div>
              <div>CGPA: ${cand.cgpa ? escapeHtml(String(cand.cgpa)) : 'N/A'} · Exp: ${cand.experience_years ? escapeHtml(String(cand.experience_years)) + ' yrs' : 'N/A'}${socialsHtml ? ` · ${socialsHtml}` : ''}</div>
            </div>

            <div style="font-size:0.7rem; text-transform:uppercase; letter-spacing:0.05em; color:var(--text-muted); font-weight:700; margin-top:0.4rem;">
              Skills & Proficiencies
            </div>
            <div class="chips-container">
              ${skillsHtml}
            </div>
          </div>

          <!-- Column 3: Flags Grid -->
          <div class="flags-grid">
            <div class="flag-box green-box">
              <div class="flag-box-header">
                <span>🟢</span> Green Flags
              </div>
              <div class="flag-list">
                ${greenFlagsHtml}
              </div>
            </div>

            <div class="flag-box red-box">
              <div class="flag-box-header">
                <span>🔴</span> Red Flags / Gaps
              </div>
              <div class="flag-list">
                ${redFlagsHtml}
              </div>
            </div>
          </div>
        </div>

        <!-- Recruiter Executive Verdict Banner -->
        <div class="recruiter-summary-banner" style="border-left-color:${tierColor}; background:${tierGlow};">
          <div class="summary-heading" style="color:${tierColor};">
            📋 Recruiter Summary Verdict — Rank #${cand.rank} (${cand.tier_label})
          </div>
          <div class="summary-text">
            ${escapeHtml(cand.explanation.overall_rationale || 'Candidate successfully analyzed with contextual similarity and rule verification.')}
          </div>
        </div>

        <!-- Pipeline Internal Breakdown -->
        <div class="pipeline-breakdown">
          <div class="breakdown-item">
            <span>Deterministic Rules:</span>
            <span class="breakdown-val">${cand.scores.rule_score}%</span>
          </div>
          <div class="breakdown-item">
            <span>Bi-Encoder Semantic:</span>
            <span class="breakdown-val">${cand.scores.semantic_score}%</span>
          </div>
          <div class="breakdown-item">
            <span>Cross-Encoder Attention:</span>
            <span class="breakdown-val">${cand.scores.cross_encoder_score}%</span>
          </div>
          <div class="breakdown-item">
            <span>Confidence Index:</span>
            <span class="breakdown-val">${cand.scores.confidence}%</span>
          </div>
        </div>
      `;

      candidatesContainer.appendChild(card);
    });

    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
  }

  function escapeHtml(text) {
    if (!text) return '';
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
});
