/**
 * AI-Powered Audio Call Scam Analyzer
 * Frontend Application
 * =================================
 */

// Configuration
let API_BASE_URL = '';

// Auto-detect backend port if running on common dev ports
if (window.location.port === '8001' || window.location.port === '3000' || window.location.port === '5501') {
    API_BASE_URL = 'http://localhost:8000';
} else if (!window.location.hostname || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    // Default to port 8000 for local development if not specified
    if (!window.location.port || window.location.port === '80' || window.location.port === '443') {
        // Might be served by a proxy or same-port, stay relative
    } else {
        // Keep current URL if on 8000, else assume backend is on 8000
        if (window.location.port !== '8000') {
            API_BASE_URL = 'http://localhost:8000';
        }
    }
}

const API_KEY = 'guvi-audio-scam-12345';  // API key for authentication

// State
let selectedFile = null;
let analysisResult = null;

// ============================================
// DOM Elements
// ============================================

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const filePreview = document.getElementById('filePreview');
const fileName = document.getElementById('fileName');
const analyzeBtn = document.getElementById('analyzeBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
const loadingText = document.getElementById('loadingText');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const languageSelect = document.getElementById('languageSelect');

// Initialize button as disabled
analyzeBtn.disabled = true;

// ============================================
// EVENT LISTENERS
// ============================================

// Upload area drag-and-drop
uploadArea.addEventListener('click', () => fileInput.click());
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'var(--primary)';
});
uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = 'var(--secondary)';
});
uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'var(--secondary)';
    handleFileSelect(e.dataTransfer.files[0]);
});

// File input change
fileInput.addEventListener('change', (e) => {
    if (e.target.files[0]) {
        handleFileSelect(e.target.files[0]);
    }
});

// Analyze button
analyzeBtn.addEventListener('click', analyzeCall);

// New analysis button
document.getElementById('newAnalysisBtn')?.addEventListener('click', () => {
    location.reload();
});

// Download report button
document.getElementById('downloadBtn')?.addEventListener('click', downloadReport);

// ============================================
// FILE HANDLING
// ============================================

function handleFileSelect(file) {
    // Accept all audio files
    if (!file.type.startsWith('audio/')) {
        showError('❌ Please upload an audio file.');
        fileInput.value = '';
        return;
    }

    selectedFile = file;
    fileName.textContent = file.name;
    document.getElementById('fileSize').textContent = `${(file.size / 1024).toFixed(2)} KB`;
    filePreview.style.display = 'block';
    analyzeBtn.disabled = false;
    errorSection.style.display = 'none';
    analyzeBtn.textContent = '🚀 Analyze Call';
}

// ============================================
// ANALYSIS
// ============================================

