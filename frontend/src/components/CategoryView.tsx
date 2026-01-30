"use client";

import { useRouter } from 'next/navigation';
import { ArrowLeft, TrendingUp, IndianRupee } from 'lucide-react';
import { useState, useEffect, use } from 'react';

export default function CategoryView({ params }: { params: Promise<{ categoryName: string }> }) {
    const { categoryName } = use(params);
    const router = useRouter();
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Read portfolio data from sessionStorage
        const stored = sessionStorage.getItem('portfolioData');
        if (stored) {
            setData(JSON.parse(stored));
        }
        setLoading(false);
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Loading portfolio data...</p>
                </div>
            </div>
        );
    }

    if (!data || !data.holdings) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <p className="text-gray-600">No portfolio data available</p>
                    <button
                        onClick={() => router.push('/dashboard')}
                        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        Back to Dashboard
                    </button>
                </div>
            </div>
        );
    }

    // Filter holdings by category
    const filteredHoldings = data.holdings.filter((h: any) => h.asset_class === categoryName);

    // Calculate category stats
    const totalValue = filteredHoldings.reduce((sum: number, h: any) => sum + (h.current_value || 0), 0);
    const totalInvested = filteredHoldings.reduce((sum: number, h: any) => sum + (h.amount || 0), 0);
    const overallReturn = totalInvested > 0 ? ((totalValue - totalInvested) / totalInvested) * 100 : 0;

    const getScoreColorClass = (score: number | undefined) => {
        if (score === undefined) return 'text-gray-400';
        if (score >= 70) return 'text-green-600';
        if (score >= 50) return 'text-yellow-600';
        return 'text-red-600';
    };

    return (
        <div className="min-h-screen p-8 animate-slide-up">
            <div className="max-w-7xl mx-auto">
                {/* Breadcrumb Navigation */}
                <nav className="mb-8">
                    <button
                        onClick={() => router.push('/dashboard')}
                        className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl shadow-lg hover:from-indigo-700 hover:to-purple-700 transition-all hover:scale-105 hover:shadow-xl"
                    >
                        <ArrowLeft className="w-5 h-5" />
                        Back to Dashboard
                    </button>
                </nav>

                {/* Page Header */}
                <div className="mb-8 bg-white/80 backdrop-blur-sm p-8 rounded-2xl shadow-lg border border-white/50">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg">
                            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                            </svg>
                        </div>
                        <div>
                            <h1 className="text-4xl font-bold text-gray-900">{categoryName} Funds</h1>
                            <p className="text-gray-600 mt-1">Detailed analysis of your {categoryName.toLowerCase()} portfolio</p>
                        </div>
                    </div>

                    {/* Category Stats */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-5 rounded-xl border border-blue-100">
                            <div className="flex items-center space-x-3">
                                <div className="p-2 bg-blue-500 rounded-lg">
                                    <IndianRupee className="w-5 h-5 text-white" />
                                </div>
                                <div>
                                    <p className="text-sm text-gray-600 font-medium">Total Value</p>
                                    <p className="text-2xl font-bold text-gray-900">₹{totalValue.toLocaleString()}</p>
                                </div>
                            </div>
                        </div>
                        <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-5 rounded-xl border border-green-100">
                            <div className="flex items-center space-x-3">
                                <div className="p-2 bg-green-500 rounded-lg">
                                    <TrendingUp className="w-5 h-5 text-white" />
                                </div>
                                <div>
                                    <p className="text-sm text-gray-600 font-medium">Overall Return</p>
                                    <p className={`text-2xl font-bold ${overallReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        {overallReturn >= 0 ? '+' : ''}{overallReturn.toFixed(2)}%
                                    </p>
                                </div>
                            </div>
                        </div>
                        <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-5 rounded-xl border border-purple-100">
                            <div className="flex items-center space-x-3">
                                <div className="p-2 bg-purple-500 rounded-lg">
                                    <div className="w-5 h-5 text-white flex items-center justify-center font-bold">#</div>
                                </div>
                                <div>
                                    <p className="text-sm text-gray-600 font-medium">Number of Funds</p>
                                    <p className="text-2xl font-bold text-gray-900">{filteredHoldings.length}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Funds Table */}
                <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/50 overflow-hidden premium-card">
                    <div className="overflow-x-auto">
                        <table className="min-w-full">
                            <thead className="bg-gradient-to-r from-indigo-50 to-purple-50">
                                <tr>
                                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                                        Fund Name
                                    </th>
                                    <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">
                                        Current Value
                                    </th>
                                    <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">
                                        Invested
                                    </th>
                                    <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">
                                        Return %
                                    </th>
                                    <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">
                                        Quant Score
                                    </th>
                                    <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">
                                        Fund Life
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white/50 divide-y divide-gray-200">
                                {filteredHoldings.length > 0 ? (
                                    filteredHoldings.map((fund: any, idx: number) => {
                                        const returnPct = fund.amount > 0 ? ((fund.current_value - fund.amount) / fund.amount) * 100 : 0;
                                        return (
                                            <tr key={idx} className="hover:bg-white/80 transition-colors">
                                                <td className="px-6 py-4">
                                                    <div>
                                                        <div className="text-sm font-medium text-gray-900">{fund.scheme_name || 'N/A'}</div>
                                                        <div className="text-xs text-gray-500">{fund.isin}</div>
                                                    </div>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-semibold text-gray-900">
                                                    ₹{(fund.current_value || 0).toLocaleString()}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-600">
                                                    ₹{(fund.amount || 0).toLocaleString()}
                                                </td>
                                                <td className={`px-6 py-4 whitespace-nowrap text-sm text-right font-semibold ${returnPct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                    {returnPct >= 0 ? '+' : ''}{returnPct.toFixed(2)}%
                                                </td>
                                                <td className={`px-6 py-4 whitespace-nowrap text-sm text-right font-bold ${getScoreColorClass(fund.score)}`}>
                                                    {fund.score !== undefined ? fund.score.toFixed(1) : '-'}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-600">
                                                    {fund.analytics?.fund_life ? `${fund.analytics.fund_life.toFixed(1)} yrs` : '-'}
                                                </td>
                                            </tr>
                                        );
                                    })
                                ) : (
                                    <tr>
                                        <td colSpan={6} className="px-6 py-12 text-center text-gray-500 italic">
                                            No funds found in this category
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}
