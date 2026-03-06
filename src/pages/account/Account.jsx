
import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { User, Mail, Shield, CreditCard, Bell, Save } from 'lucide-react';

const Account = () => {
    const { user } = useAuth();
    const [formData, setFormData] = useState({
        name: user?.name || 'Dr. Alex Smith',
        email: user?.email || 'alex.smith@clinic.com',
        phone: '+1 (555) 123-4567',
        company: 'Smith Dental Care',
        notifications: true
    });

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    return (
        <div className="p-6 max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold text-slate-800 mb-8">Account Settings</h1>

            <div className="grid grid-cols-1 gap-6">

                {/* Profile Card */}
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                    <div className="flex items-center space-x-4 mb-6">
                        <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center">
                            <User size={32} />
                        </div>
                        <div>
                            <h2 className="text-xl font-semibold text-slate-800">Profile Information</h2>
                            <p className="text-sm text-slate-500">Update your account's profile information and email address.</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
                            <div className="relative">
                                <span className="absolute left-3 top-2.5 text-slate-400"><User size={16} /></span>
                                <input
                                    type="text"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleChange}
                                    className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label>
                            <div className="relative">
                                <span className="absolute left-3 top-2.5 text-slate-400"><Mail size={16} /></span>
                                <input
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    readOnly
                                    className="w-full pl-10 pr-4 py-2 border border-slate-200 bg-slate-50 rounded-lg text-slate-500 cursor-not-allowed"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Company Name</label>
                            <input
                                type="text"
                                name="company"
                                value={formData.company}
                                onChange={handleChange}
                                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Phone Number</label>
                            <input
                                type="text"
                                name="phone"
                                value={formData.phone}
                                onChange={handleChange}
                                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            />
                        </div>
                    </div>
                </div>

                {/* Security Section Placeholders */}
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                    <div className="flex items-center space-x-4 mb-6">
                        <div className="w-12 h-12 bg-slate-100 text-slate-600 rounded-full flex items-center justify-center">
                            <Shield size={24} />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-slate-800">Security</h2>
                            <p className="text-sm text-slate-500">Protect your account with a strong password.</p>
                        </div>
                    </div>
                    <div className="border-t border-slate-100 pt-4">
                        <button className="text-blue-600 font-medium hover:text-blue-800 text-sm">Change Password</button>
                    </div>
                </div>

                {/* Billing Section Placeholders */}
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                    <div className="flex items-center space-x-4 mb-6">
                        <div className="w-12 h-12 bg-green-100 text-green-600 rounded-full flex items-center justify-center">
                            <CreditCard size={24} />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-slate-800">Billing & Subscription</h2>
                            <p className="text-sm text-slate-500">Manage your subscription plan and payment methods.</p>
                        </div>
                    </div>
                    <div className="border-t border-slate-100 pt-4 flex justify-between items-center">
                        <span className="text-sm font-medium text-slate-700">Current Plan: <span className="text-blue-600">Solo Pro</span></span>
                        <button className="text-slate-600 font-medium hover:text-slate-800 text-sm border border-slate-300 px-3 py-1 rounded">Manage Subscription</button>
                    </div>
                </div>

                <div className="flex justify-end pt-4">
                    <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium flex items-center space-x-2">
                        <Save size={18} />
                        <span>Save Changes</span>
                    </button>
                </div>

            </div>
        </div>
    );
};

export default Account;