async function analyzeCall() {
    if (!selectedFile) {
        showError('❌ No audio file selected. Please upload a file first.');
        return;
    }

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = '⏳ Processing...';
    loadingIndicator.style.display = 'block';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    loadingText.textContent = '📥 Uploading audio file...';

    try {
        // Create FormData with correct field name 'audio'
        const formData = new FormData();
        formData.append('audio', selectedFile);

        const language = languageSelect.value;
        if (language) {
            formData.append('language', language);
        }

        // DEBUG: Log what's being sent
        console.log(`[INFO] File details:`);
        console.log(`  Name: ${selectedFile.name}`);
        console.log(`  Size: ${selectedFile.size} bytes`);
        console.log(`  Type: ${selectedFile.type}`);
        console.log(`[INFO] FormData contents:`);
        for (let [key, value] of formData.entries()) {
            console.log(`  ${key}: ${value instanceof File ? `File(${value.name}, ${value.size}b)` : value}`);
        }
        console.log(`[INFO] Uploading to: ${API_BASE_URL}/analyze-call`);

        // Call API with proper error handling
        let response;
        try {
            response = await fetch(`${API_BASE_URL}/analyze-call`, {
                method: 'POST',
                headers: {
                    'X-API-KEY': API_KEY,  // Add API key for authentication
                },
                body: formData,  // DO NOT set Content-Type - browser handles it
            });
        } catch (netErr) {
            console.error('[ERROR] Network/Fetch error:', netErr);
            throw new Error(`❌ Failed to reach backend at ${API_BASE_URL}. Make sure the backend server is running.`);
        }

        console.log(`[DEBUG] Response status: ${response.status}`);

        let responseData;
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            try {
                responseData = await response.json();
            } catch (e) {
                console.error('[ERROR] Failed to parse response JSON:', e);
                responseData = { detail: 'Server error - could not parse response JSON' };
            }
        } else {
            const textResponse = await response.text();
            console.error('[ERROR] Server returned non-JSON response:', textResponse);
            responseData = { detail: `Server error: Received non-JSON response (${response.status})` };
        }

        console.log('[DEBUG] Response data:', responseData);

        if (!response.ok) {
            // Parse backend error message
            let errorMsg = responseData.error || responseData.detail || responseData.message || `API error: ${response.status}`;

            // Ensure error message is a string
            if (typeof errorMsg === 'object') {
                errorMsg = JSON.stringify(errorMsg);
            }

            console.error(`[ERROR] Backend error (${response.status}):`, errorMsg);

            // Make error messages more user-friendly
            if (errorMsg.includes('Empty audio file')) {
                errorMsg = '❌ The audio file is empty. Please upload a valid audio file.';
            } else if (errorMsg.includes('unsupported') || errorMsg.includes('Unsupported')) {
                errorMsg = '❌ Audio format issue. Try uploading a different format.';
            } else if (errorMsg.includes('no clear speech') || errorMsg.includes('no clear')) {
                errorMsg = '❌ Could not hear clear speech in the audio. Please upload a call recording.';
            } else if (errorMsg.includes('File is empty')) {
                errorMsg = '❌ File is empty or corrupt. Please upload a valid audio file.';
            } else if (errorMsg.includes('Invalid or missing API key')) {
                errorMsg = '❌ Authentication error: Invalid API key.';
            } else {
                // Prepend error code if not already formatted
                if (!errorMsg.startsWith('❌')) {
                    errorMsg = `❌ Error: ${errorMsg}`;
                }
            }

            throw new Error(errorMsg);
        }

        loadingText.textContent = '🔍 Analyzing for scam patterns...';
        analysisResult = responseData;

        loadingText.textContent = '📊 Generating report...';
        await displayResults();

    } catch (error) {
        console.error('Analysis error:', error);
        const errorMsg = error.message || 'Analysis failed. Please try again.';
        showError(errorMsg);
    } finally {
        loadingIndicator.style.display = 'none';
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = '🚀 Analyze Call';
    }
}

// ============================================
// RESULTS DISPLAY
// ============================================

async function displayResults() {
    if (!analysisResult) return;

    // Hide error and show results
    errorSection.style.display = 'none';
    resultsSection.style.display = 'block';

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });

    // Display risk score
    displayRiskScore();

    // Display transcription
    displayTranscription();

    // Display patterns
    displayPatterns();

    // Display timeline
    displayTimeline();

    // Display explanation
    displayExplanation();

    // Display recommendation
    displayRecommendation();

    // Display metadata
    displayMetadata();
}

