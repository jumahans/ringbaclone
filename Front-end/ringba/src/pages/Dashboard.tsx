import React, { useState, useEffect, useCallback, useRef, Suspense, lazy } from "react";
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
  Mail,
} from "lucide-react";
import { reportsApi } from "../api/reports";
import type { ScamReport, Stats } from "../types";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import ReportsTable from "../components/ReportsTable";
import SubmitModal from "../components/SubmitModal";
import type { EmailPayload } from "../components/ReportsTable";

const LookupPanel = lazy(() => import("../components/LookupPanel"));
const AdLibraryPanel = lazy(() => import("../components/AddLibraryPanel"));
const GoogleAdsPanel = lazy(() => import("../components/GoogleAdsPanel"));

const PAGE_SIZE = 20;
const MAX_WEBSOCKET_RETRIES = 5;
const TOKEN_CHECK_INTERVAL = 60000;
const DEBOUNCE_DELAY = 500;

function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debouncedValue;
}

const StatsSkeleton = () => (
  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
    {[1, 2, 3, 4, 5].map(i => (
      <div key={i} className="h-28 bg-white/[0.02] rounded-xl animate-pulse" />
    ))}
  </div>
);

const StatCard = React.memo(({ label, value, icon: Icon, accent, sub }: { label: string; value: number; icon: React.ElementType; accent: string; sub?: string }) => (
  <div className={`bg-white/[0.02] border border-white/[0.05] rounded-xl p-4 flex flex-col gap-3 relative overflow-hidden group hover:border-opacity-30 transition-all`}>
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
));

StatCard.displayName = 'StatCard';

const STATUS_FILTERS = [
  { value: "", label: "All", color: "text-[#9ca3af]" },
  { value: "pending", label: "Pending", color: "text-amber-400" },
  { value: "reported", label: "Reported", color: "text-blue-400" },
  { value: "killed", label: "Killed", color: "text-emerald-400" },
  { value: "failed", label: "Failed", color: "text-red-400" },
];

