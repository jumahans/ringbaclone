import React, { useState } from "react";
import { Search, RefreshCw, ExternalLink, AlertCircle, Globe } from "lucide-react";
import { reportsApi } from "../api/reports";

interface GoogleAd {
  advertiser: string;
  ad_text: string;
  ad_title: string;
  first_shown: string;
  format: string;
  region: string;
  creative_id: string;
  link: string;
}

interface GoogleAdsResult {
  found: boolean;
  ads: GoogleAd[];
  total: number;
  error: string;
}

const GoogleAdsPanel: React.FC = () => {
  const [domain, setDomain] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GoogleAdsResult | null>(null);
  const [error, setError] = useState("");

  const handleSearch = async () => {
    if (!domain.trim()) return;
    setError("");
    setResult(null);
    setLoading(true);
    try {
      const res = await reportsApi.searchGoogleAds(domain.trim());
      setResult(res);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Search failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-[#0f1117] border border-[#1e2130] rounded-xl p-4 sm:p-6 space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center shrink-0">
          <Globe size={15} className="text-emerald-400" />
        </div>
        <div>
          <h2 className="text-white text-sm font-semibold">Google Ads Transparency</h2>
          <p className="text-[#4b5563] text-xs font-mono">Find Google ads running on any scam domain</p>
        </div>
      </div>

      {/* Input */}
      <div className="flex flex-col sm:flex-row gap-2">
        <input
          className="flex-1 bg-[#1a1d2e] border border-[#2a2d3a] rounded-lg px-4 py-3 text-white text-sm font-mono placeholder-[#4b5563] focus:outline-none focus:border-[#3b82f6] transition-colors"
          placeholder="Domain — e.g. scam-site.com"
          value={domain}
          onChange={(e) => setDomain(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
        />
        <button
          onClick={handleSearch}
          disabled={loading || !domain.trim()}
          className="w-full sm:w-auto px-5 py-3 bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          {loading ? <RefreshCw size={14} className="animate-spin" /> : <Search size={14} />}
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="bg-[#1a1d2e] border border-[#2a2d3a] rounded-lg px-4 py-6 text-center">
          <RefreshCw size={20} className="animate-spin text-emerald-400 mx-auto mb-2" />
          <p className="text-[#6b7280] text-sm">Scraping Google Ads Transparency Center...</p>
          <p className="text-[#4b5563] text-xs mt-1">This may take up to 30 seconds</p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3 text-red-400 text-xs font-mono">
          <AlertCircle size={13} className="shrink-0" />
          {error}
        </div>
      )}

      {/* No results */}
      {result && !result.found && !error && (
        <div className="bg-[#1a1d2e] border border-[#2a2d3a] rounded-lg px-4 py-6 text-center">
          <p className="text-[#6b7280] text-sm">No Google ads found for this domain.</p>
          <p className="text-[#4b5563] text-xs mt-1">The scammer may be using Facebook, TikTok, or direct traffic.</p>
        </div>
      )}

      {/* Results */}
      {result && result.found && (
        <div className="space-y-3">
          <p className="text-xs text-[#6b7280] font-mono uppercase tracking-wider">
            {result.total} ad{result.total !== 1 ? "s" : ""} found
          </p>

          {result.ads.map((ad, index) => (
            <div key={index} className="border border-[#1e2130] rounded-xl overflow-hidden">
              {/* Ad Header */}
              <div className="bg-[#1a1d2e] px-4 py-3 flex items-center justify-between gap-3">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-7 h-7 rounded bg-emerald-500/20 flex items-center justify-center shrink-0">
                    <span className="text-emerald-400 text-xs font-bold">
                      {ad.advertiser?.charAt(0)?.toUpperCase() || "G"}
                    </span>
                  </div>
                  <div className="min-w-0">
                    <p className="text-white text-sm font-medium truncate">{ad.advertiser || "Unknown Advertiser"}</p>
                    {ad.creative_id && (
                      <p className="text-[#4b5563] text-xs font-mono">ID: {ad.creative_id}</p>
                    )}
                  </div>
                </div>
                <span className="text-xs font-mono px-2 py-0.5 rounded border bg-red-500/10 text-red-400 border-red-500/20 shrink-0">
                  Active
                </span>
              </div>

              {/* Ad Details */}
              <div className="p-4 space-y-3">
                {ad.ad_title && (
                  <div>
                    <p className="text-xs text-[#4b5563] mb-1">Title</p>
                    <p className="text-white text-sm font-medium">{ad.ad_title}</p>
                  </div>
                )}

                {ad.ad_text && (
                  <div>
                    <p className="text-xs text-[#4b5563] mb-1">Ad Text</p>
                    <p className="text-[#e2e8f0] text-sm leading-relaxed line-clamp-3">{ad.ad_text}</p>
                  </div>
                )}

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  <div>
                    <p className="text-xs text-[#4b5563] mb-1">First Shown</p>
                    <p className="text-white text-xs font-mono">{ad.first_shown || "—"}</p>
                  </div>
                  <div>
                    <p className="text-xs text-[#4b5563] mb-1">Format</p>
                    <p className="text-white text-xs font-mono">{ad.format || "—"}</p>
                  </div>
                  <div>
                    <p className="text-xs text-[#4b5563] mb-1">Region</p>
                    <p className="text-white text-xs font-mono">{ad.region || "US"}</p>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-[#1e2130]">
                  {ad.link && (
                    <a
                      href={ad.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1.5 text-xs text-emerald-400 hover:text-emerald-300 transition-colors"
                    >
                      <ExternalLink size={11} />
                      View on Google
                    </a>
                  )}
                  <a
                    href={`https://adstransparency.google.com/?query=${domain}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1.5 text-xs text-red-400 hover:text-red-300 transition-colors"
                  >
                    Report to Google →
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default GoogleAdsPanel;