function displayRiskScore() {
    const riskScore = analysisResult.risk_score;
    const riskLevel = analysisResult.risk_level;
    const riskCard = document.getElementById('riskCard');
    const riskScoreEl = document.getElementById('riskScore');
    const riskLabel = document.getElementById('riskLabel');
    const riskBar = document.getElementById('riskBar');

    riskScoreEl.textContent = `${riskScore}/100`;
    riskLabel.textContent = riskLevel.replace(/_/g, ' ');

    // Color based on risk (Futuristic vibrant colors)
    if (riskScore >= 90) {
        riskCard.style.background = 'linear-gradient(135deg, #f43f5e 0%, #e11d48 100%)'; // Neon Rose
        riskCard.style.boxShadow = '0 0 30px rgba(244, 63, 94, 0.4)';
    } else if (riskScore >= 70) {
        riskCard.style.background = 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)'; // Amber
        riskCard.style.boxShadow = '0 0 30px rgba(245, 158, 11, 0.3)';
    } else if (riskScore >= 50) {
        riskCard.style.background = 'linear-gradient(135deg, #fbbf24 0%, #fde047 100%)'; // Golden
        riskCard.style.boxShadow = '0 0 30px rgba(251, 191, 36, 0.2)';
    } else {
        riskCard.style.background = 'linear-gradient(135deg, #10b981 0%, #34d399 100%)'; // Emerald
        riskCard.style.boxShadow = '0 0 30px rgba(16, 185, 129, 0.2)';
    }

    // Animate bar
    riskBar.style.width = `${riskScore}%`;
}

function displayTranscription() {
    const transcription = analysisResult.transcription;
    const transcriptionText = document.getElementById('transcriptionText');
    transcriptionText.textContent = transcription || '(No transcription available)';
}

function displayPatterns() {
    const patterns = analysisResult.detected_patterns;
    const patternsList = document.getElementById('patternsList');

    if (patterns.length === 0) {
        patternsList.innerHTML = '<p style="color: #2ed573; font-weight: bold;">✅ No scam patterns detected</p>';
        return;
    }

    patternsList.innerHTML = patterns.map(pattern => `
        <div class="pattern-item">
            <div class="pattern-name">🚨 ${pattern.pattern_name}</div>
            <div class="pattern-keywords">
                <strong>Keywords:</strong> ${pattern.keywords.join(', ')}
            </div>
            <div class="pattern-explanation">${pattern.explanation}</div>
        </div>
    `).join('');
}

function displayTimeline() {
    const timeline = analysisResult.risk_timeline;
    const timelineChart = document.getElementById('timelineChart');

    if (!timeline || timeline.length === 0) {
        timelineChart.innerHTML = '<p>No timeline available</p>';
        return;
    }

    timelineChart.innerHTML = timeline.map((item, index) => {
        const dotColor = item.risk_score >= 70 ? '#ff4757' :
            item.risk_score >= 50 ? '#ffa502' :
                item.risk_score >= 30 ? '#ffd93d' : '#2ed573';

        return `
            <div class="timeline-item">
                <div class="timeline-dot" style="background: ${dotColor};"></div>
                <div class="timeline-content">
                    <div class="timeline-time">⏱️ ${item.timestamp}s - Risk: ${item.risk_score}/100</div>
                    <div class="timeline-reason">${item.reason}</div>
                </div>
            </div>
        `;
    }).join('');
}

function displayExplanation() {
    const explanation = analysisResult.explanation;
    const explanationEl = document.getElementById('explanation');
    explanationEl.innerHTML = explanation.replace(/\n/g, '<br>');
}

function displayRecommendation() {
    const riskScore = analysisResult.risk_score;
    const recommendationTitle = document.getElementById('recommendationTitle');
    const recommendationText = document.getElementById('recommendationText');
    const recommendationCard = document.getElementById('recommendationCard');

    let title, text, color;

    if (riskScore >= 90) {
        title = '🔴 CRITICAL: HANG UP IMMEDIATELY';
        text = 'This is almost certainly a scam. Do NOT provide any personal or financial information. Report the number to your bank and local authorities.';
        color = '#ff4757';
    } else if (riskScore >= 70) {
        title = '🟠 HIGH RISK: END CALL';
        text = 'High probability of fraud detected. Legitimate institutions do not operate this way. Hang up and contact your bank directly using a verified number.';
        color = '#ffa502';
    } else if (riskScore >= 50) {
        title = '🟡 SUSPICIOUS: BE CAUTIOUS';
        text = 'Multiple suspicious patterns detected. Verify independently before taking any action. Do not share sensitive information.';
        color = '#ffd93d';
    } else if (riskScore >= 30) {
        title = '🟢 LOW RISK: REMAIN VIGILANT';
        text = 'Some unusual patterns detected, but nothing conclusive. Stay alert but this may be a legitimate call.';
        color = '#ffd93d';
    } else {
        title = '✅ LIKELY SAFE';
        text = 'No major scam indicators detected. This appears to be a legitimate call, but always practice caution with unsolicited calls.';
        color = '#2ed573';
    }

    recommendationTitle.textContent = title;
    recommendationText.textContent = text;
    recommendationCard.style.borderLeftColor = color;
}

