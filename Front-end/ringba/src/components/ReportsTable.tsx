import React, { useState, useRef, useEffect } from "react";
import {
  ExternalLink, Send, Skull, RefreshCw, ChevronDown, ChevronUp,
  CheckCircle2, XCircle, Clock, Shield, Mail, Plus, X, Paperclip,
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

export interface EmailAttachment {
  name: string;
  type: string;
  data: string;
}

export interface EmailPayload {
  to: string;
  cc: string[];
  bcc: string[];
  subject: string;
  body: string;
  attachments: EmailAttachment[];
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

const CARRIER_ABUSE_EMAILS: Record<string, string> = {
  somosgov: "abuse@somos.com",
  somos: "abuse@somos.com",
  "at&t": "abuse@att.net",
  att: "abuse@att.net",
  verizon: "abuse@verizon.com",
  "t-mobile": "abuse@t-mobile.com",
  tmobile: "abuse@t-mobile.com",
  lumen: "abuse@lumen.com",
  bandwidth: "abuse@bandwidth.com",
  twilio: "abuse@twilio.com",
  vonage: "abuse@vonage.com",
  google: "abuse@google.com",
  telnyx: "abuse@telnyx.com",
  fractel: "abuse@fractel.net",
  cxsupport: "abuse@cxsupport.com",
};

function resolveCarrierEmail(report: ScamReport): string {
  if (report.resporg?.abuse_email) return report.resporg.abuse_email;
  const name = (report.resporg?.carrier_name || report.resporg_raw || "").toLowerCase();
  for (const [key, email] of Object.entries(CARRIER_ABUSE_EMAILS)) {
    if (name.includes(key)) return email;
  }
  return "";
}

// ─── Compose Modal ───────────────────────────────────────────────────────────

interface ComposeModalProps {
  report: ScamReport;
  onClose: () => void;
  onSend: (payload: EmailPayload) => Promise<void>;
}

const ComposeModal: React.FC<ComposeModalProps> = ({ report, onClose, onSend }) => {
  const carrierEmail = resolveCarrierEmail(report);

  const [to, setTo] = useState(carrierEmail);
  const [ccFields, setCcFields] = useState<string[]>(["ic3@ic3.gov", "spam@uce.gov"]);
  const [bccFields, setBccFields] = useState<string[]>([""]);
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [attachments, setAttachments] = useState<EmailAttachment[]>([]);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const addCC = () => setCcFields((prev) => [...prev, ""]);
  const updateCC = (i: number, val: string) =>
    setCcFields((prev) => prev.map((v, idx) => (idx === i ? val : v)));
  const removeCC = (i: number) =>
    setCcFields((prev) => prev.filter((_, idx) => idx !== i));

  const addBCC = () => setBccFields((prev) => [...prev, ""]);
  const updateBCC = (i: number, val: string) =>
    setBccFields((prev) => prev.map((v, idx) => (idx === i ? val : v)));
  const removeBCC = (i: number) =>
    setBccFields((prev) => prev.filter((_, idx) => idx !== i));

  const handleFiles = (files: FileList | null) => {
    if (!files) return;
    Array.from(files).forEach((file) => {
      if (!file.type.startsWith("image/")) return;
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        const base64 = result.split(",")[1];
        setAttachments((prev) => [...prev, { name: file.name, type: file.type, data: base64 }]);
      };
      reader.readAsDataURL(file);
    });
  };

  const removeAttachment = (i: number) =>
    setAttachments((prev) => prev.filter((_, idx) => idx !== i));

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    handleFiles(e.dataTransfer.files);
  };

  const handleSend = async () => {
    if (!to.trim()) { setError("To address is required."); return; }
    if (!subject.trim()) { setError("Subject is required."); return; }
    if (!body.trim()) { setError("Body is required."); return; }
    setSending(true);
    setError("");
    try {
      await onSend({
        to: to.trim(),
        cc: ccFields.map((c) => c.trim()).filter(Boolean),
        bcc: bccFields.map((b) => b.trim()).filter(Boolean),
        subject: subject.trim(),
        body: body.trim(),
        attachments,
      });
      onClose();
    } catch (e: any) {
      setError(e?.message || "Failed to send. Please try again.");
    } finally {
      setSending(false);
    }
  };

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
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-[#1a1d2e]">
          <div className="flex items-center gap-2">
            <Mail size={14} className="text-blue-400" />
            <span className="text-sm font-medium text-white">New complaint email</span>
            <span className="text-xs text-[#4b5563] font-mono ml-1">— {report.phone_number}</span>
          </div>
          <button onClick={onClose} className="text-[#4b5563] hover:text-white transition-colors p-1 rounded">
            <X size={14} />
          </button>
        </div>

        <div className="divide-y divide-[#1a1d2e]">
          <div className="flex items-center gap-4 px-5 py-3">
            <span className="text-xs text-[#4b5563] font-medium w-12 shrink-0">To</span>
            <input
              type="email"
              value={to}
              onChange={(e) => setTo(e.target.value)}
              placeholder="abuse@carrier.com"
              autoFocus
              className="flex-1 bg-transparent text-sm text-white outline-none placeholder-[#374151]"
            />
          </div>

          <div className="px-5 py-3">
            <div className="flex items-start gap-4">
              <span className="text-xs text-[#4b5563] font-medium w-12 shrink-0 pt-1.5">CC</span>
              <div className="flex-1 space-y-2">
                {ccFields.map((cc, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <input
                      type="email"
                      value={cc}
                      onChange={(e) => updateCC(i, e.target.value)}
                      placeholder="cc@example.com"
                      className="flex-1 bg-transparent text-sm text-white outline-none placeholder-[#374151]"
                    />
                    <button onClick={() => removeCC(i)} className="text-[#374151] hover:text-red-400 transition-colors shrink-0">
                      <X size={12} />
                    </button>
                  </div>
                ))}
                <button onClick={addCC} className="flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 transition-colors">
                  <Plus size={11} /> Add CC
                </button>
              </div>
            </div>
          </div>

          <div className="px-5 py-3">
            <div className="flex items-start gap-4">
              <span className="text-xs text-[#4b5563] font-medium w-12 shrink-0 pt-1.5">BCC</span>
              <div className="flex-1 space-y-2">
                {bccFields.map((bcc, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <input
                      type="email"
                      value={bcc}
                      onChange={(e) => updateBCC(i, e.target.value)}
                      placeholder="bcc@example.com"
                      className="flex-1 bg-transparent text-sm text-white outline-none placeholder-[#374151]"
                    />
                    <button onClick={() => removeBCC(i)} className="text-[#374151] hover:text-red-400 transition-colors shrink-0">
                      <X size={12} />
                    </button>
                  </div>
                ))}
                <button onClick={addBCC} className="flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 transition-colors">
                  <Plus size={11} /> Add BCC
                </button>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4 px-5 py-3">
            <span className="text-xs text-[#4b5563] font-medium w-12 shrink-0">Subject</span>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="Subject"
              className="flex-1 bg-transparent text-sm text-white outline-none placeholder-[#374151]"
            />
          </div>

          <div className="flex items-start gap-4 px-5 py-3">
            <span className="text-xs text-[#4b5563] font-medium w-12 shrink-0 pt-2">Body</span>
            <textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
              rows={13}
              placeholder="Write your complaint here..."
              className="flex-1 bg-transparent text-sm text-[#e2e8f0] outline-none resize-none leading-relaxed placeholder-[#374151]"
            />
          </div>

          <div className="px-5 py-3">
            <div className="flex items-start gap-4">
              <span className="text-xs text-[#4b5563] font-medium w-12 shrink-0 pt-1">Images</span>
              <div className="flex-1 space-y-2">
                {attachments.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-2">
                    {attachments.map((att, i) => (
                      <div key={i} className="relative group">
                        <img
                          src={`data:${att.type};base64,${att.data}`}
                          alt={att.name}
                          className="w-16 h-16 object-cover rounded-lg border border-[#2a2d3a]"
                        />
                        <button
                          onClick={() => removeAttachment(i)}
                          className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full bg-red-500 text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <X size={9} />
                        </button>
                        <span className="absolute bottom-0 left-0 right-0 text-[9px] text-white bg-black/60 rounded-b-lg px-1 py-0.5 truncate">
                          {att.name}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
                <div
                  onDrop={handleDrop}
                  onDragOver={(e) => e.preventDefault()}
                  onClick={() => fileInputRef.current?.click()}
                  className="flex items-center gap-2 px-3 py-2 rounded-lg border border-dashed border-[#2a2d3a] hover:border-blue-500/40 hover:bg-blue-500/5 transition-colors cursor-pointer"
                >
                  <Paperclip size={12} className="text-[#4b5563]" />
                  <span className="text-xs text-[#4b5563]">
                    {attachments.length > 0
                      ? `${attachments.length} image${attachments.length !== 1 ? "s" : ""} attached — click or drop to add more`
                      : "Click or drop images here"}
                  </span>
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  multiple
                  className="hidden"
                  onChange={(e) => handleFiles(e.target.files)}
                />
              </div>
            </div>
          </div>
        </div>

        {error && (
          <div className="mx-5 mb-3 text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
            {error}
          </div>
        )}

        <div className="flex items-center justify-between px-5 py-3 border-t border-[#1a1d2e]">
          <span className="text-xs text-[#374151] font-mono">
            {ccFields.filter(Boolean).length} CC{ccFields.filter(Boolean).length !== 1 ? "s" : ""}
            {bccFields.filter(Boolean).length > 0 && ` · ${bccFields.filter(Boolean).length} BCC`}
            {attachments.length > 0 && ` · ${attachments.length} image${attachments.length !== 1 ? "s" : ""}`}
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
              {sending ? <RefreshCw size={11} className="animate-spin" /> : <Send size={11} />}
              {sending ? "Sending…" : "Send"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// ─── Report Dropdown ─────────────────────────────────────────────────────────

interface ReportDropdownProps {
  isActing: boolean;
  authoritiesSubmitted: boolean;
  emailSent: boolean;
  onAuthorities: () => void;
  onEmail: () => void;
}

const ReportDropdown: React.FC<ReportDropdownProps> = ({
  isActing,
  authoritiesSubmitted,
  emailSent,
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

  // If both actions are done, show nothing
  if (authoritiesSubmitted && emailSent) return null;

  return (
    <div ref={ref} className="relative">
      <div className="flex items-center rounded-lg overflow-hidden border border-blue-500/20 bg-blue-500/10">
        {!authoritiesSubmitted && (
          <button
            onClick={onAuthorities}
            disabled={isActing}
            className="flex items-center gap-1.5 px-2.5 py-1.5 text-blue-400 hover:bg-blue-500/20 disabled:opacity-50 transition-colors text-xs font-medium"
          >
            {isActing ? <RefreshCw size={11} className="animate-spin" /> : <Send size={11} />}
            Report
          </button>
        )}
        {/* Only show dropdown arrow if there's more than one option */}
        {(!authoritiesSubmitted || !emailSent) && (
          <button
            onClick={() => setOpen((o) => !o)}
            disabled={isActing}
            className={`px-1.5 py-1.5 text-blue-400 hover:bg-blue-500/20 disabled:opacity-50 transition-colors ${!authoritiesSubmitted ? "border-l border-blue-500/20" : ""}`}
          >
            <ChevronDown size={11} />
          </button>
        )}
      </div>

      {open && (
        <div className="absolute top-full mt-1 left-0 z-40 bg-[#0f1117] border border-[#1e2130] rounded-xl overflow-hidden shadow-xl min-w-[210px]">
          {!authoritiesSubmitted && (
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
          )}

          {!authoritiesSubmitted && !emailSent && <div className="h-px bg-[#1a1d2e] mx-2" />}

          {!emailSent && (
            <button
              onClick={() => { setOpen(false); onEmail(); }}
              className="w-full flex items-start gap-3 px-3.5 py-2.5 hover:bg-[#111420] transition-colors text-left"
            >
              <Mail size={13} className="text-blue-400 mt-0.5 shrink-0" />
              <div>
                <div className="text-xs font-medium text-white">Send via email</div>
                <div className="text-[11px] text-[#4b5563] mt-0.5">Compose & send manually</div>
              </div>
            </button>
          )}
        </div>
      )}
    </div>
  );
};

// ─── Main Table ──────────────────────────────────────────────────────────────

const ReportsTable: React.FC<ReportsTableProps> = ({
  reports, actionLoading, onReport, onKill, onEmailReport,
}) => {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [logs, setLogs] = useState<Record<string, ReportLog[]>>({});
  const [logsLoading, setLogsLoading] = useState<string | null>(null);
  const [composeFor, setComposeFor] = useState<ScamReport | null>(null);
  // Track which reports have had authorities submitted or email sent this session
  const [authoritiesDone, setAuthoritiesDone] = useState<Set<string>>(new Set());
  const [emailDone, setEmailDone] = useState<Set<string>>(new Set());

  const toggleLogs = async (reportId: string) => {
    if (expandedId === reportId) { setExpandedId(null); return; }
    setExpandedId(reportId);
    setLogsLoading(reportId);
    try {
      const report = await reportsApi.getReport(reportId);
      const fetchedLogs =(report as any).logs || [];
      setLogs((prev) => ({ ...prev, [reportId]: fetchedLogs }));

      // Check logs to set done states from history
      const hasAuthorities = fetchedLogs.some((l: ReportLog) =>
        l.action === "AUTHORITY_SUBMISSIONS_INITIATED" && l.success
      );
      const hasEmail = fetchedLogs.some((l: ReportLog) =>
        (l.action === "EMAIL_SENT" || l.action === "email_sent") && l.success
      );
      if (hasAuthorities) setAuthoritiesDone((prev) => new Set(prev).add(reportId));
      if (hasEmail) setEmailDone((prev) => new Set(prev).add(reportId));
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
      const fetchedLogs = (report as any).logs || [];
      setLogs((prev) => ({ ...prev, [reportId]: fetchedLogs }));

      const hasAuthorities = fetchedLogs.some((l: ReportLog) =>
        l.action === "AUTHORITY_SUBMISSIONS_INITIATED" && l.success
      );
      const hasEmail = fetchedLogs.some((l: ReportLog) =>
        (l.action === "EMAIL_SENT" || l.action === "email_sent") && l.success
      );
      if (hasAuthorities) setAuthoritiesDone((prev) => new Set(prev).add(reportId));
      if (hasEmail) setEmailDone((prev) => new Set(prev).add(reportId));
    } catch {
    } finally {
      setLogsLoading(null);
    }
  };

  const handleAuthorities = (id: string) => {
    setAuthoritiesDone((prev) => new Set(prev).add(id));
    onReport(id);
  };

  const handleEmailSent = async (id: string, payload: EmailPayload) => {
    await onEmailReport(id, payload);
    setEmailDone((prev) => new Set(prev).add(id));
  };

  return (
    <>
      {composeFor && (
        <ComposeModal
          report={composeFor}
          onClose={() => setComposeFor(null)}
          onSend={(payload) => handleEmailSent(composeFor.id, payload)}
        />
      )}

      <div className="bg-[#0f1117] border border-[#1e2130] rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#1a1d2e]">
                {["Target Brand", "Toll-Free Number", "RespOrg", "Carrier", "Landing Page", "Status", "Detected", "Actions", "Logs"].map((h) => (
                  <th key={h} className="px-5 py-3.5 text-left text-xs font-medium text-[#4b5563] uppercase tracking-wider whitespace-nowrap">{h}</th>
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
                  const authoritiesSubmitted = authoritiesDone.has(r.id);
                  const emailSent = emailDone.has(r.id);

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
                          <span className="font-mono text-[#e2e8f0] text-sm tracking-wide">{r.phone_number}</span>
                        </td>
                        <td className="px-5 py-4">
                          <span className="font-mono text-xs text-[#6b7280] bg-[#1a1d2e] px-2 py-1 rounded">{r.resporg_raw || "—"}</span>
                        </td>
                        <td className="px-5 py-4">
                          {/* Use resporg_raw directly — it stores the carrier name from IPQS */}
                          <span className="text-[#9ca3af] text-xs">{r.resporg_raw || "Unknown"}</span>
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
                        <td className="px-5 py-4"><Badge status={r.status} /></td>
                        <td className="px-5 py-4">
                          <div className="text-xs text-[#6b7280] font-mono">
                            {new Date(r.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                            <br />
                            <span className="text-[#374151]">
                              {new Date(r.created_at).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" })}
                            </span>
                          </div>
                        </td>
                        <td className="px-5 py-4">
                          <div className="flex items-center gap-2">
                            {r.status !== "killed" && (
                              <ReportDropdown
                                isActing={isActing}
                                authoritiesSubmitted={authoritiesSubmitted}
                                emailSent={emailSent}
                                onAuthorities={() => handleAuthorities(r.id)}
                                onEmail={() => setComposeFor(r)}
                              />
                            )}
                            {r.status !== "killed" && (
                              <button
                                onClick={() => onKill(r.id)}
                                disabled={isActing}
                                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/20 disabled:opacity-50 transition-colors text-xs font-medium"
                              >
                                {isActing && actionLoading === `${r.id}-kill`
                                  ? <RefreshCw size={11} className="animate-spin" />
                                  : <Skull size={11} />}
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
                            {logsLoading === r.id
                              ? <RefreshCw size={11} className="animate-spin" />
                              : isExpanded ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
                            Logs
                          </button>
                        </td>
                      </tr>

                      {isExpanded && (
                        <tr className="border-b border-[#1a1d2e] bg-[#0a0b10]">
                          <td colSpan={9} className="px-5 py-4">
                            <div className="flex items-center justify-between mb-3">
                              <span className="text-xs text-[#4b5563] font-mono uppercase tracking-wider">Activity Log</span>
                              <button onClick={() => refreshLogs(r.id)} className="flex items-center gap-1 text-xs text-[#4b5563] hover:text-white transition-colors">
                                <RefreshCw size={10} className={logsLoading === r.id ? "animate-spin" : ""} />
                                Refresh
                              </button>
                            </div>
                            {logsLoading === r.id ? (
                              <div className="flex items-center gap-2 text-xs text-[#4b5563]">
                                <RefreshCw size={11} className="animate-spin" /> Loading logs...
                              </div>
                            ) : reportLogs.length === 0 ? (
                              <p className="text-xs text-[#4b5563] font-mono">No logs yet.</p>
                            ) : (
                              <div className="space-y-2">
                                {reportLogs.map((log) => (
                                  <div key={log.id} className="flex items-start gap-3 text-xs font-mono">
                                    {log.success
                                      ? <CheckCircle2 size={13} className="text-emerald-400 shrink-0 mt-0.5" />
                                      : <XCircle size={13} className="text-red-400 shrink-0 mt-0.5" />}
                                    <div className="flex-1 min-w-0">
                                      <span className="text-white font-medium">{ACTION_LABELS[log.action] || log.action}</span>
                                      <span className="text-[#4b5563] mx-2">—</span>
                                      <span className="text-[#9ca3af] break-all">{log.detail}</span>
                                    </div>
                                    <div className="flex items-center gap-1 text-[#374151] shrink-0">
                                      <Clock size={10} />
                                      {new Date(log.created_at).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" })}
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