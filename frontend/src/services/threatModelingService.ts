/**
 * API service for threat modeling analysis.
 */

import axios, { AxiosError } from 'axios';
import type { AnalysisResponse, AnalysisError } from '../types/analysis';

const API_BASE_URL = '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for LLM processing
});

export interface AnalyzeResult {
  success: true;
  data: AnalysisResponse;
}

export interface AnalyzeErrorResult {
  success: false;
  error: string;
  details?: Record<string, unknown>;
}

export type AnalyzeResponse = AnalyzeResult | AnalyzeErrorResult;

/**
 * Analyze an architecture diagram for security threats.
 *
 * @param file - The image file to analyze
 * @param confidence - Optional confidence threshold (0.1-0.9)
 * @param iou - Optional IoU threshold (0.1-0.9)
 * @returns Analysis response or error
 */
export async function analyzeDiagram(
  file: File,
  confidence?: number,
  iou?: number
): Promise<AnalyzeResponse> {
  try {
    const formData = new FormData();
    formData.append('file', file);
    if (confidence !== undefined) formData.append('confidence', String(confidence));
    if (iou !== undefined) formData.append('iou', String(iou));

    const response = await api.post<AnalysisResponse>(
      '/threat-model/analyze',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return {
      success: true,
      data: response.data,
    };
  } catch (err) {
    const error = err as AxiosError<AnalysisError>;

    if (error.response?.data) {
      return {
        success: false,
        error: error.response.data.error || 'Analysis failed',
        details: error.response.data.details,
      };
    }

    if (error.code === 'ECONNABORTED') {
      return {
        success: false,
        error: 'Request timed out. The analysis is taking longer than expected.',
      };
    }

    return {
      success: false,
      error: error.message || 'An unexpected error occurred',
    };
  }
}

/**
 * Check if the API is healthy.
 *
 * @returns true if healthy, false otherwise
 */
export async function checkHealth(): Promise<boolean> {
  try {
    const response = await api.get('/health');
    return response.data?.status === 'healthy';
  } catch {
    return false;
  }
}