function displayMetadata() {
    document.getElementById('duration').textContent = `${analysisResult.call_duration_seconds.toFixed(2)}s`;
    document.getElementById('language').textContent = analysisResult.language_detected || 'Unknown';
    document.getElementById('confidence').textContent = `${(analysisResult.confidence * 100).toFixed(1)}%`;

    // NEW: Display advanced analysis sections
    displayKnownScamMatch();
    displayVoiceAnalysis();
    displayEmotionalAnalysis();
    displayEntityAnalysis();
}

// NEW: Display known scam database match
function displayKnownScamMatch() {
    const card = document.getElementById('knownScamsCard');
    const content = document.getElementById('knownScamsContent');

    if (!analysisResult.known_scam_match || !analysisResult.known_scam_match.is_known_scam) {
        card.style.display = 'none';
        return;
    }

    const match = analysisResult.known_scam_match.top_match;
    card.style.display = 'block';

    content.innerHTML = `
        <div style="background: #ff6b6b20; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
            <p><strong style="color: #c92a2a;">⚠️ CRITICAL MATCH DETECTED</strong></p>
            <p><strong>Campaign:</strong> ${match.campaign_name}</p>
            <p><strong>Severity:</strong> ${match.severity}</p>
            <p><strong>Match Confidence:</strong> ${(analysisResult.known_scam_match.overall_match_confidence * 100).toFixed(1)}%</p>
            <p><strong>Description:</strong> ${match.description}</p>
            <p><strong>Average Loss per Victim:</strong> ${match.loss_average}</p>
            <p style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ddd;">
                <strong>This call pattern matches ${match.typical_targets[0]}.</strong>
            </p>
        </div>
        <div>
            <p><strong>Matched Patterns:</strong></p>
            <ul>
                ${match.matched_keywords.map(kw => `<li>${kw}</li>`).join('')}
            </ul>
        </div>
    `;
}

