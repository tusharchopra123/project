
"use client";

import { useSession, signOut } from "next-auth/react";
import { useRouter, usePathname } from "next/navigation";
import { useState } from "react";

export default function AuthenticatedNavbar() {
    const { data: session } = useSession();
    const router = useRouter();
    const pathname = usePathname();

    const getInitials = (name: string | null | undefined) => {
        if (!name) return 'U';
        const parts = name.trim().split(' ');
        if (parts.length >= 2) {
            return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
        }
        return name[0].toUpperCase();
    };

    const [imageError, setImageError] = useState(false);

    return (
        <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex justify-between items-center">
                <div className="flex items-center space-x-3 cursor-pointer" onClick={() => router.push('/dashboard')}>
                    <div className="relative group">
                        <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg blur opacity-25 group-hover:opacity-75 transition duration-200"></div>
                        <div className="relative w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg flex items-center justify-center shadow-lg">
                            <span className="text-white font-bold text-xl">W</span>
                        </div>
                    </div>
                    <div>
                        <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-gray-700">
                            WealthTrack
                        </h1>
                        <p className="text-[10px] uppercase tracking-wider text-gray-500 font-semibold">Premium Analytics</p>
                    </div>
                </div>

                <div className="flex items-center space-x-6">
                    <div className="hidden md:flex items-center space-x-6 mr-4">
                        <nav className="flex space-x-6 text-sm font-medium text-gray-500">
                            <span
                                onClick={() => router.push('/dashboard')}
                                className={`${pathname === '/dashboard' ? 'text-blue-600 font-bold' : 'hover:text-blue-600'} cursor-pointer transition-colors`}
                            >
                                Dashboard
                            </span>
                            <span
                                onClick={() => router.push('/upload')}
                                className={`${pathname === '/upload' ? 'text-blue-600 font-bold' : 'hover:text-blue-600'} cursor-pointer transition-colors`}
                            >
                                New Upload
                            </span>
                        </nav>
                    </div>

                    <div className="h-6 w-px bg-gray-200 hidden md:block"></div>

                    <div className="relative group cursor-pointer" onClick={() => {
                        sessionStorage.removeItem('portfolioData');
                        signOut({ callbackUrl: '/login' });
                    }}>
                        {session?.user?.image && !imageError ? (
                            <img
                                src={session.user.image}
                                alt="User"
                                className="w-8 h-8 rounded-full ring-2 ring-white shadow-md object-cover"
                                onError={() => setImageError(true)}
                            />
                        ) : (
                            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center ring-2 ring-white shadow-md">
                                <span className="text-white text-xs font-bold">{getInitials(session?.user?.name)}</span>
                            </div>
                        )}
                        <div className="absolute right-0 top-full mt-2 w-32 bg-white rounded-lg shadow-xl border border-gray-100 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none group-hover:pointer-events-auto p-2">
                            <p className="text-xs text-center text-gray-500 mb-1">Click to Sign Out</p>
                        </div>
                    </div>
                </div>
            </div>
        </header>
    );
}
