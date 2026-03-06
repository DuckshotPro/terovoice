import React from 'react';

const BackgroundWave = ({ children }) => {
    return (
        <>
            {/* Fixed Background Container */}
            <div className="fixed inset-0 overflow-hidden bg-slate-900 -z-10 pointer-events-none">
                {/* BACK layer */}
                <div className="tero-wave layer-back absolute inset-0"></div>

                {/* MID layer */}
                <div className="tero-wave layer-mid absolute inset-0"></div>

                {/* FRONT layer */}
                <div className="tero-wave layer-front absolute inset-0"></div>
            </div>

            {/* Scrollable Content */}
            <div className="relative z-10 w-full min-h-screen">
                {children}
            </div>
        </>
    );
};

export default BackgroundWave;
