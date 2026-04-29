import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Shield, Mail, Lock, AlertCircle, Loader } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

const Login: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Invalid email or password."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#08090d] flex items-center justify-center px-4">
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage:
            "linear-gradient(#ffffff 1px, transparent 1px), linear-gradient(90deg, #ffffff 1px, transparent 1px)",
          backgroundSize: "40px 40px",
        }}
      />

      <div className="relative w-full max-w-sm">
        <div className="flex flex-col items-center mb-10">
          <div className="w-16 h-16 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center mb-5">
            <Shield size={28} className="text-red-400" />
          </div>
          <h1 className="text-white text-2xl font-bold tracking-tight">
            Fraud Hunter
          </h1>
          <p className="text-[#4b5563] text-sm mt-1 font-mono">
            Security Operations Portal
          </p>
        </div>

        <div className="bg-[#0f1117] border border-[#1e2130] rounded-2xl p-7 shadow-2xl">
          <h2 className="text-white text-sm font-semibold mb-6 text-center">
            Sign in to your account
          </h2>

          {error && (
            <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2.5 text-red-400 text-xs font-mono mb-4">
              <AlertCircle size={13} />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-[#6b7280] mb-2">
                Email
              </label>
              <div className="relative">
                <Mail
                  size={14}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-[#4b5563]"
                />
                <input
                  type="email"
                  required
                  className="w-full bg-[#1a1d2e] border border-[#2a2d3a] rounded-lg pl-9 pr-4 py-3 text-white text-sm placeholder-[#374151] focus:outline-none focus:border-[#3b82f6] transition-colors"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-[#6b7280] mb-2">
                Password
              </label>
              <div className="relative">
                <Lock
                  size={14}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-[#4b5563]"
                />
                <input
                  type="password"
                  required
                  className="w-full bg-[#1a1d2e] border border-[#2a2d3a] rounded-lg pl-9 pr-4 py-3 text-white text-sm placeholder-[#374151] focus:outline-none focus:border-[#3b82f6] transition-colors"
                  placeholder="••••••••••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-red-500 hover:bg-red-600 disabled:opacity-50 text-white text-sm font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              {loading ? (
                <Loader size={14} className="animate-spin" />
              ) : (
                <Shield size={14} />
              )}
              {loading ? "Signing in..." : "Sign In"}
            </button>
          </form>

          <p className="text-[#4b5563] text-xs text-center mt-5">
            Don't have an account?{" "}
            <Link
              to="/register"
              className="text-red-400 hover:text-red-300 transition-colors"
            >
              Register
            </Link>
          </p>
        </div>

        <p className="text-[#2a2d3a] text-xs text-center mt-6 font-mono">
          Fraud Hunter Portal v1.0
        </p>
      </div>
    </div>
  );
};

export default Login;