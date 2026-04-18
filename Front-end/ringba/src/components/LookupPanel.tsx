import React, { useState, useEffect, useRef } from "react";
import {
  Search, RefreshCw, Plus, AlertCircle, CheckCircle2,
  Loader, Phone, Signal, MapPin, Shield, Mail, Cpu
} from "lucide-react";
import { reportsApi } from "../api/reports";

interface LookupResult {
  lookup_id: string;
  phone_number: string;
  carrier_name: string;
  resporg_code: string;
  abuse_email: string;
  landing_url: string;
  is_toll_free: boolean;
  campaign_id: string;
  domain: string;
  scraping: boolean;
  line_type: string;
  is_valid: boolean;
  is_voip: boolean;
  country: string;
  region: string;
  city: string;
  timezone: string;
  international_format: string;
  national_format: string;
  risk_level: string;
  is_disposable: boolean;
  is_abuse_detected: boolean;
  line_status: string;
  sms_email: string;
  sms_domain: string;
  mcc: string;
  mnc: string;
}

interface LookupPanelProps {
  onSubmit: (data: {
    brand: string;
    phone_number: string;
    landing_url: string;
  }) => void;
}

const Badge = ({
  value,
  color = "gray",
}: {
  value: string | boolean | null | undefined;
  color?: "green" | "red" | "amber" | "blue" | "gray";
}) => {
  const colors = {
    green: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    red: "bg-red-500/10 text-red-400 border-red-500/20",
    amber: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    blue: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    gray: "bg-[#1a1d2e] text-[#9ca3af] border-[#2a2d3a]",
  };
  return (
    <span className={`text-xs font-mono px-2 py-0.5 rounded border ${colors[color]}`}>
      {String(value ?? "—")}
    </span>
  );
};

const Field = ({
  label,
  value,
  mono = false,
  loading = false,
  color,
}: {
  label: string;
  value?: string | boolean | null;
  mono?: boolean;
  loading?: boolean;
  color?: "green" | "red" | "amber" | "blue" | "gray";
}) => (
  <div className="min-w-0">
    <p className="text-xs text-[#4b5563] mb-1">{label}</p>
    {loading ? (
      <div className="h-4 w-28 bg-[#1a1d2e] rounded animate-pulse" />
    ) : color ? (
      <Badge value={value} color={color} />
    ) : (
      <p className={`text-white text-sm break-all ${mono ? "font-mono" : ""}`}>
        {String(value ?? "—")}
      </p>
    )}
  </div>
);

const SectionHeader = ({
  icon: Icon,
  title,
}: {
  icon: React.ElementType;
  title: string;
}) => (
  <div className="flex items-center gap-2 mb-3">
    <Icon size={13} className="text-[#4b5563]" />
    <p className="text-xs font-semibold text-[#6b7280] uppercase tracking-widest">
      {title}
    </p>
  </div>
);