class ErrorBoundary extends React.Component<{ children: React.ReactNode }, { hasError: boolean }> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  componentDidCatch(error: Error) {
    console.error('Dashboard error:', error);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center py-24 gap-4">
          <p className="text-red-400">Something went wrong. Please refresh the page.</p>
          <button onClick={() => window.location.reload()} className="px-4 py-2 bg-red-500 rounded-lg text-white text-sm">Refresh Page</button>
        </div>
      );
    }
    return this.props.children;
  }
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
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
  const [wsRetryCount, setWsRetryCount] = useState(0);
  const { user, logout } = useAuth();
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const debouncedSearch = useDebounce(search, DEBOUNCE_DELAY);

  const showToast = (msg: string, ok: boolean) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 4000);
  };

  useEffect(() => {
    const checkToken = setInterval(() => {
      const token = localStorage.getItem("access_token");
      if (token) {
        try {
          const payload = JSON.parse(atob(token.split('.')[1]));
          if (payload.exp * 1000 < Date.now()) {
            logout();
            showToast("Session expired. Please login again.", false);
          }
        } catch (e) {
          console.error("Token check failed:", e);
        }
      }
    }, TOKEN_CHECK_INTERVAL);
    return () => clearInterval(checkToken);
  }, [logout]);

  const fetchAll = useCallback(async () => {
    try {
      const [reportData, statsData] = await Promise.all([
        reportsApi.listReports({ page, page_size: PAGE_SIZE, search: debouncedSearch, status: filterStatus }),
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
  }, [page, debouncedSearch, filterStatus]);

  useEffect(() => {
    setPage(1);
  }, [debouncedSearch, filterStatus]);

  useEffect(() => {
    setLoading(true);
    fetchAll();
  }, [fetchAll]);

  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        setShowSubmit(true);
      }
      if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        fetchAll();
      }
      if (e.key === 'Escape' && showSubmit) {
        setShowSubmit(false);
      }
    };
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [fetchAll, showSubmit]);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const wsBase = import.meta.env.VITE_WS_URL || "wss://scam-slayer-api.onrender.com";
    let unmounted = false;

    const connect = (delay = 1000) => {
      if (unmounted) return;
      
      try {
        const ws = new WebSocket(`${wsBase}/ws/reports/?token=${token}`);
        wsRef.current = ws;

        ws.onopen = () => {
          setWsRetryCount(0);
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            setReports((prev) => prev.map((r) => (r.id === data.id ? { ...r, ...data } : r)));
            fetchAll();
          } catch (err) {
            console.error("WebSocket message error:", err);
          }
        };

        ws.onerror = () => {};

        ws.onclose = () => {
          if (unmounted) return;
          const nextDelay = Math.min(delay * 2, 30000);
          if (wsRetryCount < MAX_WEBSOCKET_RETRIES) {
            reconnectTimerRef.current = setTimeout(() => connect(nextDelay), delay);
            setWsRetryCount(prev => prev + 1);
          }
        };
      } catch (err) {
        console.error("WebSocket connection error:", err);
      }
    };

    connect();

    return () => {
      unmounted = true;
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [fetchAll, wsRetryCount]);

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

  const statConfigs = [
    { label: "Total Reports", value: stats?.total || 0, icon: Activity, accent: "#6b7280" },
    { label: "Pending", value: stats?.pending || 0, icon: Clock, accent: "#f59e0b" },
    { label: "Reported", value: stats?.reported || 0, icon: Send, accent: "#3b82f6" },
    { label: "Killed", value: stats?.killed || 0, icon: Skull, accent: "#10b981" },
    { label: "This Week", value: stats?.this_week || 0, icon: TrendingUp, accent: "#a855f7", sub: `of ${stats?.total || 0} total` },
  ];

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-[#08090d] text-white font-sans">
        <div className="fixed inset-0 pointer-events-none">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-red-500/3 rounded-full blur-3xl" />
          <div className="absolute bottom-1/3 right-1/4 w-64 h-64 bg-blue-500/3 rounded-full blur-3xl" />
        </div>

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

        <header className="sticky top-0 z-40 border-b border-white/[0.04] bg-[#08090d]/90 backdrop-blur-xl">
          <div className="max-w-[1680px] mx-auto px-5 sm:px-8 h-16 flex items-center justify-between gap-4">
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

            <div className="hidden md:flex items-center gap-1">
              <button className="px-3 py-1.5 rounded-lg text-xs font-medium text-white bg-white/[0.03] border border-white/[0.06]">Dashboard</button>
              <button onClick={() => navigate("/emails")} className="px-3 py-1.5 rounded-lg text-xs font-medium text-[#6b7280] hover:text-white hover:bg-white/[0.03] transition-all">
                <Mail size={12} className="inline mr-1" />
                Email Logs
              </button>
            </div>

            <div className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/[0.03] border border-white/[0.06] text-xs text-[#6b7280] font-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0" />
              <span className="truncate max-w-[200px]">{user?.email}</span>
              <span className="text-[#3d4251]">·</span>
              <span className="text-[#4b5563] uppercase">{user?.role}</span>
            </div>

            <div className="hidden md:flex items-center gap-2">
              <button onClick={() => { setLoading(true); fetchAll(); }} className="w-9 h-9 flex items-center justify-center rounded-lg border border-white/[0.06] text-[#6b7280] hover:text-white hover:border-white/[0.12] transition-all">
                <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
              </button>
              <button onClick={() => reportsApi.exportCsv()} className="flex items-center gap-2 h-9 px-3.5 rounded-lg border border-white/[0.06] text-[#9ca3af] hover:text-white hover:border-white/[0.12] text-xs font-medium transition-all">
                <Download size={13} /> Export
              </button>
              <button onClick={() => navigate("/emails")} className="flex items-center gap-2 h-9 px-3.5 rounded-lg border border-white/[0.06] text-[#9ca3af] hover:text-white hover:border-white/[0.12] text-xs font-medium transition-all">
                <Mail size={13} /> Email Logs
              </button>
              <button onClick={() => setShowSubmit(true)} className="flex items-center gap-2 h-9 px-4 bg-red-500 hover:bg-red-400 rounded-lg text-white text-xs font-semibold transition-all shadow-lg shadow-red-500/20">
                <Plus size={13} /> Submit Report
              </button>
              <div className="w-px h-5 bg-white/[0.06]" />
              <button onClick={logout} className="w-9 h-9 flex items-center justify-center rounded-lg border border-white/[0.06] text-[#6b7280] hover:text-red-400 hover:border-red-500/25 transition-all">
                <LogOut size={14} />
              </button>
            </div>

            <button className="md:hidden w-9 h-9 flex items-center justify-center rounded-lg border border-white/[0.06] text-[#6b7280]" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
              {mobileMenuOpen ? <X size={16} /> : <Menu size={16} />}
            </button>
          </div>

          {mobileMenuOpen && (
            <div className="md:hidden border-t border-white/[0.04] bg-[#0b0c12] px-5 py-4 space-y-3">
              <p className="text-xs text-[#4b5563] font-mono truncate">{user?.email} · {user?.role}</p>
              <div className="flex gap-2">
                <button onClick={() => { navigate("/dashboard"); setMobileMenuOpen(false); }} className="flex-1 h-9 flex items-center justify-center gap-2 rounded-lg border border-white/[0.06] text-[#9ca3af] text-xs">
                  <Shield size={13} /> Dashboard
                </button>
                <button onClick={() => { navigate("/emails"); setMobileMenuOpen(false); }} className="flex-1 h-9 flex items-center justify-center gap-2 rounded-lg border border-white/[0.06] text-[#9ca3af] text-xs">
                  <Mail size={13} /> Email Logs
                </button>
                <button onClick={() => { setShowSubmit(true); setMobileMenuOpen(false); }} className="flex-1 h-9 flex items-center justify-center gap-2 bg-red-500 rounded-lg text-white text-xs font-semibold">
                  <Plus size={13} /> Submit
                </button>
                <button onClick={logout} className="w-9 h-9 flex items-center justify-center rounded-lg border border-white/[0.06] text-[#6b7280]">
                  <LogOut size={13} />
                </button>
              </div>
            </div>
          )}
        </header>

        <main className="relative max-w-[1680px] mx-auto px-5 sm:px-8 py-8 space-y-6">
          <div className="flex items-end justify-between">
            <div>
              <h1 className="text-xl font-bold text-white tracking-tight">Overview</h1>
              <p className="text-xs text-[#4b5563] mt-0.5 font-mono">Real-time scam intelligence dashboard</p>
            </div>
            <span className="hidden sm:flex items-center gap-1.5 text-[10px] text-[#3d4251] font-mono uppercase tracking-wider">
              <span className="w-1 h-1 rounded-full bg-emerald-400 animate-pulse" />
              Live stream {wsRetryCount > 0 && `(retry ${wsRetryCount})`}
            </span>
          </div>

          {!stats ? <StatsSkeleton /> : (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
              {statConfigs.map((config) => <StatCard key={config.label} {...config} value={config.value} />)}
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="bg-white/[0.02] border border-white/[0.05] rounded-xl overflow-hidden">
              <Suspense fallback={<div className="h-32 animate-pulse bg-white/[0.02]" />}>
                <LookupPanel onSubmit={async (data) => {
                  try {
                    const report = await reportsApi.createReport(data);
                    setReports((prev) => [report, ...prev]);
                    showToast(`Report submitted — ${report.phone_number}`, true);
                    fetchAll();
                  } catch (err: any) {
                    showToast(err.response?.data?.detail || "Submit failed", false);
                  }
                }} />
              </Suspense>
            </div>
            <div className="bg-white/[0.02] border border-white/[0.05] rounded-xl overflow-hidden">
              <Suspense fallback={<div className="h-32 animate-pulse bg-white/[0.02]" />}>
                <AdLibraryPanel />
              </Suspense>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="bg-white/[0.02] border border-white/[0.05] rounded-xl overflow-hidden">
              <Suspense fallback={<div className="h-32 animate-pulse bg-white/[0.02]" />}>
                <GoogleAdsPanel />
              </Suspense>
            </div>
          </div>

          <div className="bg-white/[0.02] border border-white/[0.05] rounded-xl overflow-hidden">
            <div className="px-5 py-4 border-b border-white/[0.04] flex flex-col sm:flex-row items-start sm:items-center gap-3">
              <div className="flex-1 flex flex-col sm:flex-row items-start sm:items-center gap-3 w-full">
                <div className="relative w-full sm:max-w-xs">
                  <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#3d4251]" />
                  <input className="w-full h-9 bg-white/[0.03] border border-white/[0.06] rounded-lg pl-8 pr-3 text-xs text-white font-mono placeholder-[#3d4251] focus:outline-none focus:border-white/[0.15] focus:bg-white/[0.04] transition-all" placeholder="Search brand, number, URL..." value={search} onChange={(e) => setSearch(e.target.value)} />
                </div>
                <div className="flex items-center gap-1.5 flex-wrap">
                  {STATUS_FILTERS.map(({ value, label, color }) => (
                    <button key={value || "all"} onClick={() => setFilterStatus(value)} className={`h-7 px-3 rounded-md text-[11px] font-mono font-medium border transition-all ${filterStatus === value ? `bg-white/[0.06] border-white/[0.12] ${color}` : "border-transparent text-[#4b5563] hover:text-[#9ca3af] hover:border-white/[0.06]"}`}>
                      {label}
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className="hidden sm:block text-[11px] text-[#3d4251] font-mono">{total.toLocaleString()} records</span>
                <button onClick={() => reportsApi.exportCsv()} className="flex items-center gap-1.5 h-8 px-3 rounded-lg border border-white/[0.06] text-[#6b7280] hover:text-white hover:border-white/[0.12] text-xs font-medium transition-all">
                  <Download size={12} /> <span className="hidden sm:inline">CSV</span>
                </button>
                <button onClick={() => { setLoading(true); fetchAll(); }} className="h-8 px-3 flex items-center gap-1.5 rounded-lg border border-white/[0.06] text-[#6b7280] hover:text-white hover:border-white/[0.12] text-xs transition-all">
                  <RefreshCw size={12} className={loading ? "animate-spin" : ""} /> <span className="hidden sm:inline">Refresh</span>
                </button>
              </div>
            </div>

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
                <ReportsTable reports={reports} actionLoading={actionLoading} onReport={(id) => handleAction(id, "report")} onKill={(id) => handleAction(id, "kill")} onEmailReport={handleEmailReport} />
              </div>
            )}

            {total > PAGE_SIZE && (
              <div className="px-5 py-3.5 border-t border-white/[0.04] flex items-center justify-between gap-4">
                <span className="text-[11px] text-[#3d4251] font-mono">Showing <span className="text-[#6b7280]">{(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, total)}</span> of <span className="text-[#6b7280]">{total.toLocaleString()}</span></span>
                <div className="flex items-center gap-1.5">
                  <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1} className="w-8 h-8 flex items-center justify-center rounded-lg border border-white/[0.06] text-[#6b7280] hover:text-white hover:border-white/[0.12] disabled:opacity-25 disabled:cursor-not-allowed transition-all">
                    <ChevronLeft size={13} />
                  </button>
                  <div className="flex items-center gap-1">
                    {(() => {
                      let pages: number[] = [];
                      if (totalPages <= 5) pages = Array.from({ length: totalPages }, (_, i) => i + 1);
                      else if (page <= 3) pages = [1, 2, 3, 4, 5];
                      else if (page >= totalPages - 2) pages = [totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages];
                      else pages = [page - 2, page - 1, page, page + 1, page + 2];
                      return pages.map((p) => (
                        <button key={p} onClick={() => setPage(p)} className={`w-8 h-8 rounded-lg text-xs font-mono font-medium transition-all ${p === page ? "bg-white/[0.08] border border-white/[0.12] text-white" : "text-[#4b5563] hover:text-[#9ca3af] hover:bg-white/[0.03]"}`}>
                          {p}
                        </button>
                      ));
                    })()}
                  </div>
                  <button onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page >= totalPages} className="w-8 h-8 flex items-center justify-center rounded-lg border border-white/[0.06] text-[#6b7280] hover:text-white hover:border-white/[0.12] disabled:opacity-25 disabled:cursor-not-allowed transition-all">
                    <ChevronRight size={13} />
                  </button>
                </div>
              </div>
            )}
          </div>
          <div className="h-4" />
        </main>
      </div>
    </ErrorBoundary>
  );
};

export default Dashboard;