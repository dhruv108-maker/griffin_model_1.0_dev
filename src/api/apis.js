const API_BASE_URL =
  import.meta.env.VITE_API_URL || "/api";

async function request(endpoint, options = {}) {
  const {
    method = "GET",
    body,
    headers = {},
    ...rest
  } = options;

  const isFormData = body instanceof FormData;

  const config = {
    method,
    ...rest,
    headers: {
      Accept: "application/json",
      ...headers,
    },
  };

  // Do NOT manually set Content-Type for FormData.
  // Browser adds the multipart boundary automatically.
  if (body !== undefined) {
    if (isFormData) {
      config.body = body;
    } else {
      config.headers["Content-Type"] = "application/json";
      config.body = JSON.stringify(body);
    }
  }

  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    config
  );

  let data = null;
  const contentType = response.headers.get("content-type");
  if (contentType?.includes("application/json")) {
    data = await response.json();
  } else {
    data = await response.text();
  }

  if (!response.ok) {
    const message =
      typeof data === "object" && data?.detail
        ? data.detail
        : typeof data === "object" && data?.message
          ? data.message
          : `API request failed with status ${response.status}`;

    const error = new Error(message);
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}

export const healthAPI = {
  check: () =>
    request("/health"),
};

export const workspaceAPI = {
  list: () =>
    request("/workspaces"),
  create: ({ name, description = "" }) =>
    request("/workspaces", {
      method: "POST",
      body: { name, description },
    }),
};

export const projectAPI = {
  list: (workspaceId) =>
    request(workspaceId ? `/projects?workspace_id=${workspaceId}` : "/projects"),
  create: ({ workspace_id, name, description = "" }) =>
    request("/projects", {
      method: "POST",
      body: { workspace_id, name, description },
    }),
};

export const curriculumAPI = {
  upload: ({ projectId, title, file }) => {
    const formData = new FormData();
    formData.append("project_id", projectId);
    formData.append("title", title);
    if (file) {
      formData.append("file", file);
    }
    return request("/curriculum/upload", {
      method: "POST",
      body: formData,
    });
  },
};

export const reportAPI = {
  upload: ({ projectId, studentName = "", file }) => {
    const formData = new FormData();
    formData.append("project_id", projectId);
    formData.append("student_name", studentName);
    if (file) {
      formData.append("file", file);
    }
    return request("/reports/upload", {
      method: "POST",
      body: formData,
    });
  },
};

export const evaluationAPI = {
  start: ({ project_id, curriculum_id, report_ids, name }) =>
    request("/evaluations/run", {
      method: "POST",
      body: { project_id, curriculum_id, report_ids, name },
    }),
  status: (evaluationId) =>
    request(`/evaluations/${evaluationId}/status`),
  result: (evaluationId) =>
    request(`/evaluations/${evaluationId}/result`),
};

export const historyAPI = {
  project: (projectId) =>
    request(projectId ? `/history?project_id=${projectId}` : "/history"),
};

export const settingsAPI = {
  get: () => request("/settings/"),
};

export const chatAPI = {
  sendMessage: ({ chatId, content }) =>
    request(`/chat/message?chat_id=${chatId}&content=${encodeURIComponent(content)}`, {
      method: "POST",
    }),
};

const api = {
  health: healthAPI,
  workspaces: workspaceAPI,
  projects: projectAPI,
  curriculum: curriculumAPI,
  reports: reportAPI,
  evaluations: evaluationAPI,
  history: historyAPI,
  settings: settingsAPI,
  chat: chatAPI,
};

export default api;
