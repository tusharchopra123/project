"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import Dashboard from "@/components/Dashboard";
import AuthenticatedNavbar from "@/components/AuthenticatedNavbar";

export default function DashboardPage() {
    const router = useRouter();
    const { data: session, status } = useSession();
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (status === "unauthenticated") {
            router.push("/login");
            return;
        }

        if (status === "authenticated" && session?.user?.email) {
            // Fetch from Backend
            const fetchPortfolio = async () => {
                try {
                    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
                    const res = await fetch(`${baseUrl}/portfolio/`, {
                        headers: {
                            // SECURE: Send the Google ID Token
                            'Authorization': `Bearer ${(session as any).id_token}`
                        }
                    });

                    if (res.ok) {
                        const json = await res.json();
                        if (json) {
                            setData(json);
                            setLoading(false);
                            return;
                        }
                    }
                } catch (e) {
                    console.error("Fetch failed", e);
                }

                // Fallback to Session Storage
                const stored = sessionStorage.getItem('portfolioData');
                if (stored) {
                    setData(JSON.parse(stored));
                } else {
                    router.push('/upload');
                }
                setLoading(false);
            };

            fetchPortfolio();
        }
    }, [router, status, session]);

    if (status === "loading" || loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Loading portfolio...</p>
                </div>
            </div>
        );
    }

    if (!data) return null;

    return (
        <main className="min-h-screen bg-gray-50">
            <AuthenticatedNavbar />
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="space-y-8">
                    <div className="text-center max-w-2xl mx-auto">
                        <h2 className="text-3xl font-extrabold text-gray-900 tracking-tight sm:text-4xl">
                            Your Portfolio Analysis
                        </h2>
                        <p className="mt-4 text-lg text-gray-500">
                            Here is a breakdown of your portfolio performance based on the uploaded CAM statement.
                        </p>
                    </div>

                    <Dashboard data={data} />
                </div>
            </div>
        </main>
    );
}
