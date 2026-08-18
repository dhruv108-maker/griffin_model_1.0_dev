const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";

class ApiError extends Error {
  constructor(message, { status, endpoint, data } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.endpoint = endpoint;
    this.data = data;
  }
}

async function request(endpoint, options = {}) {
  const { method = "GET", body, headers = {}, ...rest } = options;
  const isFormData = body instanceof FormData;
  const url = `${API_BASE_URL}${endpoint}`;

  const config = {
    method,
    ...rest,
    headers: {
      Accept: "application/json",
      ...headers,
    },
  };

  if (body !== undefined) {
    if (isFormData) {
      config.body = body;
    } else {
      config.headers["Content-Type"] = "application/json";
      config.body = JSON.stringify(body);
    }
  }

  let response;
  try {
    response = await fetch(url, config);
  } catch (cause) {
    throw new ApiError(`Network error while calling ${endpoint}`, {
      endpoint,
      data: cause,
    });
  }

  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail =
      typeof data === "object" && data?.detail
        ? data.detail
        : typeof data === "object" && data?.message
          ? data.message
          : typeof data === "string" && data.trim()
            ? data
            : `Request failed with status ${response.status}`;

    throw new ApiError(detail, {
      status: response.status,
      endpoint,
      data,
    });
  }

  return data;
}

export const healthAPI = {
  check: () => request("/health"),
};

export const workspaceAPI = {
  list: () => request("/workspaces"),
  create: ({ name, description = "" }) =>
    request("/workspaces", {
      method: "POST",
      body: { name, description },
    }),
};

export const projectAPI = {
  list: (workspaceId) =>
    request(workspaceId ? `/projects?workspace_id=${encodeURIComponent(workspaceId)}` : "/projects"),
  get: (projectId) => request(`/projects/${projectId}`),
  create: ({ workspace_id, name, description = "" }) =>
    request("/projects", {
      method: "POST",
      body: { workspace_id, name, description },
    }),
  update: (projectId, data) =>
    request(`/projects/${projectId}`, { method: "PUT", body: data }),
  delete: (projectId) =>
    request(`/projects/${projectId}`, { method: "DELETE" }),
};

export const curriculumAPI = {
  list: (projectId) => request(`/curriculum?project_id=${encodeURIComponent(projectId)}`),
  get: (curriculumId) => request(`/curriculum/${curriculumId}`),
  upload: ({ projectId, title, file }) => {
    const formData = new FormData();
    formData.append("project_id", projectId);
    formData.append("title", title);
    formData.append("file", file);
    return request("/curriculum/upload", { method: "POST", body: formData });
  },
  delete: (curriculumId) => request(`/curriculum/${curriculumId}`, { method: "DELETE" }),
};

export const reportAPI = {
  list: (projectId) => request(`/reports?project_id=${encodeURIComponent(projectId)}`),
  get: (reportId) => request(`/reports/${reportId}`),
  upload: ({ projectId, studentName = "", file }) => {
    const formData = new FormData();
    formData.append("project_id", projectId);
    formData.append("student_name", studentName);
    formData.append("file", file);
    return request("/reports/upload", { method: "POST", body: formData });
  },
  delete: (reportId) => request(`/reports/${reportId}`, { method: "DELETE" }),
};

export const evaluationAPI = {
  start: ({ project_id, curriculum_id, report_ids, name }) =>
    request("/evaluations/run", {
      method: "POST",
      body: { project_id, curriculum_id, report_ids, name },
    }),
  get: (evaluationId) => request(`/evaluations/${evaluationId}`),
  status: (evaluationId) => request(`/evaluations/${evaluationId}/status`),
  cancel: (evaluationId) =>
    request(`/evaluations/${evaluationId}/cancel`, { method: "POST" }),
  result: (evaluationId) => request(`/evaluations/${evaluationId}/result`),
  resultForReport: (evaluationId, reportId) =>
    request(`/evaluations/${evaluationId}/results/${reportId}`),
};

export const historyAPI = {
  project: (projectId) =>
    request(projectId ? `/history?project_id=${encodeURIComponent(projectId)}` : "/history"),
};

const api = {
  request,
  health: healthAPI,
  workspaces: workspaceAPI,
  projects: projectAPI,
  curriculum: curriculumAPI,
  reports: reportAPI,
  evaluations: evaluationAPI,
  history: historyAPI,
};

export { ApiError };
export default api;
