"use client";

import React, { useState, useEffect } from "react";

const LANGUAGES = [
  { id: 'awadhi', label: 'अवधी' },
  { id: 'bhojpuri', label: 'भोजपुरी' },
  { id: 'hindi', label: 'हिंदी' },
  { id: 'english', label: 'English' },
];

export default function SamaadSetuUnifiedApp() {
  const [activeTab, setActiveTab] = useState<"citizen" | "officer">("citizen");
  const [districtFilter, setDistrictFilter] = useState<string>("All Districts");
  const [selectedTicket, setSelectedTicket] = useState<any>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [selectedLang, setSelectedLang] = useState<string>("hindi");
  const citizenDialect = selectedLang;

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const speakText = (text: string) => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utter = new SpeechSynthesisUtterance(text);
      utter.lang = citizenDialect === "english" ? "en-IN" : "hi-IN";
      utter.rate = 0.9;
      window.speechSynthesis.speak(utter);
    }
  };

  // Demo active tickets synchronized across both tabs
  const [tickets, setTickets] = useState([
    {
      id: "EMG-2024-0010",
      district: "Varanasi",
      department: "uppcl",
      deptName: "विद्युत विभाग (UPPCL)",
      status: "received",
      priority: "P1",
      urgency: 5,
      isHazard: true,
      hazardType: "LIVE_ELECTRIC_WIRE",
      reassignmentCount: 0,
      reassignmentLocked: false,
      transcript: "हाई टेंशन बिजली का तार टूट के पानी भरे रास्ते में गिर गया है, कभी भी बड़ा हादसा हो सकता है तुरंत बंद कराइए!",
      maskedPhone: "+91 98••• ••842",
      clusterId: "CLU-003",
      clusterSize: 12,
      createdAt: "10 mins ago",
      exifDelta: "12m",
      landmarkScore: 0.96
    },
    {
      id: "GRV-2024-0006",
      district: "Agra",
      department: "jal_nigam",
      deptName: "जल निगम (Jal Nigam)",
      status: "verified_assigned",
      priority: "P2",
      urgency: 4,
      isHazard: false,
      reassignmentCount: 1,
      reassignmentLocked: true,
      transcript: "गंदा नाली का पानी पीने के नल के पास जमा हो रहा है। जल निगम बोल रहा है नगर निगम का काम है, कोई सुनवाई नहीं हो रही।",
      maskedPhone: "+91 94••• ••519",
      clusterId: "CLU-006",
      clusterSize: 2,
      createdAt: "2 hours ago",
      exifDelta: "35m",
      landmarkScore: 0.81
    },
    {
      id: "GRV-2024-0001",
      district: "Lucknow",
      department: "pwd",
      deptName: "लोक निर्माण विभाग (PWD)",
      status: "work_started",
      priority: "P2",
      urgency: 3,
      isHazard: false,
      reassignmentCount: 0,
      reassignmentLocked: false,
      transcript: "सड़क में बड़ा गड्ढा है, बरसात का पानी भर गया है और गाड़ियां पलट रही हैं।",
      maskedPhone: "+91 97••• ••312",
      clusterId: "CLU-001",
      clusterSize: 4,
      createdAt: "1 day ago",
      exifDelta: "22m",
      landmarkScore: 0.88
    }
  ]);

  const handleSimulateVoiceSubmit = () => {
    setIsRecording(true);
    showToast("🎙️ Listening in Awadhi / Hindi...");
    setTimeout(() => {
      setIsRecording(false);
      const newTicket = {
        id: `GRV-2024-${Math.floor(1000 + Math.random() * 9000)}`,
        district: "Gorakhpur",
        department: "pwd",
        deptName: "लोक निर्माण विभाग (PWD)",
        status: "received",
        priority: "P2",
        urgency: 3,
        isHazard: false,
        reassignmentCount: 0,
        reassignmentLocked: false,
        transcript: "गांव की मुख्य पुलिया की दीवार धंस गई है, भारी वाहन निकलने पर दुर्घटना का डर है।",
        maskedPhone: "+91 99••• ••104",
        clusterId: "CLU-007",
        clusterSize: 1,
        createdAt: "Just now",
        exifDelta: "18m",
        landmarkScore: 0.89
      };
      setTickets([newTicket, ...tickets]);
      showToast("✓ फरियाद दर्ज हो गई! (Audio readback generated)");
      speakText("आपकी शिकायत लोक निर्माण विभाग में सफलतापूर्वक दर्ज हो गई है।");
    }, 2000);
  };

  const handleReassign = (ticketId: string) => {
    setTickets(prev =>
      prev.map(t => {
        if (t.id === ticketId) {
          if (t.reassignmentLocked) {
            showToast("🚨 ONE-HOP LOCKED: Auto-escalated to District Magistrate!");
            return t;
          }
          showToast("↩ Reassigned to PWD. Allowance 1/1 Used (Now Locked).");
          return {
            ...t,
            department: "pwd",
            deptName: "लोक निर्माण विभाग (PWD)",
            reassignmentCount: 1,
            reassignmentLocked: true
          };
        }
        return t;
      })
    );
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100">
      {/* ── TOP UNIFIED NAVIGATION TOGGLE ── */}
      <header className="bg-slate-900 border-b border-slate-800 px-6 py-3 sticky top-0 z-50 flex flex-wrap items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-br from-blue-600 to-indigo-700 p-2 rounded-xl text-2xl shadow">🏛️</div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-black tracking-tight text-white">SamaadSetu (संवादसेतु)</h1>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-900/60 text-blue-300 border border-blue-700">UP 1076 Engine</span>
            </div>
            <p className="text-xs text-slate-400">Universal Citizen Intake & Officer Triage Across 75 Districts</p>
          </div>
        </div>

        {/* Top View Mode Switcher */}
        <div className="flex items-center bg-slate-950 p-1.5 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab("citizen")}
            className={`px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 transition-all ${
              activeTab === "citizen"
                ? "bg-blue-600 text-white shadow-lg"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <span>📱</span> Citizen Portal (Voice-First)
          </button>
          <button
            onClick={() => setActiveTab("officer")}
            className={`px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 transition-all ${
              activeTab === "officer"
                ? "bg-indigo-600 text-white shadow-lg"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <span>👮</span> Officer Triage Desk (75 DMs)
          </button>
        </div>

        {/* Language Selector Inside Header */}
        <div className="flex flex-wrap items-center gap-2.5 py-1.5 overflow-visible">
          {LANGUAGES.map((lang) => {
            const isActive = selectedLang === lang.id;
            return (
              <button
                key={lang.id}
                type="button"
                onClick={() => {
                  setSelectedLang(lang.id);
                  showToast(`Language set to ${lang.label}`);
                }}
                className={`inline-flex items-center justify-center min-w-[88px] h-9 px-4 rounded-full text-sm font-semibold leading-normal transition-all border ${
                  isActive
                    ? 'bg-blue-600 border-blue-400 text-white shadow-sm shadow-blue-500/30'
                    : 'bg-slate-800 border-slate-700 text-slate-200 hover:bg-slate-700 hover:border-slate-500'
                }`}
              >
                {lang.label}
              </button>
            );
          })}
        </div>

        {/* Right Stats Quick Pill */}
        <div className="hidden md:flex items-center gap-3 text-xs">
          <div className="bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700 text-slate-300">
            Active: <span className="font-bold text-white ml-1">{tickets.length}</span>
          </div>
          <div className="bg-red-950/70 border border-red-800 px-3 py-1.5 rounded-lg text-red-300 font-bold flex items-center gap-1.5 animate-pulse">
            🚨 Hazards: {tickets.filter(t => t.isHazard).length}
          </div>
        </div>
      </header>

      {/* ── TOAST NOTIFICATION ── */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-blue-600 text-white px-5 py-3 rounded-xl shadow-2xl font-bold text-sm flex items-center gap-2 border border-blue-400">
          <span>🔔</span> {toastMessage}
        </div>
      )}

      {/* ── MAIN CONTENT: CITIZEN VIEW OR OFFICER VIEW ── */}
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
        {activeTab === "citizen" ? (
          /* ============================================================
             VIEW 1: CITIZEN PORTAL (VOICE-FIRST & PICTORIAL)
             ============================================================ */
          <div className="max-w-xl mx-auto space-y-6">
            {/* Welcoming Dialect Banner */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg text-center space-y-3">
              <div className="flex justify-center gap-2">
                {(["hindi", "awadhi", "bhojpuri", "english"] as const).map(lang => (
                  <button
                    key={lang}
                    onClick={() => {
                      setCitizenDialect(lang);
                      showToast(`Language set to ${lang.toUpperCase()}`);
                    }}
                    className={`px-3 py-1.5 rounded-full text-xs font-bold capitalize transition-all ${
                      citizenDialect === lang
                        ? "bg-blue-600 text-white shadow"
                        : "bg-slate-800 text-slate-400 hover:text-white"
                    }`}
                  >
                    🗣 {lang}
                  </button>
                ))}
              </div>
              <p className="text-base text-slate-200 font-medium">
                {citizenDialect === "awadhi"
                  ? "राम राम! संवादसेतु मा आपका स्वागत बा। माइक दबाईं और अपनी फरियाद बोलीं।"
                  : citizenDialect === "bhojpuri"
                  ? "प्रणाम! संवादसेतु में रउआ के स्वागत बा। माइक दबाईं और अपनी शिकायत कहीं।"
                  : "नमस्ते! संवादसेतु में आपका स्वागत है। माइक दबाएं और अपनी समस्या बोलें।"}
              </p>
              <button
                onClick={() =>
                  speakText(
                    citizenDialect === "awadhi"
                      ? "माइक का बटन दबाईं और अपनी बात बोलीं।"
                      : "माइक का बटन दबाएं और अपनी शिकायत बोलें।"
                  )
                }
                className="inline-flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-blue-400 px-4 py-2 rounded-full text-xs font-bold border border-slate-700"
              >
                🔊 निर्देश सुनें / Listen Instruction
              </button>
            </div>

            {/* Oversized Pictorial 4-Tiles Grid */}
            <div className="grid grid-cols-2 gap-4">
              {/* Blue Mic Tile */}
              <button
                onClick={handleSimulateVoiceSubmit}
                className={`p-6 rounded-2xl flex flex-col items-center justify-center gap-3 transition-all transform active:scale-95 shadow-xl border-2 ${
                  isRecording
                    ? "bg-red-900/80 border-red-500 animate-pulse text-white"
                    : "bg-blue-900/40 hover:bg-blue-900/60 border-blue-600 text-blue-200"
                }`}
                style={{ minHeight: "150px" }}
              >
                <span className="text-5xl">{isRecording ? "🔴" : "🎙️"}</span>
                <span className="font-extrabold text-base text-center leading-tight">
                  {isRecording ? "रिकॉर्ड हो रहा है..." : "बोलकर शिकायत करें\nSpeak Complaint"}
                </span>
                <span className="text-[11px] text-blue-300">अवधी / भोजपुरी / हिंदी</span>
              </button>

              {/* Green Camera Tile */}
              <button
                onClick={() => showToast("📸 Geo-tagged camera simulated (<150 KB WebP preserved)")}
                className="bg-emerald-950/40 hover:bg-emerald-950/60 border-2 border-emerald-600 p-6 rounded-2xl flex flex-col items-center justify-center gap-3 transition-all transform active:scale-95 shadow-xl text-emerald-200"
                style={{ minHeight: "150px" }}
              >
                <span className="text-5xl">📷</span>
                <span className="font-extrabold text-base text-center leading-tight">
                  फोटो / वीडियो लें<br />Live Photo Proof
                </span>
                <span className="text-[11px] text-emerald-400">📍 Live EXIF Geo-Tagged</span>
              </button>

              {/* Purple Slip Tile */}
              <button
                onClick={() => showToast("🧾 Document OCR reader ready for electricity/water bills")}
                className="bg-purple-950/40 hover:bg-purple-950/60 border-2 border-purple-600 p-6 rounded-2xl flex flex-col items-center justify-center gap-3 transition-all transform active:scale-95 shadow-xl text-purple-200"
                style={{ minHeight: "150px" }}
              >
                <span className="text-5xl">🧾</span>
                <span className="font-extrabold text-base text-center leading-tight">
                  रसीद / पर्ची जोड़ें<br />Attach Slip / Bill
                </span>
                <span className="text-[11px] text-purple-300">Auto OCR Extractor</span>
              </button>

              {/* Amber Tracker Tile */}
              <button
                onClick={() => {
                  setSelectedTicket(tickets[0]);
                  showToast("📊 Live Pictorial Tracker opened below");
                }}
                className="bg-amber-950/40 hover:bg-amber-950/60 border-2 border-amber-600 p-6 rounded-2xl flex flex-col items-center justify-center gap-3 transition-all transform active:scale-95 shadow-xl text-amber-200"
                style={{ minHeight: "150px" }}
              >
                <span className="text-5xl">📊</span>
                <span className="font-extrabold text-base text-center leading-tight">
                  हाल जानें (ट्रैकर)<br />Track Progress
                </span>
                <span className="text-[11px] text-amber-400">🔊 Tap to Hear Status</span>
              </button>
            </div>

            {/* 4-Step Pictorial Milestone Tracker */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="font-bold text-sm text-slate-300 flex items-center gap-2">
                  <span>📌</span> आपकी ताज़ा शिकायतें (Recent Grievances)
                </h3>
                <span className="text-xs text-slate-500">Auto-synced</span>
              </div>

              <div className="space-y-3">
                {tickets.map(t => (
                  <div
                    key={t.id}
                    onClick={() => setSelectedTicket(t)}
                    className={`p-4 rounded-xl border transition-all cursor-pointer ${
                      selectedTicket?.id === t.id
                        ? "bg-slate-800 border-blue-500 shadow-md"
                        : "bg-slate-950 border-slate-800 hover:border-slate-700"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-mono font-bold text-xs text-white">{t.id}</span>
                        <span className="text-[10px] px-2 py-0.5 rounded font-bold bg-blue-950 text-blue-300 border border-blue-800">
                          {t.deptName}
                        </span>
                        {t.isHazard && (
                          <span className="text-[10px] px-2 py-0.5 rounded font-bold bg-red-900 text-red-100 border border-red-600 animate-pulse">
                            🚨 P1 Emergency
                          </span>
                        )}
                      </div>
                      <button
                        onClick={e => {
                          e.stopPropagation();
                          speakText(t.transcript);
                        }}
                        className="text-xs bg-slate-800 hover:bg-slate-700 p-1.5 rounded-full text-slate-300"
                      >
                        🔊
                      </button>
                    </div>
                    <p className="text-xs text-slate-300 leading-snug line-clamp-2">"{t.transcript}"</p>
                    <div className="flex items-center justify-between text-[11px] text-slate-500 mt-2">
                      <span>📍 {t.district}</span>
                      <span>🕒 {t.createdAt}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          /* ============================================================
             VIEW 2: OFFICER & DM TRIAGE WORKBENCH (75 DISTRICTS)
             ============================================================ */
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left 2 Cols: Queue & Anomaly Banners */}
            <div className="lg:col-span-2 space-y-4">
              {/* Seasonal Anomaly Banner */}
              <div className="bg-amber-950/40 border border-amber-700/80 rounded-2xl p-4 flex items-start gap-3 text-amber-200 text-xs">
                <span className="text-2xl">⚠️</span>
                <div>
                  <p className="font-bold">Automated Seasonal Anomaly & Cluster Detection (UP East)</p>
                  <p className="text-[11px] text-amber-300 mt-0.5 leading-relaxed">
                    Spike detected in <b>Varanasi & Gorakhpur</b> for snapped power lines and transformer burnouts. 12 complaints merged into Master Cluster <b>CLU-003</b>. Life-safety sub-tickets extracted autonomously.
                  </p>
                </div>
              </div>

              {/* Filter Strip */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 flex flex-wrap items-center justify-between gap-3 text-xs">
                <div className="flex items-center gap-2">
                  <span className="text-slate-400 font-bold">District Filter:</span>
                  <select
                    value={districtFilter}
                    onChange={e => setDistrictFilter(e.target.value)}
                    className="bg-slate-950 border border-slate-700 text-white px-3 py-1.5 rounded-lg focus:outline-none focus:border-blue-500"
                  >
                    <option>All Districts (75)</option>
                    <option>Varanasi</option>
                    <option>Lucknow</option>
                    <option>Agra</option>
                    <option>Gorakhpur</option>
                    <option>Bareilly</option>
                  </select>
                </div>
                <div className="text-slate-400">
                  Showing <b>{tickets.length}</b> live complaints
                </div>
              </div>

              {/* Triage Tickets Queue */}
              <div className="space-y-3">
                {tickets.map(t => (
                  <div
                    key={t.id}
                    onClick={() => setSelectedTicket(t)}
                    className={`p-4 rounded-2xl border transition-all cursor-pointer ${
                      selectedTicket?.id === t.id
                        ? "bg-slate-900 border-indigo-500 shadow-xl"
                        : "bg-slate-900/60 border-slate-800 hover:border-slate-700"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-mono font-black text-sm text-white">{t.id}</span>
                        <span className="text-xs px-2 py-0.5 rounded font-bold bg-slate-800 text-slate-300">
                          {t.priority}
                        </span>
                        <span className="text-xs px-2 py-0.5 rounded font-bold bg-indigo-950 text-indigo-300 border border-indigo-800">
                          {t.deptName}
                        </span>
                        {t.isHazard && (
                          <span className="text-xs px-2 py-0.5 rounded font-black bg-red-900 text-white border border-red-500 animate-pulse">
                            🚨 P1 Hazard Sub-Ticket
                          </span>
                        )}
                        {t.reassignmentLocked && (
                          <span className="text-xs px-2 py-0.5 rounded font-bold bg-amber-950 text-amber-300 border border-amber-700">
                            🔒 1-Hop Locked
                          </span>
                        )}
                      </div>
                      <span className="text-xs text-slate-500 font-mono">GPS Δ {t.exifDelta}</span>
                    </div>

                    <p className="text-xs text-slate-300 mb-3 leading-relaxed">"{t.transcript}"</p>

                    <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800/80">
                      <span>📍 {t.district}</span>
                      <span>🔗 Cluster: {t.clusterId} ({t.clusterSize} merged)</span>
                      <span>📞 {t.maskedPhone}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Right Col: AI Forensics & Closed-Loop Workbench */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
              <div className="border-b border-slate-800 pb-3">
                <h3 className="font-bold text-sm text-slate-200 flex items-center gap-2">
                  <span>🔬</span> AI Proof Forensics & Governance Controls
                </h3>
                <p className="text-[11px] text-slate-500">Live inspection for selected ticket</p>
              </div>

              {selectedTicket ? (
                <div className="space-y-4 text-xs">
                  {/* Anti-Intimidation Phone Masking Card */}
                  <div className="bg-slate-950 border border-slate-800 p-3.5 rounded-xl space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-400">Citizen Phone Masking:</span>
                      <span className="font-mono text-emerald-400 font-bold">{selectedTicket.maskedPhone}</span>
                    </div>
                    <button
                      onClick={() => showToast("📞 IVR Call bridged via +91 1800-889-UPGOV (Recording Active)")}
                      className="w-full bg-emerald-700 hover:bg-emerald-600 text-white py-2 rounded-lg font-bold flex items-center justify-center gap-1.5 transition-all"
                    >
                      <span>📞</span> Connect Masked Recorded IVR Call
                    </button>
                    <p className="text-[10px] text-slate-500">Toll-free virtual conference bridge protects citizens against field harassment.</p>
                  </div>

                  {/* EXIF vs Upload GPS Separation */}
                  <div className="bg-slate-950 border border-slate-800 p-3.5 rounded-xl space-y-1.5">
                    <span className="font-bold text-slate-400">GPS & Forensics Delta:</span>
                    <div className="grid grid-cols-2 gap-2 text-[11px] mt-1">
                      <div className="bg-slate-900 p-2 rounded border border-slate-800">
                        <span className="text-slate-500 block">EXIF Capture GPS:</span>
                        <span className="text-slate-200 font-mono font-bold">25.3182, 82.9751</span>
                      </div>
                      <div className="bg-slate-900 p-2 rounded border border-slate-800">
                        <span className="text-slate-500 block">Network Upload GPS:</span>
                        <span className="text-slate-200 font-mono font-bold">25.3180, 82.9750</span>
                      </div>
                    </div>
                    <p className="text-[10px] text-emerald-400 font-bold pt-1">✓ Verified Rural Deferred Upload (Δ 12m, mock location flags negative)</p>
                  </div>

                  {/* 1-Hop Reassignment Routing Lock */}
                  <div className="bg-slate-950 border border-slate-800 p-3.5 rounded-xl space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-400">Department Routing:</span>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                        {selectedTicket.reassignmentLocked ? "🔒 Locked (1/1 Used)" : "Allowance: 0/1 Used"}
                      </span>
                    </div>
                    <button
                      onClick={() => handleReassign(selectedTicket.id)}
                      className={`w-full py-2 rounded-lg font-bold transition-all ${
                        selectedTicket.reassignmentLocked
                          ? "bg-slate-800 text-slate-500 cursor-not-allowed"
                          : "bg-blue-800 hover:bg-blue-700 text-white"
                      }`}
                    >
                      {selectedTicket.reassignmentLocked
                        ? "🔒 Locked — Dispute Escalated to DM"
                        : "↩ Execute 1-Time Transfer to PWD"}
                    </button>
                    <p className="text-[10px] text-slate-500">Enforces single-hop limit to eliminate inter-departmental hot-potato delays.</p>
                  </div>

                  {/* Closed-Loop Resolution Verification */}
                  <div className="bg-slate-950 border border-slate-800 p-3.5 rounded-xl space-y-2">
                    <span className="font-bold text-slate-400">Two-Way Resolution Verification:</span>
                    <button
                      onClick={() => showToast("✅ After Photo Verified! Landmark Match 88%. Ticket Marked Resolved.")}
                      className="w-full bg-indigo-700 hover:bg-indigo-600 text-white py-2 rounded-lg font-bold flex items-center justify-center gap-1.5 transition-all"
                    >
                      <span>📸</span> Upload Geo-Tagged After Photo
                    </button>
                    <p className="text-[10px] text-slate-500">VLM verifies background landmarks and defect rectification before permitting closure.</p>
                  </div>
                </div>
              ) : (
                <div className="py-20 text-center text-slate-600">
                  <span className="text-4xl block mb-2">👈</span>
                  Select a ticket from the triage queue to view AI forensics and governance controls.
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
