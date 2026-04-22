import React, { useState, useRef, useEffect } from "react";
import {
  ExternalLink,
  Send,
  Skull,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  XCircle,
  Clock,
  Shield,
  Mail,
  Plus,
  X,
} from "lucide-react";
import type { ScamReport } from "../types";
import Badge from "./ui/Badge";
import { reportsApi } from "../api/reports";

interface ReportsTableProps {
  reports: ScamReport[];
  actionLoading: string | null;
  onReport: (id: string) => void;
  onKill: (id: string) => void;
  onEmailReport: (id: string, payload: EmailPayload) => Promise<void>;
}

export interface EmailPayload {
  to: string;
  cc: string[];
  subject: string;
  body: string;
}

interface ReportLog {
  id: string;
  action: string;
  detail: string;
  success: boolean;
  created_at: string;
}

const ACTION_LABELS: Record<string, string> = {
  CREATED: "Report Created",
  RESPORG_LOOKUP: "Carrier Lookup",
  EMAIL_SENT: "Complaint Email Sent",
  email_sent: "Complaint Email Sent",
  STATUS_CHANGED: "Status Changed",
  FTC_SUBMISSION: "FTC Submission",
  IC3_SUBMISSION: "IC3 Submission",
  MICROSOFT_FRAUD_REPORT: "Microsoft Fraud Report",
  AMAZON_FRAUD_REPORT: "Amazon Fraud Report",
  GOOGLE_SAFEBROWSING: "Google Safe Browsing",
  AUTHORITY_SUBMISSIONS_INITIATED: "Authority Submissions",
};

// ─── Email Compose Modal ────────────────────────────────────────────────────

interface ComposeModalProps {
  report: ScamReport;
  onClose: () => void;
  onSend: (payload: EmailPayload) => Promise<void>;
}

