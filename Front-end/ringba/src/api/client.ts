import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "https://scam-slayer-api.onrender.com/api";
// const BASE_URL = import.meta.env.REACT_APP_API_URL || "http://127.0.0.1:8000/api";

const client = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
 
      const refresh = localStorage.getItem("refresh_token");
      if (!refresh) {
        localStorage.clear();
        window.location.href = "/login";
        return Promise.reject(error);
      }

      try {
        const res = await axios.post(`${BASE_URL}/auth/refresh`, {
          refresh,
        });
        const newAccess = res.data.access;
        localStorage.setItem("access_token", newAccess);
        original.headers.Authorization = `Bearer ${newAccess}`;
        return client(original);
      } catch {
        localStorage.clear();
        window.location.href = "/login";
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

export default client;