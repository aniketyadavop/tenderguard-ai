/**
 * Centralized API Client for TenderGuard AI
 * Connects Vite/React frontend to FastAPI backend.
 * Provides real-time upload progress tracking, fallback to benchmarks if offline,
 * and typed helpers for all verification and review endpoints.
 */

import { MOCK_VENDORS, TENDER_DETAILS } from '../data/mockVendors';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

class ApiClient {
  constructor(baseUrl = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async _request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Accept': 'application/json',
      ...options.headers,
    };

    if (options.body && !(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    try {
      const response = await fetch(url, { ...options, headers });
      if (!response.ok) {
        let errorDetail = `HTTP ${response.status} ${response.statusText}`;
        try {
          const errData = await response.json();
          if (errData.detail) errorDetail = errData.detail;
        } catch (_) {}
        throw new Error(errorDetail);
      }
      return await response.json();
    } catch (err) {
      console.warn(`[TenderGuard API] Request to ${endpoint} failed:`, err.message);
      throw err;
    }
  }

  /**
   * Fetches active tender specifications.
   */
  async getTenderSpecs() {
    try {
      return await this._request('/vendors/tenders/current');
    } catch (err) {
      // Fallback to local specifications if backend offline
      return TENDER_DETAILS;
    }
  }

  /**
   * Fetches all vendors (benchmarks + uploaded).
   */
  async getVendors() {
    try {
      return await this._request('/vendors');
    } catch (err) {
      return MOCK_VENDORS;
    }
  }

  /**
   * Fetches full vendor dossier with documents, extracted fields, bounding boxes, and findings.
   */
  async getVendorDossier(vendorId) {
    try {
      return await this._request(`/vendors/${vendorId}`);
    } catch (err) {
      // Fallback to local mock vendor by ID
      const local = MOCK_VENDORS.find(v => v.id === vendorId) || MOCK_VENDORS[0];
      return local;
    }
  }

  /**
   * Uploads a document with real-time XMLHttpRequest progress bar tracking.
   */
  uploadDocumentWithProgress(file, onProgress) {
    return new Promise((resolve, reject) => {
      const url = `${this.baseUrl}/documents/upload`;
      const xhr = new XMLHttpRequest();
      const formData = new FormData();
      formData.append('file', file);

      xhr.open('POST', url, true);

      // Track upload percentage
      if (xhr.upload && onProgress) {
        xhr.upload.onprogress = (event) => {
          if (event.lengthComputable) {
            const percentComplete = Math.round((event.loaded / event.total) * 100);
            onProgress(percentComplete);
          }
        };
      }

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const data = JSON.parse(xhr.responseText);
            resolve(data);
          } catch (e) {
            reject(new Error('Invalid JSON response from server'));
          }
        } else {
          let errorMsg = `Upload failed (${xhr.status})`;
          try {
            const errObj = JSON.parse(xhr.responseText);
            if (errObj.detail) errorMsg = errObj.detail;
          } catch (_) {}
          reject(new Error(errorMsg));
        }
      };

      xhr.onerror = () => {
        reject(new Error('Network error during file upload. Check if backend is running.'));
      };

      xhr.send(formData);
    });
  }

  /**
   * Enqueues an asynchronous document analysis job.
   */
  async startAnalysis(payload) {
    return await this._request('/analysis/start', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  /**
   * Polls the live status of an analysis job (stages 1-4).
   */
  async getJobStatus(jobId) {
    return await this._request(`/analysis/jobs/${jobId}`);
  }

  /**
   * Cancels a running or queued analysis job.
   */
  async cancelJob(jobId) {
    return await this._request(`/analysis/jobs/${jobId}/cancel`, {
      method: 'POST'
    });
  }

  /**
   * Submits a human procurement officer review decision / override.
   */
  async submitReviewDecision(decisionPayload) {
    return await this._request('/review/decision', {
      method: 'POST',
      body: JSON.stringify(decisionPayload)
    });
  }

  /**
   * Retrieves the human review history for a vendor.
   */
  async getReviewHistory(vendorId) {
    try {
      return await this._request(`/review/history/${vendorId}`);
    } catch (err) {
      return [];
    }
  }

  /**
   * User authentication with short-lived JWT token.
   */
  async login(email, password) {
    return await this._request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
  }

  /**
   * Fetches audit log events.
   */
  async getAuditEvents(params = {}) {
    try {
      const query = new URLSearchParams(params).toString();
      return await this._request(`/audit/events${query ? '?' + query : ''}`);
    } catch (err) {
      return [];
    }
  }

  /**
   * Returns direct URLs for CSV and PDF report downloads.
   */
  getVendorCsvReportUrl(vendorId) {
    return `${this.baseUrl}/reports/vendors/${vendorId}/csv`;
  }

  getVendorPdfReportUrl(vendorId) {
    return `${this.baseUrl}/reports/vendors/${vendorId}/pdf`;
  }

  getTenderSummaryCsvUrl(tenderId = 'tender-gem-89412') {
    return `${this.baseUrl}/reports/tenders/${tenderId}/summary-csv`;
  }

  /**
   * Initiates browser download of vendor compliance CSV.
   */
  downloadVendorCsv(vendorId) {
    window.open(this.getVendorCsvReportUrl(vendorId), '_blank');
  }

  /**
   * Initiates browser download of official PDF audit certificate.
   */
  downloadVendorPdf(vendorId) {
    window.open(this.getVendorPdfReportUrl(vendorId), '_blank');
  }
}

export const api = new ApiClient();
export default api;
