import React, { useState } from "react";
import { Code, Copy, CheckCircle2 } from "lucide-react";

const DniPanel: React.FC = () => {
  const [phoneNumbers, setPhoneNumbers] = useState({
    facebook: "",
    google: "",
    tiktok: "",
    bing: "",
    default: "",
  });
  const [copied, setCopied] = useState(false);

  const generateSnippet = () => {
    return `<!-- Scam Slayer DNI — Dynamic Number Insertion -->
<script>
(function() {
  var numbers = {
    facebook:  "${phoneNumbers.facebook || phoneNumbers.default}",
    google:    "${phoneNumbers.google || phoneNumbers.default}",
    tiktok:    "${phoneNumbers.tiktok || phoneNumbers.default}",
    bing:      "${phoneNumbers.bing || phoneNumbers.default}",
    default:   "${phoneNumbers.default}",
  };

  function getSource() {
    var params = new URLSearchParams(window.location.search);
    var src = (params.get("utm_source") || "").toLowerCase();
    if (params.get("fbclid") || src.indexOf("fb") > -1 || src.indexOf("facebook") > -1) return "facebook";
    if (params.get("gclid") || params.get("gad_campaignid") || src.indexOf("google") > -1) return "google";
    if (params.get("ttclid") || src.indexOf("tiktok") > -1) return "tiktok";
    if (params.get("msclkid") || src.indexOf("bing") > -1) return "bing";
    return "default";
  }

  function swapNumbers() {
    var source = getSource();
    var number = numbers[source] || numbers.default;
    if (!number) return;

    // Swap all tel: links
    document.querySelectorAll("a[href^='tel:']").forEach(function(el) {
      el.href = "tel:" + number.replace(/\D/g, "");
      el.textContent = number;
    });

    // Swap all elements with class .phone-number
    document.querySelectorAll(".phone-number, .tel, [data-phone]").forEach(function(el) {
      el.textContent = number;
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", swapNumbers);
  } else {
    swapNumbers();
  }
})();
</script>
<!-- End Scam Slayer DNI -->`;
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generateSnippet());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const allFilled = phoneNumbers.default.trim().length > 0;

  return (
    <div className="bg-[#0f1117] border border-[#1e2130] rounded-xl p-4 sm:p-6 space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center shrink-0">
          <Code size={15} className="text-purple-400" />
        </div>
        <div>
          <h2 className="text-white text-sm font-semibold">DNI Snippet Generator</h2>
          <p className="text-[#4b5563] text-xs font-mono">Dynamic Number Insertion — swaps phone numbers based on traffic source</p>
        </div>
      </div>

      {/* Explanation */}
      <div className="bg-[#1a1d2e] border border-[#2a2d3a] rounded-lg px-4 py-3">
        <p className="text-[#9ca3af] text-xs leading-relaxed">
          Paste this snippet on any website. It automatically swaps the phone number based on where the visitor came from — Facebook, Google, TikTok, or Bing. This lets you track exactly which ad platform is sending traffic.
        </p>
      </div>

      {/* Phone Number Inputs */}
      <div className="space-y-3">
        <p className="text-xs text-[#6b7280] font-semibold uppercase tracking-wider">Phone Numbers per Platform</p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-[#4b5563] mb-1 block">Default Number <span className="text-red-400">*</span></label>
            <input
              className="w-full bg-[#1a1d2e] border border-[#2a2d3a] rounded-lg px-3 py-2.5 text-white text-sm font-mono placeholder-[#4b5563] focus:outline-none focus:border-[#3b82f6] transition-colors"
              placeholder="+1-855-555-0100"
              value={phoneNumbers.default}
              onChange={(e) => setPhoneNumbers({ ...phoneNumbers, default: e.target.value })}
            />
          </div>

          <div>
            <label className="text-xs text-[#4b5563] mb-1 block">Facebook / Meta</label>
            <input
              className="w-full bg-[#1a1d2e] border border-[#2a2d3a] rounded-lg px-3 py-2.5 text-white text-sm font-mono placeholder-[#4b5563] focus:outline-none focus:border-[#3b82f6] transition-colors"
              placeholder="+1-855-555-0101"
              value={phoneNumbers.facebook}
              onChange={(e) => setPhoneNumbers({ ...phoneNumbers, facebook: e.target.value })}
            />
          </div>

          <div>
            <label className="text-xs text-[#4b5563] mb-1 block">Google Ads</label>
            <input
              className="w-full bg-[#1a1d2e] border border-[#2a2d3a] rounded-lg px-3 py-2.5 text-white text-sm font-mono placeholder-[#4b5563] focus:outline-none focus:border-[#3b82f6] transition-colors"
              placeholder="+1-855-555-0102"
              value={phoneNumbers.google}
              onChange={(e) => setPhoneNumbers({ ...phoneNumbers, google: e.target.value })}
            />
          </div>

          <div>
            <label className="text-xs text-[#4b5563] mb-1 block">TikTok Ads</label>
            <input
              className="w-full bg-[#1a1d2e] border border-[#2a2d3a] rounded-lg px-3 py-2.5 text-white text-sm font-mono placeholder-[#4b5563] focus:outline-none focus:border-[#3b82f6] transition-colors"
              placeholder="+1-855-555-0103"
              value={phoneNumbers.tiktok}
              onChange={(e) => setPhoneNumbers({ ...phoneNumbers, tiktok: e.target.value })}
            />
          </div>

          <div>
            <label className="text-xs text-[#4b5563] mb-1 block">Microsoft Bing Ads</label>
            <input
              className="w-full bg-[#1a1d2e] border border-[#2a2d3a] rounded-lg px-3 py-2.5 text-white text-sm font-mono placeholder-[#4b5563] focus:outline-none focus:border-[#3b82f6] transition-colors"
              placeholder="+1-855-555-0104"
              value={phoneNumbers.bing}
              onChange={(e) => setPhoneNumbers({ ...phoneNumbers, bing: e.target.value })}
            />
          </div>
        </div>
      </div>

      {/* Generated Snippet */}
      {allFilled && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <p className="text-xs text-[#6b7280] font-semibold uppercase tracking-wider">Generated Snippet</p>
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-500/10 border border-purple-500/20 text-purple-400 hover:bg-purple-500/20 transition-colors text-xs font-medium"
            >
              {copied ? <CheckCircle2 size={12} /> : <Copy size={12} />}
              {copied ? "Copied!" : "Copy"}
            </button>
          </div>

          <div className="bg-[#0a0b10] border border-[#1e2130] rounded-lg p-4 overflow-x-auto">
            <pre className="text-xs text-[#00FF88] font-mono whitespace-pre-wrap leading-relaxed">
              {generateSnippet()}
            </pre>
          </div>

          <p className="text-xs text-[#4b5563]">
            Paste this snippet inside the <code className="text-purple-400">&lt;head&gt;</code> tag of any webpage to enable dynamic number swapping.
          </p>
        </div>
      )}

      {!allFilled && (
        <p className="text-xs text-[#4b5563] text-center py-2">
          Enter at least a default phone number to generate the snippet.
        </p>
      )}
    </div>
  );
};

export default DniPanel;