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
};