// NEW: Display voice analysis
function displayVoiceAnalysis() {
    const card = document.getElementById('voiceAnalysisCard');
    const content = document.getElementById('voiceAnalysisContent');

    if (!analysisResult.voice_analysis || analysisResult.voice_analysis.error) {
        card.style.display = 'none';
        return;
    }

    const va = analysisResult.voice_analysis;
    card.style.display = 'block';

    const riskIndicators = va.risk_indicators || [];

    // UI fix: ensure text is visible on these boxes in dark theme
    const boxStyle = 'background: rgba(255,255,255,0.05); padding: 15px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);';
    const labelStyle = 'margin: 0; color: var(--text-muted); font-size: 0.85em; text-transform: uppercase; letter-spacing: 1px;';
    const valueStyle = 'margin: 8px 0 0 0; font-size: 1.8em; font-weight: 900; color: var(--primary);';

    content.innerHTML = `
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 25px;">
            <div style="${boxStyle}">
                <p style="${labelStyle}">Speaking Rate</p>
                <p style="${valueStyle}">${(va.speaking_rate * 100).toFixed(0)}%</p>
                <p style="font-size: 0.75em; margin-top: 5px; opacity: 0.6;">Speech speed consistency</p>
            </div>
            <div style="${boxStyle}">
                <p style="${labelStyle}">Pitch Variation</p>
                <p style="${valueStyle}">${(va.pitch_variation * 100).toFixed(0)}%</p>
                <p style="font-size: 0.75em; margin-top: 5px; opacity: 0.6;">Emotional modulation</p>
            </div>
            <div style="${boxStyle}">
                <p style="${labelStyle}">Silence Ratio</p>
                <p style="${valueStyle}">${(va.silence_ratio * 100).toFixed(0)}%</p>
                <p style="font-size: 0.75em; margin-top: 5px; opacity: 0.6;">Hesitation gaps</p>
            </div>
            <div style="${boxStyle}">
                <p style="${labelStyle}">Noise Level</p>
                <p style="${valueStyle}">${(va.noise_level * 100).toFixed(0)}%</p>
                <p style="font-size: 0.75em; margin-top: 5px; opacity: 0.6;">Background clarity</p>
            </div>
        </div>
        <div style="background: rgba(14, 165, 233, 0.1); padding: 15px; border-radius: 8px; margin-top: 10px;">
            <p><strong>Voice Quality Score:</strong> ${va.voice_quality_score.toFixed(1)}/100</p>
            <p style="font-size: 0.9em; margin-top: 5px; color: var(--text-muted);">
                Analyzing physiological stress markers and audio artifacts often utilized in deepfake or synthetic speech detection.
            </p>
        </div>
        ${riskIndicators.length > 0 ? `
            <div style="margin-top: 20px;">
                <p style="color: var(--accent); font-weight: 800;">⚠️ VOICED RISK INDICATORS:</p>
                <ul style="margin-top: 8px;">${riskIndicators.map(ind => `<li style="margin-bottom: 5px; color: var(--text-main);">${ind}</li>`).join('')}</ul>
            </div>
        ` : '<p style="margin-top: 20px; color: var(--success); font-weight: 600;">✅ No physiological voice-based risk indicators detected</p>'}
    `;
}

// NEW: Display emotional analysis
function displayEmotionalAnalysis() {
    const card = document.getElementById('emotionalAnalysisCard');
    const content = document.getElementById('emotionalAnalysisContent');

    if (!analysisResult.emotional_analysis) {
        card.style.display = 'none';
        return;
    }

    const ea = analysisResult.emotional_analysis;
    card.style.display = 'block';

    let manipulationColor = '#10b981'; // Emerald/Success
    if (ea.manipulation_risk > 0.7 || ea.manipulation_risk > 70) manipulationColor = '#ef4444'; // Danger
    else if (ea.manipulation_risk > 0.5 || ea.manipulation_risk > 50) manipulationColor = '#f59e0b'; // Amber
    else if (ea.manipulation_risk > 0.3 || ea.manipulation_risk > 30) manipulationColor = '#fbbf24'; // Golden

    const manipulationRiskDisplay = ea.manipulation_risk <= 1
        ? (ea.manipulation_risk * 100).toFixed(1)
        : ea.manipulation_risk.toFixed(1);

    const toneType = ea.tone_assessment?.tone_type || "N/A";
    const tactics = ea.tone_assessment?.suspicious_tactics || ea.tactics_detected?.join(", ") || "None detected";

    content.innerHTML = `
        <div style="background: ${manipulationColor}15; padding: 20px; border-radius: 12px; border-left: 4px solid ${manipulationColor}; margin-bottom: 20px;">
            <p><strong>Manipulation Risk Score:</strong> ${manipulationRiskDisplay}/100</p>
            <p><strong>Tone Classification:</strong> ${toneType}</p>
            <p><strong>Manipulation Tactics:</strong> ${tactics}</p>
        </div>
        <p style="margin-bottom: 15px;"><strong>Detected Emotions:</strong></p>
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px;">
            ${ea.emotions ? Object.entries(ea.emotions).map(([emotion, data]) => `
                <div style="background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);">
                    <p style="margin: 0; font-weight: 800; color: var(--primary);">📊 ${emotion.charAt(0).toUpperCase() + emotion.slice(1)}</p>
                    <p style="margin: 5px 0 0 0; font-size: 0.9em; opacity: 0.8;">Intensity: ${(data.intensity * 100).toFixed(0)}%</p>
                    ${data.keywords?.length > 0 ? `<p style="margin: 5px 0 0 0; font-size: 0.8em; color: var(--text-muted);">Keywords: ${data.keywords.join(', ')}</p>` : ''}
                </div>
            `).join('') : '<p>No specific emotion data available</p>'}
        </div>
    `;
}

