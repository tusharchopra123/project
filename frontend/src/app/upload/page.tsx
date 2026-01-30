
"use client";

import FileUpload from "@/components/FileUpload";
import AuthenticatedNavbar from "@/components/AuthenticatedNavbar";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function UploadPage() {
    const { status } = useSession();
    const router = useRouter();

    useEffect(() => {
        if (status === "unauthenticated") {
            router.push("/login");
        }
    }, [status, router]);

    if (status === "loading") {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            </div>
        );
    }

    return (
        <main className="min-h-screen bg-gray-50">
            <AuthenticatedNavbar />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="space-y-8">
                    <div className="text-center max-w-2xl mx-auto">
                        <h2 className="text-3xl font-extrabold text-gray-900 tracking-tight sm:text-4xl">
                            Upload New Statement
                        </h2>
                        <p className="mt-4 text-lg text-gray-500">
                            Upload your CAMS/Karvy PDF to update your portfolio analysis.
                        </p>
                    </div>

                    <div className="mt-12">
                        <div className="max-w-xl mx-auto">
                            <FileUpload />
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}
