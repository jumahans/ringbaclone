import client from "./client";
import type{ PaginatedReports, ScamReport, Stats, ActionResult } from "../types";

export const reportsApi = {
  getStats: async (): Promise<Stats> => {
    const res = await client.get("/v1/stats");
    return res.data;
  },

  listReports: async (params?: {
    page?: number;
    page_size?: number;
    status?: string;
    search?: string;
  }): Promise<PaginatedReports> => {
    const res = await client.get("/v1/reports", { params });
    return res.data;
  },

  createReport: async (data: {
    brand: string;
    phone_number: string;
    landing_url?: string;
    notes?: string;
  }): Promise<ScamReport> => {
    const res = await client.post("/v1/reports", data);
    return res.data;
  },

  getReport: async (id: string): Promise<ScamReport> => {
    const res = await client.get(`/v1/reports/${id}`);
    return res.data;
  },

  triggerReport: async (id: string): Promise<ActionResult> => {
    const res = await client.post(`/v1/reports/${id}/report`);
    return res.data;
  },

  killReport: async (id: string): Promise<ActionResult> => {
    const res = await client.post(`/v1/reports/${id}/kill`);
    return res.data;
  },

  updateStatus: async (id: string, status: string): Promise<ActionResult> => {
    const res = await client.patch(`/v1/reports/${id}/status`, null, {
      params: { status },
    });
    return res.data;
  },

  lookup: async (data: { input: string; is_url: boolean }): Promise<any> => {
    const res = await client.post("/v1/lookup", data);
    return res.data;
  },

  getLookupResult: async (lookupId: string): Promise<any> => {
    const res = await client.get(`/v1/lookup/${lookupId}/result`);
    return res.data;
  },

  sendEmail: async (reportId: string, payload: { to: string; cc: string[]; bcc: string[]; subject: string; body: string; attachments: { name: string; type: string; data: string }[] }) => {
    const response = await client.post(`/v1/reports/${reportId}/email`, payload);
    return response.data;
  },

  getReportEmails: async (reportId: string): Promise<SentEmail[]> => {
    const response = await client.get(`/v1/reports/${reportId}/emails`);
    return response.data;
  },

  searchFacebookAds: async (domain: string, campaignId: string = "") => {
      const res = await client.get("/v1/ad-library/facebook", {
          params: { domain, campaign_id: campaignId },
      });
      return res.data;
  },

  searchGoogleAds: async (domain: string) => {
    const res = await client.get("/v1/ad-library/google", {
        params: { domain },
    });
    return res.data;
  },


  exportCsv: async () => {
      const token = localStorage.getItem("access_token");
      const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
      window.open(`${BASE}/api/v1/reports/export?token=${token}`, "_blank");
  },
  downloadScreenshot: async (reportId: string, type: "ftc" | "ic3"): Promise<void> => {
  const res = await client.get(`/v1/reports/${reportId}/screenshot`, {
    params: { type },
    responseType: "blob",
  });

  const blob = new Blob([res.data], { type: "image/png" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${type}_complaint_${reportId}.png`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
},
};