// NEW: Display entity analysis
function displayEntityAnalysis() {
    const card = document.getElementById('entityAnalysisCard');
    const content = document.getElementById('entityAnalysisContent');

    if (!analysisResult.entity_analysis) {
        card.style.display = 'none';
        return;
    }

    const ea = analysisResult.entity_analysis;
    card.style.display = 'block';

    let severityColor = '#10b981';
    if (ea.severity === 'CRITICAL') severityColor = '#ef4444';
    else if (ea.severity === 'HIGH') severityColor = '#f59e0b';
    else if (ea.severity === 'MEDIUM') severityColor = '#fbbf24';

    const phoneCount = ea.phone_numbers?.length || 0;
    const accountCount = ea.account_numbers?.length || 0;
    const infoRisk = (ea.information_extraction_risk || 0).toFixed(1);
    const entitiesList = ea.entities ? ea.entities.join(", ") : "None specific";

    content.innerHTML = `
        <div style="background: ${severityColor}15; padding: 20px; border-radius: 12px; border-left: 4px solid ${severityColor}; margin-bottom: 20px;">
            <p><strong>Extraction Severity:</strong> <span style="color: ${severityColor}; font-weight: 800;">${ea.severity || "LOW"}</span></p>
            <p><strong>Information Risk Score:</strong> ${infoRisk}/100</p>
            <p><strong>Targeted Entities:</strong> ${entitiesList}</p>
        </div>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 20px;">
            <div style="background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);">
                <p style="margin: 0; color: var(--text-muted); font-size: 0.9em;">Phone Numbers</p>
                <p style="margin: 8px 0 0 0; font-size: 1.8em; font-weight: 900; color: var(--primary);">${phoneCount}</p>
            </div>
            <div style="background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);">
                <p style="margin: 0; color: var(--text-muted); font-size: 0.9em;">Accounts/Cards</p>
                <p style="margin: 8px 0 0 0; font-size: 1.8em; font-weight: 900; color: var(--primary);">${accountCount}</p>
            </div>
        </div>
        ${ea.suspicious_commands?.length > 0 ? `
            <p style="margin-bottom: 10px;"><strong>⚠️ Detected Action Commands:</strong></p>
            <ul style="list-style-type: none; padding: 0;">
                ${ea.suspicious_commands.slice(0, 5).map(cmd => `
                    <li style="background: rgba(239, 68, 68, 0.1); padding: 8px 12px; border-radius: 6px; margin-bottom: 8px; font-size: 0.95em; border-left: 3px solid #ef4444;">
                        <strong>${cmd.type?.toUpperCase().replace("_", " ")}:</strong> ${cmd.value}
                    </li>
                `).join('')}
            </ul>
        ` : `<p style="color: var(--success); font-weight: 600;">✅ No high-risk commands detected</p>`}
    `;
}


// ============================================
// ERROR HANDLING
// ============================================

function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorSection.style.display = 'block';
    resultsSection.style.display = 'none';
    loadingIndicator.style.display = 'none';
    errorSection.scrollIntoView({ behavior: 'smooth' });
}

// ============================================
// REPORT GENERATION
// ============================================

