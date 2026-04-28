import React, { useState, useEffect, useCallback } from "react";
import {
  Shield,
  Plus,
  RefreshCw,
  Search,
  Activity,
  Clock,
  Send,
  Skull,
  TrendingUp,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Menu,
  X,
  Download,
} from "lucide-react";
import { reportsApi } from "../api/reports";
import type { ScamReport, Stats } from "../types";
import { useAuth } from "../context/AuthContext";
import ReportsTable from "../components/ReportsTable";
import SubmitModal from "../components/SubmitModal";
import LookupPanel from "../components/LookupPanel";
import type { EmailPayload } from "../components/ReportsTable";
import AdLibraryPanel from "../components/AddLibraryPanel";
import GoogleAdsPanel from "../components/GoogleAdsPanel";


const Dashboard: React.FC = () => {
  const [reports, setReports] = useState<ScamReport[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState("");
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [showSubmit, setShowSubmit] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const { user, logout } = useAuth();

  const PAGE_SIZE = 20;

  const showToast = (msg: string, ok: boolean) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 4000);
  };

  const fetchAll = useCallback(async () => {
    try {
      const [reportData, statsData] = await Promise.all([
        reportsApi.listReports({ page, page_size: PAGE_SIZE, search, status: filterStatus }),
        reportsApi.getStats(),
      ]);
      setReports(reportData.results);
      setTotal(reportData.total);
      setStats(statsData);
    } catch (err: any) {
      showToast(err.message || "Fetch failed", false);
    } finally {
      setLoading(false);
    }
  }, [page, search, filterStatus]);

  useEffect(() => {
    setLoading(true);
    fetchAll();
  }, [fetchAll]);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const wsBase = import.meta.env.VITE_WS_URL || "wss://scam-slayer-api.onrender.com";
    let ws: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    let unmounted = false;
    const MAX_DELAY = 30_000;

    const connect = (delay = 1000) => {
      if (unmounted) return;
      ws = new WebSocket(`${wsBase}/ws/reports/?token=${token}`);
      ws.onopen = () => { delay = 1000; };
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setReports((prev) => prev.map((r) => (r.id === data.id ? { ...r, ...data } : r)));
          fetchAll();
        } catch {}
      };
      ws.onerror = () => {};
      ws.onclose = () => {
        if (unmounted) return;
        const nextDelay = Math.min(delay * 2, MAX_DELAY);
        reconnectTimer = setTimeout(() => connect(nextDelay), delay);
      };
    };

    connect();
    return () => {
      unmounted = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      ws?.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleAction = async (id: string, action: "report" | "kill") => {
    setActionLoading(`${id}-${action}`);
    try {
      const fn = action === "report" ? reportsApi.triggerReport : reportsApi.killReport;
      const result = await fn(id);
      showToast(result.message, result.success);
      if (result.success) {
        setReports((prev) =>
          prev.map((r) => (r.id === id ? { ...r, status: result.new_status as any } : r))
        );
        fetchAll();
      }
    } catch (err: any) {
      showToast(err.message || "Action failed", false);
    } finally {
      setActionLoading(null);
    }
  };

  const handleEmailReport = async (reportId: string, payload: EmailPayload) => {
    try {
      await reportsApi.sendEmail(reportId, payload);
      showToast("Complaint email sent successfully", true);
      fetchAll();
    } catch (err: any) {
      showToast(err.response?.data?.detail || "Failed to send email", false);
    }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  const statusFilters = [
    { value: "", label: "All", color: "text-[#9ca3af]" },
    { value: "pending", label: "Pending", color: "text-amber-400" },
    { value: "reported", label: "Reported", color: "text-blue-400" },
    { value: "killed", label: "Killed", color: "text-emerald-400" },
    { value: "failed", label: "Failed", color: "text-red-400" },
  ];

  return (
    <div className="min-h-screen bg-[#08090d] text-white font-sans">
      {/* Ambient background glow */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-red-500/3 rounded-full blur-3xl" />
        <div className="absolute bottom-1/3 right-1/4 w-64 h-64 bg-blue-500/3 rounded-full blur-3xl" />
      </div>

      {/* Toast */}
      {toast && (
        <div className={`fixed top-5 right-5 z-50 flex items-center gap-3 px-4 py-3 rounded-xl border text-sm font-medium shadow-2xl max-w-sm backdrop-blur-sm transition-all animate-in slide-in-from-right-4 ${
          toast.ok
            ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-300"
            : "bg-red-500/10 border-red-500/20 text-red-300"
        }`}>
          <span className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold ${toast.ok ? "bg-emerald-500/20" : "bg-red-500/20"}`}>
            {toast.ok ? "✓" : "✗"}
          </span>
          {toast.msg}
        </div>
      )}

      <SubmitModal
        open={showSubmit}
        onClose={() => setShowSubmit(false)}
        onSuccess={(r) => {
          setReports((prev) => [r, ...prev]);
          showToast(`Report submitted — RespOrg: ${r.resporg_raw || "pending"}`, true);
          fetchAll();
        }}
      />

      {/* ── HEADER ── */}
      <header className="sticky top-0 z-40 border-b border-white/[0.04] bg-[#08090d]/90 backdrop-blur-xl">
        <div className="max-w-[1680px] mx-auto px-5 sm:px-8 h-16 flex items-center justify-between gap-4">

          {/* Brand */}
          <div className="flex items-center gap-3 shrink-0">
            <div className="relative">
              <div className="w-8 h-8 rounded-lg bg-red-500/15 border border-red-500/25 flex items-center justify-center">
                <Shield size={15} className="text-red-400" />
              </div>
              <div className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-400 border border-[#08090d] animate-pulse" />
            </div>
            <div className="hidden sm:flex flex-col leading-none">
              <span className="text-white font-bold text-sm tracking-tight">Scam Slayer</span>
              <span className="text-[#3d4251] text-[10px] font-mono uppercase tracking-widest">SOC Portal</span>
            </div>
          </div>

          {/* Center: user pill */}
          <div className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/[0.03] border border-white/[0.06] text-xs text-[#6b7280] font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0" />
            <span className="truncate max-w-[200px]">{user?.email}</span>
            <span className="text-[#3d4251]">·</span>
            <span className="text-[#4b5563] uppercase">{user?.role}</span>
          </div>

          {/* Right actions */}
          <div className="hidden md:flex items-center gap-2">
            <button
              onClick={() => { setLoading(true); fetchAll(); }}
              title="Refresh"
              className="w-9 h-9 flex items-center justify-center rounded-lg border border-white/[0.06] text-[#6b7280] hover:text-white hover:border-white/[0.12] hover:bg-white/[0.03] transition-all"
            >
              <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
            </button>
            <button
              onClick={() => reportsApi.exportCsv()}
              className="flex items-center gap-2 h-9 px-3.5 rounded-lg border border-white/[0.06] text-[#9ca3af] hover:text-white hover:border-white/[0.12] hover:bg-white/[0.03] text-xs font-medium transition-all"
            >
              <Download size={13} />
              Export
            </button>
            <button
              onClick={() => setShowSubmit(true)}
              className="flex items-center gap-2 h-9 px-4 bg-red-500 hover:bg-red-400 rounded-lg text-white text-xs font-semibold transition-all shadow-lg shadow-red-500/20"
            >
              <Plus size={13} />
              Submit Report
            </button>
            <div className="w-px h-5 bg-white/[0.06]" />
            <button
              onClick={logout}
              title="Logout"
              className="w-9 h-9 flex items-center justify-center rounded-lg border border-white/[0.06] text-[#6b7280] hover:text-red-400 hover:border-red-500/25 transition-all"
            >
              <LogOut size={14} />
            </button>
          </div>

          {/* Mobile toggle */}
          <button
            className="md:hidden w-9 h-9 flex items-center justify-center rounded-lg border border-white/[0.06] text-[#6b7280]"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X size={16} /> : <Menu size={16} />}
          </button>
        </div>

        {/* Mobile drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-white/[0.04] bg-[#0b0c12] px-5 py-4 space-y-3">
            <p className="text-xs text-[#4b5563] font-mono truncate">{user?.email} · {user?.role}</p>
            <div className="flex gap-2">
              <button onClick={() => { setLoading(true); fetchAll(); }}
                className="flex-1 h-9 flex items-center justify-center gap-2 rounded-lg border border-white/[0.06] text-[#9ca3af] text-xs">
                <RefreshCw size={13} className={loading ? "animate-spin" : ""} /> Refresh
              </button>
              <button onClick={() => setShowSubmit(true)}
                className="flex-1 h-9 flex items-center justify-center gap-2 bg-red-500 rounded-lg text-white text-xs font-semibold">
                <Plus size={13} /> Submit
              </button>
              <button onClick={logout}
                className="w-9 h-9 flex items-center justify-center rounded-lg border border-white/[0.06] text-[#6b7280]">
                <LogOut size={13} />
              </button>
            </div>
          </div>
        )}
      </header>

      {/* ── MAIN ── */}
      <main className="relative max-w-[1680px] mx-auto px-5 sm:px-8 py-8 space-y-6">

        {/* Page title row */}
        <div className="flex items-end justify-between">
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">Overview</h1>
            <p className="text-xs text-[#4b5563] mt-0.5 font-mono">Real-time scam intelligence dashboard</p>
          </div>
          <span className="hidden sm:flex items-center gap-1.5 text-[10px] text-[#3d4251] font-mono uppercase tracking-wider">
            <span className="w-1 h-1 rounded-full bg-emerald-400 animate-pulse" />
            Live stream active
          </span>
        </div>

        {/* ── STATS GRID ── */}
        {stats && (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            {[
              { label: "Total Reports", value: stats.total, icon: Activity, accent: "#6b7280", bg: "bg-white/[0.02]", border: "border-white/[0.05]" },
              { label: "Pending", value: stats.pending, icon: Clock, accent: "#f59e0b", bg: "bg-amber-500/[0.04]", border: "border-amber-500/10" },
              { label: "Reported", value: stats.reported, icon: Send, accent: "#3b82f6", bg: "bg-blue-500/[0.04]", border: "border-blue-500/10" },
              { label: "Killed", value: stats.killed, icon: Skull, accent: "#10b981", bg: "bg-emerald-500/[0.04]", border: "border-emerald-500/10" },
              { label: "This Week", value: stats.this_week, icon: TrendingUp, accent: "#a855f7", bg: "bg-purple-500/[0.04]", border: "border-purple-500/10", sub: `of ${stats.total} total` },
            ].map(({ label, value, icon: Icon, accent, bg, border, sub }) => (
              <div key={label} className={`${bg} ${border} border rounded-xl p-4 flex flex-col gap-3 relative overflow-hidden group hover:border-opacity-30 transition-all`}>
                <div className="flex items-center justify-between">
                  <span className="text-[11px] text-[#4b5563] font-medium uppercase tracking-wider">{label}</span>
                  <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: `${accent}15` }}>
                    <Icon size={13} style={{ color: accent }} />
                  </div>
                </div>
                <div>
                  <span className="text-2xl font-bold text-white tabular-nums">{value.toLocaleString()}</span>
                  {sub && <p className="text-[10px] text-[#3d4251] font-mono mt-0.5">{sub}</p>}
                </div>
                <div className="absolute bottom-0 left-0 right-0 h-px" style={{ background: `linear-gradient(90deg, transparent, ${accent}30, transparent)` }} />
              </div>
            ))}
          </div>
        )}

        {/* ── TOOL PANELS ── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="bg-white/[0.02] border border-white/[0.05] rounded-xl overflow-hidden">
            <LookupPanel
              onSubmit={async (data) => {
                try {
                  const report = await reportsApi.createReport(data);
                  setReports((prev) => [report, ...prev]);
                  showToast(`Report submitted — ${report.phone_number}`, true);
                  fetchAll();
                } catch (err: any) {
                  showToast(err.response?.data?.detail || "Submit failed", false);
                }
              }}
            />
          </div>
          <div className="bg-white/[0.02] border border-white/[0.05] rounded-xl overflow-hidden">
            <AdLibraryPanel />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="bg-white/[0.02] border border-white/[0.05] rounded-xl overflow-hidden">
            <GoogleAdsPanel />
          </div>
        </div>

        {/* ── REPORTS TABLE SECTION ── */}
        <div className="bg-white/[0.02] border border-white/[0.05] rounded-xl overflow-hidden">

          {/* Table header bar */}
          <div className="px-5 py-4 border-b border-white/[0.04] flex flex-col sm:flex-row items-start sm:items-center gap-3">
            <div className="flex-1 flex flex-col sm:flex-row items-start sm:items-center gap-3 w-full">
              <div className="relative w-full sm:max-w-xs">
                <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#3d4251]" />
                <input
                  className="w-full h-9 bg-white/[0.03] border border-white/[0.06] rounded-lg pl-8 pr-3 text-xs text-white font-mono placeholder-[#3d4251] focus:outline-none focus:border-white/[0.15] focus:bg-white/[0.04] transition-all"
                  placeholder="Search brand, number, URL..."
                  value={search}
                  onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                />
              </div>

              {/* Status filters */}
              <div className="flex items-center gap-1.5 flex-wrap">
                {statusFilters.map(({ value, label, color }) => (
                  <button
                    key={value || "all"}
                    onClick={() => { setFilterStatus(value); setPage(1); }}
                    className={`h-7 px-3 rounded-md text-[11px] font-mono font-medium border transition-all ${
                      filterStatus === value
                        ? `bg-white/[0.06] border-white/[0.12] ${color}`
                        : "border-transparent text-[#4b5563] hover:text-[#9ca3af] hover:border-white/[0.06]"
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {/* Table actions */}
            <div className="flex items-center gap-2 shrink-0">
              <span className="hidden sm:block text-[11px] text-[#3d4251] font-mono">
                {total.toLocaleString()} records
              </span>
              <button
                onClick={() => reportsApi.exportCsv()}
                className="flex items-center gap-1.5 h-8 px-3 rounded-lg border border-white/[0.06] text-[#6b7280] hover:text-white hover:border-white/[0.12] text-xs font-medium transition-all"
              >
                <Download size={12} />
                <span className="hidden sm:inline">CSV</span>
              </button>
              <button
                onClick={() => { setLoading(true); fetchAll(); }}
                className="h-8 px-3 flex items-center gap-1.5 rounded-lg border border-white/[0.06] text-[#6b7280] hover:text-white hover:border-white/[0.12] text-xs transition-all"
              >
                <RefreshCw size={12} className={loading ? "animate-spin" : ""} />
                <span className="hidden sm:inline">Refresh</span>
              </button>
            </div>
          </div>

          {/* Table body */}
          {loading ? (
            <div className="flex flex-col items-center justify-center py-24 gap-3">
              <RefreshCw size={20} className="animate-spin text-[#3d4251]" />
              <span className="text-xs text-[#3d4251] font-mono">Loading reports...</span>
            </div>
          ) : reports.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-24 gap-3">
              <div className="w-12 h-12 rounded-xl bg-white/[0.03] border border-white/[0.06] flex items-center justify-center">
                <Shield size={20} className="text-[#3d4251]" />
              </div>
              <p className="text-sm text-[#4b5563]">No reports found</p>
              <p className="text-xs text-[#3d4251] font-mono">Try adjusting your filters</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <ReportsTable
                reports={reports}
                actionLoading={actionLoading}
                onReport={(id) => handleAction(id, "report")}
                onKill={(id) => handleAction(id, "kill")}
                onEmailReport={handleEmailReport}
              />
            </div>
          )}

          {/* Pagination */}
          {total > PAGE_SIZE && (
            <div className="px-5 py-3.5 border-t border-white/[0.04] flex items-center justify-between gap-4">
              <span className="text-[11px] text-[#3d4251] font-mono">
                Showing <span className="text-[#6b7280]">{(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, total)}</span> of <span className="text-[#6b7280]">{total.toLocaleString()}</span>
              </span>
              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="w-8 h-8 flex items-center justify-center rounded-lg border border-white/[0.06] text-[#6b7280] hover:text-white hover:border-white/[0.12] disabled:opacity-25 disabled:cursor-not-allowed transition-all"
                >
                  <ChevronLeft size={13} />
                </button>
                <div className="flex items-center gap-1">
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    let p: number;
                    if (totalPages <= 5) p = i + 1;
                    else if (page <= 3) p = i + 1;
                    else if (page >= totalPages - 2) p = totalPages - 4 + i;
                    else p = page - 2 + i;
                    return (
                      <button
                        key={p}
                        onClick={() => setPage(p)}
                        className={`w-8 h-8 rounded-lg text-xs font-mono font-medium transition-all ${
                          p === page
                            ? "bg-white/[0.08] border border-white/[0.12] text-white"
                            : "text-[#4b5563] hover:text-[#9ca3af] hover:bg-white/[0.03]"
                        }`}
                      >
                        {p}
                      </button>
                    );
                  })}
                </div>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages}
                  className="w-8 h-8 flex items-center justify-center rounded-lg border border-white/[0.06] text-[#6b7280] hover:text-white hover:border-white/[0.12] disabled:opacity-25 disabled:cursor-not-allowed transition-all"
                >
                  <ChevronRight size={13} />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer spacer */}
        <div className="h-4" />
      </main>
    </div>
  );
};

export default Dashboard;