const ComposeModal: React.FC<ComposeModalProps> = ({ report, onClose, onSend }) => {
  const carrierEmail =
    report.resporg?.abuse_email ||
    `abuse@${report.resporg?.carrier_name?.toLowerCase().replace(/\s+/g, "") || "carrier"}.com`;

  const [to, setTo] = useState(carrierEmail);
  const [ccFields, setCcFields] = useState<string[]>(["spam@uce.gov", "ic3@ic3.gov"]);
  const [subject, setSubject] = useState(
    `[URGENT] Toll-Free Number Abuse — ${report.phone_number}`
  );
  const [body, setBody] = useState(
    `Dear ${report.resporg?.carrier_name || "Carrier"} Trust & Safety Team,\n\n` +
    `We are reporting the following toll-free number for fraudulent activity impersonating ${report.brand}. ` +
    `We request immediate investigation and termination of service.\n\n` +
    `REPORTED NUMBER:    ${report.phone_number}\n` +
    `IMPERSONATED BRAND: ${report.brand}\n` +
    `RespOrg ID:         ${report.resporg_raw || "N/A"}\n` +
    `LANDING PAGE:       ${report.landing_url || "N/A"}\n` +
    `DATE DETECTED:      ${new Date().toISOString().slice(0, 16).replace("T", " ")} UTC\n\n` +
    `We request:\n` +
    `1. Immediate suspension of the number ${report.phone_number}\n` +
    `2. Preservation of all subscriber records for law enforcement\n` +
    `3. Confirmation of action\n\n` +
    `Sincerely,\nScam Slayer Portal\nAutomated Abuse Reporting System`
  );
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  const addCC = () => setCcFields((prev) => [...prev, ""]);
  const updateCC = (i: number, val: string) =>
    setCcFields((prev) => prev.map((v, idx) => (idx === i ? val : v)));
  const removeCC = (i: number) =>
    setCcFields((prev) => prev.filter((_, idx) => idx !== i));

  const handleSend = async () => {
    if (!to.trim()) { setError("Please enter a recipient email."); return; }
    setSending(true);
    setError("");
    try {
      await onSend({
        to: to.trim(),
        cc: ccFields.map((c) => c.trim()).filter(Boolean),
        subject: subject.trim(),
        body: body.trim(),
      });
      onClose();
    } catch (e: any) {
      setError(e?.message || "Failed to send. Please try again.");
    } finally {
      setSending(false);
    }
  };

  // Close on backdrop click
  const backdropRef = useRef<HTMLDivElement>(null);
  const handleBackdrop = (e: React.MouseEvent) => {
    if (e.target === backdropRef.current) onClose();
  };

  return (
    <div
      ref={backdropRef}
      onClick={handleBackdrop}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
    >
      <div className="bg-[#0f1117] border border-[#1e2130] rounded-xl w-full max-w-2xl mx-4 overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-[#1a1d2e]">
          <div className="flex items-center gap-2">
            <Mail size={14} className="text-blue-400" />
            <span className="text-sm font-medium text-white">Compose complaint email</span>
          </div>
          <button
            onClick={onClose}
            className="text-[#4b5563] hover:text-white transition-colors p-1 rounded"
          >
            <X size={14} />
          </button>
        </div>

        {/* Fields */}
        <div className="px-5 py-4 space-y-0 divide-y divide-[#1a1d2e]">
          {/* To */}
          <div className="flex items-center gap-4 py-2.5">
            <span className="text-xs text-[#4b5563] font-medium w-12 shrink-0">To</span>
            <input
              type="email"
              value={to}
              onChange={(e) => setTo(e.target.value)}
              placeholder="abuse@carrier.com"
              className="flex-1 bg-transparent text-sm text-white outline-none placeholder-[#374151]"
            />
          </div>

          {/* CC */}
          <div className="flex items-start gap-4 py-2.5">
            <span className="text-xs text-[#4b5563] font-medium w-12 shrink-0 pt-1.5">CC</span>
            <div className="flex-1 space-y-1.5">
              {ccFields.map((cc, i) => (
                <div key={i} className="flex items-center gap-2">
                  <input
                    type="email"
                    value={cc}
                    onChange={(e) => updateCC(i, e.target.value)}
                    placeholder="cc@example.com"
                    className="flex-1 bg-transparent text-sm text-white outline-none placeholder-[#374151]"
                  />
                  <button
                    onClick={() => removeCC(i)}
                    className="text-[#374151] hover:text-[#6b7280] transition-colors shrink-0"
                  >
                    <X size={12} />
                  </button>
                </div>
              ))}
              <button
                onClick={addCC}
                className="flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 transition-colors mt-1"
              >
                <Plus size={11} /> Add CC
              </button>
            </div>
          </div>

          {/* Subject */}
          <div className="flex items-center gap-4 py-2.5">
            <span className="text-xs text-[#4b5563] font-medium w-12 shrink-0">Subject</span>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="flex-1 bg-transparent text-sm text-white outline-none placeholder-[#374151]"
            />
          </div>

          {/* Body */}
          <div className="flex items-start gap-4 py-3">
            <span className="text-xs text-[#4b5563] font-medium w-12 shrink-0 pt-1">Body</span>
            <textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
              rows={12}
              className="flex-1 bg-transparent text-sm text-[#e2e8f0] font-mono outline-none resize-none leading-relaxed placeholder-[#374151]"
            />
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="mx-5 mb-3 text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
            {error}
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between px-5 py-3 border-t border-[#1a1d2e]">
          <span className="text-xs text-[#374151] font-mono">
            {ccFields.filter(Boolean).length} CC recipient{ccFields.filter(Boolean).length !== 1 ? "s" : ""}
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-3 py-1.5 rounded-lg border border-[#2a2d3a] text-xs text-[#6b7280] hover:text-white hover:border-[#3a3d4a] transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSend}
              disabled={sending}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-xs text-white font-medium transition-colors"
            >
              {sending ? (
                <RefreshCw size={11} className="animate-spin" />
              ) : (
                <Send size={11} />
              )}
              {sending ? "Sending…" : "Send complaint"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// ─── Report Action Dropdown ─────────────────────────────────────────────────

interface ReportDropdownProps {
  reportId: string;
  isActing: boolean;
  onAuthorities: () => void;
  onEmail: () => void;
}

const ReportDropdown: React.FC<ReportDropdownProps> = ({
  reportId,
  isActing,
  onAuthorities,
  onEmail,
}) => {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  return (
    <div ref={ref} className="relative">
      <div className="flex items-center rounded-lg overflow-hidden border border-blue-500/20 bg-blue-500/10">
        <button
          onClick={onAuthorities}
          disabled={isActing}
          className="flex items-center gap-1.5 px-2.5 py-1.5 text-blue-400 hover:bg-blue-500/20 disabled:opacity-50 transition-colors text-xs font-medium"
        >
          {isActing ? (
            <RefreshCw size={11} className="animate-spin" />
          ) : (
            <Send size={11} />
          )}
          Report
        </button>
        <button
          onClick={() => setOpen((o) => !o)}
          disabled={isActing}
          className="px-1.5 py-1.5 text-blue-400 hover:bg-blue-500/20 disabled:opacity-50 transition-colors border-l border-blue-500/20"
        >
          <ChevronDown size={11} />
        </button>
      </div>

      {open && (
        <div className="absolute top-full mt-1 left-0 z-40 bg-[#0f1117] border border-[#1e2130] rounded-xl overflow-hidden shadow-xl min-w-[210px]">
          <button
            onClick={() => { setOpen(false); onAuthorities(); }}
            className="w-full flex items-start gap-3 px-3.5 py-2.5 hover:bg-[#111420] transition-colors text-left"
          >
            <Shield size={13} className="text-blue-400 mt-0.5 shrink-0" />
            <div>
              <div className="text-xs font-medium text-white">Submit to authorities</div>
              <div className="text-[11px] text-[#4b5563] mt-0.5">FTC, IC3, brand abuse teams</div>
            </div>
          </button>
          <div className="h-px bg-[#1a1d2e] mx-2" />
          <button
            onClick={() => { setOpen(false); onEmail(); }}
            className="w-full flex items-start gap-3 px-3.5 py-2.5 hover:bg-[#111420] transition-colors text-left"
          >
            <Mail size={13} className="text-blue-400 mt-0.5 shrink-0" />
            <div>
              <div className="text-xs font-medium text-white">Send via email</div>
              <div className="text-[11px] text-[#4b5563] mt-0.5">Compose carrier complaint email</div>
            </div>
          </button>
        </div>
      )}
    </div>
  );
};

// ─── Main Table ─────────────────────────────────────────────────────────────

const ReportsTable: React.FC<ReportsTableProps> = ({
  reports,
  actionLoading,
  onReport,
  onKill,
  onEmailReport,
}) => {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [logs, setLogs] = useState<Record<string, ReportLog[]>>({});
  const [logsLoading, setLogsLoading] = useState<string | null>(null);
  const [composeFor, setComposeFor] = useState<ScamReport | null>(null);

  const toggleLogs = async (reportId: string) => {
    if (expandedId === reportId) { setExpandedId(null); return; }
    setExpandedId(reportId);
    setLogsLoading(reportId);
    try {
      const report = await reportsApi.getReport(reportId);
      setLogs((prev) => ({ ...prev, [reportId]: report.logs || [] }));
    } catch {
      setLogs((prev) => ({ ...prev, [reportId]: [] }));
    } finally {
      setLogsLoading(null);
    }
  };

  const refreshLogs = async (reportId: string) => {
    setLogsLoading(reportId);
    try {
      const report = await reportsApi.getReport(reportId);
      setLogs((prev) => ({ ...prev, [reportId]: report.logs || [] }));
    } catch {
    } finally {
      setLogsLoading(null);
    }
  };

  return (
    <>
      {composeFor && (
        <ComposeModal
          report={composeFor}
          onClose={() => setComposeFor(null)}
          onSend={(payload) => onEmailReport(composeFor.id, payload)}
        />
      )}

      <div className="bg-[#0f1117] border border-[#1e2130] rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#1a1d2e]">
                {[
                  "Target Brand",
                  "Toll-Free Number",
                  "RespOrg",
                  "Carrier",
                  "Landing Page",
                  "Status",
                  "Detected",
                  "Actions",
                  "Logs",
                ].map((h) => (
                  <th
                    key={h}
                    className="px-5 py-3.5 text-left text-xs font-medium text-[#4b5563] uppercase tracking-wider whitespace-nowrap"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {reports.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-5 py-16 text-center">
                    <span className="text-[#4b5563] text-sm">No reports found</span>
                  </td>
                </tr>
              ) : (
                reports.map((r) => {
                  const isActing = actionLoading?.startsWith(r.id) ?? false;
                  const isExpanded = expandedId === r.id;
                  const reportLogs = logs[r.id] || [];

                  return (
                    <React.Fragment key={r.id}>
                      <tr className="border-b border-[#1a1d2e] hover:bg-[#111420] transition-colors">
                        <td className="px-5 py-4">
                          <div className="flex items-center gap-2">
                            <div className="w-6 h-6 rounded bg-[#1a1d2e] flex items-center justify-center text-[10px] font-bold text-[#6b7280]">
                              {r.brand.charAt(0).toUpperCase()}
                            </div>
                            <span className="font-medium text-white text-sm">{r.brand}</span>
                          </div>
                        </td>
                        <td className="px-5 py-4">
                          <span className="font-mono text-[#e2e8f0] text-sm tracking-wide">
                            {r.phone_number}
                          </span>
                        </td>
                        <td className="px-5 py-4">
                          <span className="font-mono text-xs text-[#6b7280] bg-[#1a1d2e] px-2 py-1 rounded">
                            {r.resporg_raw || "—"}
                          </span>
                        </td>
                        <td className="px-5 py-4">
                          <span className="text-[#9ca3af] text-xs">
                            {r.resporg?.carrier_name || "Unknown"}
                          </span>
                        </td>
                        <td className="px-5 py-4">
                          {r.landing_url ? (
                            <a
                              href={r.landing_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 text-xs text-[#3b82f6] hover:text-blue-300 font-mono transition-colors"
                            >
                              <ExternalLink size={10} />
                              {r.landing_url.replace(/^https?:\/\//, "").slice(0, 28)}
                              {r.landing_url.length > 36 ? "…" : ""}
                            </a>
                          ) : (
                            <span className="text-[#374151] text-xs">—</span>
                          )}
                        </td>
                        <td className="px-5 py-4">
                          <Badge status={r.status} />
                        </td>
                        <td className="px-5 py-4">
                          <div className="text-xs text-[#6b7280] font-mono">
                            {new Date(r.created_at).toLocaleDateString("en-US", {
                              month: "short",
                              day: "numeric",
                            })}
                            <br />
                            <span className="text-[#374151]">
                              {new Date(r.created_at).toLocaleTimeString("en-US", {
                                hour: "2-digit",
                                minute: "2-digit",
                              })}
                            </span>
                          </div>
                        </td>
                        <td className="px-5 py-4">
                          <div className="flex items-center gap-2">
                            {r.status !== "killed" && r.status !== "reported" && (
                              <ReportDropdown
                                reportId={r.id}
                                isActing={isActing}
                                onAuthorities={() => onReport(r.id)}
                                onEmail={() => setComposeFor(r)}
                              />
                            )}
                            {r.status !== "killed" && (
                              <button
                                onClick={() => onKill(r.id)}
                                disabled={isActing}
                                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/20 disabled:opacity-50 transition-colors text-xs font-medium"
                              >
                                {isActing && actionLoading === `${r.id}-kill` ? (
                                  <RefreshCw size={11} className="animate-spin" />
                                ) : (
                                  <Skull size={11} />
                                )}
                                Kill
                              </button>
                            )}
                            {r.status === "killed" && (
                              <span className="text-xs text-[#374151] font-mono">Terminated</span>
                            )}
                          </div>
                        </td>
                        <td className="px-5 py-4">
                          <button
                            onClick={() => toggleLogs(r.id)}
                            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-[#1a1d2e] border border-[#2a2d3a] text-[#6b7280] hover:text-white hover:border-[#3a3d4a] transition-colors text-xs font-medium"
                          >
                            {logsLoading === r.id ? (
                              <RefreshCw size={11} className="animate-spin" />
                            ) : isExpanded ? (
                              <ChevronUp size={11} />
                            ) : (
                              <ChevronDown size={11} />
                            )}
                            Logs
                          </button>
                        </td>
                      </tr>

                      {isExpanded && (
                        <tr className="border-b border-[#1a1d2e] bg-[#0a0b10]">
                          <td colSpan={9} className="px-5 py-4">
                            <div className="flex items-center justify-between mb-3">
                              <span className="text-xs text-[#4b5563] font-mono uppercase tracking-wider">
                                Activity Log
                              </span>
                              <button
                                onClick={() => refreshLogs(r.id)}
                                className="flex items-center gap-1 text-xs text-[#4b5563] hover:text-white transition-colors"
                              >
                                <RefreshCw
                                  size={10}
                                  className={logsLoading === r.id ? "animate-spin" : ""}
                                />
                                Refresh
                              </button>
                            </div>
                            {logsLoading === r.id ? (
                              <div className="flex items-center gap-2 text-xs text-[#4b5563]">
                                <RefreshCw size={11} className="animate-spin" />
                                Loading logs...
                              </div>
                            ) : reportLogs.length === 0 ? (
                              <p className="text-xs text-[#4b5563] font-mono">No logs yet.</p>
                            ) : (
                              <div className="space-y-2">
                                {reportLogs.map((log) => (
                                  <div
                                    key={log.id}
                                    className="flex items-start gap-3 text-xs font-mono"
                                  >
                                    {log.success ? (
                                      <CheckCircle2 size={13} className="text-emerald-400 shrink-0 mt-0.5" />
                                    ) : (
                                      <XCircle size={13} className="text-red-400 shrink-0 mt-0.5" />
                                    )}
                                    <div className="flex-1 min-w-0">
                                      <span className="text-white font-medium">
                                        {ACTION_LABELS[log.action] || log.action}
                                      </span>
                                      <span className="text-[#4b5563] mx-2">—</span>
                                      <span className="text-[#9ca3af] break-all">{log.detail}</span>
                                    </div>
                                    <div className="flex items-center gap-1 text-[#374151] shrink-0">
                                      <Clock size={10} />
                                      {new Date(log.created_at).toLocaleTimeString("en-US", {
                                        hour: "2-digit",
                                        minute: "2-digit",
                                      })}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            )}
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
};

export default ReportsTable;