function downloadReport() {
    if (!analysisResult) return;

    const report = generateReport();
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(report));
    element.setAttribute('download', `scam-analysis-${Date.now()}.txt`);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

function generateReport() {
    const result = analysisResult;
    const languageNames = {
        'en': 'English', 'hi': 'Hindi', 'ta': 'Tamil', 'te': 'Telugu',
        'ml': 'Malayalam', 'kn': 'Kannada', 'bn': 'Bengali', 'gu': 'Gujarati',
        'es': 'Spanish', 'fr': 'French'
    };
    const langFull = languageNames[result.language_detected] || result.language_detected;

    let report = `
═══════════════════════════════════════════════════════════
       🔐 AI-POWERED SCAM ANALYZER - SECURITY REPORT
═══════════════════════════════════════════════════════════

🔍 CASE SUMMARY
────────────────────────────────────────────────────────────
Report ID:      #${Math.random().toString(36).substring(2, 10).toUpperCase()}
Generated:      ${new Date().toLocaleString()}
Risk Score:     ${result.risk_score}/100
Risk Level:     ${result.risk_level.replace(/_/g, ' ')}
Primary Threat: ${result.primary_threat}
Confidence:     ${(result.confidence * 100).toFixed(1)}%

📞 CALL INFO
────────────────────────────────────────────────────────────
Duration:       ${result.call_duration_seconds.toFixed(2)}s
Language:       ${langFull} (ISO: ${result.language_detected})
Analysis Type:  Multilingual AI Voice Analysis

🗣️ TRANSCRIPTION PREVIEW
────────────────────────────────────────────────────────────
${result.transcription}

🚨 DETECTED SCAM PATTERNS
────────────────────────────────────────────────────────────
`;

    if (result.detected_patterns.length === 0) {
        report += 'No specific social engineering patterns detected.\n';
    } else {
        result.detected_patterns.forEach((pattern, i) => {
            report += `\n[${i + 1}] ${pattern.pattern_name}
    └─ IMPACT: +${pattern.risk_contribution} risk points
    └─ EVIDENCE: ${pattern.keywords.join(', ')}
    └─ ANALYSIS: ${pattern.explanation}\n`;
        });
    }

    if (result.known_scam_match && result.known_scam_match.is_known_scam) {
        report += `
🎯 KNOWN FRAUD CAMPAIGN MATCH
────────────────────────────────────────────────────────────
Pattern identified as: ${result.known_scam_match.top_match.campaign_name}
Threat Severity:      ${result.known_scam_match.top_match.severity}
Match Confidence:     ${(result.known_scam_match.overall_match_confidence * 100).toFixed(1)}%
Description:          ${result.known_scam_match.top_match.description}
Avg Financial Loss:   ${result.known_scam_match.top_match.loss_average}
`;
    }

    if (result.voice_analysis) {
        report += `
🎤 BIOMETRIC & VOICE CHARACTERISTICS
────────────────────────────────────────────────────────────
Speaking Rate:   ${(result.voice_analysis.speaking_rate * 100).toFixed(1)}%
Pitch Variation: ${(result.voice_analysis.pitch_variation * 100).toFixed(1)}%
Silence Ratio:   ${(result.voice_analysis.silence_ratio * 100).toFixed(1)}%
Analysis Score:  ${result.voice_analysis.voice_quality_score.toFixed(1)}/100
`;
    }

    report += `
💡 AI RECOMMENDATION
────────────────────────────────────────────────────────────
${result.explanation.replace(/<br>/g, '\n')}

═══════════════════════════════════════════════════════════
PRIVACY NOTICE: This report is generated locally and does
not include the original audio file to protect privacy.
═══════════════════════════════════════════════════════════
`;
    return report;
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', async () => {
    // Check API health
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('✅ API is healthy');
        }
    } catch (error) {
        console.error('⚠️ API not reachable. Make sure backend is running at', API_BASE_URL);
    }
});
