
"use client";

import { signIn } from "next-auth/react";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);

    const handleGoogleLogin = async () => {
        setIsLoading(true);
        try {
            await signIn('google', { callbackUrl: '/dashboard' });
        } catch (error) {
            console.error("Login failed", error);
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen w-full flex items-center justify-center bg-gray-50 p-4 relative overflow-hidden">
            {/* Geometric Background Pattern */}
            <div className="absolute inset-0 z-0 opacity-40">
                <style jsx>{`
                    .bg-pattern {
                        background-image: radial-gradient(#cbd5e1 1px, transparent 1px);
                        background-size: 32px 32px;
                    }
                `}</style>
                <div className="w-full h-full bg-pattern"></div>
            </div>

            {/* Decorational Blobs */}
            <div className="absolute top-0 right-0 -mr-20 -mt-20 w-[500px] h-[500px] bg-gradient-to-br from-blue-400/20 to-purple-400/20 rounded-full blur-3xl animate-pulse"></div>
            <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-[400px] h-[400px] bg-gradient-to-tr from-indigo-400/20 to-teal-400/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>

            {/* Main Split Card */}
            <div className="relative z-10 w-full max-w-5xl bg-white rounded-[2rem] shadow-2xl overflow-hidden flex flex-col md:flex-row min-h-[600px] border border-white/50 backdrop-blur-sm">

                {/* Visual Side (Left) */}
                <div className="w-full md:w-1/2 bg-gradient-to-br from-blue-600 via-indigo-600 to-indigo-800 p-12 text-white flex flex-col justify-between relative overflow-hidden">
                    {/* Abstract Shapes */}
                    <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full blur-3xl -mr-16 -mt-16"></div>
                    <div className="absolute bottom-0 left-0 w-48 h-48 bg-purple-500/20 rounded-full blur-2xl -ml-10 -mb-10"></div>

                    <div className="relative z-10">
                        <div className="h-12 w-12 bg-white/20 backdrop-blur-md rounded-xl flex items-center justify-center mb-6">
                            <span className="text-2xl font-bold">W</span>
                        </div>
                        <h1 className="text-4xl font-bold mb-4 leading-tight">
                            Master Your<br />
                            <span className="text-blue-200">Financial Future</span>
                        </h1>
                        <p className="text-blue-100 text-lg opacity-90">
                            Connect your portfolio and get instant, intelligent insights into your investments.
                        </p>
                    </div>

                    {/* Fake UI Element / Graphic */}
                    <div className="relative z-10 mt-12 bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/10 transform rotate-1 hover:rotate-0 transition-transform duration-500">
                        <div className="flex items-center justify-between mb-4">
                            <div className="space-y-1">
                                <div className="h-2 w-24 bg-white/40 rounded-full"></div>
                                <div className="h-2 w-16 bg-white/20 rounded-full"></div>
                            </div>
                            <div className="h-8 w-8 bg-green-400/20 rounded-full flex items-center justify-center">
                                <svg className="w-4 h-4 text-green-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                                </svg>
                            </div>
                        </div>
                        <div className="space-y-2">
                            <div className="h-3 w-full bg-white/10 rounded-full">
                                <div className="h-full w-[70%] bg-blue-400 rounded-full"></div>
                            </div>
                            <div className="flex justify-between text-xs text-blue-100/50">
                                <span>Portfolio Growth</span>
                                <span>+24.5%</span>
                            </div>
                        </div>
                    </div>

                    <div className="relative z-10 mt-auto pt-8">
                        <div className="flex -space-x-4">
                            {[1, 2, 3, 4].map(i => (
                                <div key={i} className="w-10 h-10 rounded-full border-2 border-indigo-700 bg-indigo-500 flex items-center justify-center text-xs font-bold shadow-sm">
                                    {/* Avatar Placeholder */}
                                </div>
                            ))}
                            <div className="w-10 h-10 rounded-full border-2 border-indigo-700 bg-white text-indigo-700 flex items-center justify-center text-xs font-bold shadow-sm">
                                +2k
                            </div>
                        </div>
                        <p className="text-xs text-indigo-300 mt-2 font-medium">Trusted by 2,000+ investors</p>
                    </div>
                </div>

                {/* Login Form Side (Right) */}
                <div className="w-full md:w-1/2 p-12 bg-white flex items-center justify-center">
                    <div className="w-full max-w-sm space-y-8">
                        <div className="text-center md:text-left">
                            <h2 className="text-3xl font-bold text-gray-900">Welcome Back</h2>
                            <p className="mt-2 text-gray-500">Please sign in to access your dashboard.</p>
                        </div>

                        <div className="space-y-4">
                            <button
                                onClick={handleGoogleLogin}
                                disabled={isLoading}
                                className="w-full flex items-center justify-center gap-3 px-6 py-4 bg-white border-2 border-gray-100 hover:border-blue-100 hover:bg-blue-50/50 text-gray-700 font-semibold rounded-xl transition-all duration-200 group"
                            >
                                <svg className="h-6 w-6" viewBox="0 0 24 24">
                                    <path
                                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                                        fill="#4285F4"
                                    />
                                    <path
                                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                                        fill="#34A853"
                                    />
                                    <path
                                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                                        fill="#FBBC05"
                                    />
                                    <path
                                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                                        fill="#EA4335"
                                    />
                                </svg>
                                <span className="text-lg group-hover:text-gray-900 transition-colors">
                                    {isLoading ? "Connecting..." : "Continue with Google"}
                                </span>
                            </button>

                            <div className="relative py-4">
                                <div className="absolute inset-0 flex items-center">
                                    <div className="w-full border-t border-gray-100"></div>
                                </div>
                                <div className="relative flex justify-center text-xs uppercase">
                                    <span className="bg-white px-2 text-gray-400">Secure Authentication</span>
                                </div>
                            </div>

                            <p className="text-center text-xs text-gray-400">
                                By continuing, you acknowledge that this is a demo application.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
