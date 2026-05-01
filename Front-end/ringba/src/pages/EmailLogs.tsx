import React, { useState, useEffect } from "react";
import { Mail, CheckCircle, XCircle, Eye, RefreshCw, Search, X, ArrowLeft, Inbox } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { reportsApi } from "../api/reports";

interface SentEmail {
  id: string;
  email_type: string;
  recipient: string;
  cc_recipients: string;
  subject: string;
  body_preview: string;
  status: string;
  error_message: string;
  sent_at: string;
}

const EmailLogs: React.FC = () => {
  const navigate = useNavigate();
  const [emails, setEmails] = useState<SentEmail[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedEmail, setSelectedEmail] = useState<SentEmail | null>(null);

  const fetchEmails = async () => {
    setLoading(true);
    try {
      const data = await reportsApi.getAllEmails();
      setEmails(data);
    } catch (err) {
      console.error("Failed to fetch emails:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmails();
  }, []);

  const filteredEmails = emails.filter(email => 
    email.recipient.toLowerCase().includes(search.toLowerCase()) ||
    email.subject.toLowerCase().includes(search.toLowerCase())
  );

  const getStatusIcon = (status: string) => {
    if (status === "sent") {
      return <CheckCircle size={14} className="text-emerald-400" />;
    }
    return <XCircle size={14} className="text-red-400" />;
  };

  return (
    <div className="min-h-screen bg-[#08090d] text-white">
      <div className="max-w-[1680px] mx-auto px-5 sm:px-8 py-8">
        {/* Header with back button */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate("/dashboard")}
              className="w-9 h-9 flex items-center justify-center rounded-lg border border-white/[0.06] text-[#6b7280] hover:text-white hover:border-white/[0.12] hover:bg-white/[0.03] transition-all"
              title="Back to Dashboard"
            >
              <ArrowLeft size={14} />
            </button>
            <div>
              <h1 className="text-xl font-bold text-white tracking-tight">Email Logs</h1>
              <p className="text-xs text-[#4b5563] mt-0.5 font-mono">All sent abuse emails</p>
            </div>
          </div>
          <button
            onClick={fetchEmails}
            className="w-9 h-9 flex items-center justify-center rounded-lg border border-white/[0.06] text-[#6b7280] hover:text-white hover:border-white/[0.12] transition-all"
            title="Refresh"
          >
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          </button>
        </div>

        {/* Stats Summary */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
          <div className="bg-white/[0.02] border border-white/[0.05] rounded-xl p-3">
            <p className="text-[10px] text-[#4b5563] font-mono uppercase tracking-wider">Total Sent</p>
            <p className="text-xl font-bold text-white mt-1">{emails.length}</p>
          </div>
          <div className="bg-white/[0.02] border border-white/[0.05] rounded-xl p-3">
            <p className="text-[10px] text-[#4b5563] font-mono uppercase tracking-wider">Successful</p>
            <p className="text-xl font-bold text-emerald-400 mt-1">{emails.filter(e => e.status === "sent").length}</p>
          </div>
          <div className="bg-white/[0.02] border border-white/[0.05] rounded-xl p-3">
            <p className="text-[10px] text-[#4b5563] font-mono uppercase tracking-wider">Failed</p>
            <p className="text-xl font-bold text-red-400 mt-1">{emails.filter(e => e.status === "failed").length}</p>
          </div>
        </div>

        {/* Search */}
        <div className="relative max-w-xs mb-6">
          <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#3d4251]" />
          <input
            className="w-full h-9 bg-white/[0.03] border border-white/[0.06] rounded-lg pl-8 pr-3 text-xs text-white font-mono placeholder-[#3d4251] focus:outline-none focus:border-white/[0.15]"
            placeholder="Search by recipient or subject..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {/* Email List */}
        <div className="bg-white/[0.02] border border-white/[0.05] rounded-xl overflow-hidden">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-24 gap-3">
              <RefreshCw size={20} className="animate-spin text-[#3d4251]" />
              <span className="text-xs text-[#3d4251] font-mono">Loading emails...</span>
            </div>
          ) : filteredEmails.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-24 gap-3">
              <Inbox size={32} className="text-[#3d4251]" />
              <p className="text-sm text-[#4b5563]">No emails found</p>
              <p className="text-xs text-[#3d4251] font-mono">Try a different search or refresh</p>
            </div>
          ) : (
            <div className="divide-y divide-white/[0.04]">
              {filteredEmails.map((email) => (
                <div 
                  key={email.id} 
                  className="p-4 hover:bg-white/[0.02] transition-all cursor-pointer" 
                  onClick={() => setSelectedEmail(email)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      {getStatusIcon(email.status)}
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-white truncate">{email.subject}</p>
                        <div className="flex items-center gap-3 mt-1 flex-wrap">
                          <p className="text-xs text-[#4b5563] font-mono truncate">
                            To: {email.recipient}
                          </p>
                          {email.cc_recipients && (
                            <p className="text-xs text-[#3d4251] font-mono truncate">
                              CC: {email.cc_recipients}
                            </p>
                          )}
                        </div>
                        <p className="text-[11px] text-[#3d4251] font-mono mt-1">
                          {new Date(email.sent_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={(e) => { e.stopPropagation(); setSelectedEmail(email); }}
                      className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/[0.04] transition-all"
                    >
                      <Eye size={14} className="text-[#4b5563]" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Email Detail Modal */}
        {selectedEmail && (
          <div 
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm" 
            onClick={() => setSelectedEmail(null)}
          >
            <div 
              className="bg-[#0b0c12] border border-white/[0.08] rounded-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-hidden" 
              onClick={(e) => e.stopPropagation()}
            >
              <div className="px-5 py-4 border-b border-white/[0.06] flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Mail size={14} className="text-[#4b5563]" />
                  <span className="text-sm font-medium text-white">Email Details</span>
                </div>
                <button 
                  onClick={() => setSelectedEmail(null)} 
                  className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-white/[0.04]"
                >
                  <X size={14} className="text-[#4b5563]" />
                </button>
              </div>
              <div className="p-5 space-y-4 overflow-y-auto max-h-[calc(80vh-80px)]">
                <div>
                  <p className="text-[10px] text-[#3d4251] font-mono uppercase tracking-wider mb-1">Status</p>
                  <div className="flex items-center gap-2">
                    {getStatusIcon(selectedEmail.status)}
                    <span className={`text-sm ${selectedEmail.status === "sent" ? "text-emerald-400" : "text-red-400"}`}>
                      {selectedEmail.status.toUpperCase()}
                    </span>
                  </div>
                </div>
                <div>
                  <p className="text-[10px] text-[#3d4251] font-mono uppercase tracking-wider mb-1">To</p>
                  <p className="text-sm text-[#6b7280] break-all">{selectedEmail.recipient}</p>
                </div>
                {selectedEmail.cc_recipients && (
                  <div>
                    <p className="text-[10px] text-[#3d4251] font-mono uppercase tracking-wider mb-1">CC</p>
                    <p className="text-sm text-[#6b7280] break-all">{selectedEmail.cc_recipients}</p>
                  </div>
                )}
                <div>
                  <p className="text-[10px] text-[#3d4251] font-mono uppercase tracking-wider mb-1">Subject</p>
                  <p className="text-sm text-white">{selectedEmail.subject}</p>
                </div>
                <div>
                  <p className="text-[10px] text-[#3d4251] font-mono uppercase tracking-wider mb-1">Body</p>
                  <div className="bg-black/30 rounded-lg p-4 border border-white/[0.04] max-h-64 overflow-y-auto">
                    <p className="text-sm text-[#9ca3af] whitespace-pre-wrap font-mono text-xs">{selectedEmail.body_preview || "No body preview"}</p>
                  </div>
                </div>
                {selectedEmail.error_message && (
                  <div>
                    <p className="text-[10px] text-[#3d4251] font-mono uppercase tracking-wider mb-1">Error</p>
                    <p className="text-sm text-red-400">{selectedEmail.error_message}</p>
                  </div>
                )}
                <div>
                  <p className="text-[10px] text-[#3d4251] font-mono uppercase tracking-wider mb-1">Sent At</p>
                  <p className="text-sm text-[#6b7280]">{new Date(selectedEmail.sent_at).toLocaleString()}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EmailLogs;