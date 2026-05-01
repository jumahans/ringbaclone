export interface User {
  id: string;
  email: string;
  username: string;
  role: "admin" | "operator" | "viewer";
  created_at: string;
}

export interface TokenResponse {
  access: string;
  refresh: string;
  user_id: string;
  email: string;
  username: string;
  role: string;
}

export interface RespOrg {
  code: string;
  carrier_name: string;
  abuse_email: string;
  website: string;
}

export interface ScamReport {
  id: string;
  brand: string;
  phone_number: string;
  landing_url: string;
  resporg_raw: string;
  resporg: RespOrg | null;
  status: "pending" | "reported" | "killed" | "failed";
  report_sent_at: string | null;
  screenshot_path: string;
  notes: string;
  submitted_by: string;
  created_at: string;
  updated_at: string;
}

export interface Stats {
  total: number;
  pending: number;
  reported: number;
  killed: number;
  failed: number;
  this_week: number;
}

export interface PaginatedReports {
  total: number;
  page: number;
  page_size: number;
  results: ScamReport[];
}

export interface ActionResult {
  success: boolean;
  message: string;
  report_id: string;
  new_status: string;
}


export interface SentEmail {
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