const LookupPanel: React.FC<LookupPanelProps> = ({ onSubmit }) => {
  const [input, setInput] = useState("");
  const [brand, setBrand] = useState("");
  const [loading, setLoading] = useState(false);
  const [scraping, setScraping] = useState(false);
  const [result, setResult] = useState<LookupResult | null>(null);
  const [error, setError] = useState("");
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const isUrl = (val: string) =>
    val.startsWith("http://") || val.startsWith("https://");

  const handleLookup = async () => {
    setError("");
    setResult(null);
    setScraping(false);
    if (!input.trim()) return;
    setLoading(true);
    try {
      const res = await reportsApi.lookup({
        input: input.trim(),
        is_url: isUrl(input.trim()),
      });
      setResult(res);
      if (res.scraping && res.lookup_id) {
        setScraping(true);
        pollForResult(res.lookup_id);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Lookup failed.");
    } finally {
      setLoading(false);
    }
  };

  const pollForResult = (lookupId: string) => {
    const interval = setInterval(async () => {
      try {
        const res = await reportsApi.getLookupResult(lookupId);
        if (res.done) {
          clearInterval(interval);
          if (timeoutRef.current) clearTimeout(timeoutRef.current);
          setResult((prev) =>
            prev ? {
              ...prev,
              phone_number: res.phone_number,
              carrier_name: res.carrier_name,
              resporg_code: res.resporg_code,
              abuse_email: res.abuse_email,
              is_toll_free: res.is_toll_free,
              line_type: res.line_type,
              is_valid: res.is_valid,
              is_voip: res.is_voip,
              country: res.country,
              region: res.region,
              city: res.city,
              timezone: res.timezone,
              international_format: res.international_format,
              national_format: res.national_format,
              risk_level: res.risk_level,
              is_disposable: res.is_disposable,
              is_abuse_detected: res.is_abuse_detected,
              line_status: res.line_status,
              sms_email: res.sms_email,
              sms_domain: res.sms_domain,
              mcc: res.mcc,
              mnc: res.mnc,
              scraping: false,
            } : prev
          );
          setScraping(false);
        }
      } catch (err) {
        clearInterval(interval);
        if (timeoutRef.current) clearTimeout(timeoutRef.current);
        setScraping(false);
      }
    }, 2000);

    pollRef.current = interval;

    // Stop polling after 3 minutes max
    const timeout = setTimeout(() => {
      clearInterval(interval);
      setScraping(false);
    }, 180000);

    timeoutRef.current = timeout;
  };

  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  const handleSubmit = () => {
    if (!result || !brand.trim()) return;
    onSubmit({
      brand,
      phone_number: result.phone_number,
      landing_url: result.landing_url,
    });
    setInput("");
    setBrand("");
    setResult(null);
  };

  const riskColor = (level?: string): "green" | "amber" | "red" | "gray" => {
    if (!level) return "gray";
    if (level === "low") return "green";
    if (level === "medium") return "amber";
    return "red";
  };

  return (
    <div className="bg-[#0f1117] border border-[#1e2130] rounded-xl p-4 sm:p-6 space-y-4 sm:space-y-5">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center shrink-0">
          <Search size={15} className="text-blue-400" />
        </div>
        <div className="min-w-0">
          <h2 className="text-white text-sm font-semibold">Number Lookup</h2>
          <p className="text-[#4b5563] text-xs font-mono hidden sm:block">
            Paste a toll-free number or scam landing page URL
          </p>
          <p className="text-[#4b5563] text-xs font-mono sm:hidden">
            Paste number or URL
          </p>
        </div>
      </div>

      {/* Input Row */}
      <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
        <input
          className="flex-1 bg-[#1a1d2e] border border-[#2a2d3a] rounded-lg px-3 sm:px-4 py-3 text-white text-sm font-mono placeholder-[#4b5563] focus:outline-none focus:border-[#3b82f6] transition-colors"
          placeholder="+1 888 555 0100 or https://scam-site.com"
          value={input}
          onChange={(e) => { setInput(e.target.value); setResult(null); setError(""); }}
          onKeyDown={(e) => e.key === "Enter" && handleLookup()}
        />
        <button
          onClick={handleLookup}
          disabled={loading || !input.trim()}
          className="w-full sm:w-auto px-4 sm:px-5 py-3 bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-2 whitespace-nowrap"
        >
          {loading ? <RefreshCw size={14} className="animate-spin" /> : <Search size={14} />}
          <span className="sm:hidden">{loading ? "Looking..." : "Lookup"}</span>
          <span className="hidden sm:inline">{loading ? "Looking up..." : "Lookup"}</span>
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/20 rounded-lg px-3 sm:px-4 py-3 text-red-400 text-xs font-mono">
          <AlertCircle size={13} className="shrink-0" />
          <span className="break-words">{error}</span>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="border border-[#1e2130] rounded-xl overflow-hidden">

          {/* Status Bar */}
          <div className="bg-[#1a1d2e] px-3 sm:px-5 py-3 flex items-center justify-between gap-2">
            <span className="text-xs font-medium text-emerald-400 flex items-center gap-2 min-w-0">
              <CheckCircle2 size={13} className="shrink-0" />
              <span className="truncate">
                {scraping ? "URL identified — scraping for number..." : "Lookup complete"}
              </span>
            </span>
            {scraping && <Loader size={13} className="animate-spin text-amber-400 shrink-0" />}
          </div>

          <div className="p-3 sm:p-5 space-y-5">

            {/* Phone Identity */}
            <div>
              <SectionHeader icon={Phone} title="Phone Identity" />
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                <Field
                  label="Phone Number"
                  value={
                    scraping
                      ? "Scraping..."
                      : result.phone_number
                        ? result.phone_number
                        : "No phone number found on this page"
                  }
                  mono
                  loading={scraping && !result.phone_number}
                />
                <Field label="International" value={result.international_format} mono />
                <Field label="National" value={result.national_format} mono />
              </div>
            </div>

            <div className="border-t border-[#1e2130]" />

            {/* Carrier & Line */}
            <div>
              <SectionHeader icon={Signal} title="Carrier & Line" />
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                <Field label="Carrier" value={result.carrier_name} loading={scraping && !result.carrier_name} />
                <Field
                  label="Line Type"
                  value={result.line_type || (result.is_toll_free ? "Toll-Free" : "Non-Toll")}
                  color={result.is_toll_free ? "green" : "amber"}
                />
                <Field
                  label="Line Status"
                  value={result.line_status || "—"}
                  color={result.line_status === "active" ? "green" : "red"}
                />
                <Field
                  label="Valid"
                  value={result.is_valid ? "Yes" : "No"}
                  color={result.is_valid ? "green" : "red"}
                />
                <Field
                  label="VoIP"
                  value={result.is_voip ? "Yes" : "No"}
                  color={result.is_voip ? "red" : "green"}
                />
                <Field
                  label="MCC / MNC"
                  value={result.mcc && result.mnc ? `${result.mcc} / ${result.mnc}` : "—"}
                  mono
                />
              </div>
            </div>

            <div className="border-t border-[#1e2130]" />

            {/* Location */}
            <div>
              <SectionHeader icon={MapPin} title="Location" />
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                <Field label="Country" value={result.country} />
                <Field label="Region" value={result.region} />
                <Field label="City" value={result.city} />
                <Field label="Timezone" value={result.timezone} mono />
              </div>
            </div>

            <div className="border-t border-[#1e2130]" />

            {/* Risk */}
            <div>
              <SectionHeader icon={Shield} title="Risk Assessment" />
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                <Field
                  label="Risk Level"
                  value={result.risk_level || "—"}
                  color={riskColor(result.risk_level)}
                />
                <Field
                  label="Disposable"
                  value={result.is_disposable ? "Yes" : "No"}
                  color={result.is_disposable ? "red" : "green"}
                />
                <Field
                  label="Abuse Detected"
                  value={result.is_abuse_detected ? "Yes" : "No"}
                  color={result.is_abuse_detected ? "red" : "green"}
                />
              </div>
            </div>

            <div className="border-t border-[#1e2130]" />

            {/* Messaging */}
            <div>
              <SectionHeader icon={Mail} title="SMS / Messaging" />
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <Field label="SMS Domain" value={result.sms_domain} mono />
                <Field label="SMS Email" value={result.sms_email} mono />
              </div>
            </div>

            {/* Campaign / URL — only show if URL lookup */}
            {(result.campaign_id || result.domain) && (
              <>
                <div className="border-t border-[#1e2130]" />
                <div>
                  <SectionHeader icon={Cpu} title="Campaign / URL" />
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                    <Field label="Domain" value={result.domain} mono />
                    <Field label="Campaign ID" value={result.campaign_id} mono color="amber" />
                    <Field label="Abuse Email" value={result.abuse_email} mono />
                  </div>
                </div>
              </>
            )}
          </div>

          {/* Submit Row */}
          <div className="px-3 sm:px-5 pb-3 sm:pb-5 flex flex-col sm:flex-row gap-2 sm:gap-3">
            <input
              className="flex-1 bg-[#1a1d2e] border border-[#2a2d3a] rounded-lg px-3 sm:px-4 py-2.5 text-white text-sm placeholder-[#4b5563] focus:outline-none focus:border-[#3b82f6] transition-colors"
              placeholder="Which brand is being impersonated? (e.g. Microsoft)"
              value={brand}
              onChange={(e) => setBrand(e.target.value)}
            />
            <button
              onClick={handleSubmit}
              disabled={!brand.trim() || scraping || !result.is_toll_free}
              className="w-full sm:w-auto px-4 sm:px-5 py-2.5 bg-red-500 hover:bg-red-600 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-2 whitespace-nowrap"
            >
              <Plus size={14} />
              <span className="sm:hidden">Submit</span>
              <span className="hidden sm:inline">Submit Report</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default LookupPanel;