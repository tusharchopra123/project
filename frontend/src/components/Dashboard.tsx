"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend, LineChart, Line, XAxis, YAxis, CartesianGrid } from 'recharts';
import { TrendingUp, IndianRupee, Activity, ArrowUpDown, ArrowUp, ArrowDown, Target } from 'lucide-react';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

export default function Dashboard({ data }: { data: any }) {
    const router = useRouter();
    if (!data) return null;

    // State for sorting
    const [sortConfig, setSortConfig] = useState<{ key: string; direction: 'ascending' | 'descending' } | null>(null);
    const [timeRange, setTimeRange] = useState<string>('ALL');

    // Filter Logic for Chart
    const getFilteredChartData = () => {
        if (!data.growth_chart || data.growth_chart.length === 0) return [];
        if (timeRange === 'ALL') return data.growth_chart;

        const now = new Date();
        let subtractDays = 0;
        if (timeRange === '1M') subtractDays = 30;
        if (timeRange === '6M') subtractDays = 180;
        if (timeRange === '1Y') subtractDays = 365;
        if (timeRange === '3Y') subtractDays = 365 * 3;

        const cutoffDate = new Date();
        cutoffDate.setDate(now.getDate() - subtractDays);

        return data.growth_chart.filter((pt: any) => new Date(pt.date) >= cutoffDate);
    };

    // Placeholder data transformation if needed.
    // Assuming data structure from backend: { transaction_count, xirr, total_investment, current_valuation }

    // Sorting Logic
    const sortedHoldings = [...(data.holdings || [])];
    if (sortConfig !== null) {
        const { key, direction } = sortConfig;
        sortedHoldings.sort((a, b) => {
            let aValue: any;
            let bValue: any;

            // List of keys that are inside the nested 'analytics' object
            const analyticsKeys = [
                'fund_life', 'cagr', 'alpha', 'beta', 'info_ratio',
                'sharpe_ratio', 'sortino_ratio', 'sharpe', 'sortino',
                'max_drawdown', 'recovery_days', 'upside_capture',
                'downside_capture', 'rolling_3y_avg', 'rolling_3y_max',
                'rolling_3y_min', 'rolling_pos'
            ];

            if (analyticsKeys.includes(key)) {
                aValue = a.analytics?.[key];
                bValue = b.analytics?.[key];
            } else if (key === 'return') {
                aValue = a.amount > 0 ? ((a.current_value - a.amount) / a.amount) * 100 : 0;
                bValue = b.amount > 0 ? ((b.current_value - b.amount) / b.amount) * 100 : 0;
            } else {
                aValue = a[key];
                bValue = b[key];
            }

            // Handle null/undefined for sorting
            if (aValue === undefined || aValue === null) aValue = -Infinity;
            if (bValue === undefined || bValue === null) bValue = -Infinity;

            if (aValue < bValue) return direction === 'ascending' ? -1 : 1;
            if (aValue > bValue) return direction === 'ascending' ? 1 : -1;
            return 0;
        });
    }

    const requestSort = (key: string) => {
        let direction: 'ascending' | 'descending' = 'ascending';
        if (sortConfig && sortConfig.key === key && sortConfig.direction === 'ascending') {
            direction = 'descending';
        }
        setSortConfig({ key, direction });
    };

    const getSortIcon = (key: string) => {
        if (!sortConfig || sortConfig.key !== key) {
            return <ArrowUpDown className="w-4 h-4 ml-1 text-gray-400" />;
        }
        return sortConfig.direction === 'ascending' ? (
            <ArrowUp className="w-4 h-4 ml-1 text-gray-600" />
        ) : (
            <ArrowDown className="w-4 h-4 ml-1 text-gray-600" />
        );
    };

    const stats = [
        {
            label: "Total Funds",
            value: data.holdings?.length || 0,
            icon: <Activity className="w-6 h-6 text-white" />,
            gradient: "from-blue-500 to-indigo-600",
            bgGradient: "bg-gradient-to-br from-blue-50 to-indigo-50"
        },
        {
            label: "Est. XIRR",
            value: `${(data.xirr * 100).toFixed(2)}%`,
            icon: <TrendingUp className="w-6 h-6 text-white" />,
            gradient: "from-emerald-500 to-green-600",
            bgGradient: "bg-gradient-to-br from-emerald-50 to-green-50"
        },
        {
            label: "Total Investment",
            value: `₹${data.total_investment?.toLocaleString() || "0"}`,
            icon: <IndianRupee className="w-6 h-6 text-white" />,
            gradient: "from-amber-500 to-orange-600",
            bgGradient: "bg-gradient-to-br from-amber-50 to-orange-50"
        },
        {
            label: "Current Value",
            value: `₹${data.current_valuation?.toLocaleString() || "0"}`,
            icon: <IndianRupee className="w-6 h-6 text-white" />,
            gradient: "from-purple-500 to-pink-600",
            bgGradient: "bg-gradient-to-br from-purple-50 to-pink-50"
        },
    ];

    // Convert allocation data to chart format
    const allocationData = data.allocation ? Object.entries(data.allocation).map(([name, value]) => ({
        name,
        value
    })) : [];

    // Enhanced colors for asset allocation
    const ALLOCATION_COLORS: Record<string, string> = {
        'Equity': '#10b981', // Emerald
        'Debt': '#3b82f6', // Blue
        'Hybrid': '#8b5cf6', // Violet
        'Commodities': '#f59e0b', // Amber
        'Others': '#6b7280' // Gray
    };

    return (
        <div className="w-full space-y-8 animate-slide-up">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {stats.map((stat, i) => (
                    <div
                        key={i}
                        className={`${stat.bgGradient} premium-card p-6 rounded-2xl shadow-lg border border-white/50 relative overflow-hidden group`}
                    >
                        <div className="relative z-10">
                            <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${stat.gradient} shadow-lg mb-4 group-hover:scale-110 transition-transform`}>
                                {stat.icon}
                            </div>
                            <p className="text-sm text-gray-600 font-medium mb-1">{stat.label}</p>
                            <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                        </div>
                        <div className="absolute top-0 right-0 w-32 h-32 bg-white/20 rounded-full -mr-16 -mt-16"></div>
                    </div>
                ))}
            </div>

            {/* Charts Section - Growth and Allocation */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Asset Allocation */}
                <div className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl shadow-lg border border-white/50 premium-card">
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h3 className="text-xl font-bold text-gray-900">Asset Allocation</h3>
                            <p className="text-sm text-gray-500 mt-1">Distribution across asset classes</p>
                        </div>
                    </div>
                    {allocationData.length > 0 ? (
                        <div className="h-80 flex items-center justify-center">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={allocationData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={80}
                                        outerRadius={120}
                                        fill="#8884d8"
                                        paddingAngle={3}
                                        dataKey="value"
                                        label={({ name, percent }) => `${name} (${percent ? (percent * 100).toFixed(1) : '0'}%)`}
                                    >
                                        {allocationData.map((entry, index) => (
                                            <Cell
                                                key={`cell-${index}`}
                                                fill={ALLOCATION_COLORS[entry.name] || COLORS[index % COLORS.length]}
                                                onClick={() => router.push(`/category/${entry.name}`)}
                                                className="focus:outline-none outline-none border-none"
                                                style={{ cursor: 'pointer', outline: 'none', boxShadow: 'none' }}
                                            />
                                        ))}
                                    </Pie>
                                    <Tooltip formatter={(value: any) => [`₹${(value || 0).toLocaleString()}`, ""]} />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    ) : (
                        <p className="text-gray-500 text-center py-8">No allocation data available</p>
                    )}
                </div>

                {/* Growth Chart */}
                <div className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl shadow-lg border border-white/50 premium-card">
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h3 className="text-xl font-bold text-gray-900">Portfolio Growth</h3>
                            <p className="text-sm text-gray-500 mt-1">Track your investment journey over time</p>
                        </div>
                        <Target className="w-6 h-6 text-indigo-600" />
                    </div>

                    {/* Time Range Filters */}
                    <div className="flex space-x-2 mb-6 overflow-x-auto">
                        {['1M', '6M', '1Y', '3Y', 'ALL'].map((range) => (
                            <button
                                key={range}
                                onClick={() => setTimeRange(range)}
                                className={`px-4 py-2 rounded-xl font-medium text-sm transition-all whitespace-nowrap ${timeRange === range
                                    ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-md'
                                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                    }`}
                            >
                                {range}
                            </button>
                        ))}
                    </div>

                    {/* Chart */}
                    {data.growth_chart && data.growth_chart.length > 0 ? (
                        <div className="h-80 w-full relative group">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={getFilteredChartData()}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                                    <XAxis
                                        dataKey="date"
                                        hide
                                    />
                                    <YAxis
                                        hide
                                    />
                                    <Tooltip
                                        content={({ active, payload, label }) => {
                                            if (active && payload && payload.length) {
                                                const portfolio = payload.find(p => p.name === 'Portfolio Value')?.value as number;
                                                const invested = payload.find(p => p.name === 'Invested Amount')?.value as number;
                                                const benchmark = payload.find(p => p.name === 'Benchmark (Nifty 50)')?.value as number;

                                                const absoluteReturn = portfolio - invested;
                                                const returnPercent = invested > 0 ? (absoluteReturn / invested) * 100 : 0;

                                                if (portfolio === undefined || invested === undefined) return null;

                                                return (
                                                    <div className="bg-white p-4 rounded-lg shadow-xl border border-gray-100 text-sm">
                                                        <p className="font-semibold text-gray-900 mb-2 border-b pb-2">{label ? new Date(label).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' }) : ''}</p>
                                                        <div className="space-y-1 mb-3">
                                                            <div className="flex justify-between items-center space-x-8">
                                                                <span className="text-gray-500 flex items-center"><div className="w-2 h-2 rounded-full bg-green-600 mr-2"></div>Portfolio</span>
                                                                <span className="font-bold text-gray-900">₹{portfolio.toLocaleString()}</span>
                                                            </div>
                                                            <div className="flex justify-between items-center space-x-8">
                                                                <span className="text-gray-500 flex items-center"><div className="w-2 h-2 rounded-full bg-gray-400 mr-2"></div>Invested</span>
                                                                <span className="font-bold text-gray-900">₹{invested.toLocaleString()}</span>
                                                            </div>
                                                            {(benchmark || 0) > 0 && (
                                                                <div className="flex justify-between items-center space-x-8">
                                                                    <span className="text-gray-500 flex items-center"><div className="w-2 h-2 rounded-full bg-blue-600 mr-2"></div>Nifty 50</span>
                                                                    <span className="font-bold text-gray-900 text-xs">₹{benchmark?.toLocaleString()}</span>
                                                                </div>
                                                            )}
                                                        </div>

                                                        <div className={`mt-2 pt-2 border-t ${absoluteReturn >= 0 ? "bg-green-50 border-green-100" : "bg-red-50 border-red-100"} p-2 rounded -mx-1`}>
                                                            <div className="flex justify-between items-center">
                                                                <span className={`text-xs font-semibold ${absoluteReturn >= 0 ? "text-green-700" : "text-red-700"}`}>
                                                                    {absoluteReturn >= 0 ? "Absolute Gain" : "Absolute Loss"}
                                                                </span>
                                                                <div className="text-right">
                                                                    <span className={`block font-bold ${absoluteReturn >= 0 ? "text-green-700" : "text-red-700"}`}>
                                                                        {absoluteReturn >= 0 ? "+" : "-"}₹{Math.abs(absoluteReturn).toLocaleString()}
                                                                    </span>
                                                                    <span className={`text-xs font-medium ${absoluteReturn >= 0 ? "text-green-600" : "text-red-600"}`}>
                                                                        ({absoluteReturn >= 0 ? "+" : ""}{returnPercent.toFixed(2)}%)
                                                                    </span>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                );
                                            }
                                            return null;
                                        }}
                                    />
                                    <Legend wrapperStyle={{ paddingTop: '20px' }} />
                                    <Line type="monotone" dataKey="invested" name="Invested Amount" stroke="#9ca3af" strokeDasharray="3 3" dot={false} strokeWidth={2} activeDot={{ r: 4 }} />
                                    <Line type="monotone" dataKey="portfolio" name="Portfolio Value" stroke="#16a34a" strokeWidth={2} dot={false} activeDot={{ r: 6, strokeWidth: 0 }} />
                                    <Line type="monotone" dataKey="benchmark" name="Benchmark (Nifty 50)" stroke="#2563eb" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    ) : (
                        <div className="h-80 w-full flex items-center justify-center bg-gray-50 rounded-xl border border-dashed border-gray-300">
                            <p className="text-gray-500 italic">Growth data loading or unavailable...</p>
                        </div>
                    )}
                </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                <h3 className="text-lg font-semibold mb-4">Benchmark Comparison (Nifty 50)</h3>
                {data.benchmark_xirr ? (
                    <ul className="space-y-4">
                        <li className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <span className="text-gray-600 font-medium">Your Portfolio XIRR</span>
                            <span className={`font-bold text-lg ${(data.xirr - data.benchmark_xirr) >= 0 ? "text-green-600" : "text-red-600"}`}>
                                {(data.xirr * 100).toFixed(2)}%
                            </span>
                        </li>
                        <li className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <span className="text-gray-600 font-medium">Nifty 50 Benchmark XIRR</span>
                            <span className="font-bold text-lg text-blue-600">
                                {(data.benchmark_xirr * 100).toFixed(2)}%
                            </span>
                        </li>

                        <li className="pt-2">
                            <div className={`flex items-start space-x-2 p-3 rounded-lg ${(data.xirr - data.benchmark_xirr) >= 0 ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
                                {(data.xirr - data.benchmark_xirr) >= 0 ? (
                                    <TrendingUp className="w-5 h-5 mt-0.5" />
                                ) : (
                                    <Activity className="w-5 h-5 mt-0.5" />
                                )}
                                <p className="font-medium">
                                    You are {(data.xirr - data.benchmark_xirr) >= 0 ? "beating" : "lagging"} the market by <span className="font-bold">{Math.abs((data.xirr - data.benchmark_xirr) * 100).toFixed(2)}%</span>
                                </p>
                            </div>
                        </li>
                    </ul>
                ) : (
                    <p className="text-gray-500 italic">Benchmark data unavailable or loading...</p>
                )}
            </div>
            {data.holdings && (
                <div className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl shadow-lg border border-white/50 mt-8 premium-card">
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h3 className="text-xl font-bold text-gray-900">Fund Wise Details</h3>
                            <p className="text-sm text-gray-500 mt-1">Detailed breakdown of your holdings</p>
                        </div>
                    </div>
                    <div className="overflow-x-auto rounded-xl">
                        <table className="min-w-full">
                            <thead className="bg-gradient-to-r from-indigo-50 to-purple-50">
                                <tr>
                                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider sticky left-0 bg-gradient-to-r from-indigo-50 to-purple-50 z-10 cursor-pointer hover:from-indigo-100 hover:to-purple-100 transition-all" onClick={() => requestSort('description')}>
                                        <div className="flex items-center">Scheme Name {getSortIcon('description')}</div>
                                    </th>
                                    <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-indigo-100 transition-all" onClick={() => requestSort('amount')}>
                                        <div className="flex items-center justify-end">Invested {getSortIcon('amount')}</div>
                                    </th>
                                    <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-indigo-100 transition-all" onClick={() => requestSort('current_value')}>
                                        <div className="flex items-center justify-end">Value {getSortIcon('current_value')}</div>
                                    </th>
                                    <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-indigo-100 transition-all" onClick={() => requestSort('xirr')}>
                                        <div className="flex items-center justify-end">XIRR {getSortIcon('xirr')}</div>
                                    </th>
                                    <th className="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-indigo-100 transition-all" onClick={() => requestSort('fund_life')}>
                                        <div className="flex items-center justify-end">Fund Life (Yrs) {getSortIcon('fund_life')}</div>
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" onClick={() => requestSort('score')}>
                                        <div className="flex items-center justify-end">Quant Score {getSortIcon('score')}</div>
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" onClick={() => requestSort('cagr')}>
                                        <div className="flex items-center justify-end">CAGR {getSortIcon('cagr')}</div>
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" onClick={() => requestSort('alpha')}>
                                        <div className="flex items-center justify-end">Alpha {getSortIcon('alpha')}</div>
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" onClick={() => requestSort('beta')}>
                                        <div className="flex items-center justify-end">Beta {getSortIcon('beta')}</div>
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" onClick={() => requestSort('info_ratio')}>
                                        <div className="flex items-center justify-end">Info Ratio {getSortIcon('info_ratio')}</div>
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" onClick={() => requestSort('sharpe')}>
                                        <div className="flex items-center justify-end">Sharpe Ratio {getSortIcon('sharpe')}</div>
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" onClick={() => requestSort('sortino')}>
                                        <div className="flex items-center justify-end">Sortino Ratio {getSortIcon('sortino')}</div>
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" onClick={() => requestSort('max_drawdown')}>
                                        <div className="flex items-center justify-end">Max Drawdown {getSortIcon('max_drawdown')}</div>
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" onClick={() => requestSort('recovery_days')}>
                                        <div className="flex items-center justify-end">MaxDD Rec. (Days) {getSortIcon('recovery_days')}</div>
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" onClick={() => requestSort('upside_capture')}>
                                        <div className="flex items-center justify-end">Upside Capture {getSortIcon('upside_capture')}</div>
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" onClick={() => requestSort('downside_capture')}>
                                        <div className="flex items-center justify-end">Downside Capture {getSortIcon('downside_capture')}</div>
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" onClick={() => requestSort('rolling_3y_avg')}>
                                        <div className="flex items-center justify-end">Avg Roll 3Y {getSortIcon('rolling_3y_avg')}</div>
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" onClick={() => requestSort('rolling_3y_max')}>
                                        <div className="flex items-center justify-end">Max Roll 3Y {getSortIcon('rolling_3y_max')}</div>
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" onClick={() => requestSort('rolling_3y_min')}>
                                        <div className="flex items-center justify-end">Min Roll 3Y {getSortIcon('rolling_3y_min')}</div>
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" onClick={() => requestSort('rolling_pos')}>
                                        <div className="flex items-center justify-end">% Positive {getSortIcon('rolling_pos')}</div>
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {sortedHoldings.map((fund: any, idx: number) => (
                                    <tr key={idx} className="hover:bg-gray-50 transition-colors">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 sticky left-0 bg-white border-r border-gray-100 shadow-[2px_0_5px_-2px_rgba(0,0,0,0.1)]">
                                            <div className="flex items-center space-x-2">
                                                <span>{fund.description}</span>
                                                {fund.is_sip && (
                                                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                                                        SIP
                                                    </span>
                                                )}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-600">₹{fund.amount.toLocaleString()}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900 font-semibold">₹{fund.current_value.toLocaleString()}</td>
                                        <td className={`px-6 py-4 whitespace-nowrap text-sm text-right font-bold ${(fund.xirr || 0) >= 0 ? "text-green-600" : "text-red-600"}`}>
                                            {(fund.days_invested && fund.days_invested < 365) ? "--" : (fund.xirr ? `${(fund.xirr * 100).toFixed(2)}%` : "0.00%")}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-600">{fund.analytics?.fund_life?.toFixed(1) || '-'}</td>
                                        <td className={`px-6 py-4 whitespace-nowrap text-sm text-right font-bold ${(fund.score || 0) >= 70 ? "text-green-600" :
                                            (fund.score || 0) >= 40 ? "text-yellow-600" : "text-red-500"
                                            }`}>
                                            {fund.score !== undefined ? fund.score : '-'}
                                        </td>
                                        <td className={`px-6 py-4 whitespace-nowrap text-sm text-right font-bold ${(fund.analytics?.cagr || 0) >= 0 ? "text-green-600" : "text-red-600"}`}>
                                            {fund.analytics?.cagr !== undefined ? (fund.analytics.cagr * 100).toFixed(2) + '%' : '-'}
                                        </td>
                                        <td className={`px-6 py-4 whitespace-nowrap text-sm text-right ${(fund.analytics?.alpha || 0) >= 0 ? "text-green-600" : "text-red-600"}`}>
                                            {fund.analytics?.alpha !== undefined ? (fund.analytics.alpha * 100).toFixed(2) + '%' : '-'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-600">{fund.analytics?.beta !== undefined ? fund.analytics.beta.toFixed(2) : '-'}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-600">{fund.analytics?.info_ratio !== undefined ? fund.analytics.info_ratio.toFixed(2) : '-'}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-600">{fund.analytics?.sharpe !== undefined ? fund.analytics.sharpe.toFixed(2) : '-'}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-600">{fund.analytics?.sortino !== undefined ? fund.analytics.sortino.toFixed(2) : '-'}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-red-500 font-medium">{fund.analytics?.max_drawdown !== undefined ? (fund.analytics.max_drawdown * 100).toFixed(2) + '%' : '-'}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500">
                                            {fund.analytics?.recovery_days === "Unrecovered" ? "Unrecovered" :
                                                (typeof fund.analytics?.recovery_days === 'number' ? `${fund.analytics.recovery_days}d` : '--')}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-600">{fund.analytics?.upside_capture !== undefined ? fund.analytics.upside_capture.toFixed(0) : '-'}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-600">{fund.analytics?.downside_capture !== undefined ? fund.analytics.downside_capture.toFixed(0) : '-'}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-blue-600 font-medium">{fund.analytics?.rolling_3y_avg !== undefined ? (fund.analytics.rolling_3y_avg * 100).toFixed(2) + '%' : '-'}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500">{fund.analytics?.rolling_3y_max !== undefined ? (fund.analytics.rolling_3y_max * 100).toFixed(2) + '%' : '-'}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500">{fund.analytics?.rolling_3y_min !== undefined ? (fund.analytics.rolling_3y_min * 100).toFixed(2) + '%' : '-'}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-600">{fund.analytics?.rolling_pos !== undefined ? (fund.analytics.rolling_pos * 100).toFixed(1) + '%' : '-'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}
