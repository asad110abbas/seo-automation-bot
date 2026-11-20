"use client";
import { useState } from "react";
import Image from "next/image";
import { useAuth } from "@/context/AuthContext";
import { Loader2 } from "lucide-react";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function LoginPage() {
  const { login } = useAuth();
  const [tab, setTab] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      let res: Response;
      if (tab === "login") {
        const form = new URLSearchParams({ username: email, password });
        res = await fetch(`${BASE_URL}/api/v1/auth/login`, { method: "POST", body: form });
      } else {
        res = await fetch(`${BASE_URL}/api/v1/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password, full_name: name }),
        });
      }
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Request failed");
      login(data.access_token);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white border border-gray-200 rounded-2xl p-8 w-full max-w-sm shadow-sm">
        <div className="text-center mb-6">
          <div className="flex justify-center mb-3">
            <Image src="/logo.svg" alt="SEO Automation Bot" width={64} height={64} className="rounded-xl object-contain" />
          </div>
          <h1 className="text-xl font-bold text-gray-900">SEO Automation Bot</h1>
        </div>

        <div className="flex mb-5 bg-gray-100 rounded-lg p-1">
          {(["login", "register"] as const).map((t) => (
            <button key={t} onClick={() => setTab(t)} className={`flex-1 py-1.5 text-sm font-medium rounded-md transition-colors ${tab === t ? "bg-white shadow-sm text-gray-900" : "text-gray-500"}`}>
              {t === "login" ? "Login" : "Register"}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="space-y-3">
          {tab === "register" && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <input className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={name} onChange={e => setName(e.target.value)} placeholder="Ali Ahmed" />
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input type="email" required className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={email} onChange={e => setEmail(e.target.value)} placeholder="ali@clinic.pk" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input type="password" required className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" />
          </div>
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button type="submit" disabled={loading} className="w-full bg-brand-600 text-white py-2 rounded-lg text-sm font-semibold hover:bg-brand-700 disabled:opacity-60 flex items-center justify-center gap-2">
            {loading && <Loader2 size={14} className="animate-spin" />}
            {tab === "login" ? "Sign In" : "Create Account"}
          </button>
        </form>
      </div>
    </div>
  );
}
